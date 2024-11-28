use std::{
    fs::File,
    io::BufReader,
    ops::Range,
    path::{Path, PathBuf},
    sync::Arc,
};

use arrow::{array::StringArray, ipc::reader::StreamReader};
use indicatif::{ParallelProgressIterator, ProgressBar, ProgressIterator, ProgressStyle};
use rayon::iter::{IntoParallelIterator, ParallelIterator};

use super::{Dataset, DatasetIterator, InMemoryDataset, VecDatasetIter};
use crate::{Token, Tokenizer};

pub struct HuggingfaceShardDataset {
    path: PathBuf,
    tokenizer: Tokenizer,
}

impl HuggingfaceShardDataset {
    #[must_use]
    pub fn new(path: impl AsRef<Path>, tokenizer: Tokenizer) -> Self {
        Self {
            path: path.as_ref().to_owned(),
            tokenizer,
        }
    }

    pub fn to_memory(self) -> InMemoryDataset {
        let mut chunks = Vec::with_capacity(128);
        self.iter().for_each_chunk(|chunk| {
            chunks.push(Arc::from(self.tokenizer.tokenize_bytes(chunk)));
        });
        InMemoryDataset::new(chunks)
    }
}

impl Dataset for HuggingfaceShardDataset {
    type Iter = HuggingfaceShardDatasetIter;

    fn iter(&self) -> Self::Iter {
        let file = File::open(&self.path).expect("Failed to open path");
        let reader =
            StreamReader::try_new_buffered(file, None).expect("Failed to create StreamReader");
        HuggingfaceShardDatasetIter {
            reader,
            tokenizer: self.tokenizer.clone(),
        }
    }

    fn update_tokenizer(&mut self, mut tokenizer: Tokenizer) {
        tokenizer.set_new(None);
        self.tokenizer = tokenizer;
    }
}

pub struct HuggingfaceShardDatasetIter {
    reader: StreamReader<BufReader<File>>,
    tokenizer: Tokenizer,
}

impl HuggingfaceShardDatasetIter {
    fn for_each_chunk(self, mut f: impl FnMut(&[u8])) {
        for batch in self.reader.into_iter() {
            let batch = batch.expect("to be okay");
            let batch = batch
                .column(1)
                .as_any()
                .downcast_ref::<StringArray>()
                .expect("Invalid string array");

            batch
                .iter()
                .map(Option::unwrap)
                .map(str::as_bytes)
                .for_each(&mut f);
        }
    }
}

impl DatasetIterator for HuggingfaceShardDatasetIter {
    fn for_each_token_pair(self, mut f: impl FnMut(Token, Token)) {
        let tokenizer = self.tokenizer.clone();
        self.for_each_chunk(|string| {
            let tokenized = tokenizer.tokenize_bytes(string);
            for pair in tokenized.windows(2) {
                f(pair[0], pair[1]);
            }
        })
    }
}

pub struct HuggingfaceShardsDataset {
    path_template: String,
    range: Range<usize>,
    shard_amount: usize,
    tokenizer: Tokenizer,
}

impl HuggingfaceShardsDataset {
    #[must_use]
    pub fn new(template: &str, shard_amount: usize, tokenizer: Tokenizer) -> Self {
        assert!(template.contains("{num}"), "Vorlage enthält nicht {{num}}");
        Self {
            path_template: template.to_owned(),
            range: 0..shard_amount,
            shard_amount,
            tokenizer,
        }
    }

    pub fn to_memory(mut self, range: Range<usize>) -> InMemoryDataset {
        let style = ProgressStyle::default_bar().template("Tokenizen der Eingabe: {spinner} [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})").expect("Invalide Vorlage");
        self.range = range;
        self.iter()
            .0
            .into_par_iter()
            .map(HuggingfaceShardDataset::to_memory)
            .progress_with_style(style)
            .sum()
    }
}

impl Dataset for HuggingfaceShardsDataset {
    type Iter = VecDatasetIter<HuggingfaceShardDataset>;

    fn iter(&self) -> Self::Iter {
        VecDatasetIter(
            self.range
                .clone()
                .map(|i| {
                    HuggingfaceShardDataset::new(
                        self.path_template
                            .replace("{num}", &format!("{i:0>5}"))
                            .replace("{max}", &format!("{:0>5}", self.shard_amount)),
                        self.tokenizer.clone(),
                    )
                })
                .collect(),
        )
    }

    fn update_tokenizer(&mut self, mut tokenizer: Tokenizer) {
        tokenizer.set_new(None);
        self.tokenizer = tokenizer;
    }
}

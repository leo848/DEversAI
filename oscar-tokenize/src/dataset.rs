use std::{
    fs,
    iter::Sum,
    mem,
    path::Path,
    sync::{mpsc, Arc},
};

use indicatif::{ParallelProgressIterator, ProgressBar, ProgressDrawTarget, ProgressFinish, ProgressStyle};
use itertools::Itertools;
use rayon::{
    iter::{IntoParallelRefIterator, IntoParallelRefMutIterator},
    prelude::ParallelIterator,
    ThreadPoolBuilder,
};

use crate::{config::TrainResult, Tokenizer};

mod huggingface;
mod wikipedia;

use derive_more::derive::Constructor;
pub use huggingface::{
    HuggingfaceShardDataset, HuggingfaceShardDatasetIter, HuggingfaceShardsDataset,
};
pub use wikipedia::WikipediaDataset;

use crate::{BpeState, Count, Token, TokenHistogram, TrainConfig};

pub trait Dataset {
    type Iter: Send + DatasetIterator;
    fn iter(&self) -> Self::Iter;

    fn train_step(&self, state: &mut BpeState, config: &TrainConfig) -> TrainResult
    where
        Self::Iter: 'static,
    {
        let parallelism = num_cpus::get();

        let iterators = self.iter().split_work(parallelism);
        println!("{} iterators", iterators.len());

        let shared_state = Arc::new(mem::take(state));

        let threadpool = ThreadPoolBuilder::new()
            .num_threads(parallelism)
            .build()
            .expect("Fehler beim Erstellen des Threadpool");

        let progress_bar = ProgressBar::new(iterators.len() as u64).with_style({
            {
                ProgressStyle::default_bar()
                    .template("Tokenpaare werden gezählt: [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
        .unwrap()
            }
        }).with_finish(ProgressFinish::WithMessage("Zählen abgeschlossen".into()));
        progress_bar.set_draw_target(ProgressDrawTarget::stdout());

        let (tx, rx) = mpsc::channel();

        let total_count = iterators.len();
        for token_iterator in iterators {
            let tx = tx.clone();
            threadpool.spawn(move || {
                let mut histogram = TokenHistogram::new();
                token_iterator.for_each_token_pair(|token_left, token_right| {
                    histogram.register_pair(token_left, token_right);
                    histogram.register(token_left);
                });
                tx.send(histogram).expect("Fehler beim Senden");
            });
        }

        let mut total_histogram = TokenHistogram::new();
        let mut done_count = 0;
        for histogram in rx {
            total_histogram += histogram;
            done_count += 1;
            progress_bar.inc(1);
            if done_count == total_count {
                break;
            }
        }
        progress_bar.finish();

        *state = Arc::into_inner(shared_state).expect("Threads haben Ressourcen behalten");
        println!("{}", total_histogram.display_with_state(state));

        let merges_to_add = total_histogram.merges_to_add(config.eta.for_t(state.additional_vocab_size() as f64 / config.target_vocab_size as f64));
        let mut new_token_count = Count::default();
        for (left, right) in merges_to_add {
            if config.max_token_length.is_some_and(|length| {
                state.at_token(left).len() + state.at_token(right).len() > length
            }) {
                continue;
            }
            let new_token = state.add_token(left, right);

            let count = total_histogram.get_pair(left, right);
            let [left, right, new_token] =
                [left, right, new_token].map(|token| token.display_with_state(state));

            println!("{left:>10} + {right:<10} -> {new_token:<20} ({count})");
            new_token_count += 1;
        }

        TrainResult { new_token_count }
    }

    fn update_tokenizer(&mut self, tokenizer: Tokenizer) {
        let _ = tokenizer;
    }
}

pub trait DatasetIterator {
    fn for_each_token_pair(self, f: impl FnMut(Token, Token));
    fn split_work(self, parallelism: usize) -> Vec<Self>
    where
        Self: Sized,
    {
        let _ = parallelism;
        vec![self]
    }
}

#[derive(Debug, Clone, Constructor)]
pub struct VecDataset<D: Dataset> {
    datasets: Vec<D>,
}

impl<D: Dataset + Send + Clone> Dataset for VecDataset<D> {
    type Iter = VecDatasetIter<D>;

    fn iter(&self) -> Self::Iter {
        VecDatasetIter(self.datasets.clone())
    }
}

pub struct VecDatasetIter<D: Dataset>(Vec<D>);

impl<D: Dataset> DatasetIterator for VecDatasetIter<D> {
    fn for_each_token_pair(self, mut f: impl FnMut(Token, Token)) {
        for dataset in self.0 {
            dataset.iter().for_each_token_pair(&mut f);
        }
    }

    fn split_work(self, _chunks: usize) -> Vec<Self>
    where
        Self: Sized,
    {
        self.0
            .into_iter()
            .map(|dataset| Self(vec![dataset]))
            .collect()
    }
}

#[derive(Debug, Constructor, Default)]
pub struct InMemoryDataset {
    chunks: Vec<Arc<[Token]>>,
}

impl Dataset for InMemoryDataset {
    type Iter = InMemoryDatasetIter;

    fn iter(&self) -> Self::Iter {
        InMemoryDatasetIter {
            chunks: self.chunks.iter().map(Arc::clone).collect(),
        }
    }

    fn update_tokenizer(&mut self, tokenizer: Tokenizer) {
        self.chunks
            .par_iter_mut()
            .progress_with_style({
                ProgressStyle::default_bar()
                    .template("Regeln werden angewandt: [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
        .expect("Ungültige Vorlage")
            })
            .for_each(|chunk| *chunk = tokenizer.tokenize(&mem::take(chunk)).into());
    }
}

impl InMemoryDataset {
    pub fn load_from_shards(shards: &[&(impl AsRef<Path> + Sync)], tokenizer: &Tokenizer) -> Self {
        let progress_bar = ProgressBar::new(shards.len() as u64).with_style(
            ProgressStyle::default_bar()
                .template("Laden der Shards: {spinner} [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
                .expect("Ungültige Vorlage"),
        );

        let chunks: Vec<Arc<[Token]>> = shards
            .par_iter() // Process shards in parallel
            .progress_with(progress_bar.clone())
            .flat_map(|path| {
                let data = fs::read(path).ok()?; // Read shard as bytes, skip on error
                Some(
                    data.split(|&byte| byte == 0xFF) // Split by separator
                        .filter(|chunk| !chunk.is_empty()) // Skip empty chunks
                        .map(|chunk| {
                            let tokens = tokenizer.tokenize_bytes(chunk);
                            Arc::from(tokens.into_boxed_slice())
                        })
                        .collect::<Vec<_>>(),
                )
            })
            .flatten() // Combine chunks across all shards
            .collect();

        progress_bar.finish_with_message("Laden abgeschlossen");
        Self { chunks }
    }
}

pub struct InMemoryDatasetIter {
    chunks: Vec<Arc<[Token]>>,
}

impl DatasetIterator for InMemoryDatasetIter {
    fn for_each_token_pair(self, mut f: impl FnMut(Token, Token)) {
        for chunk in self.chunks {
            for window in chunk.windows(2) {
                let [left_token, right_token] = [window[0], window[1]];
                f(left_token, right_token);
            }
        }
    }

    fn split_work(self, _parallelism: usize) -> Vec<Self>
    where
        Self: Sized,
    {
        const CHUNK_SIZE: usize = 1 << 12;
        self.chunks
            .into_iter()
            .chunks(CHUNK_SIZE)
            .into_iter()
            .map(|chunk| Self {
                chunks: chunk.collect(),
            })
            .collect()
    }
}

impl Sum for InMemoryDataset {
    fn sum<I: Iterator<Item = Self>>(iter: I) -> Self {
        let mut dataset = Self::default();
        for element in iter {
            dataset.chunks.extend(element.chunks);
        }
        dataset
    }
}

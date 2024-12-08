use regex::Match;
use std::{
    fs,
    fs::{File, OpenOptions},
    io::{BufReader, BufWriter, Write},
    path::{Path, PathBuf},
    sync::LazyLock,
};

use indicatif::{ParallelProgressIterator, ProgressStyle};
use itertools::Itertools;
use rayon::iter::{IndexedParallelIterator, IntoParallelIterator, ParallelIterator};
use regex::Regex;
use serde::Deserialize;

use super::{Dataset, DatasetIterator};
use crate::{Token, Tokenizer};

pub struct WikipediaDataset {
    directory: PathBuf,
    tokenizer: Tokenizer,
}

impl WikipediaDataset {
    #[must_use]
    pub fn new(directory: impl AsRef<Path>, tokenizer: Tokenizer) -> Self {
        Self {
            directory: directory.as_ref().to_owned(),
            tokenizer,
        }
    }

    pub fn to_disk(self, format_string: &str) {
        assert!(format_string.contains("{num}"));
        let style = ProgressStyle::default_bar().template("Abspeichern der Datensätze: {spinner} [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})").expect("Invalide Vorlage");

        self.iter()
            .files
            .into_par_iter()
            .chunks(1 << 17)
            .enumerate()
            .progress_with_style(style)
            .for_each(|(index, chunk)| {
                let file = OpenOptions::new()
                    .create(true)
                    .truncate(true)
                    .write(true)
                    .open(format_string.replace("{num}", &format!("{index:05}")))
                    .expect("IO-Fehler");
                let mut writer = BufWriter::new(file);
                for path in &chunk {
                    let entry = WikipediaDatasetIter::load_entry(path);
                    let text = WikipediaDatasetIter::prepare_string(&entry.text, &entry.title);
                    writer
                        .write_all(text.as_bytes())
                        .expect("Fehler beim Schreiben");
                    writer.write_all(&[0xFF]).expect("Schreibfehler");
                }
            });
    }
}

impl Dataset for WikipediaDataset {
    type Iter = WikipediaDatasetIter;

    fn iter(&self) -> WikipediaDatasetIter {
        let mut files = fs::read_dir(&self.directory)
            .expect("Invalid path")
            .map(|res| res.map(|e| e.path()))
            .collect::<Result<Vec<_>, _>>()
            .expect("Invalid directory");
        files.retain(|file| {
            file.extension()
                .is_some_and(|extension| extension == "json")
        });

        WikipediaDatasetIter {
            files,
            tokenizer: self.tokenizer.clone(),
        }
    }
}

#[derive(Deserialize)]
pub struct Entry {
    title: String,
    text: String,
}

pub struct WikipediaDatasetIter {
    files: Vec<PathBuf>,
    tokenizer: Tokenizer,
}

impl WikipediaDatasetIter {
    fn load_entry(path: &Path) -> Entry {
        let file = File::open(path).expect("IO-Fehler");
        let reader = BufReader::new(file);
        serde_json::from_reader(reader).expect("Serialisierungsfehler")
    }

    fn prepare_string(string: &str, title: &str) -> String {
        const EQUALS: [&str; 7] = ["", "=", "==", "===", "====", "=====", "======"];
        static DUPLICATE_HEADING_RE: LazyLock<Regex> = LazyLock::new(|| {
            Regex::new(r"= =").expect("Ungültiger regulärer Ausdruck")
        });
        static HEADING_RE: LazyLock<Regex> = LazyLock::new(|| {
            let base_regex = r"(?m)(?:\s|^)(?P<equals{n}>{n_e})\s(?P<title{n}>[^=]+?)(?:(?:\s{n_e})|\s*$)";
            let regex = (2..=6)
                .map(|n| base_regex.replace("{n_e}", EQUALS[n]).replace("{n}", &n.to_string()))
                .join("|");
            Regex::new(&regex).expect("Ungültiger regulärer Ausdruck")
        });
        static BULLET_RE: LazyLock<Regex> =
            LazyLock::new(|| Regex::new(r"\s\*+\s\*?\s?").expect("Ungültiger regulärer Ausdruck"));
        static SUPERFLUOUS_HEADINGS_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\n{3,}").expect("Ungültiger regulärer Ausdruck"));

        const HASHES: [&str; 7] = ["", "#", "##", "###", "####", "#####", "######"];

        let dupe_headings_replaced = DUPLICATE_HEADING_RE.replace_all(string, "=\n=");
        let heading_replaced = HEADING_RE.replace_all(&dupe_headings_replaced, |caps: &regex::Captures| {
            for n in 2..=6 {
                let equals = &caps.name(&format!("equals{n}"));
                let title = &caps.name(&format!("title{n}"));
                let [Some(equals), Some(title)] = [equals, title] else { continue };
                let [equals, section_title] = [equals, title].map(Match::as_str);
                let hashes = HASHES[equals.len()];
                return format!("\n\n{hashes} {section_title}\n\n")
            }
            unreachable!();
        });
        let bullet_replaced = BULLET_RE.replace_all(&heading_replaced, "\n- ");
        let newlines_normalized = SUPERFLUOUS_HEADINGS_RE.replace_all(&bullet_replaced, "\n\n");

        // format!("{string}\n\n")
        format!("# {title}\n\n{newlines_normalized}")
    }
}

impl DatasetIterator for WikipediaDatasetIter {
    fn for_each_token_pair(self, mut f: impl FnMut(Token, Token)) {
        for path in self.files {
            let entry = Self::load_entry(&path);
            let text = Self::prepare_string(&entry.text, &entry.title);
            let tokenized = self.tokenizer.tokenize_bytes(text.as_bytes());
            for pair in tokenized.windows(2) {
                f(pair[0], pair[1]);
            }
        }
    }
}

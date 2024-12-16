use std::{
    fs::{self, File, OpenOptions},
    io::{Seek, SeekFrom, Write},
    path::Path,
    str::FromStr,
};

use itertools::{chain, Itertools};

use crate::{Token, Tokenizer};

#[derive(Copy, Clone, Debug)]
pub struct MergeRule {
    pub left: Token,
    pub right: Token,
    pub result: Token,
}

const VOCAB_SIZE: usize = 50_000;

#[derive(Debug)]
pub struct BpeState {
    vocab: Vec<Vec<u8>>,
    merges: Vec<MergeRule>,
    file: File,
}

impl BpeState {
    #[must_use]
    pub fn empty() -> Self {
        Self::synced_with_file("/dev/null")
    }

    #[must_use]
    pub fn synced_with_file(path: impl AsRef<Path> + Clone) -> Self {
        Self::with_merge_capacity(VOCAB_SIZE, path)
    }

    #[must_use]
    pub fn add_token(&mut self, left: Token, right: Token) -> Token {
        #![allow(clippy::cast_possible_truncation)]
        let left_assoc = &self.vocab[left.index()];
        let right_assoc = &self.vocab[right.index()];
        let token_string: Vec<u8> = left_assoc.iter().chain(right_assoc).copied().collect();
        let new_token = Token::new(self.vocab.len() as u16);
        self.merges.push(MergeRule {
            left,
            right,
            result: new_token,
        });
        self.vocab.push(token_string);
        writeln!(
            self.file,
            "{} {} {}",
            left.index(),
            right.index(),
            new_token.index()
        )
        .expect("IO-Fehler");
        new_token
    }

    pub fn remove_token_unsynced(&mut self, token: Token) {
        assert!(
            self.vocab.get(token.index()).is_some(),
            "Token is not contained in this vocabulary"
        );
        assert!(
            !self
                .merges
                .iter()
                .any(|rule| rule.left == token || rule.right == token),
            "Token is used in further merge rules"
        );
        let index = token.index();
        self.vocab.remove(index); // O(n)
        self.merges.remove(index - 256);
        for merge in &mut self.merges {
            if merge.left.index() > index {
                merge.left = Token::new(merge.left.into_inner() - 1)
            }
            if merge.right.index() > index {
                merge.right = Token::new(merge.right.into_inner() - 1)
            }
            if merge.result.index() > index {
                merge.result = Token::new(merge.result.into_inner() - 1)
            }
        }
    }

    pub fn sync(&mut self) {
        self.file.set_len(0).expect("Could not reset file");
        self.file
            .seek(SeekFrom::Start(0))
            .expect("Could not seek file");

        for MergeRule {
            left,
            right,
            result: new_token,
        } in &self.merges
        {
            writeln!(
                self.file,
                "{} {} {}",
                left.index(),
                right.index(),
                new_token.index()
            )
            .expect("IO-Fehler");
        }
    }

    /// # Panics
    /// Panics if the provided file is not in the following format:
    /// Each line must contain exactly three base-10 positive integers < 65536,
    /// and the last one in each line must start with 256 and be incremented.
    #[must_use]
    pub fn with_merge_capacity(merges: usize, path: impl AsRef<Path> + Clone) -> Self {
        let merges = fs::read_to_string(path.clone()).ok().map_or_else(
            || Vec::with_capacity(merges),
            |string| {
                string
                    .lines()
                    .map(|line| {
                        line.splitn(3, ' ')
                            .map(|num| u16::from_str(num).expect("Ungültige Zahl"))
                            .map(Token::new)
                            .collect_tuple()
                            .expect("Erwartete drei Zahlen")
                    })
                    .map(|(left, right, result)| MergeRule {
                        left,
                        right,
                        result,
                    })
                    .collect_vec()
            },
        );

        let mut vocab = (0..=u8::MAX).map(|byte| vec![byte]).collect_vec();
        for &MergeRule {
            left,
            right,
            result,
        } in &merges
        {
            assert_eq!(result.index(), vocab.len());
            vocab.push(chain(vocab[left.index()].clone(), vocab[right.index()].clone()).collect());
        }

        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
            .expect("Datei konnte nicht geöffnet werden");
        Self {
            vocab,
            merges,
            file,
        }
    }

    #[must_use]
    pub fn additional_vocab_size(&self) -> usize {
        self.merges.len()
    }

    #[must_use]
    pub fn at_token(&self, token: Token) -> &[u8] {
        &self.vocab[token.index()]
    }

    #[must_use]
    pub fn tokenizer(&self) -> Tokenizer {
        Tokenizer::from_rules(self.merges.iter().copied())
    }

    #[must_use]
    pub fn vocab(&self) -> Vec<&[u8]> {
        self.vocab.iter().map(|v| &**v).collect()
    }

    #[must_use]
    pub fn tokens(&self) -> Vec<Token> {
        (0u16..self.vocab.len() as u16).map(Token::new).collect()
    }
}

impl Default for BpeState {
    fn default() -> Self {
        Self::empty()
    }
}

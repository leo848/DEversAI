use std::fmt::{Debug, Display};

use derive_more::derive::Constructor;

use crate::{BpeState, MergeRule};

#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Constructor, Hash)]
pub struct Token(u16);

impl Token {
    #[must_use]
    pub fn index(self) -> usize {
        self.0.into()
    }

    #[allow(dead_code)]
    #[must_use]
    pub fn display_with_state(self, state: &'_ BpeState) -> impl Display + '_ {
        String::from_utf8_lossy(state.at_token(self))
            .replace('\n', "\\n")
            .replace(' ', "⎵")
    }
}

impl Debug for Token {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        Debug::fmt(&self.0, f)
    }
}

#[derive(Clone, Debug)]
pub struct Tokenizer {
    rules: Vec<MergeRule>,
    new: usize,
}

impl Tokenizer {
    #[must_use]
    pub fn from_rules(rules: impl Iterator<Item = MergeRule>) -> Self {
        let rules: Vec<_> = rules.collect();
        Self {
            new: rules.len(),
            rules,
        }
    }

    pub fn set_new(&mut self, new: Option<usize>) {
        self.new = new.unwrap_or(self.rules.len());
    }

    #[must_use]
    pub fn tokenize_bytes(&self, bytes: &[u8]) -> Vec<Token> {
        let tokens: Vec<Token> = bytes
            .iter()
            .map(|byte| Token::new((*byte).into()))
            .collect();
        self.tokenize(&tokens)
    }

    pub fn tokenize(&self, tokens: &[Token]) -> Vec<Token> {
        let mut tokens = tokens.to_vec();
        for &MergeRule {
            left,
            right,
            result,
        } in &self.rules[self.rules.len() - self.new..]
        {
            let mut new_tokens = Vec::with_capacity(tokens.len());
            let mut merged = false;
            for window in tokens.windows(2) {
                if merged {
                    merged = false;
                    continue;
                }
                let [left_present, right_present] = [window[0], window[1]];
                if left == left_present && right == right_present {
                    new_tokens.push(result);
                    merged = true;
                } else {
                    new_tokens.push(left_present);
                }
            }
            if !merged {
                if let Some(&last_token) = tokens.last() {
                    new_tokens.push(last_token);
                }
            }
            tokens = new_tokens;
        }

        tokens
    }
}

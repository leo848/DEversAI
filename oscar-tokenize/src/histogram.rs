use itertools::chain;
use std::{
    collections::{HashMap, HashSet},
    fmt::Display,
    iter::Sum,
    num::NonZeroU64,
    ops::AddAssign,
};

use dashmap::DashMap;
use itertools::Itertools;

use crate::{BpeState, Count, Token, TrainConfig};

#[derive(Clone, PartialEq, Eq)]
pub struct TokenHistogram {
    tokens: Box<[Count; 0xffff]>,
    token_pairs: HashMap<(Token, Token), Count>,
}

impl TokenHistogram {
    #[must_use]
    pub fn new() -> Self {
        #[allow(clippy::large_stack_arrays)]
        Self {
            tokens: Box::new([Count::default(); 0xffff]),
            token_pairs: HashMap::new(),
        }
    }

    pub fn register(&mut self, token: Token) {
        self.tokens[token.index()] += 1;
    }

    pub fn register_n(&mut self, token: Token, n: u64) {
        self.tokens[token.index()] += n;
    }

    pub fn register_pair(&mut self, left: Token, right: Token) {
        *self.token_pairs.entry((left, right)).or_default() += 1;
    }

    #[allow(dead_code)]
    #[must_use]
    pub fn display_with_state(&self, state: &BpeState) -> impl Display {
        let mut string = String::new();
        let top10_tokens = self
            .tokens
            .iter()
            .enumerate()
            .sorted_by_key(|&(_, v)| v.by_key_desc())
            .take(10);
        let top10_pairs = self
            .token_pairs
            .iter()
            .sorted_by_key(|&(_, v)| v.by_key_desc())
            .take(10);
        for ((token, count), ((pair_l, pair_r), pair_count)) in top10_tokens.zip(top10_pairs) {
            let token = Token::new(token as u16).display_with_state(state);
            string += &format!("{token:>20}:    {count}    │    ");

            let [pair_l, pair_r] = [pair_l, pair_r].map(|token| token.display_with_state(state));
            let token_pair = format!("{pair_l} -> {pair_r}");
            string += &format!("{token_pair:>20}:    {pair_count}\n");
        }
        string
    }

    #[allow(dead_code)]
    #[must_use]
    pub fn display_tokens_with_state(&self, state: &BpeState) -> impl Display {
        let mut string = String::new();
        let top10_tokens = self
            .tokens
            .iter()
            .enumerate()
            .sorted_by_key(|&(_, v)| v.by_key_desc())
            .take(10);
        for (token, count) in top10_tokens {
            let token = Token::new(token as u16).display_with_state(state);
            string += &format!("{token:>20}:    {count}\n");
        }
        string
    }

    pub fn merges_to_add<'a>(&'a self, tokens: Vec<Vec<u8>>, config: &'a TrainConfig, t: f64) -> impl Iterator<Item = (Token, Token)> + 'a {
        #[derive(Default)]
        struct State {
            top_count: Option<NonZeroU64>,
            disallowed_tokens_left: HashSet<Token>,
            disallowed_tokens_right: HashSet<Token>,
        }
        let eta = config.eta.for_t(t);
        self.token_pairs
            .iter()
            .sorted_by_key(|&(_, count)| count.by_key_desc())
            .scan(
                State::default(),
                move |state, (&(token_left, token_right), &count)| {
                    if state.top_count.is_none() {
                        state.top_count = NonZeroU64::new(count.into_inner());
                    }
                    let merged_bytes = chain(tokens[token_left.index()].clone(), tokens[token_right.index()].clone()).collect_vec();
                    if config.max_token_length.is_some_and(|max_len| merged_bytes.len() > max_len) {
                        return Some(None);
                    }
                    if config.forbidden_patterns.is_match(&merged_bytes) {
                        return None;
                    }

                    // Direction is correct: a token must not end with the start token,
                    state.disallowed_tokens_left.insert(token_right);
                    // or start with the end token.
                    state.disallowed_tokens_right.insert(token_left);

                    if state.disallowed_tokens_left.contains(&token_left)
                        || state.disallowed_tokens_right.contains(&token_right)
                    {
                        Some(None)
                    } else {
                        Some(Some((
                            token_left,
                            token_right,
                            state
                                .top_count
                                .map_or(1.0, |top_count| count.float() / top_count.get() as f64),
                        )))
                    }
                },
            )
            .flatten()
            .take_while(move |&(_, _, factor)| factor >= eta)
            .map(|(left, right, _)| (left, right))
    }

    #[must_use]
    pub fn get_pair(&self, left: Token, right: Token) -> Count {
        self.token_pairs
            .get(&(left, right))
            .copied()
            .unwrap_or_default()
    }

    #[must_use]
    pub fn len_pairs(&self) -> Count {
        Count::new(self.token_pairs.len() as u64)
    }

    #[must_use]
    pub fn get_token(&self, token: Token) -> Count {
        self.tokens.get(token.index()).copied().unwrap_or_default()
    }
}

impl Default for TokenHistogram {
    fn default() -> Self {
        Self::new()
    }
}

impl AddAssign for TokenHistogram {
    fn add_assign(&mut self, rhs: Self) {
        for i in 0..0xffff {
            self.tokens[i] += rhs.tokens[i];
        }
        for &key in rhs.token_pairs.keys() {
            *self.token_pairs.entry(key).or_default() +=
                rhs.token_pairs.get(&key).copied().unwrap_or_default();
        }
        drop(rhs);
    }
}

impl Sum for TokenHistogram {
    fn sum<I: Iterator<Item = Self>>(iter: I) -> Self {
        let mut th = TokenHistogram::new();
        for other in iter {
            th += other;
        }
        th
    }
}

#[derive(Clone)]
pub struct TokenHistogramShared {
    token_pairs: DashMap<(Token, Token), Count>,
}
impl TokenHistogramShared {
    #[must_use]
    pub fn new() -> Self {
        #[allow(clippy::large_stack_arrays)]
        Self {
            token_pairs: DashMap::new(),
        }
    }

    pub fn register_pair(&self, left: Token, right: Token) {
        *self.token_pairs.entry((left, right)).or_default() += 1;
    }

    #[allow(dead_code)]
    #[must_use]
    pub fn display_with_state(&self, state: &BpeState) -> impl Display {
        let mut string = String::new();
        let top10_pairs = self
            .token_pairs
            .iter()
            .map(|rm| (*rm.key(), *rm.value()))
            .sorted_by_key(|&(_, v)| v.by_key_desc())
            .take(10);
        for ((pair_l, pair_r), pair_count) in top10_pairs {
            let [pair_l, pair_r] = [pair_l, pair_r].map(|token| token.display_with_state(state));
            let token_pair = format!("{pair_l} -> {pair_r}");
            string += &format!("{token_pair:>20}:    {pair_count}\n");
        }
        string
    }

    pub fn merges_to_add(&self, eta: f64) -> impl Iterator<Item = (Token, Token)> + '_ {
        #[derive(Default)]
        struct State {
            top_count: Option<NonZeroU64>,
            disallowed_tokens_left: HashSet<Token>,
            disallowed_tokens_right: HashSet<Token>,
        }
        self.token_pairs
            .iter()
            .map(|rm| (*rm.key(), *rm.value()))
            .sorted_by_key(|&(_, count)| count.by_key_desc())
            .scan(
                State::default(),
                |state, ((token_left, token_right), count)| {
                    if state.top_count.is_none() {
                        state.top_count = NonZeroU64::new(count.into_inner());
                    }
                    if state.disallowed_tokens_left.contains(&token_left)
                        || state.disallowed_tokens_right.contains(&token_right)
                    {
                        Some(None)
                    } else {
                        // Direction is correct: a token must not end with the start token,
                        state.disallowed_tokens_left.insert(token_right);
                        // or start with the end token.
                        state.disallowed_tokens_right.insert(token_left);
                        Some(Some((
                            token_left,
                            token_right,
                            state
                                .top_count
                                .map_or(1.0, |top_count| count.float() / top_count.get() as f64),
                        )))
                    }
                },
            )
            .flatten()
            .take_while(move |&(_, _, factor)| factor >= eta)
            .map(|(left, right, _)| (left, right))
    }

    #[must_use]
    pub fn get_pair(&self, left: Token, right: Token) -> Count {
        self.token_pairs
            .get(&(left, right))
            .map(|result| *result.value())
            .unwrap_or_default()
    }

    #[must_use]
    pub fn len_pairs(&self) -> Count {
        Count::new(self.token_pairs.len() as u64)
    }
}

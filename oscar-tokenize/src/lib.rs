#![warn(clippy::pedantic)]
#![allow(clippy::cast_precision_loss)]
#![allow(clippy::cast_possible_truncation)]
#![allow(clippy::module_name_repetitions)]
#![allow(clippy::unnecessary_wraps)]
#![allow(clippy::iter_not_returning_iterator)]

mod bpe_state;
mod config;
mod count;
pub mod dataset;
mod histogram;
mod token;

pub use bpe_state::{BpeState, MergeRule};
pub use config::TrainConfig;
pub use count::Count;
pub use dataset::{Dataset, DatasetIterator};
pub use histogram::TokenHistogram;
pub use token::{Token, Tokenizer};

use std::{fmt::Debug, ops::Range, sync::Arc};

use regex::bytes::{self, RegexSet};

use crate::Count;

#[derive(Debug, Clone)]
pub struct TrainConfig {
    pub eta: EtaScheduler,
    pub max_token_length: Option<usize>,
    pub target_vocab_size: usize,
    pub forbidden_patterns: bytes::RegexSet,
}

impl Default for TrainConfig {
    fn default() -> Self {
        Self {
            eta: EtaScheduler::constant(0.5),
            max_token_length: None,
            target_vocab_size: 50_000,
            forbidden_patterns: RegexSet::empty(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct TrainResult {
    pub new_token_count: Count,
}

#[derive(Clone)]
pub struct EtaScheduler(Arc<dyn Fn(f64) -> f64>);

impl Debug for EtaScheduler {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "EtaScheduler <fn {:?}>", std::ptr::from_ref(&self.0))
    }
}

impl EtaScheduler {
    #[must_use]
    pub fn constant(value: f64) -> Self {
        Self::from_fn(move |_| value)
    }

    #[must_use]
    pub fn linear_transition(Range { start, end }: Range<f64>) -> Self {
        Self::from_fn(move |t| start + (end - start) * t)
    }

    #[must_use]
    pub fn piecewise_linear_two(split_point: f64, values: [f64; 3]) -> Self {
        assert!((0.0..=1.0).contains(&split_point));
        Self::from_fn(move |t| {
            if t < split_point {
                values[0] + (values[1] - values[0]) * (t / split_point)
            } else {
                values[1] + (values[2] - values[1]) * ((t - split_point) / (1.0 - split_point))
            }
        })
    }

    #[must_use]
    pub fn from_fn(function: impl Fn(f64) -> f64 + 'static) -> Self {
        Self(Arc::new(function))
    }

    #[must_use]
    pub fn for_t(&self, t: f64) -> f64 {
        self.0(t)
    }
}

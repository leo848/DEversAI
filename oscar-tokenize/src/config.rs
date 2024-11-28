use crate::Count;

#[derive(Debug, Clone, Copy)]
pub struct TrainConfig {
    pub eta: f64,
    pub max_token_length: Option<usize>,
}

impl Default for TrainConfig {
    fn default() -> Self {
        Self {
            eta: 0.5,
            max_token_length: None,
        }
    }
}

#[derive(Debug, Clone)]
pub struct TrainResult {
    pub new_token_count: Count,
}

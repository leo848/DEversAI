#![warn(clippy::pedantic)]
#![allow(clippy::cast_precision_loss)]
#![allow(clippy::cast_possible_truncation)]
#![allow(clippy::module_name_repetitions)]
#![allow(clippy::unnecessary_wraps)]

use oscar_tokenize::EtaScheduler;
use std::path::PathBuf;
use std::time::Instant;

use itertools::{chain, Itertools};
use oscar_tokenize::{
    dataset::InMemoryDataset,
    BpeState, Dataset, TrainConfig,
};

fn main() {
    let mut bpe_state = BpeState::synced_with_file("/output/german-complete.vocab");

    println!("=== Vokabular ===\n");
    for token in bpe_state.tokens() {
        print!("{} ", token.display_with_state(&bpe_state));
    }
    println!();

    let paths = chain(
        (0..500).map(|i| format!("/data/oscar-2301-shard-{i:05}.bin")),
        (0..23).map(|i| format!("/data/wikipedia-shard-{i:05}.bin")),
    ).map(PathBuf::from).collect_vec();

    println!("Loading dataset from {} shards.", paths.len());
    let mut dataset = InMemoryDataset::load_from_shards(
        &paths.iter().collect_vec(),
        &bpe_state.tokenizer(),
    );

    let config = TrainConfig {
        eta: EtaScheduler::piecewise_linear_two(0.5, [0.75, 0.75, 0.85]),
        max_token_length: None,
        target_vocab_size: 60_000,
    };

    let start_time = Instant::now();

    loop {
        println!("Starting next train step ({}/{})", bpe_state.additional_vocab_size(), config.target_vocab_size);
        let result = dataset.train_step(&mut bpe_state, &config);

        println!(
            "\n{new_token_count} Tokens nach {:?} hinzufügt",
            start_time.elapsed(),
            new_token_count = result.new_token_count,
        );
        println!("Neue Vokabulargröße: {}", bpe_state.additional_vocab_size());

        if bpe_state.additional_vocab_size() > config.target_vocab_size {
            break;
        }

        let mut new_tokenizer = bpe_state.tokenizer();
        new_tokenizer.set_new(Some(result.new_token_count.into_inner() as usize));
        println!("Updating tokenizer, tokenizing memory.");
        dataset.update_tokenizer(new_tokenizer);
    }

    println!("Vocabulary fully trained. Manual filtering required next.")
}

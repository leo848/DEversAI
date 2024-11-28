#![warn(clippy::pedantic)]
#![allow(clippy::cast_precision_loss)]
#![allow(clippy::cast_possible_truncation)]
#![allow(clippy::module_name_repetitions)]
#![allow(clippy::unnecessary_wraps)]

use std::time::Instant;

use oscar_tokenize::{dataset::HuggingfaceShardsDataset, BpeState, Dataset, TrainConfig};

fn main() {
    let mut bpe_state = BpeState::synced_with_file("bpe-memory-eta-0-5.vocab");

    print!("=== Vokabular ===");
    for token in bpe_state.tokens() {
        print!("{} ", token.display_with_state(&bpe_state));
    }
    println!();

    let mut dataset = HuggingfaceShardsDataset::new(
    "/home/l.blume/.cache/huggingface/datasets/oscar-corpus___oscar-2301/de-language=de/0.0.0/156efb8ba9f439f881d8f41fd7fddd5e04604bc27505c46ddef015f2fc551a4a/oscar-2301-train-{num}-of-{max}.arrow",
        1383,
        bpe_state.tokenizer()
    ).to_memory(0..24);

    let config = TrainConfig {
        eta: 0.5,
        max_token_length: None,
        ..Default::default()
    };

    let start_time = Instant::now();

    while bpe_state.additional_vocab_size() < 50_000 {
        let result = dataset.train_step(&mut bpe_state, config);

        println!(
            "\n{new_token_count} Tokens nach {:?} hinzufügt",
            start_time.elapsed(),
            new_token_count = result.new_token_count,
        );
        println!("Neue Vokabulargröße: {}", bpe_state.additional_vocab_size());

        let mut new_tokenizer = bpe_state.tokenizer();
        new_tokenizer.set_new(Some(result.new_token_count.into_inner() as usize));
        dataset.update_tokenizer(new_tokenizer);
    }
}

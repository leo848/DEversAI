#![warn(clippy::pedantic)]
#![allow(clippy::cast_precision_loss)]
#![allow(clippy::cast_possible_truncation)]
#![allow(clippy::module_name_repetitions)]
#![allow(clippy::unnecessary_wraps)]

use std::{path::PathBuf, time::Instant};

use itertools::{chain, Itertools};
use oscar_tokenize::{
    dataset::InMemoryDataset, BpeState, Dataset, EtaScheduler, Token, TrainConfig,
};
fn main() {
    let mut bpe_state = BpeState::synced_with_file("/output/german-complete.vocab");

    dbg!(bpe_state.additional_vocab_size());

    let blacklist: &[&[u8]] = &[
        b"Cookies",
        b"Google",
        b"Facebook",
        "Datenschutzerklärung".as_bytes(),
        b"Website ",
    ];

    let word_count = |token: Token| {
        token.display_with_state(&bpe_state).to_string().split_whitespace()
            .filter(|m| m.len() != 0)
            .count()
    };

    let sixteen_bytes = |token| bpe_state.at_token(token).len() >= 16;
    let three_words = |token| word_count(token) >= 3;
    let in_blacklist = |token| {
        blacklist.iter().any(|&term| {
            bpe_state
                .at_token(token)
                .windows(term.len())
                .any(|window| window == term)
        })
    };
    let two_words_at_end = |token: Token| token.index() >= 40530 && word_count(token) >= 2;

    let tokens_removed = bpe_state
        .tokens()
        .iter()
        .copied()
        .filter(|&token| {
            sixteen_bytes(token)
                || three_words(token)
                || in_blacklist(token)
                || two_words_at_end(token)
        })
        .sorted_by_key(|token| usize::MAX - token.index());

    dbg!(tokens_removed.len());

    for token in tokens_removed {
        bpe_state.remove_token(token);
    }

    for token in bpe_state.tokens() {
        // println!("{}", token.display_with_state(&bpe_state));
    }
    dbg!(bpe_state.additional_vocab_size());
}

#[allow(dead_code)]
fn train_vocabulary(bpe_state: &mut BpeState) {
    println!("=== Vokabular ===\n");
    for token in bpe_state.tokens() {
        print!("{} ", token.display_with_state(&bpe_state));
    }
    println!();

    let paths = chain!(
        (256..512).map(|i| format!("/data/oscar-2301-shard-{i:05}.bin")),
        (0..23).map(|i| format!("/data/wikipedia-shard-{i:05}.bin")),
        (0..23).map(|i| format!("/data/wikipedia-shard-{i:05}.bin")),
    )
    .map(PathBuf::from)
    .collect_vec();

    println!("Loading dataset from {} shards.", paths.len());
    let mut dataset =
        InMemoryDataset::load_from_shards(&paths.iter().collect_vec(), &bpe_state.tokenizer());

    let config = TrainConfig {
        eta: EtaScheduler::piecewise_linear_two(0.3, [0.8, 0.8, 0.9]),
        max_token_length: None,
        target_vocab_size: 60_000,
    };

    let start_time = Instant::now();

    loop {
        println!(
            "Starting next train step ({}/{})",
            bpe_state.additional_vocab_size(),
            config.target_vocab_size
        );
        let result = dataset.train_step(bpe_state, &config);

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

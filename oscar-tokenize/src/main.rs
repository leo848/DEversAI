#![warn(clippy::pedantic)]
#![allow(clippy::cast_precision_loss)]
#![allow(clippy::cast_possible_truncation)]
#![allow(clippy::module_name_repetitions)]
#![allow(clippy::unnecessary_wraps)]

use std::{
    collections::HashMap,
    env::args,
    fmt::write,
    fs::{self, File, OpenOptions},
    io::{BufRead, BufReader, BufWriter, Read, Seek, SeekFrom, Write},
    iter::once,
    path::PathBuf,
    process::exit,
    time::Instant,
};

use indicatif::{ParallelProgressIterator, ProgressStyle};
use itertools::{chain, Itertools};
use oscar_tokenize::{
    dataset::InMemoryDataset, BpeState, Dataset, EtaScheduler, Token, TokenHistogram, TrainConfig,
};
use rayon::iter::{IntoParallelIterator, ParallelIterator};
use regex::Regex;

#[allow(dead_code)]
pub fn main() {
    const EXAMPLE_COUNT: usize = 1;
    const TOKENS_CONTEXT: usize = 100;

    let paths = args().skip(1).map(PathBuf::from).collect_vec();

    let bpe_state = BpeState::synced_with_file("/vocab/german-complete.vocab");

    let mut token_examples = HashMap::<Token, Vec<Box<[Token]>>>::new();

    let tokens = bpe_state.tokens();
    for token in tokens {
        if token.index() < 256 {
            continue;
        }
        let path = &paths[fastrand::usize(..paths.len())];
        let file = File::open(path).expect("File should exist");
        let size_bytes = file.metadata().expect("File should have metadata").len();
        let mut reader = BufReader::new(file);

        let seek_bytes = fastrand::u64(0..size_bytes / 2) & !1; // ensure divisibility by two
        reader
            .seek(SeekFrom::Start(seek_bytes))
            .expect("Failed to seek");

        let mut buffer = [0u8; 2];
        while let Ok(_) = reader.read_exact(&mut buffer) {
            let found_token = Token::new(u16::from_be_bytes(buffer));
            if found_token != token {
                continue;
            }
            let mut bytes_after = [0u8; TOKENS_CONTEXT * 2];
            reader
                .read_exact(&mut bytes_after)
                .expect("Failed to read right context");
            let mut bytes_before = [0u8; TOKENS_CONTEXT * 2];
            reader
                .seek_relative(-(TOKENS_CONTEXT as i64) * 4 - 2)
                .expect("Failed to seek");
            reader
                .read_exact(&mut bytes_before)
                .expect("Failed to read right context");

            let bytes_to_tokens = move |bytes: [u8; TOKENS_CONTEXT * 2]| {
                bytes
                    .into_iter()
                    .chunks(2)
                    .into_iter()
                    .map(|chunk| {
                        let chunk = chunk.collect_vec();
                        Token::new(u16::from_be_bytes([chunk[0], chunk[1]]))
                    })
                    .collect_vec()
            };

            let [ctx_before, ctx_after] = [bytes_before, bytes_after]
                .map(|bytes| bytes_to_tokens(bytes))
                .map(|tokens| {
                    tokens
                        .iter()
                        .flat_map(|&token| bpe_state.at_token(token))
                        .copied()
                        .collect_vec()
                })
                .map(|bytes| String::from_utf8_lossy(&bytes).into_owned());

            let split_many = |before: bool| {
                move |mut string: String, delims: &[&str]| {
                    for delim in delims {
                        if before {
                            string = string
                                .rsplit_once(delim)
                                .map(|(_, right)| right.to_owned())
                                .unwrap_or(string);
                        } else {
                            string = string
                                .split_once(delim)
                                .map(|(left, _)| left.to_owned() + delim)
                                .unwrap_or(string);
                        }
                    }
                    string.to_owned()
                }
            };
            let split_before = split_many(true);
            let split_after = split_many(false);

            let patterns = &["\n", ". ", "#"];

            let str_before = split_before(ctx_before, patterns);
            let str_after = split_after(ctx_after, patterns);

            println!(
                "{str_before}\x1B[1;31m{}\x1B[0m{str_after}",
                token.display_with_state(&bpe_state)
            );
            exit(1)
        }
    }
}

#[allow(dead_code)]
fn count_tokens() {
    let bpe_state = BpeState::synced_with_file("/vocab/german-complete.vocab");

    let paths = args().skip(1).map(PathBuf::from).collect_vec();

    let [mut direct_histogram_file, mut transitive_histogram_file] = [
        "/output/direct_histogram.txt",
        "/output/transitive_histogram.txt",
    ]
    .map(|path| {
        let file = OpenOptions::new()
            .create(true)
            .write(true)
            .truncate(true)
            .open(&path)
            .expect("Failed to open file");
        BufWriter::new(file)
    });

    let direct_histogram = paths
        .into_par_iter()
        .map(|path| {
            let mut reader = BufReader::new(File::open(path).expect("Failed to open file"));

            let mut histogram = TokenHistogram::new();
            let mut buffer = [0u8; 2];
            while let Ok(_) = reader.read_exact(&mut buffer) {
                let token = Token::new(u16::from_be_bytes(buffer));
                histogram.register(token);
            }
            histogram
        })
        .progress()
        .sum::<TokenHistogram>();

    let mut transitive_histogram = direct_histogram.clone();
    for &token in bpe_state.tokens().iter().rev() {
        let Some((left, right)) = bpe_state.split_token(token) else {
            continue;
        };
        transitive_histogram.register_n(left, transitive_histogram.get_token(token).into_inner());
        transitive_histogram.register_n(right, transitive_histogram.get_token(token).into_inner());
    }

    for &token in bpe_state.tokens().iter() {
        writeln!(
            direct_histogram_file,
            "{}",
            direct_histogram.get_token(token).into_inner()
        )
        .expect("IO error");
        writeln!(
            transitive_histogram_file,
            "{}",
            transitive_histogram.get_token(token).into_inner()
        )
        .expect("IO error");
    }
    direct_histogram_file.flush().expect("IO-Fehler");
    transitive_histogram_file.flush().expect("IO-Fehler");
}

#[allow(dead_code)]
fn tokenize_corpora() {
    let bpe_state = BpeState::synced_with_file("/vocab/german-complete.vocab");

    let paths = chain!(
        (0..23).map(|i| format!("wikipedia-shard-{i:05}.bin")),
        (0..600).map(|i| format!("oscar-2301-shard-{i:05}.bin")),
    )
    .map(PathBuf::from)
    .collect_vec();

    paths
        .into_par_iter()
        .progress_with_style({
                ProgressStyle::default_bar()
                    .template("Tokenizing der Korpora: [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
                    .expect("Template-Fehler")
        })
        .for_each(|path| {

        let input_path = format!("/input/{}", path.display());
        let output_path = format!("/output/{}", path.display());

            let file = fs::read(input_path).expect("Failed to read file");
            let tokens = bpe_state.tokenizer().tokenize_bytes(&file);

            let output_file = OpenOptions::new().write(true).create(true).append(false).truncate(true).open(output_path).expect("Failed to open output file");
            let mut output_writer = BufWriter::new(output_file);

            for token in tokens {
                output_writer.write_all(&token.into_inner().to_be_bytes()).expect("Could not write to file");
            }
            output_writer.flush().expect("Could not flush to file");
        });
}

#[allow(dead_code)]
fn reduce_vocab_size() {
    let mut bpe_state = BpeState::synced_with_file("/output/german-complete.vocab");

    dbg!(bpe_state.additional_vocab_size());

    let space_regex = Regex::new(r"\s").expect("Could not build regex");

    let blacklist: &[&[u8]] = &[
        b"Cookies",
        b"Google",
        b"Facebook",
        "Datenschutzerklärung".as_bytes(),
        b"Website ",
    ];

    let word_count = |token: Token| {
        space_regex
            .split(&token.to_string_raw(&bpe_state).to_string())
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
        bpe_state.remove_token_unsynced(token);
    }
    bpe_state.sync();

    for token in bpe_state.tokens() {
        println!("{}", token.display_with_state(&bpe_state));
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

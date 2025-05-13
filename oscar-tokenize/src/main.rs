#![warn(clippy::pedantic)]
#![allow(clippy::cast_precision_loss)]
#![allow(clippy::cast_possible_truncation)]
#![allow(clippy::module_name_repetitions)]
#![allow(clippy::unnecessary_wraps)]

use std::{
    collections::BTreeSet,
    env::args,
    fs::{self, File, OpenOptions},
    io::{BufReader, BufWriter, Read, Seek, SeekFrom, Write},
    path::{Path, PathBuf},
    time::Instant,
};

use indicatif::{ParallelProgressIterator, ProgressIterator, ProgressStyle};
use itertools::{chain, Itertools};
use oscar_tokenize::{
    dataset::InMemoryDataset, xml, BpeState, Dataset, EtaScheduler, Token, TokenHistogram,
    TrainConfig,
};
use rayon::iter::{IntoParallelIterator, ParallelIterator};
use regex::bytes::RegexSet;
use rusqlite::{params, Connection};

pub fn main() {
    train_test_split();
}

#[allow(dead_code)]
pub fn train_test_split() {
    let path = args().nth(1).expect("No argument");
    let file = File::open(path).expect("Failed to open file");
    let mut reader = BufReader::new(file);

    let mut samples = Vec::with_capacity(200_000);
    samples.push(Vec::with_capacity(200));

    let mut buf = [0u8; 2];
    while let Ok(_) = reader.read_exact(&mut buf) {
        let token = Token::new(u16::from_be_bytes(buf));
        if token == Token::new(0xff) {
            samples.push(Vec::with_capacity(200));
        }
        samples.last_mut().expect("Empty sample list").push(token);
    }

    fastrand::shuffle(&mut samples);

    println!("{:?}", &samples[..20]);
}

#[allow(dead_code)]
pub fn find_token_examples() {
    const EXAMPLE_COUNT: usize = 100;
    const TOKENS_CONTEXT: usize = 100;
    const MAX_TRIES: usize = 5;

    let paths = std::env::args()
        .skip(1)
        .map(PathBuf::from)
        .collect::<Vec<_>>();

    let bpe_state = BpeState::synced_with_file("/vocab/fineweb2.vocab");

    let tokens = bpe_state.tokens();

    // Open SQLite database connection
    let conn = Connection::open("/output/token_examples.db").expect("Failed to open database");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS token_examples_fineweb (
            token_id TEXT PRIMARY KEY,
            examples TEXT
        )",
        [],
    )
    .expect("Failed to create table");

    let token_examples = tokens
        .into_par_iter()
        .progress()
        .map(|token| {
            let mut examples = BTreeSet::new();
            while examples.len() < EXAMPLE_COUNT {
                let path = &paths[fastrand::usize(..paths.len())];
                let file = File::open(path).expect("File should exist");
                let size_bytes = file.metadata().expect("File should have metadata").len();
                let mut reader = BufReader::new(file);

                let seek_bytes = fastrand::u64(TOKENS_CONTEXT as u64 * 10..size_bytes / 2) & !1;
                reader
                    .seek(SeekFrom::Start(seek_bytes))
                    .expect("Failed to seek");

                let mut buffer = [0u8; 2];
                let mut found_token = false;
                while let Ok(_) = reader.read_exact(&mut buffer) {
                    let present_token = Token::new(u16::from_be_bytes(buffer));
                    if present_token == token {
                        found_token = true;
                        break;
                    }
                }
                if !found_token {
                    break;
                }

                let mut bytes_after = [0u8; TOKENS_CONTEXT * 2];
                let Ok(_) = reader
                    .read_exact(&mut bytes_after)
                    else { continue };
                let mut bytes_before = [0u8; TOKENS_CONTEXT * 2];
                reader
                    .seek_relative(-(TOKENS_CONTEXT as i64) * 4 - 2)
                    .expect("Failed to seek");
                reader
                    .read_exact(&mut bytes_before)
                    .expect("Failed to read left context");

                let bytes_to_tokens = |bytes: [u8; TOKENS_CONTEXT * 2]| {
                    bytes
                        .chunks_exact(2)
                        .map(|chunk| Token::new(u16::from_be_bytes([chunk[0], chunk[1]])))
                        .collect::<Vec<_>>()
                };

                let [ctx_before, ctx_after] = [bytes_before, bytes_after]
                    .map(bytes_to_tokens)
                    .map(|tokens| {
                        tokens
                            .iter()
                            .flat_map(|&token| bpe_state.at_token(token))
                            .copied()
                            .collect::<Vec<_>>()
                    })
                    .map(|bytes| String::from_utf8_lossy(&bytes).into_owned());

                let patterns = &[("\n", false), (". ", true), ("#", false), ("�", false)];
                let split_many = |before: bool| {
                    move |mut string: String| {
                        for &(pattern, keep) in patterns {
                            if before {
                                string = string
                                    .rsplit_once(pattern)
                                    .map(|(_, right)| right.to_owned())
                                    .unwrap_or(string);
                            } else {
                                string = string
                                    .split_once(pattern)
                                    .map(|(left, _)| {
                                        left.to_owned() + if keep { pattern } else { "" }
                                    })
                                    .unwrap_or(string);
                            }
                        }
                        string.to_owned()
                    }
                };
                let split_before = split_many(true);
                let split_after = split_many(false);

                let str_before = split_before(ctx_before);
                let str_after = split_after(ctx_after);

                if (str_before.len() < 5 || str_after.len() < 5) && fastrand::f32() < 0.9 {
                    continue;
                }

                examples.insert((str_before, str_after));
            }

            (token.index().to_string(), examples)
        })
        .collect::<Vec<_>>();

    // Insert into SQLite
    let mut stmt = conn
        .prepare("INSERT OR REPLACE INTO token_examples_fineweb (token_id, examples) VALUES (?, ?)")
        .expect("Failed to prepare insert statement");

    for (token_id, examples) in token_examples {
        let examples_json = serde_json::to_string(&examples).expect("Failed to serialize examples");
        stmt.execute(params![token_id, examples_json])
            .expect("Failed to insert token examples");
    }
}

#[allow(dead_code)]
fn count_tokens() {
    let bpe_state = BpeState::synced_with_file("/vocab/fineweb2.vocab");

    let paths = args().skip(1).map(PathBuf::from).collect_vec();

    let [mut direct_histogram_file, mut transitive_histogram_file] = [
        "/output/direct_histogram2.txt",
        "/output/transitive_histogram2.txt",
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
fn tokenize_wikipedia() {
    let bpe_state = BpeState::synced_with_file("/vocab/fineweb2.vocab");
    let mut input_paths = Path::new("/data/tokenizer-shards/")
        .read_dir()
        .expect("directory should exist")
        .filter(|path| path.as_ref().is_ok_and(|path| {
            path.path().to_string_lossy().contains("wikipedia")
        }))
        .collect_vec();
    let output_path = "/data/wikipedia-tokenized/shard.bin";
    let output_file = OpenOptions::new()
        .write(true)
        .create(true)
        .append(false)
        .truncate(true)
        .open(output_path)
        .expect("Failed to open output file");
    let mut output_writer = BufWriter::new(output_file);

    fastrand::shuffle(&mut input_paths);

    let tokens = input_paths
        .into_par_iter()
        .progress_with_style({
        ProgressStyle::default_bar()
            .template("Tokenizing der Wikipedia: [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
            .expect("Template-Fehler")
        })
        .flat_map(|path| {
            let mut buffer = Vec::with_capacity(1_000_000);
            let path = path.expect("failed to read path").path();
            let mut file = File::open(path).expect("failed to open file");
            file.read_to_end(&mut buffer).expect("failed to read file");
            let mut tokens = bpe_state.tokenizer().tokenize_bytes(&buffer);
            tokens.push(Token::new(0xff));
            tokens
        })
        .collect::<Vec<_>>();

    for token in tokens {
        output_writer
            .write_all(&token.into_inner().to_be_bytes())
            .expect("Could not write to file");
    }
}

#[allow(dead_code)]
fn tokenize_plenarprotokolle() {
    let bpe_state = BpeState::synced_with_file("/vocab/fineweb2.vocab");
    let mut input_paths = Path::new("/data/plenarprotokolle-raw/")
        .read_dir()
        .expect("directory should exist")
        .collect_vec();
    let output_path = "/data/plenarprotokolle-tokenized/shard.bin";
    let output_file = OpenOptions::new()
        .write(true)
        .create(true)
        .append(false)
        .truncate(true)
        .open(output_path)
        .expect("Failed to open output file");
    let mut output_writer = BufWriter::new(output_file);

    fastrand::shuffle(&mut input_paths);

    let tokens = input_paths
        .into_par_iter()
        .progress_with_style({
    ProgressStyle::default_bar()
        .template("Tokenizing der Plenarprotokolle: [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
        .expect("Template-Fehler")
    })
        .flat_map(|path| {
            let path = path.expect("failed to read path").path();
            let Some(text) = xml::extract_text(&path) else { return vec![] };
            let mut tokens = bpe_state.tokenizer().tokenize_bytes(&text.as_bytes());
            tokens.push(Token::new(0xff));
            tokens
        })
        .collect::<Vec<_>>();

    for token in tokens {
        output_writer
            .write_all(&token.into_inner().to_be_bytes())
            .expect("Could not write to file");
    }
}

#[allow(dead_code)]
fn tokenize_gesetze() {
    let bpe_state = BpeState::synced_with_file("/vocab/fineweb2.vocab");
    let mut input_paths = Path::new("/data/gesetze-raw/")
        .read_dir()
        .expect("directory should exist")
        .collect_vec();
    let output_path = "/data/gesetze-tokenized/shard.bin";
    let output_file = OpenOptions::new()
        .write(true)
        .create(true)
        .append(false)
        .truncate(true)
        .open(output_path)
        .expect("Failed to open output file");
    let mut output_writer = BufWriter::new(output_file);

    fastrand::shuffle(&mut input_paths);

    let tokens = input_paths
        .into_par_iter()
        .progress_with_style({
        ProgressStyle::default_bar()
            .template("Tokenizing der Gesetze: [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
            .expect("Template-Fehler")
        })
        .flat_map(|path| {
            let mut buffer = Vec::with_capacity(1_000_000);
            let path = path.expect("failed to read path").path();
            let mut file = File::open(path).expect("failed to open file");
            file.read_to_end(&mut buffer).expect("failed to read file");
            let mut tokens = bpe_state.tokenizer().tokenize_bytes(&buffer);
            tokens.push(Token::new(0xff));
            tokens
        })
        .collect::<Vec<_>>();

    for token in tokens {
        output_writer
            .write_all(&token.into_inner().to_be_bytes())
            .expect("Could not write to file");
    }
}

#[allow(dead_code)]
fn tokenize_gutenberg() {
    let bpe_state = BpeState::synced_with_file("/vocab/fineweb2.vocab");
    let mut input_paths = Path::new("/data/gutenberg-extracted/")
        .read_dir()
        .expect("directory should exist")
        .collect_vec();
    let output_path = "/data/gutenberg-tokenized/shard.bin";
    let output_file = OpenOptions::new()
        .write(true)
        .create(true)
        .append(false)
        .truncate(true)
        .open(output_path)
        .expect("Failed to open output file");
    let mut output_writer = BufWriter::new(output_file);

    fastrand::shuffle(&mut input_paths);

    let tokens = input_paths
        .into_par_iter()
        .progress_with_style({
        ProgressStyle::default_bar()
            .template("Tokenizing des Gutenberg-Korpus: [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
            .expect("Template-Fehler")
        })
        .flat_map(|path| {
            let mut buffer = Vec::with_capacity(1_000_000);
            let path = path.expect("failed to read path").path();
            let mut file = File::open(path).expect("failed to open file");
            file.read_to_end(&mut buffer).expect("failed to read file");
            let mut tokens = bpe_state.tokenizer().tokenize_bytes(&buffer);
            tokens.push(Token::new(0xff));
            tokens
        })
        .collect::<Vec<_>>();

    for token in tokens {
        output_writer
            .write_all(&token.into_inner().to_be_bytes())
            .expect("Could not write to file");
    }
}

#[allow(dead_code)]
fn tokenize_corpora() {
    let bpe_state = BpeState::synced_with_file("/vocab/fineweb2.vocab");

    let paths = chain!(
        (200..1000).rev().map(|i| format!("train/fw2-shard-{i:05}.bin")),
    )
    .map(PathBuf::from)
    .collect_vec();

    paths.into_par_iter().for_each(|path| {
        let input_path = format!("/data/fw2-raw/{}", path.display());
        let output_path = format!("/data/fw2-tokenized/{}", path.display());
        let file = fs::read(&input_path).expect("Failed to read file");

        // Open the output file once for this input file.
        let output_file = OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(true)
            .open(&output_path)
            .expect("Failed to open output file");
        let mut output_writer = BufWriter::new(output_file);

        // Split the file into chunks.
        let chunks: Vec<_> = file.split(|&byte| byte == 0xff).collect();
        let chunks_len = chunks.len();
        for (i, chunk) in chunks.into_iter().progress_with_style({
            ProgressStyle::default_bar()
                .template("chunks: [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
                .expect("Template-Fehler")
            })
            .enumerate() {
            let tokens = bpe_state.tokenizer().tokenize_bytes(chunk);

            for token in tokens {
                output_writer
                    .write_all(&token.into_inner().to_be_bytes())
                    .expect("Could not write token to file");
            }
            // Write the separator between chunks, except after the last one.
            if i < chunks_len - 1 {
                output_writer
                    .write(&u16::to_be_bytes(0xff))
                    .expect("Could not write separator to file");
            }
        }
        output_writer.flush().expect("Could not flush to file");
    });
}

#[allow(dead_code)]
fn reduce_vocab_size() {
    let mut bpe_state = BpeState::synced_with_file("./output/fineweb2.vocab");

    dbg!(bpe_state.additional_vocab_size());

    let space_regex = regex::Regex::new(r"\s").expect("Could not build regex");

    let blacklist: &[&[u8]] = &[b"\n", b"casino", b"Casino", b"||"];

    let word_count = |token: Token| {
        space_regex
            .split(&token.to_string_raw(&bpe_state).to_string())
            .filter(|m| m.len() != 0)
            .count()
    };

    let twentyone_bytes = |token| bpe_state.at_token(token).len() >= 21;
    let three_words = |token| word_count(token) >= 3;
    let in_blacklist = |token| {
        blacklist.iter().any(|&term| {
            bpe_state
                .at_token(token)
                .windows(term.len())
                .any(|window| window == term)
        })
    };
    // let two_words_at_end = |token: Token| token.index() >= 40530 && word_count(token) >= 2;

    let tokens_removed = bpe_state
        .tokens()
        .iter()
        .copied()
        .filter(|&token| {
            (token.into_inner() > 256)
                && (twentyone_bytes(token) || three_words(token) || in_blacklist(token))
            // || two_words_at_end(token)
        })
        .sorted_by_key(|token| usize::MAX - token.index());

    dbg!(tokens_removed.len());

    for token in tokens_removed {
        bpe_state.remove_token_unsynced(token);
    }
    dbg!(bpe_state.additional_vocab_size());
    while bpe_state.additional_vocab_size() > 50_000 {
        bpe_state.remove_token_unsynced(*bpe_state.tokens().last().unwrap());
    }
    dbg!("syncing");
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

    let paths = chain!((100..150).map(|i| format!("/data/fw2-raw/train/fw2-shard-{i:05}.bin")),)
        .map(PathBuf::from)
        .collect_vec();

    println!("Loading dataset from {} shards.", paths.len());
    let mut dataset =
        InMemoryDataset::load_from_shards(&paths.iter().collect_vec(), &bpe_state.tokenizer());

    let pattern_punctuation = r#"([.,!?:;"/])"#;
    let letter = r"(([A-Za-z])|(\xc3(\xa4|\xb6|\xbc|\x84|\x96|\x9c|\x9f)))";
    let config = TrainConfig {
        eta: EtaScheduler::piecewise_linear_two(0.3, [0.8, 0.8, 0.9]),
        max_token_length: None,
        target_vocab_size: 55_000,
        forbidden_patterns: RegexSet::new([
            &format!(r"(?-u)\xff"),
            &format!(r"(?-u){pattern_punctuation}\s*{letter}"),
            &format!(r"(?-u){letter}\s*{pattern_punctuation}"),
            &format!(r"(?-u)^\s."),
            &format!(r"(?-u){letter}\s+{letter}$"),
            &format!(r"(?-u)^{letter}{{1,2}}\s+{letter}+"),
            &format!(r"(?-u){letter}+\s+{letter}{{1,2}}$"),
        ])
        .expect("Invalid pattern encountered"),
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

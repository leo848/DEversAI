use quick_xml::events::Event;
use quick_xml::Reader;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;

pub fn extract_text(file_path: &impl AsRef<Path>) -> Option<String> {
    let file = File::open(file_path).ok()?;
    let reader = BufReader::new(file);
    let mut xml_reader = Reader::from_reader(reader);

    let mut buf = Vec::new();
    let mut inside_text = false;
    let mut text_content = String::new();

    while let Ok(event) = xml_reader.read_event_into(&mut buf) {
        match event {
            Event::Start(ref e) if e.name().as_ref() == b"TEXT" => {
                inside_text = true;
            }
            Event::Text(e) if inside_text => {
                text_content.push_str(&e.unescape().unwrap_or_default());
                text_content.push('\n'); // Preserve formatting
            }
            Event::End(ref e) if e.name().as_ref() == b"TEXT" => {
                inside_text = false;
            }
            Event::Eof => break,
            _ => {}
        }
        buf.clear();
    }

    if text_content.is_empty() {
        None
    } else {
        Some(text_content)
    }
}

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use regex::Regex;

#[pyfunction]
fn create_documents(texts: Vec<String>, chunk_size: usize) -> PyResult<Vec<String>> {
    let mut chunks = Vec::new();
    for text in texts {
        chunks.extend(divide_text_into_chunks(&text, chunk_size));
    }
    Ok(chunks)
}

fn divide_text_into_chunks(text: &str, chunk_size: usize) -> Vec<String> {
    let mut chunks = Vec::new();
    let re = Regex::new(r"[.!?]$").unwrap();
    let words: Vec<&str> = text.split_whitespace().collect();
    let mut current_chunk = Vec::new();
    let mut current_word_count = 0;

    for word in words.iter() {
        current_chunk.push(*word);
        current_word_count += 1;

        if current_word_count >= chunk_size {
            if re.is_match(word) {
                chunks.push(current_chunk.join(" "));
                current_chunk.clear();
                current_word_count = 0;
            } else {
                // Extend to next punctuation
                let remainder = &words[words.len() - current_chunk.len()..];
                if let Some((i, _)) = remainder.iter().enumerate().find(|&(_, &w)| re.is_match(w)) {
                    current_chunk.extend(&remainder[..=i]);
                    chunks.push(current_chunk.join(" "));
                    current_chunk.clear();
                    current_word_count = 0;
                }
            }
        }
    }

    if !current_chunk.is_empty() {
        chunks.push(current_chunk.join(" "));
    }

    chunks
}

#[pymodule]
fn indexify_text_splitter(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(create_documents, m)?)?;
    Ok(())
}

use pyo3::prelude::*;
use regex::Regex;

#[pyclass]
struct Document {
    #[pyo3(get, set)]
    page_content: String,
}

#[pymethods]
impl Document {
    #[new]
    fn new(page_content: String) -> Self {
        Document { page_content }
    }
}

#[pyclass]
struct FastRecursiveTextSplitter {
    chunk_size: usize,
}

#[pymethods]
impl FastRecursiveTextSplitter {
    #[new]
    fn new(chunk_size: usize) -> Self {
        FastRecursiveTextSplitter { chunk_size }
    }

    fn create_documents(&self, texts: Vec<String>) -> PyResult<Vec<Document>> {
        let mut documents = Vec::new();
        for text in texts {
            let chunks = self.divide_text_into_chunks(&text);
            for chunk in chunks {
                documents.push(Document::new(chunk));
            }
        }
        Ok(documents)
    }

    fn divide_text_into_chunks(&self, text: &str) -> Vec<String> {
        let mut chunks = Vec::new();
        let re = Regex::new(r"[.!?]$").unwrap();
        let words: Vec<&str> = text.split_whitespace().collect();
        let mut current_chunk = Vec::new();
        let mut current_word_count = 0;

        for word in words.iter() {
            current_chunk.push(*word);
            current_word_count += 1;

            if current_word_count >= self.chunk_size {
                if re.is_match(word) {
                    chunks.push(current_chunk.join(" "));
                    current_chunk.clear();
                    current_word_count = 0;
                } else {
                    // Extend to next punctuation
                    let remainder = &words[words.len() - current_chunk.len()..];
                    if let Some((i, _)) =
                        remainder.iter().enumerate().find(|&(_, &w)| re.is_match(w))
                    {
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
}

#[pymodule]
fn indexify_text_splitter(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<FastRecursiveTextSplitter>()?;
    Ok(())
}

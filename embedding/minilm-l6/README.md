# MiniLM-6 Embedding Extractor

This extractor extractors an embedding for a piece of text.
It uses the huggingface [MiniLM-6 model](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), which is a tiny but very robust emebdding model for text.

Content[String] -> Content[Empty] + Features[JSON metadata of embedding].

Example input:

```text
The quick brown fox jumps over the lazy dog.
```

Example output:

```json
{
    "embedding": [
            510.3,
            240.2,
            ...
    ]
}
```

## Usage

Try out the extractor. Write your favorite (foreign) quote.

```bash
cd minilm-l6
indexify extractor extract --text "The quick brown fox jumps over the lazy dog."
```

## Container

* The container is not published yet. *

```bash
docker run  -it diptanu/minilm-l6-extractor extractor extract --text "The quick brown fox jumps over the lazy dog."
```

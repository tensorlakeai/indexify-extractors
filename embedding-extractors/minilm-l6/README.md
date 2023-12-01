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
[
  {
    "content_type": "text/plain",
    "source": [
      84,
      104,
      ...
      46
    ],
    "feature": {
      "feature_type": "Embedding",
      "name": "embedding",
      "data": [
        0.04393356665968895,
        0.05893441289663315,
        ...
        0.10206394642591476
      ]
    }
  }
]
```

## Usage

Try out the extractor. Write your favorite (foreign) quote.

```bash
cd text-lid
indexify extractor extract --text "The quick brown fox jumps over the lazy dog."
```

## Container

* The container is not published yet. *

```bash
docker run --mount type=bind,source="$HOME/.cache/huggingface/hub",target=/root/.cache/huggingface/hub diptanu/minilm-l6-extractor extractor extract --text "The quick brown fox jumps over the lazy dog."
```

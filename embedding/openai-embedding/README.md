# OpenAI Embedding Extractor

This extractor extracts an embedding for a piece of text.
It uses the OpenAI text-embedding-ada-002 model.

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
      101,
      ...
    ],
    "feature": {
      "feature_type": "Embedding",
      "name": "embedding",
      "data": 0.0016260817646980286
    }
  }
]
```

## Usage

Try out the extractor. Write your favorite (foreign) quote.

```bash
cd openai-embedding
indexify extractor extract --text "The quick brown fox jumps over the lazy dog."
```

## Container

* The container is not published yet. *

```bash
docker run  -it lucas/openai-embedding-ada-002-extractor extractor extract --text "The quick brown fox jumps over the lazy dog."
```

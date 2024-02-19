# Jina Embedding Extractor (English)

This extractor extractors an embedding for a piece of text.
It uses the huggingface [Jina model](https://huggingface.co/jinaai/jina-embeddings-v2-base-en) which is an English, monolingual embedding model supporting 8192 sequence length. It is based on a Bert architecture (JinaBert) that supports the symmetric bidirectional variant of ALiBi to allow longer sequence length.

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
cd jina_base_en
indexify extractor extract --text "The quick brown fox jumps over the lazy dog."
```

## Container

* The container is not published yet. *

```bash
docker run  -it indexify-extractors/jina_base_en extractor extract --text "The quick brown fox jumps over the lazy dog."
```

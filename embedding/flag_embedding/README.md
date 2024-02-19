# Flag Embedding extractor (BGE)

This extracctor uses FlagEmbedding that can map any text to a low-dimensional dense vector which can be used for tasks like retrieval, classification, clustering, or semantic search. It uses [BGE base model](https://huggingface.co/BAAI/bge-base-en) from [HuggingFace](https://huggingface.co/).

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
cd flag_embedding
indexify extractor extract --text "The quick brown fox jumps over the lazy dog."
```

## Container

* The container is not published yet. *

```bash
docker run  -it indexify-extractors/flag_embedding extractor extract --text "The quick brown fox jumps over the lazy dog."
```

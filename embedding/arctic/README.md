# Arctic Embedding Extractor

This extractor extractors an embedding for a piece of text.
It uses the huggingface [Snowflake's Arctic-embed-m](https://huggingface.co/Snowflake/snowflake-arctic-embed-m). The snowflake-arctic-embedding models achieve state-of-the-art performance on the MTEB/BEIR leaderboard for each of their size variants.

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
cd arctic
indexify-extractor extract --text "The quick brown fox jumps over the lazy dog."
```

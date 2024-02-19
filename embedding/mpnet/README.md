# MPNET Multilingual Base V2

This is a sentence embedding extractor based on the [MPNET Multilingual Base V2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2).
This is a sentence-transformers model: It maps sentences & paragraphs to a 768 dimensional dense vector space and can be used for tasks like clustering or semantic search.
It's best use case is paraphrasing, but it can also be used for other tasks.

Example input:

```text
Hello World!
```

Example output:

```json
"feature": {
        "feature_type": "Embedding",
        "name": "embedding",
        "data": [
          -0.07014346122741699,
          -0.3152652084827423,
          0.7451112270355225,
          -0.20808571577072144,
          -0.06616905331611633,
          0.2570410370826721,
          1.041167378425598,
          0.41626620292663574,
          ...
        ]
        }
```

## Usage

Try out the extractor. Write your favorite (foreign) quote.

```bash
cd mpnet
indexify extractor extract --text "The quick brown fox jumps over the lazy dog."
```

## Container

* The container is not published yet. *

```bash
docker run  -it indexify-extractors/mpnet extractor extract --text "The quick brown fox jumps over the lazy dog."
```

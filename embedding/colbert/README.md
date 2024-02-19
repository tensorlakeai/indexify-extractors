# Colbert v2 Embedding Extractor

This extractor extracts an embedding for a piece of text.
It uses the huggingface [Colbert v2 model](https://huggingface.co/colbert-ir/colbertv2.0) It encodes each passage into a matrix of token-level embeddings (shown above in blue). Then at search time, it embeds every query into another matrix (shown in green) and efficiently finds passages that contextually match the query using scalable vector-similarity (MaxSim) operators.

Example input:

```text
Hello lovely people!
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
cd colbert
indexify extractor extract --text "The quick brown fox jumps over the lazy dog."
```

## Container

* The container is not published yet. *

```bash
docker run  -it indexify-extractors/colbert extractor extract --text "The quick brown fox jumps over the lazy dog."
```

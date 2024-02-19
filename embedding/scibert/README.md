# SciBERT Uncased

This is the pretrained model presented in [SciBERT: A Pretrained Language Model for Scientific Text](https://www.aclweb.org/anthology/D19-1371/), which is a BERT model trained on scientific text.
Works best with scientific text embedding extraction.

Example input:

```text
Scientific discovery is fascinating
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

Try out the extractor. Write your favorite (scientific) quote.

```bash
cd scibert
indexify extractor extract --text "Scientific discovery is fascinating"
```

## Container

* The container is not published yet. *

```bash
docker run  -it indexify-extractors/scibert extractor extract --text "Scientific discovery is fascinating"
```
Citation:

```bibtex
@inproceedings{beltagy-etal-2019-scibert,
    title = "SciBERT: A Pretrained Language Model for Scientific Text",
    author = "Beltagy, Iz  and Lo, Kyle  and Cohan, Arman",
    booktitle = "EMNLP",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/D19-1371"
}
```
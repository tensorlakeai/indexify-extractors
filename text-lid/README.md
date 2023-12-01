# Language Identification Extractor

This extractor identifies what language a certain piece of text is.
It uses the [py-lingua](https://github.com/pemistahl/lingua-py) package to determine this.

Content[String] -> Content[Empty] + Features[JSON metadata of language].

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
      "feature_type": "Metadata",
      "name": "language",
      "data": {
        "language": "ENGLISH",
        "score": "0.1780954573167577"
      }
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
docker run --mount type=bind,source="$HOME/.cache/huggingface/hub",target=/root/.cache/huggingface/hub yenicelik/language-extractor extractor extract --text "The quick brown fox jumps over the lazy dog."
```

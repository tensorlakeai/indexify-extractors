# Hash-Embedding Extractor

This extractor extractors an "identity-"embedding for a piece of text, or file.
It uses the sha256 to calculate the unique embeding for a given text, or file.
This can be used to quickly search for duplicates within a large set of data.

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
cd invoice-extractor
indexify extractor extract --text "The quick brown fox jumps over the lazy dog."
```

## Container

* The container is not published yet. *

```bash
docker run  -it yenicelik/identity-hash-extractor extractor extract --text "The quick brown fox jumps over the lazy dog."
```

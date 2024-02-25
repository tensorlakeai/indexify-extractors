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
{
    {
        "language": {
            "language": "ENGLISH", "score": 0.9
        }
    }
}
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
docker run  -it yenicelik/language-extractor --text "The quick brown fox jumps over the lazy dog."
```

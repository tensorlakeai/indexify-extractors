# E5 Small V2 Embedding Extractor

A good small and fast general model for similarity search or downstream enrichments.
Based on [E5_Small_V2](https://huggingface.co/intfloat/e5-small-v2) which only works for English texts. Long texts will be truncated to at most 512 tokens.

Example input:

```text
'query: how much protein should a female eat',
"passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or training for a marathon. Check out the chart below to see how much protein you should be eating each day."
```

Example output:

```json
{
    "embedding": [
        -0.06445365399122238,
        -0.0156948771327734,
        0.047192659229040146,
        ...
    ]
}
```

## Usage

Here are some rules of thumb:

- Use "query: " and "passage: " correspondingly for asymmetric tasks such as passage retrieval in open QA, ad-hoc information retrieval.

- Use "query: " prefix for symmetric tasks such as semantic similarity, paraphrase retrieval.

- Use "query: " prefix if you want to use embeddings as features, such as linear probing classification, clustering.

```bash
cd e5_embedding
indexify extractor extract --text "query: how much protein should a female eat'"
```

## Container

* The container is not published yet. *

```bash
docker run  -it indexify-extractors/e5_embedding extractor extract --text "query: how much protein should a female eat'"
```

# Embedding Extractors

To begin utilizing these extractors install the indexify-extractor CLI.

```bash
pip install indexify-extractor-sdk
```

## Download and Run
```bash
indexify-extractor download <download-link>
indexify-extractor join-server
```

| Name     | Download link                    | Extractor Module Name                             |
|----------|----------------------------------|---------------------------------------------------|
| clip     | hub://embedding/clip_embedding   | openai_clip_extractor:ClipEmbeddingExtractor      |
| Colbert  | hub://embedding/colbert          | colbertv2:ColBERTv2Base                           |
| e5       | hub://embedding/e5_embedding     | e5_small_v2:E5SmallEmbeddings                     |
| flag     | hub://embedding/flag_embedding   | bge_base:BGEBase                                  |
| hash     | hub://embedding/hash-embedding   | identity_hash_embedding:IdentityHashEmbedding     |
| jina     | hub://embedding/jina_base_en     | jina_base_en:JinaEmbeddingsBase                   |
| MiniLML6 | hub://embedding/minilm-l6        | minilm_l6:MiniLML6Extractor                       |
| mpnet    | hub://embedding/mpnet            | mpnet_base_v2:MPNetV2                             |
| openai   | hub://embedding/openai-embedding | openai_embedding:OpenAIEmbeddingExtractor         |
| scibert  | hub://embedding/scibert          | scibert_uncased:SciBERTExtractor                  |
| arctic   | hub://embedding/arctic           | arctic:ArcticExtractor                            |

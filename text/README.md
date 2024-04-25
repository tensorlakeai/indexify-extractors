# Text Extractors

To begin utilizing these extractors install the indexify-extractor CLI.

```bash
pip install indexify-extractor-sdk
```

## Download and Run
```bash
indexify-extractor download <download-link>
indexify-extractor join-server <extractor-module-name>
```

| Name                 | Download link                  | Extractor Module Name                    |
|----------------------|--------------------------------|------------------------------------------|
| summarization        | hub://text/summarization       | summary_extractor:SummaryExtractor       |
| llm-summary          | hub://text/llm-summary         | summary_extractor:SummaryExtractor       |
| chunking             | hub://text/chunking            | chunk_extractor:ChunkExtractor           |
| llm                  | hub://text/llm                 | llm_extractor:LLMExtractor           |
| schema               | hub://text/schema              | schema_extractor:SchemaExtractor           |

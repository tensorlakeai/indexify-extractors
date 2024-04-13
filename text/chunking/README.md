# Chunking Extractors 

`ChunkExtractor` splits text into smaller chunks. The input to this extractor can be from any source which produces text, with a mime type `text/plain`. The chunk extractor can be configured to use one of the many chunking strategies available. We use Langchain under the hood in this extractor.

### Configuration Options 
* `overlap(default:0)`: Number of tokens which overlap 
* `chunk_size(default:0)`: Number of tokens in the chunk
* `text_splitter(default:recursive)`: Text splitter algorithms borrowed from Langchain. Available options: `char`, `recursive`, `markdown`, `html`
* `headers_to_split_on`: Headers to split the text if you are using markdown or HTML


### Create Extraction Policy

```python
from indexify import Indexify
client = Indexify()
client.add_extraction_policy(extractor='tensorlake/chunk-extractor', name="my-text-chunks", content_source='...', params={"overlap": 100, "chunk_size": 1400})
```


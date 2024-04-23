# Indexify Extractors

## Overview

Extractors are modules that give Indexify data processing capabilities such as metadata or embedding extraction from document, videos and audio. This repository hosts a collection of extractors for Indexify.

For the main Indexify project, visit: [Indexify Main Repository](https://github.com/diptanu/indexify).

## Available Extractors
We have built some extractors based on demand from our users. You can write a new or a custom extractor for your use-case too, instructions for writing new extractors are below.

* [Embedding Extractors](https://github.com/tensorlakeai/indexify-extractors/tree/main/embedding)
* [Video Extractors](https://github.com/tensorlakeai/indexify-extractors/tree/main/video)
* [Invoice Extractors](https://github.com/tensorlakeai/indexify-extractors/tree/main/invoices)
* [Audio Extractors](https://github.com/tensorlakeai/indexify-extractors/tree/main/whisper-asr)
* [PDF Extractors](https://github.com/tensorlakeai/indexify-extractors/tree/main/pdf)

## Usage
#### Install
```bash
pip install indexify-extractor-sdk
```

#### List Available extractors 
```bash
indexify-extractor list
```

#### Download an Extractor
Find the name of the extractor you want.
```bash
indexify-extractor download hub://embedding/minilm-l6
```

#### Use them independently 
```python
from indexify_extractor_sdk import load_extractor, Content
extractor, config_cls = load_extractor("minilm-l6.minilm_l6:MiniLML6Extractor")
content = Content.from_text("hello world")
out = extractor.extract(content)
```

Extractors can be parameterized when they are called. The input parameters are Pydantic Models. Inspect the config class programatically or in the docs of the corresponding extractor -
```python
ex, config = load_extractor("chunking.chunk_extractor:ChunkExtractor")
config.schema()
#{'properties': {'overlap': {'default': 0, 'title': 'Overlap', 'type': 'integer'}, 'chunk_size': {'default': 100, 'title': 'Chunk Size', 'type': 'integer'}, 'text_splitter': {'default': 'recursive', 'enum': ['char', 'recursive', 'markdown', 'html'], 'title': 'Text Splitter', 'type': 'string'}, 'headers_to_split_on': {'default': [], 'items': {'type': 'string'}, 'title': 'Headers To Split On', 'type': 'array'}}, 'title': 'ChunkExtractionInputParams', 'type': 'object'}
```

#### Extract Locally on shell -
```bash
indexify-extractor local minilm_l6:MiniLML6Extractor --text "hello world"
```

#### Run with Indexify Server
To run the extractor with Indexify's control plane such that it can continuously extract from content -
```bash
indexify-extractor join-server minilm_l6:MiniLML6Extractor --coordinator-addr localhost:8950 --ingestion-addr localhost:8900
```
The `coordinator-addr` and `ingestion-addr` above are the default addresses exposed by the Indexify server to get extraction instructions and to upload extracted data, they can be configured in the server configuration.

## Build a new Extractor
If want to build a new extractor to give Indexify new data processing capabilities you can write a new extractor by cloning this repository - https://tensorlakeai/indexify-extractor-template

### Clone the template
```shell
git clone https://github.com/tensorlakeai/indexify-extractor-template.git
``` 

### Implement the extractor interface 
```python
class MyExtractor(Extractor):
    input_mime_types = ["text/plain", "application/pdf", "image/jpeg"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params: InputParams) -> List[Content]:
        return [
            Content.from_text(
                text="Hello World",
                features=[
                    Feature.embedding(values=[1, 2, 3]),
                    Feature.metadata(json.loads('{"a": 1, "b": "foo"}')),
                ],
                labels={"url": "test.com"},
            ),
            Content.from_text(
                text="Pipe Baz",
                features=[Feature.embedding(values=[1, 2, 3])],
                labels={"url": "test.com"},
            ),
        ]

    def sample_input(self) -> Content:
        return Content.from_text("hello world")

```

Once you have developed the extractor you can test the extractor locally by running the `indexify-extractor local` command as described above.

### Deploy the extractor
When you are ready to deploy the extractor in production, package the extractor and deploy as many instances you want on your cluster for parallelism, and point it to the indexify server. 
```
indexify-extractor join-server my_extractor.py:MyExtractor --coordinator-addr localhost:8950 --ingestion-addr localhost:8900
```

### Package the Extractor 
Once you build a new extractor, and have tested it and it's time to deploy this in production, you can build a container with the extractor -
```bash
indexify-extractor package my_extractor:MyExtractor
```

### Running Your packaged extractor
To run your packaged extractor image you can run the following command
```bash
docker run ExtractorImageName indexify-extractor join-server --coordinator-addr=host.docker.internal:8950 --ingestion-addr=host.docker.internal:8900
```

# Indexify Extractors

## Overview

Extractors are modules that give Indexify data processing capabilities such as metadata or embedding extraction from document, videos and audio. This repository hosts a collection of extractors for Indexify.
These extractors complement the core functionalities of Indexify, enabling seamless integration and enhanced data processing capabilities.

For the main Indexify project, visit: [Indexify Main Repository](https://github.com/diptanu/indexify).

## Available Extractors
We have built some extractors based on demand from our users. You can write a new or a custom extractor for your use-case too, instructions for writing new extractors are below.

* [Embedding Extractors](https://github.com/tensorlakeai/indexify-extractors/tree/main/embedding)
* [Invoice Extractor](https://github.com/tensorlakeai/indexify-extractors/tree/main/invoices)
* [Audio Extractor](https://github.com/tensorlakeai/indexify-extractors/tree/main/whisper-asr)

## Usage
Install the Indexify Extractor SDK 
```bash
pip install indexify-extractor-sdk
```

Pick any extractor you are interested in running. For example, if you want to run the MinLML6 Embedding Extractors -

```bash
indexify-extractor download hub://embedding/colbert
```

To run an extractor locally -
```
indexify-extractor local minilm_l6:MiniLML6Extractor --text "hello world"
```

To run the extractor with Indexify's control plane such that it can continuously extract from content -
```
indexify-extractor join minilm_l6:MiniLML6Extractor --coordinator-addr localhost:8950 --ingestion-addr localhost:8900
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

## Deploy the extractor
When you are ready to deploy the extractor in production, package the extractor and deploy as many instances you want on your cluster for parallelism, and point it to the indexify server. 
```
indexify-extractor join my_extractor.py:MyExtractor --coordinator-addr localhost:8950 --ingestion-addr:8900
```

## Running Your Packaged Extractor Image
To run your packaged extractor image you can run the following command
```
docker run ExtractorImageName indexify-extractor join --coordinator-addr=host.docker.internal:8950 --ingestion-addr=host.docker.internal:8900
```

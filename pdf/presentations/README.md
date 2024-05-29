## PPT Extractor

It can be used to analyze PowerPoint files from a corpus, perhaps to extract search indexing text and images. It runs on any Python capable platform, including macOS and Linux, and does not require the PowerPoint application to be installed or licensed.

## Example

### Input
```python
filepath = "test.pptx"
with open(filepath, 'rb') as f:
    ppt_data = f.read()
data = Content(content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", data=ppt_data)
extractor = PPTExtractor()
results = extractor.extract(data)
```

### Output
```
[Content(content_type='text/plain', data=b'Hello, World!', features=[], labels={}), Content(content_type='text/plain', data=b'Developed with \xf0\x9f\xab\xb6 by Indexify | a Tensorlake product', features=[], labels={})]
```
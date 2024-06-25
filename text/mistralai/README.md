# Mistral AI Extractor

This is an extractor that supports text input documents and returns output in text using Mistral AI. This extractor supports various Mistral AI models like mistral-large-latest and works on the Content of previous extractor as message, however we can manually overwrite prompt and message.

### Example:
##### input:
```
prompt = """Extract all named entities from the text."""
article = Content.from_text("My name is Rishiraj and I live in India.")
input_params = MistralExtractorConfig(system_prompt=prompt)
extractor = MistralExtractor()
results = extractor.extract(article, params=input_params)
print(results)
```

##### output:
```
[Content(content_type='text/plain', data=b'1. Rishiraj\n2. India', features=[], labels={})]
```
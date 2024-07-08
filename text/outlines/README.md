# Outlines Extractor

This is an extractor that supports text input documents and returns output in text using the Outlines library. This extractor supports various language models and generation types, working on the Content of previous extractors as input. You can customize the prompt, model, and generation parameters.

### Features:
- Supports multiple generation types: text, choice, format, regex, json, and cfg
- Compatible with various language models from Hugging Face
- Customizable prompts and generation parameters
- Flexible output formats based on the chosen generation type

### Example:
##### Input:
```python
from indexify_extractor_sdk import Content
from outlines_extractor import OutlinesExtractor, OutlinesExtractorConfig

article = Content.from_text("I love using Outlines for NLP tasks!")
input_params = OutlinesExtractorConfig(
    generation_type='choice',
    prompt="You are a sentiment analysis assistant. Classify the following text as either Positive or Negative.",
    choices=["Positive", "Negative"]
)
extractor = OutlinesExtractor()
results = extractor.extract(article, params=input_params)
print(results)
```

##### Output:
```
[Content(content_type='text/plain', data=b'Positive', features=[], labels={})]
```

### Configuration Options:
- `model_name`: The name of the Hugging Face model to use (default: 'mistralai/Mistral-7B-Instruct-v0.2')
- `generation_type`: The type of generation to perform (default: 'text')
- `prompt`: The system prompt or instruction for the model (default: 'You are a helpful assistant.')
- `max_tokens`: Maximum number of tokens to generate (default: 100)
- `regex_pattern`: Pattern for regex-based generation (optional)
- `choices`: List of choices for choice-based generation (optional)
- `output_type`: Output type for format-based generation (optional)
- `json_schema`: JSON schema for JSON-based generation (optional)
- `cfg_grammar`: Grammar for CFG-based generation (optional)
- `hf_token`: Hugging Face API token (optional, defaults to environment variable HF_TOKEN)

### Note:
Make sure to set up your Hugging Face API token either in the environment variable `HF_TOKEN` or pass it directly in the `OutlinesExtractorConfig`.
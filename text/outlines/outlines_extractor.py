from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
import os
import outlines
from outlines.models import transformers
from outlines.generate import text, choice, format, regex, json, cfg
from huggingface_hub import login
import sys

sys.set_int_max_str_digits(0)
token = os.getenv('HF_TOKEN')

class OutlinesExtractorConfig(BaseModel):
    model_name: str = Field(default='unsloth/mistral-7b-instruct-v0.3-bnb-4bit')
    generation_type: str = Field(default='text')
    prompt: str = Field(default='You are a helpful assistant.')
    max_tokens: int = Field(default=100)
    regex_pattern: Optional[str] = Field(default=None)
    choices: Optional[List[str]] = Field(default=None)
    output_type: Optional[str] = Field(default=None)
    json_schema: Optional[str] = Field(default=None)
    cfg_grammar: Optional[str] = Field(default=None)
    hf_token: Optional[str] = Field(default=token)

class OutlinesExtractor(Extractor):
    name = "tensorlake/outlines"
    description = "An extractor that lets you use LLMs with Outlines."
    system_dependencies = []
    input_mime_types = ["text/plain"]

    def __init__(self):
        super(OutlinesExtractor, self).__init__()

    def extract(self, content: Content, params: OutlinesExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        model_name = params.model_name
        generation_type = params.generation_type
        prompt = params.prompt
        max_tokens = params.max_tokens
        login(token=params.hf_token)

        text_input = content.data.decode("utf-8")
        full_prompt = f"{prompt} {text_input}"

        model = transformers(model_name)

        if generation_type == 'text':
            generator = text(model)
            response = generator(full_prompt, max_tokens=max_tokens)
        elif generation_type == 'choice' and params.choices:
            generator = choice(model, params.choices)
            response = generator(full_prompt)
        elif generation_type == 'format' and params.output_type:
            output_type = eval(params.output_type)  # Be cautious with eval
            generator = format(model, output_type)
            response = generator(full_prompt, max_tokens=max_tokens)
        elif generation_type == 'regex' and params.regex_pattern:
            generator = regex(model, params.regex_pattern)
            response = generator(full_prompt, max_tokens=max_tokens)
        elif generation_type == 'json' and params.json_schema:
            generator = json(model, params.json_schema)
            response = generator(full_prompt)
        elif generation_type == 'cfg' and params.cfg_grammar:
            generator = cfg(model, params.cfg_grammar)
            response = generator(full_prompt)
        else:
            response = "Invalid generation type or missing required parameters."

        contents.append(Content.from_text(str(response)))
        
        return contents

    def sample_input(self) -> Content:
        return Content.from_text("Hello world, I am using Outlines.")

if __name__ == "__main__":
    article = Content.from_text("Create a mysterious elven ranger character.")
    input_params = OutlinesExtractorConfig(
        generation_type='json',
        json_schema='''{ "title": "Character", "type": "object", "properties": { "name": { "title": "Name", "maxLength": 10, "type": "string" }, "age": { "title": "Age", "type": "integer" }, "armor": {"$ref": "#/definitions/Armor"}, "weapon": {"$ref": "#/definitions/Weapon"} }, "required": ["name", "age", "armor", "weapon", "strength"], "definitions": { "Armor": { "title": "Armor", "description": "An enumeration.", "enum": ["leather", "chainmail", "plate"], "type": "string" }, "Weapon": { "title": "Weapon", "description": "An enumeration.", "enum": ["sword", "axe", "mace", "spear", "bow", "crossbow"], "type": "string" } } }''',
        prompt="Generate a character description for a fantasy role-playing game."
    )
    extractor = OutlinesExtractor()
    results = extractor.extract(article, params=input_params)
    print(results)

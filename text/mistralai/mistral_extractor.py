from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import mimetypes

class MistralExtractorConfig(BaseModel):
    model_name: Optional[str] = Field(default='mistral-large-latest')
    key: Optional[str] = Field(default=None)
    system_prompt: str = Field(default='You are a helpful assistant.')
    user_prompt: Optional[str] = Field(default=None)

class MistralExtractor(Extractor):
    name = "tensorlake/mistral"
    description = "An extractor that let's you use LLMs from Mistral."
    system_dependencies = []
    input_mime_types = ["text/plain", "application/json"]

    def __init__(self):
        super(MistralExtractor, self).__init__()

    def extract(self, content: Content, params: MistralExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        model_name = params.model_name
        key = params.key
        prompt = params.system_prompt
        query = params.user_prompt

        text = content.data.decode("utf-8")
        if query is None:
            query = text

        if ('MISTRAL_API_KEY' not in os.environ) and (key is None):
            response_content = "The MISTRAL_API_KEY environment variable is not present."
        else:
            if ('MISTRAL_API_KEY' in os.environ) and (key is None):
                client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])
            else:
                client = MistralClient(api_key=key)
            
            messages_content = [ ChatMessage(role="system", content=prompt), ChatMessage(role="user", content=query) ]

            response = client.chat( model=model_name, messages=messages_content )
            response_content = response.choices[0].message.content
        
        contents.append(Content.from_text(response_content))
        
        return contents

    def sample_input(self) -> Content:
        return Content.from_text("Hello world, I am a good boy.")

if __name__ == "__main__":
    prompt = """Extract all named entities from the text."""
    article = Content.from_text("My name is Rishiraj and I live in India.")
    input_params = MistralExtractorConfig(prompt=prompt)
    extractor = MistralExtractor()
    results = extractor.extract(article, params=input_params)
    print(results)
from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
import os
import base64
from openai import OpenAI
from pdf2image import convert_from_path
import tempfile
import mimetypes

class OAIExtractorConfig(BaseModel):
    model_name: Optional[str] = Field(default='gpt-3.5-turbo')
    key: Optional[str] = Field(default=None)
    system_prompt: str = Field(default='You are a helpful assistant.')
    user_prompt: Optional[str] = Field(default=None)

class OAIExtractor(Extractor):
    name = "tensorlake/openai"
    description = "An extractor that let's you use LLMs from OpenAI."
    system_dependencies = []
    input_mime_types = ["text/plain", "application/pdf", "image/jpeg", "image/png"]

    def __init__(self):
        super(OAIExtractor, self).__init__()

    def extract(self, content: Content, params: OAIExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        model_name = params.model_name
        key = params.key
        prompt = params.system_prompt
        query = params.user_prompt

        if content.content_type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(content.data)
                file_path = temp_file.name
                images = convert_from_path(file_path)
                
                all_responses = []
                for i, image in enumerate(images):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image_file:
                        image.save(temp_image_file.name, 'JPEG')
                        response = self._process_image(temp_image_file.name, model_name, key, prompt, query)
                        all_responses.append(f"Page {i+1}:\n{response}")
                    os.unlink(temp_image_file.name)
                
                response_content = "\n\n".join(all_responses)
                os.unlink(file_path)
        
        elif content.content_type in ["image/jpeg", "image/png"]:
            suffix = mimetypes.guess_extension(content.content_type)
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_image_file:
                temp_image_file.write(content.data)
                response_content = self._process_image(temp_image_file.name, model_name, key, prompt, query)
            os.unlink(temp_image_file.name)
        
        else:
            text = content.data.decode("utf-8")
            if query is None:
                query = text
            response_content = self._process_text(model_name, key, prompt, query)
        
        contents.append(Content.from_text(response_content))
        return contents

    def _process_image(self, image_path, model_name, key, prompt, query):
        if ('OPENAI_API_KEY' not in os.environ) and (key is None):
            return "The OPENAI_API_KEY environment variable is not present."
        
        if ('OPENAI_API_KEY' in os.environ) and (key is None):
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        else:
            client = OpenAI(api_key=key)
        
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        messages_content = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt + " " + (query or "")},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ]
        
        response = client.chat.completions.create(model=model_name, messages=messages_content)
        return response.choices[0].message.content

    def _process_text(self, model_name, key, prompt, query):
        if ('OPENAI_API_KEY' not in os.environ) and (key is None):
            return "The OPENAI_API_KEY environment variable is not present."
        
        if ('OPENAI_API_KEY' in os.environ) and (key is None):
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        else:
            client = OpenAI(api_key=key)
        
        messages_content = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        response = client.chat.completions.create(model=model_name, messages=messages_content)
        return response.choices[0].message.content

    def sample_input(self) -> Content:
        return Content.from_text("Hello world, I am a good boy.")

if __name__ == "__main__":
    prompt = """Extract all text from the document."""
    f = open("resume.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    input_params = OAIExtractorConfig(prompt=prompt, model_name="gpt-4-vision-preview")
    extractor = OAIExtractor()
    results = extractor.extract(pdf_data, params=input_params)
    print(results)
    prompt = """Extract all named entities from the text."""
    article = Content.from_text("My name is Rishiraj and I live in India.")
    input_params = OAIExtractorConfig(prompt=prompt)
    extractor = OAIExtractor()
    results = extractor.extract(article, params=input_params)
    print(results)
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
    prompt: str = Field(default='You are a helpful assistant.')
    query: Optional[str] = Field(default=None)

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
        prompt = params.prompt
        query = params.query

        if content.content_type in ["application/pdf"]:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(content.data)
                file_path = temp_file.name
                images = convert_from_path(file_path)
                image_files = []
                for i in range(len(images)):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image_file:
                        images[i].save(temp_image_file.name, 'JPEG')
                        image_files.append(temp_image_file.name)
        elif content.content_type in ["image/jpeg", "image/png"]:
            image_files = []
            suffix = mimetypes.guess_extension(content.content_type)
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_image_file:
                temp_image_file.write(content.data)
                file_path = temp_image_file.name
                image_files.append(file_path)
        else:
            text = content.data.decode("utf-8")
            if query is None:
                query = text
            file_path = None
        
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        if ('OPENAI_API_KEY' not in os.environ) and (key is None):
            response_content = "The OPENAI_API_KEY environment variable is not present."
        else:
            if ('OPENAI_API_KEY' in os.environ) and (key is None):
                client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            else:
                client = OpenAI(api_key=key)
            if file_path:
                encoded_images = [encode_image(image_path) for image_path in image_files]
                messages_content = [ { "role": "user", "content": [ { "type": "text", "text": prompt, } ] + [ { "type": "image_url", "image_url": { "url": f"data:image/jpeg;base64,{encoded_image}", }, } for encoded_image in encoded_images ], } ]
            else:
                messages_content = [ {"role": "system", "content": prompt}, {"role": "user", "content": query} ]

            response = client.chat.completions.create( model=model_name, messages=messages_content )
            response_content = response.choices[0].message.content
        
        contents.append(Content.from_text(response_content))
        
        return contents

    def sample_input(self) -> Content:
        return Content.from_text("Hello world, I am a good boy.")

if __name__ == "__main__":
    prompt = """Extract all text from the document."""
    f = open("resume.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    input_params = OAIExtractorConfig(prompt=prompt, model_name="gpt-4o")
    extractor = OAIExtractor()
    results = extractor.extract(pdf_data, params=input_params)
    print(results)
    prompt = """Extract all named entities from the text."""
    article = Content.from_text("My name is Rishiraj and I live in India.")
    input_params = OAIExtractorConfig(prompt=prompt)
    extractor = OAIExtractor()
    results = extractor.extract(article, params=input_params)
    print(results)
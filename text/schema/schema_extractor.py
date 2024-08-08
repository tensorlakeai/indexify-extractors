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
    model: Optional[str] = Field(default='gpt-4o-2024-08-06')
    api_key: Optional[str] = Field(default=None)
    system_prompt: str = Field(default='Extract the information.')
    user_prompt: Optional[str] = Field(default=None)
    response_format: Optional[BaseModel] = None

class OAIExtractor(Extractor):
    name = "tensorlake/schema"
    description = "An extractor that let's you extract JSON from schemas."
    system_dependencies = []
    input_mime_types = ["text/plain", "application/json", "application/pdf", "image/jpeg", "image/png"]

    def __init__(self):
        super(OAIExtractor, self).__init__()

    def extract(self, content: Content, params: OAIExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        model_name = params.model
        key = params.api_key
        prompt = params.system_prompt
        query = params.user_prompt
        response_format = params.response_format

        if content.content_type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(content.data)
                file_path = temp_file.name
                images = convert_from_path(file_path)
                
                all_responses = []
                for image in images:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image_file:
                        image.save(temp_image_file.name, 'JPEG')
                        response = self._process_image(temp_image_file.name, model_name, key, prompt, query, response_format)
                        all_responses.append(response)
                    os.unlink(temp_image_file.name)
                
                response_content = "\n\n".join(all_responses)
                os.unlink(file_path)
        
        elif content.content_type in ["image/jpeg", "image/png"]:
            suffix = mimetypes.guess_extension(content.content_type)
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_image_file:
                temp_image_file.write(content.data)
                response_content = self._process_image(temp_image_file.name, model_name, key, prompt, query, response_format)
            os.unlink(temp_image_file.name)
        
        else:
            text = content.data.decode("utf-8")
            if query is None:
                query = text
            response_content = self._process_text(model_name, key, prompt, query, response_format)
        
        contents.append(Content.from_text(response_content))
        return contents

    def _process_image(self, image_path, model_name, key, prompt, query, response_format):
        client = self._get_client(key)

        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        messages_content = [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ]

        try: 
            response = client.beta.chat.completions.parse(
                model=model_name, 
                messages=messages_content, 
                response_format=response_format
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Unable to process image: {str(e)}")
            raise e

    def _process_text(self, model_name, key, prompt, query, response_format):
        client = self._get_client(key)
        
        messages_content = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]

        try: 
            response = client.beta.chat.completions.parse(
                model=model_name, 
                messages=messages_content, 
                response_format=response_format
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Unable to process text: {str(e)}")
            raise e

    def _get_client(self, key):
        if ('OPENAI_API_KEY' not in os.environ) and (key is None):
            raise ValueError("The OPENAI_API_KEY environment variable is not present and no API key was provided.")
        if ('OPENAI_API_KEY' in os.environ) and (key is None):
            return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        return OpenAI(api_key=key)

    def sample_input(self) -> Content:
        return Content.from_text("Alice and Bob are going to a science fair on Friday.")

if __name__ == "__main__":
    class CalendarEvent(BaseModel):
        name: str
        date: str
        participants: list[str]

    prompt = "Extract the event information."
    article = Content.from_text("Alice and Bob are going to a science fair on Friday.")
    input_params = OAIExtractorConfig(
        model="gpt-4o-2024-08-06",
        system_prompt=prompt,
        response_format=CalendarEvent
    )
    extractor = OAIExtractor()
    results = extractor.extract(article, params=input_params)
    print(results)

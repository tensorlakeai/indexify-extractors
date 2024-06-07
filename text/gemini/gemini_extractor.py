from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
import os
import google.generativeai as genai
from pdf2image import convert_from_path
import tempfile
import mimetypes

class GeminiExtractorConfig(BaseModel):
    model_name: Optional[str] = Field(default='gemini-1.5-flash-latest')
    key: Optional[str] = Field(default=None)
    system_prompt: str = Field(default='You are a helpful assistant.')
    user_prompt: Optional[str] = Field(default=None)

class GeminiExtractor(Extractor):
    name = "tensorlake/gemini"
    description = "An extractor that let's you use LLMs from Gemini."
    system_dependencies = []
    input_mime_types = ["text/plain", "application/pdf", "image/jpeg", "image/png"]

    def __init__(self):
        super(GeminiExtractor, self).__init__()

    def extract(self, content: Content, params: GeminiExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        model_name = params.model_name
        key = params.key
        prompt = params.system_prompt
        query = params.user_prompt

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
        
        def upload_to_gemini(path, mime_type=None):
            file = genai.upload_file(path, mime_type=mime_type)
            print(f"Uploaded file '{file.display_name}' as: {file.uri}")
            return file

        if ('GEMINI_API_KEY' not in os.environ) and (key is None):
            response_content = "The GEMINI_API_KEY environment variable is not present."
        else:
            if ('GEMINI_API_KEY' in os.environ) and (key is None):
                genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            else:
                genai.configure(api_key=key)
            generation_config = { "temperature": 1, "top_p": 0.95, "top_k": 64, "max_output_tokens": 8192, "response_mime_type": "text/plain", }
            model = genai.GenerativeModel( model_name=model_name, generation_config=generation_config, )
            if file_path:
                files = [upload_to_gemini(image_file, mime_type="image/jpeg") for image_file in image_files]
                chat_session = model.start_chat( history=[ { "role": "user", "parts": files, }, ] )
                response = chat_session.send_message(prompt)
            else:
                chat_session = model.start_chat( history=[ ] )
                response = chat_session.send_message(prompt + " " + query)

            response_content = response.text
        
        contents.append(Content.from_text(response_content))
        
        return contents

    def sample_input(self) -> Content:
        return Content.from_text("Hello world, I am a good boy.")

if __name__ == "__main__":
    prompt = """Extract all text from the document."""
    f = open("resume.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    input_params = GeminiExtractorConfig(prompt=prompt)
    extractor = GeminiExtractor()
    results = extractor.extract(pdf_data, params=input_params)
    print(results)
    prompt = """Extract all named entities from the text."""
    article = Content.from_text("My name is Rishiraj and I live in India.")
    input_params = GeminiExtractorConfig(prompt=prompt)
    extractor = GeminiExtractor()
    results = extractor.extract(article, params=input_params)
    print(results)
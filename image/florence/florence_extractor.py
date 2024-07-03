from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
import os
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import requests
import io

class FlorenceImageExtractorConfig(BaseModel):
    model_name: str = Field(default='microsoft/Florence-2-large')
    task_prompt: str = Field(default='<CAPTION>')
    text_input: Optional[str] = Field(default=None)

class FlorenceImageExtractor(Extractor):
    name = "tensorlake/florence"
    description = "An extractor that uses the Florence-2 model for image analysis tasks."
    system_dependencies = []
    input_mime_types = ["image/jpeg", "image/png", "image/gif"]

    def __init__(self):
        super(FlorenceImageExtractor, self).__init__()
        self.model = None
        self.processor = None

    def load_model(self, model_name):
        if self.model is None or self.processor is None:
            self.model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).eval().cuda()
            self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)

    def extract(self, content: Content, params: FlorenceImageExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        model_name = params.model_name
        task_prompt = params.task_prompt
        text_input = params.text_input

        self.load_model(model_name)

        image = Image.open(io.BytesIO(content.data))

        if text_input is None:
            prompt = task_prompt
        else:
            prompt = task_prompt + text_input

        inputs = self.processor(text=prompt, images=image, return_tensors="pt")
        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"].cuda(),
            pixel_values=inputs["pixel_values"].cuda(),
            max_new_tokens=1024,
            early_stopping=False,
            do_sample=False,
            num_beams=3,
        )
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = self.processor.post_process_generation(
            generated_text,
            task=task_prompt,
            image_size=(image.width, image.height)
        )

        contents.append(Content.from_text(str(parsed_answer)))
        
        return contents

    def sample_input(self) -> Content:
        return self.sample_jpg()

if __name__ == "__main__":
    image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/car.jpg?download=true"
    response = requests.get(image_url)
    image_content = Content(data=response.content, mime_type="image/jpeg")
    input_params = FlorenceImageExtractorConfig(task_prompt='<CAPTION>')
    extractor = FlorenceImageExtractor()
    results = extractor.extract(image_content, params=input_params)
    print(results)

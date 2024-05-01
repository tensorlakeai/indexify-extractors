from pydantic import BaseModel

from typing import List
import torch

from indexify_extractor_sdk import Extractor, Content, Feature
from indexify_extractor_sdk.base_extractor import Content
from transformers import AutoTokenizer, AutoModelForCausalLM
import PIL.Image as Image
import io
import json

class MoondreamConfig(BaseModel):
    prompt: str = "Describe this image."

class MoondreamExtractor(Extractor):
    name = "tensorlake/moondream"
    description = "This Extractor uses Moondream which is tiny LLM that can answer questions about images"

    input_mime_types = ["image/bmp", "image/gif", "image/jpeg", "image/png", "image/tiff"]

    def __init__(self):
        super(MoondreamExtractor).__init__()

        model_id = "vikhyatk/moondream2"
        revision = "2024-04-02"
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, trust_remote_code=True, revision=revision, torchscript=True
        )
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)

    def extract(self, content: Content, params: MoondreamConfig) -> List[Content]:
        image = Image.open(io.BytesIO(content.data))
        enc_image = self.model.encode_image(image)
        answer = self.model.answer_question(enc_image, params.prompt, self.tokenizer)
        return [Content.from_text(answer)]

    def sample_input(self) -> Content:
        return self.sample_jpg()

if __name__ == "__main__":
    extractor = MoondreamExtractor()
    input = extractor.sample_input()
    results = extractor.extract(input, MoondreamConfig())
    print(results)

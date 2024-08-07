from pydantic import BaseModel
from typing import List, Dict, Union
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import PIL.Image as Image
import io
from accelerate import Accelerator

from indexify_extractor_sdk import Extractor, Content, Feature
from indexify_extractor_sdk.base_extractor import Content
from indexify_extractor_sdk.exceptions import ExtractorError, InputValidationError, ModelLoadError, ExtractionProcessError, safe_execute
from indexify_extractor_sdk.logging_config import logger



class MoondreamConfig(BaseModel):
    prompt: str = "Describe this image."

class MoondreamExtractor(Extractor):
    name = "tensorlake/moondream"
    description = "This Extractor uses Moondream which is tiny LLM that can answer questions about images"
    input_mime_types = ["image/bmp", "image/gif", "image/jpeg", "image/png", "image/tiff"]

    @safe_execute
    def __init__(self):
        super(MoondreamExtractor, self).__init__()
        try:
            self._accelerator = Accelerator()
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            model_id = "vikhyatk/moondream2"
            revision = "2024-04-02"
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                trust_remote_code=True,
                revision=revision,
                torchscript=True,
            )

            if torch.cuda.is_available():
                model = model.to("cuda")

            self.model = model
            self.model.eval()
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
        except Exception as e:
            logger.error(f"Failed to initialize MoondreamExtractor: {str(e)}")
            raise ModelLoadError(f"Failed to load Moondream model: {str(e)}")

    @safe_execute
    def extract(self, content: Content, params: MoondreamConfig) -> List[Union[Feature, Content]]:
        if content.content_type not in self.input_mime_types:
            raise InputValidationError(f"Unsupported content type: {content.content_type}")

        try:
            image = Image.open(io.BytesIO(content.data))
            prompt = params.prompt
            
            answers = self.model.batch_answer([image], [prompt], self.tokenizer)
            
            results = []
            for answer in answers:
                results.append(Content.from_text(answer))
            
            return results
        except Exception as e:
            logger.error(f"Error during extraction: {str(e)}")
            raise ExtractionProcessError(f"Failed to process image: {str(e)}")

    @safe_execute
    def extract_batch(self, content_list: List[Content], params: List[MoondreamConfig]) -> List[List[Union[Feature, Content]]]:
        images = []
        prompts = []
        for content, config in zip(content_list, params):
            if content.content_type not in self.input_mime_types:
                raise InputValidationError(f"Unsupported content type: {content.content_type}")
            image = Image.open(io.BytesIO(content.data))
            images.append(image)
            prompts.append(config.prompt)

        try:
            answers = self.model.batch_answer(images, prompts, self.tokenizer)
            results = []
            for answer in answers:
                results.append([Content.from_text(answer)])
            return results
        except Exception as e:
            logger.error(f"Error during batch extraction: {str(e)}")
            raise ExtractionProcessError(f"Failed to process batch of images: {str(e)}")

    def sample_input(self) -> Content:
        config = MoondreamConfig()
        return (self.sample_jpg(), config.model_dump_json())

if __name__ == "__main__":
    extractor = MoondreamExtractor()
    input = extractor.sample_input()
    results = extractor.extract_batch({"task_id": input}, {"task_id": config.model_dump_json()})
    print(results)

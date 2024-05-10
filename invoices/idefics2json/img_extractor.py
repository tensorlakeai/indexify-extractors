import logging
import torch
import os
from PIL import Image
from io import BytesIO

from transformers import AutoProcessor, BitsAndBytesConfig, Idefics2ForConditionalGeneration
from huggingface_hub import hf_hub_download
from indexify_extractor_sdk import Content, Extractor, Feature
from parse_utils import token2json

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, Literal, List, Union

logger = logging.getLogger(__name__)
token = os.getenv('HF_TOKEN')

class ModelSettings(BaseSettings):
    peft_model_id: str = "nielsr/idefics2-cord-demo"
    hf_token: Optional[str] = token

model_settings = ModelSettings()

class ImgExtractorConfig(BaseModel):
    instruction: Optional[str] = "Extract JSON."

class ImgExtractor(Extractor):
    name = "tensorlake/idefics2json"
    description = "Finetuned Idefics2 for Image to JSON."
    system_dependencies = []
    input_mime_types = ["image/jpeg", "image/png"]

    def __init__(self):
        super(ImgExtractor, self).__init__()

        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        logger.info(f"Using device: {device.type}")
        torch_dtype = torch.float32 if device.type == "cpu" else torch.float16

        self.processor = AutoProcessor.from_pretrained(model_settings.peft_model_id)
        # Define quantization config
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch_dtype
        )
        # Load the base model with adapters on top
        self.model = Idefics2ForConditionalGeneration.from_pretrained(
            model_settings.peft_model_id,
            torch_dtype=torch_dtype,
            quantization_config=quantization_config,
        )
        # get the resized input embeddings
        filepath = hf_hub_download(repo_id="nielsr/idefics2-embeddings", filename="input_embeddings.pt", repo_type="dataset")
        input_embeddings = torch.load(filepath, map_location="cuda:0")
        input_embeddings_module = torch.nn.Embedding(input_embeddings.shape[0], input_embeddings.shape[1], _weight=input_embeddings)
        # set the resized output embeddings
        filepath = hf_hub_download(repo_id="nielsr/idefics2-embeddings", filename="output_embeddings.pt", repo_type="dataset")
        output_embeddings = torch.load(filepath, map_location="cuda:0")
        output_embeddings_module = torch.nn.Linear(output_embeddings.shape[0], output_embeddings.shape[1], bias=False)
        output_embeddings_module.weight = output_embeddings

        # set them accordingly
        self.model.resize_token_embeddings(len(self.processor.tokenizer))
        self.model.set_input_embeddings(input_embeddings_module)
        self.model.set_output_embeddings(output_embeddings_module)

    def extract(self, content: Content, params: ImgExtractorConfig) -> List[Union[Feature, Content]]:
        image = Image.open(BytesIO(content.data))
        # prepare image and prompt for the model
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": params.instruction},
                    {"type": "image"},
                ]
            },
        ]
        prompt = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(text=prompt, images=[image], return_tensors="pt").to("cuda")

        # Generate token IDs
        generated_ids = self.model.generate(**inputs, max_new_tokens=768)

        # Decode back into text
        generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        added_vocab = self.processor.tokenizer.get_added_vocab()
        generated_json = token2json(generated_texts[0], added_vocab)
        return [Content.from_text(str(generated_json))]
    
    def sample_input(self) -> Content:
        filepath = "sample.jpg"
        with open(filepath, 'rb') as f:
            image_data = f.read()
        return Content(content_type="image/jpg", data=image_data)

if __name__ == "__main__":
    filepath = "sample.jpg"
    with open(filepath, 'rb') as f:
        image_data = f.read()
    data = Content(content_type="image/jpg", data=image_data)
    params = ImgExtractorConfig(instruction="Extract JSON.")
    extractor = ImgExtractor()
    results = extractor.extract(data, params=params)
    print(results)
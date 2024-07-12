from pydantic import BaseModel

from typing import List, Dict, Union
import torch

from accelerate import Accelerator
from indexify_extractor_sdk import Extractor, Content, Feature
from indexify_extractor_sdk.base_extractor import Content
from transformers import AutoTokenizer, AutoModelForCausalLM
import PIL.Image as Image
import io

class MoondreamConfig(BaseModel):
    prompt: str = "Describe this image."

class MoondreamExtractor(Extractor):
    name = "tensorlake/moondream"
    description = "This Extractor uses Moondream which is tiny LLM that can answer questions about images"

    input_mime_types = ["image/bmp", "image/gif", "image/jpeg", "image/png", "image/tiff"]

    def __init__(self):
        super(MoondreamExtractor).__init__()

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

    def extract_batch(
        self, content_list: Dict[str, Content], input_params: Dict[str, MoondreamConfig]
    ) -> Dict[str, List[Union[Feature, Content]]]:
        images = []
        prompts = []
        tasks = []
        for (task_id, content) in content_list.items():
            image = Image.open(io.BytesIO(content.data))
            config = input_params.get(task_id, MoondreamConfig())
            images.append(image)
            prompts.append(config.prompt)
            tasks.append(task_id)
        answers = self.model.batch_answer(images, prompts, self.tokenizer)
        results = {}
        for (task_id, answer) in zip(tasks, answers):
            results[task_id] = [Content.from_text(answer)]
        return results

    def extract(
        self, content: Content, params: MoondreamConfig = None
    ) -> List[Union[Feature, Content]]:
        raise NotImplementedError()

    def sample_input(self) -> Content:
        return self.sample_jpg()

if __name__ == "__main__":
    extractor = MoondreamExtractor()
    input = extractor.sample_input()
    results = extractor.extract_batch({"task_id": input}, {"task_id": MoondreamConfig()})
    print(results)

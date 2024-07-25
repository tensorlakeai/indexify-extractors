from typing import List, Tuple
from indexify_extractor_sdk.base_extractor import Feature
from pydantic import BaseModel, Field
from llama_cpp import Llama
from indexify_extractor_sdk import Extractor, Content

class ModelConfig(BaseModel):
    model: str = Field(default='Meta-Llama-3.1-8B-Instruct-GGUF')
    system_prompt: str = Field(default='You are a helpful assistant.')
    max_tokens: int = Field(default=8000)

class LlamaCppExtractor(Extractor):
    name = "tensorlake/llama_cpp"
    description = "An extractor that let's you use LLMs from Llama CPP."
    input_mime_types = ["text/plain", "application/json"]

    def __init__(self):
        super(LlamaCppExtractor, self).__init__()
        self._model = Llama.from_pretrained("bullerwins/Meta-Llama-3.1-8B-Instruct-GGUF",filename="*Q8_0.gguf",)

    def extract(self, content: Content, params: ModelConfig) -> List[Content]:
        user_input = content.data.decode("utf-8")
        messages = [
            {"role": "system", "content": params.system_prompt},
            {"role": "user", "content": user_input}
        ]
        response = self._model.create_chat_completion(messages, max_tokens=params.max_tokens)
        result = response["choices"][0]["message"]["content"]
        return [Content.from_text(result)]
    
    def sample_input(self) -> Tuple[Content, ModelConfig]:
        return (Content.from_text("How to create a chatbot in Python?"), ModelConfig(max_tokens=10).model_dump_json())
    

if __name__ == "__main__":
    extractor = LlamaCppExtractor()
    content = extractor.sample_input()
    params = ModelConfig(max_tokens=100)
    print(extractor.extract(content, params))

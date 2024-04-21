from typing import List, Tuple
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Json
import pickle
import instructor
from openai import OpenAI

class InputParams(BaseModel):
    schema_bytes: bytes 
    model: str = "gpt-3.5-turbo"
    system_message: str | None
    instructions: str | None


# this is for testing purposes.
# pickle doesn't like it inside the sample_input function 
class UserInfo(BaseModel):
    name: str
    age: int
    place: str

class Instructor(Extractor):
    name = "tensorlake/instructor"
    description = "Instructor Extractor"
    system_dependencies = []


    def __init__(self):
        super().__init__()

    def extract(
        self, content: Content, params: InputParams 
    ) -> List[Content]:
        cls = pickle.loads(params.schema_bytes)
        text = content.data.decode("utf-8")
        client = instructor.from_openai(OpenAI())
        messages = [{"role": "user", "content": f"{params.instructions}: {text}"}]
        if params.system_message:
            messages.append({"role": "system", "content": params.system_message})
        model  = client.chat.completions.create(model=params.model,response_model=cls, messages=messages)
        return Feature.metadata(value=model.model_dump(), name="model")
    
    def sample_input(self) -> Tuple[Content, BaseModel]:
        data = pickle.dumps(UserInfo)
        params = InputParams(schema_bytes=data)
        return (self.sample_text(), params)
    
if __name__ == "__main__":
    extractor = Instructor()
    text, params = extractor.sample_input()
    contents = extractor.extract(text, params)
    print(contents)
    



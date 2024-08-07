from pydantic import BaseModel
from typing import List
from indexify_extractor_sdk import Extractor, Content, Feature
import json
import subprocess
import re
import os
import tempfile

# Extractors can be parameterized by providing a pydantic model
# as the second argument to the Extractor class. The model is exposed
# in the Indexify API so that users can dynamically change the behavior
# of the extractor for various use cases. Some examples here can be
# chunk size of audio clips during segmentation, or the text splitter algorithm
# for embedding long documents
class InputParams(BaseModel):
    a: int = 0
    b: str = ""

class WhisperCC(Extractor):
    name = "tensorflake/whisper.cc"
    description = "Description of the extractor goes here."
    system_dependencies = []
    input_mime_types = ["audio","audio/wav"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params: InputParams) -> List[Content]:
        cwd = os.getcwd()
        # Execute the command
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(content.data)
            file = open(fp.name, "rb").read()
        
        model = os.path.join(cwd, "models", "ggml-base.en-q5_0.bin")
        main = os.path.join(cwd, "main")
        
        result = subprocess.run(
            [main, "-m", model, file],
            capture_output=True,
            text=True
        )

        # Decode the byte data to string
        text_data = result.stdout

        # Regular expression to match the timestamp and text
        pattern = re.compile(r'\[(.*?) --> (.*?)\]\s*(.*?)(?=\[\d{2}:\d{2}:\d{2}\.\d{3} --> |\Z)', re.DOTALL)

        # # Parse the text
        entries = []
        for match in pattern.finditer(text_data):
            start_time, end_time, text = match.groups()
            entries.append({
                "timestamp": {"start": start_time, "end": end_time},
                "text": text.strip()
            })

        # Convert to JSON
        json_output = json.dumps(entries, indent=2)

        # Return transformed content
        return [
            Content.from_json(json_output),
        ]

    def sample_input(self) -> Content:
        return self.sample_mp3()

if __name__ == "__main__":
    # You can run the extractor by simply invoking this python file
    # python custom_extractor.py and that would run the extractor
    # with the sample input provided.
    print(WhisperCC().sample_input().data)

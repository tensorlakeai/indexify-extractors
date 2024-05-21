from typing import List

from indexify_extractor_sdk import (
    Extractor,
    Content,
)
from indexify_extractor_sdk.base_extractor import Feature
from pydantic import BaseModel
from . import whisper

class InputParams(BaseModel):
    chunk_length: int = 30
    max_new_tokens: int = 128

class WhisperExtractor(Extractor):
    name = "tensorlake/whisper-mlx"
    description = "Whisper ASR on Apple MLX"
    system_dependencies = ["ffmpeg"]
    input_mime_types = ["audio", "audio/mpeg"]
    def __init__(self):
        super().__init__()

    def extract(
        self, content: Content, params: InputParams) -> List[Content]:
        import tempfile
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(content.data)
            result = whisper.transcribe(fp.name)
            text = result['text']
            return [Content.from_text(text)]

    def sample_input(self) -> Content:
        return self.sample_mp3()

if __name__ == "__main__":
    extractor = WhisperExtractor()
    contents = extractor.extract(extractor.sample_mp3(), None)
    print(len(contents))
    for content in contents:
        print(len(content.features))
        for feature in content.features:
            print(feature.value)


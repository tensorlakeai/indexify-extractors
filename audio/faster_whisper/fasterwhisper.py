from pydantic import BaseModel
from typing import List
from indexify_extractor_sdk import Extractor, Content
import json
import io
from faster_whisper import WhisperModel

class InputParams(BaseModel):
    model: str = "small"

class FasterWhisper(Extractor):
    name = "tensorflake/fasterWhisper"
    description = "fasterWhisper transcripts audio into json with timestamps and text"
    system_dependencies = []
    input_mime_types = ["audio","audio/wav"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params: InputParams) -> List[Content]:
        # Wrap the content data in io.BytesIO
        audio_stream = io.BytesIO(content.data)
    
        model = WhisperModel(params.model, device="cpu", compute_type="int8")

        segments, info = model.transcribe(audio_stream, beam_size=5)

        entries = []
        for segment in segments:
            entries.append({
                "timestamp": {"start": segment.start, "end": segment.end},
                "text": segment.text.strip()
            })

        # Convert to JSON if needed
        json_output = json.dumps(entries, indent=2)

        # Return transformed content as needed
        return [
            Content.from_json(json_output), 
        ]
    
    def sample_input(self) -> Content:
        return self.sample_mp3()

if __name__ == "__main__":
    print(FasterWhisper().sample_input().data)
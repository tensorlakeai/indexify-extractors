from pydantic import BaseModel
from typing import List
from indexify_extractor_sdk import Extractor, Content
import json
import tempfile
from faster_whisper import WhisperModel

class InputParams(BaseModel):
    model: str = "small"

def save_bytes_to_wav(bytes_payload):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
        wav_file.write(bytes_payload)
        temp_file_name = wav_file.name
    
    return temp_file_name


class FasterWhisper(Extractor):
    name = "tensorflake/fasterWhisper"
    description = "Description of the extractor goes here."
    system_dependencies = []
    input_mime_types = ["audio","audio/wav"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params: InputParams) -> List[Content]:
        wavFile = save_bytes_to_wav(content.data)
    
        model = WhisperModel(params.model, device="cpu", compute_type="int8")

        segments, info = model.transcribe(wavFile, beam_size=5)

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

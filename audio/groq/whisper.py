from indexify_extractor_sdk import Extractor, Content

from pydantic import BaseModel, Field

from openai import OpenAI
import os

class TranscriptionParams(BaseModel):
    prompt: str = Field(default="")

def chunked(size, source):
    for i in range(0, len(source), size):
        yield source[i:i+size]
class WhisperExtractor(Extractor):
    name = "tensorlake/whispergroq"
    description = "Whisper ASR using GROQ."
    input_mime_types = ["audio", "audio/mpeg"]

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self._groq = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    def extract(self, content: Content, params: TranscriptionParams):
        chunks = list(chunked(24000, content.data))
        text = ""
        for chunk in chunks:
            try:
                transcription = self._groq.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=("temp." + "mp3", chunk, content.content_type),
                    response_format="json",
                    prompt=params.prompt
                )
                text += transcription.text
            except Exception as e:
                print(f"unable to call groq {e}")
                raise e
        return [Content.from_text(text)]
    
    def sample_input(self) -> Content:
        return self.sample_mp3()


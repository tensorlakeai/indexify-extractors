from indexify_extractor_sdk import Extractor, Content

from pydantic import BaseModel, Field

from openai import OpenAI
import os

class TranscriptionParams(BaseModel):
    prompt: str = Field(default="")

class WhisperExtractor(Extractor):
    name = "tensorlake/whispergroq"
    description = "Whisper ASR using GROQ."
    input_mime_types = ["audio", "audio/mpeg"]

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self._groq = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    def extract(self, content: Content, params: TranscriptionParams):
        transcription = self._groq.audio.transcriptions.create(
            model="whisper-large-v3",
            file=("temp." + "mp3", content.data, content.content_type),
            response_format="json",
            prompt=params.prompt
        )
        return [Content.from_text(transcription.text)]
    
    def sample_input(self) -> Content:
        return self.sample_mp3()


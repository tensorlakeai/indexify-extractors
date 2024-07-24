import logging
import torch
import tempfile
import base64
import os

from indexify_extractor_sdk import Content, Extractor, Feature
from pyannote.audio import Pipeline
from transformers import pipeline, AutoModelForCausalLM
from .diarization_utils import diarize
from huggingface_hub import HfApi
from starlette.exceptions import HTTPException

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, Literal, List, Union

logger = logging.getLogger(__name__)
token = os.getenv('HF_TOKEN')

class ModelSettings(BaseSettings):
    asr_model: str = "openai/whisper-large-v3"
    assistant_model: Optional[str] = "distil-whisper/distil-large-v3"
    diarization_model: Optional[str] = "pyannote/speaker-diarization-3.1"
    hf_token: Optional[str] = token

model_settings = ModelSettings()

class ASRExtractorConfig(BaseModel):
    task: Literal["transcribe", "translate"] = "transcribe"
    batch_size: int = 24
    assisted: bool = False
    chunk_length_s: int = 30
    sampling_rate: int = 16000
    language: Optional[str] = None
    num_speakers: Optional[int] = None
    min_speakers: Optional[int] = None
    max_speakers: Optional[int] = None

class ASRExtractor(Extractor):
    name = "tensorlake/asrdiarization"
    description = "Powerful ASR + diarization + speculative decoding."
    system_dependencies = ["ffmpeg"]
    input_mime_types = ["audio", "audio/mpeg"]

    def __init__(self):
        super(ASRExtractor, self).__init__()

        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        torch_dtype = torch.float32 if device.type == "cpu" else torch.float16
        print(f"Using device: {device.type} data_type: {torch_dtype}")

        self.assistant_model = AutoModelForCausalLM.from_pretrained(
            model_settings.assistant_model,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ) if model_settings.assistant_model else None

        if self.assistant_model:
            self.assistant_model.to(device)

        self.asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model=model_settings.asr_model,
            torch_dtype=torch_dtype,
            device=device
        )

        if model_settings.diarization_model:
            # diarization pipeline doesn't raise if there is no token
            HfApi().whoami(model_settings.hf_token)
            self.diarization_pipeline = Pipeline.from_pretrained(
                checkpoint_path=model_settings.diarization_model,
                use_auth_token=model_settings.hf_token,
            )
            self.diarization_pipeline.to(device)
        else:
            self.diarization_pipeline = None

    def extract(self, content: Content, params: ASRExtractorConfig) -> List[Union[Feature, Content]]:
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(content.data)
            file = open(fp.name, "rb").read()
            logger.info(f"inference params: {params}")

            generate_kwargs = {
                "task": params.task,
                "language": params.language,
                "assistant_model": self.assistant_model if params.assisted else None
            }

            asr_outputs = self.asr_pipeline(
                file,
                chunk_length_s=params.chunk_length_s,
                batch_size=params.batch_size,
                generate_kwargs=generate_kwargs,
                return_timestamps=True,
            )

            if self.diarization_pipeline:
                transcript = diarize(self.diarization_pipeline, file, params, asr_outputs)
            else:
                transcript = []

            return [Content.from_json(transcript)]

    def sample_input(self) -> Content:
        return self.sample_mp3()

if __name__ == "__main__":
    params = ASRExtractorConfig(batch_size=24)
    extractor = ASRExtractor()
    results = extractor.extract(extractor.sample_mp3(), params=params)
    print(results)

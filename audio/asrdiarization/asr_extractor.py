import logging
import torch
import io
import numpy as np

from indexify_extractor_sdk import Content, Extractor, Feature
from pyannote.audio import Pipeline
from transformers import pipeline, AutoModelForCausalLM
from .diarization_utils import diarize

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, Literal, List, Union

logger = logging.getLogger(__name__)

class ModelSettings(BaseSettings):
    asr_model: str = "tensorlake/whisper-large-v3"
    assistant_model: Optional[str] = "tensorlake/distil-large-v3"
    diarization_model: Optional[str] = "tensorlake/speaker-diarization-3.1"

model_settings = ModelSettings()

class ASRExtractorConfig(BaseModel):
    task: Literal["transcribe", "translate"] = "transcribe"
    batch_size: int = 1
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
        print(f"ASR model: {model_settings.asr_model}, Assistant Model: {model_settings.assistant_model}")

        try:
            self.assistant_model = AutoModelForCausalLM.from_pretrained(
                model_settings.assistant_model,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
        except Exception as e:
            print(f"Error loading assistant model: {str(e)}")
            raise e

        try:
            self.asr_pipeline = pipeline(
                "automatic-speech-recognition",
                model=model_settings.asr_model,
                torch_dtype=torch_dtype,
                device=device
            )
            self.diarization_pipeline = Pipeline.from_pretrained(
                checkpoint_path=model_settings.diarization_model,
            )
            self.diarization_pipeline.to(device)
        except Exception as e:
            print(f"Error loading ASR or diarization model: {str(e)}")
            raise e
        print("ASR and diarization models loaded successfully.")

    def extract(self, content: Content, params: ASRExtractorConfig) -> List[Union[Feature, Content]]:
            generate_kwargs = {
                "task": params.task,
                "language": params.language,
                "assistant_model": self.assistant_model
            }

            try:
                asr_outputs = self.asr_pipeline(
                    np.frombuffer(content.data, dtype=np.int8),
                    chunk_length_s=params.chunk_length_s,
                    batch_size=params.batch_size,
                    generate_kwargs=generate_kwargs,
                    return_timestamps=True,
                )
            except RuntimeError as e:
                logger.error(f"ASR inference error: {str(e)}")
                raise RuntimeError(f"ASR inference error: {str(e)}")
            except Exception as e:
                logger.error(f"Unknown error diring ASR inference: {str(e)}")
                raise Exception(f"Unknown error during ASR inference: {str(e)}")

            if self.diarization_pipeline:
                try:
                    transcript = diarize(self.diarization_pipeline, io.BytesIO(content.data).read(), params, asr_outputs)
                except RuntimeError as e:
                    logger.error(f"Diarization inference error: {str(e)}")
                    raise RuntimeError(f"Diarization inference error: {str(e)}")
                except Exception as e:
                    logger.error(f"Unknown error during diarization: {str(e)}")
                    raise Exception(f"Unknown error during diarization: {str(e)}")
            else:
                transcript = []

            return [Content.from_json(transcript)]
    
    def sample_input(self) -> Content:
        return self.sample_mp3()

if __name__ == "__main__":
    params = ASRExtractorConfig(batch_size=1)
    extractor = ASRExtractor()
    results = extractor.extract(extractor.sample_mp3(), params=params)
    print(results)

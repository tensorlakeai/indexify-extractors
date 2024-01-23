from pydantic import BaseModel

from typing import List

from indexify_extractor_sdk import (
    Extractor,
    Content,
)

import json

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


class InputParams(BaseModel):
    chunk_length: int = 30
    max_new_tokens: int = 128


class WhisperExtractor(Extractor):
    input_mimes = ["audio", "audio/mpeg"]
    def __init__(self):
        super().__init__()
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        model_id = "distil-whisper/distil-large-v2"
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )
        model.to(device)
        processor = AutoProcessor.from_pretrained(model_id)
        self._pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=15,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=torch_dtype,
            device=device,
        )

    def extract(
        self, content: Content, params: InputParams) -> List[Content]:
        result = self._pipe(content.data)
        text = result['text']
        return [Content.from_text(text)]

    def sample_input(self) -> Content:
        import os
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "SDS_746.mp3")
        with open(filename, "rb") as f:
            data = f.read()
        return Content(content_type="audio/mpeg", data=data)

if __name__ == "__main__":
    extractor = WhisperExtractor()
    with open("all-in-e154.mp3", "rb") as f:
        data = f.read()
    content = Content(content_type="audio", data=data)
    print(extractor.extract([content], InputParams()))

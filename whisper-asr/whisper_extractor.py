from pydantic import BaseModel

from typing import List

from indexify_extractor_sdk import (
    Extractor,
    Content,
    Feature,
    EmbeddingSchema,
    ExtractorSchema,
)

import json

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


class InputParams(BaseModel):
    chunk_length: int = 30
    max_new_tokens: int = 128


class WhisperExtractor(Extractor):
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
        self, content_list: List[Content], params: InputParams
    ) -> List[List[Content]]:
        out: List[List[Content]] = []
        for content in content_list:
            if content.content_type not in ["audio", "audio/mpeg"]:
                continue
            result = self._pipe(content.data)
            text = result['text']
            out.append([Content(content_type="text/plain", data=bytes(text, "utf-8"))])
        return out

    @classmethod
    def schemas(cls) -> ExtractorSchema:
        """
        Returns a list of options for indexing.
        """
        return ExtractorSchema(
            features={},
        )


if __name__ == "__main__":
    extractor = WhisperExtractor()
    with open("all-in-e154.mp3", "rb") as f:
        data = f.read()
    content = Content(content_type="audio", data=data)
    print(extractor.extract([content], InputParams()))

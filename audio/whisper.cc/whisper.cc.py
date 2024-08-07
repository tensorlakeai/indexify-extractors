from pydantic import BaseModel
from typing import List
from indexify_extractor_sdk import Extractor, Content, Feature
import json
import subprocess
import re
import os
import tempfile
import argparse
import whispercpp as w

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
        ##todo: Add timestamps and fetch take the wav file as input
        transcriber = w.Whisper.from_pretrained("base.en")
        res = transcriber.transcribe_from_file("output.wav")
        return [
            Content.from_text(res)
        ]

    def sample_input(self) -> Content:
        return self.sample_mp3()

if __name__ == "__main__":
    print(WhisperCC().sample_input().data)

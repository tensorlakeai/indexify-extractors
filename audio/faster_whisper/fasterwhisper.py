from pydantic import BaseModel
from typing import List
from indexify_extractor_sdk import Extractor, Content, Feature
import json
import subprocess
import re
import os
import tempfile
import argparse
from transformers.pipelines.audio_utils import ffmpeg_read
import torch
from faster_whisper import WhisperModel

class InputParams(BaseModel):
    model: str = "small"

class FasterWhisper(Extractor):
    name = "tensorflake/fasterWhisper"
    description = "Description of the extractor goes here."
    system_dependencies = []
    input_mime_types = ["audio","audio/wav"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params: InputParams) -> List[Content]:
        # Create a temporary file to hold the audio data
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(content.data)  # Write the audio bytes to the file
            file = open(fp.name, "rb").read() # Store the name for later use
        # Use ffmpeg_read to convert the audio file to a float32 tensor
        inputs = ffmpeg_read(file, 16000)

        # Convert the input to a Torch tensor and ensure it's float32
        diarizer_inputs = torch.from_numpy(inputs).float()
        print("Diarizer inputs type (before unsqueeze):", diarizer_inputs.dtype)
        print("Diarizer inputs type (before unsqueeze): dim", diarizer_inputs.shape)
        diarizer_inputs = diarizer_inputs.unsqueeze(0)  # Add batch dimension
        # Load the Whisper model
        print("Diarizer inputs type (after unsqueeze):", diarizer_inputs.dtype)
        print("Diarizer inputs type (after unsqueeze): dim", diarizer_inputs.shape)
        model = WhisperModel(params.model, device="cpu", compute_type="int8")

        # Transcribe the audio using the model
        segments, info = model.transcribe(diarizer_inputs, beam_size=5)

        # Optionally, parse and convert segments to JSON or any other format
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

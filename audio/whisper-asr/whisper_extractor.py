from typing import List

from indexify_extractor_sdk import (
    Extractor,
    Content,
)
from indexify_extractor_sdk.base_extractor import Feature
from pydantic import BaseModel
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from accelerate import Accelerator
from accelerate.utils import gather_object

class InputParams(BaseModel):
    chunk_length: int = 30
    max_new_tokens: int = 128

class WhisperExtractor(Extractor):
    name = "tensorlake/whisper-asr"
    description = "Whisper ASR"
    system_dependencies = ["ffmpeg"]
    input_mime_types = ["audio", "audio/mpeg"]
    def __init__(self):
        super().__init__()
        self._accelerator = Accelerator()
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        model_id = "distil-whisper/distil-large-v2"

        # FIXME : THERE MUST BE A BETTER WAY TO DO THIS
        if torch.cuda.is_available():
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                device_map={"":self._accelerator.process_index},
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True,
            )
        else:
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True,
            )
        processor = AutoProcessor.from_pretrained(model_id)
        if torch.cuda.is_available():
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
                device_map={"":self._accelerator.process_index},
            )
        else:
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
            )

    def extract(
        self, content: Content, params: InputParams) -> List[Content]:
        result = self._pipe(content.data)
        text = result['text']
        return [Content.from_text(text)]
    
    def extract_batch(self, content_list: List[Content], params: type[BaseModel] = None) -> List[List[Feature | Content]]:
        out = []
        with self._accelerator.split_between_processes(content_list) as content_list:
            data = [content.data for content in content_list]
            results = self._pipe(data)
            texts = []
            for result in results:
                texts.append(result["text"])
            for text in texts:
                out.append([Content.from_text(text)])
        results_gathered = gather_object(out)
        return results_gathered


    def sample_input(self) -> Content:
        return self.sample_mp3()

if __name__ == "__main__":
    extractor = WhisperExtractor()
    content_list = [extractor.sample_mp3(), extractor.sample_mp3()]
    contents = extractor.extract_batch(content_list)
    print(len(contents))
    for content in contents:
        print(len(content.features))
        for feature in content.features:
            print(feature.value)


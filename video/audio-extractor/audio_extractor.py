from typing import List
from indexify_extractor_sdk import Content, Extractor, Feature
import moviepy.editor as mp
import tempfile
from pydantic import BaseModel

class AudioExtractorConfig(BaseModel):
   pass


class AudioExtractor(Extractor):
    name = "tensorlake/audio-extractor"
    description = "Extract audio from video"
    input_mime_types = ["video", "video/mp4", "video/mov", "video/avi"]

    def __init__(self):
        super(AudioExtractor, self).__init__()

    def extract(self, content: Content, params: AudioExtractorConfig) -> List[Content]:
        suffix = f'.{content.content_type.split("/")[-1]}'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmpfile:
            # write bytes to temp file
            tmpfile.write(content.data)
            tmpfile.flush() 

            # moviepy read file 
            video = mp.VideoFileClip(tmpfile.name)
            
            # write audio to tmp file and return content
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as tmpfile_audio:
                video.audio.write_audiofile(tmpfile_audio.name, codec="libmp3lame")
                f = open(tmpfile_audio.name, "rb")
                data = f.read()
                return [Content(data=data, content_type="audio/mpeg")]

    def sample_input(self) -> Content:
        return self.sample_mp4()


if __name__ == "__main__":
    AudioExtractor().extract_sample_input()

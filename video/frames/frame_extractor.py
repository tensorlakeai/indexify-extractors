from indexify_extractor_sdk import Content, Extractor, Feature
from typing import List
import cv2
import tempfile
from io import BytesIO
from pydantic import BaseModel

class FrameExtractorConfig(BaseModel):
    max_fps:int = 60
class FrameExtractor(Extractor):
    name = "tensorlake/frame-extractor"
    description = "Extract frames from video"
    input_mime_types = ["video", "video/mp4"]

    def __init__(self):
        super(FrameExtractor, self).__init__()

    def get_skip_factor(self,fps:float, max_fps:int):
        if fps > max_fps:
            skip_factor = int(fps / max_fps)
        else:
            skip_factor = 1
        return skip_factor

    def extract(self, content: Content, params: FrameExtractorConfig) -> List[Content]:
        content_list = []
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=True) as tmpfile:
            tmpfile.write(content.data)
            tmpfile.flush()  # Ensure data is written to disk
            
            cap = cv2.VideoCapture(tmpfile.name)
            fps = cap.get(cv2.CAP_PROP_FPS)

            skip_factor = self.get_skip_factor(fps, params.max_fps)

            frame_count = 0
            while cap.isOpened():
                # Capture frame-by-frame
                ret, frame = cap.read()

                if not ret:
                    break
                
                frame_count += 1

                # skip frame
                if (frame_count - 1) % skip_factor != 0:
                    continue

                # extract frame
                output = BytesIO()
                _, buffer = cv2.imencode('.jpg', frame)
                output.write(buffer)

                feature = Feature.metadata(
                    {"frame": frame_count, "timestamp": frame_count / fps}
                )
                
                content_list.append(
                    Content(
                        content_type=f"image/jpeg",
                        data=output.getvalue(),
                        features=[feature],
                    )
                )
                
            return content_list


    def sample_input(self) -> Content:
        file_path = "sample.mp4"

        with open(file_path, "rb") as f:
            data = f.read()

        return Content(
            data=data,
            content_type="video/mp4",
            features=[Feature.metadata({"filename": file_path})],
        )


if __name__ == "__main__":
    contents = FrameExtractor().extract_sample_input()
    print(len(contents))
    for content in contents:
        print(len(content.features))
        for feature in content.features:
            print(feature.value)

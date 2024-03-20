from indexify_extractor_sdk import Content, Extractor, Feature
from typing import List
import cv2
import tempfile
from io import BytesIO
from pydantic import BaseModel


class FrameExtractorConfig(BaseModel):
    max_fps: int = 60
    # specifying key frames will override max_fps
    key_frames: bool = False
    key_frames_threshold: float = 0.8


class FrameExtractor(Extractor):
    name = "tensorlake/frame-extractor"
    description = "Extract frames from video"
    input_mime_types = ["video", "video/mp4"]

    def __init__(self):
        super(FrameExtractor, self).__init__()

    def get_skip_factor(self, fps: float, max_fps: int):
        if fps > max_fps:
            skip_factor = int(fps / max_fps)
        else:
            skip_factor = 1
        return skip_factor

    def is_keyframe(self, hist_current, hist_prev, threshold):
        similarity = cv2.compareHist(hist_current, hist_prev, cv2.HISTCMP_CORREL)
        return similarity < threshold

    def frame_to_content(self, frame, frame_count, fps) -> Content:
        output = BytesIO()
        _, buffer = cv2.imencode(".jpg", frame)
        output.write(buffer)

        feature = Feature.metadata(
            {"frame": frame_count, "timestamp": frame_count / fps}
        )

        return Content(
            content_type=f"image/jpeg",
            data=output.getvalue(),
            features=[feature],
        )

    def extract(self, content: Content, params: FrameExtractorConfig) -> List[Content]:
        content_list = []

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as tmpfile:
            tmpfile.write(content.data)
            tmpfile.flush()  # Ensure data is written to disk

            cap = cv2.VideoCapture(tmpfile.name)
            fps = cap.get(cv2.CAP_PROP_FPS)

            frame_count = 0
            skip_factor = self.get_skip_factor(fps, params.max_fps)
            hist_prev = None
            while cap.isOpened():
                # Capture frame-by-frame
                ret, frame = cap.read()

                if not ret:
                    break

                if params.key_frames:
                    # calculate histogram
                    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    hist_current = cv2.calcHist(
                        [frame_gray], [0], None, [256], [0, 256]
                    )
                    if (hist_prev is None) or self.is_keyframe(
                        hist_current, hist_prev, params.key_frames_threshold
                    ):
                        content_list.append(
                            self.frame_to_content(frame, frame_count, fps)
                        )
                    hist_prev = hist_current
                elif frame_count % skip_factor == 0:
                    content_list.append(self.frame_to_content(frame, frame_count, fps))

                frame_count += 1

            return content_list

    def sample_input(self) -> Content:
        return self.sample_mp4()

if __name__ == "__main__":
    contents = FrameExtractor().extract_sample_input()
    print(len(contents))
    for content in contents:
        print(len(content.features))
        for feature in content.features:
            print(feature.value)

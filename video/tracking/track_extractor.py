from typing import List, Union
from indexify_extractor_sdk import Content, Extractor, Feature
import requests
import tempfile
import cv2
from ultralytics import YOLO

class TrackExtractor(Extractor):
    name = "tensorlake/tracking"
    description = "A YOLO based object tracker for video."
    system_dependencies = ["ffmpeg", "libsm6", "libxext6"]
    input_mime_types = ["video", "video/mp4"]

    def __init__(self):
        super().__init__()
        self.model = YOLO('yolov8n.pt')

    def extract(self, content: Content, params = None) -> List[Union[Feature, Content]]:
        features = []
        frame_count = 0
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            self.filename = tmpfile.name
            tmpfile.write(content.data)
            tmpfile.flush()

        # Open the video file
        cap = cv2.VideoCapture(self.filename)

        # Loop through the video frames
        while cap.isOpened():
            # Read a frame from the video
            success, frame = cap.read()

            if success:
                # Run YOLOv8 tracking on the frame, persisting tracks between frames
                results = self.model.track(frame, persist=True)

                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        b = box.xyxy[0]
                        c = box.cls
                        id = box.id.int().tolist()
                        name = self.model.names[int(c)]
                        feature = Feature.metadata({"frame": frame_count, "track_id": id, "bounding_box": b.tolist(), "object_name": name})
                        features.append(feature)
            frame_count += 1

        return features

    def sample_input(self) -> Content:
        return self.sample_mp4()

if __name__ == "__main__":
    filename = "sample.mp4"
    with requests.get("https://extractor-files.diptanu-6d5.workers.dev/sample.mp4", stream=True) as r:
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    f = open(filename, "rb")
    video_data = Content(content_type="video/mp4", data=f.read())
    extractor = TrackExtractor()
    results = extractor.extract(video_data)
    print(results)
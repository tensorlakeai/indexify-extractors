from indexify_extractor_sdk import Content, Extractor, Feature
from typing import List, Union
from ultralytics import YOLO
import numpy as np
import cv2


class YoloExtractor(Extractor):
    name = "tensorlake/yolo-extractor"
    description = "Extract yolo features from images"
    input_mime_types = ["image", "image/jpeg", "image/png"]
    system_dependencies = ["ffmpeg", "libsm6", "libxext6"]

    def __init__(self):
        super(YoloExtractor, self).__init__()
        self._download_file("https://extractor-files.diptanu-6d5.workers.dev/yolov9e.pt","yolov9e.pt")
        self.model = YOLO("yolov9e.pt")

    def extract(self, content: Content, params=None) -> List[Union[Feature, Content]]:
        image_array = np.frombuffer(content.data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_ANYCOLOR)

        results = self.model(image)

        features = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0]
                c = box.cls
                name = self.model.names[int(c)]
                feature = Feature.metadata(
                    value={"bounding_box": b.tolist(), "object_name": name},
                    comment={"bounding_box": "Bounding box coordinates in the format [x1, y1, x2, y2]"}
                )
                features.append(feature)

        return features

    def sample_input(self) -> Content:
        return self.sample_jpg()

if __name__ == "__main__":
    extractor = YoloExtractor()
    input = extractor.sample_input()
    extractor.extract(input)

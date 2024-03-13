from indexify_extractor_sdk import Content, Extractor, Feature
from typing import List, Union
from ultralytics import YOLO
import numpy as np
import cv2


class YoloExtractor(Extractor):
    name = "tensorlake/yolo-extractor"
    description = "Extract yolo features from images"
    input_mime_types = ["image", "image/jpeg", "image/png"]

    def __init__(self):
        super(YoloExtractor, self).__init__()
        self.model = YOLO("yolov9c.pt")

    def extract(self, content: Content, params: None) -> List[Union[Feature, Content]]:
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
                feature = Feature.metadata({"bounding_box": b.tolist(), "name": name})
                features.append(feature)

        return features

    def sample_input(self) -> Content:
        file_path = "ny.jpg"

        with open(file_path, "rb") as f:
            data = f.read()

        return (
            Content(
                data=data,
                content_type="image/jpeg",
                features=[],
            ),
            None,
        )


if __name__ == "__main__":
    features = YoloExtractor().extract_sample_input()
    print(features)

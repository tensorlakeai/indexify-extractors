from indexify_extractor_sdk import Content, Extractor, Feature
from typing import List
from ultralytics import YOLO
import numpy as np
import cv2
import json

class YoloExtractor(Extractor):
    name = "tensorlake/yolo-extractor"
    description = "Extract yolo features from images"
    input_mime_types = ["image", "image/jpeg", "image/png"]

    def __init__(self):
        super(YoloExtractor, self).__init__()
        self.model = YOLO('yolov8n.pt')

    def extract(self, content: Content, params: None) -> List[Content]:
        image_array = np.frombuffer(content.data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_ANYCOLOR)

        results = self.model(image)
        
        all_detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0]
                c = box.cls
                name = self.model.names[int(c)]
                detection = {"bounding_box": b.tolist(), "class_name": name}
                all_detections.append(detection)
            
        return [Content(
            data=bytes(json.dumps(all_detections), "utf-8"),
            content_type="text/json",
            features=[],
        )]


    def sample_input(self) -> Content:
        file_path = "ny.jpg"

        with open(file_path, "rb") as f:
            data = f.read()

        return Content(
            data=data,
            content_type="image/jpeg",
            features=[],
        )


if __name__ == "__main__":
    contents = YoloExtractor().extract_sample_input()
    print(len(contents))
    for content in contents:
        print(len(content.features))
        for feature in content.features:
            print(feature.value)

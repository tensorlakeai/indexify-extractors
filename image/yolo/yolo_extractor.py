from indexify_extractor_sdk import Content, Extractor, Feature
from typing import List
from ultralytics import YOLO
import numpy as np
import cv2


class YoloExtractor(Extractor):
    name = "tensorlake/yolo-extractor"
    description = "Extract yolo features from images"
    input_mime_types = ["image", "image/jpeg", "image/png"]

    def __init__(self):
        super(YoloExtractor, self).__init__()
        self.model = YOLO("yolov8n.pt")

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
                # crop
                x_min, y_min, x_max, y_max = map(int, b)
                cropped_image = image[y_min:y_max, x_min:x_max]

                # convert to jpg
                success, buffer = cv2.imencode(
                    ".jpg", cropped_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100]
                )

                if not success:
                    print("unable to encode image to jpeg")
                    continue
                
                feature = Feature.metadata({"bounding_box": b.tolist(), "name": name})
                all_detections.append(
                    Content(
                        data=buffer.tobytes(),
                        content_type="image/jpeg",
                        features=[feature],
                    )
                )

        return all_detections

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

from typing import List
from pydantic import BaseModel
from indexify_extractor_sdk import Extractor, Content, Feature
import tempfile
import mimetypes
from groundingdino.util.inference import load_model, load_image, predict
from PIL import Image


class GroundingDinoConfig(BaseModel):
    prompt: str = "person"
    box_threshold: float = 0.35
    text_threshold: float = 0.25


class GroundingDinoExtractor(Extractor):
    name = "tensorlake/groundingdino"
    description = "This extractor uses groundingdino which is a zero-shot object detector. It can identify objects from categories it was not specifically trained on based on a prompt."
    input_mime_types = ["image/jpeg", "image/png"]
    system_dependencies = []

    def __init__(self):
        super(GroundingDinoExtractor, self).__init__()
        self._download_file("https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth", "groundingdino_swint_ogc.pth")
        self.model = load_model(
            "GroundingDINO_SwinT_OGC.py", "groundingdino_swint_ogc.pth"
        )

    def scale_bounding_box_to_pixels(self, box, img_width, img_height):
        x_center, y_center, width, height = box

        # Calculate pixel values
        box_width = width * img_width
        box_height = height * img_height
        left = (x_center * img_width) - (box_width / 2)
        top = (y_center * img_height) - (box_height / 2)
        right = left + box_width
        bottom = top + box_height
        return [int(v) for v in [left, top, right, bottom]]

    def get_image_size(self, image_path):
        with Image.open(image_path) as img:
            width, height = img.size
        return width, height

    def extract(self, content: Content, params: GroundingDinoConfig) -> List[Feature]:
        suffix = mimetypes.guess_extension(content.content_type)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            _, image = load_image(inputtmpfile.name)

            boxes, logits, phrases = predict(
                model=self.model,
                image=image,
                caption=params.prompt,
                box_threshold=params.box_threshold,
                text_threshold=params.text_threshold,
                device="cpu",
            )
            width, height = self.get_image_size(inputtmpfile.name)
            metadata = []
            for box, logit, phrase in zip(boxes, logits, phrases):
                metadata.append(
                    Feature.metadata(
                        value={
                            "boundingbox": self.scale_bounding_box_to_pixels(
                                box.tolist(), width, height
                            ),
                            "score": logit.item(),
                            "phrase": phrase,
                        }
                    )
                )

            return metadata

    def sample_input(self) -> Content:
        return self.sample_jpg()


if __name__ == "__main__":
    GroundingDinoExtractor().extract_sample_input()

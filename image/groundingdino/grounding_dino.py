from typing import List
from pydantic import BaseModel
from indexify_extractor_sdk import Extractor, Content, Feature
import tempfile
import mimetypes
from groundingdino.util.inference import load_model, load_image, predict


class GroundingDinoConfig(BaseModel):
    prompt: str = "dog"


class GroundingDinoExtractor(Extractor):
    name = "tensorlake/groundingdino"
    description = "This extractor uses groundingdino which is a zero-shot object detector. It can identify objects from categories it was not specifically trained on based on a prompt."
    input_mime_types = ["image/jpeg", "image/png"]
    system_dependencies = []

    def __init__(self):
        super(GroundingDinoExtractor, self).__init__()
        self.model = load_model(
            "GroundingDINO_SwinT_OGC.py", "groundingdino_swint_ogc.pth"
        )

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
                box_threshold=0.35,
                text_threshold=0.25,
                device="cpu",
            )

            metadata = []
            for box, logit, phrase in zip(boxes, logits, phrases):
                metadata.append(
                    Feature.metadata(
                        value={
                            "boundingbox": box.tolist(),
                            "score": logit.item(),
                            "phrase": phrase,
                        }
                    )
                )

            return metadata

    def sample_input(self) -> Content:
        f = open("sample.jpg", "rb")
        return Content(content_type="image/jpeg", data=f.read())


if __name__ == "__main__":
    GroundingDinoExtractor().extract_sample_input()

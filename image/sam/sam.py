import torch
from transformers import SamModel, SamProcessor
from typing import List
from pydantic import BaseModel
from indexify_extractor_sdk import Extractor, Content, Feature
from PIL import Image
from io import BytesIO
import json
import numpy as np


class SamConfig(BaseModel):
    boundingbox_key: str = "boundingbox"
    class_key: str = "phrase"


class SamExtractor(Extractor):
    name = "tensorlake/sam"
    description = "This extractor uses SAM (Segment-Anything-Model), given content with features containing some boundingbox and classname, extract segments."
    input_mime_types = ["image/jpeg", "image/png"]
    system_dependencies = []

    def __init__(self):
        super(SamExtractor, self).__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SamModel.from_pretrained("facebook/sam-vit-huge").to(self.device)
        self.processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")

    def get_features(self, content, params: SamConfig):
        input_boxes = []
        class_names = []

        for feature in content.features:
            feature_data = feature.model_dump()
            feature_data = json.loads(feature_data.get("value", {}))

            box = feature_data.get(params.boundingbox_key)
            if not box:
                print("no box found for feature", feature_data)
                continue

            input_boxes.append([box])
            class_names.append(feature_data.get(params.class_key, "unknown"))

        return input_boxes, class_names

    def mask_pixels_from_original_image(self, orig_img, mask_np) -> Image:
        """ 
        export cropped images with mask
        set everything transparent besides where mask is true
        """

        original_pixels = np.array(orig_img)
        output_pixels = np.zeros_like(original_pixels)
        output_pixels[mask_np] = original_pixels[mask_np] 
        output_pixels[~mask_np, 3] = (
            0  # set alpha to 0 (transparent) where mask is False
        )
        output_image = Image.fromarray(output_pixels, "RGBA")
        return output_image

    def extract(self, content: Content, params: SamConfig) -> List[Content]:
        # extract image embeddings
        raw_image = Image.open(BytesIO(content.data))
        inputs = self.processor(raw_image, return_tensors="pt").to(self.device)
        image_embeddings = self.model.get_image_embeddings(inputs["pixel_values"])

        # get boxes
        boxes, class_names = self.get_features(content, params)
        if not len(boxes):
            print("no bounding boxes found")
            return []
        
        # process boxes
        inputs = self.processor(raw_image, input_boxes=[boxes], return_tensors="pt").to(
            self.device
        )
        inputs.pop("pixel_values", None)
        inputs.update({"image_embeddings": image_embeddings})

        # get masks
        with torch.no_grad():
            outputs = self.model(**inputs)
        masks = self.processor.image_processor.post_process_masks(
            outputs.pred_masks.cpu(),
            inputs["original_sizes"].cpu(),
            inputs["reshaped_input_sizes"].cpu(),
        )
        scores = outputs.iou_scores

        # iterate masks and extract segments
        results = []
        for i, mask_set in enumerate(masks[0]):
            mask = mask_set[2]
            mask_boolean = mask.to(torch.bool)
            mask_np = mask_boolean.cpu().numpy()
            output_image = self.mask_pixels_from_original_image(
                raw_image.convert("RGBA"), mask_np
            )
            # crop to bounding box
            output_image = output_image.crop(boxes[i][0])

            # save to bytes
            output = BytesIO()
            output_image.save(output, format="PNG")
            output.seek(0)
            results.append(
                Content(
                    content_type="image/png",
                    data=output.read(),
                    features=[
                        Feature.metadata(
                            value={
                                "mask_score": scores[0][i][2].item(),
                                "class_name": class_names[i],
                            }
                        )
                    ],
                )
            )

        return results

    def sample_input(self) -> Content:
        f = open("sample.jpg", "rb")
        return Content(
            content_type="image/jpeg",
            data=f.read(),
            features=[
                Feature.metadata(
                    value={"boundingbox": [348, 117, 426, 339], "phrase": "person"}
                ),
                Feature.metadata(
                    value={"boundingbox": [69, 114, 137, 340], "phrase": "person"}
                ),
                Feature.metadata(
                    value={"boundingbox": [468, 130, 534, 339], "phrase": "person"}
                ),
                Feature.metadata(
                    value={"boundingbox": [301, 127, 354, 340], "phrase": "person"}
                ),
                Feature.metadata(
                    value={"boundingbox": [135, 120, 202, 347], "phrase": "person"}
                ),
                Feature.metadata(
                    value={"boundingbox": [261, 111, 310, 349], "phrase": "person"}
                ),
                Feature.metadata(
                    value={"boundingbox": [418, 124, 474, 336], "phrase": "person"}
                ),
                Feature.metadata(
                    value={"boundingbox": [209, 134, 254, 345], "phrase": "person"}
                ),
                Feature.metadata(
                    value={"boundingbox": [0, 110, 27, 337], "phrase": "person"}
                ),
                Feature.metadata(
                    value={"boundingbox": [28, 122, 89, 341], "phrase": "person"}
                ),
            ],
        )


if __name__ == "__main__":
    SamExtractor().extract_sample_input()

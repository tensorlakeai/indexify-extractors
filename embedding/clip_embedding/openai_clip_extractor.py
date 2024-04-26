from typing import List, Union
from indexify_extractor_sdk import Content, Extractor, Feature
import torch
import clip
from PIL import Image
from io import BytesIO


class ClipEmbeddingExtractor(Extractor):
    name = "tensorlake/clip-extractor"
    description = "OpenAI Clip Embedding Extractor"
    input_mime_types = ["image/jpeg", "image/png", "image/gif", "text/plain"]

    def __init__(self):
        super(ClipEmbeddingExtractor, self).__init__()
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model, self._preprocess = clip.load("ViT-B/32", device=self._device)

    def extract(self, content: Content, params = None) -> Union[List[Feature], List[Content]]:
        if "image" in content.content_type:
            img = Image.open(BytesIO(content.data))
            image = self._preprocess(img).unsqueeze(0).to(self._device)
            with torch.no_grad():
                image_features = self._model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            embedding = image_features.numpy()[0]
            return [Feature.embedding(values=embedding)]
        elif "text" in content.content_type:
            txt = content.data.decode("utf-8")
            text = clip.tokenize(txt).to(self._device)
            with torch.no_grad():
                text_features = self._model.encode_text(text)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            embedding = text_features.numpy()[0]
            return [Feature.embedding(values=embedding)]
        else:
            raise ValueError("Unsupported Content Type")

    def sample_input(self) -> Content:
        return self.sample_jpg()


if __name__ == "__main__":
    ClipEmbeddingExtractor().extract_sample_input()

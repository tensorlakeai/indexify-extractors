from typing import List, Union
from indexify_extractor_sdk import Content, Extractor, Feature
import clip
from PIL import Image
from io import BytesIO


class ClipEmbeddingExtractor(Extractor):
    name = "tensorlake/clip-extractor"
    description = "OpenAI Clip Embedding Extractor"
    input_mime_types = ["image/jpeg", "image/png", "image/gif", "text/plain"]

    def __init__(self):
        super(ClipEmbeddingExtractor, self).__init__()
        self._model, self._preprocess = clip.load("ViT-B/32", jit=True)

    def extract(self, content: Content, params = None) -> Union[List[Feature], List[Content]]:
        if "image" in content.content_type:
            img = Image.open(BytesIO(content.data))
            image = self._preprocess(img).unsqueeze(0)
            embedding = self._model.encode_image(image)
            embedding = embedding.tolist()[0]
            return [Feature.embedding(values=embedding)]
        elif "text" in content.content_type:
            text = content.data.decode("utf-8")
            embedding = self._model.encode_text(clip.tokenize(text))
            embedding = embedding.tolist()[0]
            return [Feature.embedding(values=embedding)]
        else:
            raise ValueError("Unsupported Content Type")

    def sample_input(self) -> Content:
        return self.sample_jpg()


if __name__ == "__main__":
    ClipEmbeddingExtractor().extract_sample_input()

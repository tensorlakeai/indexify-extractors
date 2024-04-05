from typing import List, Union
from pydantic import BaseModel
from indexify_extractor_sdk import Content, Extractor, Feature
import torch
import clip
from PIL import Image
from io import BytesIO
import base64
class ClipInputParams(BaseModel):
    model: str = "ViT-B/32"

class ClipEmbeddingExtractor(Extractor):
    name = "tensorlake/clip-extractor"
    description = "OpenAI Clip Embedding Extractor"
    input_mime_types = ["image/jpeg", "image/png", "image/gif", "text/plain"]

    def __init__(self):
        super(ClipEmbeddingExtractor, self).__init__()

    def extract(self, content: Content, params: ClipInputParams) -> Union[List[Feature], List[Content]]:
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model, self._preprocess = clip.load(params.model, device=self._device)

        if "image" in content.content_type:
            img = Image.open(BytesIO(content.data))
            image = self._preprocess(img).unsqueeze(0).to(self._device)
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
        img_data = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAABoVBMVEX////////////////////////////////////////////////////////////////////////////////////////x8fTKy9asr7+srr/Jy9Xw8fP5+vuusMBESW8SGUgECz0RGEhCSG2rrr75+fqKjaQQFkYDCjwoLllQVXhRVngqMFoECj0PFUWGiaKprL2AhJ3h4uj6+vvi4+mEh6ANFESlqLru7vI+Q2r7+/z8/PyIjKMFDD46P2fr7PDAwc4KEEIsMlzk5ern6O0wNl8IDkC7vcvP0Nl3epWipbf8/P3+/v78/f79/f2lp7l2epXMzdf0+f73+/7t9v2t1vqDwPeCwPes1fns9f34/P7z+f7S6PyNxvjD4fu63PpyuPZLpPRfrvVwt/a52/rE4fuOxvjP5/xrtfZKpPRdrfWw1/pervVps/Xr9f3b7fy32/q+3vve7v3U6fyx1/rT6fzf7v2/3vu32vra7Pzk8f2WyvhTqPRMpfRSqPSUyfji8P39/v693vtmsvWEwffJ5PvK5PuGwvdlsfW73Pr1+v72+v5uxreCAAAAFXRSTlMEXNT8/dpnB+vwbNPj+9no9Xjk6gsU/ejiAAAAAWJLR0QAiAUdSAAAAAd0SU1FB+gBDxIRFutv6/YAAAD2SURBVBjTY2BgZGIWhQIWVjZ2BkYOIEtMXEJSShrI4ORi4BYVlZGVk1dQUFRSVhEV5WHgFZVRVVPX0NTS1tHVA4owiIrq66oZGBoZGZsompqBBMwtFEwsQUZaWdvY2gEF7B0cnSCWOLu4ugEF3D08vUS9fXy8RX39/AOAAoFBoqLBIaFh4RGiopFRQIHomNi4+ITExISk5JTUNKBAcHpGQmZIcHBWdkJGTi5QwDsvv6CwqDirpLSsvMJblAHoEe/Kquqamtq6em+gVQx8oqINjU3NLa1t7R0+oqL8DGycQJHgTlHRrogGUVEBQQZ2LiFROBAWFAEAaAo1WMyTNbMAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjQtMDEtMTVUMTg6MTc6MjIrMDA6MDBLxIMJAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDI0LTAxLTE1VDE4OjE3OjIyKzAwOjAwOpk7tQAAAFd6VFh0UmF3IHByb2ZpbGUgdHlwZSBpcHRjAAB4nOPyDAhxVigoyk/LzEnlUgADIwsuYwsTIxNLkxQDEyBEgDTDZAMjs1Qgy9jUyMTMxBzEB8uASKBKLgDqFxF08kI1lQAAAABJRU5ErkJggg=="
        return Content(content_type="image/png", data=base64.b64decode(img_data))


if __name__ == "__main__":
    ClipEmbeddingExtractor().extract_sample_input()

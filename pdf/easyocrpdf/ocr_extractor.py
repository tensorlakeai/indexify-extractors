from typing import List, Union
import io
from indexify_extractor_sdk import Content, Extractor, Feature
from .utils.ocr_module import get_text
import fitz
import tempfile

class OCRExtractor(Extractor):
    name = "tensorlake/easyocr"
    description = "PDF Extractor using EasyOCR on GPU"
    system_dependencies = ["poppler-utils"]
    input_mime_types = ["application/pdf", "image/jpeg", "image/png"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params = None) -> List[Union[Feature, Content]]:
        contents = []

        suffix = f'.{content.content_type.split("/")[-1]}'
        if not suffix.endswith(".pdf"):
            image_text = get_text(content.data)
            contents.append(Content.from_text(image_text))
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
                inputtmpfile.write(content.data)
                inputtmpfile.flush()

                doc = fitz.open(inputtmpfile.name)
                for i in range(len(doc)):
                    page = doc[i]
                    page_text = page.get_text()
                    image_list = page.get_images()
                    feature = Feature.metadata(value={"page": i+1}, name="text")
                    if page_text:
                        contents.append(Content.from_text(page_text, features=[feature]))

                    for img in image_list:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        image_text = get_text(pix.tobytes())
                        contents.append(Content.from_text(image_text, features=[feature]))
        
        return contents

    def sample_input(self) -> Content:
        f = open("sample.pdf", "rb")
        return Content(content_type="application/pdf", data=f.read())

if __name__ == "__main__":
    f = open("sample.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    extractor = OCRExtractor()
    results = extractor.extract(pdf_data)
    print(results)
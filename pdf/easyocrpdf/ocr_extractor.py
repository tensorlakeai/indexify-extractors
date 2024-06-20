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
        full_text = ""

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

                    if page_text:
                        full_text += page_text + " "

                    for img in image_list:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        image_text = get_text(pix.tobytes())
                        full_text += image_text + " "
                
                feature = Feature.metadata(value={"type": "text"})
                contents.append(Content.from_text(full_text, features=[feature]))
        
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

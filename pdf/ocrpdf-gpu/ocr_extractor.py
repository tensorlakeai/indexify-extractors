from typing import List, Union
import io
from indexify_extractor_sdk import Content, Extractor, Feature
from utils.ocr_module import get_text
from pypdf import PdfReader

class OCRExtractor(Extractor):
    name = "tensorlake/ocrpdf-gpu"
    description = "PDF Extractor using EasyOCR on GPU"
    system_dependencies = ["poppler-utils"]
    input_mime_types = ["application/pdf"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params = None) -> List[Union[Feature, Content]]:
        contents = []

        reader = PdfReader(io.BytesIO(content.data))
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            page_text = page.extract_text()
            feature = Feature.metadata(value={"page": i+1}, name="text")
            if page_text:
                contents.append(Content.from_text(page_text, features=[feature]))

            for img in page.images:
                image_text = get_text(img.data)
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
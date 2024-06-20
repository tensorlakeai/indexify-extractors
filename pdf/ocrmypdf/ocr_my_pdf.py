from typing import List, Iterable, Optional
from pydantic import BaseModel
from indexify_extractor_sdk import Extractor, Content, Feature
import tempfile
import ocrmypdf
import fitz


class OCRMyPDFConfig(BaseModel):
    deskew: Optional[bool] = None
    language: Optional[Iterable[str]] = None
    remove_background: Optional[bool] = None
    rotate_pages: Optional[bool] = None


class OCRMyPDFExtractor(Extractor):
    name = "tensorlake/ocrmypdf"
    description = "This extractor uses ocrmypdf to generate searchable PDF/A content from a regular PDF and then extract the text into plain text content."
    input_mime_types = ["application/pdf"]
    # language packs can be added to system dependencies
    system_dependencies = ["ghostscript", "tesseract-ocr", "tesseract-ocr-spa", "tesseract-ocr-chi-sim", "tesseract-ocr-fra", "tesseract-ocr-deu"]

    def __init__(self):
        super(OCRMyPDFExtractor, self).__init__()

    def extract(self, content: Content, params: OCRMyPDFConfig) -> List[Content]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as outtmpfile:
                ocrmypdf.ocr(inputtmpfile.name, outtmpfile.name, **dict(params))

                contents = []
                full_text = ""

                # extract text from each page
                doc = fitz.open(outtmpfile.name)
                for i, page in enumerate(doc):
                    full_text += page.get_text() + " "
                
                feature = Feature.metadata(value={"type": "text"})
                contents.append(Content.from_text(full_text, features=[feature]))

                return contents

    def sample_input(self) -> Content:
        return self.sample_image_based_pdf()


if __name__ == "__main__":
    f = open("sample.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    input_params = OCRMyPDFConfig()
    extractor = OCRMyPDFExtractor()
    results = extractor.extract(pdf_data, params=input_params)
    print(results)
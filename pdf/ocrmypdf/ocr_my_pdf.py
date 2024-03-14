from typing import List, Iterable, Optional
from pydantic import BaseModel
from indexify_extractor_sdk import Extractor, Content, Feature
import tempfile
import ocrmypdf
from pypdf import PdfReader


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
    system_dependencies = ["tesseract-ocr", "tesseract-ocr-spa", "tesseract-ocr-chi-sim", "tesseract-ocr-fra", "tesseract-ocr-deu"]

    def __init__(self):
        super(OCRMyPDFExtractor, self).__init__()

    def extract(self, content: Content, params: OCRMyPDFConfig) -> List[Content]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as outtmpfile:
                ocrmypdf.ocr(inputtmpfile.name, outtmpfile.name, **dict(params))

                new_content = []
                # extract text from each page
                reader = PdfReader(outtmpfile.name)
                for i, page in enumerate(reader.pages):
                    new_content.append(
                        Content(
                            content_type="text/plain",
                            data=bytes(page.extract_text(), "utf-8"),
                            features=[Feature.metadata(value={"page": i})],
                        )
                    )

                return new_content

    def sample_input(self) -> Content:
        f = open("image-based.pdf", "rb")
        return Content(content_type="application/pdf", data=f.read())


if __name__ == "__main__":
    OCRMyPDFExtractor().extract_sample_input()

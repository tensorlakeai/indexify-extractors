from typing import List, Union, Optional
import json
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
from .utils.tt_module import get_tables
import fitz
import pymupdf4llm
import tempfile

class PDFExtractorConfig(BaseModel):
    output_types: List[str] = Field(default_factory=lambda: ["text"])

class PDFExtractor(Extractor):
    name = "tensorlake/pdfextractor"
    description = "PDF Extractor for Texts, Images & Tables"
    system_dependencies = ["poppler-utils"]
    input_mime_types = ["application/pdf"]

    def __init__(self):
        super(PDFExtractor, self).__init__()

    def extract(self, content: Content, params: PDFExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            if "text" in params.output_types:
                md_text = pymupdf4llm.to_markdown(inputtmpfile.name)
                feature = Feature.metadata(value={"type": "text"})
                contents.append(Content.from_text(md_text, features=[feature]))

            if "image" in params.output_types:
                doc = fitz.open(inputtmpfile.name)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    for img_index, img in enumerate(page.get_images(full=True)):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        feature = Feature.metadata({"type": "image", "page": float(f"{page_num+1}.{img_index+1}")})
                        contents.append(Content(content_type="image/png", data=image_bytes, features=[feature]))

            if "table" in params.output_types:
                tables = get_tables(content.data)
                for page_index, content in tables.items():
                    feature = Feature.metadata({"type": "table", "page": float(page_index)})
                    contents.append(Content(content_type="application/json", data=json.dumps(content), features=[feature]))

        return contents

    def sample_input(self) -> Content:
        return self.sample_scientific_pdf()

if __name__ == "__main__":
    f = open("2310.16944.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    extractor = PDFExtractor()
    params = PDFExtractorConfig(output_types=["text", "table"])
    results = extractor.extract(pdf_data, params)
    print(results)

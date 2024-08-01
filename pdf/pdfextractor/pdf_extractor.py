from typing import List, Union, Optional, Literal
import json
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
from .utils.tt_module import get_tables
import pymupdf
import fitz
import pymupdf4llm
import tempfile

class PDFExtractorConfig(BaseModel):
    output_types: List[str] = Field(default_factory=lambda: ["text"])
    output_format: Literal['markdown', 'text'] = "markdown"

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
                if params.output_format == "markdown":
                    md_text = pymupdf4llm.to_markdown(inputtmpfile.name)
                    contents.append(Content.from_text(md_text))
                else:
                    with pymupdf.open(inputtmpfile.name) as doc:
                        for page_num, page in enumerate(doc):
                            text = page.get_text()
                            contents.append(Content.from_text(text, features=[Feature.metadata({"page_num": page_num})]))

            if "image" in params.output_types:
                doc = fitz.open(inputtmpfile.name)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    for img_index, img in enumerate(page.get_images(full=True)):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        feature = Feature.metadata({"page": page_num, "img_num": img_index})
                        contents.append(Content(content_type="image/png", data=image_bytes, features=[feature]))

            if "table" in params.output_types:
                tables = get_tables(content.data)
                for page_index, content in tables.items():
                    feature = Feature.metadata({"page": page_index})
                    contents.append(Content(content_type="application/json", data=json.dumps(content), features=[feature]))

        return contents

    def sample_input(self) -> Content:
        config = PDFExtractorConfig()
        return (self.sample_scientific_pdf(), config.model_dump_json())

if __name__ == "__main__":
    f = open("2310.16944.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    extractor = PDFExtractor()
    params = PDFExtractorConfig(output_types=["text", "table"])
    results = extractor.extract(pdf_data, params)
    print(results)

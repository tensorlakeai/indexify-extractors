from typing import List, Union
import json
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
import tempfile
from paddleocr import PaddleOCR
from pdf2image import convert_from_path

class PaddleOCRExtractorConfig(BaseModel):
    output_types: List[str] = Field(default_factory=lambda: ["text"])

class PaddleOCRExtractor(Extractor):
    name = "tensorlake/paddleocr_extractor"
    description = "PDF Extractor for Texts using PaddleOCR"
    system_dependencies = ["poppler-utils", "tesseract-ocr"]
    input_mime_types = ["application/pdf"]

    def __init__(self):
        super(PaddleOCRExtractor, self).__init__()
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')

    def extract(self, content: Content, params: PaddleOCRExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            if "text" in params.output_types:
                # Convert PDF to images
                images = convert_from_path(inputtmpfile.name, dpi=200)  # Adjust DPI as needed

                all_texts = []
                for image in images:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_file:
                        image.save(img_file.name, 'PNG')
                        result = self.ocr.ocr(img_file.name, cls=True)
                        for res in result:
                            texts = [line[1][0] for line in res]
                            all_texts.extend(texts)

                md_text = "\n".join(all_texts)
                feature = Feature.metadata(value={"type": "text"})
                contents.append(Content.from_text(md_text, features=[feature]))

        return contents

    def sample_input(self) -> Content:
        return self.sample_scientific_pdf()

if __name__ == "__main__":
    f = open("W2_Summary.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    extractor = PaddleOCRExtractor()
    params = PaddleOCRExtractorConfig(output_types=["text"])
    results = extractor.extract(pdf_data, params)
    print(results)

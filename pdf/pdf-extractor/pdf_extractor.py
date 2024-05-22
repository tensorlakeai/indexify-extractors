from typing import List, Union
import json
from indexify_extractor_sdk import Content, Extractor, Feature
from .utils.tt_module import get_tables
import fitz
import tempfile

class PDFExtractor(Extractor):
    name = "tensorlake/pdf-extractor"
    description = "PDF Extractor for Texts, Images & Tables"
    system_dependencies = ["poppler-utils"]
    input_mime_types = ["application/pdf"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params = None) -> List[Union[Feature, Content]]:
        contents = []
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            doc = fitz.open(inputtmpfile.name)
            for i in range(len(doc)):
                page = doc[i]
                page_text = page.get_text()
                image_list = page.get_images()
                feature = Feature.metadata(value={"type": "text", "page": i+1})
                contents.append(Content.from_text(page_text, features=[feature]))

                for img in image_list:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    if not pix.colorspace.name in (fitz.csGRAY.name, fitz.csRGB.name):
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    feature = Feature.metadata({"type": "image", "page": i+1})
                    contents.append(Content(content_type="image/png", data=pix.tobytes(), features=[feature]))

        tables = get_tables(content.data)

        for page, content in tables.items():
            feature = Feature.metadata({"type": "table", "page": int(page)})
            contents.append(Content(content_type="application/json", data=json.dumps(content), features=[feature]))
        
        return contents

    def sample_input(self) -> Content:
        return self.sample_scientific_pdf()

if __name__ == "__main__":
    f = open("2310.16944.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    extractor = PDFExtractor()
    results = extractor.extract(pdf_data)
    print(results)
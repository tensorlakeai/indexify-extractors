from typing import List, Union
import io
from marker.convert import convert_single_pdf
from marker.models import load_all_models
import tempfile
from indexify_extractor_sdk import Content, Extractor, Feature

class MarkdownExtractor(Extractor):
    name = "tensorlake/markdown-extractor"
    description = "Markdown Extractor for PDFs"
    system_dependencies = []
    input_mime_types = ["application/pdf"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params = None) -> List[Union[Feature, Content]]:
        contents = []
        model_lst = load_all_models()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            full_text, out_meta = convert_single_pdf(inputtmpfile.name, model_lst, max_pages=None, parallel_factor=1)
            
            feature = Feature.metadata(value=out_meta, name="text")
            contents.append(Content.from_text(full_text, features=[feature]))

        return contents

    def sample_input(self) -> Content:
        return self.sample_scientific_pdf()

if __name__ == "__main__":
    f = open("test.pdf", "rb")
    pdf_data = Content(content_type="application/pdf", data=f.read())
    extractor = MarkdownExtractor()
    results = extractor.extract(pdf_data)
    print(results)
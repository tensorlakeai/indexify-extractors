from marker.convert import convert_single_pdf
from marker.models import load_all_models
import tempfile
from indexify_extractor_sdk import Content, Extractor, Feature

from pydantic import BaseModel
from typing import Optional, Literal, List, Union

class MarkdownExtractorConfig(BaseModel):
    max_pages: Optional[int] = None
    langs: Optional[str] = None
    batch_multiplier: Optional[int] = 2

class MarkdownExtractor(Extractor):
    name = "tensorlake/markdown-extractor"
    description = "Markdown Extractor for PDFs"
    system_dependencies = []
    input_mime_types = ["application/pdf"]

    def __init__(self):
        super(MarkdownExtractor, self).__init__()
        self.model_lst = load_all_models()

    def extract(self, content: Content, params: MarkdownExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            full_text, images, out_meta = convert_single_pdf(inputtmpfile.name, self.model_lst, max_pages=params.max_pages, langs=params.langs, batch_multiplier=params.batch_multiplier)
            
            feature = Feature.metadata(value=out_meta, name="text")
            contents.append(Content.from_text(full_text, features=[feature]))

        return contents

    def sample_input(self) -> Content:
        return self.sample_scientific_pdf()

if __name__ == "__main__":
    filepath = "sample.pdf"
    with open(filepath, 'rb') as f:
        pdf_data = f.read()
    data = Content(content_type="application/pdf", data=pdf_data)
    params = MarkdownExtractorConfig(batch_multiplier=2)
    extractor = MarkdownExtractor()
    results = extractor.extract(data, params=params)
    print(results)
from marker.convert import convert_single_pdf
from marker.models import load_all_models
import tempfile
from indexify_extractor_sdk import Content, Extractor, Feature

from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Union

class MarkdownExtractorConfig(BaseModel):
    max_pages: Optional[int] = None
    start_page: Optional[int] = None
    langs: Optional[str] = None
    batch_multiplier: Optional[int] = 2
    output_types: List[str] = Field(default_factory=lambda: ["text"])

class MarkdownExtractor(Extractor):
    name = "tensorlake/marker"
    description = "Markdown Extractor for PDFs"
    system_dependencies = ["ffmpeg", "libsm6", "libxext6"]
    input_mime_types = ["application/pdf"]

    def __init__(self):
        super(MarkdownExtractor, self).__init__()
        self.model_lst = load_all_models()

    def extract(self, content: Content, params: MarkdownExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            langs = params.langs.split(",") if params.langs else None

            full_text, images, out_meta = convert_single_pdf(inputtmpfile.name, self.model_lst, max_pages=params.max_pages, langs=langs, batch_multiplier=params.batch_multiplier, start_page=params.start_page)
            
            if "text" in params.output_types:
                feature = Feature.metadata(value=out_meta)
                contents.append(Content.from_text(full_text, features=[feature]))

            if "image" in params.output_types:
                for filename, image in images.items():
                    feature = Feature.metadata({"type": "image", "file": filename})
                    contents.append(Content(content_type="image/png", data=image, features=[feature]))

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

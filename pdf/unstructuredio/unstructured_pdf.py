from unstructured.partition.pdf import partition_pdf
import tempfile
from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field

class UnstructuredIOConfig(BaseModel):
    strategy: Optional[str] = Field(default="auto") # "auto", "hi_res", "ocr_only", and "fast"
    hi_res_model_name: Optional[str] = Field(default="yolox")
    infer_table_structure: Optional[bool] = True

class UnstructuredIOExtractor(Extractor):
    name = "tensorlake/unstructuredio"
    description = "This extractor uses unstructured.io to extract pieces of pdf document into separate plain text content data."
    system_dependencies = ["libmagic-dev", "poppler-utils", "tesseract-ocr"]
    input_mime_types = ["application/pdf"]

    def __init__(self):
        super(UnstructuredIOExtractor, self).__init__()

    def extract(self, content: Content, params: UnstructuredIOConfig) -> List[Union[Feature, Content]]:
        contents = []
        strategy = params.strategy
        hi_res_model_name = params.hi_res_model_name
        infer_table_structure = params.infer_table_structure
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()

            elements = partition_pdf(inputtmpfile.name, strategy=strategy, hi_res_model_name=hi_res_model_name, infer_table_structure=infer_table_structure)
            for el in elements:
                feature = Feature.metadata(value={"type": type(el).__name__, "page_number": el.metadata.page_number})
                contents.append(Content.from_text(el.text, features=[feature]))

        return contents

    def sample_input(self) -> Content:
        return self.sample_scientific_pdf()

if __name__ == "__main__":
    filepath = "sample.pdf"
    with open(filepath, 'rb') as f:
        pdf_data = f.read()
    data = Content(content_type="application/pdf", data=pdf_data)
    params = UnstructuredIOConfig(strategy="hi_res")
    extractor = UnstructuredIOExtractor()
    results = extractor.extract(data, params=params)
    print(results)
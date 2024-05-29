from typing import List, Union, Optional
from pydantic import BaseModel, Field
from indexify_extractor_sdk import Content, Extractor, Feature
from pptx import Presentation
import requests
import tempfile

class PPTExtractorConfig(BaseModel):
    output_types: List[str] = Field(default_factory=lambda: ["text", "table"])

class PPTExtractor(Extractor):
    name = "tensorlake/ppt"
    description = "An extractor that let's you extract information from presentations."
    system_dependencies = []
    input_mime_types = ["application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation"]

    def __init__(self):
        super(PPTExtractor, self).__init__()

    def extract(self, content: Content, params: PPTExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()
            prs = Presentation(inputtmpfile.name)

            for slide in prs.slides:
                for shape in slide.shapes:
                    if "text" in params.output_types:
                        if shape.has_text_frame:
                            feature = Feature.metadata(value={"type": "text"})
                            contents.append(Content.from_text(shape.text_frame.text, features=[feature]))
                    if "table" in params.output_types:
                        if shape.shape_type == 19:
                            tb = shape.table
                            rows = []
                            for i in range(1, len(tb.rows)):
                                rows.append("; ".join([tb.cell(0, j).text + ": " + tb.cell(i, j).text for j in range(len(tb.columns)) if tb.cell(i, j)]))
                            stacked_rows = "\n".join(rows)
                            feature = Feature.metadata({"type": "table"})
                            contents.append(Content.from_text(stacked_rows, features=[feature]))
                    if "image" in params.output_types:
                        if shape.shape_type == 13:
                            feature = Feature.metadata({"type": "image"})
                            contents.append(Content(content_type="image/png", data=shape.image.blob, features=[feature]))
            
        return contents

    def sample_input(self) -> Content:
        req = requests.get("https://raw.githubusercontent.com/tensorlakeai/indexify/main/docs/docs/files/test.pptx")
        with open('test.pptx','wb') as f:
            f.write(req.content)
        with open('test.pptx','rb') as f:
            ppt_data = f.read()
        return Content(content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", data=ppt_data)

if __name__ == "__main__":
    filepath = "test.pptx"
    with open(filepath, 'rb') as f:
        ppt_data = f.read()
    data = Content(content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", data=ppt_data)
    extractor = PPTExtractor()
    params = PPTExtractorConfig(output_types=["text", "table"])
    results = extractor.extract(data, params)
    print(results)
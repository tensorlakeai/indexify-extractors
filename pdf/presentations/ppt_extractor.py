from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pptx import Presentation
import tempfile

class PPTExtractor(Extractor):
    name = "tensorlake/ppt"
    description = "An extractor that let's you extract information from presentations."
    system_dependencies = []
    input_mime_types = ["application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation"]

    def __init__(self):
        super(PPTExtractor, self).__init__()

    def extract(self, content: Content, params = None) -> List[Union[Feature, Content]]:
        contents = []
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as inputtmpfile:
            inputtmpfile.write(content.data)
            inputtmpfile.flush()
            prs = Presentation(inputtmpfile.name)

            for slide in prs.slides:
                for shape in slide.shapes:
                    if not shape.has_text_frame:
                        continue
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            contents.append(Content.from_text(run.text))
            
        return contents

    def sample_input(self) -> Content:
        return self.sample_presentation()

if __name__ == "__main__":
    filepath = "test.pptx"
    with open(filepath, 'rb') as f:
        ppt_data = f.read()
    data = Content(content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", data=ppt_data)
    extractor = PPTExtractor()
    results = extractor.extract(data)
    print(results)
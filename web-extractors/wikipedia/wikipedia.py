import json

from utils.utils import extract_images, extract_infobox, extract_sections

from typing import List
from indexify_extractor_sdk.base_extractor import Content, Extractor, Feature
from pydantic import BaseModel


class InputParams(BaseModel):
    ...


class WikipediaExtractor(Extractor):
    name = "mohitraghavendra/wikipedia-extractor"
    description = "Extract text content from wikipedia html pages"
    input_mime_types = ["text/html", "text/plain"]
    python_dependencies = ["beautifulsoup4"]
    system_dependencies = []

    def __init__(self):
        super(WikipediaExtractor, self).__init__()

    def extract(self, content: Content, params: InputParams) -> List[Content]:

        contents = []

        infobox_dict = extract_infobox(content)

        if infobox_dict:
            feature = Feature.metadata(json.dumps(infobox_dict), name="infobox")

            infobox_content = Content.from_text(
                text="", feature=feature, labels=content.labels
            )
            contents.append(infobox_content)

        sections = extract_sections(content)
        images = extract_images(content)

        contents.extend(sections)
        contents.extend(images)

        return contents

    def sample_input(self) -> Content:
        import os

        dirname = os.path.dirname(__file__)
        file_name = os.path.join(dirname, "utils/Stephen_Curry.html")
        with open(file_name, "rb") as f:
            data = f.read()

        return Content(
            data=data, content_type="text/html", labels={"filename": file_name}
        )

    def run_sample_input(self) -> List[Content]:
        return self.extract(self.sample_input(), InputParams())


if __name__ == "__main__":
    WikipediaExtractor().run_sample_input()

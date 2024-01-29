import json

from utils.utils import extract_images, extract_infobox, extract_sections, extract_title

from typing import List
from indexify_extractor_sdk.base_extractor import Content, Extractor, Feature
from pydantic import BaseModel


class InputParams(BaseModel):
    ...


class WikipediaExtractor(Extractor):
    name = "tensorlake/wikipedia"
    description = "Extract text content from wikipedia html pages"
    input_mime_types = ["text/html", "text/plain"]
    python_dependencies = ["beautifulsoup4"]
    system_dependencies = []

    def __init__(self):
        super(WikipediaExtractor, self).__init__()

    def extract(self, content: Content, params: InputParams) -> List[Content]:

        contents: List[Content] = []
        title = extract_title(content)
        infobox_dict = extract_infobox(content)
        doc_features = json.loads(content.feature.value) if content.feature else {}

        if infobox_dict:
            feature = Feature.metadata(infobox_dict, name="infobox")

            infobox_content = Content.from_text(
                text="", feature=feature, labels=content.labels
            )
            contents.append(infobox_content)

        sections = extract_sections(content)
        images = extract_images(content)

        contents.extend(sections)
        contents.extend(images)

        for content_piece in contents:
            feature = (
                json.loads(content_piece.feature.value) if content_piece.feature else {}
            )
            feature["title"] = title
            feature = {**feature, **doc_features}
            content_piece.feature = Feature.metadata(feature)
        return contents

    def sample_input(self) -> Content:
        import os

        dirname = os.path.dirname(__file__)
        file_name = "Stephen_Curry.html"
        file_path = os.path.join(dirname, "utils/", file_name)

        with open(file_path, "rb") as f:
            data = f.read()

        return Content(
            data=data,
            content_type="text/html",
            feature=Feature.metadata({"filename": file_name}),
        )

    def run_sample_input(self) -> List[Content]:
        return self.extract(self.sample_input(), InputParams())


if __name__ == "__main__":
    WikipediaExtractor().run_sample_input()

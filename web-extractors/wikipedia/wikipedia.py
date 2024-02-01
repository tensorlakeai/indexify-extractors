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

        if infobox_dict:
            feature = Feature.metadata(infobox_dict, name="infobox")

            infobox_content = Content.from_text(
                text="", features=[feature], labels=content.labels
            )
            contents.append(infobox_content)

        sections = extract_sections(content)
        images = extract_images(content)

        contents.extend(sections)
        contents.extend(images)

        for content_piece in contents:
            for (i, feature) in enumerate(content_piece.features):
                feature = (
                    json.loads(feature.value) if feature else {}
                )
                feature["title"] = title
                content_piece.features[i] = Feature.metadata(feature)
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

if __name__ == "__main__":
    contents = WikipediaExtractor().extract_sample_input()
    print(len(contents))

import os
import sys

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)

if current_directory not in sys.path:
    sys.path.append(current_directory)

from utils.utils import extract_images, extract_infobox, extract_sections, extract_title
from typing import List, Union
from indexify_extractor_sdk.base_extractor import Content, Extractor, Feature


class WikipediaExtractor(Extractor):
    name = "tensorlake/wikipedia"
    description = "Extract text content from wikipedia html pages"
    input_mime_types = ["text/html", "text/plain"]
    system_dependencies = []

    def __init__(self):
        super(WikipediaExtractor, self).__init__()

    def extract(self, content: Content, params=None) -> List[Union[Feature, Content]]:
        output = []

        # add metadata if infobox found
        infobox_dict = extract_infobox(content)
        if infobox_dict:
            infobox_feature = Feature.metadata(infobox_dict, name="infobox")
            output.append(infobox_feature)

        title = extract_title(content)
        sections = extract_sections(content)
        images = extract_images(content)

        new_content: List[Content] = []
        new_content.extend(sections)
        new_content.extend(images)

        # update new content feature with title
        for content_piece in new_content:
            for i, feature in enumerate(content_piece.features):
                feature = feature.value if feature else {}
                feature["title"] = title
                content_piece.features[i] = Feature.metadata(feature)

        # add new content to output
        output.extend(new_content)
        return output

    def sample_input(self) -> Content:
        return self.sample_html()


if __name__ == "__main__":
    contents = WikipediaExtractor().extract_sample_input()
    print(len(contents))
    for content in contents:
        print(len(content.features))
        for feature in content.features:
            print(feature.value)

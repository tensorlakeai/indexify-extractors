import json

from bs4 import BeautifulSoup
from typing import List
from indexify_extractor_sdk.base_extractor import Content, Extractor, Feature
from pydantic import BaseModel


HTML_PARSER = "html.parser"
WIKIPEDIA_CONTENT_DIV_ID = "mw-content-text"
HEADLINE_TAG = "h2"
TEXT_TAG = "p"


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

    def extract_infobox(self, content: str) -> dict:
        soup = BeautifulSoup(content.data, HTML_PARSER)
        infobox = soup.find("table", {"class": "infobox vcard"})
        if not infobox:
            return {}

        infobox_dict = {}
        rows = infobox.find_all("tr")
        for row in rows:
            header = row.find("th")
            if not header:
                continue

            key = header.text.strip()
            value = row.find("td")
            if not value:
                continue

            value = value.text.strip()
            infobox_dict[key] = value

        return infobox_dict

    def extract_sections(self, content: str) -> list[Content]:
        sections = []
        soup = BeautifulSoup(content.data, HTML_PARSER)
        page_content = soup.find("div", {"id": WIKIPEDIA_CONTENT_DIV_ID})

        if not page_content:
            return sections

        doc_labels = content.labels if content.labels else {}
        headlines = page_content.find_all(HEADLINE_TAG)
        if headlines:
            for headline in headlines:
                p_tags = headline.find_all_next(TEXT_TAG)
                associated_content = [p_tag.text for p_tag in p_tags]
                content_text = " ".join(associated_content)
                doc_labels["headline"] = headline.text
                sections.append(Content.from_text(content_text, labels=doc_labels))

        return sections

    def extract(self, content: Content, params: InputParams) -> List[Content]:

        contents = []

        infobox_dict = self.extract_infobox(content)

        if infobox_dict:
            feature = Feature.metadata(json.dumps(infobox_dict), name="infobox")

            infobox_content = Content.from_text(
                text="", feature=feature, labels=content.labels
            )
            contents.append(infobox_content)

        sections = self.extract_sections(content)
        contents.extend(sections)

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

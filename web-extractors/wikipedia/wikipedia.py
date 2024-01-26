from bs4 import BeautifulSoup
from pathlib import Path
from typing import List
from indexify_extractor_sdk.base_extractor import Content, Extractor
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
    python_dependencies = ["beautifulsoup4"]
    system_dependencies = []

    def __init__(self):
        super(WikipediaExtractor, self).__init__()

    def extract(self, content: Content, params: InputParams) -> List[Content]:
        soup = BeautifulSoup(content.data, HTML_PARSER)
        page_content = soup.find("div", {"id": WIKIPEDIA_CONTENT_DIV_ID})

        if not page_content:
            return []

        doc_labels = content.labels if content.labels else {}
        sections = []
        headlines = page_content.find_all(HEADLINE_TAG)
        if headlines:
            for headline in headlines:
                p_tags = headline.find_all_next(TEXT_TAG)
                associated_content = [p_tag.text for p_tag in p_tags]
                content_text = " ".join(associated_content)
                doc_labels["headline"] = headline.text
                sections.append(Content.from_text(content_text, labels=doc_labels))

        return sections

    def sample_input(self) -> Content:
        import os
        dirname = os.path.dirname(__file__)
        file_name = os.path.join(dirname, "utils/Stephen_Curry.html")
        with open(file_name, "rb") as f:
            data = f.read()

        return Content(data=data, content_type="text/html", labels={"filename": file_name})


if __name__ == "__main__":
    WikipediaExtractor().extract_sample_input()

from bs4 import BeautifulSoup
from pathlib import Path
from typing import List

from pydantic import BaseModel

from indexify_extractor_sdk import (
    Content,
    Extractor,
    ExtractorSchema,
)


HTML_PARSER = "html.parser"
WIKIPEDIA_CONTENT_DIV_ID = "mw-content-text"
HEADLINE_TAG = "h2"
TEXT_TAG = "p"


class InputParams(BaseModel):
    ...


class WikipediaExtractor(Extractor):
    def __init__(self):
        super(WikipediaExtractor, self).__init__()

    def extract(self, html_content: List[Content]) -> List[List[Content]]:

        data = []
        for doc in html_content:
            soup = BeautifulSoup(doc.data, HTML_PARSER)
            page_content = soup.find("div", {"id": WIKIPEDIA_CONTENT_DIV_ID})
            doc_labels = doc.labels
            if page_content:
                headlines = page_content.find_all(HEADLINE_TAG)
                if headlines:
                    for headline in headlines:
                        p_tags = headline.find_all_next(TEXT_TAG)
                        associated_content = [p_tag.text for p_tag in p_tags]
                        content_check = " ".join(associated_content)
                        if doc_labels:
                            doc_labels["headline"] = headline.text
                        data.append(Content.from_text(content_check, labels=doc_labels))

                else:
                    data.append([])

        return data

    @classmethod
    def schemas(cls) -> ExtractorSchema:
        ...


if __name__ == "__main__":
    from utils.utils import parse_html_files, save_html_pages

    path = str(Path(__file__).parent) + "/utils/html_pages"

    urls = [
        "https://en.wikipedia.org/wiki/Stephen_Curry",
        "https://en.wikipedia.org/wiki/Draymond_Green",
        "https://en.wikipedia.org/wiki/Klay_Thompson",
        "https://en.wikipedia.org/wiki/Andre_Iguodala",
        "https://en.wikipedia.org/wiki/Andrew_Wiggins",
    ]

    save_html_pages(urls, path)
    html_files = parse_html_files(path)

    extractor = WikipediaExtractor()
    result = extractor.extract(html_files)
    print(result)
    print(extractor.schemas())

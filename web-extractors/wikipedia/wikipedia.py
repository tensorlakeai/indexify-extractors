from bs4 import BeautifulSoup
from pathlib import Path
from typing import List

from pydantic import BaseModel

from indexify_extractor_sdk import (
    Content,
    Extractor,
    ExtractorSchema,
)

class InputParams(BaseModel):
    ...


class WikipediaExtractor(Extractor):
    def __init__(self):
        super(WikipediaExtractor, self).__init__()

    def extract(self, html_content: List[Content], params: InputParams) -> List[List[Content]]:

        data = []
        for doc in html_content:
            soup = BeautifulSoup(doc.data, "html.parser")
            page_content = soup.find("div", {"id": "mw-content-text"})
            if page_content:
                paragraphs = page_content.find_all("p")
                data.append(
                    [
                        Content.from_text(paragraph.text, feature=doc.feature)
                        for paragraph in paragraphs
                    ]
                )
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

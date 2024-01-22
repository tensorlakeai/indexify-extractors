import json
import os

from typing import List

from urllib.request import urlopen

from indexify_extractor_sdk import Content, Feature


def save_html_pages(urls, path):
    if not os.path.exists(path):
        os.mkdir(path)

    for url in urls:
        response = urlopen(url)

        with open(f"{path}/{url.split('/')[-1]}.html", "wb") as f:
            f.write(response.read())


def parse_html_files(path: str) -> List[Content]:

    html_content = []
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if file_path.endswith(".html"):
            url_metadata = json.dumps({"url": filename})
            with open(file_path, "r") as f:
                document = Content.from_text(
                    text=f.read(),
                    feature=Feature.metadata(value=url_metadata, name="url"),
                )
                html_content.append(document)

    return html_content

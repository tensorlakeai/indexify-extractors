import aiohttp
import asyncio
import json
import os
import re

from typing import List

from urllib.request import urlopen

from bs4 import BeautifulSoup
from indexify_extractor_sdk import Content, Feature


HTML_PARSER = "html.parser"
WIKIPEDIA_CONTENT_DIV_ID = "mw-content-text"
HTTPS_PREFIX = "https:"

HEADLINE_TAG = "h2"
TITLE_TAG = "h1"
TITLE_ID = "firstHeading"
FIGURE_TAG = "figure"
INFOBOX_CLASS = "infobox vcard"
TABLE_TAG = "table"
FIGURE_CAPTION_TAG = "figcaption"
IMAGE_TAG = "img"
IMAGE_URL_ATTR = "src"
TEXT_TAG = "p"


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
            with open(file_path, "r") as f:
                document = Content.from_text(text=f.read())
                html_content.append(document)

    return html_content


def get_all_image_urls(content: Content) -> list[str]:
    soup = BeautifulSoup(content.data, HTML_PARSER)
    page_content = soup.find("div", {"id": WIKIPEDIA_CONTENT_DIV_ID})

    if not page_content:
        return []

    figures = page_content.find_all(FIGURE_TAG)

    image_urls = []
    for figure in figures:
        caption = figure.find(FIGURE_CAPTION_TAG)
        url = HTTPS_PREFIX + figure.find(IMAGE_TAG)[IMAGE_URL_ATTR]
        image_urls.append([url, caption.text])

    return image_urls


async def get_image_content(session, url, caption):
    async with session.get(url) as response:
        if response.status == 200:
            content_type = response.content_type
            data = await response.read()

            feature = Feature.metadata({"caption": caption}, name="image")

            return Content(content_type=content_type, data=data, feature=feature)


async def get_all_images(image_urls) -> List[Content]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url, caption in image_urls:
            tasks.append(get_image_content(session, url, caption))

        return await asyncio.gather(*tasks)


def extract_images(content: Content):
    image_urls = get_all_image_urls(content)
    if not image_urls:
        return []

    return asyncio.run(get_all_images(image_urls))


def extract_infobox(content: Content) -> dict:
    soup = BeautifulSoup(content.data, HTML_PARSER)
    infobox = soup.find(TABLE_TAG, {"class": INFOBOX_CLASS})
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

        value = value.text.encode("ascii", "ignore").decode().strip()
        value = re.sub(r"[\t]+", " ", value)
        value = re.sub(r"[\n]+", " ", value)
        infobox_dict[key] = value

    return infobox_dict


def extract_sections(content: Content) -> list[Content]:
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


def extract_title(content: Content) -> str:
    soup = BeautifulSoup(content.data, HTML_PARSER)
    title = soup.find(TITLE_TAG, {"id": TITLE_ID})
    if not title:
        return ""

    return title.text

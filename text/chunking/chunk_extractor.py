from typing import Callable, List, Literal

from indexify_extractor_sdk import Content, Feature, extractor
from langchain import text_splitter
from langchain.docstore.document import Document
from pydantic import BaseModel


class ChunkExtractionInputParams(BaseModel):
    overlap: int = 0
    chunk_size: int = 100
    text_splitter: Literal["char", "recursive", "markdown", "html"] = "recursive"
    headers_to_split_on: List[str] = []


def _create_splitter(
    input_params: ChunkExtractionInputParams,
) -> Callable[[str], List[str]]:
    if input_params.text_splitter == "recursive":
        return text_splitter.RecursiveCharacterTextSplitter(
            chunk_size=input_params.chunk_size,
            chunk_overlap=input_params.overlap,
        ).split_text
    elif input_params.text_splitter == "char":
        return text_splitter.CharacterTextSplitter(
            chunk_size=input_params.chunk_size,
            chunk_overlap=input_params.overlap,
            separator="\n\n",
        ).split_text
    elif input_params.text_splitter == "markdown":
        return text_splitter.MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ],
        ).split_text
    elif input_params.text_splitter == "html":
        return text_splitter.HTMLHeaderTextSplitter(
            headers_to_split_on=[
                ("h1", "Header 1"),
                ("h2", "Header 2"),
                ("h3", "Header 3"),
                ("h4", "Header 4"),
            ],
        ).split_text


@extractor(
    name="tensorlake/chunk-extractor",
    description="Text Chunk Extractor",
    python_dependencies=["langchain", "lxml"],
)
def chunk_extractor(
    content: Content, params: ChunkExtractionInputParams
) -> List[Content]:
    splitter = _create_splitter(params)
    text = content.data.decode("utf-8")
    chunks = splitter(text)
    chunk_contents = []
    for chunk in chunks:
        if type(chunk) == Document:
            chunk_content = Content.from_text(
                chunk.page_content,
                features=content.features,
                labels=content.labels,
            )
            if chunk.metadata:
                chunk_content.features.append(Feature.metadata(chunk.metadata))
        else:
            chunk_content = Content.from_text(
                chunk, features=content.features, labels=content.labels
            )

        chunk_contents.append(chunk_content)

    return chunk_contents

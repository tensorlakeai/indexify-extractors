from dataclasses import dataclass
from dataclasses_json import dataclass_json
from langchain import text_splitter
from typing import Callable, List, Literal

from indexify_extractor_sdk import Content, Extractor, Feature


@dataclass_json
@dataclass
class ChunkExtractionInputParams:
    overlap: int = 0
    chunk_size: int = 100
    text_splitter: Literal["char", "recursive"] = "recursive"


class ChunkExtractor(Extractor):
    """
    Extractor that chunks text into smaller pieces.
    """

    def __init__(self):
        super().__init__()

    def extract(
        self, content: Content, params: ChunkExtractionInputParams
    ) -> List[Content]:

        splitter = self._create_splitter(params)
        text = content.data.decode("utf-8")
        chunks = splitter(text)
        chunk_contents = []
        for chunk in chunks:
            chunk_content = Content.from_text(
                chunk, features=content.features, labels=content.labels
            )

            chunk_contents.append(chunk_content)

        return chunk_contents

    def _create_splitter(
        self, input_params: ChunkExtractionInputParams
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

    def sample_input(self) -> Content:
        return Content.from_text(
            "This is a test string to be split into chunks",
            features=[Feature.metadata({"filename": "test.txt"})],
        )

    def extract_sample_input(self) -> List[Content]:
        input = self.sample_input()
        return self.extract(
            input,
            ChunkExtractionInputParams(
                overlap=0, chunk_size=5, text_splitter="recursive"
            ),
        )

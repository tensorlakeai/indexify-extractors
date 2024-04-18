from .recursive_text_splitter import _FastRecursiveTextSplitter
from typing import Any, List

from langchain_text_splitters.base import TextSplitter

class FastRecursiveTextSplitter(TextSplitter):
    def __init__(self, chunk_size: int = 512,  **kwargs: Any):
        super().__init__(**kwargs)
        self._chunk_size = chunk_size
        self._splitter = _FastRecursiveTextSplitter(chunk_size=chunk_size)

    def split_text(self, text: str) -> List[str]:
        return self._splitter.divide_text_into_chunks(text)





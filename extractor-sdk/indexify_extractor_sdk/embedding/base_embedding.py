from abc import abstractmethod
from typing import List, Union

from indexify_extractor_sdk.base_extractor import (
    Content,
    Extractor,
    Feature,
)


class BaseEmbeddingExtractor(Extractor):
    input_mimes = ["text/plain"]

    def __init__(self, max_context_length: int):
        self._model_context_length: int = max_context_length

    def extract(self, content: Content, params = None) -> List[Union[Feature, Content]]:
        text = content.data.decode("utf-8")
        embedding_list = self.extract_embeddings([text])
        if len(embedding_list) == 0:
            return []
        embedding = embedding_list[0]
        return [Feature.embedding(values=embedding)]

    def extract_batch(self, content_list: List[Content], params  = None) -> List[List[Union[Feature, Content]]]:
        out = []
        texts = [content.data.decode("utf-8") for content in content_list]
        embeddings_list = self.extract_embeddings(texts)
        for embedding in embeddings_list:
            feature = Feature.embedding(values=embedding)
            out.append([feature])
        return out

    @abstractmethod
    def extract_embeddings(self, texts: List[str]) -> List[List[float]]: ...

    def sample_input(self) -> Content:
        return Content.from_text("hello world")

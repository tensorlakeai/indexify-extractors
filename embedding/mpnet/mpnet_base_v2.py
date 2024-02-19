from typing import List
from indexify_extractor_sdk import (
    ExtractorSchema,
    EmbeddingSchema,
    Content,
)
from indexify_extractor_sdk.base_embedding import (
    BaseEmbeddingExtractor,
    EmbeddingInputParams,
)
from sentence_transformers import SentenceTransformer

class MPNetV2(BaseEmbeddingExtractor):
    def __init__(self):
        super(MPNetV2, self).__init__(max_context_length=512)
        self._model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.encode(texts)
        return embeddings.tolist()

    @classmethod
    def schemas(cls) -> ExtractorSchema:
        return ExtractorSchema(
            features={
                "embedding": EmbeddingSchema(distance_metric="cosine", dim=768)
            },
        )

if __name__ == "__main__":
    extractor = MPNetV2()
    print(extractor.schemas())
    print(extractor.extract([Content.from_text(text="Hello World")], EmbeddingInputParams()))

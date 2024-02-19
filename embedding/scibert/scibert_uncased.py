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


class SciBERTExtractor(BaseEmbeddingExtractor):
    def __init__(self):
        super(SciBERTExtractor, self).__init__(max_context_length=512)
        self._model = SentenceTransformer("allenai/scibert_scivocab_uncased")

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts, convert_to_tensor=False).tolist()

    @classmethod
    def schemas(cls) -> ExtractorSchema:
        return ExtractorSchema(
            features={
                "embedding": EmbeddingSchema(distance_metric="cosine", dim=768)
            },
        )


if __name__ == "__main__":
    extractor = SciBERTExtractor()
    print(extractor.schemas())
    print(extractor.extract([Content.from_text(text="Scientific discovery is fascinating")], EmbeddingInputParams()))

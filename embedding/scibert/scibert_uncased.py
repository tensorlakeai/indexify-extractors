from typing import List
from indexify_extractor_sdk.embedding.base_embedding import (
    BaseEmbeddingExtractor,
)
from sentence_transformers import SentenceTransformer


class SciBERTExtractor(BaseEmbeddingExtractor):
    name = "tensorlake/scibert"
    description = "A BERT based transformer model trained on scientific text."
    
    def __init__(self):
        super(SciBERTExtractor, self).__init__(max_context_length=512)
        self._model = SentenceTransformer("allenai/scibert_scivocab_uncased")

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts, convert_to_tensor=False).tolist()


if __name__ == "__main__":
    extractor = SciBERTExtractor()
    extractor.extract_sample_input()

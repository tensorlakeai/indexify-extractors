from typing import List
from indexify_extractor_sdk.base_embedding import BaseEmbeddingExtractor
from indexify_extractor_sdk.sentence_transformer import SentenceTransformersEmbedding


class MiniLML6Extractor(BaseEmbeddingExtractor):
    name = "tensorlake/minilm-l6"
    description = "MiniLM-L6 Sentence Transformer"
    python_dependencies = ["torch", "transformers"]
    system_dependencies = []

    def __init__(self):
        super(MiniLML6Extractor, self).__init__(max_context_length=128)
        self._model = SentenceTransformersEmbedding(model_name="all-MiniLM-L6-v2")

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._model.embed_ctx(texts)


if __name__ == "__main__":
    MiniLML6Extractor().run_sample_input()

from typing import List
from indexify_extractor_sdk.embedding.base_embedding import BaseEmbeddingExtractor
from sentence_transformers import SentenceTransformer


class ArcticExtractor(BaseEmbeddingExtractor):
    name = "tensorlake/arctic"
    description = "Snowflake's Artic-embed-m-long"
    system_dependencies = []

    def __init__(self):
        super(ArcticExtractor, self).__init__(max_context_length=512)
        self.model = SentenceTransformer("Snowflake/snowflake-arctic-embed-m")

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts)


if __name__ == "__main__":
    ArcticExtractor().extract_embeddings(['The Data Cloud!', 'Mexico City of Course!'])
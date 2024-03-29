from typing import List
from indexify_extractor_sdk.embedding.base_embedding import (
    BaseEmbeddingExtractor,
)
from sentence_transformers import SentenceTransformer

class MPNetV2(BaseEmbeddingExtractor):
    name = "tensorlake/mpnet"
    description = "This MPNet-based extractor is a Python class that encapsulates the functionality to convert text inputs into vector embeddings using the MPNet model. It leverages MPNet's transformer-based architecture to generate context-aware embeddings suitable for various natural language processing tasks."
    
    def __init__(self):
        super(MPNetV2, self).__init__(max_context_length=512)
        self._model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.encode(texts)
        return embeddings.tolist()


if __name__ == "__main__":
    extractor = MPNetV2()
    extractor.extract_sample_input()

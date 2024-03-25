import hashlib
import numpy as np
from typing import List

from indexify_extractor_sdk.embedding.base_embedding import BaseEmbeddingExtractor


class IdentityHashEmbedding(BaseEmbeddingExtractor):
    name = "yenicelik/identity-hash-extractor"
    description = """Hash Extractor, which can be used to find duplicates within the dataset. 
    It hashes the text into bytes, and interprets these are a numpy array.

    We can extend this by LocalitySensitiveHashing, to also account for small perturbations in the input bytes.

    This is equivalent to an identity mapping (with the sample-size n large enough, there will be collisions, but this is highly unlikely )
    """
    system_dependencies = []

    def __init__(self):
        super(IdentityHashEmbedding, self).__init__(max_context_length=128)

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text) -> List[float]:
        model = hashlib.sha256()
        model.update(bytes(text, "utf-8"))
        out = model.digest()
        return np.frombuffer(out, dtype=np.int8).tolist()

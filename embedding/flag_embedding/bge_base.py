from typing import List
import torch
from transformers import AutoModel, AutoTokenizer
from indexify_extractor_sdk.base_embedding import BaseEmbeddingExtractor

class BGEBase(BaseEmbeddingExtractor):
    name = "BAAI/bge-base-en"
    description = "BGE Base English Model for Sentence Embeddings"
    system_dependencies = []

    def __init__(self):
        super(BGEBase, self).__init__(max_context_length=512)
        self.max_context_length = 512  # TO-CHECK Explicitly set max_context_length as an instance attribute
        self._tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-base-en')
        self._model = AutoModel.from_pretrained('BAAI/bge-base-en')
        self._model.eval()

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        with torch.no_grad():
            inputs = self._tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=self.max_context_length)
            model_output = self._model(**inputs)
            # Use the [CLS] token's embedding for each sentence and apply L2 normalization
            sentence_embeddings = model_output[0][:, 0]
            sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
            # Convert embeddings to list of lists
            embeddings = sentence_embeddings.tolist()
        return embeddings

if __name__ == "__main__":
    BGEBase().run_sample_input()

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
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
from torch import Tensor

class E5SmallEmbeddings(BaseEmbeddingExtractor):
    def __init__(self):
        super(E5SmallEmbeddings, self).__init__(max_context_length=512)
        self._tokenizer = AutoTokenizer.from_pretrained('intfloat/e5-small-v2')
        self._model = AutoModel.from_pretrained('intfloat/e5-small-v2')

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        batch_dict = self._tokenizer(texts, max_length=512, padding=True, truncation=True, return_tensors='pt')
        outputs = self._model(**batch_dict)
        embeddings = self._average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
        # Normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings.tolist()

    def _average_pool(self, last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    @classmethod
    def schemas(cls) -> ExtractorSchema:
        return ExtractorSchema(
            features={
                "embedding": EmbeddingSchema(distance_metric="cosine", dim=384)
            },
        )

if __name__ == "__main__":
    extractor = E5SmallEmbeddings()
    print(extractor.schemas())
    print(extractor.extract([Content.from_text(text="Hello World")], EmbeddingInputParams()))

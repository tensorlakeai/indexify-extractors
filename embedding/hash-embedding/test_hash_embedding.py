import json
import unittest
from typing import Type

from indexify_extractor_sdk.base_embedding import EmbeddingInputParams
from indexify_extractor_sdk.base_extractor import Content, Extractor, ExtractorSchema
from identity_hash_embedding import IdentityHashEmbedding
from parameterized import parameterized


class TestIdentityHashEmbeddingExtractor(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestIdentityHashEmbeddingExtractor, self).__init__(*args, **kwargs)

    @parameterized.expand([("minilm6", IdentityHashEmbedding())])
    def test_ctx_embeddings(self, extractor_name: str, extractor: Type[Extractor]):
        embeddings = extractor.extract(
            [Content.from_text("hello world")],
            EmbeddingInputParams(),
        )
        embeddings_values = json.loads(embeddings[0][0].feature.value)
        self.assertEqual(len(embeddings), 1)
        self.assertEqual(embeddings[0][0].feature.feature_type, "embedding")
        self.assertEqual(len(embeddings_values), 32)

    @parameterized.expand([("minilm6", IdentityHashEmbedding())])
    def test_query_embeddings(self, extractor_name: str, extractor: Type[Extractor]):
        embeddings = extractor.extract_query_embeddings("hello world")
        self.assertEqual(len(embeddings), 32)

    @parameterized.expand([("minilm6", IdentityHashEmbedding())])
    def test_extractor_info(self, extractor_name: str, extractor: Type[Extractor]):
        schema: ExtractorSchema = extractor.schemas()
        self.assertIsNotNone(schema.model_dump()["output_schemas"]["embedding"])


if __name__ == "__main__":
    unittest.main()

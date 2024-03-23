import unittest

from indexify_extractor_sdk.base_extractor import ExtractorWrapper, Content, Feature

from indexify_extractor_sdk.mock_extractor import MockExtractor, InputParams

from typing import List


class TestMockExtractor(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestMockExtractor, self).__init__(*args, **kwargs)

    def test_mock_extractor(self):
        params = InputParams(a=1, b="foo")
        e = MockExtractor()
        extracted_content = e.extract(
            Content(content_type="text", data=bytes("Hello World", encoding="utf-8")),
            params,
        )
        self.assertEqual(len(extracted_content), 2)

    def test_extractor_wrapper(self):
        e = ExtractorWrapper("indexify_extractor_sdk.mock_extractor", "MockExtractor")
        extracted_content = e.extract_batch(
            {"task1":Content(content_type="text", data=bytes("Hello World", encoding="utf-8"))},
            '{"a": 1, "b": "foo"}',
        )
        self.assertEqual(len(extracted_content), 1)

    def test_extractor_schema(self):
        e = ExtractorWrapper("indexify_extractor_sdk.mock_extractor", "MockExtractor")
        schemas = e.describe()
        self.assertEqual(schemas.embedding_schemas["embedding"].distance, "cosine")

    def test_run_sample_input(self):
        e = MockExtractor()
        result = e.extract_sample_input()
        self.assertEqual(len(result), 2)

    def test_only_features(self):
        e = ExtractorWrapper(
            "indexify_extractor_sdk.mock_extractor", "MockExtractorsReturnsFeature"
        )
        extracted_features: List[Feature] = e.extract_batch(
            {"task1" :Content(content_type="text", data=bytes("Hello World", encoding="utf-8"))},
            '{"a": 1, "b": "foo"}',
        )
        self.assertEqual(len(extracted_features), 1)
        self.assertEqual(extracted_features["task1"][0].feature_type, "embedding")
        self.assertEqual(extracted_features["task1"][1].feature_type, "metadata")


if __name__ == "__main__":
    unittest.main()

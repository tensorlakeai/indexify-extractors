import json
import unittest

from indexify_extractor_sdk.base_extractor import Content, Feature
from chunk_extractor import ChunkExtractor, ChunkExtractionInputParams


class TestChunkExtractor(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestChunkExtractor, self).__init__(*args, **kwargs)
        self.text_content = self._get_text_content()

    def _get_text_content(self) -> Content:
        return Content.from_text(
            "This is a test string to be split into chunks",
            features=[Feature.metadata({"filename": "test.txt"})],
        )

    def test_chunk_extraction(self):

        extracted_content = ChunkExtractor().extract_sample_input()

        self.assertGreater(len(extracted_content), 1, "Text is not chunked")

        self.assertEqual(
            json.loads(extracted_content[0].features[0].value)["filename"],
            "test.txt",
            "Feature not correctly extracted",
        )


if __name__ == "__main__":
    unittest.main()

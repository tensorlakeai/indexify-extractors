import unittest

from chunk_extractor import ChunkExtractionInputParams, chunk_extractor
from indexify_extractor_sdk.base_extractor import Content, Feature


class TestChunkExtractor(unittest.TestCase):
    def test_chunk_extraction(self):
        extracted_content = chunk_extractor().extract(
            Content.from_text(
                "This is a test string to be split into chunks",
                features=[Feature.metadata({"filename": "test.txt"})],
            ),
            ChunkExtractionInputParams(
                chunk_size=5, overlap=0, text_splitter="recursive"
            ),
        )

        self.assertGreater(len(extracted_content), 1, "Text is not chunked")

        self.assertEqual(
            extracted_content[0].features[0].value["filename"],
            "test.txt",
            "Feature not correctly extracted",
        )


if __name__ == "__main__":
    unittest.main()

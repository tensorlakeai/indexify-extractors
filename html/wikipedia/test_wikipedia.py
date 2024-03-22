import json
import unittest

from typing import List

from indexify_extractor_sdk.base_extractor import Content, Feature
from wikipedia import WikipediaExtractor


class TestWikipediaExtractor(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestWikipediaExtractor, self).__init__(*args, **kwargs)
        self.html_content = self._get_html_content()

    def _get_html_content(self) -> List[Content]:
        import os

        dirname = os.path.dirname(__file__)
        file_name = "Stephen_Curry.html"
        file_path = os.path.join(dirname, "utils/", file_name)

        with open(file_path, "rb") as f:
            data = f.read()

        return Content(
            data=data, 
            content_type="text/html",
            feature=Feature.metadata({"filename": file_name}),
        )

    def test_wikipedia_extraction(self):
        extracted_content = WikipediaExtractor().extract_sample_input()
        extracted_features = json.loads(extracted_content[0].feature.value)

        self.assertIsNotNone(extracted_content[0], "No content extracted")

        self.assertEqual(extracted_features["filename"],
                         "Stephen_Curry.html",
                         "Filename not correctly extracted")

        self.assertEqual(extracted_features["title"],
                         "Stephen Curry",
                         "Title not correctly extracted")


if __name__ == '__main__':
    unittest.main()

from indexify_extractor_sdk.extractor_worker import ExtractorWorker
from indexify_extractor_sdk.base_extractor import Content, ExtractorWrapper
import unittest
import asyncio

from unittest import IsolatedAsyncioTestCase


class TestExtractorWorker(IsolatedAsyncioTestCase):
    def __init__(self, *args, **kwargs):
        super(TestExtractorWorker, self).__init__(*args, **kwargs)

    async def test_extract(self):
        wrapper = ExtractorWrapper(
            "indexify_extractor_sdk.mock_extractor", "MockExtractor"
        )
        e_worker = ExtractorWorker(wrapper)
        content = Content.from_text("hello world")
        loop = asyncio.get_event_loop()
        extracted_content = await e_worker.extract(
            loop=loop, content=content, params='{"a": 1, "b": "foo"}'
        )
        self.assertEqual(len(extracted_content), 2)


if __name__ == "__main__":
    unittest.main()

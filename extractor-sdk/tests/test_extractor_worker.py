from indexify_extractor_sdk.extractor_worker import (
    extract_content,
    ExtractorModule,
    create_executor,
)
from indexify_extractor_sdk.base_extractor import Content
import unittest
import asyncio

from unittest import IsolatedAsyncioTestCase


class TestExtractorWorker(IsolatedAsyncioTestCase):
    def __init__(self, *args, **kwargs):
        super(TestExtractorWorker, self).__init__(*args, **kwargs)

    async def test_extract(self):
        extactor_module = ExtractorModule(
            module_name="indexify_extractor_sdk.mock_extractor",
            class_name="MockExtractor",
        )
        executor = create_executor(extactor_module)
        content = Content.from_text("hello world")
        content1 = Content.from_text("pipe baz")
        loop = asyncio.get_event_loop()
        extracted_content = await extract_content(
            loop=loop,
            executor=executor,
            content=content,
            params='{"a": 1, "b": "foo"}',
        )
        self.assertEqual(len(extracted_content), 2)

        extracted_content1 = await extract_content(
            loop=loop,
            executor=executor,
            content=content1,
            params='{"a": 1, "b": "foo"}',
        )


if __name__ == "__main__":
    unittest.main()

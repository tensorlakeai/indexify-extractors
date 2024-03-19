import unittest
import json
from indexify_extractor_sdk.base_extractor import Feature


class TestExtractorWorker(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestExtractorWorker, self).__init__(*args, **kwargs)

    def test_metadata_schema(self):
        metadata = {
            "a": 1,
            "b": "foo",
            "c": [1, 2, 3],
            "x": 3.4,
            "y": False,
            "d": {"e": "bar"},
            "e": ["a", "b", "c"],
        }
        feature = Feature.metadata(json.dumps(metadata), name="foo")
        schema = feature.get_schema()
        self.assertEqual(
            schema,
            {
                "a": {"type": "integer"},
                "b": {"type": "string"},
                "c": {"type": "array"},
                "x": {"type": "number"},
                "y": {"type": "boolean"},
                "d": {"type": "object"},
                "e": {"type": "array"},
            },
        )


if __name__ == "__main__":
    unittest.main()

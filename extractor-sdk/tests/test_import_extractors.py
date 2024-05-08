import unittest
# from indexify_extractor_sdk import load_indexify_extractors, load_extractor
# from indexify_extractor_sdk.downloader import download_extractor
import json
import os

class TestLoadAllExtractors(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLoadAllExtractors, self).__init__(*args, **kwargs)

    def test_download_all_extractors_function(self):
        extractors_json_path = os.path.join(os.path.dirname(__file__),"../../", "extractors.json")
        f = open(extractors_json_path,'r')
        extractors = json.loads(f.read())
        for e in extractors:
            module = e.get("module_name").split(":")[0]
            print(module)
            # download_extractor()
    
    def test_downloaded_extractors_describe(self):
        # depend on
        pass


if __name__ == "__main__":
    unittest.main()

import unittest
# from indexify_extractor_sdk import load_indexify_extractors, load_extractor
from indexify_extractor_sdk.downloader import download_extractor
import json
import os

class TestLoadAllExtractors(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLoadAllExtractors, self).__init__(*args, **kwargs)

    def test_download_all_extractors_function(self):
        extractors_json_path = os.path.join(
            os.path.dirname(__file__),
            "../../",
            "extractors.json"
        )

        with open(extractors_json_path,"r") as f:
            extractors = json.loads(f.read())
            for extractor in extractors:
                folder = extractor.get("type")
                module = extractor.get("module_name").split(":")[0].split(".")[0]
                extractor_path = f"hub://{folder}/{module}"

                print(f"testing extractor: {module}")

                # Skip the test if the extractor is marked to be skipped.
                if extractor.get("skip_deploy", False):
                    continue

                # FIXME: this fails for me due to some issue with nvidia-cublas-cu11
                # and whisper-diarization.whisper_diarization:WhisperDiarizationExtractor
                download_extractor(extractor_path)

    def test_downloaded_extractors_describe(self):
        # depend on
        pass


if __name__ == "__main__":
    unittest.main()

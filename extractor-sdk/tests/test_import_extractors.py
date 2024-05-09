import unittest
from indexify_extractor_sdk.indexify_extractor import describe_sync
from indexify_extractor_sdk.downloader import download_extractor, find_extractor_subclasses, get_extractor_description
import json
import os
import random
from pathlib import Path
from shutil import copytree
from indexify_extractor_sdk.base_extractor import EXTRACTOR_MODULE_PATH

# Root path of the indexify-extractors project.
ROOT = Path(__file__).resolve().parents[2]

def setup_test_environment(extractors):
    """This setup method will:
    1. Install the extractor-sdk from source.
    2. Move the extractors to the extractors folder.
    3. Install the dependencies for each extractor.

    Args:
    - extractors: List of extractors in extractors.json file.
    """

    if not os.environ.get("VIRTUAL_ENV"):
        raise Exception("Please run this test in a virtual environment.")

    venv = os.environ.get("VIRTUAL_ENV")
    pip = os.path.join(venv, "bin", "pip")

    # Install extractor-sdk from source
    extractor_sdk_path = os.path.join(ROOT, "extractor-sdk")
    os.system(f"{pip} install -e {extractor_sdk_path}")

    # Extractors folder path
    for extractor in extractors:
        folder = extractor.get("type")
        module = extractor.get("module_name").split(":")[0].split(".")[0]

        current_extractor_path = os.path.join(ROOT, folder, module)
        new_extractor_path = os.path.join(EXTRACTOR_MODULE_PATH, module)

        print(f"setting up extractor: {module}")

        # Copy the extractor module to the extractors folder
        if os.path.isdir(current_extractor_path):
            copytree(current_extractor_path, new_extractor_path, dirs_exist_ok=True)

        # Install the dependencies
        requirements_path = os.path.join(new_extractor_path, "requirements.txt")
        if os.path.exists(requirements_path):
            os.system(f"{pip} install -r {requirements_path}")


class TestLoadAllExtractors(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLoadAllExtractors, self).__init__(*args, **kwargs)

        # Extractors to skip for testing
        skip_extractors = [
            "openai-embedding.openai_embedding:OpenAIEmbeddingExtractor",
            "whisper-asr.whisper_extractor:WhisperExtractor",
            "whisper-diarization.whisper_diarization:WhisperDiarizationExtractor",
        ]

        extractors_json_path = os.path.join(ROOT, "extractors.json")

        with open(extractors_json_path,"r") as f:
            self.extractors = [
                extractor for extractor in json.loads(f.read())
                if extractor.get("module_name") not in skip_extractors and
                not extractor.get("skip_deploy", False)
            ]

        setup_test_environment(self.extractors)

    def test_get_extractor_subclasses(self):
        """Test the extractor modules have the correct class name: module:class."""
        for extractor in self.extractors:
            folder = extractor.get("type")
            module_name = extractor.get("module_name")
            module_dir, module_class = module_name.split(".")
            path = os.path.join(EXTRACTOR_MODULE_PATH, module_dir)
            subclass_name = find_extractor_subclasses(path)
            assert subclass_name == module_class

    def test_get_extractor_description(self):
        for extractor in self.extractors:
            module_name = extractor.get("module_name")
            print("testing", module_name)
            extractor_description = get_extractor_description(module_name)
            assert extractor_description is not None
            assert len(extractor_description.description) > 0
            assert len(extractor_description.name) > 0

    def test_download_extractors_sampled(self):
        # Randomly pick 3 extractors to test download
        extractors = random.sample(self.extractors, 3)

        for extractor in extractors:
            folder = extractor.get("type")
            module_name = extractor.get("module_name")
            module_dir = module_name.split(".")[0]
            extractor_path = f"hub://{folder}/{module_dir}"

            print(f"testing download extractor: {module_name}")

            # Skip the test if the extractor is marked to be skipped.
            if extractor.get("skip_deploy", False):
                continue

            download_extractor(extractor_path)

            # Test that the extractor is downloaded and ready to use.
            # If describe_sync does not raise an exception, the extractor is downloaded.
            describe_sync(module_name)


if __name__ == "__main__":
    unittest.main()

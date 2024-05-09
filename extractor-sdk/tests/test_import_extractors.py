import unittest
# from indexify_extractor_sdk import load_indexify_extractors, load_extractor
from indexify_extractor_sdk.downloader import download_extractor, find_extractor_subclasses, get_extractor_description
import json
import os
import pytest
from pathlib import Path
from shutil import copytree
from indexify_extractor_sdk.base_extractor import EXTRACTOR_MODULE_PATH

def setup_test_environment(extractors):
    """This setup method will:
    1. Install the extractor-sdk from source.
    2. Move the extractors to the extractors folder.
    3. Install the dependencies for each extractor.

    Args:
    - extractors: List of extractors in extractors.json file.
    """

    # Root path of the indexify-extractors project,
    root = Path(__file__).resolve().parents[2]

    if not os.environ.get("VIRTUAL_ENV"):
        raise Exception("Please run this test in a virtual environment.")

    venv = os.environ.get("VIRTUAL_ENV")
    pip = os.path.join(venv, "bin", "pip")

    # Install extractor-sdk from source
    extractor_sdk_path = os.path.join(root, "extractor-sdk")
    os.system(f"{pip} install -e {extractor_sdk_path}")

    # Extractors folder path
    for extractor in extractors:
        folder = extractor.get("type")
        module = extractor.get("module_name").split(":")[0].split(".")[0]

        current_extractor_path = os.path.join(root, folder, module)
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
            "whisper-asr.whisper_extractor:WhisperExtractor"
        ]

        extractors_json_path = os.path.join(
            os.path.dirname(__file__),
            "../../",
            "extractors.json"
        )

        with open(extractors_json_path,"r") as f:
            self.extractors = [
                extractor for extractor in json.loads(f.read())
                if extractor.get("module_name") not in skip_extractors
            ]

        setup_test_environment(self.extractors)


    def test_get_extractor_subclasses(self):
        """
        Test that each extractor has file that subclasses extractor class
        """
        for extractor in self.extractors:
            folder = extractor.get("type")
            module_name = extractor.get("module_name")
            module_dir = module_name.split(".")[0]
            path = os.path.join("../../",folder,module_dir)
            subclass_name = find_extractor_subclasses(path)
            assert ":" in subclass_name


    @pytest.mark.dependency(depends=['test_download_all_extractors_function'])
    def test_get_extractor_description(self):
        """
        Test that each extractor has file that subclasses extractor class
        """
        for extractor in self.extractors:
            module_name = extractor.get("module_name")
            print("testing", module_name)
            extractor_description = get_extractor_description(module_name)
            assert extractor_description is not None
            assert len(extractor_description.description) > 0
            assert len(extractor_description.name) > 0

    def test_download_all_extractors_function(self):
        for extractor in self.extractors:
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

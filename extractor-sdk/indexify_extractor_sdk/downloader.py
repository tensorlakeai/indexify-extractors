import fsspec
import string


def download_extractor(extractor_path: str):
    extractor_path = extractor_path.removeprefix("hub://")
    fs = fsspec.filesystem("github", org="tensorlakeai", repo="indexify-extractors")
    fs.get(extractor_path, "indexify-extractor", recursive=True)

from indexify_extractor_sdk.packager import ExtractorPackager
import pytest
import gzip
import tarfile
import io


@pytest.fixture
def packager():
    return ExtractorPackager(
        module_name="indexify_extractor_sdk.mock_extractor",
        class_name="MockExtractor",
        dockerfile_template_path="dockerfiles/Dockerfile.extractor",
        verbose=False,
        dev=False,
        gpu=False,
    )


@pytest.fixture
def packager_dev():
    return ExtractorPackager(
        module_name="indexify_extractor_sdk.mock_extractor",
        class_name="MockExtractor",
        dockerfile_template_path="dockerfiles/Dockerfile.extractor",
        verbose=False,
        dev=True,
        gpu=False,
    )


def test_generate_dockerfile(packager, snapshot):
    # `syrupy` snapshot testing -
    dockerfile_content = packager._generate_dockerfile()
    assert dockerfile_content == snapshot


def test_generate_dockerfile_dev(packager_dev, snapshot):
    dockerfile_content = packager_dev._generate_dockerfile()
    assert dockerfile_content == snapshot


def test_generate_compressed_tarball(packager):
    dockerfile_content = packager._generate_dockerfile()
    tarball_bytes = packager._generate_compressed_tarball(dockerfile_content)

    with gzip.open(io.BytesIO(tarball_bytes), "rb") as f:
        with tarfile.open(fileobj=f, mode="r") as tar:
            tarball = tar.getnames()

    # print contents of tarball
    assert "Dockerfile" in tarball
    assert "mock_extractor.py" in tarball

    # dev files are NOT there
    assert "pyproject.toml" not in tarball
    assert "README.md" not in tarball
    assert "indexify_extractor_sdk/__init__.py" not in tarball
    assert "indexify_extractor_sdk/base_extractor.py" not in tarball


def test_generate_compressed_tarball_dev(packager_dev):
    dockerfile_content = packager_dev._generate_dockerfile()
    tarball_bytes = packager_dev._generate_compressed_tarball(dockerfile_content)

    with gzip.open(io.BytesIO(tarball_bytes), "rb") as f:
        with tarfile.open(fileobj=f, mode="r") as tar:
            tarball = tar.getnames()

    # print contents of tarball
    assert "Dockerfile" in tarball
    assert "mock_extractor.py" in tarball

    # minimum dev files are there
    assert "pyproject.toml" in tarball
    assert "README.md" in tarball
    assert "indexify_extractor_sdk/__init__.py" in tarball
    assert "indexify_extractor_sdk/base_extractor.py" in tarball


@pytest.mark.skip(reason="This test will build the docker image and will take time")
def test_package(packager):
    # This test will create an image at mock_extractor:latest
    # Enter the image with: `docker run -it --entrypoint "" mock_extractor:latest sh -c /bin/bash`
    packager.package()

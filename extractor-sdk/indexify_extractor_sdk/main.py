import typer
from . import indexify_extractor, version
from .packager import ExtractorPackager
from typing import Optional
import logging
import os

import sys

sys.path.append(".")

if os.path.exists("indexify-extractor"):
    sys.path.append("indexify-extractor")

typer_app = typer.Typer(
    help="indexify-extractor - CLI for running and packaging indexify extractors"
)


# Hack to get around buffered output when not run using interactive terminal in docker
# and to ensure that print statements are flushed immediately
class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


sys.stdout = Unbuffered(sys.stdout)


def print_version():
    print(f"indexify-extractor-sdk version {version.__version__}")


@typer_app.command()
def describe(extractor: str):
    indexify_extractor.describe_sync(extractor)


@typer_app.command()
def local(
    extractor: str = typer.Argument(
        None,
        help="The extractor name in the format 'module_name:class_name'. For example, 'mock_extractor:MockExtractor'.",
    ),
    text: Optional[str] = None,
    file: Optional[str] = None,
):
    indexify_extractor.local(extractor, text, file)


@typer_app.command()
def join(
    # optional, default to $EXTRACTOR_PATH if not provided. If $EXTRACTOR_PATH is not set, it will raise an error.
    extractor: str = typer.Argument(
        None,
        help="The extractor name in the format 'module_name:class_name'. For example, 'mock_extractor:MockExtractor'.",
    ),
    coordinator_addr: str = "localhost:8950",
    ingestion_addr: str = "localhost:8900",
):
    print_version()
    if not extractor:
        extractor = os.environ.get("EXTRACTOR_PATH")
        print(f"Using extractor path from $EXTRACTOR_PATH: {extractor}")
        assert extractor, "Extractor path not provided and $EXTRACTOR_PATH not set."

    indexify_extractor.join(extractor, coordinator_addr, ingestion_addr)


@typer_app.command()
def package(
    extractor: str = typer.Argument(
        ...,
        help="The extractor name in the format 'module_name:class_name'. For example, 'mock_extractor:MockExtractor'.",
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Run in verbose mode."),
    dev: bool = typer.Option(False, "--dev", help="Run in development mode."),
    gpu: bool = typer.Option(False, "--gpu", help="Use GPU acceleration."),
):
    """
    Packages an extractor into a Docker image, including Dockerfile generation and tarball creation.
    """
    print_version()
    module_name, class_name = indexify_extractor.split_validate_extractor(extractor)
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    packager = ExtractorPackager(
        module_name=module_name,
        class_name=class_name,
        verbose=verbose,
        dev=dev,
        gpu=gpu,
    )
    packager.package()


@typer_app.command()
def download(extractor_path: str = typer.Argument(..., help="Extractor Name")):
    from .downloader import download_extractor

    download_extractor(extractor_path)

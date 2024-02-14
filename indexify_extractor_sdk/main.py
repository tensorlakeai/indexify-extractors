import typer
from . import indexify_extractor, version
from .packager import ExtractorPackager
from typing import Optional
import logging
import os

import sys

sys.path.append(".")

typer_app = typer.Typer()

def print_version():
    print(f"indexify-extractor-sdk version {version.__version__}")

@typer_app.command()
def describe(extractor: str):
    indexify_extractor.describe(extractor)


@typer_app.command()
def local(extractor: str, text: Optional[str] = None, file: Optional[str] = None):
    indexify_extractor.local(extractor, text, file)


@typer_app.command()
def join(
    # optional, default to $EXTRACTOR_PATH if not provided. If $EXTRACTOR_PATH is not set, it will raise an error.
    extractor: str = typer.Argument(
        None,
        help="The extractor name in the format 'module_name:class_name'. For example, 'mock_extractor:MockExtractor'.",
    ),
    coordinator: str = "localhost:8950",
    ingestion_addr: str = "localhost:8900",
):
    print_version()
    if not extractor:
        extractor = os.environ.get("EXTRACTOR_PATH")
        print(f"Using extractor path from $EXTRACTOR_PATH: {extractor}")
        assert extractor, "Extractor path not provided and $EXTRACTOR_PATH not set."

    indexify_extractor.join(extractor, coordinator, ingestion_addr)


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

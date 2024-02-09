import typer
from . import indexify_extractor
from .packager import ExtractorPackager, ExtractorPackagerConfig
from typing import Optional
import logging

import sys

sys.path.append(".")

typer_app = typer.Typer()


@typer_app.command()
def describe(extractor: str):
    indexify_extractor.describe(extractor)


@typer_app.command()
def local(extractor: str, text: Optional[str] = None, file: Optional[str] = None):
    indexify_extractor.local(extractor, text, file)

@typer_app.command()
def join(
    extractor: str,
    coordinator: str = "localhost:8950",
    ingestion_addr: str = "localhost:8900",
):
    indexify_extractor.join(extractor, coordinator, ingestion_addr)

@typer_app.command()
def package(
    module_name: str = typer.Argument(..., help="The name of the module."),
    class_name: str = typer.Argument(..., help="The name of the class."),
    dockerfile_template_path: str = typer.Option("../dockerfiles/Dockerfile.extractor", "--dockerfile-template-path", help="Path to the Dockerfile template."),
    verbose: bool = typer.Option(False, "--verbose", help="Run in verbose mode."),
    dev: bool = typer.Option(False, "--dev", help="Run in development mode."),
    gpu: bool = typer.Option(False, "--gpu", help="Use GPU acceleration.")
):
    """
    Packages an extractor into a Docker image, including Dockerfile generation and tarball creation.
    """
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    config = ExtractorPackagerConfig(
        module_name=module_name,
        class_name=class_name,
        dockerfile_template_path=dockerfile_template_path,
        verbose=verbose,
        dev=dev,
        gpu=gpu
    )
    packager = ExtractorPackager(config)
    packager.package()
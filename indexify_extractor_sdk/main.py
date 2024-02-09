import typer
from . import indexify_extractor
from typing import Optional

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

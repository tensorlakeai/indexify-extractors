import typer
from .indexify_extractor import join, describe, local
from typing import Optional

typer_app = typer.Typer()


@typer_app.command()
def describe(extractor: str):
    describe(extractor)


@typer_app.command()
def local(extractor: str, text: Optional[str] = None, file: Optional[str] = None):
    local(extractor, text, file)


@typer_app.command()
def join(
    extractor: str,
    coordinator: str = "localhost:8950",
    ingestion_addr: str = "localhost:8900",
):
    join(extractor, coordinator, ingestion_addr)

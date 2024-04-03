import fsspec
import json
from rich.console import Console
from rich.table import Table
from typing import Optional


def read_json_file(filename):
    # # debug
    # with open(filename, "r") as file:
    #     json_content = json.load(file)
    # return json_content

    fs = fsspec.filesystem("github", org="tensorlakeai", repo="indexify-extractors")
    file_path = filename

    with fs.open(file_path, "r") as file:
        # Load the JSON content from the file
        json_content = json.load(file)

    return json_content


def list_extractors(extractor_type: Optional[str] = None):
    extractor_data = read_json_file("extractors.json")

    table = Table(title="[bold]Extractor List[/bold]", title_justify="left")

    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Download Link", style="orange3")
    table.add_column("Run Command", style="green")

    for extractor in extractor_data:
        if extractor_type and extractor_type != extractor.get("type"):
            continue
        module_name = extractor.get("module_name")
        name = module_name.split(".")[0]

        table.add_row(
            module_name.split(".")[0],
            extractor.get("type"),
            f"hub://{extractor.get('type')}/{name}",
            f"indexify-extractor join-server {module_name}",
        )

    console = Console()
    console.print(table)

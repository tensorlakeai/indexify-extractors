import sqlite3
import json
import fsspec
import os
import sys
import ast
import subprocess
from rich.console import Console
from rich.panel import Panel
from .extractor_worker import ExtractorWrapper
from .base_extractor import ExtractorDescription, EXTRACTORS_PATH, EXTRACTOR_MODULE_PATH
from .utils import log_event, read_extractors_json_file
console = Console()

VENV_PATH = os.path.join(EXTRACTORS_PATH, "ve")

class ClassVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []

    def visit_ClassDef(self, node):
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in ['Extractor', 'BaseEmbeddingExtractor']:
                self.classes.append(node.name)
        self.generic_visit(node)

def find_extractor_subclasses(root_dir):
    for filename in os.listdir(root_dir):
        if filename.endswith('.py'):
            with open(os.path.join(root_dir, filename), 'r') as file:
                content = file.read()
                try:
                    tree = ast.parse(content)
                    visitor = ClassVisitor()
                    visitor.visit(tree)
                    if visitor.classes:
                        base_name = os.path.splitext(filename)[0]
                        return f"{base_name}:{visitor.classes[0]}"
                except SyntaxError as e:
                    print(f"Syntax error in {filename}: {e}")


def print_instructions():
    message = """To use all the downloaded extractors run the following:\n[bold #4AA4F4]"""

    if not os.environ.get("VIRTUAL_ENV"):
        message += f"source {VENV_PATH}/bin/activate\n"

    message += f"indexify-extractor join-server[/]"
    console.print(Panel(message, title="[bold magenta]Run the extractor[/]", expand=True))


def create_new_venv():
    print("Creating virtual environment...")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    try:
        subprocess.check_call(['virtualenv', '-p', f"python{version_str}", VENV_PATH])

        # Load python from the virtual environment to sys.path
        # This is required since to get the extractor description,
        # we need to import the extractor module which depends on
        # the dependencies installed in the virtual environment.
        sys.path.append(os.path.join(
            VENV_PATH,
            "lib",
            f"python{version.major}.{version.minor}",
            "site-packages")
        )
    except FileNotFoundError as err:
        if "virtualenv" in str(err):
            console.print("[bold #f04318]command virtualenv not found, did you install it? Try 'pip install virtualenv'[/]")
            return
        else:
            raise
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=} while attempting to create virtual envirnment.")
        raise


def install_dependencies(directory_path):
    console.print("[bold #4AA4F4]Installing dependencies...[/]")
    requirements_path = os.path.join(directory_path, "requirements.txt")

    if not os.path.exists(requirements_path):
            raise ValueError("Unable to find requirements.txt")

    if os.environ.get("VIRTUAL_ENV"):
        # install requirements to current env
        pip_path = os.path.join(os.environ.get("VIRTUAL_ENV"), 'bin', 'pip')
        subprocess.check_call([pip_path, 'install', '-r', requirements_path])
    else:
        create_new_venv()

        # install requirements to new venv
        pip_path = os.path.join(VENV_PATH, 'bin', 'pip')
        subprocess.check_call([pip_path, 'install', '-r', requirements_path])
        subprocess.check_call([pip_path, 'install', 'indexify-extractor-sdk']) 


def get_db_path():
    """Returns the path the extractors database file."""
    db_path = os.path.join(EXTRACTORS_PATH, "extractors.db")
    return db_path

def create_extractor_db():
    # Connect to the database
    path = get_db_path()
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    # Check if the table exists
    table_name = "extractors"
    cur.execute(f"""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' 
        AND name='{table_name}'
    """)

    # If the table exists, return
    if  cur.fetchone():
        conn.close()
        return

    # Create the table
    # ID is the full extractor name: minilm-l6.minilm_l6:MiniLML6Extractor
    cur.execute(f"""
        CREATE TABLE {table_name} (
            id TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            input_params TEXT,
            input_mime_types TEXT,
            metadata_schemas TEXT,
            embedding_schemas TEXT
        )
    """)

    conn.commit()
    conn.close()

def get_extractor_description(name: str) -> ExtractorDescription:
    module, cls = name.split(":")
    module = f"indexify_extractors.{module}"
    wrapper = ExtractorWrapper(module, cls)
    return wrapper.describe()

def get_extractor_full_name(directory: str):
    path = os.path.join(EXTRACTOR_MODULE_PATH, directory)
    name = find_extractor_subclasses(path)
    return f"{directory}.{name}"

def sanitize_db_value(value: str) -> str:
    return value.replace("'", "''")

def serialize_embedding_schemas(embedding_schemas) -> str:
    schemas = {}
    for name, embedding_schema in embedding_schemas.items():
        schemas[name] = embedding_schema.model_dump_json()
    return json.dumps(schemas)

def save_extractor_description(id: str, description: ExtractorDescription):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if the extractor already exists
    cur.execute("""
        SELECT id 
        FROM extractors 
        WHERE id=?
    """, [id])

    if cur.fetchone():
        # delete the existing extractor record.
        # This is to ensure that the database is always
        # up-to-date with the latest extractor info.
        cur.execute("""
            DELETE FROM extractors
            WHERE id=?
        """, [id])

    input_params: str = description.input_params if description.input_params else None

    # Convert the lists to JSON strings
    mime_types = json.dumps(description.input_mime_types)
    embedding_schemas = serialize_embedding_schemas(description.embedding_schemas)
    metadata_schemas = json.dumps(description.metadata_schemas)

    # Insert the extractor info into the database
    cur.execute("""
        INSERT INTO extractors (
            id, name, description, input_params, input_mime_types, metadata_schemas, embedding_schemas
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?
        )
    """, [id, description.name, description.description, input_params, mime_types, metadata_schemas, embedding_schemas])

    conn.commit()
    conn.close()

def extractors_by_name():
    extractors_info_list = read_extractors_json_file("extractors.json")
    result = {}
    for extractor_info in extractors_info_list:
        result[extractor_info["name"]] = extractor_info
    return result

def download_extractor(extractor_name):
    # Create extractor database if not exists
    create_extractor_db()

    console.print("[bold #4AA4F4]Downloading Extractor...[/]")
    extractors_index = extractors_by_name()
    fs = fsspec.filesystem("github", org="tensorlakeai", repo="indexify-extractors")
    if extractor_name not in extractors_index:
        console.print(f"[bold #f04318]Extractor {extractor_name} not found[/]")
        console.print(f"[bold #f04318]Use command: [yellow]indexify-extractor list[/yellow] to see the list of available extractors[/]")
        return
    extractor_path = extractors_index[extractor_name]["path"]

    fs.get(extractor_path, EXTRACTOR_MODULE_PATH, recursive=True)
    base_extractor_path = os.path.basename(extractor_path)
    install_dependencies(os.path.join(EXTRACTOR_MODULE_PATH, base_extractor_path))

    # Store the extractor info in the database
    
    extractor_full_name = get_extractor_full_name(base_extractor_path)
    description = get_extractor_description(extractor_full_name)
    
    if description.name.startswith("tensorlake"):
        log_event("extractor_download", description.name)

    try:
        save_extractor_description(extractor_full_name, description)
    except Exception as e:
        print(f"Error saving extractor description: {e}")
        raise e

    # Print instruction last to improve user experience.
    print_instructions()

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
from .base_extractor import ExtractorDescription

console = Console()


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


def print_instructions(directory_path):
    venv_path = os.path.join(directory_path, "ve")

    message = """To run extractor, run the following:\n[bold #4AA4F4]"""

    if not os.environ.get("VIRTUAL_ENV"):
        message += f"source {venv_path}/bin/activate\n"

    message += f"indexify-extractor join-server {os.path.basename(directory_path)}.{find_extractor_subclasses(directory_path)}[/]"
    console.print(Panel(message, title="[bold magenta]Run the extractor[/]", expand=True))
    
    
def install_dependencies(directory_path):
    console.print("[bold #4AA4F4]Installing dependencies...[/]")
    venv_path = os.path.join(directory_path, "ve")
    requirements_path = os.path.join(directory_path, "requirements.txt")
    
    if not os.path.exists(requirements_path):
            raise ValueError("Unable to find requirements.txt")
        
    if os.environ.get("VIRTUAL_ENV"):
        # install requirements to current env
        subprocess.check_call([os.path.join(os.environ.get("VIRTUAL_ENV"), 'bin', 'pip'), 'install', '-r', requirements_path])
    else:
        # create env and install requirements
        print("Creating virtual environment...")
        version_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        subprocess.check_call(['virtualenv', '-p', f"python{version_str}", venv_path])
        pip_path = os.path.join(venv_path, 'bin', 'pip')

        subprocess.check_call([pip_path, 'install', '-r', requirements_path])
        subprocess.check_call([pip_path, 'install', 'indexify-extractor-sdk'])

    # print instructions for next steps
    print_instructions(directory_path)

def get_db_path():
    """Returns the path the extractors database file."""
    base_path = os.path.join(os.path.expanduser("~"), ".indexify-extractors")

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    db_path = os.path.join(base_path, "extractors.db")
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
    wrapper = ExtractorWrapper(module, cls)
    return wrapper.describe()

def get_extractor_full_name(directory: str):
    path = os.path.join(os.path.expanduser("~"), ".indexify-extractors", directory)
    name = find_extractor_subclasses(path)
    return f"{directory}.{name}"

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
    cur.execute(f"""
        SELECT id 
        FROM extractors 
        WHERE id='{id}'
    """)

    if cur.fetchone():
        # delete the existing extractor record.
        # This is to ensure that the database is always
        # up-to-date with the latest extractor info.
        cur.execute(f"""
            DELETE FROM extractors
            WHERE id='{id}'
        """)

    input_params: str = description.input_params if description.input_params else None

    # Convert the lists to JSON strings
    mime_types = json.dumps(description.input_mime_types)
    embedding_schemas = serialize_embedding_schemas(description.embedding_schemas)
    metadata_schemas = json.dumps(description.metadata_schemas)

    # Insert the extractor info into the database
    cur.execute(f"""
        INSERT INTO extractors (
            id, name, description, input_params, input_mime_types, metadata_schemas, embedding_schemas
        ) VALUES (
            '{id}', '{description.name}', '{description.description}',
            '{input_params}', '{mime_types}',
            '{metadata_schemas}', '{embedding_schemas}'
        )
    """)

    conn.commit()
    conn.close()

def download_extractor(extractor_path):
    # Create extractor database if not exists
    create_extractor_db()

    console.print("[bold #4AA4F4]Downloading Extractor...[/]")
    extractor_path = extractor_path.removeprefix("hub://")
    fs = fsspec.filesystem("github", org="tensorlakeai", repo="indexify-extractors")

    base_extractor_path = os.path.basename(extractor_path)
    directory_path = os.path.join(
        os.path.expanduser("~"), ".indexify-extractors", base_extractor_path
    )

    fs.get(extractor_path, directory_path, recursive=True)
    install_dependencies(directory_path)

    # Store the extractor info in the database

    extractor_full_name = get_extractor_full_name(base_extractor_path)
    description = get_extractor_description(extractor_full_name)

    try:
        save_extractor_description(extractor_full_name, description)
    except Exception as e:
        print(f"Error saving extractor description: {e}")
        raise e

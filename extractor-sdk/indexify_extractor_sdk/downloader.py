import fsspec
import os
import ast
import subprocess
from rich.console import Console
from rich.panel import Panel

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

    message += f"indexify-extractor join {os.path.basename(directory_path)}.{find_extractor_subclasses(directory_path)}[/]"
    console.print(Panel(message, title="[bold magenta]Run the extractor[/]", expand=True))
    
    
def install_dependencies(directory_path):
    console.print("[bold #4AA4F4]Installing dependencies...[/]")
    venv_path = os.path.join(directory_path, "ve")
    requirements_path = os.path.join(directory_path, "requirements.txt")
    
    if not os.path.exists(requirements_path):
            raise ValueError("Unable to find requirements.txt")
        
    if os.environ.get("VIRTUAL_ENV"):
        # install requirements to current env
        subprocess.check_call([os.path.join(os.environ.get("VIRTUAL_ENV"), 'bin', 'pip'), 'install', '--no-deps', '-r', requirements_path])
    else:
        # create env and install requirements
        print("Creating virtual environment...")
        subprocess.check_call(['virtualenv', '-p', "python3.11", venv_path])
        pip_path = os.path.join(venv_path, 'bin', 'pip')

        subprocess.check_call([pip_path, 'install', '--no-deps', '-r', requirements_path])
        subprocess.check_call([pip_path, 'install', 'indexify-extractor-sdk'])

    # print instructions for next steps
    print_instructions(directory_path)
        

def download_extractor(extractor_path):
    console.print("[bold #4AA4F4]Downloading Extractor...[/]")
    extractor_path = extractor_path.removeprefix("hub://")
    fs = fsspec.filesystem("github", org="tensorlakeai", repo="indexify-extractors")
    directory_path = os.path.join(
        os.path.expanduser("~"), ".indexify-extractors", os.path.basename(extractor_path)
    )
    fs.get(extractor_path, directory_path, recursive=True)
    install_dependencies(directory_path)


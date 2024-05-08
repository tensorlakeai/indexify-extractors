import os
import sys
import importlib
from pathlib import Path

def load_indexify_extractors(base_path):
    # Resolve and expand the base path
    base_path = os.path.expanduser(base_path)
    base_dir = Path(base_path).resolve()

    if not base_dir.is_dir():
        raise ValueError(f"Invalid directory: {base_dir}")

    # Add the base path's parent to sys.path for dynamic imports
    sys.path.insert(0, str(base_dir.parent))

    # Traverse the base directory and register submodules
    for root, dirs, files in os.walk(base_dir):
        if "__init__.py" in files:
            rel_path = Path(root).relative_to(base_dir.parent)
            module_name = ".".join(rel_path.parts)

            # Import the submodule dynamically
            try:
                importlib.import_module(module_name)
                print(f"Successfully loaded: {module_name}")
            except Exception as e:
                print(f"Failed to load: {module_name}, due to {e}")

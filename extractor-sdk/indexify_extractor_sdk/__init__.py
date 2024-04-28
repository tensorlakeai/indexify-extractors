from .base_extractor import Content, Extractor, Feature, EmbeddingSchema, load_extractor
import os
import sys

sys.path.append(".")

extractors_path = os.path.join(os.path.expanduser("~"), ".indexify-extractors")
if not os.path.exists(extractors_path):
    os.mkdir(extractors_path)
all_subdirs = [d for d in os.listdir(extractors_path) ]
for dir in all_subdirs:
    print(f"Adding extractor dir: {dir} to PYTHONPATH")
    sys.path.append(os.path.join(extractors_path, dir))



__all__ = [
    "Content",
    "EmbeddingSchema",
    "Extractor",
    "Feature",
    "load_extractor",
]

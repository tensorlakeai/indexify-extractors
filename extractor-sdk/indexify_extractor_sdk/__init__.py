from .base_extractor import Content, Extractor, Feature, EmbeddingSchema, load_extractor
import os
import sys

sys.path.append(".")

extractors_path = os.path.join(os.path.expanduser("~"), ".indexify-extractors")
if not os.path.exists(extractors_path):
    os.mkdir(extractors_path)
sys.path.append(extractors_path)



__all__ = [
    "Content",
    "EmbeddingSchema",
    "Extractor",
    "Feature",
    "load_extractor",
]

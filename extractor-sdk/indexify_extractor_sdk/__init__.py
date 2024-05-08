from .base_extractor import Content, Extractor, Feature, EmbeddingSchema, load_extractor, EXTRACTORS_PATH, EXTRACTOR_MODULE_PATH
from .module_loader import load_indexify_extractors
import os
import sys

sys.path.append(".")

if not os.path.exists(EXTRACTORS_PATH):
    os.mkdir(EXTRACTORS_PATH)

if not os.path.exists(EXTRACTOR_MODULE_PATH):
    os.mkdir(EXTRACTOR_MODULE_PATH)

load_indexify_extractors(EXTRACTOR_MODULE_PATH)


__all__ = [
    "Content",
    "EmbeddingSchema",
    "Extractor",
    "Feature",
    "load_extractor",
]

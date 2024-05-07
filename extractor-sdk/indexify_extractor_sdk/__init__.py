from .base_extractor import Content, Extractor, Feature, EmbeddingSchema, load_extractor, EXTRACTORS_PATH
import os
import sys

sys.path.append(".")

if not os.path.exists(EXTRACTORS_PATH):
    os.mkdir(EXTRACTORS_PATH)


__all__ = [
    "Content",
    "EmbeddingSchema",
    "Extractor",
    "Feature",
    "load_extractor",
]

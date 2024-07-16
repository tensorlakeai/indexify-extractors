import os
import sys

from .base_extractor import (
    EXTRACTOR_MODULE_PATH,
    EXTRACTORS_PATH,
    Content,
    EmbeddingSchema,
    Extractor,
    Feature,
    load_extractor,
)
from .decorator import extractor
from .module_loader import load_indexify_extractors

sys.path.append(".")

if not os.path.exists(EXTRACTORS_PATH):
    os.mkdir(EXTRACTORS_PATH)

if not os.path.exists(EXTRACTOR_MODULE_PATH):
    os.mkdir(EXTRACTOR_MODULE_PATH)
    with open(os.path.join(EXTRACTOR_MODULE_PATH, "__init__.py"), "w") as f:
        f.write("")

load_indexify_extractors(EXTRACTOR_MODULE_PATH)


__all__ = [
    "Content",
    "EmbeddingSchema",
    "extractor",
    "Extractor",
    "Feature",
    "load_extractor",
]

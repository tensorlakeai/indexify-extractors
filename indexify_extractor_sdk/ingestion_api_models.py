from pydantic import BaseModel, Json
from typing import List, Dict


class ApiFeature(BaseModel):
    feature_type: str
    name: str
    data: Json


class ApiContent(BaseModel):
    mime: str
    bytes: List[int]
    features: List[ApiFeature] = []
    labels: Dict[str, str] = {}


class ExtractedContent(BaseModel):
    content_list: List[ApiContent]
    task_id: str
    namespace: str
    output_to_index_table_mapping: Dict[str, str]
    parent_content_id: str
    executor_id: str
    task_outcome: str
    extractor_binding: str

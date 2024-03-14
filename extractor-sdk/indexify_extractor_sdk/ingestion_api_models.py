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


class BeginExtractedContentIngest(BaseModel):
    task_id: str
    namespace: str
    output_to_index_table_mapping: Dict[str, str]
    parent_content_id: str
    executor_id: str
    task_outcome: str
    extraction_policy: str
    extractor: str


class ExtractedFeatures(BaseModel):
    content_id: str
    features: List[ApiFeature]


class ExtractedContent(BaseModel):
    content_list: List[ApiContent]


class FinishExtractedContentIngest(BaseModel):
    num_extracted_content: int


class ApiBeginExtractedContentIngest(BaseModel):
    BeginExtractedContentIngest: BeginExtractedContentIngest


class ApiExtractedContent(BaseModel):
    ExtractedContent: ExtractedContent


class ApiFinishExtractedContentIngest(BaseModel):
    FinishExtractedContentIngest: FinishExtractedContentIngest


class ApiExtractedFeatures(BaseModel):
    ExtractedFeatures: ExtractedFeatures

from pydantic import BaseModel, Json
from typing import List, Dict

####
{
    "content_list": [
        {
            "bytes": "string",
            "features": [
                {"data": "string", "feature_type": "Embedding", "name": "string"}
            ],
            "labels": {
                "additionalProp1": "string",
                "additionalProp2": "string",
                "additionalProp3": "string",
            },
            "mime": "string",
        }
    ],
    "executor_id": "string",
    "extractor_binding": "string",
    "namespace": "string",
    "output_to_index_table_mapping": {
        "additionalProp1": "string",
        "additionalProp2": "string",
        "additionalProp3": "string",
    },
    "parent_content_id": "string",
    "task_id": "string",
    "task_outcome": "Unknown",
}

####


class ApiFeature(BaseModel):
    feature_type: str
    name: str
    data: Json


class ApiContent(BaseModel):
    mime: str
    bytes: bytes
    features: List[ApiFeature]
    labels: Dict[str, str]

    @classmethod
    def from_text(cls, text: str, features: list = [], labels: dict = {}):
        return cls(
            content_type="text/plain",
            data=bytes(text, "utf-8"),
            features=features,
            labels=labels,
        )


class ExtractedContent(BaseModel):
    content_list: List[ApiContent]
    task_id: str
    namespace: str
    output_to_index_table_mapping: Dict[str, str]
    parent_content_id: str
    executor_id: str
    task_outcome: str
    extractor_binding: str

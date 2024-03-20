from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Type, Optional
import json
from importlib import import_module
from typing import get_type_hints, Literal, Union, Dict

from pydantic import BaseModel, Json
from genson import SchemaBuilder
import requests
import os
import tempfile


class EmbeddingSchema(BaseModel):
    dim: int
    distance: str


class Embedding(BaseModel):
    values: List[float]
    distance: str


class ExtractorDescription(BaseModel):
    name: str
    version: str
    description: str
    python_dependencies: List[str]
    system_dependencies: List[str]
    embedding_schemas: dict[str, EmbeddingSchema]
    metadata_schemas: dict[str, Dict]
    input_params: Optional[str]
    input_mime_types: List[str]


class Feature(BaseModel):
    feature_type: Literal["embedding", "metadata"]
    name: str
    value: Json

    @classmethod
    def embedding(cls, values: List[float], name: str = "embedding", distance="cosine"):
        embedding = Embedding(values=values, distance=distance)
        return cls(
            feature_type="embedding",
            name=name,
            value=json.dumps(embedding.model_dump_json()),
        )

    @classmethod
    def metadata(cls, value: Json, name: str = "metadata"):
        return cls(feature_type="metadata", name=name, value=json.dumps(value))

    def get_schema(self) -> dict:
        if self.feature_type == "embedding":
            embedding_value: Embedding = Embedding.model_validate_json(self.value)
            return EmbeddingSchema(
                dim=len(embedding_value.values), distance=embedding_value.distance
            ).model_dump()
        else:
            schema_builder = SchemaBuilder()
            schema_builder.add_object(self.value)
            metadata_schema = schema_builder.to_schema()
            schema = {}
            for (k, v) in metadata_schema["properties"].items():
                schema[k] = {"type": v["type"]}
            return schema


class Content(BaseModel):
    content_type: Optional[str]
    data: bytes
    features: List[Feature] = []
    labels: Dict[str, str] = {}

    @classmethod
    def from_text(
        cls, text: str, features: List[Feature] = [], labels: Dict[str, str] = {}
    ):
        return cls(
            content_type="text/plain",
            data=bytes(text, "utf-8"),
            features=features,
            labels=labels,
        )

    @classmethod
    def from_file(cls, path: str):
        import mimetypes

        m, _ = mimetypes.guess_type(path)
        with open(path, "rb") as f:
            return cls(content_type=m, data=f.read())


class Extractor(ABC):
    name: str = ""

    version: str = "0.0.0"

    system_dependencies: List[str] = []

    python_dependencies: List[str] = []

    description: str = ""

    input_mime_types = ["text/plain"]

    @abstractmethod
    def extract(
        self, content: Content, params: Type[BaseModel] = None
    ) -> List[Union[Feature, Content]]:
        """
        Extracts information from the content. Returns a list of features to add
        to the content.
        It can also return a list of Content objects, which will be added to storage
        and any extraction policies defined will be applied to them.
        """
        pass

    @abstractmethod
    def sample_input(self) -> Tuple[Content, Type[BaseModel]]:
        pass

    def extract_sample_input(self) -> List[Union[Feature, Content]]:
        input = self.sample_input()
        return self.extract(*input)

    def _download_file(self, url, filename):
        if os.path.exists(filename):
            # file exists skip
            return
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading the file: {e}")


    def sample_mp3(self, features: List[Feature] = []) -> Content:
        file_name = "sample.mp3"
        self._download_file(
            "https://extractor-files.diptanu-6d5.workers.dev/sample-000009.mp3",
            file_name,
        )
        f = open(file_name, "rb")
        return Content(content_type="audio/mpeg", data=f.read(), features=features)

    def sample_mp4(self, features: List[Feature] = []) -> Content:
        file_name="sample.mp4"
        self._download_file(
            "https://extractor-files.diptanu-6d5.workers.dev/sample.mp4",
            file_name,
        )
        f = open(file_name, "rb")
        return Content(content_type="video/mp4", data=f.read(), features=features)

    def sample_jpg(self, features: List[Feature] = []) -> Content:
        file_name = "sample.jpg"
        self._download_file(
            "https://extractor-files.diptanu-6d5.workers.dev/people-standing.jpg",
            file_name,
        )
        f = open(file_name, "rb")
        return Content(content_type="image/jpg", data=f.read(), features=features)

    def sample_invoice_jpg(self, features: List[Feature] = []) -> Content:
        file_name = "sample.jpg"
        self._download_file(
            "https://extractor-files.diptanu-6d5.workers.dev/invoice-example.jpg",
            file_name,
        )
        f = open(file_name, "rb")
        return Content(content_type="image/jpg", data=f.read(), features=features)

    def sample_invoice_pdf(self, features: List[Feature] = []) -> Content:
        file_name = "sample.pdf"
        self._download_file(
            "https://extractor-files.diptanu-6d5.workers.dev/invoice-example.pdf",
            file_name,
        )
        f = open(file_name, "rb")
        return Content(content_type="application/pdf", data=f.read(), features=features)
    
    def sample_image_based_pdf(self, features: List[Feature] = []) -> Content:
        file_name = "sample.pdf"
        self._download_file(
            "https://extractor-files.diptanu-6d5.workers.dev/image-based.pdf",
            file_name,
        )
        f = open(file_name, "rb")
        return Content(content_type="application/pdf", data=f.read(), features=features)
    
    def sample_scientific_pdf(self, features: List[Feature] = []) -> Content:
        file_name = "sample.pdf"
        self._download_file(
            "https://extractor-files.diptanu-6d5.workers.dev/scientific-paper-example.pdf",
            file_name,
        )
        f = open(file_name, "rb")
        return Content(content_type="application/pdf", data=f.read(), features=features)


class ExtractorWrapper:
    def __init__(self, module_name: str, class_name: str):
        module = import_module(module_name)
        cls = getattr(module, class_name)
        self._instance: Extractor = cls()
        self._param_cls = get_type_hints(cls.extract).get("params", None)

    def extract(self, content: Content, params: Json) -> List[Content]:
        params = "{}" if params is None else params
        params_dict = json.loads(params)
        param_instance = (
            self._param_cls.model_validate(params_dict)
            if self._param_cls != type(None)
            else None
        )
        return self._instance.extract(content, param_instance)

    def describe(self, input_params: Type[BaseModel] = None) -> ExtractorDescription:
        s_input = self._instance.sample_input()
        if type(s_input) == tuple:
            (s_input, input_params) = s_input
        # Come back to this when we can support schemas based on user defined input params
        if input_params is None:
            input_params = self._param_cls() if self._param_cls else None
        outputs: Union[List[Feature], List[Content]] = self._instance.extract(
            s_input, input_params
        )
        embedding_schemas = {}
        metadata_schemas = {}
        json_schema = (
            None
            if self._param_cls == type(None)
            else self._param_cls.model_json_schema()
        )
        if json_schema:
            json_schema["additionalProperties"] = False
        for out in outputs:
            features = out.features if type(out) == Content else [out]
            for feature in features:
                if feature.feature_type == "embedding":
                    embedding_value: Embedding = Embedding.model_validate_json(
                        feature.value
                    )
                    embedding_schema = EmbeddingSchema(
                        dim=len(embedding_value.values),
                        distance=embedding_value.distance,
                    )
                    embedding_schemas[feature.name] = embedding_schema
                elif feature.feature_type == "metadata":
                    metadata_schemas[feature.name] = feature.get_schema()
        return ExtractorDescription(
            name=self._instance.name,
            version=self._instance.version,
            description=self._instance.description,
            python_dependencies=self._instance.python_dependencies,
            system_dependencies=self._instance.system_dependencies,
            embedding_schemas=embedding_schemas,
            metadata_schemas=metadata_schemas,
            input_mime_types=self._instance.input_mime_types,
            input_params=json.dumps(json_schema),
        )

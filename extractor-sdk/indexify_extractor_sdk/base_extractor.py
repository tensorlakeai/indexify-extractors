from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Type, Optional
import json
from importlib import import_module
from typing import get_type_hints, Literal, Union, Dict

from pydantic import BaseModel, Json, Field
from genson import SchemaBuilder
import requests
import os


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
    comment: Optional[Json] = Field(default=None)

    @classmethod
    def embedding(cls, values: List[float], name: str = "embedding", distance="cosine"):
        embedding = Embedding(values=values, distance=distance)
        return cls(
            feature_type="embedding",
            name=name,
            value=embedding.model_dump_json(),
            comment=None
        )

    @classmethod
    def metadata(cls, value: Json, comment: Json = None, name: str = "metadata"):
        value = json.dumps(value)
        comment = json.dumps(comment) if comment is not None else None
        return cls(feature_type="metadata", name=name, value=value)

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
            for k, v in metadata_schema["properties"].items():
                schema[k] = {"type": v["type"]}

                if self.comment is not None and k in self.comment:
                    schema[k]["comment"] = self.comment[k]
            
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
        file_name = "sample.mp4"
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
    
    def sample_text(self, features: List[Feature] = []) -> Content:
        article = """New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York. A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband. Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared "I do" five more times, sometimes only within two weeks of each other. In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her "first and only" marriage. Barrientos, now 39, is facing two criminal counts of "offering a false instrument for filing in the first degree," referring to her false statements on the 2010 marriage license application, according to court documents. Prosecutors said the marriages were part of an immigration scam. On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further. After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002. All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say. Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages. Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted. The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s Investigation Division. Seven of the men are from so-called "red-flagged" countries, including Egypt, Turkey, Georgia, Pakistan and Mali. Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force. If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18."""
        return Content(content_type="text/plain", data=article, features=features)
    
    def sample_html(self, features: List[Feature] = []) -> Content:
        file_name = "sample.html"
        self._download_file(
            "https://extractor-files.diptanu-6d5.workers.dev/sample.html",
            file_name,
        )
        f = open(file_name, "rb")
        return Content(content_type="text/html", data=f.read(), features=features)


def load_extractor(name: str) -> Tuple[Extractor, Type[BaseModel]]:
    module_name, class_name = name.split(":")
    wrapper = ExtractorWrapper(module_name, class_name)
    return (wrapper._instance, wrapper._param_cls)

class ExtractorWrapper:
    def __init__(self, module_name: str, class_name: str):
        module = import_module(module_name)
        cls = getattr(module, class_name)
        self._instance: Extractor = cls()
        self._param_cls = get_type_hints(cls.extract).get("params", None)
        extract_batch = getattr(self._instance, "extract_batch", None)
        self._has_batch_extract = True if callable(extract_batch) else False

    def _param_from_json(self, param: Json) -> BaseModel:
        param_dict = json.loads(param) if param is not None else {}
        return self._param_cls.model_validate(param_dict) if self._param_cls is not None else None

    def extract_batch(
        self, content_list: Dict[str, Content], input_params: Dict[str, Json]
    ) -> Dict[str, List[Union[Feature, Content]]]:
        if self._has_batch_extract:
            task_ids = []
            task_contents = []
            params = []
            for task_id, content in content_list.items():
                param_instance = self._param_from_json(input_params.get(task_id, None))
                params.append(param_instance)
                task_ids.append(task_id)
                task_contents.append(content)
            result = self._instance.extract_batch(task_contents, params)
            out: Dict[str, List[Union[Feature, Content]]] = {}
            for i, extractor_out in enumerate(result):
                out[task_ids[i]] = extractor_out
            return out
        out = {}
        for task_id, content in content_list.items():
            param_instance = self._param_from_json(input_params.get(task_id, None))
            out[task_id] = self._instance.extract(content, param_instance)
        return out

    def describe(self, input_params: Type[BaseModel] = None) -> ExtractorDescription:
        s_input = self._instance.sample_input()
        if type(s_input) == tuple:
            (s_input, input_params) = s_input
        # Come back to this when we can support schemas based on user defined input params
        if input_params is None:
            input_params = (
                self._param_cls().model_dump_json()
                if self._param_cls is not None
                else None
            )
        outputs: Dict[str, List[Union[Feature, Content]]] = self.extract_batch(
            {"task_id": s_input}, {"task_id": input_params},
        )
        embedding_schemas = {}
        metadata_schemas = {}
        json_schema = (
            self._param_cls.model_json_schema() if self._param_cls is not None else None
        )
        output = outputs["task_id"]
        for out in output:
            features = out.features if type(out) == Content else [out]
            for feature in features:
                if feature.feature_type == "embedding":
                    embedding_value: Embedding = Embedding.model_validate(feature.value)
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

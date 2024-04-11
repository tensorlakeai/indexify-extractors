from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskOutcome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[TaskOutcome]
    FAILED: _ClassVar[TaskOutcome]
    SUCCESS: _ClassVar[TaskOutcome]
UNKNOWN: TaskOutcome
FAILED: TaskOutcome
SUCCESS: TaskOutcome

class GetContentMetadataRequest(_message.Message):
    __slots__ = ("content_list",)
    CONTENT_LIST_FIELD_NUMBER: _ClassVar[int]
    content_list: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, content_list: _Optional[_Iterable[str]] = ...) -> None: ...

class GetContentMetadataResponse(_message.Message):
    __slots__ = ("content_list",)
    CONTENT_LIST_FIELD_NUMBER: _ClassVar[int]
    content_list: _containers.RepeatedCompositeFieldContainer[ContentMetadata]
    def __init__(self, content_list: _Optional[_Iterable[_Union[ContentMetadata, _Mapping]]] = ...) -> None: ...

class UpdateTaskRequest(_message.Message):
    __slots__ = ("executor_id", "task_id", "outcome", "content_list", "content_id", "extraction_policy_name")
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_LIST_FIELD_NUMBER: _ClassVar[int]
    CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
    EXTRACTION_POLICY_NAME_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    task_id: str
    outcome: TaskOutcome
    content_list: _containers.RepeatedCompositeFieldContainer[ContentMetadata]
    content_id: str
    extraction_policy_name: str
    def __init__(self, executor_id: _Optional[str] = ..., task_id: _Optional[str] = ..., outcome: _Optional[_Union[TaskOutcome, str]] = ..., content_list: _Optional[_Iterable[_Union[ContentMetadata, _Mapping]]] = ..., content_id: _Optional[str] = ..., extraction_policy_name: _Optional[str] = ...) -> None: ...

class ListStateChangesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StateChange(_message.Message):
    __slots__ = ("id", "object_id", "change_type", "created_at", "processed_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    object_id: str
    change_type: str
    created_at: int
    processed_at: int
    def __init__(self, id: _Optional[str] = ..., object_id: _Optional[str] = ..., change_type: _Optional[str] = ..., created_at: _Optional[int] = ..., processed_at: _Optional[int] = ...) -> None: ...

class ListStateChangesResponse(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: _containers.RepeatedCompositeFieldContainer[StateChange]
    def __init__(self, changes: _Optional[_Iterable[_Union[StateChange, _Mapping]]] = ...) -> None: ...

class ListTasksRequest(_message.Message):
    __slots__ = ("namespace", "extraction_policy")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    EXTRACTION_POLICY_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    extraction_policy: str
    def __init__(self, namespace: _Optional[str] = ..., extraction_policy: _Optional[str] = ...) -> None: ...

class ListTasksResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    def __init__(self, tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ...) -> None: ...

class UpdateTaskResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetExtractorCoordinatesRequest(_message.Message):
    __slots__ = ("extractor",)
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    extractor: str
    def __init__(self, extractor: _Optional[str] = ...) -> None: ...

class GetExtractorCoordinatesResponse(_message.Message):
    __slots__ = ("addrs",)
    ADDRS_FIELD_NUMBER: _ClassVar[int]
    addrs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, addrs: _Optional[_Iterable[str]] = ...) -> None: ...

class ListIndexesRequest(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    def __init__(self, namespace: _Optional[str] = ...) -> None: ...

class ListIndexesResponse(_message.Message):
    __slots__ = ("indexes",)
    INDEXES_FIELD_NUMBER: _ClassVar[int]
    indexes: _containers.RepeatedCompositeFieldContainer[Index]
    def __init__(self, indexes: _Optional[_Iterable[_Union[Index, _Mapping]]] = ...) -> None: ...

class GetIndexRequest(_message.Message):
    __slots__ = ("namespace", "name")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    name: str
    def __init__(self, namespace: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class GetIndexResponse(_message.Message):
    __slots__ = ("index",)
    INDEX_FIELD_NUMBER: _ClassVar[int]
    index: Index
    def __init__(self, index: _Optional[_Union[Index, _Mapping]] = ...) -> None: ...

class CreateIndexRequest(_message.Message):
    __slots__ = ("index",)
    INDEX_FIELD_NUMBER: _ClassVar[int]
    index: Index
    def __init__(self, index: _Optional[_Union[Index, _Mapping]] = ...) -> None: ...

class CreateIndexResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Index(_message.Message):
    __slots__ = ("name", "namespace", "table_name", "schema", "extraction_policy", "extractor")
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    EXTRACTION_POLICY_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    table_name: str
    schema: str
    extraction_policy: str
    extractor: str
    def __init__(self, name: _Optional[str] = ..., namespace: _Optional[str] = ..., table_name: _Optional[str] = ..., schema: _Optional[str] = ..., extraction_policy: _Optional[str] = ..., extractor: _Optional[str] = ...) -> None: ...

class Embedding(_message.Message):
    __slots__ = ("embedding",)
    EMBEDDING_FIELD_NUMBER: _ClassVar[int]
    embedding: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, embedding: _Optional[_Iterable[float]] = ...) -> None: ...

class Attributes(_message.Message):
    __slots__ = ("attributes",)
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    attributes: str
    def __init__(self, attributes: _Optional[str] = ...) -> None: ...

class Feature(_message.Message):
    __slots__ = ("name", "embedding", "attributes")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    embedding: Embedding
    attributes: Attributes
    def __init__(self, name: _Optional[str] = ..., embedding: _Optional[_Union[Embedding, _Mapping]] = ..., attributes: _Optional[_Union[Attributes, _Mapping]] = ...) -> None: ...

class Content(_message.Message):
    __slots__ = ("mime", "data", "features")
    MIME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    mime: str
    data: bytes
    features: _containers.RepeatedCompositeFieldContainer[Feature]
    def __init__(self, mime: _Optional[str] = ..., data: _Optional[bytes] = ..., features: _Optional[_Iterable[_Union[Feature, _Mapping]]] = ...) -> None: ...

class RegisterExecutorRequest(_message.Message):
    __slots__ = ("executor_id", "addr", "extractor")
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ADDR_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    addr: str
    extractor: Extractor
    def __init__(self, executor_id: _Optional[str] = ..., addr: _Optional[str] = ..., extractor: _Optional[_Union[Extractor, _Mapping]] = ...) -> None: ...

class RegisterExecutorResponse(_message.Message):
    __slots__ = ("executor_id",)
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    def __init__(self, executor_id: _Optional[str] = ...) -> None: ...

class RegisterIngestionServerRequest(_message.Message):
    __slots__ = ("ingestion_server_id", "addr")
    INGESTION_SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    ADDR_FIELD_NUMBER: _ClassVar[int]
    ingestion_server_id: str
    addr: str
    def __init__(self, ingestion_server_id: _Optional[str] = ..., addr: _Optional[str] = ...) -> None: ...

class RegisterIngestionServerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GCTaskAcknowledgement(_message.Message):
    __slots__ = ("task_id", "completed", "ingestion_server_id")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    INGESTION_SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    completed: bool
    ingestion_server_id: str
    def __init__(self, task_id: _Optional[str] = ..., completed: bool = ..., ingestion_server_id: _Optional[str] = ...) -> None: ...

class GCTask(_message.Message):
    __slots__ = ("task_id", "namespace", "content_id", "output_tables", "blob_store_path")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_TABLES_FIELD_NUMBER: _ClassVar[int]
    BLOB_STORE_PATH_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    namespace: str
    content_id: str
    output_tables: _containers.RepeatedScalarFieldContainer[str]
    blob_store_path: str
    def __init__(self, task_id: _Optional[str] = ..., namespace: _Optional[str] = ..., content_id: _Optional[str] = ..., output_tables: _Optional[_Iterable[str]] = ..., blob_store_path: _Optional[str] = ...) -> None: ...

class HeartbeatRequest(_message.Message):
    __slots__ = ("executor_id", "pending_tasks")
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    PENDING_TASKS_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    pending_tasks: int
    def __init__(self, executor_id: _Optional[str] = ..., pending_tasks: _Optional[int] = ...) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ("executor_id", "tasks")
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    def __init__(self, executor_id: _Optional[str] = ..., tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("id", "extractor", "namespace", "content_metadata", "input_params", "extraction_policy_id", "output_index_mapping", "outcome", "index_tables")
    class OutputIndexMappingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_METADATA_FIELD_NUMBER: _ClassVar[int]
    INPUT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    EXTRACTION_POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_INDEX_MAPPING_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    INDEX_TABLES_FIELD_NUMBER: _ClassVar[int]
    id: str
    extractor: str
    namespace: str
    content_metadata: ContentMetadata
    input_params: str
    extraction_policy_id: str
    output_index_mapping: _containers.ScalarMap[str, str]
    outcome: TaskOutcome
    index_tables: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., extractor: _Optional[str] = ..., namespace: _Optional[str] = ..., content_metadata: _Optional[_Union[ContentMetadata, _Mapping]] = ..., input_params: _Optional[str] = ..., extraction_policy_id: _Optional[str] = ..., output_index_mapping: _Optional[_Mapping[str, str]] = ..., outcome: _Optional[_Union[TaskOutcome, str]] = ..., index_tables: _Optional[_Iterable[str]] = ...) -> None: ...

class ListExtractorsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListExtractorsResponse(_message.Message):
    __slots__ = ("extractors",)
    EXTRACTORS_FIELD_NUMBER: _ClassVar[int]
    extractors: _containers.RepeatedCompositeFieldContainer[Extractor]
    def __init__(self, extractors: _Optional[_Iterable[_Union[Extractor, _Mapping]]] = ...) -> None: ...

class Extractor(_message.Message):
    __slots__ = ("name", "description", "input_params", "embedding_schemas", "metadata_schemas", "input_mime_types")
    class EmbeddingSchemasEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class MetadataSchemasEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    METADATA_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    INPUT_MIME_TYPES_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    input_params: str
    embedding_schemas: _containers.ScalarMap[str, str]
    metadata_schemas: _containers.ScalarMap[str, str]
    input_mime_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., input_params: _Optional[str] = ..., embedding_schemas: _Optional[_Mapping[str, str]] = ..., metadata_schemas: _Optional[_Mapping[str, str]] = ..., input_mime_types: _Optional[_Iterable[str]] = ...) -> None: ...

class GetNamespaceRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetNamespaceResponse(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: Namespace
    def __init__(self, namespace: _Optional[_Union[Namespace, _Mapping]] = ...) -> None: ...

class ListContentRequest(_message.Message):
    __slots__ = ("namespace", "source", "parent_id", "labels_eq")
    class LabelsEqEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_EQ_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    source: str
    parent_id: str
    labels_eq: _containers.ScalarMap[str, str]
    def __init__(self, namespace: _Optional[str] = ..., source: _Optional[str] = ..., parent_id: _Optional[str] = ..., labels_eq: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ListContentResponse(_message.Message):
    __slots__ = ("content_list",)
    CONTENT_LIST_FIELD_NUMBER: _ClassVar[int]
    content_list: _containers.RepeatedCompositeFieldContainer[ContentMetadata]
    def __init__(self, content_list: _Optional[_Iterable[_Union[ContentMetadata, _Mapping]]] = ...) -> None: ...

class ListExtractionPoliciesRequest(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    def __init__(self, namespace: _Optional[str] = ...) -> None: ...

class ListExtractionPoliciesResponse(_message.Message):
    __slots__ = ("policies",)
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    policies: _containers.RepeatedCompositeFieldContainer[ExtractionPolicy]
    def __init__(self, policies: _Optional[_Iterable[_Union[ExtractionPolicy, _Mapping]]] = ...) -> None: ...

class CreateNamespaceRequest(_message.Message):
    __slots__ = ("name", "policies")
    NAME_FIELD_NUMBER: _ClassVar[int]
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    name: str
    policies: _containers.RepeatedCompositeFieldContainer[ExtractionPolicy]
    def __init__(self, name: _Optional[str] = ..., policies: _Optional[_Iterable[_Union[ExtractionPolicy, _Mapping]]] = ...) -> None: ...

class CreateNamespaceResponse(_message.Message):
    __slots__ = ("name", "created_at")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    created_at: int
    def __init__(self, name: _Optional[str] = ..., created_at: _Optional[int] = ...) -> None: ...

class ListNamespaceRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNamespaceResponse(_message.Message):
    __slots__ = ("namespaces",)
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    namespaces: _containers.RepeatedCompositeFieldContainer[Namespace]
    def __init__(self, namespaces: _Optional[_Iterable[_Union[Namespace, _Mapping]]] = ...) -> None: ...

class ExtractionPolicy(_message.Message):
    __slots__ = ("id", "extractor", "name", "input_params", "filters", "content_source")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    extractor: str
    name: str
    input_params: str
    filters: _containers.ScalarMap[str, str]
    content_source: str
    def __init__(self, id: _Optional[str] = ..., extractor: _Optional[str] = ..., name: _Optional[str] = ..., input_params: _Optional[str] = ..., filters: _Optional[_Mapping[str, str]] = ..., content_source: _Optional[str] = ...) -> None: ...

class ExtractionPolicyRequest(_message.Message):
    __slots__ = ("namespace", "extractor", "name", "input_params", "filters", "content_source", "created_at")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    extractor: str
    name: str
    input_params: str
    filters: _containers.ScalarMap[str, str]
    content_source: str
    created_at: int
    def __init__(self, namespace: _Optional[str] = ..., extractor: _Optional[str] = ..., name: _Optional[str] = ..., input_params: _Optional[str] = ..., filters: _Optional[_Mapping[str, str]] = ..., content_source: _Optional[str] = ..., created_at: _Optional[int] = ...) -> None: ...

class ExtractionPolicyResponse(_message.Message):
    __slots__ = ("created_at", "extractor", "extraction_policy", "index_name_table_mapping", "output_index_name_mapping")
    class IndexNameTableMappingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class OutputIndexNameMappingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    EXTRACTION_POLICY_FIELD_NUMBER: _ClassVar[int]
    INDEX_NAME_TABLE_MAPPING_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_INDEX_NAME_MAPPING_FIELD_NUMBER: _ClassVar[int]
    created_at: int
    extractor: Extractor
    extraction_policy: ExtractionPolicy
    index_name_table_mapping: _containers.ScalarMap[str, str]
    output_index_name_mapping: _containers.ScalarMap[str, str]
    def __init__(self, created_at: _Optional[int] = ..., extractor: _Optional[_Union[Extractor, _Mapping]] = ..., extraction_policy: _Optional[_Union[ExtractionPolicy, _Mapping]] = ..., index_name_table_mapping: _Optional[_Mapping[str, str]] = ..., output_index_name_mapping: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ContentMetadata(_message.Message):
    __slots__ = ("id", "file_name", "parent_id", "mime", "labels", "storage_url", "created_at", "namespace", "source", "size_bytes")
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    MIME_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    STORAGE_URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    id: str
    file_name: str
    parent_id: str
    mime: str
    labels: _containers.ScalarMap[str, str]
    storage_url: str
    created_at: int
    namespace: str
    source: str
    size_bytes: int
    def __init__(self, id: _Optional[str] = ..., file_name: _Optional[str] = ..., parent_id: _Optional[str] = ..., mime: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., storage_url: _Optional[str] = ..., created_at: _Optional[int] = ..., namespace: _Optional[str] = ..., source: _Optional[str] = ..., size_bytes: _Optional[int] = ...) -> None: ...

class CreateContentRequest(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: ContentMetadata
    def __init__(self, content: _Optional[_Union[ContentMetadata, _Mapping]] = ...) -> None: ...

class CreateContentResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class TombstoneContentRequest(_message.Message):
    __slots__ = ("namespace", "content_ids")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, namespace: _Optional[str] = ..., content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class TombstoneContentResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Namespace(_message.Message):
    __slots__ = ("name", "policies")
    NAME_FIELD_NUMBER: _ClassVar[int]
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    name: str
    policies: _containers.RepeatedCompositeFieldContainer[ExtractionPolicy]
    def __init__(self, name: _Optional[str] = ..., policies: _Optional[_Iterable[_Union[ExtractionPolicy, _Mapping]]] = ...) -> None: ...

class GetSchemaRequest(_message.Message):
    __slots__ = ("namespace", "content_source")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    content_source: str
    def __init__(self, namespace: _Optional[str] = ..., content_source: _Optional[str] = ...) -> None: ...

class GetSchemaResponse(_message.Message):
    __slots__ = ("schema",)
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    schema: StructuredDataSchema
    def __init__(self, schema: _Optional[_Union[StructuredDataSchema, _Mapping]] = ...) -> None: ...

class StructuredDataSchema(_message.Message):
    __slots__ = ("columns", "content_source")
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    columns: str
    content_source: str
    def __init__(self, columns: _Optional[str] = ..., content_source: _Optional[str] = ...) -> None: ...

class GetAllSchemaRequest(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    def __init__(self, namespace: _Optional[str] = ...) -> None: ...

class GetAllSchemaResponse(_message.Message):
    __slots__ = ("schemas",)
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    schemas: _containers.RepeatedCompositeFieldContainer[StructuredDataSchema]
    def __init__(self, schemas: _Optional[_Iterable[_Union[StructuredDataSchema, _Mapping]]] = ...) -> None: ...

class GetRaftMetricsSnapshotRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Uint64List(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, values: _Optional[_Iterable[int]] = ...) -> None: ...

class RaftMetricsSnapshotResponse(_message.Message):
    __slots__ = ("fail_connect_to_peer", "sent_bytes", "recv_bytes", "sent_failures", "snapshot_send_success", "snapshot_send_failure", "snapshot_recv_success", "snapshot_recv_failure", "snapshot_send_inflights", "snapshot_recv_inflights", "snapshot_sent_seconds", "snapshot_recv_seconds", "snapshot_size", "last_snapshot_creation_time_millis", "running_state_ok", "id", "current_term", "vote", "last_log_index", "current_leader")
    class FailConnectToPeerEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SentBytesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class RecvBytesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SentFailuresEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SnapshotSendSuccessEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SnapshotSendFailureEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SnapshotRecvSuccessEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SnapshotRecvFailureEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SnapshotSendInflightsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SnapshotRecvInflightsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SnapshotSentSecondsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Uint64List
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Uint64List, _Mapping]] = ...) -> None: ...
    class SnapshotRecvSecondsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Uint64List
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Uint64List, _Mapping]] = ...) -> None: ...
    FAIL_CONNECT_TO_PEER_FIELD_NUMBER: _ClassVar[int]
    SENT_BYTES_FIELD_NUMBER: _ClassVar[int]
    RECV_BYTES_FIELD_NUMBER: _ClassVar[int]
    SENT_FAILURES_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_SEND_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_SEND_FAILURE_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_RECV_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_RECV_FAILURE_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_SEND_INFLIGHTS_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_RECV_INFLIGHTS_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_SENT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_RECV_SECONDS_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_SIZE_FIELD_NUMBER: _ClassVar[int]
    LAST_SNAPSHOT_CREATION_TIME_MILLIS_FIELD_NUMBER: _ClassVar[int]
    RUNNING_STATE_OK_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TERM_FIELD_NUMBER: _ClassVar[int]
    VOTE_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    CURRENT_LEADER_FIELD_NUMBER: _ClassVar[int]
    fail_connect_to_peer: _containers.ScalarMap[str, int]
    sent_bytes: _containers.ScalarMap[str, int]
    recv_bytes: _containers.ScalarMap[str, int]
    sent_failures: _containers.ScalarMap[str, int]
    snapshot_send_success: _containers.ScalarMap[str, int]
    snapshot_send_failure: _containers.ScalarMap[str, int]
    snapshot_recv_success: _containers.ScalarMap[str, int]
    snapshot_recv_failure: _containers.ScalarMap[str, int]
    snapshot_send_inflights: _containers.ScalarMap[str, int]
    snapshot_recv_inflights: _containers.ScalarMap[str, int]
    snapshot_sent_seconds: _containers.MessageMap[str, Uint64List]
    snapshot_recv_seconds: _containers.MessageMap[str, Uint64List]
    snapshot_size: _containers.RepeatedScalarFieldContainer[int]
    last_snapshot_creation_time_millis: int
    running_state_ok: bool
    id: int
    current_term: int
    vote: int
    last_log_index: int
    current_leader: int
    def __init__(self, fail_connect_to_peer: _Optional[_Mapping[str, int]] = ..., sent_bytes: _Optional[_Mapping[str, int]] = ..., recv_bytes: _Optional[_Mapping[str, int]] = ..., sent_failures: _Optional[_Mapping[str, int]] = ..., snapshot_send_success: _Optional[_Mapping[str, int]] = ..., snapshot_send_failure: _Optional[_Mapping[str, int]] = ..., snapshot_recv_success: _Optional[_Mapping[str, int]] = ..., snapshot_recv_failure: _Optional[_Mapping[str, int]] = ..., snapshot_send_inflights: _Optional[_Mapping[str, int]] = ..., snapshot_recv_inflights: _Optional[_Mapping[str, int]] = ..., snapshot_sent_seconds: _Optional[_Mapping[str, Uint64List]] = ..., snapshot_recv_seconds: _Optional[_Mapping[str, Uint64List]] = ..., snapshot_size: _Optional[_Iterable[int]] = ..., last_snapshot_creation_time_millis: _Optional[int] = ..., running_state_ok: bool = ..., id: _Optional[int] = ..., current_term: _Optional[int] = ..., vote: _Optional[int] = ..., last_log_index: _Optional[int] = ..., current_leader: _Optional[int] = ...) -> None: ...

class GetAllTaskAssignmentRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaskAssignments(_message.Message):
    __slots__ = ("assignments",)
    class AssignmentsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    assignments: _containers.ScalarMap[str, str]
    def __init__(self, assignments: _Optional[_Mapping[str, str]] = ...) -> None: ...

from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

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
    def __init__(
        self,
        content_list: _Optional[_Iterable[_Union[ContentMetadata, _Mapping]]] = ...,
    ) -> None: ...

class UpdateTaskRequest(_message.Message):
    __slots__ = ("executor_id", "task_id", "outcome", "content_list")
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_LIST_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    task_id: str
    outcome: TaskOutcome
    content_list: _containers.RepeatedCompositeFieldContainer[ContentMetadata]
    def __init__(
        self,
        executor_id: _Optional[str] = ...,
        task_id: _Optional[str] = ...,
        outcome: _Optional[_Union[TaskOutcome, str]] = ...,
        content_list: _Optional[_Iterable[_Union[ContentMetadata, _Mapping]]] = ...,
    ) -> None: ...

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
    def __init__(
        self,
        id: _Optional[str] = ...,
        object_id: _Optional[str] = ...,
        change_type: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        processed_at: _Optional[int] = ...,
    ) -> None: ...

class ListStateChangesResponse(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: _containers.RepeatedCompositeFieldContainer[StateChange]
    def __init__(
        self, changes: _Optional[_Iterable[_Union[StateChange, _Mapping]]] = ...
    ) -> None: ...

class ListTasksRequest(_message.Message):
    __slots__ = ("namespace", "extractor_binding")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_BINDING_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    extractor_binding: str
    def __init__(
        self, namespace: _Optional[str] = ..., extractor_binding: _Optional[str] = ...
    ) -> None: ...

class ListTasksResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    def __init__(
        self, tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ...
    ) -> None: ...

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
    def __init__(
        self, indexes: _Optional[_Iterable[_Union[Index, _Mapping]]] = ...
    ) -> None: ...

class GetIndexRequest(_message.Message):
    __slots__ = ("namespace", "name")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    name: str
    def __init__(
        self, namespace: _Optional[str] = ..., name: _Optional[str] = ...
    ) -> None: ...

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
    __slots__ = (
        "name",
        "namespace",
        "table_name",
        "schema",
        "extractor_binding",
        "extractor",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_BINDING_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    table_name: str
    schema: str
    extractor_binding: str
    extractor: str
    def __init__(
        self,
        name: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        table_name: _Optional[str] = ...,
        schema: _Optional[str] = ...,
        extractor_binding: _Optional[str] = ...,
        extractor: _Optional[str] = ...,
    ) -> None: ...

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
    def __init__(
        self,
        name: _Optional[str] = ...,
        embedding: _Optional[_Union[Embedding, _Mapping]] = ...,
        attributes: _Optional[_Union[Attributes, _Mapping]] = ...,
    ) -> None: ...

class Content(_message.Message):
    __slots__ = ("mime", "data", "features")
    MIME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    mime: str
    data: bytes
    features: _containers.RepeatedCompositeFieldContainer[Feature]
    def __init__(
        self,
        mime: _Optional[str] = ...,
        data: _Optional[bytes] = ...,
        features: _Optional[_Iterable[_Union[Feature, _Mapping]]] = ...,
    ) -> None: ...

class RegisterExecutorRequest(_message.Message):
    __slots__ = ("executor_id", "addr", "extractor")
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ADDR_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    addr: str
    extractor: Extractor
    def __init__(
        self,
        executor_id: _Optional[str] = ...,
        addr: _Optional[str] = ...,
        extractor: _Optional[_Union[Extractor, _Mapping]] = ...,
    ) -> None: ...

class RegisterExecutorResponse(_message.Message):
    __slots__ = ("executor_id",)
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    def __init__(self, executor_id: _Optional[str] = ...) -> None: ...

class HeartbeatRequest(_message.Message):
    __slots__ = ("executor_id",)
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    def __init__(self, executor_id: _Optional[str] = ...) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ("executor_id", "tasks")
    EXECUTOR_ID_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    executor_id: str
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    def __init__(
        self,
        executor_id: _Optional[str] = ...,
        tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ...,
    ) -> None: ...

class Task(_message.Message):
    __slots__ = (
        "id",
        "extractor",
        "namespace",
        "content_metadata",
        "input_params",
        "extractor_binding",
        "output_index_mapping",
        "outcome",
    )

    class OutputIndexMappingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    ID_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_METADATA_FIELD_NUMBER: _ClassVar[int]
    INPUT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_BINDING_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_INDEX_MAPPING_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    id: str
    extractor: str
    namespace: str
    content_metadata: ContentMetadata
    input_params: str
    extractor_binding: str
    output_index_mapping: _containers.ScalarMap[str, str]
    outcome: TaskOutcome
    def __init__(
        self,
        id: _Optional[str] = ...,
        extractor: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        content_metadata: _Optional[_Union[ContentMetadata, _Mapping]] = ...,
        input_params: _Optional[str] = ...,
        extractor_binding: _Optional[str] = ...,
        output_index_mapping: _Optional[_Mapping[str, str]] = ...,
        outcome: _Optional[_Union[TaskOutcome, str]] = ...,
    ) -> None: ...

class ListExtractorsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListExtractorsResponse(_message.Message):
    __slots__ = ("extractors",)
    EXTRACTORS_FIELD_NUMBER: _ClassVar[int]
    extractors: _containers.RepeatedCompositeFieldContainer[Extractor]
    def __init__(
        self, extractors: _Optional[_Iterable[_Union[Extractor, _Mapping]]] = ...
    ) -> None: ...

class Extractor(_message.Message):
    __slots__ = ("name", "description", "input_params", "outputs", "input_mime_types")

    class OutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    INPUT_MIME_TYPES_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    input_params: str
    outputs: _containers.ScalarMap[str, str]
    input_mime_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        input_params: _Optional[str] = ...,
        outputs: _Optional[_Mapping[str, str]] = ...,
        input_mime_types: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class GetNamespaceRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetNamespaceResponse(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: Namespace
    def __init__(
        self, namespace: _Optional[_Union[Namespace, _Mapping]] = ...
    ) -> None: ...

class ListContentRequest(_message.Message):
    __slots__ = ("namespace", "source", "parent_id", "labels_eq")

    class LabelsEqEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    LABELS_EQ_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    source: str
    parent_id: str
    labels_eq: _containers.ScalarMap[str, str]
    def __init__(
        self,
        namespace: _Optional[str] = ...,
        source: _Optional[str] = ...,
        parent_id: _Optional[str] = ...,
        labels_eq: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class ListContentResponse(_message.Message):
    __slots__ = ("content_list",)
    CONTENT_LIST_FIELD_NUMBER: _ClassVar[int]
    content_list: _containers.RepeatedCompositeFieldContainer[ContentMetadata]
    def __init__(
        self,
        content_list: _Optional[_Iterable[_Union[ContentMetadata, _Mapping]]] = ...,
    ) -> None: ...

class ListBindingsRequest(_message.Message):
    __slots__ = ("namespace",)
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    def __init__(self, namespace: _Optional[str] = ...) -> None: ...

class ListBindingsResponse(_message.Message):
    __slots__ = ("bindings",)
    BINDINGS_FIELD_NUMBER: _ClassVar[int]
    bindings: _containers.RepeatedCompositeFieldContainer[ExtractorBinding]
    def __init__(
        self, bindings: _Optional[_Iterable[_Union[ExtractorBinding, _Mapping]]] = ...
    ) -> None: ...

class CreateNamespaceRequest(_message.Message):
    __slots__ = ("name", "bindings")
    NAME_FIELD_NUMBER: _ClassVar[int]
    BINDINGS_FIELD_NUMBER: _ClassVar[int]
    name: str
    bindings: _containers.RepeatedCompositeFieldContainer[ExtractorBinding]
    def __init__(
        self,
        name: _Optional[str] = ...,
        bindings: _Optional[_Iterable[_Union[ExtractorBinding, _Mapping]]] = ...,
    ) -> None: ...

class CreateNamespaceResponse(_message.Message):
    __slots__ = ("name", "created_at")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    created_at: int
    def __init__(
        self, name: _Optional[str] = ..., created_at: _Optional[int] = ...
    ) -> None: ...

class ListNamespaceRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListNamespaceResponse(_message.Message):
    __slots__ = ("namespaces",)
    NAMESPACES_FIELD_NUMBER: _ClassVar[int]
    namespaces: _containers.RepeatedCompositeFieldContainer[Namespace]
    def __init__(
        self, namespaces: _Optional[_Iterable[_Union[Namespace, _Mapping]]] = ...
    ) -> None: ...

class ExtractorBinding(_message.Message):
    __slots__ = ("extractor", "name", "input_params", "filters", "content_source")

    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    extractor: str
    name: str
    input_params: str
    filters: _containers.ScalarMap[str, str]
    content_source: str
    def __init__(
        self,
        extractor: _Optional[str] = ...,
        name: _Optional[str] = ...,
        input_params: _Optional[str] = ...,
        filters: _Optional[_Mapping[str, str]] = ...,
        content_source: _Optional[str] = ...,
    ) -> None: ...

class ExtractorBindRequest(_message.Message):
    __slots__ = ("namespace", "binding", "created_at")
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    BINDING_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    binding: ExtractorBinding
    created_at: int
    def __init__(
        self,
        namespace: _Optional[str] = ...,
        binding: _Optional[_Union[ExtractorBinding, _Mapping]] = ...,
        created_at: _Optional[int] = ...,
    ) -> None: ...

class ExtractorBindResponse(_message.Message):
    __slots__ = (
        "created_at",
        "extractor",
        "index_name_table_mapping",
        "output_index_name_mapping",
    )

    class IndexNameTableMappingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    class OutputIndexNameMappingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXTRACTOR_FIELD_NUMBER: _ClassVar[int]
    INDEX_NAME_TABLE_MAPPING_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_INDEX_NAME_MAPPING_FIELD_NUMBER: _ClassVar[int]
    created_at: int
    extractor: Extractor
    index_name_table_mapping: _containers.ScalarMap[str, str]
    output_index_name_mapping: _containers.ScalarMap[str, str]
    def __init__(
        self,
        created_at: _Optional[int] = ...,
        extractor: _Optional[_Union[Extractor, _Mapping]] = ...,
        index_name_table_mapping: _Optional[_Mapping[str, str]] = ...,
        output_index_name_mapping: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class ContentMetadata(_message.Message):
    __slots__ = (
        "id",
        "file_name",
        "parent_id",
        "mime",
        "labels",
        "storage_url",
        "created_at",
        "namespace",
        "source",
    )

    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    ID_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    MIME_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    STORAGE_URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    file_name: str
    parent_id: str
    mime: str
    labels: _containers.ScalarMap[str, str]
    storage_url: str
    created_at: int
    namespace: str
    source: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        file_name: _Optional[str] = ...,
        parent_id: _Optional[str] = ...,
        mime: _Optional[str] = ...,
        labels: _Optional[_Mapping[str, str]] = ...,
        storage_url: _Optional[str] = ...,
        created_at: _Optional[int] = ...,
        namespace: _Optional[str] = ...,
        source: _Optional[str] = ...,
    ) -> None: ...

class CreateContentRequest(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: ContentMetadata
    def __init__(
        self, content: _Optional[_Union[ContentMetadata, _Mapping]] = ...
    ) -> None: ...

class CreateContentResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class Namespace(_message.Message):
    __slots__ = ("name", "bindings")
    NAME_FIELD_NUMBER: _ClassVar[int]
    BINDINGS_FIELD_NUMBER: _ClassVar[int]
    name: str
    bindings: _containers.RepeatedCompositeFieldContainer[ExtractorBinding]
    def __init__(
        self,
        name: _Optional[str] = ...,
        bindings: _Optional[_Iterable[_Union[ExtractorBinding, _Mapping]]] = ...,
    ) -> None: ...

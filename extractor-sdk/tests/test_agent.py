import unittest

from indexify_extractor_sdk.base_extractor import ExtractorWrapper, Content, Feature

from indexify_extractor_sdk.mock_extractor import MockExtractor, InputParams

from indexify_extractor_sdk.coordinator_service_pb2 import (
    Task,
    TaskOutcome,
    ContentMetadata,
    Extractor,
)
from indexify_extractor_sdk.agent import ExtractorAgent
from indexify_extractor_sdk.extractor_worker import ExtractorModule, create_executor
from pathlib import Path


def create_mock_task():
    storage_url = str(Path(__file__).parent / "foo.txt")
    storage_url = "file://" + storage_url
    content_metadata = ContentMetadata(
        id="1",
        file_name="foo.txt",
        parent_id="12",
        mime="text/plain",
        labels={"url": "test.com"},
        storage_url=storage_url,
        created_at=123,
        namespace="mynamespace",
        source="foo_extractor",
    )
    return Task(
        id="1",
        extractor="mock_extractor",
        namespace="mynamespace",
        content_metadata=content_metadata,
        input_params='{"a": 1, "b": "foo"}',
        extraction_policy="mypolicy",
        output_index_mapping={"embedding": "embedding_index_name_x"},
        outcome=TaskOutcome.UNKNOWN,
    )


def _create_executor():
    extractor_module = ExtractorModule(
        module_name="indexify_extractor_sdk.mock_extractor",
        class_name="MockExtractor",
    )
    return create_executor(extractor_module)


def create_extractor_agent():
    extractor = Extractor(
        name="mock_extractor",
        description="mock extractor",
        input_params="{}",
        input_mime_types=["text/plain"],
        outputs={"embedding": "embedding_index_name_x"},
    )
    return ExtractorAgent(
        executor_id="124",
        extractor=extractor,
        coordinator_addr="localhost:8950",
        executor=_create_executor(),
        ingestion_addr="localhost:8900",
    )


class TestAgent(unittest.IsolatedAsyncioTestCase):
    def __init__(self, *args, **kwargs):
        super(TestAgent, self).__init__(*args, **kwargs)

    async def test_launch_tasks(self):
        agent: ExtractorAgent = create_extractor_agent()
        task: Task = create_mock_task()
        agent.add_task(task)
        await agent.launch_task(task)
        self.assertEqual(len(agent._task_outcomes), 1)
        self.assertEqual(agent._task_outcomes[task.id].task_outcome, "Success")
        self.assertEqual(len(agent._task_outcomes[task.id].new_content), 2)


if __name__ == "__main__":
    unittest.main()

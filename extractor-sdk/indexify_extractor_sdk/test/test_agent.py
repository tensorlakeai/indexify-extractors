import traceback
import json
import asynctest
from asynctest.mock import patch, MagicMock
from unittest.mock import AsyncMock
from indexify_extractor_sdk.agent import process_task_outcome
from indexify_extractor_sdk.ingestion_api_models import (
    ApiContent,
    Content,
    Feature,
    ApiFeature,
    ApiMultipartContentFrame,
    ApiMultipartContentFeature,
    ApiBeginMultipartContent,
    ApiFinishMultipartContent,
    ApiBeginExtractedContentIngest,
    ApiFinishExtractedContentIngest,
    ApiExtractedFeatures,
)
from indexify_extractor_sdk.base_extractor import Embedding
import websockets

CONTENT_FRAME_SIZE = 2


class TestProcessTaskOutcome(asynctest.TestCase):
    def setUp(self):
        self.server_exception = None

    async def server(self, websocket, path):
        try:
            message = await websocket.recv()

            message_dict = json.loads(message)
            begin_ingest = ApiBeginExtractedContentIngest.model_validate(
                message_dict
            ).BeginExtractedContentIngest
            assert begin_ingest.task_id == "test_task_id"
            assert begin_ingest.namespace == "test_namespace"
            assert begin_ingest.output_to_index_table_mapping == {
                "output1": "index_table1",
                "output2": "index_table2",
            }
            assert begin_ingest.parent_content_id == "test_content_id"
            assert begin_ingest.executor_id == "test_executor_id"
            assert begin_ingest.task_outcome == "test_task_outcome"
            assert begin_ingest.extraction_policy == "test_extraction_policy"
            assert begin_ingest.extractor == "test_extractor"

            expected_data = [[1, 2, 3, 4, 5, 6, 7], [4, 5, 6, 7, 8, 9]]

            for i in range(2):
                message = await websocket.recv()
                # check if messages is ApiBeginMultpartContent
                message_dict = json.loads(message)
                begin_multipart_content = ApiBeginMultipartContent.model_validate(
                    message_dict
                ).BeginMultipartContent
                assert begin_multipart_content.id == i + 1

                # check if next messages are ApiContentFrame covering expected_data[i]
                for j in range(0, len(expected_data[i]), CONTENT_FRAME_SIZE):
                    message = await websocket.recv()
                    message_dict = json.loads(message)
                    content_frame = ApiMultipartContentFrame.model_validate(
                        message_dict
                    ).MultipartContentFrame
                    assert (
                        content_frame.bytes
                        == expected_data[i][j : j + CONTENT_FRAME_SIZE]
                    )

                # check if next messages are AddExtractedFeatures for each embedding
                for j in range(2):
                    message = await websocket.recv()
                    message_dict = json.loads(message)
                    feature = ApiMultipartContentFeature.model_validate(
                        message_dict
                    ).MultipartContentFeature
                    name = "name1" if j == 0 else "name3"
                    assert feature.name == name
                    data = [1, 2, 3] if j == 0 else [4, 5, 6]
                    assert feature.values == data

                # check if next message is FinishMultipartContent
                message = await websocket.recv()
                message_dict = json.loads(message)["FinishMultipartContent"]
                assert message_dict["content_type"] == "type1" if i == 0 else "type2"
                assert (
                    message_dict["labels"] == {"label1": "value1"}
                    if i == 0
                    else {"label2": "value2"}
                )
                assert len(message_dict["features"]) == 1

            # receive features associated with content one by one
            for i in range(2):
                message = await websocket.recv()
                message_dict = json.loads(message)
                features = message_dict["ExtractedFeatures"]
                assert features["content_id"] == "test_content_id"
                assert len(features["features"]) == 1
                feature = features["features"][0]
                name = "name1" if i == 0 else "name2"
                assert feature["name"] == name
                type = "embedding" if i == 0 else "metadata"
                assert feature["feature_type"] == type

            # check if next message is ApiFinishExtractedContentIngest
            message = await websocket.recv()
            message_dict = json.loads(message)
            finish_ingest = ApiFinishExtractedContentIngest.model_validate(message_dict)

        except Exception as e:
            print(traceback.format_exc())
            self.server_exception = e

    async def test_process_task_outcome(self):
        # Start the server in the background
        server = await websockets.serve(self.server, "localhost", 8765)

        # Create mock objects for the parameters
        mock_task_outcome = MagicMock()
        mock_task_outcome.task_id = "test_task_id"
        mock_task_outcome.new_content = ["content1", "content2"]
        mock_task = MagicMock()
        mock_task.namespace = "test_namespace"
        mock_task.output_index_mapping = {
            "output1": "index_table1",
            "output2": "index_table2",
        }
        mock_task.content_metadata.id = "test_content_id"
        mock_task_outcome.task_outcome = "test_task_outcome"
        mock_task.extraction_policy = "test_extraction_policy"
        mock_task.extractor = "test_extractor"

        embedding1 = Embedding(values=[1, 2, 3], distance="cosine")
        embedding2 = Embedding(values=[4, 5, 6], distance="cosine")
        # Create Feature objects
        feature1 = Feature.embedding(
            name="name1", values=embedding1.values, distance=embedding1.distance
        )
        feature2 = Feature.metadata(name="name2", value={"a": 1, "b": "foo"})
        feature3 = Feature.embedding(
            name="name3", values=embedding2.values, distance=embedding2.distance
        )

        # Create Content objects
        content1 = Content(
            content_type="type1",
            data=bytes([1, 2, 3, 4, 5, 6, 7]),
            features=[feature1, feature2, feature3],
            labels={"label1": "value1"},
        )
        content2 = Content(
            content_type="type2",
            data=bytes([4, 5, 6, 7, 8, 9]),
            features=[feature1, feature2, feature3],
            labels={"label2": "value2"},
        )

        # Create ApiContent objects from Content objects
        api_content1 = ApiContent.from_content(content1)
        api_content2 = ApiContent.from_content(content2)

        mock_task_outcome.new_content = [api_content1, api_content2]

        mock_task_outcome.features = [
            ApiFeature.from_feature(feature1),
            ApiFeature.from_feature(feature2),
        ]

        url = "ws://localhost:8765"
        _executor_id = "test_executor_id"

        await process_task_outcome(mock_task_outcome, mock_task, url, _executor_id, 2)

        # Close the server
        server.close()
        await server.wait_closed()

        if self.server_exception is not None:
            self.fail(f"Test failed with error: {self.server_exception}")


if __name__ == "__main__":
    asynctest.main()

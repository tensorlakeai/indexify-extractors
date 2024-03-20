import asyncio
from . import coordinator_service_pb2
from .coordinator_service_pb2_grpc import CoordinatorServiceStub
import grpc
from typing import List, Dict, Union
from .base_extractor import Content, Feature
from .content_downloader import download_content
from pydantic import BaseModel
from .extractor_worker import extract_content
from .ingestion_api_models import (
    ApiContent,
    ApiFeature,
    BeginExtractedContentIngest,
    ExtractedContent,
    ExtractedFeatures,
    FinishExtractedContentIngest,
    ApiBeginExtractedContentIngest,
    ApiExtractedContent,
    ApiExtractedFeatures,
    ApiFinishExtractedContentIngest,
)
import json
from .server import http_server, ServerRouter, get_server_advertise_addr
import concurrent
from itertools import islice
import websockets

CONTENT_UPLOAD_BATCH_SIZE = 5


class CompletedTask(BaseModel):
    task_id: str
    task_outcome: str
    new_content: List[ApiContent]
    features: List[ApiFeature]


class ExtractorAgent:
    def __init__(
        self,
        executor_id: str,
        extractor: coordinator_service_pb2.Extractor,
        coordinator_addr: str,
        executor: concurrent.futures.ProcessPoolExecutor,
        ingestion_addr: str = "localhost:8900",
    ):
        self._executor_id = executor_id
        self._extractor = extractor
        self._has_registered = False
        self._coordinator_addr = coordinator_addr
        self._tasks: map[str, coordinator_service_pb2.Task] = {}
        self._task_outcomes: Dict[str, CompletedTask] = {}
        self._ingestion_addr = ingestion_addr
        self._executor = executor

    async def ticker(self):
        while True:
            await asyncio.sleep(5)
            yield coordinator_service_pb2.HeartbeatRequest(
                executor_id=self._executor_id,
                pending_tasks=len(self._tasks),
            )

    async def register(self):
        # This needs to be here because every time we register we need to create a new channel
        # because the old one might have been closed after hb was broken or we could never connect
        self._channel = grpc.aio.insecure_channel(self._coordinator_addr)
        self._stub: CoordinatorServiceStub = CoordinatorServiceStub(self._channel)
        req = coordinator_service_pb2.RegisterExecutorRequest(
            executor_id=self._executor_id,
            addr=self._advertise_addr,
            extractor=self._extractor,
        )
        return await self._stub.RegisterExecutor(req)

    async def task_completion_reporter(self):
        print("starting task completion reporter")
        while True:
            await asyncio.sleep(5)
            # We should copy only the keys and not the values
            url = f"ws://{self._ingestion_addr}/write_content"
            for task_id, task_outcome in self._task_outcomes.copy().items():
                print(
                    f"reporting outcome of task {task_id}, outcome: {task_outcome.task_outcome}, num_content: {len(task_outcome.new_content)}, num_features: {len(task_outcome.features)}"
                )
                task: coordinator_service_pb2.Task = self._tasks[task_id]
                begin_msg = ApiBeginExtractedContentIngest(
                    BeginExtractedContentIngest=BeginExtractedContentIngest(
                        task_id=task_outcome.task_id,
                        namespace=task.namespace,
                        output_to_index_table_mapping=task.output_index_mapping,
                        parent_content_id=task.content_metadata.id,
                        executor_id=self._executor_id,
                        task_outcome=task_outcome.task_outcome,
                        extraction_policy=task.extraction_policy,
                        extractor=task.extractor,
                    )
                )
                try:
                    # https://docs.python.org/3/library/itertools.html#itertools.batched
                    def batched(iterable, n):
                        # batched('ABCDEFG', 3) --> ABC DEF G
                        if n < 1:
                            raise ValueError("n must be at least one")
                        it = iter(iterable)
                        while batch := tuple(islice(it, n)):
                            yield batch

                    async with websockets.connect(
                        url, ping_interval=5, ping_timeout=30
                    ) as ws:
                        await ws.send(begin_msg.model_dump_json())
                        for batch in batched(
                            task_outcome.new_content, CONTENT_UPLOAD_BATCH_SIZE
                        ):
                            extracted_content = ApiExtractedContent(
                                ExtractedContent=ExtractedContent(content_list=batch)
                            )
                            await ws.send(extracted_content.model_dump_json())
                        print(
                            f"finished message {FinishExtractedContentIngest(num_extracted_content=len(task_outcome.new_content)).model_dump_json()}"
                        )
                        for batch in batched(
                            task_outcome.features, CONTENT_UPLOAD_BATCH_SIZE
                        ):
                            extracted_features = ApiExtractedFeatures(
                                ExtractedFeatures=ExtractedFeatures(
                                    content_id=task.content_metadata.id, features=batch
                                )
                            )
                            await ws.send(extracted_features.model_dump_json())
                        finish_msg = ApiFinishExtractedContentIngest(
                            FinishExtractedContentIngest=FinishExtractedContentIngest(
                                num_extracted_content=len(task_outcome.new_content)
                            )
                        )
                        await ws.send(finish_msg.model_dump_json())
                except Exception as e:
                    print(f"failed to report task {task_id}, exception: {e}")
                    continue

                self._task_outcomes.pop(task_id)

    async def launch_task(self, task: coordinator_service_pb2.Task):
        try:
            content = download_content(task.content_metadata)
        except Exception as e:
            print(f"failed to download content{e} for task {task.id}")
            return
        try:
            outputs: Union[List[Feature], List[Content]] = await extract_content(
                loop=asyncio.get_running_loop(),
                executor=self._executor,
                content=content,
                params=task.input_params,
            )
        except Exception as e:
            print(f"failed to execute task {task.id} {e}")
            self._task_outcomes[task.id] = CompletedTask(
                task_id=task.id, task_outcome="Failed", new_content=[], features=[]
            )
            return
        print(f"completed task {task.id}")
        new_content: List[ApiContent] = []
        new_features: List[ApiFeature] = []
        out: Union[Feature, Content]
        for out in outputs:
            if type(out) == Feature:
                new_features.append(
                    ApiFeature(
                        feature_type=out.feature_type, name=out.name, data=json.dumps(out.value)
                    )
                )
                continue
            content_features = []
            for feature in out.features:
                content_features.append(
                    ApiFeature(
                        feature_type=feature.feature_type,
                        name=feature.name,
                        data=feature.value,
                    )
                )
            new_content.append(
                ApiContent(
                    mime=out.content_type,
                    bytes=list(out.data),
                    features=content_features,
                    labels=out.labels,
                )
            )
        self._task_outcomes[task.id] = CompletedTask(
            task_id=task.id,
            task_outcome="Success",
            new_content=new_content,
            features=new_features,
        )

    async def run(self):
        import signal

        asyncio.get_event_loop().add_signal_handler(
            signal.SIGINT, self.shutdown, asyncio.get_event_loop()
        )
        server_router = ServerRouter(self._executor)
        self._http_server = http_server(server_router)
        asyncio.create_task(self._http_server.serve())
        self._advertise_addr = await get_server_advertise_addr(self._http_server)
        print(f"advertise addr is {self._advertise_addr}")
        asyncio.create_task(self.task_completion_reporter())
        self._should_run = True
        while self._should_run:
            print("attempting to register")
            try:
                await self.register()
                self._has_registered = True
            except Exception as e:
                print(f"failed to register{e}")
                await asyncio.sleep(5)
                continue
            hb_ticker = self.ticker()
            print("starting heartbeat")
            try:
                hb_response_it = self._stub.Heartbeat(hb_ticker)
                resp: coordinator_service_pb2.HeartbeatResponse
                async for resp in hb_response_it:
                    task: coordinator_service_pb2.Task
                    for task in resp.tasks:
                        if task.id not in self._tasks:
                            self.add_task(task)
                            print(f"added task {task.id} to queue")
                            asyncio.create_task(self.launch_task(task))
            except Exception as e:
                print(f"failed to heartbeat{e}")
                continue

    def add_task(self, task: coordinator_service_pb2.Task):
        self._tasks[task.id] = task

    async def exeucte_task(self):
        return {"status": "ok"}

    async def _shutdown(self, loop):
        print("shutting down agent ...")
        self._should_run = False
        self._http_server.should_exit = True
        await self._channel.close()
        for task in asyncio.all_tasks(loop):
            task.cancel()

    def shutdown(self, loop):
        self._executor.shutdown(wait=True, cancel_futures=True)
        loop.create_task(self._shutdown(loop))

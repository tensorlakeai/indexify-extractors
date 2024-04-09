import asyncio
from . import coordinator_service_pb2
from .coordinator_service_pb2_grpc import CoordinatorServiceStub
import grpc
import json
from typing import List, Dict, Union, Optional
from .base_extractor import Content, Feature, Embedding
from .content_downloader import download_content, create_content
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
    ApiBeginMultipartContent,
    BeginMultipartContent,
    ApiFinishMultipartContent,
    ApiMultipartContentFeature,
    MultipartContentFeature,
    ApiMultipartContentFrame,
    MultipartContentFrame,
    FinishMultipartContent,
)
from .utils import batched
from .server import http_server, ServerRouter, get_server_advertise_addr
import concurrent
import websockets
from .task_store import TaskStore, CompletedTask

CONTENT_FRAME_SIZE = 1024 * 1024


def begin_message(task_outcome, task: coordinator_service_pb2.Task, _executor_id):
    return ApiBeginExtractedContentIngest(
        BeginExtractedContentIngest=BeginExtractedContentIngest(
            task_id=task_outcome.task_id,
            namespace=task.namespace,
            output_to_index_table_mapping=task.output_index_mapping,
            parent_content_id=task.content_metadata.id,
            executor_id=_executor_id,
            task_outcome=task_outcome.task_outcome,
            extraction_policy=task.extraction_policy_id,
            extractor=task.extractor,
            index_tables=task.index_tables,
        )
    )


async def send_extracted_content(ws, content: ApiContent, id: int, frame_size):
    # start new multipart content
    await ws.send(
        ApiBeginMultipartContent(
            BeginMultipartContent=BeginMultipartContent(id=id)
        ).model_dump_json()
    )

    # send data in chunks of frame_size
    for i in range(0, len(content.bytes), frame_size):
        slice = content.bytes[i : i + frame_size]
        content_frame = ApiMultipartContentFrame(
            MultipartContentFrame=MultipartContentFrame(bytes=slice)
        )
        await ws.send(content_frame.model_dump_json())

    # finish multipart content with features
    await ws.send(
        ApiFinishMultipartContent(
            FinishMultipartContent=FinishMultipartContent(
                content_type=content.content_type,
                features=content.features,
                labels=content.labels,
            )
        ).model_dump_json()
    )


async def process_task_outcome(
    task_outcome,
    task: coordinator_service_pb2.Task,
    url,
    _executor_id,
    frame_size=CONTENT_FRAME_SIZE,
):
    async with websockets.connect(url, ping_interval=5, ping_timeout=30) as ws:
        # start new extracted content ingest
        await ws.send(begin_message(task_outcome, task, _executor_id).model_dump_json())

        # send all contents one at a time
        for i, content in enumerate(task_outcome.new_content):
            await send_extracted_content(ws, content, id=i + 1, frame_size=frame_size)

        # send all features one at a time
        for feature in task_outcome.features:
            extracted_features = ApiExtractedFeatures(
                ExtractedFeatures=ExtractedFeatures(
                    content_id=task.content_metadata.id, features=[feature]
                )
            )
            await ws.send(extracted_features.model_dump_json())
        print(
            f"finished message {FinishExtractedContentIngest(num_extracted_content=len(task_outcome.new_content)).model_dump_json()}"
        )

        # finish extracted content ingest
        finish_msg = ApiFinishExtractedContentIngest(
            FinishExtractedContentIngest=FinishExtractedContentIngest(
                num_extracted_content=len(task_outcome.new_content)
            )
        )
        await ws.send(finish_msg.model_dump_json())


class ExtractorAgent:
    def __init__(
        self,
        executor_id: str,
        extractor: coordinator_service_pb2.Extractor,
        coordinator_addr: str,
        executor: concurrent.futures.ProcessPoolExecutor,
        listen_port: int,
        advertise_addr: Optional[str],
        ingestion_addr: str = "localhost:8900",
    ):
        self._task_store: TaskStore = TaskStore()
        self._executor_id = executor_id
        self._extractor = extractor
        self._has_registered = False
        self._coordinator_addr = coordinator_addr
        self._ingestion_addr = ingestion_addr
        self._listen_port = listen_port
        self._advertise_addr = advertise_addr
        self._executor = executor

    async def ticker(self):
        while True:
            await asyncio.sleep(5)
            yield coordinator_service_pb2.HeartbeatRequest(
                executor_id=self._executor_id,
                pending_tasks=self._task_store.num_pending_tasks(),
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
            await self.launch_tasks()
            # We should copy only the keys and not the values
            url = f"ws://{self._ingestion_addr}/write_content"
            for task_outcome in self._task_store.task_outcomes():
                print(
                    f"reporting outcome of task {task_outcome.task_id}, outcome: {task_outcome.task_outcome}, num_content: {len(task_outcome.new_content)}, num_features: {len(task_outcome.features)}"
                )
                task: coordinator_service_pb2.Task = self._task_store.get_task(
                    task_outcome.task_id
                )
                try:
                    await process_task_outcome(
                        task_outcome, task, url, self._executor_id
                    )
                except Exception as e:
                    print(
                        f"failed to report task {task_outcome.task_outcome}, exception: {e}"
                    )
                    continue

                self._task_store.mark_reported(task_id=task_outcome.task_id)

    async def launch_tasks(self):
        tasks_to_launch = self._task_store.get_runnable_tasks()
        if len(tasks_to_launch) == 0:
            return
        print("launching tasks : ", ",".join(tasks_to_launch.keys()))
        content_list = {}
        content_urls = {}
        for _, task in tasks_to_launch.items():
            content_urls[task.id] = task.content_metadata.storage_url
        content_bytes = await download_content(content_urls)
        for task_id, bytes in content_bytes.items():
            if isinstance(bytes, Exception):
                print(f"failed to download content{bytes} for task {task_id}")
                completed_task = CompletedTask(
                    task_id=task_id, task_outcome="Failed", new_content=[], features=[]
                )
                self._task_store.complete(outcome=completed_task)
                continue
            c = create_content(bytes, tasks_to_launch[task_id])
            content_list[task_id] = c
        if len(content_list) == 0:
            return
        try:
            print(f"launching tasks {len(content_list)}")
            outputs: Dict[str, Union[List[Feature], List[Content]]] = (
                await extract_content(
                    loop=asyncio.get_running_loop(),
                    executor=self._executor,
                    content_list=content_list,
                    params=task.input_params,
                )
            )
        except Exception as e:
            task_ids = ",".join(content_list.keys())
            print(f"failed to execute tasks {task_ids} {e}")
            for task_id in content_list.keys():
                completed_task = CompletedTask(
                    task_id=task_id, task_outcome="Failed", new_content=[], features=[]
                )
                self._task_store.complete(outcome=completed_task)
            return
        print(f"completed task len {len(outputs)}")
        for task_id, e_output in outputs.items():
            print(f"completed task {task_id}")
            new_content: List[ApiContent] = []
            new_features: List[ApiFeature] = []
            out: Union[Feature, Content]
            for out in e_output:
                if type(out) == Feature:
                    new_features.append(ApiFeature.from_feature(feature=out))
                    continue
                new_content.append(ApiContent.from_content(content=out))
            completed_task = CompletedTask(
                task_id=task_id,
                task_outcome="Success",
                new_content=new_content,
                features=new_features,
            )
            self._task_store.complete(outcome=completed_task)

    async def run(self):
        import signal

        asyncio.get_event_loop().add_signal_handler(
            signal.SIGINT, self.shutdown, asyncio.get_event_loop()
        )
        server_router = ServerRouter(self._executor)
        self._http_server = http_server(server_router, port=self._listen_port)
        asyncio.create_task(self._http_server.serve())
        if not self._advertise_addr:
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
                    self._task_store.add_tasks(resp.tasks)
            except Exception as e:
                print(f"failed to heartbeat{e}")
                continue

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

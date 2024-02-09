from fastapi import FastAPI
import uvicorn
import asyncio
from . import coordinator_service_pb2
from .coordinator_service_pb2_grpc import CoordinatorServiceStub
import grpc
from .base_extractor import ExtractorWrapper, ExtractorDescription
from typing import Optional, List, Dict
from .base_extractor import Content
import nanoid
import json
from .content_downloader import download_content
from pydantic import BaseModel
from concurrent.futures import ProcessPoolExecutor
from .extractor_worker import extract_content, ExtractorModule


class CompletedTask(BaseModel):
    task_id: str
    task_outcome: str
    content: List[Content]


class ExtractorAgent:
    def __init__(
        self,
        executor_id: str,
        extractor: coordinator_service_pb2.Extractor,
        channel: grpc.aio.Channel,
        extractor_module: ExtractorModule,
    ):
        self._executor_id = executor_id
        self._extractor = extractor
        self._extractor_module = extractor_module
        self._has_registered = False
        self._stub: CoordinatorServiceStub = CoordinatorServiceStub(channel)
        self._tasks: map[str, coordinator_service_pb2.Task] = {}
        self._task_outcomes: Dict[str, CompletedTask] = {}

    async def ticker(self):
        while True:
            await asyncio.sleep(5)
            yield coordinator_service_pb2.HeartbeatRequest(
                executor_id=self._executor_id
            )

    async def register(self):
        req = coordinator_service_pb2.RegisterExecutorRequest(
            executor_id=self._executor_id, extractor=self._extractor
        )
        return await self._stub.RegisterExecutor(req)

    async def launch_task(self, task: coordinator_service_pb2.Task):
        try:
            content = download_content(task.content_metadata)
        except Exception as e:
            print(f"failed to download content{e} for task {task.id}")
            return
        try:
            out: List[Content] = await extract_content(
                loop=asyncio.get_running_loop(),
                extractor_module=self._extractor_module,
                content=content,
                params=task.input_params,
            )
        except Exception as e:
            print(f"failed to execute task {task.id} {e}")
            self._task_outcomes[task.id] = CompletedTask(
                task_id=task.id, task_outcome="error", content=[]
            )
            return
        print(f"completed task {task.id} {out}")
        self._task_outcomes[task.id] = CompletedTask(
            task_id=task.id, task_outcome="ok", content=out
        )

    async def run(self):
        while True:
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
                            self._tasks[task.id] = task
                            print(f"added task {task.id} to queue")
                            asyncio.create_task(self.launch_task(task))
            except Exception as e:
                print(f"failed to heartbeat{e}")
                continue

    async def exeucte_task(self):
        return {"status": "ok"}


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


async def http_server_main(loop) -> uvicorn.Server:
    config = uvicorn.Config(
        "indexify_extractor:app", port=0, log_level="info", loop=loop
    )
    server = uvicorn.Server(config)
    return server


def local(extractor: str, text: Optional[str] = None, file: Optional[str] = None):
    if text and file:
        raise ValueError("You can only pass either text or file, not both.")
    if not text and not file:
        raise ValueError("You need to pass either text or file")
    if text:
        content = Content.from_text(text)
    module, cls = extractor.split(":")
    wrapper = ExtractorWrapper(module, cls)
    result = wrapper.extract([content], params="{}")
    print(result)


def describe(extractor: str):
    module, cls = extractor.split(":")
    wrapper = ExtractorWrapper(module, cls)
    print(wrapper.describe())


def join(
    extractor: str,
    coordinator: str = "localhost:8950",
    ingestion_addr: str = "localhost:8900",
):
    print(f"joining {coordinator} and sending extracted content to {ingestion_addr}")
    module, cls = extractor.split(":")
    extractor_module = ExtractorModule(module_name=module, class_name=cls)
    wrapper = ExtractorWrapper(module, cls)
    description: ExtractorDescription = wrapper.describe()
    outputs = {}
    for name, embedding_schema in description.embedding_schemas.items():
        outputs[name] = json.dumps({"embedding": embedding_schema.model_dump()})
    for name, metadata_schema in description.metadata_schemas.items():
        outputs[name] = json.dumps({"attributes": metadata_schema})
    print(outputs)

    api_extractor_description = coordinator_service_pb2.Extractor(
        name=description.name,
        description=description.description,
        input_params=description.input_params,
        input_mime_types=description.input_mime_types,
        outputs=outputs,
    )
    channel = grpc.aio.insecure_channel(coordinator)
    id = nanoid.generate()
    print(f"extractor id is {id}")
    server = ExtractorAgent(id, api_extractor_description, channel, extractor_module)
    asyncio.get_event_loop().run_until_complete(server.run())

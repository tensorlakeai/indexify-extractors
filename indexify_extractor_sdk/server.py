from pydantic import BaseModel, Json
from typing import Optional, List
from .indexify_api_objects import ApiContent, ApiFeature
from .base_extractor import Content
from .extractor_worker import extract_content, ExtractorModule
import uvicorn
import asyncio

from fastapi import FastAPI, APIRouter


class ExtractionRequest(BaseModel):
    content: ApiContent
    input_params: Optional[Json]


class ServerRouter:

    def __init__(self, extractor_module: ExtractorModule):
        self._extractor_module = extractor_module
        self.router = APIRouter()
        self.router.add_api_route("/extract", self.extract, methods=["POST"])

    def extract(self, request: ExtractionRequest):
        loop = asyncio.get_event_loop()
        content = Content(
            content_type=request.content.mime,
            data=request.content.bytes,
            features=[],
            labels=request.content.labels,
        )
        content_out: List[Content] = extract_content(
            loop, self._extractor_module, content, params=request.input_params
        )
        api_content: List[ApiContent] = []
        for content in content_out:
            api_features = []
            for feature in content.features:
                api_features.append(
                    ApiFeature(
                        feature_type=feature.feature_type,
                        name=feature.name,
                        data=feature.value,
                    )
                )
            api_content.append(
                ApiContent(
                    mime=content.content_type,
                    bytes=content.data,
                    features=api_features,
                    labels=content.labels,
                )
            )
        return api_content


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


class ServerWithNoSigHandler(uvicorn.Server):

    # Override
    def install_signal_handlers(self) -> None:

        # Do nothing
        pass


def http_server(server_router: ServerRouter) -> uvicorn.Server:
    print("starting extraction server endpoint")
    app.include_router(server_router.router)
    config = uvicorn.Config(
        app, loop="asyncio", port=0, log_level="info", lifespan="off"
    )

    return ServerWithNoSigHandler(config)

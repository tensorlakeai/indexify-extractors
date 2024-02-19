from pydantic import BaseModel, Json
from typing import Optional, List
from .ingestion_api_models import ApiContent, ApiFeature
from .base_extractor import Content
from .extractor_worker import extract_content, ExtractorModule
import uvicorn
import asyncio
import json
import netifaces
import concurrent

from fastapi import FastAPI, APIRouter


class ExtractionRequest(BaseModel):
    content: ApiContent
    input_params: Optional[Json]


class ExtractionResponse(BaseModel):
    content: List[ApiContent]


class ServerRouter:
    def __init__(self, executor: concurrent.futures.ProcessPoolExecutor):
        self._executor = executor
        self.router = APIRouter()
        self.router.add_api_route("/", self.root, methods=["GET"])
        self.router.add_api_route("/extract", self.extract, methods=["POST"])

    async def root(self):
        return {"Indexify Extractor"}

    async def extract(self, request: ExtractionRequest):
        loop = asyncio.get_event_loop()
        content = Content(
            content_type=request.content.mime,
            data=bytes(request.content.bytes),
            features=[],
            labels=request.content.labels,
        )
        input_params = (
            json.dumps(request.input_params) if request.input_params else None
        )
        content_out: List[Content] = await extract_content(
            loop, self._executor, content, params=input_params
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
                    bytes=list(content.data),
                    features=api_features,
                    labels=content.labels,
                )
            )
        return ExtractionResponse(content=api_content)


class ServerWithNoSigHandler(uvicorn.Server):
    def install_signal_handlers(self) -> None:
        pass


def http_server(server_router: ServerRouter) -> uvicorn.Server:
    print("starting extraction server endpoint")
    app = FastAPI()
    app.include_router(server_router.router)
    config = uvicorn.Config(
        app, loop="asyncio", host="0.0.0.0", port=0, log_level="info", lifespan="off"
    )

    return ServerWithNoSigHandler(config)


async def get_server_advertise_addr(
    server: uvicorn.Server, advertise_addr: str = ""
) -> str:
    while not server.started:
        await asyncio.sleep(0.1)
    port: int
    for server in server.servers:
        for sock in server.sockets:
            port = sock.getsockname()[1]
            break
    addr = (
        get_most_publicly_addressable_ip() if advertise_addr == "" else advertise_addr
    )
    return f"{addr}:{port}"


def get_most_publicly_addressable_ip():
    # IP address priorities
    ip_priorities = {"public": 1, "private": 2, "loopback": 3}

    def ip_type(ip_address):
        """Determine IP address type based on known ranges."""
        if ip_address.startswith("127."):
            return "loopback"
        elif (
            ip_address.startswith("10.")
            or ip_address.startswith("172.16.")
            or ip_address.startswith("172.31.")
            or ip_address.startswith("192.168.")
        ):
            return "private"
        else:
            return "public"

    def sort_key(ip):
        """Sort key for IP addresses based on their type."""
        return ip_priorities[ip_type(ip)]

    ip_addresses = []
    # List all network interfaces
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        # Consider IPv4 addresses only
        if netifaces.AF_INET in addrs:
            for addr_info in addrs[netifaces.AF_INET]:
                ip_addresses.append(addr_info["addr"])

    # Sort IP addresses by their type
    ip_addresses.sort(key=sort_key)

    # Return the most publicly addressable IP, if available
    if ip_addresses:
        return ip_addresses[0]
    else:
        raise Exception("No IP address available")

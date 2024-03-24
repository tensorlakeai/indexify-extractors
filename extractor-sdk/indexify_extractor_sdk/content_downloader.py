import boto3

from .base_extractor import Content
from . import coordinator_service_pb2
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from google.cloud import storage
import httpx
from typing import Dict
import asyncio


def disk_loader(file_path: str):
    print(file_path)
    file_path = file_path.removeprefix("file:/")
    with open(file_path, "rb") as f:
        return f.read()


def s3_loader(s3_url: str) -> bytes:
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc
    key = parsed_url.path.lstrip("/")

    s3 = boto3.client("s3")

    response = s3.get_object(Bucket=bucket_name, Key=key)
    return response["Body"].read()


def azure_blob_loader(blob_url: str) -> bytes:
    token_credential = DefaultAzureCredential()
    parsed_url = urlparse(blob_url)
    account_url = f"https://{parsed_url.netloc}"
    container_name = parsed_url.path.split("/")[1]
    blob_name = "/".join(parsed_url.path.split("/")[2:])

    blob_service_client = BlobServiceClient(
        account_url=account_url, credential=token_credential
    )
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )

    return blob_client.download_blob().readall()


def gcp_storage_loader(storage_url: str) -> bytes:
    parsed_url = urlparse(storage_url)
    bucket_name = parsed_url.netloc
    blob_name = parsed_url.path.lstrip("/")

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


async def fetch_url(id, url):
    try:
        async with httpx.AsyncClient() as client:
            print(f"downloading url {url}")
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return id, response.read()
    except Exception as e:
        return id, e


async def download_parallel(urls):
    tasks = [fetch_url(id, url) for id, url in urls.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results


async def download_content(urls: Dict[str, str]) -> Dict[str, Content]:
    out = {}
    disk_urls = {}
    s3_urls = {}
    http_urls = {}
    gs_urls = {}
    for task_id, url in urls.items():
        if url.startswith("file://"):
            disk_urls[task_id] = url
        elif url.startswith("s3://"):
            s3_urls[task_id] = url
        elif url.startswith("https://") or url.startswith("http://"):
            http_urls[task_id] = url
        elif url.startswith("gs://"):
            gs_urls[task_id] = url
        else:
            out[task_id] = Exception(f"unsupported storage url {url}")
    for task_id, url in gs_urls.items():
        out[task_id] = gcp_storage_loader(url)
    for task_id, url in s3_urls.items():
        out[task_id] = s3_loader(url)
    for task_id, url in disk_urls.items():
        out[task_id] = disk_loader(url)

    result = await download_parallel(http_urls)
    for task_id, b in result:
        out[task_id] = b

    return out


def create_content(bytes, task: coordinator_service_pb2.Task) -> Content:
    metadata = task.content_metadata
    return Content(
        content_type=metadata.mime, data=bytes, features=[], labels=metadata.labels
    )

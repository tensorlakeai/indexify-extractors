import boto3

from .base_extractor import Content
from . import coordinator_service_pb2
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from google.cloud import storage


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


def download_content(
    content_metadata: coordinator_service_pb2.ContentMetadata,
) -> Content:
    if content_metadata.storage_url.startswith("file://"):
        data = disk_loader(content_metadata.storage_url)
    elif content_metadata.storage_url.startswith("s3://"):
        data = s3_loader(content_metadata.storage_url)
    elif content_metadata.storage_url.startswith("https://"):
        data = azure_blob_loader(content_metadata.storage_url)
    elif content_metadata.storage_url.startswith("gs://"):
        data = gcp_storage_loader(content_metadata.storage_url)
    else:
        raise Exception(f"Unsupported storage url{content_metadata.storage_url}")

    return Content(
        content_type=content_metadata.mime,
        data=data,
        labels=content_metadata.labels,
        features=[],
    )

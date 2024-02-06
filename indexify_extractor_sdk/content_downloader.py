from .base_extractor import Content
from . import coordinator_service_pb2


def disk_loader(file_path: str):
    file_path = file_path.strip("file://")
    with open(file_path, "rb") as f:
        return f.read()


def s3_loader(s3_url: str):
    raise Exception("Not implemented")


def download_content(
    content_metadata: coordinator_service_pb2.ContentMetadata,
) -> Content:
    if content_metadata.storage_url.startswith("file://"):
        data = disk_loader(content_metadata.storage_url)
    elif content_metadata.storage_url.startswith("s3://"):
        data = s3_loader(content_metadata.storage_url)
    else:
        raise Exception(f"Unsupported storage url{content_metadata.storage_url}")

    return Content(
        content_type=content_metadata.mime,
        data=data,
        labels=content_metadata.labels,
        features=[],
    )

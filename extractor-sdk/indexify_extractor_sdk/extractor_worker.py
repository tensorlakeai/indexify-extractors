from typing import List, Union, Dict
from .base_extractor import Content, ExtractorWrapper, Feature, ExtractorDescription
from pydantic import Json, BaseModel
import concurrent
from .downloader import get_db_path
import sqlite3
import os
import sys
import json


class ExtractorModule(BaseModel):
    module_name: str
    class_name: str

# str here is ExtractorDescription.name
extractor_wrapper_map: Dict[str, ExtractorWrapper] = {}

def create_extractor_wrapper_map(ids: List[str] = []):
    global extractor_wrapper_map
    print("creating extractor wrappers")

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    records = []

    # When running the extractor worker as Docker container,
    # the database does not exist because the downloader is not run.
    # So just use the ExtractorWrapper from the provided IDs.
    try:
        cur.execute("SELECT id, name FROM extractors")
        records = cur.fetchall()
    except sqlite3.OperationalError:
        conn.close()

        print("adding extractor from environment")
        extractor = os.environ.get("EXTRACTOR_PATH")

        extractor_directory = os.path.join(
            os.path.expanduser("~"),
            ".indexify-extractors",
            os.path.basename(extractor.split(".")[0])
        )

        sys.path.append(extractor_directory)

        module, cls = extractor.split(":")
        extractor_wrapper = ExtractorWrapper(module, cls)
        description = extractor_wrapper.describe()
        name = description.name

        records = [(extractor, name)]

    # Return error if no extractors are found
    if len(records) == 0:
        conn.close()
        raise ValueError(
            "No extractors found in the database.",
            "Please run the downloader to download extractors."
        )

    for row in records:
        if len(ids) > 0 and row[0] not in ids:
            continue

        print(f"adding extractor: {row[1]}")
        module, cls = row[0].split(":")
        extractor_wrapper = ExtractorWrapper(module, cls)
        extractor_wrapper_map[row[1]] = extractor_wrapper

    conn.close()


def create_executor(workers: int, extractor_ids: List[str] = []):
    print("creating executor")
    return concurrent.futures.ProcessPoolExecutor(
        initializer=create_extractor_wrapper_map,
        max_workers=workers,
        initargs=(extractor_ids,)
    )


def _extract_content(
    task_content_map: Dict[str, Content],
    task_params_map: Dict[str, Json],
    task_extractor_map: Dict[str, str],
) -> Dict[str, Union[List[Feature], List[Content]]]:
    result = {}

    # Iterate over available extractors
    for extractor_name, extractor_wrapper in extractor_wrapper_map.items():
        # Get task IDs using the extractor
        task_ids = [
            task_id
            for task_id, task_extractor_name in task_extractor_map.items()
            if extractor_name == task_extractor_name
        ]

        # Skip if no tasks are using the extractor
        if len(task_ids) == 0:
            continue

        # Filter task contents and params using the task IDs
        task_contents = {}
        for task_id in task_ids:
            task_contents[task_id] = task_content_map[task_id]

        params =  {}
        inner = task_params_map["dummy_task_id"]
        for task_id in task_ids:
            params[task_id] = inner[task_id]
        task_params = {"dummy_task_id": json.dumps(params)}

        # Extract content using the right extractor
        extracted = extractor_wrapper.extract_batch(task_contents, task_params)

        # Add the extracted data to the result
        for task_id, extracted_data in extracted.items():
            result[task_id] = extracted_data

    return result


def _describe() -> List[ExtractorDescription]:
    return [
        wrapper.describe()
        for _, wrapper in extractor_wrapper_map.items()
    ]


async def extract_content(
    loop, 
    executor, 
    content_list: Dict[str, Content], 
    params: Json,
    extractors: Dict[str, str] # task ID -> extractor name
) -> Dict[str, List[Union[Feature, Content]]]:
    return await loop.run_in_executor(
        executor, 
        _extract_content, 
        content_list, 
        {"dummy_task_id": params},
        extractors
    )


async def describe(loop, executor):
    return await loop.run_in_executor(executor, _describe)

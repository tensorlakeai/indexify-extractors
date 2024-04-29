from typing import List, Union, Dict
from .base_extractor import Content, ExtractorWrapper, Feature, ExtractorDescription
from pydantic import Json, BaseModel
import concurrent
from .downloader import get_db_path
import sqlite3
import os


class ExtractorModule(BaseModel):
    module_name: str
    class_name: str

# str here is ExtractorDescription.name
extractor_wrapper_map: Dict[str, ExtractorWrapper] = {}

def create_extractor_wrapper_map():
    global extractor_wrapper_map
    print("creating extractor wrappers")

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM extractors")
    records = cur.fetchall()

    # Return error if no extractors are found
    if len(records) == 0:
        conn.close()
        raise ValueError(
            "No extractors found in the database.",
            "Please run the downloader to download extractors."
        )

    for row in records:
        print(f"adding extractor: {row[1]}")
        module, cls = row[0].split(":")
        extractor_wrapper = ExtractorWrapper(module, cls)
        extractor_wrapper_map[row[1]] = extractor_wrapper

    conn.close()


def create_executor(workers: int):
    print("creating executor")
    return concurrent.futures.ProcessPoolExecutor(
        initializer=create_extractor_wrapper_map,
        max_workers=workers,
    )


def _extract_content(
    task_content_map: Dict[str, Content],
    task_params_map: Dict[str, Json],
    task_extractor_map: Dict[str, str],
) -> Dict[str, Union[List[Feature], List[Content]]]:
    result = {}

    for extractor_name, extractor_wrapper in extractor_wrapper_map.items():
        # Get task IDs using the extractor
        task_ids = [
            task_id
            for task_id, extractor_name in task_extractor_map.items()
            if extractor_name == extractor_name
        ]

        # Filter task contents and params using the task IDs
        task_contents = {}
        for task_id in task_ids:
            task_contents[task_id] = task_content_map[task_id]

        params =  {}
        inner = task_params_map["dummy_task_id"]
        for task_id in task_ids:
            params[task_id] = inner[task_id]
        task_params = {"dummy_task_id": params}

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

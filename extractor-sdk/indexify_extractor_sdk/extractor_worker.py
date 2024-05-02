from typing import List, Union, Dict, Optional
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

# List of ExtractorDescription
# This is used to report the available extractors to the coordinator
extractor_descriptions: List[ExtractorDescription] = []

def load_extractors(name: str):
    """Load an extractor to the memory: extractor_wrapper_map."""
    global extractor_wrapper_map

    # Return early if the extractor is already loaded
    if name in extractor_wrapper_map:
        return

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute("SELECT id FROM extractors WHERE name = ?", (name,))
    record = cur.fetchone()
    conn.close()

    if record is None:
        raise ValueError(f"Extractor {name} not found in the database.")

    print(f"loading extractor: {name}")
    extractor_wrapper = create_extractor_wrapper(record[0])
    extractor_wrapper_map[name] = extractor_wrapper


def create_extractor_wrapper_map(id: Optional[str] = None):
    global extractor_wrapper_map
    print("creating extractor wrappers")

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    # When running the extractor as a Docker container,
    # the extractor ID is passed as an environment variable.
    # If there is ID or EXTRACTOR_PATH, load the extractor singularly.
    if id:
        cur.execute(f"SELECT id, name FROM extractors WHERE id = '{id}'")
        record = cur.fetchone()
        if record is None:
            raise ValueError(f"Extractor {id} not found in the database.")

        extractor_wrapper = create_extractor_wrapper(record[0])
        load_extractor_description(extractor_wrapper)
        extractor_wrapper_map[record[1]] = extractor_wrapper
    elif os.environ.get("EXTRACTOR_PATH"):
        print("adding extractor from environment")
        extractor = os.environ.get("EXTRACTOR_PATH")

        extractor_directory = os.path.join(
            os.path.expanduser("~"),
            ".indexify-extractors",
            os.path.basename(extractor.split(".")[0])
        )

        # This has to be done first to import the extractor module correctly
        sys.path.append(extractor_directory)

        extractor_wrapper = create_extractor_wrapper(extractor)
        description = load_extractor_description(extractor_wrapper)
        name = description.name
        extractor_wrapper_map[name] = extractor_wrapper
    else:
        cur.execute("SELECT id, name FROM extractors")
        records = cur.fetchall()
        for record in records:
            # This only loads the description of the extractor to be reported
            # to the coordinator. The actual extractor will be loaded when needed.
            print(f"reporting available extractor: {record[1]}")
            extractor_wrapper = create_extractor_wrapper(record[0])
            load_extractor_description(extractor_wrapper)

    conn.close()


def load_extractor_description(extractor_wrapper: ExtractorWrapper) -> ExtractorDescription:
    global extractor_descriptions
    description = extractor_wrapper.describe()
    extractor_descriptions.append(description)
    return description


def create_extractor_wrapper(extractor_id: str) -> ExtractorWrapper:
    module, cls = extractor_id.split(":")
    extractor_wrapper = ExtractorWrapper(module, cls)
    return extractor_wrapper


def create_executor(workers: int, extractor_id: Optional[str] = None):
    print("creating executor")
    return concurrent.futures.ProcessPoolExecutor(
        initializer=create_extractor_wrapper_map,
        max_workers=workers,
        initargs=(extractor_id,)
    )


def _extract_content(
    task_content_map: Dict[str, Content],
    task_params_map: Dict[str, Json],
    task_extractor_map: Dict[str, str],
) -> Dict[str, Union[List[Feature], List[Content]]]:
    result = {}

    # Load extractors depending on the tasks
    for _, extractor_name in task_extractor_map.items():
        load_extractors(extractor_name)

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
    return extractor_descriptions


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

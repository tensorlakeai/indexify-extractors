from typing import List, Union, Dict
from .base_extractor import Content, ExtractorWrapper, Feature
from pydantic import Json, BaseModel
import concurrent
import asyncio


class ExtractorModule(BaseModel):
    module_name: str
    class_name: str


def create_extractor_wrapper(extractor_module: ExtractorModule) -> ExtractorWrapper:
    print("creating extractor wrapper")
    global extractor_wrapper
    extractor_wrapper = ExtractorWrapper(
        extractor_module.module_name, extractor_module.class_name
    )


def create_executor(extractor_module: ExtractorModule, workers: int):
    print("creating executor")
    return concurrent.futures.ProcessPoolExecutor(
        initializer=create_extractor_wrapper,
        max_workers=workers,
        initargs=(extractor_module,),
    )


def _extract_content(content_list: Dict[str, Content], params: Json) -> List[Content]:
    return extractor_wrapper.extract_batch(content_list, params)


def _describe():
    return extractor_wrapper.describe()


async def extract_content(
    loop, executor, content_list: Dict[str, Content], params: Json
) -> Dict[str, List[Union[Feature, Content]]]:
    return await loop.run_in_executor(executor, _extract_content, content_list, params)


async def describe(loop, executor):
    return await loop.run_in_executor(executor, _describe)

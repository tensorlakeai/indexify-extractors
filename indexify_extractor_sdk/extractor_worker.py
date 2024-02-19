from typing import List
from .base_extractor import Content, ExtractorWrapper
from pydantic import Json, BaseModel
import concurrent


class ExtractorModule(BaseModel):
    module_name: str
    class_name: str


def create_extractor_wrapper(extractor_module: ExtractorModule) -> ExtractorWrapper:
    print("creating extractor wrapper")
    global extractor_wrapper
    extractor_wrapper = ExtractorWrapper(
        extractor_module.module_name, extractor_module.class_name
    )


def create_executor(extractor_module: ExtractorModule):
    print("creating executor")
    return concurrent.futures.ProcessPoolExecutor(
        initializer=create_extractor_wrapper, initargs=(extractor_module,)
    )


def _extract_content(content: Content, params: Json) -> List[Content]:
    return extractor_wrapper.extract(content, params)


def _describe():
    return extractor_wrapper.describe()


async def extract_content(
    loop, executor, content: Content, params: Json
) -> List[Content]:
    return await loop.run_in_executor(executor, _extract_content, content, params)


async def describe(loop, executor):
    return await loop.run_in_executor(executor, _describe)

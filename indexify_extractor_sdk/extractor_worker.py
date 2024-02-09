from typing import List
from .base_extractor import Content, ExtractorWrapper
from pydantic import Json, BaseModel
import concurrent


class ExtractorModule(BaseModel):
    module_name: str
    class_name: str


async def extract_content(
    loop, extractor_module: ExtractorModule, content: Content, params: Json
) -> List[Content]:
    with concurrent.futures.ProcessPoolExecutor() as pool:
        wrapper = ExtractorWrapper(
            extractor_module.module_name, extractor_module.class_name
        )
        result = await loop.run_in_executor(pool, wrapper.extract, content, params)
        return result
    raise Exception("unable to fork process for extraction")

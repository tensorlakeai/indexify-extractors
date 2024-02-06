from typing import List
from .base_extractor import Content, ExtractorWrapper
from pydantic import Json
import concurrent

class ExtractorWorker:
    def __init__(self, extractor: ExtractorWrapper):
        self._extractor = extractor

    async def extract(self, loop, content: Content, params: Json) -> List[Content]:
        with concurrent.futures.ProcessPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool, self._extractor.extract, [content], params
            )
            return result

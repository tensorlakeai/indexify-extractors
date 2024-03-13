from typing import List, Literal, Optional, Iterable
from pydantic import BaseModel
from indexify_extractor_sdk import Extractor, Content, Feature
import tempfile
import mimetypes
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.image import partition_image


class UnstructuredConfig(BaseModel):
    strategy: Literal['hi_res', 'fast', 'ocr_only', 'auto'] = "fast"
    languages: Optional[Iterable[str]] = None


class UnstructuredExtractor(Extractor):
    name = "tensorlake/unstructured"
    description = "This extractor uses unstructured to extract pieces of pdf document into separate plain text content data."
    input_mime_types = ["application/pdf", "image/jpeg", "image.png"]
    # language packs can be added to system dependencies
    system_dependencies = ["tesseract-ocr"]

    def __init__(self):
        super(UnstructuredExtractor, self).__init__()

    def extract(self, content: Content, params: UnstructuredConfig) -> List[Content]:
        suffix = mimetypes.guess_extension(content.content_type)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmpfile:
            tmpfile.write(content.data)
            tmpfile.flush()

            # detect content type
            if suffix == ".pdf":
                elements = partition_pdf(tmpfile.name, **dict(params))
            else:
                elements = partition_image(tmpfile.name, **dict(params))

            # extract data
            new_content = []
            for e in elements:
                data = e.to_dict()
                metadata = {**data.get("metadata"), "type": data.get("type")}
                new_content.append(
                    Content(
                        content_type="text/plain",
                        data=bytes(data.get("text"), "utf-8"),
                        features=[Feature.metadata(value=metadata)],
                    )
                )
            return new_content

    def sample_input(self) -> Content:
        f = open("sample.pdf", "rb")
        return Content(content_type="application/pdf", data=f.read())


if __name__ == "__main__":
    UnstructuredExtractor().extract_sample_input()

from typing import List, Literal, Optional, Iterable
from pydantic import BaseModel
from indexify_extractor_sdk import Extractor, Content, Feature
import tempfile
import mimetypes
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.image import partition_image


class UnstructuredIOConfig(BaseModel):
    strategy: Literal['hi_res', 'fast', 'ocr_only', 'auto'] = "fast"
    languages: Optional[Iterable[str]] = None


class UnstructuredIOExtractor(Extractor):
    name = "tensorlake/unstructuredio"
    description = "This extractor uses unstructured.io to extract pieces of pdf document into separate plain text content data."
    input_mime_types = ["application/pdf", "image/jpeg", "image.png"]
    # language packs can be added to system dependencies
    system_dependencies = ["tesseract-ocr", "tesseract-ocr-spa", "tesseract-ocr-chi-sim", "tesseract-ocr-fra", "tesseract-ocr-deu"]

    def __init__(self):
        super(UnstructuredIOExtractor, self).__init__()

    def extract(self, content: Content, params: UnstructuredIOConfig) -> List[Content]:
        suffix = mimetypes.guess_extension(content.content_type)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmpfile:
            tmpfile.write(content.data)
            tmpfile.flush()

            # detect content type
            if suffix == ".pdf":
                elements = partition_pdf(tmpfile.name, **dict(params))
            else:
                if params.strategy == "fast":
                    print("fast is not supported on images, defaulting to hi_res")
                    params.strategy = "hi_res"
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
        return self.sample_scientific_pdf()


if __name__ == "__main__":
    UnstructuredIOExtractor().extract_sample_input()

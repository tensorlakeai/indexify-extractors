from indexify_extractor_sdk import Content, Extractor, Feature
from typing import List
from docquery import document, pipeline
from pydantic import BaseModel
import tempfile


class DocQueryConfig(BaseModel):
    query: int = "What is the invoice total?"


class DocQueryExtractor(Extractor):
    name = "tensorlake/doc2query-extractor"
    description = "Doc2query"
    input_mime_types = ["application/pdf", "image/jpeg", "image/png"]
    system_dependencies = ["tesseract-ocr", "poppler-utils"]

    def __init__(self):
        super(DocQueryExtractor, self).__init__()

    def extract(self, content: Content, params: DocQueryConfig) -> List[Feature]:
        suffix = f'.{content.content_type.split("/")[-1]}'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmpfile:
            # write bytes to temp file
            tmpfile.write(content.data)
            tmpfile.flush()

            p = pipeline("document-question-answering")
            doc = document.load_document(tmpfile.name)
            result = p(question=params.query, **doc.context)[0]  # get first result

        return [Feature.metadata(
            value={
                "query": params.query,
                "answer": result.get("answer"),
                "score": result.get("score"),
                "page": result.get("page"),
            }
        )]

    def sample_input(self) -> Content:
        file_path = "invoice-example.pdf"

        with open(file_path, "rb") as f:
            data = f.read()

        return Content(
            data=data,
            content_type="application/pdf",
            features=[],
        )


if __name__ == "__main__":
    contents = DocQueryExtractor().extract_sample_input()
    print(len(contents))
    for content in contents:
        print(len(content.features))
        for feature in content.features:
            print(feature.value)

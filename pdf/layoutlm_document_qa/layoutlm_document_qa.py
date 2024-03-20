from indexify_extractor_sdk import Content, Extractor, Feature
from typing import List
from transformers import pipeline
from pydantic import BaseModel
from pdf2image import convert_from_bytes
import tempfile


class LayoutLMDocumentQAConfig(BaseModel):
    query: str = "What is the invoice total?"


class LayoutLMDocumentQA(Extractor):
    name = "tensorlake/layoutlm-document-qa-extractor"
    description = "Layoutlm document qa"
    input_mime_types = ["application/pdf", "image/jpeg", "image/png"]
    system_dependencies = ["tesseract-ocr", "tesseract-ocr-spa", "tesseract-ocr-chi-sim", "tesseract-ocr-fra", "tesseract-ocr-deu", "poppler-utils"]

    def __init__(self):
        super(LayoutLMDocumentQA, self).__init__()
        self.nlp = pipeline(
            "document-question-answering",
            model="impira/layoutlm-document-qa",
        )

    def extract_from_image(self, content: Content, params: LayoutLMDocumentQAConfig):
        suffix = f'.{content.content_type.split("/")[-1]}'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmpfile:
            tmpfile.write(content.data)
            tmpfile.flush()

            result = self.nlp(tmpfile.name, params.query)[0]
            result["page"] = 0
        return result

    def extract_from_pdf(self, content: Content, params: LayoutLMDocumentQAConfig):
        images = convert_from_bytes(content.data)
        results = []
        # iterate over each image
        for i, img in enumerate(images):
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmpfile:
                img.save(tmpfile.name)
                result = self.nlp(tmpfile.name, params.query)[0]
                result["page"] = i
                results.append(result)
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
        # return the highest score from the results
        return sorted_results[0]

    def extract(
        self, content: Content, params: LayoutLMDocumentQAConfig
    ) -> List[Feature]:

        suffix = f'.{content.content_type.split("/")[-1]}'
        if suffix.endswith(".pdf"):
            result = self.extract_from_pdf(content, params)
        else:
            result = self.extract_from_image(content, params)

        return [
            Feature.metadata(
                value={
                    "query": params.query,
                    "answer": result.get("answer"),
                    "page": result.get("page"),
                    "score": result.get("score"),
                }
            )
        ]

    def sample_input(self) -> Content:
        return self.sample_invoice_pdf()


if __name__ == "__main__":
    contents = LayoutLMDocumentQA().extract_sample_input()
    print(len(contents))
    for content in contents:
        print(len(content.features))
        for feature in content.features:
            print(feature.value)

from pypdf import PdfReader
from pydantic import BaseModel
import torch
from typing import List
from transformers import AutoProcessor, Blip2ForConditionalGeneration
from sentence_transformers import SentenceTransformer

from indexify_extractor_sdk import (
    Extractor,
    Content,
)

class InputParams(BaseModel):
    # No input except the file itself
    ...

class PyPDFExtractor(Extractor):
    input_mime_types = ["application/pdf"]

    def __init__(self):
        super().__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.embedding_model = SentenceTransformer("avsolatorio/GIST-Embedding-v0")
        self.image_processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-6.7b")
        self.captioning_model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-6.7b", device_map="auto", load_in_8bit=True)
    
    def _extract_text_from_pdf(self, pdf_data):
        reader = PdfReader(pdf_data)
        texts = []

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            texts.append(text)
        
        return texts
    
    def _extract_image_from_pdf(self, pdf_data):
        reader = PdfReader(pdf_data)
        images = []

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            for image_file_object in page.images:
                image = image_file_object.data
                images.append(image)
        
        return images
    
    def _process_pdf(self, texts, images):
        for image in images:
            inputs = self.image_processor(images=image, return_tensors="pt").to(self.device, torch.float16)
            generated_ids = self.captioning_model.generate(
                pixel_values=inputs.pixel_values,
                do_sample=True,
                temperature=1.0,
                length_penalty=1.0,
                repetition_penalty=1.5,
                max_length=128,
                min_length=1,
                num_beams=5,
                top_p=0.9,
            )
            result = self.image_processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            texts.append(result)
        
        embeddings = self.embedding_model.encode(texts)
        return embeddings

    def extract(self, content: Content, params: InputParams) -> List[List[float]]:
        texts = self._extract_text_from_pdf(content.data)
        images = self._extract_image_from_pdf(content.data)
        embeddings = self._process_pdf(texts, images)
        return embeddings

# Testing block
if __name__ == "__main__":
    pdf_file_path = "/content/paper.pdf"  # Replace with your PDF file path

    extractor = PyPDFExtractor()

    with open(pdf_file_path, "rb") as file:
        pdf_data = file.read()
        pdf_content = Content(data=pdf_data)
        pdf_results = extractor.extract([pdf_content], InputParams())
        print("PDF Extraction Results:", pdf_results)
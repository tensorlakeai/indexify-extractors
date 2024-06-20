import math
from rapidfuzz import fuzz
import re
import regex
from statistics import mean
import os
import time
from indexify import IndexifyClient, ExtractionGraph

CHUNK_MIN_CHARS = 25

def chunk_text(text, chunk_len=500):
    chunks = [text[i:i+chunk_len] for i in range(0, len(text), chunk_len)]
    chunks = [c for c in chunks if c.strip() and len(c) > CHUNK_MIN_CHARS]
    return chunks

def overlap_score(hypothesis_chunks, reference_chunks):
    length_modifier = len(hypothesis_chunks) / len(reference_chunks)
    search_distance = max(len(reference_chunks) // 5, 10)
    chunk_scores = []
    for i, hyp_chunk in enumerate(hypothesis_chunks):
        max_score = 0
        total_len = 0
        i_offset = int(i * length_modifier)
        chunk_range = range(max(0, i_offset-search_distance), min(len(reference_chunks), i_offset+search_distance))
        for j in chunk_range:
            ref_chunk = reference_chunks[j]
            score = fuzz.ratio(hyp_chunk, ref_chunk, score_cutoff=30) / 100
            if score > max_score:
                max_score = score
                total_len = len(ref_chunk)
        chunk_scores.append(max_score)
    return chunk_scores

def score_text(hypothesis, reference):
    hypothesis_chunks = chunk_text(hypothesis)
    reference_chunks = chunk_text(reference)
    chunk_scores = overlap_score(hypothesis_chunks, reference_chunks)
    return mean(chunk_scores)

# Download the extractors and join the server
os.system("!indexify-extractor download tensorlake/marker")
os.system("!indexify-extractor download tensorlake/pdf-extractor")
os.system("!indexify-extractor download tensorlake/unstructuredio")
os.system("!indexify-extractor download tensorlake/easyocr")
os.system("!indexify-extractor download tensorlake/ocrmypdf")
os.system("!indexify-extractor join-server")

# Initialize the Indexify client
client = IndexifyClient()

# Function to create and run extraction graphs
def create_and_run_extraction_graph(graph_name, extractor_name, pdf_filepath):
    extraction_graph_spec = f"""
    name: '{graph_name}'
    extraction_policies:
       - extractor: '{extractor_name}'
         name: 'pdf_to_text'
    """
    extraction_graph = ExtractionGraph.from_yaml(extraction_graph_spec)
    client.create_extraction_graph(extraction_graph)
    content_id = client.upload_file(graph_name, pdf_filepath)
    client.wait_for_extraction(content_id)
    extracted_content = client.get_extracted_content(content_id=content_id, graph_name=graph_name, policy_name="pdf_to_text")
    return extracted_content

# Directories containing PDF and reference files
pdf_dir = "/content/pdfs"
reference_dir = "/content/references"

# Iterate over PDF files in the directory
for pdf_file in os.listdir(pdf_dir):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        reference_file = os.path.join(reference_dir, pdf_file.replace(".pdf", ".md"))

        # Read reference text
        with open(reference_file, "r", encoding="utf-8") as f:
            reference_text = f.read()

        # Run Marker extractor
        start_time = time.time()
        marker_output = create_and_run_extraction_graph("markerbench", "tensorlake/marker", pdf_path)
        marker_time = time.time() - start_time
        marker_score = score_text(marker_output, reference_text)
        print(f"Marker score for {pdf_file}: {marker_score} (Time taken: {marker_time:.2f} seconds)")

        # Run PDF extractor
        start_time = time.time()
        pdf_extractor_output = create_and_run_extraction_graph("pdfbench", "tensorlake/pdf-extractor", pdf_path)
        pdf_extractor_time = time.time() - start_time
        pdf_extractor_score = score_text(pdf_extractor_output, reference_text)
        print(f"PDF extractor score for {pdf_file}: {pdf_extractor_score} (Time taken: {pdf_extractor_time:.2f} seconds)")

        # Run Unstructured IO extractor
        start_time = time.time()
        unstructured_output = create_and_run_extraction_graph("unstructuredbench", "tensorlake/unstructuredio", pdf_path)
        unstructured_time = time.time() - start_time
        unstructured_score = score_text(unstructured_output, reference_text)
        print(f"Unstructured IO score for {pdf_file}: {unstructured_score} (Time taken: {unstructured_time:.2f} seconds)")

        # Run EasyOCR extractor
        start_time = time.time()
        easyocr_output = create_and_run_extraction_graph("easyocrbench", "tensorlake/easyocr", pdf_path)
        easyocr_time = time.time() - start_time
        easyocr_score = score_text(easyocr_output, reference_text)
        print(f"Easy OCR score for {pdf_file}: {easyocr_score} (Time taken: {easyocr_time:.2f} seconds)")

        # Run OCRMyPDF extractor
        start_time = time.time()
        ocrmypdf_output = create_and_run_extraction_graph("ocrmypdfbench", "tensorlake/ocrmypdf", pdf_path)
        ocrmypdf_time = time.time() - start_time
        ocrmypdf_score = score_text(ocrmypdf_output, reference_text)
        print(f"OCR My PDF score for {pdf_file}: {ocrmypdf_score} (Time taken: {ocrmypdf_time:.2f} seconds)")

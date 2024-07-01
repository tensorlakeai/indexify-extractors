import os
import time
from indexify import IndexifyClient, ExtractionGraph
import math
from rapidfuzz import fuzz
import re
import regex
from statistics import mean

# Scoring functions
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
    try:
        return mean(chunk_scores)
    except:
        return 0

# Extraction graph creation functions
def create_openai_graph():
    extraction_graph_spec = """
    name: 'pdf_extraction_openai'
    extraction_policies:
      - extractor: 'tensorlake/openai'
        name: 'pdf_to_text'
        input_params:
          model_name: 'gpt-4o'
          key: 'YOUR_OPENAI_KEY'
          system_prompt: 'Extract all text from the document.'
    """
    return ExtractionGraph.from_yaml(extraction_graph_spec)

def create_gemini_graph():
    extraction_graph_spec = """
    name: 'pdf_extraction_gemini'
    extraction_policies:
      - extractor: 'tensorlake/gemini'
        name: 'pdf_to_text'
        input_params:
          model_name: 'gemini-1.5-flash-latest'
          key: 'YOUR_GEMINI_KEY'
          system_prompt: 'Extract all text from the document.'
    """
    return ExtractionGraph.from_yaml(extraction_graph_spec)

# Benchmark function
def benchmark_extraction(client, graph, pdf_path, reference_path):
    # Upload the PDF file
    start_time = time.time()
    content_id = client.upload_file(graph.name, pdf_path)
    
    # Wait for the extraction to complete
    client.wait_for_extraction(content_id)
    
    # Retrieve the extracted content
    extracted_content = client.get_extracted_content(
        content_id=content_id,
        graph_name=graph.name,
        policy_name="pdf_to_text"
    )
    end_time = time.time()

    try:
        extracted_text = extracted_content[0]['content'].decode('utf-8')
    except:
        extracted_text = ""
    
    # Read reference text
    with open(reference_path, 'r') as f:
        reference_text = f.read()
    
    # Calculate score
    score = score_text(extracted_text, reference_text)
    
    return {
        'time': end_time - start_time,
        'score': score
    }

# Main benchmarking script
def run_benchmark():
    client = IndexifyClient()
    
    # Create extraction graphs
    openai_graph = create_openai_graph()
    gemini_graph = create_gemini_graph()
    client.create_extraction_graph(openai_graph)
    client.create_extraction_graph(gemini_graph)
    
    pdf_folder = '/Users/rishiraj/tensorlakeai/experiments/demo/benchmark_data/data/pdfs'
    reference_folder = '/Users/rishiraj/tensorlakeai/experiments/demo/benchmark_data/data/references'
    
    results = {
        'openai': [],
        'gemini': []
    }
    
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            reference_path = os.path.join(reference_folder, pdf_file.replace('.pdf', '.md'))
            
            print(f"Processing {pdf_file}...")
            
            # Benchmark OpenAI
            openai_result = benchmark_extraction(client, openai_graph, pdf_path, reference_path)
            print(pdf_file, ": ", openai_result)
            results['openai'].append(openai_result)
            
            # Benchmark Gemini
            gemini_result = benchmark_extraction(client, gemini_graph, pdf_path, reference_path)
            results['gemini'].append(gemini_result)
    
    # Calculate average scores and times
    for model in results:
        avg_time = mean([r['time'] for r in results[model]])
        avg_score = mean([r['score'] for r in results[model]])
        print(f"{model.capitalize()} Results:")
        print(f"  Average Time: {avg_time:.2f} seconds")
        print(f"  Average Score: {avg_score:.4f}")

if __name__ == "__main__":
    run_benchmark()

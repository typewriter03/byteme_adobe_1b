# src/main.py (Corrected Imports)

import os
import json
import time

# --- CHANGE HERE: Make imports relative ---
from.parsing import process_all_pdfs
from.embedding import EmbeddingModel
from.ranking import HybridRanker
from.utils import format_output_json
# --- END CHANGE ---

def main():
    """
    Main function to orchestrate the persona-driven document intelligence pipeline.
    """
    start_time = time.time()
    print("Starting the document intelligence pipeline...")

    # Define paths as per hackathon rules
    input_dir = os.environ.get("INPUT_DIR", "input")
    output_dir = os.environ.get("OUTPUT_DIR", "output")
    model_dir = "models/"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load Persona and Job-to-be-Done
    try:
        with open(os.path.join(input_dir, "persona.txt"), "r", encoding="utf-8") as f:
            persona = f.read().strip()
        with open(os.path.join(input_dir, "job.txt"), "r", encoding="utf-8") as f:
            job = f.read().strip()
        print(f"Loaded Persona: {persona}")
    except FileNotFoundError:
        print("Error: 'persona.txt' or 'job.txt' not found in input directory.")
        return

    query_text = f"Persona: {persona}. Job to be done: {job}"

    # 2. Process all PDF files
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    pdf_paths = [os.path.join(input_dir, f) for f in pdf_files]
    print(f"Found {len(pdf_files)} PDF(s) to process.")
    
    all_sections = process_all_pdfs(pdf_paths)
    print(f"Extracted {len(all_sections)} sections from all documents.")

    if not all_sections:
        print("No sections could be extracted. Writing an empty output file.")
        output_data = {"message": "No processable sections found in the documents."}
    else:
        # 3. Initialize AI components
        print("Loading the embedding model...")
        embedder = EmbeddingModel(model_path=model_dir)
        if embedder.model is None:
            return # Stop if model loading failed

        ranker = HybridRanker(embedder)
        print("Model loaded. Starting ranking process...")

        # 4. Execute the ranking pipeline
        ranked_results = ranker.rank_sections(all_sections, query_text)
        print("Ranking complete. Generating final output...")

        # 5. Format the final JSON output
        # We need the raw query embedding for the sub-section analysis
        query_embedding = embedder.encode(f"search_query: {query_text}")
        output_data = format_output_json(ranked_results, pdf_files, persona, job, query_embedding, embedder)

    # 6. Write the final JSON to the output directory
    output_filepath = os.path.join(output_dir, "output.json")
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    
    end_time = time.time()
    print(f"Processing complete. Output written to {output_filepath}")
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
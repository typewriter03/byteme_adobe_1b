# src/utils.py

import json
import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .embedding import EmbeddingModel
import re
import os

def clean_document_path(doc_path: str) -> str:
    if not doc_path:
        return 'N/A'
    
    cleaned = re.sub(r'^input[/\\]', '', doc_path)
    cleaned = cleaned.replace('\\', '/')
    cleaned = os.path.basename(cleaned)
    
    return cleaned

def clean_refined_text(text: str) -> str:
    if not text:
        return ""
    
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    
    text = re.sub(r'\(https://[^\)]*\)', '', text)
    text = re.sub(r'https://[^\s]*', '', text)
    text = re.sub(r'\]\s*\(', ' (', text)
    text = re.sub(r'\]\(', ' (', text)
    
    text = re.sub(r'input[/\\]', '', text)
    
    text = re.sub(r'\\+', ' ', text)
    text = re.sub(r'/+', ' ', text)
    
    text = re.sub(r'\b\d{3,}\b', '', text)
    
    text = re.sub(r'\b(wikipedia|britannica|kevmrc|bestofniceblog|snippetsofparis|isolatedtraveller)\b', '', text)
    
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    text = text.strip()
    
    sentences = text.split('.')
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 10 and not re.match(r'^[^\w]*$', sentence):
            cleaned_sentences.append(sentence)
    
    if cleaned_sentences:
        text = '. '.join(cleaned_sentences)
        if not text.endswith('.'):
            text += '.'
    
    return text

def get_refined_text(section: dict, query_embedding: np.ndarray, embedder: EmbeddingModel, top_k: int = 5) -> str:
    content = section.get('content_text', '')
    if not content or embedder.model is None:
        return "No content available for refinement."

    raw_sentences = [s.strip() for s in content.split('.') if s.strip()]
    
    sentences = []
    i = 0
    while i < len(raw_sentences):
        current_sentence = raw_sentences[i].strip()
        
        while (i + 1 < len(raw_sentences) and 
               len(current_sentence) < 80 and 
               len(current_sentence + '. ' + raw_sentences[i + 1]) < 200):
            i += 1
            current_sentence += '. ' + raw_sentences[i].strip()
        
        if current_sentence:
            sentences.append(current_sentence)
        i += 1
    
    if not sentences:
        return content

    sentence_texts_with_prefix = [f"search_document: {s}" for s in sentences]
    sentence_embeddings = embedder.encode(sentence_texts_with_prefix)

    if sentence_embeddings is None or sentence_embeddings.shape[0] == 0:
        return content

    similarities = cosine_similarity(query_embedding.reshape(1, -1), sentence_embeddings)

    top_indices = np.argsort(similarities[0])[-top_k:][::-1]

    refined_sentences = [sentences[int(i)] for i in top_indices]
    
    refined_text = '. '.join(refined_sentences)
    if refined_text and not refined_text.endswith('.'):
        refined_text += '.'

    refined_text = clean_refined_text(refined_text)

    words = refined_text.split()
    if len(words) > 400:
        word_count = 0
        sentences = refined_text.split('.')
        output_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_words = sentence.split()
            if word_count + len(sentence_words) > 400:
                break
            output_sentences.append(sentence)
            word_count += len(sentence_words)
        
        if output_sentences:
            refined_text = '. '.join(output_sentences)
            if not refined_text.endswith('.'):
                refined_text += '.'
        else:
            refined_text = ' '.join(words[:400]) + '.'
    
    return refined_text.strip()


def format_output_json(ranked_sections: list[dict], pdf_files: list[str], persona: str, job: str, query_embedding: np.ndarray, embedder: EmbeddingModel) -> dict:
    cleaned_pdf_files = [clean_document_path(pdf) for pdf in pdf_files]
    
    output = {
        "Metadata": {
            "input_documents": cleaned_pdf_files,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.datetime.now().isoformat()
        },
        "Extracted Sections": [],
        "Sub-section Analysis": []
    }

    if not ranked_sections:
        return output

    output_sections_count = min(len(ranked_sections), 20)

    for section in ranked_sections[:output_sections_count]:
        cleaned_doc_name = clean_document_path(section.get('doc_name', 'N/A'))

        output["Extracted Sections"].append({
            "document": cleaned_doc_name,
            "section_title": section.get('title', 'N/A'),
            "importance_rank": section.get('importance_rank', -1)
        })

        refined_text = get_refined_text(section, query_embedding, embedder)
        output["Sub-section Analysis"].append({
            "document": cleaned_doc_name,
            "refined_text": refined_text
        })

    return output
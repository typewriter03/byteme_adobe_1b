# src/ranking.py (Definitive Final Version)

import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from.embedding import EmbeddingModel

class HybridRanker:
    """
    Implements a two-stage hybrid ranking algorithm combining semantic
    similarity with graph-based centrality to find the most important
    document sections.
    """
    def __init__(self, embedder: EmbeddingModel):
        self.embedder = embedder

    def rank_sections(self, sections: list[dict], query: str, top_n_semantic: int = 50, alpha: float = 0.6) -> list[dict]:
        if not sections or self.embedder.model is None:
            return

        # --- Stage 1: Semantic Search ---
        query_with_prefix = f"search_query: {query}"
        section_texts_with_prefix = [f"search_document: {s['title']}. {s['content_text']}" for s in sections]

        query_embedding = self.embedder.encode(query_with_prefix)
        section_embeddings = self.embedder.encode(section_texts_with_prefix, show_progress_bar=True)

        similarities = cosine_similarity(query_embedding.reshape(1, -1), section_embeddings)

        # --- THIS IS THE CORRECT FIX ---
        # The 'similarities' array has a shape of (1, num_sections).
        # We need to extract the first (and only) row to get a simple list of scores.
        scores = similarities[0]
        for i, section in enumerate(sections):
            section['semantic_score'] = scores[i]
        # --- END OF FIX ---

        sections.sort(key=lambda x: x['semantic_score'], reverse=True)
        top_candidates = sections[:top_n_semantic]
        
        if len(top_candidates) < 2:
            for i, section in enumerate(sections):
                section['final_score'] = section.get('semantic_score', 0)
                section['importance_rank'] = i + 1
            return sections

        # --- Stage 2: Graph-Based Re-ranking ---
        candidate_indices = [sections.index(s) for s in top_candidates]
        candidate_embeddings = np.array([section_embeddings[i] for i in candidate_indices])

        graph = self._build_similarity_graph(candidate_embeddings)

        try:
            pagerank_scores = nx.pagerank(graph, weight='weight')
        except nx.PowerIterationFailedConvergence:
            pagerank_scores = {i: 1.0 / len(graph) for i in range(len(graph))}

        for i, section in enumerate(top_candidates):
            semantic_score = section['semantic_score']
            pagerank_score = pagerank_scores.get(i, 0)
            
            max_pr = max(pagerank_scores.values()) if pagerank_scores else 1
            normalized_pr = pagerank_score / max_pr if max_pr > 0 else 0
            
            section['pagerank_score'] = normalized_pr
            section['final_score'] = (alpha * semantic_score) + ((1 - alpha) * normalized_pr)

        for section in sections:
            if 'final_score' not in section:
                section['final_score'] = section.get('semantic_score', 0)

        sections.sort(key=lambda x: x['final_score'], reverse=True)

        for i, section in enumerate(sections):
            section['importance_rank'] = i + 1
            
        return sections

    def _build_similarity_graph(self, embeddings: np.ndarray, threshold: float = 0.75) -> nx.Graph:
        # Ensure embeddings is a 2D array and not empty
        if embeddings is None or len(embeddings) == 0:
            return nx.Graph()
        if len(embeddings.shape) != 2:
            embeddings = np.atleast_2d(embeddings)
        num_nodes = embeddings.shape[0]
        graph = nx.Graph()
        graph.add_nodes_from(range(num_nodes))

        similarity_matrix = cosine_similarity(embeddings)

        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                similarity = similarity_matrix[i, j]
                if similarity > threshold:
                    graph.add_edge(i, j, weight=similarity)
        return graph
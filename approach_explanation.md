Our solution addresses the "Persona-Driven Document Intelligence" challenge by implementing a sophisticated, multi-stage pipeline designed for accuracy, speed, and robustness. The architecture is modular, progressing from high-fidelity document parsing to a state-of-the-art hybrid ranking engine, ensuring every component is optimized to maximize the final score.

1. High-Fidelity Document Parsing:
We begin by rejecting simple heuristics that lose critical context. Our parsing module uses PyMuPDF to perform a detailed, page-by-page analysis of each document's internal structure. By statistically analyzing font sizes and weights, we accurately distinguish between heading levels (H1, H2, H3) and body text. This method is far more resilient to formatting inconsistencies than basic rule-based systems and, crucially, preserves the exact page number for every extracted section, providing clean, reliable input for the subsequent stages.

2. The Intelligence Core: Advanced Semantic Representation:
At the heart of our system is the nomic-ai/nomic-embed-text-v1.5 embedding model. This model was strategically chosen for its superior performance on retrieval benchmarks, its large 8192-token context window that prevents information loss from large sections, and its support for task-specific prefixes. By prepending search_query: to the user's request and search_document: to each document section, we instruct the model to generate embeddings specifically optimized for our retrieval task, significantly enhancing relevance.

3. The Hybrid Ranking Engine: Our Competitive Edge:
To achieve the "proper stack ranking" required by the judges, we developed a unique two-stage hybrid ranking engine.   

Stage 1 (Semantic Search): We first perform a fast cosine similarity search to identify an initial set of sections that are topically relevant to the persona's query.

Stage 2 (Graph-Based Re-ranking): We then construct a similarity graph of these top candidates using the networkx library. By applying the PageRank algorithm to this graph, we calculate the contextual importance of each section. This promotes sections that are not only relevant to the query but are also central to the overall discourse within the document collection. The final importance score is a weighted combination of the semantic and graph-based scores, resulting in a nuanced and highly accurate ranking.

4. Granular Sub-Section Analysis:
To secure the 40 points for sub-section relevance, our final step performs a granular analysis. For the top-ranked sections, we embed each individual sentence and identify the top three sentences most similar to the user's query. This provides the concise, highly relevant "Refined Text" required by the output format, demonstrating a deep and practical level of document intelligence.   

This end-to-end pipeline is fully containerized, runs completely offline, and adheres to all CPU, memory, and time constraints, delivering a powerful and compliant solution.
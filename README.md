
# Persona-Driven Document Intelligence Adobe Hackathon
This is Solution for Round 1B By Team Byteme
Abhay Sharma
Harsh Agarwal
Devang Kumawat

This project is a solution for Round 1B of the "Connecting the Dots" Hackathon. It is an intelligent document analysis pipeline that processes a collection of PDF documents and, based on a given user persona and their job-to-be-done, extracts and ranks the most relevant sections. The system is designed to be generic, robust, and performant, operating entirely offline within a constrained Docker environment.

## Project Structure

The project is organized into a modular structure to ensure clarity and maintainability:

```
adobe-hackathon-1b/
├──.gitignore               # Specifies files for Git to ignore (e.g., models/, output/).
├── Dockerfile               # Blueprint for building the production Docker container.
├── README.md                # This documentation file.
├── approach_explanation.md  # A concise summary of our technical approach for the judges.
├── download_model.py        # Helper script to download the AI model for local testing.
├── requirements.txt         # Lists all Python dependencies for the project.
├── input/                   # Local directory for test input files (PDFs, persona.txt, job.txt).
├── models/                  # (Ignored by Git) Stores the downloaded AI model files for offline use.
├── output/                  # (Ignored by Git) Local directory where the final output.json is saved.
└── src/                     # Contains all the application's source code.
    ├── __init__.py          # Makes the 'src' directory a Python package.
    ├── embedding.py         # Handles loading the AI model and generating text embeddings.
    ├── main.py              # The main entry point that orchestrates the entire pipeline.
    ├── parsing.py           # Module for high-accuracy PDF parsing and section extraction.
    ├── ranking.py           # Implements our unique hybrid semantic and graph-based ranking engine.
    └── utils.py             # Helper functions for output formatting and sub-section analysis.
```

## Technical Approach

Our solution is a multi-stage pipeline engineered for maximum accuracy under the hackathon's strict constraints.[1]

#### 1\. High-Fidelity Document Parsing

Instead of relying on fragile heuristics, our `parsing.py` module uses `PyMuPDF` to perform a detailed analysis of each document's internal structure. By statistically analyzing font sizes and weights across the document, it accurately distinguishes between heading levels (H1, H2, H3) and body text. This method is highly resilient to formatting inconsistencies and, most importantly, preserves the exact page number for every extracted section, providing clean and reliable input for the subsequent stages.[1]

#### 2\. Advanced Semantic Representation

At the core of our system is the `nomic-ai/nomic-embed-text-v1.5` embedding model. This model was strategically chosen for several key advantages:

  * **High Performance:** It consistently ranks near the top of text embedding leaderboards, ensuring a high degree of semantic understanding.
  * **Long Context Window:** It supports a context length of 8192 tokens, allowing us to embed large document sections without losing critical information.
  * **Task-Specific Prefixes:** We leverage its unique ability to accept prefixes to optimize performance. By prepending `search_query:` to the user's request and `search_document:` to each document section, we instruct the model to generate embeddings specifically tailored for our retrieval task, significantly enhancing relevance.

#### 3\. Hybrid Ranking Engine

To achieve the "proper stack ranking" required by the judges [1], we developed a unique two-stage hybrid ranking engine in `ranking.py`:

  * **Stage 1 (Semantic Search):** We first perform a fast cosine similarity search between the query embedding and all section embeddings. This efficiently identifies an initial set of topically relevant sections.
  * **Stage 2 (Graph-Based Re-ranking):** We then construct a similarity graph of these top candidates using the `networkx` library. By applying the **PageRank algorithm** to this graph, we calculate the contextual importance of each section. This powerful technique promotes sections that are not only relevant to the query but are also central to the overall discourse within the document collection. The final importance score is a weighted combination of the semantic and graph-based scores, resulting in a nuanced and highly accurate final ranking.

#### 4\. Granular Sub-Section Analysis

To secure the 40 points for "Sub-Section Relevance," our `utils.py` module performs a final granular analysis.[1] For the top-ranked sections, we embed each individual sentence and identify the top three sentences most similar to the user's query. This provides the concise, highly relevant "Refined Text" required by the output format, demonstrating a deep and practical level of document intelligence.[1]

## How to Build and Run

The entire solution is containerized with Docker and is designed to run completely offline, as per the hackathon rules.[1]

### Prerequisites

  * Docker Desktop must be installed and running on your system.

### Step 1: Build the Docker Image

This command builds the Docker image from the `Dockerfile`. This process will download the base Python image, install all necessary dependencies from `requirements.txt`, and run the `download_model.py` script to download and save the AI model inside the image. This step requires an internet connection.

From the root directory of the project, run the following command:

```bash
docker build -t persona-intelligence .
```

### Step 2: Prepare Input Data

Place your test files into the `input` folder in the project's root directory. The folder must contain:

  * **3 to 10 PDF documents.**
  * **A `persona.txt` file:** A plain text file containing a description of the user's role.
  * **A `job.txt` file:** A plain text file describing the specific task the user wants to accomplish.

#### Example `persona.txt` content:

```
PhD Researcher in Computational Biology
```

#### Example `job.txt` content:

```
Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks
```

These examples correspond to "Test Case 1: Academic Research" from the challenge documentation.[1]

### Step 3: Run the Docker Container

This command runs the application. It creates a container from the image we just built, links your local `input` and `output` folders to the folders inside the container, and disables the container's network access to prove it works offline.[1]

#### For Windows (in Command Prompt or PowerShell):

```bash
docker run --rm --network none -v "${PWD}\input:/app/input" -v "${PWD}\output:/app/output" persona-intelligence
```
or 

```bash
docker run --rm --network none -v "%cd%\input":/app/input -v "%cd%\output":/app/output persona-intelligence
```

#### For macOS or Linux:

```bash
docker run --rm --network none -v "$(pwd)/input":/app/input -v "$(pwd)/output":/app/output persona-intelligence
```

After the command finishes, the final `output.json` file will be generated in your local `output` folder.

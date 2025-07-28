# src/embedding.py

from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    """
    A wrapper class for the sentence-transformer model to handle
    loading and encoding in an offline environment.
    """
    def __init__(self, model_path: str):
        """
        Initializes and loads the sentence-transformer model from a local path.

        Args:
            model_path (str): The local directory path where the pre-trained
                              model is stored.
        """
        try:
            # --- THIS IS THE ONLY LINE TO CHANGE ---
            # Add trust_remote_code=True to allow the model's custom code to run.
            self.model = SentenceTransformer(model_path, trust_remote_code=True)
            # --- END OF CHANGE ---
        except Exception as e:
            print(f"Fatal Error: Could not load the embedding model from {model_path}. Please ensure the model is downloaded correctly. Error: {e}")
            self.model = None

    def encode(self, texts: list[str] | str, **kwargs) -> np.ndarray | None:
        """
        Encodes a single text or a list of texts into embedding vectors.

        Args:
            texts (list[str] | str): The text(s) to encode.
            **kwargs: Additional arguments for the encode method, e.g., show_progress_bar.

        Returns:
            np.ndarray: A numpy array containing the embedding(s).
                        Returns None if the model failed to load.
        """
        if self.model is None:
            return None
        
        # The model's encode method is highly optimized for batch processing.
        embeddings = self.model.encode(texts, **kwargs)
        return embeddings
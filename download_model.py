import os
from sentence_transformers import SentenceTransformer

def download_and_save_model():
    model_name = 'nomic-ai/nomic-embed-text-v1.5'
    model_path = 'models/'

    os.makedirs(model_path, exist_ok=True)  # ✅ Create directory if missing

    if any(os.scandir(model_path)):
        print(f"Model directory '{model_path}' already contains files. Skipping download.")
        print("If you want to re-download, please empty the 'models/' directory first.")
        return

    print(f"Downloading our chosen embedding model: {model_name}")
    print("This is a larger model and may take a few minutes...")

    try:
        model = SentenceTransformer(model_name, trust_remote_code=True)
        model.save(model_path)
        print(f"Model successfully saved to '{model_path}'")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    download_and_save_model()

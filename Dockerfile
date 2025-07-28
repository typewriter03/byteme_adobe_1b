
FROM --platform=linux/amd64 python:3.11-slim-bullseye as builder

# Install the libraries needed to run our download script.
RUN pip install --no-cache-dir torch einops --extra-index-url https://download.pytorch.org/whl/cpu sentence-transformers

# Set the working directory inside this temporary stage.
WORKDIR /app

# Copy the model download script into the builder.
COPY download_model.py download_model.py

# Execute the script to download the model into the /app/models/ directory.
RUN python download_model.py



FROM --platform=linux/amd64 python:3.11-slim-bullseye

# Set environment variables for the application.
# This forces the transformers library to run in offline mode, a key requirement.
ENV TRANSFORMERS_OFFLINE=1
ENV PYTHONUNBUFFERED=1

# Set the final working directory inside the container.
WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching.
COPY requirements.txt requirements.txt

# Install the Python dependencies from the requirements file.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the pre-downloaded model from the builder stage.
COPY --from=builder /app/models /app/models


COPY src/ ./src/


# Define the command to run the application.
# This executes our main script as a module, ensuring all relative imports work correctly.
CMD ["python", "-m", "src.main"]

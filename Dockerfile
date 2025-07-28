
# --- Stage 1: The Builder ---
FROM --platform=linux/amd64 python:3.11-slim-bullseye as builder

WORKDIR /app

RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu sentence-transformers

COPY download_model.py download_model.py

RUN python download_model.py


FROM --platform=linux/amd64 python:3.11-slim-bullseye

ENV TRANSFORMERS_OFFLINE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /app/models/ ./models/

COPY src/ ./src/

CMD ["python", "-m", "src.main"]

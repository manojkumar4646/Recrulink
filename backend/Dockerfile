FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# FORCE upgrade typing_extensions to fix the PyTorch import error
RUN pip install --no-cache-dir --force-reinstall typing_extensions>=4.8.0

# Pre-download the embedding model during build
RUN python -c "from sentence_transformers import SentenceTransformer; print('Downloading BAAI/bge-m3...'); SentenceTransformer('BAAI/bge-m3'); print('Model downloaded successfully!')"

# Copy the application code
COPY . .

# Create directories
RUN mkdir -p faiss_index data

EXPOSE 8000

CMD ["python", "run.py"]
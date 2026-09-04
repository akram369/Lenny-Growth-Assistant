# ------------------------------------------------------------------------------
# Stage 1: Build React Vite Frontend
# ------------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Production Python Backend + Static Frontend Serve
# ------------------------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight CPU-only PyTorch first (drastically reduces RAM from 800MB to ~120MB, eliminates CUDA bloat)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend source
COPY backend/ ./backend

# Copy built frontend bundle from Stage 1 into backend/static
COPY --from=frontend-builder /app/frontend/dist ./backend/static

WORKDIR /app/backend

# Pre-cache embedding model weights during build phase (Render build has ample RAM)
ENV HF_HOME=/root/.cache/huggingface
ENV TOKENIZERS_PARALLELISM=false
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
RUN python -c "import torch; torch.set_num_threads(1); from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Pre-seed sample transcripts into SQLite database during build phase
RUN python scripts/ingest.py --clear

# Render dynamic port binding (defaults to 10000 on Render, or 8001)
ENV PORT=10000
ENV ENVIRONMENT=production
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start Uvicorn directly (no boot-time downloads or heavy ingestion)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

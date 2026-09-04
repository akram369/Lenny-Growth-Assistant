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

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend source
COPY backend/ ./backend

# Copy built frontend bundle from Stage 1 into backend/static
COPY --from=frontend-builder /app/frontend/dist ./backend/static

WORKDIR /app/backend

# Render dynamic port binding (defaults to 10000 on Render, or 8001)
ENV PORT=10000
ENV ENVIRONMENT=production
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/health || exit 1

# On startup: ingest sample transcripts, then start Uvicorn
CMD sh -c "python scripts/ingest.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"

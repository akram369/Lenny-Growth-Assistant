"""
Vector Embedding Provider.
Uses sentence-transformers/all-MiniLM-L6-v2 (384 dimensions) for local, fast embeddings.
"""

from typing import List
import numpy as np
from app.config import settings
from app.logging_config import logger

_model = None


def get_embedding_model():
    """Lazy-loads the sentence-transformers model instance."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}. Falling back to deterministic pseudo-embedding for testing.")
            _model = "fallback"
    return _model


def embed_text(text: str) -> List[float]:
    """Generates normalized vector embedding for a single string."""
    model = get_embedding_model()
    if model == "fallback":
        # Deterministic 384-dim pseudo-random unit vector based on text hash for tests
        np.random.seed(abs(hash(text)) % (2**31))
        vec = np.random.randn(settings.EMBEDDING_DIMENSION).astype(np.float32)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist()

    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Generates normalized vector embeddings for a list of strings."""
    if not texts:
        return []
    model = get_embedding_model()
    if model == "fallback":
        return [embed_text(t) for t in texts]

    embeddings = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()

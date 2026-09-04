"""
RAG Retriever Module.
Performs semantic similarity search against pgvector transcript chunks with SQLite fallback.
"""

from typing import Any, Dict, List
import numpy as np
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import TranscriptChunkModel, HAS_PGVECTOR
from app.rag.embeddings import embed_text
from app.logging_config import logger


REFUSAL_MESSAGE = "I do not have sufficient information in Lenny's podcast archive to answer this."


async def retrieve_relevant_chunks(
    db: AsyncSession,
    query: str,
    top_k: int = 5,
    threshold: float = 0.35,
) -> List[Dict[str, Any]]:
    """
    Retrieves the top-k most similar transcript chunks for a query.
    Returns list of dicts with chunk metadata and similarity scores.
    """
    if not query.strip():
        return []

    query_embedding = embed_text(query)

    # Check if we are running in pgvector PostgreSQL or fallback mode
    bind = db.bind
    is_postgres = bind and "postgresql" in str(bind.url)

    if is_postgres and HAS_PGVECTOR:
        try:
            # Native pgvector cosine similarity search
            # 1 - (embedding <=> query_vec) gives cosine similarity
            sql = text("""
                SELECT id, episode_id, guest, title, youtube_url, timestamp, chunk_index, content,
                       1 - (embedding <=> :query_vec) AS similarity
                FROM transcript_chunks
                WHERE 1 - (embedding <=> :query_vec) >= :threshold
                ORDER BY embedding <=> :query_vec ASC
                LIMIT :top_k;
            """)
            # pgvector accepts list of floats as string representation '[0.1, 0.2, ...]'
            vec_str = "[" + ",".join(map(str, query_embedding)) + "]"
            result = await db.execute(sql, {"query_vec": vec_str, "threshold": threshold, "top_k": top_k})
            rows = result.fetchall()

            chunks = []
            for row in rows:
                chunks.append({
                    "id": str(row[0]),
                    "episode_id": row[1],
                    "guest": row[2],
                    "title": row[3],
                    "youtube_url": row[4],
                    "timestamp": row[5],
                    "chunk_index": row[6],
                    "content": row[7],
                    "score": round(float(row[8]), 4),
                })
            return chunks
        except Exception as e:
            logger.warning(f"pgvector query failed: {e}. Falling back to in-memory cosine search.")

    # Fallback in-memory cosine search (for SQLite or non-pgvector environments)
    stmt = select(TranscriptChunkModel)
    result = await db.execute(stmt)
    all_chunks = result.scalars().all()

    if not all_chunks:
        return []

    q_vec = np.array(query_embedding, dtype=np.float32)
    q_norm = np.linalg.norm(q_vec)
    if q_norm == 0:
        return []

    scored_chunks = []
    for chunk in all_chunks:
        c_vec = chunk.embedding
        if isinstance(c_vec, (list, tuple, np.ndarray)):
            c_vec = np.array(c_vec, dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)
            if c_norm > 0:
                sim = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
                if sim >= threshold:
                    scored_chunks.append((sim, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_chunks = scored_chunks[:top_k]

    return [
        {
            "id": c.id,
            "episode_id": c.episode_id,
            "guest": c.guest,
            "title": c.title,
            "youtube_url": c.youtube_url,
            "timestamp": c.timestamp,
            "chunk_index": c.chunk_index,
            "content": c.content,
            "score": round(score, 4),
        }
        for score, c in top_chunks
    ]


def format_context_for_prompt(chunks: List[Dict[str, Any]]) -> str:
    """Formats retrieved chunks into numbered source blocks for grounding prompt."""
    if not chunks:
        return "NO RELEVANT PODCAST TRANSCRIPTS FOUND."

    lines = []
    for i, c in enumerate(chunks, 1):
        lines.append(
            f"--- SOURCE {i} ---\n"
            f"Episode: {c['guest']} - {c['title']}\n"
            f"Timestamp: {c['timestamp']}\n"
            f"Excerpt:\n{c['content']}\n"
        )
    return "\n".join(lines)

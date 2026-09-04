"""
Unit Tests for Vector Retrieval, Chunking, and Grounding.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.chunker import chunk_transcript, parse_frontmatter
from app.rag.retriever import retrieve_relevant_chunks, format_context_for_prompt, REFUSAL_MESSAGE


SAMPLE_MARKDOWN = """---
guest: Julie Zhuo
title: Leading with design and intuition
youtube_url: https://youtube.com/watch?v=julie-zhuo
keywords:
- design
- management
---

Julie Zhuo (00:01:15):
Great product design is fundamentally about clarity of purpose and deep customer empathy.

Lenny (00:05:30):
How do you build trust with engineers?

Julie Zhuo (00:05:45):
You build trust by admitting what you do not know and actively listening to technical trade-offs.
"""


def test_parse_frontmatter():
    meta, body = parse_frontmatter(SAMPLE_MARKDOWN)
    assert meta["guest"] == "Julie Zhuo"
    assert "Julie Zhuo (00:01:15):" in body


def test_chunk_transcript():
    chunks = chunk_transcript(SAMPLE_MARKDOWN, episode_id="julie-zhuo", chunk_size_words=10)
    assert len(chunks) >= 1
    first_chunk = chunks[0]
    assert first_chunk["guest"] == "Julie Zhuo"
    assert first_chunk["timestamp"] == "00:01:15"
    assert first_chunk["episode_id"] == "julie-zhuo"


@pytest.mark.asyncio
async def test_relevant_chunks_retrieval(db_session: AsyncSession):
    # Query matching Will Larson's seeded chunk
    query = "engineering mindset and treating engineers like adult peers"
    results = await retrieve_relevant_chunks(db_session, query, top_k=2, threshold=0.1)

    assert len(results) > 0
    top_result = results[0]
    assert top_result["guest"] in ("Will Larson", "Elena Verna")
    assert "timestamp" in top_result
    assert "score" in top_result


@pytest.mark.asyncio
async def test_out_of_domain_empty_retrieval(db_session: AsyncSession):
    # An entirely unrelated query with strict threshold should return no relevant chunks
    query = "recipe for chocolate chip walnut cookies baking instructions"
    results = await retrieve_relevant_chunks(db_session, query, top_k=2, threshold=0.8)

    assert len(results) == 0


def test_format_context_for_prompt():
    chunks = [
        {
            "guest": "Will Larson",
            "title": "The engineering mindset",
            "timestamp": "00:00:00",
            "content": "Treat engineers like adult peers.",
        }
    ]
    formatted = format_context_for_prompt(chunks)
    assert "Will Larson" in formatted
    assert "00:00:00" in formatted
    assert "Treat engineers like adult peers." in formatted

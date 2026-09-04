"""
Transcript Ingestion CLI Script.
Parses transcripts, chunks text with speaker & timestamp metadata,
generates embeddings, and indexes them into PostgreSQL pgvector table.
"""

import argparse
import asyncio
import glob
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, delete
from app.config import settings
from app.logging_config import logger
from app.db.session import get_session_factory, init_db
from app.db.models import TranscriptChunkModel
from app.rag.chunker import chunk_transcript
from app.rag.embeddings import embed_batch


async def ingest_directory(dir_path: str, clear_existing: bool = False):
    """Reads all markdown files from a directory and indexes chunks into the database."""
    logger.info(f"Starting ingestion from directory: {dir_path}")
    path = Path(dir_path)
    if not path.exists():
        logger.error(f"Directory does not exist: {dir_path}")
        return

    # Find all .md or transcript files
    md_files = list(path.glob("**/*.md"))
    if not md_files:
        logger.warning(f"No .md files found in {dir_path}")
        return

    logger.info(f"Found {len(md_files)} episode transcript files to process.")

    # Initialize DB schema
    await init_db()
    factory = get_session_factory()

    total_chunks_indexed = 0

    async with factory() as db:
        if clear_existing:
            logger.info("Clearing existing transcript chunks...")
            await db.execute(delete(TranscriptChunkModel))
            await db.commit()

        for file_path in md_files:
            # Episode ID from folder name or file stem
            episode_id = file_path.parent.name if file_path.name == "transcript.md" else file_path.stem
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Chunk transcript
                chunks = chunk_transcript(
                    content,
                    episode_id=episode_id,
                    chunk_size_words=settings.CHUNK_SIZE_TOKENS,
                    overlap_words=settings.CHUNK_OVERLAP_TOKENS,
                )

                if not chunks:
                    logger.warning(f"No chunks generated for {episode_id}")
                    continue

                # Batch embed chunks
                texts = [c["content"] for c in chunks]
                embeddings = embed_batch(texts)

                # Insert into database
                for c_data, emb in zip(chunks, embeddings):
                    chunk_row = TranscriptChunkModel(
                        episode_id=c_data["episode_id"],
                        guest=c_data["guest"],
                        title=c_data["title"],
                        youtube_url=c_data["youtube_url"],
                        timestamp=c_data["timestamp"],
                        chunk_index=c_data["chunk_index"],
                        content=c_data["content"],
                        embedding=emb,
                    )
                    db.add(chunk_row)

                await db.commit()
                total_chunks_indexed += len(chunks)
                logger.info(f"Indexed episode '{episode_id}' -> {len(chunks)} chunks.")

            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")

    logger.info(f"Ingestion complete! Total chunks indexed: {total_chunks_indexed}")


def main():
    parser = argparse.ArgumentParser(description="Ingest Lenny's Podcast transcripts into pgvector.")
    parser.add_argument(
        "--source",
        type=str,
        default=str(backend_dir / "data" / "sample_transcripts"),
        help="Path to directory containing transcript markdown files.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing transcript chunks before ingesting.",
    )
    args = parser.parse_args()

    asyncio.run(ingest_directory(args.source, clear_existing=args.clear))


if __name__ == "__main__":
    main()

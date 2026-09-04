"""
Transcript Parser and Recursive Speaker-Aware Chunker.
Splits podcast transcripts into 500-800 token chunks while preserving speaker turns and timestamps.
"""

import re
from typing import Any, Dict, List, Tuple
import yaml


TIMESTAMP_PATTERN = re.compile(r"^([A-Za-z0-9\s\.\-'\"]+)\s*\(([0-9]{1,2}:[0-9]{2}:[0-9]{2}|[0-9]{1,2}:[0-9]{2})\)\s*:", re.MULTILINE)
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(raw_text: str) -> Tuple[Dict[str, Any], str]:
    """Extracts YAML frontmatter and returns (metadata_dict, body_text)."""
    match = FRONTMATTER_PATTERN.match(raw_text)
    if not match:
        return {}, raw_text

    frontmatter_raw = match.group(1)
    body_text = raw_text[match.end():]
    try:
        metadata = yaml.safe_load(frontmatter_raw) or {}
    except Exception:
        metadata = {}

    return metadata, body_text


def chunk_transcript(
    raw_markdown: str,
    episode_id: str,
    chunk_size_words: int = 500,
    overlap_words: int = 100,
) -> List[Dict[str, Any]]:
    """
    Parses frontmatter and chunks transcript into speaker-tagged chunks.
    Each chunk records: episode_id, guest, title, youtube_url, timestamp, chunk_index, content.
    """
    metadata, body = parse_frontmatter(raw_markdown)
    guest = metadata.get("guest") or "Unknown Guest"
    title = metadata.get("title") or episode_id.replace("-", " ").title()
    youtube_url = metadata.get("youtube_url") or ""

    # Split body into speaker segments
    # Find all matches of "Speaker (HH:MM:SS):"
    matches = list(TIMESTAMP_PATTERN.finditer(body))
    segments: List[Dict[str, str]] = []

    if matches:
        for i in range(len(matches)):
            start_pos = matches[i].start()
            speaker = matches[i].group(1).strip()
            timestamp = matches[i].group(2).strip()
            # Normalize timestamp to HH:MM:SS
            if len(timestamp) == 5:
                timestamp = f"00:{timestamp}"

            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            segment_text = body[start_pos:end_pos].strip()
            segments.append({
                "speaker": speaker,
                "timestamp": timestamp,
                "text": segment_text,
            })
    else:
        # Fallback if no speaker timestamps found
        paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
        for p in paragraphs:
            segments.append({
                "speaker": guest,
                "timestamp": "00:00:00",
                "text": p,
            })

    # Group segments into chunks
    chunks: List[Dict[str, Any]] = []
    current_words: List[str] = []
    current_timestamp = segments[0]["timestamp"] if segments else "00:00:00"
    current_speaker = segments[0]["speaker"] if segments else guest
    chunk_index = 0

    for seg in segments:
        seg_words = seg["text"].split()
        if not current_words:
            current_timestamp = seg["timestamp"]
            current_speaker = seg["speaker"]

        current_words.extend(seg_words)

        if len(current_words) >= chunk_size_words:
            chunk_text = " ".join(current_words)
            chunks.append({
                "episode_id": episode_id,
                "guest": guest,
                "title": title,
                "youtube_url": youtube_url,
                "timestamp": current_timestamp,
                "chunk_index": chunk_index,
                "content": chunk_text,
            })
            chunk_index += 1
            # Keep overlap words
            current_words = current_words[-overlap_words:] if overlap_words > 0 else []

    # Final trailing chunk if sufficient content remains
    if current_words and len(current_words) > 50:
        chunk_text = " ".join(current_words)
        chunks.append({
            "episode_id": episode_id,
            "guest": guest,
            "title": title,
            "youtube_url": youtube_url,
            "timestamp": current_timestamp,
            "chunk_index": chunk_index,
            "content": chunk_text,
        })

    return chunks

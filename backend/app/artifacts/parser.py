"""
Artifact Tag Parser.
Detects and extracts <artifact ...>...</artifact> tags from generated content.
"""

import re
import uuid
from typing import Any, Dict, List, Tuple


ARTIFACT_REGEX = re.compile(
    r'<artifact\s+([^>]*?)>(.*?)(?:</artifact>|$)',
    re.DOTALL | re.IGNORECASE,
)
ATTR_REGEX = re.compile(r'([a-zA-Z0-9_\-]+)=["\'](.*?)["\']')


def parse_attributes(attr_string: str) -> Dict[str, str]:
    """Parses key-value pairs inside XML/HTML tag attributes."""
    matches = ATTR_REGEX.findall(attr_string)
    attrs = {}
    for key, val in matches:
        attrs[key.lower()] = val.strip()
    return attrs


def extract_artifacts(text: str) -> List[Dict[str, Any]]:
    """
    Finds all <artifact> tags in the text and returns a list of parsed artifact dicts.
    """
    artifacts = []
    matches = list(ARTIFACT_REGEX.finditer(text))

    for m in matches:
        attr_str = m.group(1)
        body = m.group(2).strip()

        attrs = parse_attributes(attr_str)
        artifact_type = attrs.get("type", "markdown").lower()
        if artifact_type not in ("markdown", "html"):
            artifact_type = "markdown"

        title = attrs.get("title") or "Generated Artifact"
        identifier = attrs.get("identifier") or f"artifact-{uuid.uuid4().hex[:8]}"

        artifacts.append({
            "identifier": identifier,
            "title": title,
            "artifact_type": artifact_type,
            "content": body,
        })

    return artifacts


def clean_text_for_chat(text: str) -> str:
    """
    Replaces raw <artifact>...</artifact> blocks with an elegant inline artifact reference card in chat.
    """
    def replace_match(match):
        attr_str = match.group(1)
        attrs = parse_attributes(attr_str)
        title = attrs.get("title", "Generated Artifact")
        artifact_type = attrs.get("type", "Document").upper()
        return f"\n\n> 📦 **Artifact Created:** *{title}* ({artifact_type})\n> *Viewing in side-by-side drawer on the right.* \n\n"

    return ARTIFACT_REGEX.sub(replace_match, text).strip()

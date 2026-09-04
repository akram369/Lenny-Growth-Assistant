"""
Unit Tests for Skills Engine (Ship 30 for 30 and Grounded QA).
"""

from app.skills.grounded_qa import build_grounded_qa_prompt
from app.skills.ship30 import build_ship30_prompt, SHIP_30_FRAMEWORK_INSTRUCTIONS


def test_grounded_qa_prompt_directives():
    context = "Source 1: Will Larson on treating engineers as adults."
    prompt = build_grounded_qa_prompt(context)

    # Must contain critical grounding directives
    assert "GROUNDING MANDATE" in prompt
    assert "[Episode: Guest Name, Timestamp]" in prompt
    assert "I do not have sufficient information in Lenny's podcast archive to answer this." in prompt
    assert "<artifact type=" in prompt
    assert context in prompt


def test_ship30_prompt_framework_heuristics():
    topic = "Product-Led Sales and PQL Conversion"
    chunks = [
        {
            "guest": "Elena Verna",
            "title": "B2B product-led sales",
            "timestamp": "00:04:00",
            "content": "PQLs convert at 3x to 5x the rate of MQLs.",
        }
    ]
    prompt = build_ship30_prompt(topic, chunks)

    # Check for Ship 30 for 30 specific framework rules
    assert "Ship 30 for 30" in prompt
    assert "HEADLINE & HOOK" in prompt
    assert "1,250 WORDS" in prompt or "1,250 words" in prompt
    assert "SKIMMABLE FORMATTING" in prompt
    assert "Atomic paragraphs" in prompt
    assert "Selective Bold Anchors" in prompt
    assert "ACTIONABLE TAKEAWAY" in prompt or "Actionable Takeaway" in prompt
    assert "<artifact type=\"markdown\"" in prompt
    assert "Elena Verna" in prompt

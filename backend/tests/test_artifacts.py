"""
Unit Tests for Artifact Parser and Extractor.
"""

from app.artifacts.parser import extract_artifacts, parse_attributes, clean_text_for_chat


def test_parse_attributes():
    attr_str = 'type="html" title="Pricing Calculator" identifier="pricing-calc"'
    attrs = parse_attributes(attr_str)
    assert attrs["type"] == "html"
    assert attrs["title"] == "Pricing Calculator"
    assert attrs["identifier"] == "pricing-calc"


def test_extract_markdown_artifact():
    text = """
Here is your requested memo:

<artifact type="markdown" title="Engineering Strategy Memo" identifier="eng-memo-1">
# Engineering Strategy
This is a grounded document about technical strategy.
</artifact>

I hope this helps your team.
"""
    artifacts = extract_artifacts(text)
    assert len(artifacts) == 1
    art = artifacts[0]
    assert art["artifact_type"] == "markdown"
    assert art["title"] == "Engineering Strategy Memo"
    assert art["identifier"] == "eng-memo-1"
    assert "# Engineering Strategy" in art["content"]


def test_extract_html_artifact():
    text = """
<artifact type="html" title="Growth Funnel Dashboard" identifier="funnel-widget">
<!DOCTYPE html>
<html>
<head><style>body { background: #000; }</style></head>
<body><h1>Funnel</h1></body>
</html>
</artifact>
"""
    artifacts = extract_artifacts(text)
    assert len(artifacts) == 1
    art = artifacts[0]
    assert art["artifact_type"] == "html"
    assert art["title"] == "Growth Funnel Dashboard"
    assert "<h1>Funnel</h1>" in art["content"]


def test_clean_text_for_chat():
    text = 'Before artifact <artifact type="markdown" title="Sprint Plan">Content</artifact> After artifact'
    cleaned = clean_text_for_chat(text)
    assert "<artifact" not in cleaned
    assert "Sprint Plan" in cleaned
    assert "Artifact Created" in cleaned
    assert "side-by-side drawer" in cleaned

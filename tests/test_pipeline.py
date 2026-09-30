"""Unit tests for the NL2KG Triplification Pipeline."""

import tempfile
from pathlib import Path
from pipelines.extract import extract_all_documents, parse_markdown_sections
from pipelines.loader import GraphLoader
from pipelines.schema import TriplifiedGraph
from pipelines.triplify import merge_graphs, triplify_document


def test_markdown_parsing_and_extraction():
    """Test extracting sections and headers from a markdown sample."""
    sample_content = """# Architecture Best Practice: Agent Security
#agent-security #sandboxing

## Pattern: Zero Ambient Authority
Agents execute with zero ambient authority to avoid confused deputy attacks.

## Pitfall: Hardcoded API Keys
Storing API keys in plain text causes credential leakage.
"""
    with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
        f.write(sample_content)
        f.flush()
        file_path = Path(f.name)

    try:
        parsed = parse_markdown_sections(file_path)
        assert parsed["title"] == "Architecture Best Practice: Agent Security"
        assert "agent-security" in parsed["tags"]
        assert len(parsed["sections"]) >= 2

        graph = triplify_document(parsed)
        assert len(graph.guidelines) == 1
        assert len(graph.patterns) == 1
        assert len(graph.antipatterns) == 1
        assert len(graph.implements_edges) == 1
    finally:
        file_path.unlink()


def test_graph_loader_json_export():
    """Test JSON export of triplified graph."""
    graph = TriplifiedGraph()
    loader = GraphLoader()
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / "test_triples.json"
        saved = loader.export_to_json(graph, out_file)
        assert saved.exists()
        assert saved.stat().st_size > 0

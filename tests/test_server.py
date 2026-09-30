"""Unit tests for FastMCP server tools and graph client."""

import pytest
from src.graph.client import GraphClient


@pytest.mark.asyncio
async def test_search_guidelines(graph_client: GraphClient):
    """Test searching guidelines by query."""
    results = await graph_client.search_guidelines(query="quality")
    assert len(results) > 0
    assert any("Quality" in r.title for r in results)


@pytest.mark.asyncio
async def test_search_guidelines_category_filter(graph_client: GraphClient):
    """Test searching guidelines with category filter."""
    results = await graph_client.search_guidelines(query="security", category="security")
    assert len(results) > 0
    for r in results:
        assert r.category == "security"


@pytest.mark.asyncio
async def test_get_guideline_by_id(graph_client: GraphClient):
    """Test retrieving guideline by ID."""
    g = await graph_client.get_guideline("DOC-01")
    assert g is not None
    assert g.guideline_id == "DOC-01"
    assert "Quality" in g.title


@pytest.mark.asyncio
async def test_get_pattern_mitigations(graph_client: GraphClient):
    """Test retrieving pattern and checking mitigations."""
    pattern = await graph_client.get_pattern("Zero Ambient Authority")
    assert pattern is not None
    assert pattern.pattern_id == "PAT-ZAA"
    assert "Credential Leakage" in pattern.mitigates


@pytest.mark.asyncio
async def test_evaluate_tradeoffs(graph_client: GraphClient):
    """Test evaluating tradeoffs between options."""
    evaluation = await graph_client.evaluate_tradeoffs("Memory Bank", "Custom Redis")
    assert evaluation.option_a == "Memory Bank"
    assert evaluation.option_b == "Custom Redis"
    assert "Memory Bank" in evaluation.recommendation

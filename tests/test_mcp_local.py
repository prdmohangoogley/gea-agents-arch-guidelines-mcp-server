"""Local FastMCP Server Integration Tests (Stdio Transport Subprocess).

Validates that:
1. FastMCP server runs cleanly in Stdio Subprocess mode.
2. 'get_best_practice' executes operational GQL lookup (<100ms Spanner latency).
3. 'deep_dive_guideline' executes analytical SQL/federated lookup via BigQuery.
4. Latency and error envelopes are properly formatted and resilient.
"""

from __future__ import annotations

import sys
import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport


@pytest.fixture
def stdio_transport() -> StdioTransport:
    """Fixture providing an StdioTransport pointing to src.server."""
    return StdioTransport(
        command=sys.executable,
        args=["-m", "src.server", "--transport", "stdio"],
    )


@pytest.mark.asyncio
async def test_stdio_server_tool_discovery(stdio_transport: StdioTransport):
    """Test starting FastMCP server in Stdio mode and discovering exposed tools."""
    async with Client(stdio_transport) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]

        assert "get_best_practice" in tool_names
        assert "deep_dive_guideline" in tool_names
        assert "search_guidelines" in tool_names
        assert "health_check" in tool_names


@pytest.mark.asyncio
async def test_get_best_practice_spanner_latency(stdio_transport: StdioTransport):
    """Test operational GQL query over stdio subprocess and assert latency < 100ms."""
    async with Client(stdio_transport) as client:
        result = await client.call_tool("get_best_practice", {"topic": "Quality"})

        assert not result.is_error
        data = result.structured_content

        # Assert status and source
        assert data["status"] in ("success", "degraded")
        assert "source" in data

        # Assert operational latency constraint (<100ms for Spanner)
        latency_ms = data.get("latency_ms", 0.0)
        assert latency_ms < 100.0, f"Spanner operational latency {latency_ms}ms exceeded 100ms threshold"

        # Assert valid guidelines and patterns returned
        assert "guidelines" in data
        assert "patterns" in data
        assert len(data["guidelines"]) > 0 or len(data["patterns"]) > 0


@pytest.mark.asyncio
async def test_deep_dive_guideline_bigquery_analytical(stdio_transport: StdioTransport):
    """Test analytical SQL query over stdio subprocess."""
    async with Client(stdio_transport) as client:
        result = await client.call_tool("deep_dive_guideline", {"component": "Security"})

        assert not result.is_error
        data = result.structured_content

        assert data["status"] in ("success", "degraded")
        assert "source" in data
        assert "latency_ms" in data
        assert "details" in data
        assert data["row_count"] > 0

        # Validate structure of first analytical item
        first = data["details"][0]
        assert "guideline_id" in first
        assert "title" in first


@pytest.mark.asyncio
async def test_error_and_fallback_resilience(stdio_transport: StdioTransport):
    """Test error envelope handling when querying an obscure or non-existent keyword."""
    async with Client(stdio_transport) as client:
        result = await client.call_tool("get_best_practice", {"topic": "xyz_obscure_topic_never_exists"})

        assert not result.is_error
        data = result.structured_content

        # Server must not crash and should return a valid envelope
        assert data["status"] in ("success", "degraded")
        assert "latency_ms" in data
        assert "source" in data

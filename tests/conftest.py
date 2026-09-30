"""Pytest fixtures and test setup."""

import pytest
from src.graph.client import GraphClient
from src.server import create_server


@pytest.fixture
def graph_client() -> GraphClient:
    """Provide a GraphClient seeded with mock test data."""
    return GraphClient(use_mock=True)


@pytest.fixture
def server():
    """Provide configured FastMCP server instance."""
    return create_server()

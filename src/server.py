"""FastMCP Server Application Entrypoint for Enterprise Agents Architectural Guidelines."""

from __future__ import annotations

import argparse
import sys
from fastmcp import FastMCP
from src.config import config
from src.graph.client import GraphClient
from src.otel_setup import setup_opentelemetry
from src.tools.guidelines import register_guideline_tools
from src.tools.health import register_health_tools
from src.tools.patterns import register_pattern_tools

# Initialize OpenTelemetry instrumentation
setup_opentelemetry("guidelines-mcp-server")


def create_server() -> FastMCP:
    """Instantiate and configure the FastMCP application."""
    mcp = FastMCP(
        name=config.server_name,
        instructions=(
            "Enterprise Agents Architectural Guidelines MCP Server. "
            "Use this server to query validated design patterns, trade-offs, "
            "security protocols, and deployment standards for AI agents on Google Cloud."
        ),
    )

    # Initialize graph client
    client = GraphClient(use_mock=config.use_mock_graph)

    # Register tools & resources
    register_health_tools(mcp)
    register_guideline_tools(mcp, client)
    register_pattern_tools(mcp, client)

    return mcp


mcp_server = create_server()


def main() -> None:
    """CLI entrypoint supporting both stdio and sse transports."""
    parser = argparse.ArgumentParser(description="Run the Enterprise Agents Guidelines MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default=config.transport,
        help="MCP transport protocol (stdio or sse)",
    )
    parser.add_argument("--host", default=config.host, help="Host to bind for SSE mode")
    parser.add_argument("--port", type=int, default=config.port, help="Port to bind for SSE mode")

    args = parser.parse_args()

    if args.transport == "sse":
        print(f"Starting FastMCP SSE server on {args.host}:{args.port}...", file=sys.stderr)
        mcp_server.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp_server.run(transport="stdio")


if __name__ == "__main__":
    main()

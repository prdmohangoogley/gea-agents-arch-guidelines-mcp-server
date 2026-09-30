"""Health and server status tools and resources."""

from fastmcp import FastMCP
from src.config import config


def register_health_tools(mcp: FastMCP) -> None:
    """Register health check and server info tools/resources."""

    @mcp.tool()
    async def health_check() -> str:
        """Verify server operational status and backend connectivity."""
        return (
            f"✅ **Server Status**: OK\n"
            f"- Server: `{config.server_name}` (v{config.server_version})\n"
            f"- Transport: `{config.transport}`\n"
            f"- Spanner Graph: `{config.spanner_instance_id}/{config.spanner_database_id}`\n"
            f"- Mock Mode: `{config.use_mock_graph}`"
        )

    @mcp.resource("resource://server/info")
    async def server_info() -> str:
        """Provide metadata and configuration summary for this MCP server."""
        return (
            f"Enterprise Agents Architectural Guidelines MCP Server\n"
            f"Version: {config.server_version}\n"
            f"Transport: {config.transport}\n"
            f"Project: {config.gcp_project_id}"
        )

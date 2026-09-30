"""FastMCP Server Configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    """MCP Server configuration settings."""

    model_config = SettingsConfigDict(env_prefix="MCP_", env_file=".env", extra="ignore")

    server_name: str = Field(default="gea-arch-guidelines-mcp", description="FastMCP Server Name")
    server_version: str = Field(default="0.1.0", description="Server semantic version")
    transport: str = Field(default="stdio", description="MCP transport mode: 'stdio' or 'sse'")
    host: str = Field(default="0.0.0.0", description="Host to bind for SSE mode")
    port: int = Field(default=8080, description="Port to bind for SSE mode")
    debug: bool = Field(default=False, description="Enable debug logging")

    # Cloud Data Store configurations
    gcp_project_id: str = Field(default="local-dev-project", description="GCP project ID")
    spanner_instance_id: str = Field(default="gea-arch-guidelines-spanner", description="Spanner instance ID")
    spanner_database_id: str = Field(default="arch_guidelines_graph", description="Spanner database ID")
    bq_dataset_id: str = Field(default="gea_arch_guidelines_analytics", description="BigQuery dataset ID")
    use_mock_graph: bool = Field(default=True, description="Use local mock knowledge store if Spanner is offline")


config = ServerConfig()

"""FastMCP Server Configuration."""

import os
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    """MCP Server configuration settings."""

    model_config = SettingsConfigDict(env_prefix="MCP_", env_file=".env", extra="ignore")

    server_name: str = Field(default="gea-arch-guidelines-mcp", description="FastMCP Server Name")
    server_version: str = Field(default="0.1.0", description="Server semantic version")
    transport: str = Field(
        default="stdio",
        validation_alias=AliasChoices("MCP_TRANSPORT", "TRANSPORT"),
        description="MCP transport mode: 'stdio' or 'sse'",
    )
    host: str = Field(
        default="0.0.0.0",
        validation_alias=AliasChoices("MCP_HOST", "HOST"),
        description="Host to bind for SSE mode",
    )
    port: int = Field(
        default=8080,
        validation_alias=AliasChoices("PORT", "MCP_PORT"),
        description="Port to bind for SSE mode",
    )
    debug: bool = Field(default=False, description="Enable debug logging")

    # Cloud Data Store configurations
    gcp_project_id: str = Field(
        default="fivedaysai-prd-sandbox-317383",
        validation_alias=AliasChoices("GCP_PROJECT_ID", "PROJECT_ID", "MCP_GCP_PROJECT_ID"),
        description="GCP project ID",
    )
    spanner_instance_id: str = Field(
        default="gea-arch-guidelines-spanner",
        validation_alias=AliasChoices("SPANNER_INSTANCE", "SPANNER_INSTANCE_ID", "MCP_SPANNER_INSTANCE_ID"),
        description="Spanner instance ID",
    )
    spanner_database_id: str = Field(
        default="arch_guidelines_graph",
        validation_alias=AliasChoices("SPANNER_DATABASE", "SPANNER_DATABASE_ID", "MCP_SPANNER_DATABASE_ID"),
        description="Spanner database ID",
    )
    bq_dataset_id: str = Field(
        default="gea_arch_guidelines_analytics",
        validation_alias=AliasChoices("BQ_DATASET", "BQ_DATASET_ID", "MCP_BQ_DATASET_ID"),
        description="BigQuery dataset ID",
    )
    use_mock_graph: bool = Field(
        default=False,
        validation_alias=AliasChoices("USE_MOCK_GRAPH", "MCP_USE_MOCK_GRAPH"),
        description="Use local mock knowledge store if Spanner is offline",
    )


config = ServerConfig()

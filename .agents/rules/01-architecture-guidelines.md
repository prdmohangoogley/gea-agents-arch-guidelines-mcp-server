# Architecture Guidelines: Enterprise Agents MCP Server

## 1. System Mission
`gea-agents-arch-guidelines-mcp-server` is an enterprise-grade Model Context Protocol (MCP) server that exposes validated AI agent architecture best practices, design patterns, and engineering tradeoffs to AI developer agents and human engineers.

## 2. Component Architecture
The architecture comprises three primary tiers:
1. **Knowledge Store Tier**:
   - **Google Cloud Spanner Graph**: Property graph storage for architectural entities (Patterns, Tradeoffs, Components, Antipatterns) and relational traversals.
   - **Google BigQuery**: Full-text and vector embeddings repository, audit logging, and analytic reporting on guideline utilization.
   - **Google Cloud Storage (GCS)**: Raw markdown knowledge bases, pipeline checkpoints, and validation datasets.
2. **Ingestion Tier (NL2KG Triplification Pipeline)**:
   - Natural Language to Knowledge Graph (NL2KG) extractor converting architectural documents into typed entity nodes and labeled relationships.
   - Schema validation enforcing strict ontology constraints before committing to Spanner Graph.
3. **Application & Serving Tier (FastMCP Server)**:
   - Built on `FastMCP` supporting dual transports: `stdio` (local IDE agents) and `sse` (Cloud Run managed service).
   - High-performance, asynchronous query handlers with structured Pydantic response models.

## 3. Storage Modeling & GQL Standards
- Always use ISO GQL (Graph Query Language) compatible queries against Cloud Spanner Graph.
- Graph entities MUST strictly adhere to the defined schema labels:
  - Nodes: `Guideline`, `Pattern`, `Tradeoff`, `Component`, `Antipattern`
  - Edges: `RELATES_TO`, `IMPLEMENTS`, `MITIGATES`, `REQUIRES`, `TRADES_OFF`
- All queries must be parametrized to eliminate injection vulnerabilities and optimize Spanner query plan caching.

## 4. MCP Server Conventions
- Use `FastMCP` decorators (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`).
- All tools must return clean, markdown-formatted outputs or structured Pydantic models.
- Support graceful degradation: if Spanner Graph is unreachable in local dev mode, provide informative fallback messaging or cached responses.
- Implement comprehensive health checks and telemetry.

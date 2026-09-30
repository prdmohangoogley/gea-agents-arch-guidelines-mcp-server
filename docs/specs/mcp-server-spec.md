# FastMCP Server Specification: Enterprise Agents Architectural Guidelines

## 1. Overview
The FastMCP Server exposes structured architectural knowledge about enterprise AI agents on Google Cloud to client agents (e.g. Antigravity, Claude Desktop, Cursor) and developer workflows.

## 2. Server Transport & Endpoints
- **stdio**: Standard Input/Output transport for local IDE and developer desktop integration.
- **sse**: Server-Sent Events over HTTP for remote deployments on Google Cloud Run.
  - Port: `8080` (configurable via `PORT` environment variable).
  - Health check endpoint: `GET /health`.
  - SSE endpoint: `GET /sse`.
  - Message endpoint: `POST /messages`.

## 3. FastMCP Tools Specification

### `search_guidelines`
- **Description**: Search enterprise agent architecture guidelines by query keywords, category, or topic tags.
- **Parameters**:
  - `query` (string, required): Free-text architectural query or topic (e.g., "memory bank", "ZAA", "A2A").
  - `category` (string, optional): Category filter (`quality`, `security`, `protocols`, `runtime`, `orchestration`, `skills`, `context`).
  - `limit` (integer, optional, default: 5): Maximum number of guidelines to return.
- **Returns**: Markdown formatted list of matching guidelines with summaries, key takeaways, and references.

### `get_guideline_details`
- **Description**: Retrieve complete architectural guideline details, best practices, and anti-patterns by guideline ID.
- **Parameters**:
  - `guideline_id` (string, required): Unique identifier of the guideline (e.g., `DOC-01`, `DOC-08`).
- **Returns**: Comprehensive guideline text, associated design patterns, and Mermaid diagrams.

### `query_architectural_pattern`
- **Description**: Query specific architectural design patterns and their graph relationships (implements, mitigates, requires).
- **Parameters**:
  - `pattern_name` (string, required): Name of the architectural pattern (e.g., "Zero Ambient Authority", "Memory Bank", "Progressive Disclosure").
- **Returns**: Pattern structure, tradeoffs, related components, and mitigation strategies.

### `evaluate_design_tradeoffs`
- **Description**: Evaluate pros, cons, and architectural tradeoffs between two competing design choices.
- **Parameters**:
  - `option_a` (string, required): First architectural approach (e.g., "Platform-Native Managed Memory").
  - `option_b` (string, required): Second architectural approach (e.g., "Self-Managed Redis Memory").
- **Returns**: Comparative tradeoff matrix with latency, operational complexity, security, and cost dimensions.

## 4. MCP Resources
- `resource://guidelines/index`: JSON manifest of all available architectural guidelines and metadata.
- `resource://ontology/schema`: Graph ontology schema defining entities and edge relationships.

# Validation and Evaluation Plan

## 1. Scope
This plan details the testing, benchmarking, and evaluation strategy for the Enterprise Agents Architectural Guidelines MCP Server and its underlying Spanner Graph data store.

## 2. Evaluation Dimensions

### A. Retrieval Quality (Hit Rate & MRR)
- **Goal**: Measure whether natural language architectural queries retrieve the expected guidelines and patterns.
- **Dataset**: `tests/evals/golden_dataset.json` containing 50+ curated architecture queries across topics (Security, State Management, MCP, A2A, Quality, SDLC).
- **Target Metrics**:
  - Hit Rate @ 3 >= 90%
  - Mean Reciprocal Rank (MRR) >= 0.85

### B. Graph Traversal Integrity
- **Goal**: Verify that multi-hop GQL queries (e.g., Pattern -> Mitigates -> Antipattern) maintain structural consistency without orphan nodes.
- **Test Suite**: `tests/test_pipeline.py`.

### C. FastMCP Protocol Compliance
- **Goal**: Validate that all tools and resources comply with MCP 2024-11-05+ schema specifications over both `stdio` and `sse` transports.
- **Test Suite**: `tests/test_server.py`.

### D. Performance & Latency SLAs
- **Goal**: FastMCP tool execution latency must meet real-time agent pair programming requirements.
- **SLA**:
  - Local stdio tool latency: < 50ms (in-memory / cached), < 300ms (remote Spanner).
  - SSE Cloud Run p95 latency: < 500ms.

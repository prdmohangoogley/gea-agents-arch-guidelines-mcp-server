# AGY Goal: Phase 4 - FastMCP Server & Local Integration Tests

## 📌 Context
Build the FastMCP server. Before deploying to Cloud Run, we must write a local test suite to verify the GQL (Spanner) and SQL (BigQuery) queries work correctly.

---

## 🛠️ Tasks
1. Implement `src/server.py` using **FastMCP** (Streamable HTTP/SSE transport).
2. Expose the **Agent Tools**:
   - `get_best_practice(topic: str)`: Operational GQL lookup.
   - `deep_dive_guideline(component: str)`: Analytical SQL/Federated lookup.
3. Implement `tests/test_mcp_local.py`:
   - Start the MCP server locally in **Stdio mode** (Subprocess).
   - Use a FastMCP client to invoke `get_best_practice` and `deep_dive_guideline`.
   - Assert that the returned payloads contain valid guidelines and adhere to expected latency (<100ms for Spanner).
4. Generate the `Dockerfile` for Cloud Run.

## ✅ Acceptance Criteria
- `pytest tests/test_mcp_local.py` passes 100%.
- Latency and Error Envelopes are handled correctly in the tool responses.

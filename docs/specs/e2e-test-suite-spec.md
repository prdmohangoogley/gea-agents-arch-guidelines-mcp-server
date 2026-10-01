# AGY Goal: Phase 5 - Cloud Deployment & End-to-End Testing

## 📌 Context
Deploy the MCP server to Cloud Run and run the final End-to-End validation to prove Token Economics, Latency, and Precision metrics are met.

---

## 🛠️ Tasks
1. **Deploy:** Containerize and deploy the MCP server to **Google Cloud Run** using `gcloud run deploy --functional-type=mcp-server`.
2. **E2E Testing Harness:** Implement `tests/test_mcp_remote.py`.
   - The test connects to the live **Cloud Run URL** with OIDC authentication.
   - It performs sequential calls to simulate an agent (like Cancer Co-scientist):
     - Query a topic (Spanner).
     - Trigger a fallback (BigQuery) by querying obscure/historical data.
   - **Metrics Validation:**
     - Assert Spanner latency is < 100ms (P95).
     - Assert BigQuery fallback maintains P85+ latency goals while maximizing recall.
3. Generate `.agents/rules/constitution.md` with guidelines on how downstream agents should invoke this service.

## ✅ Acceptance Criteria
- Remote tests pass against the live Cloud Run endpoint.
- Cloud Run scales to zero and handles authenticated invocations correctly.

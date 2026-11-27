# AGY Goal: Phase 5 - Cloud Deployment & End-to-End Testing

## 📌 Context
Deploy the MCP server and ADK agents natively to **Gemini Enterprise / Vertex AI Agent Engine (`google-adk` / `AdkApp`)** (with an optional **Cloud Run frontend / web deployment layer** over it) and run End-to-End validation to prove Token Economics, Latency, Retrieval IR/ROUGE-L, and 58-skill Trajectory metrics are met.

---

## 🛠️ Tasks
1. **Deploy:** Deploy the ADK Agent & MCP runtime to **Gemini Enterprise / Vertex AI Agent Engine** via `scripts/deploy_reasoning_engine.py` and `scripts/deploy_okf_evolution_engine.py` (with an optional Cloud Run frontend/web portal layered over the deployed Agent Engine & MCP server).
2. **E2E Testing Harness:** Implement `tests/test_mcp_remote.py`, `tests/test_all_38_skills_runbook.py` (all 58 skills), and live Vertex AI Agent Engine experimental trace suites (`scripts/populate_online_eval_traces.py`).
   - Connects to the live **Vertex AI Agent Engine** (`reasoningEngines/<id>`) and optional Cloud Run frontend with OIDC/ADC authentication.
   - Exercises Spanner Graph lookups, BigQuery fallback, and all 7 engineering rubric suites.
   - **Metrics Validation:**
     - Assert Spanner latency is `< 100ms` (p95), retrieval Hit Rate@k `>= 80%`, MRR `>= 0.35`, and `100%` pass rate across all 58 skills.
3. Verify `.agents/rules/01-architecture-guidelines.md` and `docs/architecture.md` stay synchronized with the deployed topology.

## ✅ Acceptance Criteria
- Remote and live Vertex AI Agent Engine evaluations pass (`OnlineEvaluator` active).
- Optional Cloud Run frontend layer scales to zero and forwards authenticated requests cleanly to Gemini Enterprise / MCP.

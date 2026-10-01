# Enterprise AI Agent Development Constitution

> **Status:** Active & Enforced  
> **Authority:** Enterprise Architecture & Security Review Board (GEA)  
> **Server Endpoint:** `https://gea-agents-arch-guidelines-mcp-server-301802433103.us-central1.run.app`  
> **Knowledge Stores:** Cloud Spanner Graph (`arch_guidelines_graph`), BigQuery (`gea_arch_guidelines_analytics`)

---

## Article I: Zero Ambient Authority (ZAA)

1. **No Implicit Privilege:** AI agents, tools, and background subagents must never run with ambient, default, or unauthenticated privileges. Every interaction must carry an explicitly scoped identity.
2. **Workload Identity Federation:** All GCP interactions (Cloud Spanner, BigQuery, GCS, Cloud Trace) must utilize Google Application Default Credentials (ADC) or Workload Identity. Hardcoded keys, service account JSON files, and static bearer tokens are strictly forbidden.
3. **Just-In-Time Downscoping:** Agents performing actions on behalf of a user must downscope privileges just-in-time to the minimum surface area required for that specific tool call.

---

## Article II: Mandatory Model Armor Protection & Prompt Injection Defense

1. **Edge Prompt Sanitization:** All incoming user prompts, agent instructions, and dynamic parameters routed to MCP tools must pass through **Google Cloud Model Armor** (`mcp-prompt-armor-template`) before tool dispatch.
2. **Deterministic Interception:** Any query triggering `MATCH_FOUND` on prompt injection, jailbreaking (`pi_and_jailbreak`), or sensitive data leakage (`sdp`) must be rejected immediately with an immutable security envelope:
   ```json
   {
     "status": "blocked",
     "source": "model_armor",
     "error": "Input rejected by Model Armor: potential prompt injection or policy violation detected."
   }
   ```
3. **Defense-in-Depth Heuristics:** In the event of network disruption or offline execution, local heuristic scanners must enforce identical blocking decisions. Fail-secure semantics must be maintained at all times.

---

## Article III: Architectural Guidelines Knowledge Retrieval Protocol

1. **Operational vs. Analytical Routing:**
   - **Low-Latency Operational Queries (< 50ms):** Use `get_best_practice(topic)` to execute property graph lookups in **Cloud Spanner Graph**.
   - **Analytical & Compliance Deep Dives (< 2500ms):** Use `deep_dive_guideline(component)` to execute zero-ETL BigQuery federated graph queries.
2. **Knowledge Integrity:** Guidelines and design patterns must originate from validated OKF markdown corpora ingested through the automated NL2KG pipeline. Manual node insertion into production graph stores without cryptographic SHA-256 verification is prohibited.

---

## Article IV: Observability & Audit Compliance

1. **Distributed Tracing:** Every tool invocation must be instrumented using OpenTelemetry (`opentelemetry-api` and `opentelemetry-sdk`) and exported to Google Cloud Trace.
2. **Audit Logging:** Tool name, sanitized topic, security decision, query execution latency, and return status must be recorded in Cloud Monitoring and BigQuery audit tables (`mcp_query_audit_logs`).
3. **Zero PII Exposure:** User personally identifiable information (PII) must never be logged in Cloud Trace span attributes or stdout container streams.

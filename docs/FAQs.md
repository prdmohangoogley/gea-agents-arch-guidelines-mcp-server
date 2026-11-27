# Frequently Asked Questions (FAQs)

<!-- AI_ML_RUBRIC_FAQS_START -->
## AI/ML Engineering Rubric FAQs

> This section documents how the **Enterprise Agents Architectural Guidelines MCP Server** (`architecture_best_practices_mcp`) demonstrates competency across all **5 domains** and **21 sub-criteria** of the **AI/ML Engineering Rubric** (**Overall Verdict: PASS — 5/5 Domains, 21/21 Sub-Criteria at Competent or Exemplary level**).

| # | Rubric Domain | Competent Criteria | Required Cutline | Status |
|---:|:---|---:|---:|:---|
| 1 | Agentic & Multi-Agent Systems | 5 / 5 | >= 2 | **PASS** |
| 2 | Retrieval & Data Engineering for AI | 5 / 5 | >= 1 | **PASS** |
| 3 | Model Selection, Tuning & Optimization | 5 / 5 | >= 2 | **PASS** |
| 4 | LLM Ops and Evaluation | 3 / 3 | >= 1 | **PASS** |
| 5 | Domain-Applied AI/ML Expertise | 3 / 3 | >= 1 | **PASS** |

---

### 1. Agentic & Multi-Agent Systems

**Q1.1: How does this project design cognitive architectures and orchestration patterns aligned with Critical User Journeys (CUJs)?**
**A:** The system implements a layered cognitive architecture anchored by a Google ADK `Agent` wrapped in `vertexai.agent_engines.AdkApp` (`src/agent/adk_agent.py`) and `EnterpriseArchGuidelinesAgent` (`src/agent/reasoning_engine.py`). To avoid prompt bloat across 29 FastMCP tools and 41 skills, `src/registry/skills_registry.py` enforces **Two-Tier Progressive Disclosure** (Tier 1 lightweight catalog at ~30 tokens/skill; Tier 2 on-demand manifest hydration), directly aligning with developer and architect CUJs in Antigravity, VS Code, and Gemini Enterprise.

**Q1.2: How are planning, reasoning loops, session memory, and state management handled without infinite execution loops?**
**A:** Session lifecycle and streaming state are managed via ADK's standard session contract (`async_create_session`, `async_stream_query`) in `src/agent/adk_agent.py`, complemented by long-term session feedback persistence in `src/telemetry/session_feedback.py` and the `PAT-MEM-BANK` pattern in `src/graph/client.py`. Iterative workflows such as `AIMLRubricAssessmentFeedbackResolutionSkill` (`src/skills/plugins/ai_ml_rubric.py`) enforce bounded `max_iterations` loop guards, while `ModelArmorSanitizer` (`src/security/model_armor.py`) enforces a rolling circuit breaker (`failure_threshold=3`, `cooldown_seconds=60.0`) to prevent retry storms.

**Q1.3: How does tool/function calling integrate with external APIs while respecting data boundaries and system security?**
**A:** All 29 FastMCP tools (`src/tools/`) and 41 dynamically discovered skills (`src/skills/discovery.py`) enforce **Zero Ambient Authority (ZAA)**, explicit `sandbox_tier` declarations (`read_only`, `workspace_write`, `infra_deploy`), and **Dual-Pass Model Armor** (`src/security/model_armor.py`): Pass 1 blocks prompt injections, SQL/Cypher injection, and SSRF (`169.254.169.254` / `metadata.google.internal`) on ingress, while Pass 2 applies Cloud DLP + deterministic regex redaction on egress.

**Q1.4: How are multi-agent interactions coordinated in production-ready workflows?**
**A:** `src/agent/adk_agent.py` coordinates specialized agents — `EnterpriseArchGuidelinesAgent` for real-time architecture & governance reviews and `OKFEvolutionReasoningEngine` (`src/agent/okf_evolution_reasoning_engine.py`) for autonomous knowledge-base freshness & evolution — alongside composable skill orchestration (e.g., `skill_ai_ml_rubric_assessment_feedback_resolution` chaining assessment, library remediation skills, and iterative re-assessment).

**Q1.5: How does the system meet enterprise latency SLAs and maintain graceful error handling?**
**A:** Model Armor enforces a strict interactive timeout (`150ms` default) with automatic circuit-breaker failover to `<1ms` local heuristic guardrails. Both `GraphClient` (`src/graph/client.py`) and `MultiModelRouter` (`src/models/router.py`) implement multi-tier failover and deterministic grounded fallbacks so transient cloud or network outages degrade gracefully without crashing user sessions.

---

### 2. Retrieval & Data Engineering for AI

**Q2.1: What RAG architecture patterns, embedding models, and vector/graph databases are implemented?**
**A:** The project implements a tiered **GraphRAG + Analytical Vector RAG** architecture: **Cloud Spanner Graph** (`ArchGuidelinesGraph`, ISO GQL property graph with `Guideline`, `Pattern`, `Antipattern`, `Tradeoff`, and `FDERubricItem` nodes) for sub-100ms operational traversal, paired with **BigQuery** (`guideline_embeddings` and audit tables) and **Dataplex Universal Catalog** hosting the 92-concept OKF v0.2 corpus (`L200`, `L300`, `L400`, `OKF-PCA-01..09`), using the encoder-only `gemini-embedding-001` model registered in `src/models/router.py`.

**Q2.2: How are chunking, indexing, and hybrid search configured to maximize retrieval precision?**
**A:** `GraphClient.hybrid_search_guidelines()` (`src/graph/client.py`) implements **Reciprocal Rank Fusion (RRF)** (`RRF(d) = sum(1 / (k + rank_i(d)))`, `k=60`) fusing lexical BM25-style token scoring (title 2x, summary 1x) with structural category/pattern-link affinity scoring, alongside parameterized Spanner Graph ISO GQL queries (`src/graph/queries.py`) and BigQuery SQL joins.

**Q2.3: How do grounding and citation mechanisms mitigate hallucinations?**
**A:** Every ingested OKF concept carries verifiable provenance metadata (`guideline_id`, `source_url`, `content_sha256`, `version_tag`, and 6-month `stale_after` TTL in `pipelines/nl2kg_pipeline.py`). Retrieval tools return explicit concept IDs (`DOC-01..09`, `OKF-PCA-01..09`) and source URLs grounded in the Cloud FDE Charter.

**Q2.4: How do data pipelines parse complex document formats such as Markdown/HTML tables?**
**A:** `pipelines/nl2kg_pipeline.py` orchestrates the NL2KG (Natural Language to Knowledge Graph) triplification pipeline with `preserve_document_layout()` to retain Markdown lists, indentation, and tabular structures, extracting typed Pydantic ontology nodes (`GuidelineNode`, `PatternNode`, `AntipatternNode`, `TradeoffNode`, `FDERubricItemNode`) and directed `GraphEdge` triples for Spanner Graph and BigQuery ingestion.

**Q2.5: How is retrieval quality validated against business requirements to ensure data trust?**
**A:** `tests/evals/test_retrieval_quality.py` validates retrieval against `tests/evals/golden_dataset.json` using deterministic IR thresholds (`Hit Rate@k >= 0.80`, `MRR >= 0.35`, `Precision@k`, `Recall@k`, `F1`, and `ROUGE-L F1`), while `scripts/crc32c_verify.py` and `check_okf_freshness` enforce corpus integrity and 6-month TTL freshness.

---

### 3. Model Selection, Tuning & Optimization

**Q3.1: How does the project assess and select models balancing quality, latency, cost, and context window?**
**A:** `src/models/router.py` implements `MultiModelRouter` and `MODEL_REGISTRY` spanning Gemini 3.1+/4 Argon, GPT-5/o3, and Claude 5.* mapped to 6 operational `ModelTier` classes (`JUDGE`, `REASONING_FRONTIER`, `ROUTING_FAST`, `AUDIT_SOCRATIC`, `FORMAL_VERIFICATION`, `EMBEDDING_ENCODER`). Each `ModelSpec` tracks `max_context_tokens` (up to 2M tokens), `supports_thinking`, and `supports_tools`, with automatic failover and a strict **Zero Legacy Policy** blocking deprecated checkpoints (`2.5`, `2.0`, `1.5`, `gpt-3.5`).

**Q3.2: What inference optimization and cost/token compression techniques are implemented?**
**A:** `MultiModelRouter` implements deterministic **KV Prefix Context Caching** (`compute_prefix_cache_key`, tracking cache hits/misses), while `SkillsRegistry` enforces **Two-Tier Progressive Disclosure** achieving >80% prompt token savings per turn, tracked via `token_metrics` (`prompt_tokens_estimated`, `completion_tokens_estimated`, `tokens_saved_by_cache`) in `src/skills/base.py`.

**Q3.3: How are prompt engineering and structured JSON output enforcement implemented?**
**A:** `MultiModelRouter.generate_structured()` (`src/models/router.py`) enforces structured JSON output (`response_mime_type='application/json'`) by injecting the target Pydantic `model_json_schema()` into the system instruction and validating responses via `response_schema.model_validate()`, guaranteeing schema-conforming outputs for downstream programmatic consumers.

**Q3.4: How is data engineering (preparation, labeling, synthetic generation) managed?**
**A:** The repository maintains curated, schema-validated evaluation datasets (`tests/evals/golden_dataset.json`, `trajectory_dataset.json`, `model_armor_trajectory_dataset.json`, `skills_trajectory_dataset.json`) alongside automated OKF corpus ingestion, merging, and manifest generation scripts (`pipelines/nl2kg_pipeline.py`, `scripts/generate_okf_manifest.py`, `scripts/merge_and_extend_okf.py`).

**Q3.5: How does the project select optimal model architectures (encoder vs. decoder)?**
**A:** `ModelSpec.architecture` in `src/models/router.py` explicitly distinguishes **encoder-only** models (`gemini-embedding-001`, `tier=ModelTier.EMBEDDING_ENCODER`, `architecture="encoder"`) for dense vector embedding & retrieval from **decoder-only** frontier LLMs (`gemini-4-argon`, `gemini-3.1-pro`, `claude-5-sonnet`, `gpt-5`, `architecture="decoder"`) for multi-step reasoning, specification synthesis, and Socratic critique.

---

### 4. LLM Ops and Evaluation

**Q4.1: How does the evaluation methodology go beyond LLM-as-a-Judge?**
**A:** The project combines deterministic IR, NLG, and trajectory metrics with LLM-as-a-Judge:
- **Retrieval IR Metrics** (`tests/evals/test_retrieval_quality.py`): `Hit Rate@k` (`>= 0.80`), `Precision@k`, `Recall@k`, `F1 Score`, and `Mean Reciprocal Rank (MRR >= 0.35)`.
- **Deterministic NLG Faithfulness** (`tests/evals/test_retrieval_quality.py`): `ROUGE-L F1` computed via exact Longest Common Subsequence (LCS).
- **Agent Trajectory Metrics** (`tests/evals/test_trajectory_evals.py`): `Tool Selection Precision (TSP >= 0.90)` and `Argument Accuracy (AA >= 0.95)` plus invariant assertions.
- **Security Defense Evals** (`tests/evals/test_model_armor_trajectory_evals.py`): 100% deterministic interception of prompt injections and PII/secret exfiltration.

**Q4.2: How are evaluation datasets designed and executed across both automated and human evaluation?**
**A:** Automated evaluation executes via `pytest` against 4 versioned JSON datasets in `tests/evals/` plus full end-to-end execution of all 41 skills in `tests/test_all_38_skills_runbook.py`. Human-in-the-loop (HITL) evaluation and session quality ratings are captured via the `record_session_feedback` FastMCP tool (`src/telemetry/session_feedback.py`).

**Q4.3: How are regressions detected and observability (tracing/logging) implemented?**
**A:** `src/otel_setup.py` configures **OpenTelemetry OTLP over gRPC** exporting spans directly to **Google Cloud Trace** (`telemetry.googleapis.com:443`) with ADC authentication and graceful local OTLP fallback. Continuous production monitoring and online eval trace population are automated via `scripts/setup_online_monitor.py` and `scripts/populate_online_eval_traces.py`, while `pytest` CI gates block regressions across all tools, skills, and eval thresholds.

---

### 5. Domain-Applied AI/ML Expertise

**Q5.1: How are vertical-specific business KPIs translated into AI/ML objectives and architectures?**
**A:** Enterprise cloud architecture governance KPIs are translated into quantitative AI/ML SLOs: **FDE Field-Readiness Composite Score `>= 2.0/3.0`** with zero `0.0` disqualifiers (`src/skills/plugins/fde_rubric_critique.py`), **Google Landing Metrics** (`TTFT <= 250ms`, `p99 <= 600ms`, `Cloud CDN Hit Ratio >= 95%`), and **>80% token cost compression** via Two-Tier Progressive Disclosure.

**Q5.2: How are domain-specific data handling, regulatory compliance, and privacy (e.g., HIPAA, FINRA, PCI-DSS) enforced?**
**A:** `src/security/model_armor.py` enforces egress Sensitive Data Protection (SDP/DLP) redacting SSNs, credit card numbers (PCI-DSS), GCP API keys, OAuth bearer tokens, and private keys. Domain WAF verification skills (`src/skills/plugins/waf_okf_pillars.py`) enforce HIPAA, FINRA, and PCI-DSS architectural controls including Cloud KMS CMEK, VPC Service Controls (VPC-SC), Confidential GKE, and Zero Ambient Authority.

**Q5.3: How does the AI solution integrate with industry-standard legacy systems and enterprise workflows?**
**A:** The platform exposes standard **Model Context Protocol (MCP)** over `stdio` and `SSE` (`src/server.py`, `src/mcp_adapter.py`) for Antigravity, VS Code, Cursor, and Claude Desktop; publishes natively to **Gemini Enterprise / Vertex AI Agent Engine** (`scripts/publish_gemini_enterprise.sh`); integrates with **Dataplex Universal Catalog** (`scripts/register_knowledge_catalog.sh`); and validates enterprise **Terraform HCL** IaC (`iac/`, `src/skills/plugins/terraform_infra.py`).
<!-- AI_ML_RUBRIC_FAQS_END -->

---

<!-- SECURITY_PRIVACY_COMPLIANCE_FAQS_START -->
## Security, Privacy & Compliance FAQs

> Plain-English, direct answers explaining how the **Enterprise Agents Architectural Guidelines MCP Server** (`architecture_best_practices_mcp`) handles authentication, network security, data protection, AI-specific guardrails, and compliance — with exact file paths and tests so you can verify every single claim yourself (**Rubric Verdict: PASS — 5/5 Domains, 10/10 Sub-Criteria at Competent or Exemplary level**).

| # | Security, Privacy & Compliance Domain | Competent Criteria | Required Cutline | Status |
|---:|:---|---:|---:|:---|
| 1 | Authentication & Authorization | 2 / 2 | >= 2 | **PASS** |
| 2 | Infrastructure & Network Security | 2 / 2 | >= 2 | **PASS** |
| 3 | Data Protection & Privacy | 2 / 2 | >= 2 | **PASS** |
| 4 | AI-Specific Security | 2 / 2 | >= 2 | **PASS** |
| 5 | Compliance & Governance | 2 / 2 | >= 1 | **PASS** |

---

### 1. Authentication & Authorization

**Q: How does this project authenticate to Google Cloud services without leaking static API keys or JSON credentials?**
**A:** Zero static service account keys are used anywhere in the runtime or Terraform IaC. All Google Cloud calls authenticate via Application Default Credentials (ADC) / OAuth2 bearer tokens scoped to the exact API needed — you can check `google.auth.default(scopes=["https://www.googleapis.com/auth/trace.append"])` in `src/otel_setup.py` and `ModelArmorSanitizer._init_auth()` in `src/security/model_armor.py`. Even in our Terraform verification rules (`src/skills/plugins/terraform_infra.py`), creating a `google_service_account_key` is flagged immediately as a security violation.

**Q: How do I verify that Least Privilege is actually enforced across IAM and agent tools?**
**A:** Every skill in the registry declares an explicit `sandbox_tier` (`read_only`, `workspace_write`, `analytics_read`, or `infra_deploy`) in `src/skills/base.py`, and our architecture enforces **Zero Ambient Authority (ZAA)** (`PAT-ZAA` in `src/graph/client.py` and `.agents/rules/03-security-rules.md`). For IAM, the `waf-pillar-security` and `terraform-waf-verifier` skills deterministically flag primitive `roles/owner` or `roles/editor` bindings and enforce least-privilege Workload Identity roles.

---

### 2. Infrastructure & Network Security

**Q: How are VPC networking, private endpoints, and zero-trust boundaries designed and enforced here?**
**A:** The core MCP server and ADK agents run natively on Google Cloud's managed **Gemini Enterprise / Vertex AI Agent Engine (`google-adk`)** (`scripts/deploy_reasoning_engine.py`), with an optional **Cloud Run frontend / web deployment layer** sitting over that backend for browser/portal UIs. Across our architecture specs and Terraform WAF checks (`src/skills/plugins/waf_okf_pillars.py` & `src/skills/plugins/terraform_infra.py`), we enforce Private Google Access, segmented subnets, Confidential GKE/VM isolation, and Identity-Aware Proxy (IAP) zero-trust access.

**Q: What service perimeters, firewall policies, and SSRF protections keep enterprise assets locked down?**
**A:** At the application boundary, `HEURISTIC_INJECTION_PATTERNS` in `src/security/model_armor.py` (line 33) explicitly blocks SSRF probes against cloud metadata endpoints (`169.254.169.254`, `metadata.google.internal`, `metadata.goog`), plus SQL/Cypher injection (`drop table`, `detach delete`). At the cloud perimeter, `waf_okf_pillars.py` enforces **VPC Service Controls (VPC-SC)** with Access Context Manager ingress/egress rules and **Cloud Armor** WAF firewall policies.

---

### 3. Data Protection & Privacy

**Q: How does the project encrypt data in transit/at rest and stop PII from leaking out?**
**A:** All telemetry and API traffic runs over TLS / gRPC SSL (`grpc.ssl_channel_credentials()` in `src/otel_setup.py`), while storage modules (`iac/modules/spanner`, `iac/modules/bq`, `iac/modules/gcs`) and WAF checks enforce encryption at rest and Cloud KMS CMEK. For PII and Sensitive Data Protection (SDP/DLP), check `HEURISTIC_EGRESS_PATTERNS` in `src/security/model_armor.py` (lines 38–78): every tool response passes through egress DLP redaction that masks SSNs (`[REDACTED_SSN]`), credit card numbers (`[REDACTED_CREDIT_CARD]`), and secrets before anything leaves the server. You can run `pytest tests/test_model_armor.py` to watch it work live.

**Q: Where are secrets stored, and how can I check that nothing sensitive is hardcoded?**
**A:** Secrets and runtime config are injected via environment variables / Secret Manager (`.env` is gitignored in `.gitignore`, and Terraform state is stored remotely in GCS via `iac/backend.tf`, never locally). On top of that, `src/security/model_armor.py` automatically strips accidental `AIza...` GCP API keys (`[REDACTED_GCP_API_KEY]`), `ya29...` OAuth tokens (`[REDACTED_BEARER_TOKEN]`), private keys (`[REDACTED_PRIVATE_KEY]`), and `client_secret`/`db_password` assignments on egress — verified directly by `traj_model_armor_egress_dlp` in `tests/evals/trajectory_dataset.json`.

---

### 4. AI-Specific Security

**Q: What actually stops prompt injection, jailbreaks, or unsafe outputs from getting through?**
**A:** Every user prompt and tool output passes through **Dual-Pass Model Armor** (`src/security/model_armor.py` & `src/agent/reasoning_engine.py`): Pass 1 inspects ingress prompts against Google Cloud Model Armor (with a strict `150ms` timeout and rolling circuit breaker that fails over to `<1ms` local heuristic injection rules so protection never drops), and Pass 2 sanitizes egress responses in fail-closed mode (`_sanitize_output` returns `[REDACTED BY MODEL ARMOR EGRESS DLP]` on policy match or error). You can verify 100% interception in `tests/evals/test_model_armor_trajectory_evals.py`.

**Q: How does the project control which AI models can run and enforce content safety?**
**A:** `src/models/router.py` enforces an explicit **Model Allow-List (`MODEL_REGISTRY`)** and a **Zero Legacy Policy (`PROHIBITED_LEGACY_PATTERNS`)** that raises hard validation errors if any deprecated or unapproved checkpoint (`2.5`, `2.0`, `1.5`, `gpt-3.5`, etc.) is requested — verified by `tests/test_model_router.py`. Content safety (CSAM, prompt injection, jailbreak, SDP) is enforced via Cloud Model Armor templates before any model call executes.

---

### 5. Compliance & Governance

**Q: Where do audit logs live, and how does the project handle data residency and regulatory requirements?**
**A:** Every agent invocation, tool call, and span is exported via OpenTelemetry OTLP/gRPC (`src/otel_setup.py`) to **Google Cloud Trace**, with BigQuery analytical/audit tables (`iac/modules/bq`) and GCS telemetry logs (`LOGS_BUCKET_NAME`). Data residency (`us-central1` / `constraints/gcp.resourceLocations`) and HIPAA/FINRA/PCI-DSS regulatory requirements are codified in our Terraform variables (`iac/variables.tf`) and verified by `skill_waf_pillar_security` and `skill_security_privacy_compliance_assessor_feedback`.

**Q: How is enterprise policy enforced automatically across deployments?**
**A:** Governance isn't a manual checklist — it's wired into automated test and audit gates:
- **44-skill Runbook Gate** (`tests/test_all_38_skills_runbook.py`) and **Independent Trajectory Evaluations** (`tests/evals/test_skills_trajectory_evals.py` & `tests/evals/test_trajectory_evals.py`).
- **FDE Field-Readiness Rubric (`>= 2.0` cutline, `0.0` immediate pause)** in `src/skills/plugins/fde_rubric_critique.py`.
- **Terraform WAF Compliance & Drift Comparator** (`src/skills/plugins/terraform_infra.py`) and **Vertex AI Online Monitor** (`scripts/setup_online_monitor.py`) continuously scoring live production traces.
<!-- SECURITY_PRIVACY_COMPLIANCE_FAQS_END -->

---

<!-- RELIABILITY_RESILIENCE_FAQS_START -->
## Reliability & Resilience FAQs

> Direct, verifiable pointers to the exact files, classes, tests, and infrastructure where the **Enterprise Agents Architectural Guidelines MCP Server** (`architecture_best_practices_mcp`) implements availability design, observability, failure/recovery testing, and graceful degradation (**Rubric Verdict: PASS — 4/4 Domains, 8/8 Sub-Criteria at Competent or Exemplary level**).

| # | Reliability & Resilience Domain | Competent Criteria | Required Cutline | Status |
|---:|:---|---:|---:|:---|
| 1 | Availability Design | 2 / 2 | >= 1 | **PASS** |
| 2 | Observability | 2 / 2 | >= 1 | **PASS** |
| 3 | Failure & Recovery Testing | 2 / 2 | >= 1 | **PASS** |
| 4 | Graceful Degradation | 2 / 2 | >= 1 | **PASS** |

---

### 1. Availability Design

**Q: Where does this project implement redundancy, failover, health checks, and SLO/SLA definitions?**
**A:** Look at `src/tools/health.py` (`health_check` FastMCP tool) for live operational readiness probing, `src/models/router.py` (`MultiModelRouter.generate_content`) for multi-provider automatic failover across Gemini, GPT, and Claude frontier models, and `src/graph/client.py` (`GraphClient`) for transparent failover from Cloud Spanner / BigQuery to the embedded knowledge store. Target SLOs/SLAs (`99.999%` Spanner availability, `TTFT <= 250ms`, `p99 <= 600ms`, `RTO=0/RPO=0` hot DR tiers) are enforced in `src/skills/plugins/waf_okf_pillars.py` (`waf-pillar-reliability`) and `src/skills/plugins/google_landing_metrics.py`.

**Q: Where are distributed systems patterns (consistency, partitioning, multi-region) used for high availability?**
**A:** Operational knowledge lives in **Cloud Spanner Graph** (`iac/modules/spanner`, `src/graph/queries.py`) for external consistency and regional/multi-region replication, paired with **BigQuery** (`iac/modules/bq`, `iac/modules/federation`) for partitioned analytical workloads and zero-ETL federation. Compute runs statelessly on Google Cloud's managed **Vertex AI Agent Runtime** (`scripts/deploy_reasoning_engine.py`).

---

### 2. Observability

**Q: How can I inspect structured logging, metrics, and distributed tracing in this codebase?**
**A:** Open `src/otel_setup.py` — it configures an OpenTelemetry `TracerProvider` with `BatchSpanProcessor` and authenticated **OTLP over gRPC** exporting directly to Google Cloud Trace (`telemetry.googleapis.com:443`) with graceful local OTLP fallback. Deployed ADK traces capture full tool waterfalls via `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true` and `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=SPAN_AND_EVENT` in `scripts/deploy_reasoning_engine.py`.

**Q: How does the project monitor AI-specific KPIs like latency, token usage, and response quality?**
**A:** Every `SkillResult` (`src/skills/base.py`) emits `latency_ms` and `token_metrics` (`prompt_tokens_estimated`, `completion_tokens_estimated`, `tokens_saved_by_cache`), `MultiModelRouter` tracks KV prefix cache hits/misses (`_cache_hits`, `_cache_misses`), `src/telemetry/session_feedback.py` records session-level quality ratings, and `scripts/setup_online_monitor.py` provisions a live **Vertex AI `OnlineEvaluator`** (`final_response_quality_v1` at `100%` trace sampling).

---

### 3. Failure & Recovery Testing

**Q: Where does the project run failure injection, red teaming, and disaster recovery validation?**
**A:** Check `tests/test_model_armor.py` and `tests/test_reliability_resilience_skills.py` for automated **failure injection** (`trip_circuit_breaker()` -> fast-path degraded heuristic verification -> `reset_circuit_breaker()` recovery), `tests/evals/test_model_armor_trajectory_evals.py` for **adversarial red teaming** (prompt injections, jailbreaks, SSRF, PII exfiltration), and `src/skills/plugins/waf_okf_pillars.py` (`skill_waf_pillar_reliability`) for Cold/Warm/Hot DR RTO/RPO validation.

**Q: How are backup/restore and degraded-mode resilience tested?**
**A:** Terraform state is remotely versioned and locked in GCS (`iac/backend.tf`), OKF corpus bundles are verified via SHA-256 and CRC32C checksums (`scripts/crc32c_verify.py`, `pipelines/nl2kg_pipeline.py`), and degraded-mode resilience (Spanner/BQ unavailable -> embedded cache; frontier LLM unreachable -> deterministic zero-legacy fallback) is continuously verified in `tests/test_model_router.py` and `tests/test_reliability_resilience_skills.py`.

---

### 4. Graceful Degradation

**Q: What fallback strategies, circuit breakers, and retry policies protect the system during dependency failures?**
**A:** `ModelArmorSanitizer` (`src/security/model_armor.py`, lines 110–146) implements a **rolling circuit breaker** (`failure_threshold=3`, `cooldown_seconds=60.0`) that automatically fails over to `<1ms` local heuristic guardrails when Cloud Model Armor is unreachable. `GraphClient` (`src/graph/client.py`) gracefully degrades from Spanner/BigQuery to its dynamically hydrated embedded knowledge store (`status="degraded"`), and `MultiModelRouter` (`src/models/router.py`) fails over across candidate models and falls back deterministically rather than crashing.

**Q: How are timeouts and high-load / partial-failure stability configured?**
**A:** `ModelArmorSanitizer` enforces a strict `150ms` interactive HTTP client timeout (`model_armor_timeout_seconds = 0.150` in `src/security/model_armor.py`), iterative resolution workflows (`ai_ml_rubric.py`, `security_privacy_compliance.py`, `reliability_resilience.py`) bound execution with `max_iterations` loop guards (capped at 5), and live evaluation streams enforce explicit `asyncio.wait_for(..., timeout=...)` bounds so partial failures never stall the runtime.
<!-- RELIABILITY_RESILIENCE_FAQS_END -->

---

<!-- PERFORMANCE_COST_OPTIMIZATION_FAQS_START -->
## Performance & Cost Optimization FAQs

> Direct, verifiable answers pointing to exact code, IaC, and caching layers where the **Enterprise Agents Architectural Guidelines MCP Server** (`architecture_best_practices_mcp`) demonstrates scalability & elasticity, resource efficiency, and AI cost management (**Rubric Verdict: PASS — 3/3 Domains, 6/6 Sub-Criteria at Competent or Exemplary level**).

| # | Performance & Cost Optimization Domain | Competent Criteria | Required Cutline | Status |
|---:|:---|---:|---:|:---|
| 1 | Scalability & Elasticity | 2 / 2 | >= 1 | **PASS** |
| 2 | Resource Efficiency | 2 / 2 | >= 1 | **PASS** |
| 3 | AI Cost Management | 2 / 2 | >= 1 | **PASS** |

---

### 1. Scalability & Elasticity

**Q: How does this project handle horizontal/vertical scaling, autoscaling, and load balancing?**
**A:** The core MCP server and ADK agents run statelessly on Google Cloud's managed **Gemini Enterprise / Vertex AI Agent Engine (`google-adk`)** (`scripts/deploy_reasoning_engine.py`), with an optional **Cloud Run frontend / web deployment layer** layered over it for browser-based apps, scaling serving replicas elastically without manual VM management. For customer architectures, `waf-pillar-performance-optimization` (`src/skills/plugins/waf_okf_pillars.py`) and `google-landing-metrics` enforce Global External ALB load balancing, GKE Autopilot autoscaling, and Cloud Spanner horizontal partitioning.

**Q: How are API throughput and inference latency optimized?**
**A:** All FastMCP tools (`src/tools/`), `GraphClient`, `ModelArmorSanitizer` (persistent `httpx.AsyncClient` connection pooling), and ADK streaming (`async_stream_query`) are natively asynchronous. Latency envelopes (`TTFT <= 250ms`, `p99 <= 600ms`, `Cloud CDN Hit Ratio >= 95%`, `150ms` guardrail SLA) are enforced across `src/security/model_armor.py` and `src/skills/plugins/google_landing_metrics.py`, while `iac/main.tf` enables BigQuery `use_data_boost = true` for isolated high-throughput analytical queries.

---

### 2. Resource Efficiency

**Q: How are compute/database resources right-sized and serverless/spot efficiency leveraged?**
**A:** Look at `iac/main.tf` and `iac/variables.tf`: Cloud Spanner is right-sized using granular `processing_units` (rather than over-provisioning full nodes), compute runs on managed serverless Vertex AI Agent Runtime (zero idle container fleet), and `waf-pillar-cost-optimization` (`src/skills/plugins/waf_okf_pillars.py`) enforces GKE Autopilot bin-packing, Spot/Preemptible VMs for batch jobs, Flexible CUDs, and Recommender API idle-VM cleanup.

**Q: What eliminates resource waste while maintaining performance targets?**
**A:** Zero-ETL BigQuery-to-Spanner federation (`iac/modules/federation`) avoids duplicate ETL pipelines and redundant storage copies, while `waf-pillar-cost-optimization` enforces GCS Autoclass, BigQuery partitioning/clustering with automatic 90-day 50% long-term storage discounts, `_Default` log exclusion filters, and Billing Budgets wired to Pub/Sub hard caps.

---

### 3. AI Cost Management

**Q: How does this project balance model selection trade-offs, response caching, batching, and embedding optimization?**
**A:** Check `src/models/router.py` (`MultiModelRouter` & `MODEL_REGISTRY`): requests are routed across 6 explicit `ModelTier` tiers — lightweight/fast `ROUTING_FAST` models (`gemini-3.1-flash`, `claude-5-haiku`, `o4-mini`) for triage vs `REASONING_FRONTIER` / `JUDGE` models (`gemini-3.1-pro`, `gemini-4-argon`) only when deep reasoning is required, plus an encoder-only `EMBEDDING_ENCODER` model (`gemini-embedding-001`) for dense vector retrieval. `compute_prefix_cache_key()` implements KV prefix context caching with hit/miss tracking.

**Q: How are tokens and context windows managed for fiscal responsibility?**
**A:** `SkillsRegistry` (`src/registry/skills_registry.py`) enforces **Two-Tier Progressive Disclosure**: Tier 1 loads only lightweight catalog metadata (~30 tokens/skill instead of stuffing all 50 full schemas into every prompt), achieving **>80% prompt token compression** per turn. Every `SkillManifest` declares `context_token_estimate` and every `SkillResult` (`src/skills/base.py`) reports `token_metrics` (`prompt_tokens_estimated`, `completion_tokens_estimated`, `tokens_saved_by_cache`).
<!-- PERFORMANCE_COST_OPTIMIZATION_FAQS_END -->

---

<!-- OPERATIONAL_EXCELLENCE_FAQS_START -->
## Operational Excellence FAQs

> Direct, verifiable pointers to the exact CI/CD scripts, Terraform modules, AI lifecycle tooling, and automated test suites where the **Enterprise Agents Architectural Guidelines MCP Server** (`architecture_best_practices_mcp`) demonstrates Operational Excellence (**Rubric Verdict: PASS — 4/4 Domains, 8/8 Sub-Criteria at Competent or Exemplary level**).

| # | Operational Excellence Domain | Competent Criteria | Required Cutline | Status |
|---:|:---|---:|---:|:---|
| 1 | CI/CD & Deployment | 2 / 2 | >= 1 | **PASS** |
| 2 | Infrastructure as Code | 2 / 2 | >= 1 | **PASS** |
| 3 | AI Lifecycle Management | 2 / 2 | >= 1 | **PASS** |
| 4 | Testing & Quality Engineering | 2 / 2 | >= 1 | **PASS** |

---

### 1. CI/CD & Deployment

**Q: How does this project automate CI/CD pipelines and safe progressive deployments?**
**A:** End-to-end deployment is automated via `scripts/deploy_from_scratch.sh`, `scripts/deploy_from_scratch.py`, `scripts/redeploy_all_to_project.py`, and `scripts/deploy_reasoning_engine.py` (supporting `--dry-run` pre-flight validation and in-place `--update` to Vertex AI Agent Engine). For enterprise workload blueprints, `waf-pillar-operational-excellence` (`src/skills/plugins/waf_okf_pillars.py`) enforces Cloud Build Private Pools and Cloud Deploy canary/blue-green progressive delivery.

**Q: How are rollbacks and repeatable releases handled?**
**A:** Every deployment packages immutable, versioned artifacts (`agent_engine.pkl`, `requirements.txt`, `dependencies.tar.gz`) to GCS staging (`gs://<project>-reasoning-engine-staging`), supports deterministic `--dry-run` gating prior to cloud mutation, and preserves prior OKF corpus snapshots with SHA-256/CRC32C digests (`scripts/crc32c_verify.py`) so releases are repeatable and safely reversible.

---

### 2. Infrastructure as Code

**Q: Where is Infrastructure as Code (Terraform / Cloud Build) defined?**
**A:** All cloud infrastructure is codified in modular Terraform under `iac/` (`iac/main.tf`, `iac/variables.tf`, `iac/outputs.tf`, and modules `iac/modules/spanner`, `iac/modules/bq`, `iac/modules/federation`, `iac/modules/gcs`, `iac/modules/gemini_enterprise`) with remote GCS state locking in `iac/backend.tf`. Terraform configurations are also continuously audited for WAF drift via `skill_terraform_waf_verifier` and `skill_terraform_version_comparator` (`src/skills/plugins/terraform_infra.py`).

**Q: How does the project maintain strict parity across dev, staging, and production?**
**A:** Environment parity is enforced through parameterized Terraform variables (`iac/terraform.tfvars.example` & `iac/terraform.tfvars`), a pinned dependency lockfile (`uv.lock` + `pyproject.toml`), portable OKF bundles (`dist/portable_bundle/`), and turnkey cross-project redeployment (`scripts/redeploy_all_to_project.py`).

---

### 3. AI Lifecycle Management

**Q: How does this project manage model/agent versioning, configuration, and A/B routing?**
**A:** `src/models/router.py` maintains an explicit `MODEL_REGISTRY` across Gemini 3.1+/4, GPT-5/o3, and Claude 5.* with typed `ModelTier` routing (`JUDGE`, `REASONING_FRONTIER`, `ROUTING_FAST`, `AUDIT_SOCRATIC`, `FORMAL_VERIFICATION`, `EMBEDDING_ENCODER`), while `src/config.py` (`pydantic-settings`) manages typed runtime configuration and `SkillManifest.version` versions all 53 skills.

**Q: What experiment tracking and operational tooling powers scalable agent management?**
**A:** The platform combines **OpenTelemetry Cloud Trace** (`src/otel_setup.py`), **Vertex AI `OnlineEvaluator`** (`scripts/setup_online_monitor.py`, continuously scoring `final_response_quality_v1`), **session feedback telemetry** (`src/telemetry/session_feedback.py`), **autonomous 6-month TTL corpus evolution** (`src/agent/okf_evolution_reasoning_engine.py`), and versioned independent skill trajectory evaluation records (`docs/validation/all_53_skills_trajectory_record.json`).

---

### 4. Testing & Quality Engineering

**Q: Where are unit, integration, end-to-end, and performance/latency tests implemented?**
**A:** Open `tests/`:
- **Unit & Security Tests**: `tests/test_model_router.py`, `tests/test_model_armor.py`, `tests/test_ai_ml_rubric_skills.py`, `tests/test_security_privacy_compliance_skills.py`, `tests/test_reliability_resilience_skills.py`, `tests/test_performance_cost_optimization_skills.py`, `tests/test_operational_excellence_skills.py`.
- **Integration & E2E Runbook Tests**: `tests/test_all_38_skills_runbook.py` (validating all 53 skills + all 29 FastMCP tools end-to-end) and `tests/test_mcp_local.py`.
- **IR, Trajectory & Latency/Performance Evals**: `tests/evals/test_retrieval_quality.py` (Hit Rate, Precision, Recall, F1, MRR, ROUGE-L), `tests/evals/test_trajectory_evals.py` (10 multi-turn trajectories), `tests/evals/test_skills_trajectory_evals.py` (24 Gemini Argon Chief Judge trajectories), and live Vertex AI latency/streaming evaluations.

**Q: How is test automation and coverage enforced for production-grade reliability?**
**A:** Every skill addition is gated by parametrized `pytest` suites covering Tier 1 discovery, Tier 2 manifest hydration, Tier 3 execution, independent 3-turn trajectory evaluation across all 53 skills (`100%` pass rate), ADK `--dry-run` session validation, and live post-deployment verification against Vertex AI Agent Engine.
<!-- OPERATIONAL_EXCELLENCE_FAQS_END -->

---

<!-- DESIGNING_FOR_CHANGE_FAQS_START -->
## Designing for Change FAQs

> Direct, verifiable pointers to the exact abstractions, externalized configs, contract-first schemas, and auto-discovered plugin patterns where the **Enterprise Agents Architectural Guidelines MCP Server** (`architecture_best_practices_mcp`) demonstrates Designing for Change (**Rubric Verdict: PASS — 4/4 Domains, 8/8 Sub-Criteria at Competent or Exemplary level**).

| # | Designing for Change Domain | Competent Criteria | Required Cutline | Status |
|---:|:---|---:|---:|:---|
| 1 | Modularity & Abstraction | 2 / 2 | >= 1 | **PASS** |
| 2 | Configuration Management | 2 / 2 | >= 1 | **PASS** |
| 3 | API Design & Versioning | 2 / 2 | >= 1 | **PASS** |
| 4 | Extensibility | 2 / 2 | >= 1 | **PASS** |

---

### 1. Modularity & Abstraction

**Q: How does this project enforce loose coupling, interface contracts, and model swappability?**
**A:** Every skill implements the `SkillPlugin` abstract base class (`abc.ABC` in `src/skills/base.py`) with a strict `manifest -> SkillManifest` and `execute(context, parameters) -> SkillResult` contract. Foundation models are completely decoupled behind `MultiModelRouter` (`src/models/router.py`), which lets you swap seamlessly across Gemini 3.1+/4, Claude 5.*, and GPT-5/o3 by `model_id` or `ModelTier` without changing a single calling skill.

**Q: Where is dependency injection used to keep the codebase modular and testable?**
**A:** `GraphClient` (`src/graph/client.py`), `ModelArmorSanitizer` (`src/security/model_armor.py`), `MultiModelRouter` (`src/models/router.py`), and `EnterpriseArchGuidelinesAgent` (`src/agent/reasoning_engine.py`) all accept injected constructor dependencies (`project_id`, `location`, `use_mock`, `enabled`, `fail_open`, database/dataset IDs), paired with pytest fixtures in `tests/conftest.py` and modular Terraform directories under `iac/modules/`.

---

### 2. Configuration Management

**Q: How are environments, feature flags, and externalized settings separated?**
**A:** Open `src/config.py`: all runtime settings (`gcp_project_id`, `gcp_region`, `spanner_instance_id`, `use_mock_graph`, `model_armor_enabled`, `model_armor_fail_open`, `model_armor_timeout_seconds`) are externalized via `pydantic-settings` and `.env` / environment variables (with `.env` gitignored). Infrastructure environments are parameterized via `iac/variables.tf` and `iac/terraform.tfvars.example`.

**Q: What runtime adjustments can be made without changing code?**
**A:** Operators can switch the active ADK model (`ADK_MODEL`), toggle offline mock mode (`USE_MOCK_GRAPH`), toggle Model Armor enforcement or fail-open/closed posture (`MODEL_ARMOR_ENABLED`, `MODEL_ARMOR_FAIL_OPEN`), adjust timeouts (`MODEL_ARMOR_TIMEOUT_SECONDS`), or re-point OTLP telemetry endpoints (`OTEL_EXPORTER_OTLP_ENDPOINT`) purely through environment variables in `scripts/deploy_reasoning_engine.py`.

---

### 3. API Design & Versioning

**Q: How does the project enforce contract-first design and backward compatibility?**
**A:** Every FastMCP tool (`src/tools/`), skill (`SkillManifest`, `SkillParameter`, `SkillResult` in `src/skills/base.py`), graph ontology entity (`pipelines/nl2kg_pipeline.py`), and structured LLM response (`MultiModelRouter.generate_structured`) is defined contract-first with Pydantic models and JSON Schema. `SkillsRegistry` (`src/registry/skills_registry.py`) also normalizes hyphen/underscore aliases (`skill-foo` <-> `skill_foo`) for backward compatibility.

**Q: How is schema evolution managed across system updates?**
**A:** Every `SkillManifest` carries an explicit `version` field, optional parameters provide safe defaults (`required=False`, `default=...`) so existing callers never break, OpenTelemetry specifies `semconv_version="1.39.0"` (`scripts/setup_online_monitor.py`), and the autonomous `OKFEvolutionReasoningEngine` (`src/agent/okf_evolution_reasoning_engine.py`) evolves the 92 OKF v0.2 concepts with backward-compatible 6-month TTL revisions.

---

### 4. Extensibility

**Q: Where are plugin patterns and event-driven hooks/callbacks implemented?**
**A:** `src/skills/discovery.py` implements an auto-discovered plugin engine that dynamically imports every `SkillPlugin` subclass in `src/skills/plugins/*.py` and parses every `.agents/skills/*/SKILL.md` manifest on startup. Event-driven hooks and streaming callbacks include ADK `streaming_agent_run_with_events` (`src/agent/adk_agent.py`), OpenTelemetry `OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK="upload"`, and Pub/Sub billing/alert hooks enforced in `waf_okf_pillars.py`.

**Q: How can new skills or integrations be added with minimal disruption to core logic?**
**A:** Adding a new skill requires **zero changes** to `src/server.py`, `src/tools/skills.py`, or `src/registry/skills_registry.py`: simply drop a new `SkillPlugin` subclass into `src/skills/plugins/` and a companion `SKILL.md` into `.agents/skills/<name>/`. That exact drop-in pattern enabled scaling the platform cleanly from 38 to **56 registered skills** without touching core dispatch logic.
<!-- DESIGNING_FOR_CHANGE_FAQS_END -->

# Project Scoping Charter, Roadmap & Architecture Decision Records (ADRs)

> Authoritative scoping, stakeholder alignment, and decision record document for the **Enterprise Agents Architectural Guidelines MCP Server** (`architecture_best_practices_mcp`), complementing the system design specs (`docs/specs/`), API/MCP docs (`docs/01_MCP_SERVER_DOCUMENTATION.md`, `docs/02_SKILLS_REGISTRY_DOCUMENTATION.md`), operational runbooks (`docs/03`–`06`), and rubric FAQs (`docs/FAQs.md`).

---

## 1. Problem Definition & Customer Success Unlocks

### Business Problem
Enterprise engineering teams building AI agents on Google Cloud face fragmented, rapidly drifting architectural standards across security (Zero Ambient Authority, Model Armor), data/graph retrieval (Spanner Graph, BigQuery), Well-Architected Framework (WAF) pillars, and FDE field-readiness rubrics. Manual architecture reviews create multi-week bottlenecks, inconsistent quality gates, and preventable production security/cost regressions.

### Technical Opportunity & Customer Success Unlocks
By codifying 92 OKF v0.2 architectural concepts into a **Cloud Spanner Graph + Dataplex + FastMCP + Vertex AI ADK Agent** platform with **58 auto-discovered skills**, engineering teams unlock:
- **Sub-minute automated architecture, Terraform, and rubric audits** directly inside IDEs (Antigravity, VS Code, Cursor) and Gemini Enterprise.
- **>80% prompt token cost reduction** via Two-Tier Progressive Disclosure (`list_registered_skills` -> `get_skill_manifest` -> `invoke_skill`).
- **Continuous compliance enforcement** (`>= 2.0/3.0` FDE cutline, zero `0.0` security disqualifiers, 6-month OKF TTL freshness).

### Critical User Journeys (CUJs) & Definition of Done (DoD)
| CUJ ID | Critical User Journey | Definition of Done (DoD) |
| :--- | :--- | :--- |
| **CUJ-1** | Architect queries authoritative GCP/Agent best practices & tradeoffs in IDE or Gemini Enterprise | Grounded response citing OKF IDs + Spanner Graph patterns in `<600ms` p99 (embedded/graph lookup). |
| **CUJ-2** | Engineer audits a project spec or Terraform HCL against WAF, AI/ML, Security, Reliability, FinOps, Ops Excellence, Designing for Change, and Scoping rubrics | Deterministic Pass/Fail scorecard + prioritized remediation plan + iterative re-assessment until PASS. |
| **CUJ-3** | Platform SRE deploys & monitors the ADK Agent Engine with continuous online evaluation | Turnkey `deploy_reasoning_engine.py` update + active Vertex AI `OnlineEvaluator` (`final_response_quality_v1`) + `100%` passing 58-skill independent trajectory record. |

---

## 2. Technical Scope, Constraints & Assumptions

### In-Scope vs. Out-of-Scope System Boundaries
- **In-Scope**: FastMCP server (`stdio`/`SSE`, 29 tools), 58 dynamically discovered skills (`src/skills/plugins/` + `.agents/skills/`), Cloud Spanner Graph (`ArchGuidelinesGraph`), BigQuery analytics/embeddings, Dataplex OKF v0.2 corpus, Dual-Pass Model Armor guardrails, **Gemini Enterprise / Vertex AI Agent Engine (`google-adk` / `AdkApp`)** deployment as both MCP server and ADK agent, optional **Cloud Run frontend / web deployment layer** over Gemini Enterprise & MCP, OpenTelemetry Cloud Trace, and automated pytest/trajectory evaluation suites.
- **Out-of-Scope**: Hosting the core ADK agent runtime directly inside self-managed containers instead of Gemini Enterprise / Vertex AI Agent Engine, or mutating customer production GCP projects without human-in-the-loop review.

### Constraints & Assumptions
- **Zero Ambient Authority (ZAA)**: Zero static service account JSON keys in runtime or Terraform.
- **Zero Legacy Model Policy**: Hard block on Gemini 2.5/2.0/1.5 and legacy checkpoints in `src/models/router.py`.
- **Prototype vs. Production Separation**: Offline development and CI tests use injected `use_mock=True` / embedded cache fallbacks (`GraphClient`, `MultiModelRouter`), while production enforces live Spanner Graph, BigQuery, Cloud Model Armor, and Vertex AI Agent Runtime (`USE_MOCK_GRAPH=false` in `.env`).

---

## 3. Stakeholder Alignment, Success Criteria & Phased Delivery Roadmap

### Measurable Success & Acceptance Criteria
- **Retrieval Quality**: `Hit Rate@k >= 0.80`, `MRR >= 0.35`, positive `ROUGE-L F1` (`tests/evals/test_retrieval_quality.py`).
- **Trajectory Precision**: `Tool Selection Precision >= 90%`, `Argument Accuracy >= 95%` (`tests/evals/test_trajectory_evals.py`), `100%` pass rate across all 58 skills (`docs/validation/all_58_skills_trajectory_record.json`).
- **Security Defense**: `100%` prompt injection & PII/secret egress interception (`tests/evals/test_model_armor_trajectory_evals.py`).
- **Governance Cutline**: FDE Composite Score `>= 2.0/3.0` with zero `0.0` disqualifiers.

### Phased Delivery Plan
- **Phase 1 (Foundation & GraphRAG)**: NL2KG triplification pipeline, Spanner Graph + BigQuery federation, core FastMCP server (`29` tools). *(Completed)*
- **Phase 2 (WAF, Terraform & Progressive Disclosure)**: Two-Tier Progressive Disclosure registry, 6 WAF pillar verifiers, Terraform compliance & drift comparator, Dual-Pass Model Armor. *(Completed)*
- **Phase 3 (Enterprise Engineering Rubrics & Live Online Evaluation)**: AI/ML, Security/Privacy/Compliance, Reliability & Resilience, Performance & Cost, Operational Excellence, Designing for Change, and Scoping & Documentation skills (`58` total skills / `31` ADK tools), `docs/FAQs.md`, Vertex AI `OnlineEvaluator`, and live trace verification. *(Completed)*

---

## 4. Architecture Decision Records (ADRs)

### ADR-001: Vertex AI Managed Agent Runtime (`google-adk`) vs. Cloud Run / GKE
- **Status:** `Accepted`
- **Context:** Needed 24x7x365 managed hosting with native Google Cloud Console Playground, session streaming, and GenAI OpenTelemetry trace waterfalls.
- **Alternatives Considered:** Self-hosted Cloud Run service; GKE Autopilot deployment.
- **Decision & Rationale:** Deployed natively via `vertexai.agent_engines.AdkApp` (`scripts/deploy_reasoning_engine.py`). Eliminates container patching, exposed public ports, and manual session store plumbing while enabling first-class Vertex AI `OnlineEvaluator`.
- **Trade-offs / Consequences:** Tied to Vertex AI Agent Engine packaging (`cloudpickle` + `extra_packages`), mitigated via `--dry-run` pre-flight validation.

### ADR-002: Two-Tier Progressive Disclosure Skills Registry
- **Status:** `Accepted`
- **Context:** Stuffing 58 full skill manifests into every LLM prompt causes context bloat, attention dilution, and high token spend.
- **Alternatives Considered:** Static eager tool loading; splitting into separate MCP servers per domain.
- **Decision & Rationale:** Implemented `SkillsRegistry` (`src/registry/skills_registry.py`) with Tier 1 catalog discovery (~30 tokens/skill) and Tier 2 on-demand manifest hydration (`get_skill_manifest`).
- **Trade-offs / Consequences:** Adds one lightweight discovery turn when a skill ID is unknown, saving >80% prompt tokens across multi-turn sessions.

### ADR-003: Cloud Spanner Graph + BigQuery Zero-ETL Federation
- **Status:** `Accepted`
- **Context:** Required both sub-100ms multi-hop relationship traversal (`Guideline -> Pattern -> Antipattern`) and analytical/vector queries.
- **Alternatives Considered:** Pure vector database (no graph traversals); Cloud SQL + manual ETL to BigQuery.
- **Decision & Rationale:** Adopted Cloud Spanner Graph (`iac/modules/spanner`) with BigQuery Zero-ETL federation (`iac/modules/federation`, `use_data_boost = true`) and Reciprocal Rank Fusion (`hybrid_search_guidelines`).
- **Trade-offs / Consequences:** Higher baseline Spanner cost mitigated by granular `processing_units` right-sizing and embedded offline fallback for dev/CI.

### ADR-004: Dual-Pass Model Armor with 150ms Timeout & Rolling Circuit Breaker
- **Status:** `Accepted`
- **Context:** Needed defense-in-depth against prompt injections, SSRF, and PII/secret exfiltration without breaking interactive latency SLAs.
- **Alternatives Considered:** Ingress-only filtering; synchronous unbounded Cloud API calls.
- **Decision & Rationale:** Implemented Dual-Pass ingress + fail-closed egress sanitization (`src/security/model_armor.py`) with a `150ms` timeout and rolling circuit breaker (`failure_threshold=3`, `cooldown_seconds=60.0`) failing over to `<1ms` local heuristic guardrails.
- **Trade-offs / Consequences:** Local heuristics are narrower than cloud semantic models during outages, but guarantee uninterrupted protection and SLA stability.

### ADR-005: Auto-Discovered Plugin Architecture (`SkillPlugin` + `.agents/skills/*/SKILL.md`)
- **Status:** `Accepted`
- **Context:** Needed to scale rapidly from 38 to 58+ skills without modifying core MCP dispatch or routing code.
- **Alternatives Considered:** Manual registration table in `src/server.py`.
- **Decision & Rationale:** Implemented dynamic plugin & YAML frontmatter discovery in `src/skills/discovery.py` with strict `SkillPlugin` (`abc.ABC`) contracts and hyphen/underscore alias normalization.
- **Trade-offs / Consequences:** Requires disciplined unit + runbook test coverage (`test_all_38_skills_runbook.py` and independent trajectory records) to catch broken plugins at CI time.

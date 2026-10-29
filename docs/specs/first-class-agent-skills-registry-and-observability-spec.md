# Master Spec: First-Class Enterprise Architecture Agent, Skills Registry & Observability Engine (`first-class-agent-skills-registry-and-observability-spec.md`)

**Status:** ACTIVE (Target Master Architecture & Implementation Specification)  
**Target Repository:** [`https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server`](https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server)  
**Canonical Repo Path:** `specs/first-class-agent-skills-registry-and-observability-spec.md` (mirrored in `docs/specs/`)  
**Target GCP Project:** `fivedaysai-prd-sandbox-317383` (`301802433103`)  
**Target Cloud Region:** `us-central1`  
**Governing Standard:** [`concepts/00-fde-field-readiness-and-grading-rubric.md`](../okf/concepts/00-fde-field-readiness-and-grading-rubric.md) · Google Cloud FDE Charter  
**Knowledge Base Corpus:** Complete OKF v0.2 Corpus (83 Flat Concepts + 25 Root L400 Concepts + Socratic Grilling + Tokenomics + Context Cache Memory)  

---

## 1. Executive Summary & North Star Architecture

This specification defines the complete engineering architecture for an enterprise-grade **First-Class Deployed Agent in Google Cloud (Gemini Enterprise Agent Runtime & Vertex AI Agent Engine)** that powers **24x7x365 follow-the-sun worldwide development** of MCP and A2A enterprise prototypes, POCs, and production applications.

### Core Architectural Pillars
1. **First-Class Deployed Agent Form Factor:** Rather than a passive tool server or container on Cloud Run, the system deploys as a managed Python application runtime on Vertex AI Agent Engine (`reasoningEngines/<id>`) featuring native turn-by-turn Sessions and Memory Bank. Vertex AI Reasoning Engine does not use a BYOC (Bring Your Own Container) model; Google Cloud manages containerization, sandboxing, autoscaling, and endpoint lifecycle directly.
2. **Dual-Surface Invocation:**
   - **Antigravity CLI / AGY SDK:** Anywhere, anytime access for coding agents and human developers worldwide via a lightweight local FastMCP `stdio` adapter (`src/mcp_adapter.py`) that proxies tool calls to the remote Vertex AI Reasoning Engine using the developer's ADC identity.
   - **Gemini Enterprise Web App:** Conversational access for enterprise architects and business executives via Google Cloud Agent Registry, Agent Gateway, and delegated OAuth 2.0 user credentials, capable of generating production-ready technical specifications strictly grounded in the 83-concept OKF v0.2 knowledge base.
3. **Comprehensive Enterprise Skills Registry:** Houses 12 specialized enterprise skills plus an extensible Dynamic Discovery Engine with discrete least-privilege IAM scoping per skill.
4. **Rigorous Trajectory Evaluation Suite:** Per-skill and collection-level multi-turn trajectory benchmarks graded by Gemini 2.5 Pro LLM-as-a-judge auto-raters enforcing the $\ge 2.0 / 3.0$ FDE rubric cutline.
5. **Online OpenTelemetry Session Feedback System:** Ingests live developer ratings, critiques, and execution telemetry into Cloud Trace and BigQuery (`session_feedback`).

```mermaid
flowchart TD
    subgraph Clients ["Dual Enterprise Consumption Surfaces"]
        AntigravityCLI["Surface A: Antigravity CLI / AGY SDK<br/>(stdio / Subagents, .agents/skills/)"]
        LocalAdapter["Local FastMCP Adapter (src/mcp_adapter.py)<br/>• Pure Python bridge over stdio<br/>• Maps call_tool to reasoningEngines.query"]
        GeminiWebApp["Surface B: Gemini Enterprise Web App<br/>(Browser Chat UI, Agent Gateway, Delegated OAuth)"]
        AntigravityCLI --> LocalAdapter
    end

    subgraph AgentCore ["First-Class Deployed Agent (Vertex AI Reasoning Engine)"]
        AgentEngine["EnterpriseArchGuidelinesAgent (reasoningEngines/<id>)<br/>• Managed Python Runtime (No BYOC, No Cloud Run)<br/>• Gemini 2.5 Pro Socratic Reasoning Loop<br/>• Native Sessions & Memory Bank (Concept 04)"]
    end

    subgraph Registry ["Comprehensive Enterprise Skills Registry (Discrete Least Privilege)"]
        S1["1. Design (skill-arch-design)<br/>Scope: Spanner Graph SELECT"]
        S2["2. Spec Gen (skill-spec-generation)<br/>Scope: In-Memory / Zero DB"]
        S3["3. Spec Flow (skill-spec-workflow)<br/>Scope: Spec State DAG"]
        S4["4. WAF Critique (skill-waf-critique)<br/>Scope: BigQuery SELECT"]
        S5["5. Landing Metrics (skill-landing-metrics-critique)<br/>Scope: BigQuery Analytics"]
        S6["6. Spec Socratic Critique (skill-spec-critique)<br/>Scope: KELE Socratic Engine"]
        S7["7. WAF Pillar Critique (skill-waf-pillar-critique)<br/>Scope: BigQuery Pillars"]
        S8["8. FDE Rubric Critique (skill-fde-rubric-critique)<br/>Scope: 26 Rubric Benchmarks"]
        S9["9. Complete Audit (skill-complete-audit)<br/>Scope: Full-Stack Inspection"]
        S10["10. Alexandria Search (skill-alexandria-search)<br/>Scope: Alexandria Search"]
        S11["11. OKF LRO Cron (skill-okf-lro-cron)<br/>Scope: Dedicated Scheduler SA"]
        S12["12. Terraform Infra (skill-terraform-infra)<br/>Scope: IaC Generator"]
        SDynamic["Dynamic Discovery Engine (.agents/skills/ & GCS)"]
    end

    subgraph TelemetryFlywheel ["Observability & Trajectory Quality Flywheel"]
        TrajEvals["Trajectory Eval Suite (Per-Skill + Collection Benchmarks)"]
        OTelFeedback["Online OTel Feedback System (Cloud Trace + BigQuery)"]
    end

    subgraph KnowledgeSubstrate ["Knowledge Substrate & Security Tier"]
        Spanner["Cloud Spanner Graph (arch_guidelines_graph)"]
        BQ["BigQuery Analytics (gea_arch_guidelines_analytics)"]
        ModelArmor["Dual-Pass Model Armor + Cloud DLP (Concept 33)"]
    end

    LocalAdapter -->|Vertex AI query() via ADC| AgentEngine
    GeminiWebApp -->|Agent Registry / Gateway| AgentEngine
    AgentEngine --> Registry
    S1 --> Spanner
    S4 --> BQ
    S5 --> BQ
    S7 --> BQ
    S8 --> BQ
    Registry --> KnowledgeSubstrate
    Clients -.-> OTelFeedback
    OTelFeedback --> BQ
    Registry -.-> TrajEvals
```

---

## 2. Detailed Skills Registry Taxonomy & Action Schemas

The Skills Registry replaces static hardcoded if/elif dispatches with a dynamic registry supporting progressive disclosure:
- **Tier 1 (Catalog):** Lightweight schema disclosure consuming $< 600$ tokens per turn.
- **Tier 2 (Manifest Hydration):** Full JSON schema and execution logic loaded on demand.

### 2.1 Skill 1: Architecture Design (`skill-arch-design`)
- **Purpose:** Synthesizes end-to-end enterprise architectures, component topologies, data flow diagrams, and cloud landing zones grounded in OKF v0.2.
- **Entrypoints:** `design_enterprise_architecture(requirements: str, constraints: dict)`, `generate_component_topology(architecture_type: str)`.
- **Outputs:** PlantUML / Mermaid diagrams, component matrices, and landing zone blueprints.

### 2.2 Skill 2: Spec Generation (`skill-spec-generation`)
- **Purpose:** Generates contract-first technical specifications, architectural decision records (ADRs), API schemas, and deployment plans strictly adhering to OKF concepts.
- **Entrypoints:** `generate_technical_spec(proposal: str, scope: str)`, `create_architecture_decision_record(decision_title: str, context: str, tradeoffs: list)`.
- **Outputs:** Markdown specifications with GFM tables, alerts, and Mermaid state/sequence diagrams.

### 2.3 Skill 3: Spec Creation Workflow (`skill-spec-workflow`)
- **Purpose:** Orchestrates multi-stage drafting, grilling, refining, and human-in-the-loop approval workflows before code execution.
- **Entrypoints:** `initiate_spec_workflow(spec_id: str, author: str)`, `advance_spec_stage(spec_id: str, current_stage: str, artifacts: dict)`, `finalize_spec_approval(spec_id: str)`.
- **Stages:** `DRAFT` $\rightarrow$ `SOCRATIC_GRILLING` $\rightarrow$ `ADVISORY_CRITIQUE` $\rightarrow$ `FDE_RUBRIC_AUDIT` $\rightarrow$ `APPROVED`.

### 2.4 Skill 4: Well-Architected Framework Critique (`skill-waf-critique`)
- **Purpose:** Holistic architectural review against the Google Cloud Well-Architected Framework (WAF), assessing architecture across all pillars.
- **Entrypoints:** `critique_well_architected_framework(spec_content: str)`, `get_waf_alignment_matrix(architecture_json: dict)`.
- **Outputs:** Comprehensive score and remediation table across all 5 WAF pillars.

### 2.5 Skill 5: Google Landing Metric Critique (`skill-landing-metrics-critique`)
- **Purpose:** Evaluates business value, customer ROI bounds, TCO models, and landing metrics (FDE Advisory Rigor Part A).
- **Entrypoints:** `critique_landing_metrics(business_case: str, architecture_spec: str)`, `calculate_agent_tco_bounds(concurrency: int, token_rate: float)`.
- **Outputs:** Projected TCO, payback period, risk mitigations, and executive landing metric scorecard.

### 2.6 Skill 6: Spec Socratic Critique (`skill-spec-critique`)
- **Purpose:** Conducts Socratic grilling (KELE - Knowledge Elicitation via Longitudinal Examination) on specs to identify ambiguity, underspecified SLAs, edge cases, and missing invariants.
- **Entrypoints:** `critique_technical_spec(spec_text: str)`, `grill_spec_assumptions(spec_text: str, severity_threshold: str)`.
- **Outputs:** Structured diagnostic questionnaire with selectable options and decision criteria.

### 2.7 Skill 7: WAF Specific Pillar Critique (`skill-waf-pillar-critique`)
- **Purpose:** Deep-dive diagnostic evaluation against specific WAF pillars:
  - Security (Zero Ambient Authority, Model Armor, VPC-SC, IAM Principal Access Boundaries)
  - Reliability (Multi-region HA, circuit breakers, backpressure, failover)
  - Operational Excellence (IaC, CI/CD gates, OTel tracing, SLOs)
  - Performance Efficiency (Gemini KV context caching, HTTP/2 multiplexing, Spanner GQL tuning)
  - Cost Optimization (AI tokenomics, intensive margin compression, cache hit ratio)
- **Entrypoints:** `critique_waf_pillar(pillar: str, spec_content: str, detail_level: str)`.
- **Outputs:** Deep-dive pillar scorecard with high-severity gap identifications.

### 2.8 Skill 8: Rubric-Level Critique (`skill-fde-rubric-critique`)
- **Purpose:** Audits projects against the 26/31 sub-competencies of the Google Cloud FDE Field-Readiness Rubric, enforcing the $\ge 2.0 / 3.0$ cutline and detecting 0-score disqualifiers.
- **Entrypoints:** `audit_project_against_fde_rubric(project_spec_or_repo: str)`, `check_fde_disqualifiers(architecture_metadata: dict)`.
- **Outputs:** Full 26-competency scorecard, composite average score, and prioritized remediation roadmap.

### 2.9 Skill 9: Complete Full-Stack Audit (`skill-complete-audit`)
- **Purpose:** End-to-end composite audit evaluating repository, IaC, data tiers, protocol conformance, and security postures in one pass.
- **Entrypoints:** `execute_complete_architecture_audit(repo_url_or_path: str, environment_tier: str)`.
- **Outputs:** Unified Executive Audit Report synthesizing WAF, FDE Rubric, and OKF compliance.

### 2.10 Skill 10: Alexandria Best Practices Search (`skill-alexandria-search`)
- **Purpose:** High-precision search across Alexandria and enterprise knowledge bases for verified architecture patterns.
- **Entrypoints:** `search_alexandria_best_practices(query: str, domain: str)`, `cross_reference_patterns(pattern_name: str)`.
- **Outputs:** Grounded pattern references, proven customer exemplars, and anti-pattern warnings.

### 2.11 Skill 11: OKF LRO Cronjob Agent (`skill-okf-lro-cron`)
- **Purpose:** Long-Running Operation (LRO) / monthly Cloud Scheduler cronjob agent that performs autonomous freshness audits, concept drafting, and GCS/Spanner sync.
- **Entrypoints:** `run_monthly_okf_evolution_lro(project_id: str, dry_run: bool)`, `check_okf_freshness_lro()`.
- **Outputs:** LRO operation ID, diff report, commit metadata, and sync receipt.

### 2.12 Skill 12: Terraform Infrastructure (`skill-terraform-infra`)
- **Purpose:** Synthesizes, validates, and audits production Terraform modules (Spanner, BigQuery, Cloud Run, IAM PAB) with least privilege.
- **Entrypoints:** `generate_terraform_infra(spec: dict, target_modules: list)`, `audit_terraform_compliance(tf_code_or_dir: str)`.
- **Outputs:** Synthesized HCL Terraform code and security compliance pass/fail report.

### 2.13 Dynamic Skill Discovery Engine (`skill-dynamic-discovery`)
- **Purpose:** Scans `.agents/skills/`, GCS buckets, and Agent Registry for new `SKILL.md` manifests and hydrates them dynamically into runtime without code edits.
- **Entrypoints:** `discover_skills(source: str)`, `hydrate_skill_manifest(manifest_path: str)`.

---

## 3. Trajectory Evaluation Suite (Per-Skill & Collection Benchmarks)

### 3.1 Per-Skill Trajectory Dataset Schema (`tests/evals/trajectory_dataset.json`)
```json
{
  "trajectory_id": "TRAJ-SKILL-01-ARCH-DESIGN",
  "skill_id": "skill-arch-design",
  "turns": [
    {
      "turn_index": 1,
      "user_prompt": "Design a resilient payment processing agent system for global retail.",
      "expected_tools": ["search_guidelines", "query_architectural_pattern"],
      "expected_concepts": ["02-zero-ambient-authority", "03-enterprise-ai-agent-protocol-stack"]
    },
    {
      "turn_index": 2,
      "user_prompt": "Apply Socratic grilling on the p99 latency SLA and Model Armor constraints.",
      "expected_tools": ["critique_technical_spec", "evaluate_design_tradeoffs"],
      "rubric_bar": { "RUBRIC_A_3": 2.5, "RUBRIC_B_3_1": 2.5 }
    }
  ]
}
```

### 3.2 Collection-Level Benchmarks
1. **Benchmark C1 (Spec Creation & Infra Synthesis):** Evaluates `skill-arch-design` $\rightarrow` `skill-spec-generation` $\rightarrow$ `skill-spec-critique` $\rightarrow$ `skill-terraform-infra`.
2. **Benchmark C2 (Complete Enterprise Review):** Evaluates `skill-waf-critique` $\rightarrow$ `skill-landing-metrics-critique` $\rightarrow$ `skill-fde-rubric-critique` $\rightarrow$ `skill-complete-audit`.
3. **Benchmark C3 (Monthly Auto-Evolution):** Evaluates `skill-okf-lro-cron` $\rightarrow$ `skill-alexandria-search` $\rightarrow$ Spanner Graph ingestion.

### 3.3 LLM-as-a-Judge Evaluation Engine (`tests/evals/test_trajectory_evals.py`)
- Evaluates multi-turn conversation traces against the FDE rubric grading scale (0.0 to 3.0).
- Automatically asserts that the trajectory composite score satisfies:
  $$\text{Composite Score} \ge 2.0 / 3.0$$
- Triggers a failing exit code in CI/CD if any 0-score disqualifier is detected.

---

## 4. Online OpenTelemetry Session Feedback System

### 4.1 Real-Time Session Telemetry Flow
Every session conducted via Antigravity CLI or Gemini Enterprise Web App streams telemetry via OpenTelemetry:
1. **Trace Propagation:** W3C `traceparent` correlated from client to agent.
2. **Span Events:** Tool invocations, Socratic question prompts, and user decisions.
3. **User Feedback Capture:** Ratings (1–5 stars), qualitative critiques, and approved/rejected spec diffs captured via `POST /v1/feedback`.
4. **BigQuery Ingestion:** Real-time streaming into `fivedaysai-prd-sandbox-317383.gea_arch_guidelines_analytics.session_feedback`.

---

## 5. Gemini Enterprise Web App Spec Generation Contract

When users in the Gemini Enterprise Web App invoke this agent to create specifications:
1. The agent grounds all recommendations in the 83 flat concepts and 25 root L400 concepts in the OKF v0.2 knowledge base.
2. The agent automatically generates an Architectural Decision Record (ADR) detailing tradeoffs, options, and rationale.
3. The generated specification includes:
   - Executive Summary & North Star Mandate
   - PlantUML or Mermaid component diagrams
   - Zero Trust IAM & PAB boundary definitions
   - WAF pillar alignment matrix
   - FDE Rubric compliance verification scorecard ($\ge 2.0 / 3.0$ cutline)

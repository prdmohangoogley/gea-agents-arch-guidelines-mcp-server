---
type: "Index"
title: "GEA Agent Development — Unified Architecture Best Practices & Well-Architected OKF Knowledge Base (L200 + L300 + L400 + WAF Pillars)"
description: "Root progressive-disclosure index for the unified L200, L300, L400, and Well-Architected Framework Pillars Open Knowledge Format (OKF v0.2) bundle."
timestamp: "2026-11-24T18:20:00-08:00"
status: "stable"
stale_after: "2027-05-24T18:20:00-08:00"
ttl: "P6M"
ttl_days: 180
corpus: "GEA_UNIFIED_L200_L300_L400_WAF"
version_tag: "GEA_UNIFIED_L200_L300_L400_WAF_2026-11-24_182000"
---

# GEA Agent Development — Unified Architecture Best Practices & FDE Grading Rubric Knowledge Base

Open Knowledge Format (`OKF v0.2`) bundle · **Version:** `GEAPL200_2026-09-30_124746` · **Corpus:** `GEAPL200` · **TTL:** `180 days` (Existing Version & TTL Preserved)

- **Backing Cloud Storage Bucket:** [`gs://gea_agent_development_architectural_best_practices_1790796607`](https://pantheon.corp.google.com/storage/browser/gea_agent_development_architectural_best_practices_1790796607?forceOnBucketsSortingFiltering=true&project=fivedaysai-prd-sandbox-317383) (`project=fivedaysai-prd-sandbox-317383`)
- **Cloud FDE Team Charter Reference:** [`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head)
- **Mandatory Project Grading Rubric Concept:** [`/concepts/00-fde-field-readiness-and-grading-rubric.md`](/concepts/00-fde-field-readiness-and-grading-rubric.md)

**Bundle Totals:** **83 Concepts** (Unified Flat Hierarchy) · **928 Mermaid Diagrams** · **1767 GFM Tables** · **5 Retained Figures** · **100% FDE Grading Rubric Enforcement**

---

## Mandatory Governance: Google Cloud FDE Field-Readiness & Project Grading Rubric

> **Enforceable Rule Across All Projects & Concepts:** Every architecture, prototype, skill, or application built using this OKF knowledge base must satisfy the [Google Cloud FDE Field-Readiness & Project Grading Rubric](/concepts/00-fde-field-readiness-and-grading-rubric.md) and the [Cloud FDE Charter](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).

### Grading Scale (0–3) & Pass Cutlines

| Score | Level | Definition | Enforcement Rule |
|---:|---|---|---|
| **0** | **Not Demonstrated** | Missed the mark, ignored the requirement, or could not answer basic questions. | **AUTOMATIC PAUSE:** Must remediate gaps and re-present within **2 weeks** if *any single metric* scores `0`. |
| **1** | **Awareness** | Understands the concept but struggles to apply it practically or misses critical edge cases. | Needs Additional Coaching (must be offset so section average >= 2.0). |
| **2** | **Competent (Pass)** | Articulates a solid approach, understands trade-offs, and meets Field-Ready FDE expectations. | **PASS BASELINE:** Requires an average score of **`>= 2.0`** in **Part A** AND **`>= 2.0`** in **Part B**. |
| **3** | **Proficient (Strong Pass)** | Demonstrates deep, production-level expertise, anticipates complex failure modes, and teaches the panel something new. | Exemplar Reference Architecture. |

### Rubric Competency Architecture (Enforced in Every Concept `01`–`57`)

| Rubric Section | Domain / Competency Cluster | Core Assessment Cutlines (`2 - Competent`) | Primary OKF Concepts |
|---|---|---|---|
| **Part A: Presentation & Advisory Rigor** | **1. Strategic Delivery & Value Articulation**<br>**2. Objection Handling & Technical Defense**<br>**3. Presentation Skills**<br>**4. AI-Driven Development Discussion**<br>**5. Futures / Roadmap** | Narrative walkthrough anchored to customer personas, CUJs, and a viable **TCO model** (no 'science projects'); calm, data-backed defense of trade-offs; disciplined time pacing & intellectual honesty; setup of **in-the-loop** and **outside-the-loop** GenAI harnesses where mistakes update agent instructions; phased GCP production roadmap. | [00](/concepts/00-fde-field-readiness-and-grading-rubric.md), [01](/concepts/01-ai-agent-quality-engineering.md), [11](/concepts/11-prototype-to-production.md), [13](/concepts/13-spec-driven-production-grade-development.md), [16](/concepts/16-the-new-sdlc-with-vibe-coding.md), [28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md), [31](/concepts/31-plan-change-management-for-gemini-enterprise-deployments.md) |
| **Part B.1: AI/ML Engineering** | **1. Agentic & Multi-Agent Systems** (>=2)<br>**2. Retrieval & Data Engineering** (>=1)<br>**3. Model Selection, Tuning & Optimization** (>=2)<br>**4. LLM Ops & Evaluation** (>=1, > Judge alone)<br>**5. Domain-Applied AI/ML Expertise** (>=1) | Cognitive orchestration (`Sequential`, `Parallel`, `Loop`), Session + Memory Bank retention, bounded loops; hybrid RAG + ACL citations; Flash/Pro routing, thinking budgets, `response_schema`; Tri-Partite eval (deterministic + SME + calibrated autoraters) + OpenTelemetry tracing; HIPAA/FINRA/EU AI Act vertical compliance. | [01](/concepts/01-ai-agent-quality-engineering.md), [05](/concepts/05-enterprise-ai-agent-systems-google-cloud.md), [07](/concepts/07-enterprise-agent-skills.md), [08](/concepts/08-context-engineering-stateful-agents.md), [21](/concepts/21-build-and-deploy-multi-agent-adk-systems.md), [24](/concepts/24-agent-with-persistent-memories-deep-dive.md), [25](/concepts/25-evaluate-generative-agentic-systems.md), [26](/concepts/26-hill-climbing-agentic-systems.md), [27](/concepts/27-upgrade-to-the-latest-models.md) |
| **Part B.2: Scoping & Documentation** | **1. Problem Definition** · **2. Technical Scope & Constraints** · **3. Stakeholder Alignment** · **4. System Design Artifacts** · **5. Decision Records (ADRs)** · **6. API Documentation** · **7. Operational Documentation** | CUJs & 'Definition of Done'; pre-build system boundaries; CoE RACI & phased delivery waves; Mermaid sequence/architecture diagrams; trade-off ADRs; OpenAPI / MCP schemas / A2A `AgentCard`; deployment & troubleshooting runbooks. | [03](/concepts/03-enterprise-ai-agent-protocol-stack.md), [04](/concepts/04-deploying-gemini-enterprise-agent-runtime.md), [13](/concepts/13-spec-driven-production-grade-development.md), [17](/concepts/17-agents-concepts-visually-explained.md), [18](/concepts/18-agent-tools-interoperability-with-mcp.md), [29](/concepts/29-deploy-the-gemini-enterprise-app.md), [31](/concepts/31-plan-change-management-for-gemini-enterprise-deployments.md) |
| **Part B.3: Security, Privacy & Compliance** | **1. Authentication & Authorization** (>=2)<br>**2. Infrastructure & Network Security** (>=2)<br>**3. Data Protection & Privacy** (>=2)<br>**4. AI-Specific Security** (>=2)<br>**5. Compliance & Governance** (>=1) | Per-agent identities (`principal://`), WIF (SAML/OIDC + CEL), 3-legged OAuth (Auth Manager), PAB; VPC-SC, CAA, PSC-I, isolated `AgentSandbox`, Agent Gateway; CMEK, mTLS, Cloud DLP (SDP); **Model Armor** inline input + tool-output sanitization; dual-principal audit logs & data residency. | [02](/concepts/02-vibe-coding-agent-security-evaluation-kb.md), [10](/concepts/10-vibe-coding-agent-security-and-evaluation.md), [22](/concepts/22-build-enterprise-agents-with-code-execution.md), [29](/concepts/29-deploy-the-gemini-enterprise-app.md), [30](/concepts/30-third-party-idp-with-workforce-identity-federation.md), [33](/concepts/33-model-armor-securing-ai-deployments.md), [34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md), [35](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md) |
| **Part B.4: Reliability & Resilience** | **1. Availability Design** · **2. Observability** · **3. Failure & Recovery Testing** · **4. Graceful Degradation** | Semantic SLIs/SLOs & tool idempotency keys; structured JSON logs + OTel spans + Agent Quality Dashboard; red-teaming & persona simulation; circuit breakers, 3–5 min SSE timeouts, async polling, and HITL fallbacks. | [01](/concepts/01-ai-agent-quality-engineering.md), [05](/concepts/05-enterprise-ai-agent-systems-google-cloud.md), [12](/concepts/12-agent-quality.md), [25](/concepts/25-evaluate-generative-agentic-systems.md), [29](/concepts/29-deploy-the-gemini-enterprise-app.md), [32](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md) |
| **Part B.5: Performance & Cost Optimization** | **1. Scalability & Elasticity** · **2. Resource Efficiency** · **3. AI Cost Management (FinOps)** | Stateless horizontal scaling & `ParallelAgent` fan-out; GSU Provisioned Throughput baseline + PAYG burst + Batch Inference (50% off); Context Caching (75–90% savings), Flash/Pro tiering, `tool_filter`, and session compaction. | [07](/concepts/07-enterprise-agent-skills.md), [08](/concepts/08-context-engineering-stateful-agents.md), [22](/concepts/22-build-enterprise-agents-with-code-execution.md), [24](/concepts/24-agent-with-persistent-memories-deep-dive.md), [28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md) |
| **Part B.6: Operational Excellence** | **1. CI/CD & Deployment** · **2. Infrastructure as Code (IaC)** · **3. AI Lifecycle Management** · **4. Testing & Quality Engineering** | Automated evaluation gates + Shadow/Canary deployment rings (`< 5 min` rollback); Terraform & Cloud Build parity; version-stamped bundles (`GEAPL200_2026-09-30_124746`) & SxS experiment tracking; unit + contract + trajectory + load testing. | [04](/concepts/04-deploying-gemini-enterprise-agent-runtime.md), [11](/concepts/11-prototype-to-production.md), [25](/concepts/25-evaluate-generative-agentic-systems.md), [27](/concepts/27-upgrade-to-the-latest-models.md), [32](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md) |
| **Part B.7: Designing for Change** | **1. Modularity & Abstraction** · **2. Configuration Management** · **3. API Design & Versioning** · **4. Extensibility** | Model-agnostic aliases & swappable `SessionService`/`MemoryService`; externalized env configs & feature flags; backward-compatible MCP/A2A/OKF schemas; ADK lifecycle callbacks (`before_model`, `before_tool`, `after_agent`) & `SKILL.md` plugins. | [03](/concepts/03-enterprise-ai-agent-protocol-stack.md), [07](/concepts/07-enterprise-agent-skills.md), [14](/concepts/14-agent-skills.md), [18](/concepts/18-agent-tools-interoperability-with-mcp.md), [21](/concepts/21-build-and-deploy-multi-agent-adk-systems.md), [34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md) |

---

## Unified Concepts Catalog (`00`–`57`)

### Governance Anchor (`00`)
- [`00` — Architecture Best Practice: Google Cloud FDE Field-Readiness & Project Grading Rubric (Mandatory Governance Standard)](/concepts/00-fde-field-readiness-and-grading-rubric.md) — `#fde-grading-rubric` `#field-readiness` `#advisory-rigor` `#engineering-excellence`

### Part I: Existing GCS Bucket Concepts (`01`–`20` — `GEAPL200` Merged with FDE Grading Rubric)
- [Architecture Best Practice: AI Agent Quality — Evaluation, Observability, Cost & Security Engineering](/concepts/01-ai-agent-quality-engineering.md) — `agent-evaluation` `trajectory-evaluation` `observability` `agent-security` `cost-optimization`
- [Architecture Best Practice: Vibe Coding Agent Security & Evaluation — Sandboxing, Zero Ambient Authority, Agentic SecOps & Session Convergence](/concepts/02-vibe-coding-agent-security-evaluation-kb.md) — `agent-security` `vibe-coding` `sandboxing` `supply-chain-security` `zero-ambient-authority`
- [Architecture Best Practice: The Open AI Agent Protocol Stack on Google Cloud (MCP · A2A · UCP · AP2/x402 · A2UI · AG-UI)](/concepts/03-enterprise-ai-agent-protocol-stack.md) — `agent-protocols` `mcp` `a2a` `ap2` `generative-ui`
- [Architecture Best Practice: Deploying to Agent Runtime — Prerequisites, Cloud Shell Execution & Deployment Troubleshooting](/concepts/04-deploying-gemini-enterprise-agent-runtime.md) — `gemini-enterprise` `agent-runtime` `deployment` `google-cloud` `troubleshooting`
- [Architecture Best Practice: Enterprise AI Agent Systems on Google Cloud](/concepts/05-enterprise-ai-agent-systems-google-cloud.md) — `enterprise-agents` `google-cloud` `agent-architecture` `multi-agent-orchestration` `agent-security`
- [Architecture Best Practice: Agent Tools, MCP Interoperability & Multi-Agent Orchestration on Google Cloud](/concepts/06-agent-tools-mcp-multi-agent-orchestration.md) — `agent-tools` `mcp` `multi-agent-orchestration` `google-cloud` `agent-security`
- [Architecture Best Practice: Enterprise Agent Skills — Progressive Disclosure, Capability Profiles & Skill Lifecycle Engineering](/concepts/07-enterprise-agent-skills.md) — `agent-skills` `progressive-disclosure` `context-engineering` `agent-evaluation` `enterprise-agents`
- [Architecture Best Practice: Context Engineering for Stateful AI Agents on Google Cloud — Sessions, Memory & Governance](/concepts/08-context-engineering-stateful-agents.md) — `context-engineering` `sessions` `memory` `rag` `adk`
- [Architecture Best Practice: Platform-Native State Management with Gemini Enterprise Agent Runtime & Memory Bank](/concepts/09-platform-native-state-management.md) — `gemini-enterprise` `agent-runtime` `memory-bank` `state-management` `managed-services`
- [Vibe Coding Agent Security and Evaluation](/concepts/10-vibe-coding-agent-security-and-evaluation.md) — `agent-security` `vibe-coding` `sandboxing` `agent-evaluation` `agentops`
- [Prototype to Production](/concepts/11-prototype-to-production.md) — `agentops` `prototype-to-production` `cicd` `agent-evaluation` `observability`
- [Agent Quality](/concepts/12-agent-quality.md) — `agent-evaluation` `agent-quality` `observability` `agentops` `llm-as-judge`
- [Spec-Driven Production Grade Development in the Age of Vibe Coding](/concepts/13-spec-driven-production-grade-development.md) — `spec-driven-development` `vibe-coding` `agentic-ai` `code-review` `agent-guardrails`
- [Agent Skills](/concepts/14-agent-skills.md) — `agent-skills` `progressive-disclosure` `context-engineering` `agent-evals` `adk`
- [Introduction to Agents](/concepts/15-introduction-to-agents.md) — `ai-agents` `agent-architecture` `agent-ops` `multi-agent-systems` `agent-security`
- [The New SDLC With Vibe Coding: From ad-hoc prompting to Agentic Engineering](/concepts/16-the-new-sdlc-with-vibe-coding.md) — `vibe-coding` `agentic-engineering` `sdlc` `context-engineering` `harness-engineering`
- [Agents Concepts Visually Explained](/concepts/17-agents-concepts-visually-explained.md) — `ai-agents` `agent-architecture` `adk` `mcp-a2a-ap2` `agent-security`
- [Agent Tools & Interoperability with MCP](/concepts/18-agent-tools-interoperability-with-mcp.md) — `mcp` `agent-tools` `interoperability` `tool-calling` `agentic-ai`
- [Agent Tools & Interoperability](/concepts/19-agent-tools-interoperability-2.md) — `agent-tools` `interoperability` `mcp` `a2a` `a2ui`
- [Context Engineering — Sessions, Memory](/concepts/20-context-engineering-sessions-memory.md) — `context-engineering` `sessions` `memory` `llm-agents` `agent-state`

### Part II: Extended L300 Concepts (`21`–`35` — `GEAP L300` Synthesized with FDE Grading Rubric)
- [Architecture Best Practice: Build and Deploy Multi-Agent ADK Systems to Gemini Enterprise](/concepts/21-build-and-deploy-multi-agent-adk-systems.md) — `google-adk` `multi-agent-systems` `gemini-enterprise` `agent-runtime` `mcp`
- [Architecture Best Practice: Build Enterprise Agents with Code Execution on Gemini Enterprise Agent Platform](/concepts/22-build-enterprise-agents-with-code-execution.md) — `code-execution` `agent-sandbox` `gemini-enterprise` `google-adk` `agent-security`
- [Architecture Best Practice: Agent Context Persistence, Sessions, and Memory Engineering](/concepts/23-agent-context-persistence-and-memories.md) — `context-engineering` `session-management` `agent-memory` `memory-bank` `google-adk`
- [Architecture Best Practice: Stateful Agents with Persistent Memories and Vertex AI Memory Bank](/concepts/24-agent-with-persistent-memories-deep-dive.md) — `memory-bank` `session-history` `multi-agent-context` `context-compaction` `google-adk`
- [Architecture Best Practice: Evaluating Generative and Agentic Systems on Google Cloud](/concepts/25-evaluate-generative-agentic-systems.md) — `agent-evaluation` `trajectory-evaluation` `autoraters` `llm-as-a-judge` `vertex-ai-evaluation`
- [Architecture Best Practice: Hill Climbing and Continuous Quality Optimization for Agentic Systems](/concepts/26-hill-climbing-agentic-systems.md) — `hill-climbing` `agent-optimization` `agent-evaluation` `prompt-refactoring` `trajectory-analysis`
- [Architecture Best Practice: Model Lifecycle Migration and Upgrading to the Latest Gemini Models](/concepts/27-upgrade-to-the-latest-models.md) — `model-migration` `gemini-models` `prompt-debt` `thinking-models` `shadow-deployment`
- [Architecture Best Practice: Cost Estimation, FinOps, and Token Optimization for Agentic Solutions](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md) — `cost-optimization` `finops` `token-economics` `context-caching` `provisioned-throughput`
- [Architecture Best Practice: Preparing and Deploying the Gemini Enterprise Application](/concepts/29-deploy-the-gemini-enterprise-app.md) — `gemini-enterprise` `enterprise-deployment` `vpc-service-controls` `context-aware-access` `cmek`
- [Architecture Best Practice: Third-Party Identity Provider Integration with Workforce Identity Federation](/concepts/30-third-party-idp-with-workforce-identity-federation.md) — `workforce-identity-federation` `iam` `identity-provider` `saml` `oidc`
- [Architecture Best Practice: Organizational Change Management for Gemini Enterprise Deployments](/concepts/31-plan-change-management-for-gemini-enterprise-deployments.md) — `change-management` `gemini-enterprise` `ai-governance` `center-of-excellence` `enterprise-adoption`
- [Architecture Best Practice: Lifecycle Change Management and Rollout Governance for Gemini Enterprise Agents](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md) — `agent-change-management` `gemini-enterprise` `release-governance` `canary-deployment` `human-in-the-loop`
- [Architecture Best Practice: Securing AI and Agentic Deployments with Google Cloud Model Armor](/concepts/33-model-armor-securing-ai-deployments.md) — `model-armor` `ai-security` `prompt-injection` `jailbreak-protection` `sensitive-data-protection`
- [Architecture Best Practice: Securing Enterprise Agents with Gemini Enterprise Agent Platform](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md) — `agent-security` `agent-identity` `principal-access-boundary` `delegated-oauth` `confused-deputy`
- [Architecture Best Practice: Governing the Agent Ecosystem with Agent Gateway, Agent Registry, and Policies](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md) — `agent-governance` `agent-gateway` `agent-registry` `a2a-protocol` `mcp-governance`

---

### Part III: Extended L400 Concepts (`36`–`57` — Master Architecture, Identity, Security, Scale, Governance, Autoraters, Coding Agents, FinOps, Nexus, AlphaEvolve, FAQ & Cross-KB Best Practices)
- [Architecture Best Practice: Master OKF Knowledge Catalog Index & Antigravity Agentic AI Blueprint (L400)](/concepts/36-l400-00-master-knowledge-catalog-index.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Gemini Enterprise Overall Architecture — Flattened Orchestration & Spark Sandboxes](/concepts/37-l400-a1-overall-architecture.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Identity Architecture — Cloud Identity, Workforce Identity Federation & SCIM](/concepts/38-l400-a2-identity-architecture.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Gemini Enterprise Network Architecture and Security — PSC, VPC-SC & CMEK](/concepts/39-l400-a3-network-architecture-and-security.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: API Integration, Federated Connector OAuth & Bring-Your-Own MCP](/concepts/40-l400-a4-api-integration-federated-connector-byo-mcp.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: End-to-End Debugging, Observability & Diagnostic Tooling](/concepts/41-l400-a5-debugging-and-troubleshooting.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Anatomy of an Enterprise Agent — ADK 2.0 Internals & Multi-Agent Mechanics](/concepts/42-l400-b1-anatomy-of-an-enterprise-agent.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: A2A Protocol and Multi-Agent Mechanics — Agent Cards & Interoperability](/concepts/43-l400-b2-a2a-protocol-and-multi-agent-mechanics.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Agent Skills and the Skills Registry — Progressive Disclosure & SOPs](/concepts/44-l400-b3-agent-skills-and-skills-registry.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Zero-Trust Identity Foundation for Enterprise Agentic AI](/concepts/45-l400-g1-zero-trust-identity-foundation.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Managing Production Agents at Scale — Multi-Region Fleets & Circuit Breakers](/concepts/46-l400-g2-managing-production-agents-at-scale.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Enterprise Agent Governance — Zero-Trust Network Perimeter & Model Armor](/concepts/47-l400-g3-agent-governance.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: More Reliable Autoraters — Enterprise Agentic AI Evaluation & Bias Mitigation](/concepts/48-l400-o1-more-reliable-autoraters.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: DeepMind Troubleshooting Tool — Label-Free Diagnostics & Trajectory Observability](/concepts/49-l400-o2-deepmind-troubleshooting-tool.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Design & Optimization of Coding Agents — Harness Architecture & Antigravity](/concepts/50-l400-o3-design-and-optimization-of-coding-agents.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Cost & Token Estimation, Analysis, and Optimization (FinOps)](/concepts/51-l400-o4-cost-token-estimation-analysis-and-optimization.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Project Nexus — Gemini Model Quality Reporting & Diagnostic Bisection](/concepts/52-l400-o5-project-nexus-model-quality-reporting.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: AlphaEvolve — Autonomous Evolutionary Algorithm Discovery & Optimization](/concepts/53-l400-o6-alpha-evolve.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Master L400 Topic Modeling, Cross-KB Connectivity & Agent Flow Graph](/concepts/54-l400-18-topic-connection-and-flow-graph.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Master Enterprise Architecture & Implementation FAQ Compendium](/concepts/55-l400-19-master-enterprise-faq-compendium.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Cross-Knowledge-Base Best Practices & Enterprise Customer Use Cases](/concepts/56-l400-20-cross-kb-best-practices-and-customer-use-cases.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`
- [Architecture Best Practice: Enforceable FDE Field-Readiness & Project Grading Rubric Standard (L400 Standard)](/concepts/57-l400-21-fde-grading-rubric-and-field-readiness-standard.md) — `l400` `gemini-enterprise` `google-cloud` `fde-grading-rubric`

## Freshness, Provenance & Structural Inventory (Updated 2026-11-24 · 6-Month Expiry `2027-05-24`)

| # | Concept | Tier | Version Tag | Mermaid | Tables | Status | Stale After |
|---:|---|---|---|---:|---:|---|---|
| 00 | [Architecture Best Practice: Google Cloud FDE Field-Readiness & Pr...](/concepts/00-fde-field-readiness-and-grading-rubric.md) | L200 | `L200_OKF_2026-11-24_182000` | 1 | 17 | stable | 2027-05-24 |
| 01 | [Architecture Best Practice: AI Agent Quality — Evaluation, Observ...](/concepts/01-ai-agent-quality-engineering.md) | L200 | `L200_OKF_2026-11-24_182000` | 0 | 12 | stable | 2027-05-24 |
| 02 | [Architecture Best Practice: Vibe Coding Agent Security & Evaluati...](/concepts/02-vibe-coding-agent-security-evaluation-kb.md) | L200 | `L200_OKF_2026-11-24_182000` | 0 | 8 | stable | 2027-05-24 |
| 03 | [Architecture Best Practice: The Open AI Agent Protocol Stack on G...](/concepts/03-enterprise-ai-agent-protocol-stack.md) | L200 | `L200_OKF_2026-11-24_182000` | 7 | 5 | stable | 2027-05-24 |
| 04 | [Architecture Best Practice: Deploying to Agent Runtime — Prerequi...](/concepts/04-deploying-gemini-enterprise-agent-runtime.md) | L200 | `L200_OKF_2026-11-24_182000` | 2 | 10 | stable | 2027-05-24 |
| 05 | [Architecture Best Practice: Enterprise AI Agent Systems on Google...](/concepts/05-enterprise-ai-agent-systems-google-cloud.md) | L200 | `L200_OKF_2026-11-24_182000` | 0 | 2 | stable | 2027-05-24 |
| 06 | [Architecture Best Practice: Agent Tools, MCP Interoperability & M...](/concepts/06-agent-tools-mcp-multi-agent-orchestration.md) | L200 | `L200_OKF_2026-11-24_182000` | 0 | 2 | stable | 2027-05-24 |
| 07 | [Architecture Best Practice: Enterprise Agent Skills — Progressive...](/concepts/07-enterprise-agent-skills.md) | L200 | `L200_OKF_2026-11-24_182000` | 0 | 10 | stable | 2027-05-24 |
| 08 | [Architecture Best Practice: Context Engineering for Stateful AI A...](/concepts/08-context-engineering-stateful-agents.md) | L200 | `L200_OKF_2026-11-24_182000` | 0 | 10 | stable | 2027-05-24 |
| 09 | [Architecture Best Practice: Platform-Native State Management with...](/concepts/09-platform-native-state-management.md) | L200 | `L200_OKF_2026-11-24_182000` | 0 | 4 | stable | 2027-05-24 |
| 10 | [Vibe Coding Agent Security and Evaluation](/concepts/10-vibe-coding-agent-security-and-evaluation.md) | L200 | `L200_OKF_2026-11-24_182000` | 2 | 2 | stable | 2027-05-24 |
| 11 | [Prototype to Production](/concepts/11-prototype-to-production.md) | L200 | `L200_OKF_2026-11-24_182000` | 5 | 1 | stable | 2027-05-24 |
| 12 | [Agent Quality](/concepts/12-agent-quality.md) | L200 | `L200_OKF_2026-11-24_182000` | 4 | 3 | stable | 2027-05-24 |
| 13 | [Spec-Driven Production Grade Development in the Age of Vibe Coding](/concepts/13-spec-driven-production-grade-development.md) | L200 | `L200_OKF_2026-11-24_182000` | 1 | 1 | stable | 2027-05-24 |
| 14 | [Agent Skills](/concepts/14-agent-skills.md) | L200 | `L200_OKF_2026-11-24_182000` | 9 | 6 | stable | 2027-05-24 |
| 15 | [Introduction to Agents](/concepts/15-introduction-to-agents.md) | L200 | `L200_OKF_2026-11-24_182000` | 10 | 2 | stable | 2027-05-24 |
| 16 | [The New SDLC With Vibe Coding: From ad-hoc prompting to Agentic E...](/concepts/16-the-new-sdlc-with-vibe-coding.md) | L200 | `L200_OKF_2026-11-24_182000` | 8 | 2 | stable | 2027-05-24 |
| 17 | [Agents Concepts Visually Explained](/concepts/17-agents-concepts-visually-explained.md) | L200 | `L200_OKF_2026-11-24_182000` | 5 | 7 | stable | 2027-05-24 |
| 18 | [Agent Tools & Interoperability with MCP](/concepts/18-agent-tools-interoperability-with-mcp.md) | L200 | `L200_OKF_2026-11-24_182000` | 3 | 2 | stable | 2027-05-24 |
| 19 | [Agent Tools & Interoperability](/concepts/19-agent-tools-interoperability-2.md) | L200 | `L200_OKF_2026-11-24_182000` | 11 | 3 | stable | 2027-05-24 |
| 20 | [Context Engineering — Sessions, Memory](/concepts/20-context-engineering-sessions-memory.md) | L200 | `L200_OKF_2026-11-24_182000` | 6 | 2 | stable | 2027-05-24 |
| 21 | [Architecture Best Practice: Build and Deploy Multi-Agent ADK Syst...](/concepts/21-build-and-deploy-multi-agent-adk-systems.md) | L300 | `L300_OKF_2026-11-24_182000` | 12 | 12 | stable | 2027-05-24 |
| 22 | [Architecture Best Practice: Build Enterprise Agents with Code Exe...](/concepts/22-build-enterprise-agents-with-code-execution.md) | L300 | `L300_OKF_2026-11-24_182000` | 5 | 6 | stable | 2027-05-24 |
| 23 | [Architecture Best Practice: Agent Context Persistence, Sessions, ...](/concepts/23-agent-context-persistence-and-memories.md) | L300 | `L300_OKF_2026-11-24_182000` | 8 | 8 | stable | 2027-05-24 |
| 24 | [Architecture Best Practice: Stateful Agents with Persistent Memor...](/concepts/24-agent-with-persistent-memories-deep-dive.md) | L300 | `L300_OKF_2026-11-24_182000` | 21 | 78 | stable | 2027-05-24 |
| 25 | [Architecture Best Practice: Evaluating Generative and Agentic Sys...](/concepts/25-evaluate-generative-agentic-systems.md) | L300 | `L300_OKF_2026-11-24_182000` | 58 | 133 | stable | 2027-05-24 |
| 26 | [Architecture Best Practice: Hill Climbing and Continuous Quality ...](/concepts/26-hill-climbing-agentic-systems.md) | L300 | `L300_OKF_2026-11-24_182000` | 144 | 116 | stable | 2027-05-24 |
| 27 | [Architecture Best Practice: Model Lifecycle Migration and Upgradi...](/concepts/27-upgrade-to-the-latest-models.md) | L300 | `L300_OKF_2026-11-24_182000` | 34 | 31 | stable | 2027-05-24 |
| 28 | [Architecture Best Practice: Cost Estimation, FinOps, and Token Op...](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md) | L300 | `L300_OKF_2026-11-24_182000` | 43 | 91 | stable | 2027-05-24 |
| 29 | [Architecture Best Practice: Preparing and Deploying the Gemini En...](/concepts/29-deploy-the-gemini-enterprise-app.md) | L300 | `L300_OKF_2026-11-24_182000` | 36 | 93 | stable | 2027-05-24 |
| 30 | [Architecture Best Practice: Third-Party Identity Provider Integra...](/concepts/30-third-party-idp-with-workforce-identity-federation.md) | L300 | `L300_OKF_2026-11-24_182000` | 56 | 112 | stable | 2027-05-24 |
| 31 | [Architecture Best Practice: Organizational Change Management for ...](/concepts/31-plan-change-management-for-gemini-enterprise-deployments.md) | L300 | `L300_OKF_2026-11-24_182000` | 54 | 113 | stable | 2027-05-24 |
| 32 | [Architecture Best Practice: Lifecycle Change Management and Rollo...](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md) | L300 | `L300_OKF_2026-11-24_182000` | 54 | 113 | stable | 2027-05-24 |
| 33 | [Architecture Best Practice: Securing AI and Agentic Deployments w...](/concepts/33-model-armor-securing-ai-deployments.md) | L300 | `L300_OKF_2026-11-24_182000` | 54 | 105 | stable | 2027-05-24 |
| 34 | [Architecture Best Practice: Securing Enterprise Agents with Gemin...](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md) | L300 | `L300_OKF_2026-11-24_182000` | 53 | 45 | stable | 2027-05-24 |
| 35 | [Architecture Best Practice: Governing the Agent Ecosystem with Ag...](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md) | L300 | `L300_OKF_2026-11-24_182000` | 57 | 179 | stable | 2027-05-24 |
| 36 | [Architecture Best Practice: Agentic Context Engineering (ACE) — E...](/concepts/36-agentic-context-engineering-evolving-playbooks.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 9 | stable | 2027-05-24 |
| 37 | [Architecture Best Practice: Foundations of AI Tokenomics — Dual-V...](/concepts/36-foundations-of-ai-tokenomics-and-dual-view-production.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 8 | stable | 2027-05-24 |
| 38 | [Architecture Best Practice: Master OKF Knowledge Catalog Index & ...](/concepts/36-l400-00-master-knowledge-catalog-index.md) | L400 | `L400_OKF_2026-11-24_182000` | 1 | 3 | stable | 2027-05-24 |
| 39 | [Socratic Prompting Foundations, CRIT Algorithm & The Socratic Met...](/concepts/36-socratic-prompting-foundations-and-crit-taxonomy.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 10 | stable | 2027-05-24 |
| 40 | [Agent Grills the User: Structured Socratic Inquiry, KELE Multi-Ag...](/concepts/37-agent-grills-user-structured-socratic-inquiry-kele.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 9 | stable | 2027-05-24 |
| 41 | [Architecture Best Practice: Tokenomics of Agent-to-User Grilling ...](/concepts/37-agent-user-grilling-tokenomics-chatbot-elicitation.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 7 | stable | 2027-05-24 |
| 42 | [Architecture Best Practice: Cache Engineering for Agents — Direct...](/concepts/37-cache-engineering-kv-prefix-optimization-for-agents.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 6 | stable | 2027-05-24 |
| 43 | [Architecture Best Practice: Gemini Enterprise Overall Architectur...](/concepts/37-l400-a1-overall-architecture.md) | L400 | `L400_OKF_2026-11-24_182000` | 7 | 12 | stable | 2027-05-24 |
| 44 | [Case 2A: Agent-Grills-Agent via Identity-Grounded Heterogeneous D...](/concepts/38-agent-grills-agent-heterogeneous-debate-and-identity-grounding.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 8 | stable | 2027-05-24 |
| 45 | [Architecture Best Practice: Tokenomics of Inter-Agent Grilling, C...](/concepts/38-inter-agent-grilling-debate-critic-tokenomics.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 7 | stable | 2027-05-24 |
| 46 | [Architecture Best Practice: Identity Architecture — Cloud Identit...](/concepts/38-l400-a2-identity-architecture.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 13 | stable | 2027-05-24 |
| 47 | [Architecture Best Practice: Structured File-Native & Open-Source ...](/concepts/38-structured-file-native-and-oss-context-engineering.md) | L400 | `L400_OKF_2026-11-24_182000` | 1 | 9 | stable | 2027-05-24 |
| 48 | [Architecture Best Practice: Corporate Multi-Agent Context Archite...](/concepts/39-corporate-multi-agent-context-architecture-and-memory-tiers.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 6 | stable | 2027-05-24 |
| 49 | [Architecture Best Practice: Gemini Enterprise Network Architectur...](/concepts/39-l400-a3-network-architecture-and-security.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 11 | stable | 2027-05-24 |
| 50 | [Case 2B: Multi-Agent Collaborative Grilling, Constraint Satisfact...](/concepts/39-multi-agent-collaborative-grilling-and-temporal-planning-maci.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 9 | stable | 2027-05-24 |
| 51 | [Architecture Best Practice: Networked Workflow DAG Token Allocati...](/concepts/39-workflow-dag-token-allocation-and-adjoint-optimization.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 5 | stable | 2027-05-24 |
| 52 | [Architecture Best Practice: Intensive-Margin Communication Compre...](/concepts/40-intensive-margin-protocol-compression-and-runtime-cascades.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 7 | stable | 2027-05-24 |
| 53 | [Architecture Best Practice: API Integration, Federated Connector ...](/concepts/40-l400-a4-api-integration-federated-connector-byo-mcp.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 9 | stable | 2027-05-24 |
| 54 | [Architecture Best Practice: Meta Context Engineering (MCE) via Ag...](/concepts/40-meta-context-engineering-and-agentic-skill-evolution.md) | L400 | `L400_OKF_2026-11-24_182000` | 1 | 5 | stable | 2027-05-24 |
| 55 | [Recursive Socratic Questioning (Top-Down Decomposition & Bottom-U...](/concepts/40-recursive-socratic-questioning-and-soda-chain-of-thought.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 9 | stable | 2027-05-24 |
| 56 | [Architecture Best Practice: End-to-End Debugging, Observability &...](/concepts/41-l400-a5-debugging-and-troubleshooting.md) | L400 | `L400_OKF_2026-11-24_182000` | 5 | 10 | stable | 2027-05-24 |
| 57 | [Architecture Best Practice: Multi-Agent KV-Cache Capital Deepenin...](/concepts/41-multi-agent-kv-cache-sharing-and-memory-inventory-tokenomics.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 8 | stable | 2027-05-24 |
| 58 | [Socratic Autoraters (SOCREVAL) and Outcome-Driven Question Optimi...](/concepts/41-socratic-autoraters-socreval-and-outcome-driven-question-optimization.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 9 | stable | 2027-05-24 |
| 59 | [Architecture Best Practice: Socratic Grilling & Prompting in Mult...](/concepts/41-socratic-grilling-user-to-agent-and-agent-to-agent-protocols.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 4 | stable | 2027-05-24 |
| 60 | [Architecture Best Practice: Anatomy of an Enterprise Agent — ADK ...](/concepts/42-l400-b1-anatomy-of-an-enterprise-agent.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 13 | stable | 2027-05-24 |
| 61 | [Architecture Best Practice: Multi-Agent Memory Lifecycle & Contex...](/concepts/42-multi-agent-memory-lifecycle-and-context-rot-prevention.md) | L400 | `L400_OKF_2026-11-24_182000` | 1 | 4 | stable | 2027-05-24 |
| 62 | [Architecture Best Practice: Security-Conditioned Token Economics,...](/concepts/42-security-tokenomics-and-ecosystem-market-design.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 7 | stable | 2027-05-24 |
| 63 | [Architecture Best Practice: Cross-KB Topic Connection & Mermaid F...](/concepts/43-context-cache-memory-topic-connection-and-flow-graph.md) | L400 | `L400_OKF_2026-11-24_182000` | 2 | 3 | stable | 2027-05-24 |
| 64 | [Architecture Best Practice: A2A Protocol and Multi-Agent Mechanic...](/concepts/43-l400-b2-a2a-protocol-and-multi-agent-mechanics.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 11 | stable | 2027-05-24 |
| 65 | [Architecture Best Practice: Multi-Agent Tokenomics & Grilling Mas...](/concepts/43-tokenomics-master-faq-and-pca-scenario-compendium.md) | L400 | `L400_OKF_2026-11-24_182000` | 1 | 7 | stable | 2027-05-24 |
| 66 | [Architecture Best Practice: Master Enterprise FAQ Compendium & En...](/concepts/44-fde-socratic-grilling-rubric-and-faq-compendium.md) | L400 | `L400_OKF_2026-11-24_182000` | 1 | 5 | stable | 2027-05-24 |
| 67 | [Architecture Best Practice: Agent Skills and the Skills Registry ...](/concepts/44-l400-b3-agent-skills-and-skills-registry.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 15 | stable | 2027-05-24 |
| 68 | [Architecture Best Practice: Zero-Trust Identity Foundation for En...](/concepts/45-l400-g1-zero-trust-identity-foundation.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 12 | stable | 2027-05-24 |
| 69 | [Architecture Best Practice: Managing Production Agents at Scale —...](/concepts/46-l400-g2-managing-production-agents-at-scale.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 14 | stable | 2027-05-24 |
| 70 | [Architecture Best Practice: Enterprise Agent Governance — Zero-Tr...](/concepts/47-l400-g3-agent-governance.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 13 | stable | 2027-05-24 |
| 71 | [Architecture Best Practice: More Reliable Autoraters — Enterprise...](/concepts/48-l400-o1-more-reliable-autoraters.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 13 | stable | 2027-05-24 |
| 72 | [Architecture Best Practice: DeepMind Troubleshooting Tool — Label...](/concepts/49-l400-o2-deepmind-troubleshooting-tool.md) | L400 | `L400_OKF_2026-11-24_182000` | 7 | 9 | stable | 2027-05-24 |
| 73 | [Architecture Best Practice: Design & Optimization of Coding Agent...](/concepts/50-l400-o3-design-and-optimization-of-coding-agents.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 13 | stable | 2027-05-24 |
| 74 | [Architecture Best Practice: Cost & Token Estimation, Analysis, an...](/concepts/51-l400-o4-cost-token-estimation-analysis-and-optimization.md) | L400 | `L400_OKF_2026-11-24_182000` | 5 | 15 | stable | 2027-05-24 |
| 75 | [Architecture Best Practice: Project Nexus — Gemini Model Quality ...](/concepts/52-l400-o5-project-nexus-model-quality-reporting.md) | L400 | `L400_OKF_2026-11-24_182000` | 6 | 10 | stable | 2027-05-24 |
| 76 | [Architecture Best Practice: AlphaEvolve — Autonomous Evolutionary...](/concepts/53-l400-o6-alpha-evolve.md) | L400 | `L400_OKF_2026-11-24_182000` | 5 | 15 | stable | 2027-05-24 |
| 77 | [Architecture Best Practice: Master L400 Topic Modeling, Cross-KB ...](/concepts/54-l400-18-topic-connection-and-flow-graph.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 10 | stable | 2027-05-24 |
| 78 | [Architecture Best Practice: Master Enterprise Architecture & Impl...](/concepts/55-l400-19-master-enterprise-faq-compendium.md) | L400 | `L400_OKF_2026-11-24_182000` | 1 | 12 | stable | 2027-05-24 |
| 79 | [Architecture Best Practice: Cross-Knowledge-Base Best Practices &...](/concepts/56-l400-20-cross-kb-best-practices-and-customer-use-cases.md) | L400 | `L400_OKF_2026-11-24_182000` | 8 | 6 | stable | 2027-05-24 |
| 80 | [Architecture Best Practice: Enforceable FDE Field-Readiness & Pro...](/concepts/57-l400-21-fde-grading-rubric-and-field-readiness-standard.md) | L400 | `L400_OKF_2026-11-24_182000` | 1 | 12 | stable | 2027-05-24 |
| 81 | [Multi-Agent Tokenomics, Agent-to-User Grilling & Inter-Agent Crit...](/concepts/58-l400-o7-multi-agent-tokenomics-and-grilling-best-practices.md) | L400 | `L400_OKF_2026-11-24_182000` | 1 | 4 | stable | 2027-05-24 |
| 82 | [OKF-L400-S0: Socratic Grilling & Prompting for Multi-Agent System...](/concepts/59-l400-s0-master-socratic-grilling-and-prompting-architecture.md) | L400 | `L400_OKF_2026-11-24_182000` | 3 | 5 | stable | 2027-05-24 |

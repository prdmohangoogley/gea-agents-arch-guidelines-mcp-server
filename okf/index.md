---
type: "Index"
title: "GEA Agent Development — Unified Architecture Best Practices & FDE Grading Rubric Knowledge Base (L200 + L300 + L400)"
description: "Root progressive-disclosure index for the unified GEAPL200 + GEAPL300 + L400 Open Knowledge Format (OKF v0.2) bundle, enforcing the Google Cloud FDE Field-Readiness Grading Rubric across all 58 concepts."
timestamp: "2026-09-30T12:47:46-07:00"
status: "draft"
stale_after: "2027-03-29T12:47:46-07:00"
corpus: "GEAPL200"
version_tag: "GEAPL200_2026-09-30_124746"
---

# GEA Agent Development — Unified Architecture Best Practices & FDE Grading Rubric Knowledge Base

Open Knowledge Format (`OKF v0.2`) bundle · **Version:** `GEAPL200_2026-09-30_124746` · **Corpus:** `GEAPL200` · **TTL:** `180 days` (Existing Version & TTL Preserved)

- **Backing Cloud Storage Bucket:** [`gs://gea_agent_development_architectural_best_practices_1790796607`](https://pantheon.corp.google.com/storage/browser/gea_agent_development_architectural_best_practices_1790796607?forceOnBucketsSortingFiltering=true&project=fivedaysai-prd-sandbox-317383) (`project=fivedaysai-prd-sandbox-317383`)
- **Cloud FDE Team Charter Reference:** [`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head)
- **Mandatory Project Grading Rubric Concept:** [`/concepts/00-fde-field-readiness-and-grading-rubric.md`](/concepts/00-fde-field-readiness-and-grading-rubric.md)

**Bundle Totals:** **58 Concepts** (1 FDE Grading Rubric Standard + 20 GCS Bucket L200 Concepts + 15 Extended L300 Concepts + 22 Comprehensive L400 Concepts) · **875 Mermaid Diagrams** · **1533 GFM Tables** · **5 Retained Figures** · **100% FDE Grading Rubric Enforcement**

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

## Freshness, Provenance & Structural Inventory (180-Day TTL Preserved)

| # | Concept | Tier | Mermaid | Tables | Figures | Status | Stale After |
|---:|---|---|---:|---:|---:|---|---|
| 00 | [Architecture Best Practice: Google Cloud FDE Field-Readiness & Proje](/concepts/00-fde-field-readiness-and-grading-rubric.md) | Rubric | 1 | 10 | 0 | draft | 2027-03-29 |
| 01 | [Architecture Best Practice: AI Agent Quality — Evaluation, Observabi](/concepts/01-ai-agent-quality-engineering.md) | L200 (Bucket) | 0 | 0 | 0 | draft | 2027-03-29 |
| 02 | [Architecture Best Practice: Vibe Coding Agent Security & Evaluation ](/concepts/02-vibe-coding-agent-security-evaluation-kb.md) | L200 (Bucket) | 0 | 8 | 0 | draft | 2027-03-29 |
| 03 | [Architecture Best Practice: The Open AI Agent Protocol Stack on Goog](/concepts/03-enterprise-ai-agent-protocol-stack.md) | L200 (Bucket) | 7 | 0 | 0 | draft | 2027-03-29 |
| 04 | [Architecture Best Practice: Deploying to Agent Runtime — Prerequisit](/concepts/04-deploying-gemini-enterprise-agent-runtime.md) | L200 (Bucket) | 2 | 10 | 0 | draft | 2027-03-29 |
| 05 | [Architecture Best Practice: Enterprise AI Agent Systems on Google Cl](/concepts/05-enterprise-ai-agent-systems-google-cloud.md) | L200 (Bucket) | 0 | 0 | 0 | draft | 2027-03-29 |
| 06 | [Architecture Best Practice: Agent Tools, MCP Interoperability & Mult](/concepts/06-agent-tools-mcp-multi-agent-orchestration.md) | L200 (Bucket) | 0 | 2 | 0 | draft | 2027-03-29 |
| 07 | [Architecture Best Practice: Enterprise Agent Skills — Progressive Di](/concepts/07-enterprise-agent-skills.md) | L200 (Bucket) | 0 | 10 | 0 | draft | 2027-03-29 |
| 08 | [Architecture Best Practice: Context Engineering for Stateful AI Agen](/concepts/08-context-engineering-stateful-agents.md) | L200 (Bucket) | 0 | 0 | 0 | draft | 2027-03-29 |
| 09 | [Architecture Best Practice: Platform-Native State Management with Ge](/concepts/09-platform-native-state-management.md) | L200 (Bucket) | 0 | 0 | 0 | draft | 2027-03-29 |
| 10 | [Vibe Coding Agent Security and Evaluation](/concepts/10-vibe-coding-agent-security-and-evaluation.md) | L200 (Bucket) | 2 | 2 | 0 | draft | 2027-03-24 |
| 11 | [Prototype to Production](/concepts/11-prototype-to-production.md) | L200 (Bucket) | 5 | 1 | 0 | draft | 2027-03-27 |
| 12 | [Agent Quality](/concepts/12-agent-quality.md) | L200 (Bucket) | 4 | 3 | 0 | draft | 2027-03-24 |
| 13 | [Spec-Driven Production Grade Development in the Age of Vibe Coding](/concepts/13-spec-driven-production-grade-development.md) | L200 (Bucket) | 1 | 1 | 0 | draft | 2027-03-27 |
| 14 | [Agent Skills](/concepts/14-agent-skills.md) | L200 (Bucket) | 9 | 6 | 2 | draft | 2027-03-21 |
| 15 | [Introduction to Agents](/concepts/15-introduction-to-agents.md) | L200 (Bucket) | 10 | 2 | 1 | draft | 2027-03-03 |
| 16 | [The New SDLC With Vibe Coding: From ad-hoc prompting to Agentic Engi](/concepts/16-the-new-sdlc-with-vibe-coding.md) | L200 (Bucket) | 8 | 2 | 1 | draft | 2027-03-03 |
| 17 | [Agents Concepts Visually Explained](/concepts/17-agents-concepts-visually-explained.md) | L200 (Bucket) | 5 | 7 | 0 | draft | 2027-03-08 |
| 18 | [Agent Tools & Interoperability with MCP](/concepts/18-agent-tools-interoperability-with-mcp.md) | L200 (Bucket) | 3 | 2 | 0 | draft | 2027-03-13 |
| 19 | [Agent Tools & Interoperability](/concepts/19-agent-tools-interoperability-2.md) | L200 (Bucket) | 11 | 3 | 0 | draft | 2027-03-14 |
| 20 | [Context Engineering — Sessions, Memory](/concepts/20-context-engineering-sessions-memory.md) | L200 (Bucket) | 6 | 2 | 0 | draft | 2027-03-19 |
| 21 | [Architecture Best Practice: Build and Deploy Multi-Agent ADK Systems](/concepts/21-build-and-deploy-multi-agent-adk-systems.md) | L300 (Extended) | 12 | 12 | 0 | draft | 2027-03-29 |
| 22 | [Architecture Best Practice: Build Enterprise Agents with Code Execut](/concepts/22-build-enterprise-agents-with-code-execution.md) | L300 (Extended) | 5 | 6 | 0 | draft | 2027-03-29 |
| 23 | [Architecture Best Practice: Agent Context Persistence, Sessions, and](/concepts/23-agent-context-persistence-and-memories.md) | L300 (Extended) | 8 | 8 | 0 | draft | 2027-03-29 |
| 24 | [Architecture Best Practice: Stateful Agents with Persistent Memories](/concepts/24-agent-with-persistent-memories-deep-dive.md) | L300 (Extended) | 21 | 78 | 0 | draft | 2027-03-29 |
| 25 | [Architecture Best Practice: Evaluating Generative and Agentic System](/concepts/25-evaluate-generative-agentic-systems.md) | L300 (Extended) | 58 | 133 | 0 | draft | 2027-03-29 |
| 26 | [Architecture Best Practice: Hill Climbing and Continuous Quality Opt](/concepts/26-hill-climbing-agentic-systems.md) | L300 (Extended) | 144 | 116 | 0 | draft | 2027-03-29 |
| 27 | [Architecture Best Practice: Model Lifecycle Migration and Upgrading ](/concepts/27-upgrade-to-the-latest-models.md) | L300 (Extended) | 34 | 31 | 0 | draft | 2027-03-29 |
| 28 | [Architecture Best Practice: Cost Estimation, FinOps, and Token Optim](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md) | L300 (Extended) | 43 | 91 | 0 | draft | 2027-03-29 |
| 29 | [Architecture Best Practice: Preparing and Deploying the Gemini Enter](/concepts/29-deploy-the-gemini-enterprise-app.md) | L300 (Extended) | 36 | 93 | 0 | draft | 2027-03-29 |
| 30 | [Architecture Best Practice: Third-Party Identity Provider Integratio](/concepts/30-third-party-idp-with-workforce-identity-federation.md) | L300 (Extended) | 56 | 112 | 0 | draft | 2027-03-29 |
| 31 | [Architecture Best Practice: Organizational Change Management for Gem](/concepts/31-plan-change-management-for-gemini-enterprise-deployments.md) | L300 (Extended) | 54 | 105 | 0 | draft | 2027-03-29 |
| 32 | [Architecture Best Practice: Lifecycle Change Management and Rollout ](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md) | L300 (Extended) | 54 | 105 | 0 | draft | 2027-03-29 |
| 33 | [Architecture Best Practice: Securing AI and Agentic Deployments with](/concepts/33-model-armor-securing-ai-deployments.md) | L300 (Extended) | 54 | 105 | 0 | draft | 2027-03-29 |
| 34 | [Architecture Best Practice: Securing Enterprise Agents with Gemini E](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md) | L300 (Extended) | 53 | 45 | 0 | draft | 2027-03-29 |
| 35 | [Architecture Best Practice: Governing the Agent Ecosystem with Agent](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md) | L300 (Extended) | 57 | 179 | 0 | draft | 2027-03-29 |

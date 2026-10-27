---
type: "Architecture Best Practice"
title: "Architecture Best Practice: Enterprise AI Agent Systems on Google Cloud"
description: "Architecture best-practice knowledge base entry converted from the source Google Doc “Architecture Best Practice: Enterprise AI Agent Systems on Google Cloud”."
timestamp: "2026-09-30T00:35:09Z"
status: "draft"
stale_after: "2027-03-29T00:35:09+00:00"
sources:
  - "https://docs.google.com/document/d/1vk61bHa0T-RvYs4ZCvJSILNM0XxIfH_wAiKAURt9KaE/edit"
generated:
  by: "gemini-enterprise:gdoc-to-markdown"
  at: "2026-09-30T12:47:46-07:00"
  method: "gdoc-to-markdown skill; diagrams reconstructed as Mermaid from page images"
verified:
  - by: "machine:structural-qa"
    at: "2026-09-30T12:47:46-07:00"
    scope: "markdown structure, fenced-block balance, Mermaid syntax, table shape, link and placeholder integrity"
  - by: "machine:crc32c-manifest"
    at: "2026-09-30T12:47:46-07:00"
    scope: "content hash recorded in MANIFEST.json"
tags:
  - enterprise-agents
  - google-cloud
  - agent-architecture
  - multi-agent-orchestration
  - agent-security
  - observability-and-evals
  - adk
  - cost-optimization
  - fde-grading-rubric
corpus: "GEAPL200"
version_tag: "GEAPL200_2026-09-30_124746"
document_id: "05-enterprise-ai-agent-systems-google-cloud"
source_doc_id: "1vk61bHa0T-RvYs4ZCvJSILNM0XxIfH_wAiKAURt9KaE"
content_sha256: "460f1d02fe5989c12bf2e35472edf909201e236071442f2839dae69166475339"
---

# Architecture Best Practice: Enterprise AI Agent Systems on Google Cloud

**Topics:** #enterprise-agents #google-cloud #agent-architecture #multi-agent-orchestration #agent-security #observability-and-evals #adk #cost-optimization

> **Source:** [Architecture Best Practice: Enterprise AI Agent Systems on Google Cloud](https://docs.google.com/document/d/1vk61bHa0T-RvYs4ZCvJSILNM0XxIfH_wAiKAURt9KaE/edit) · Converted from Google Docs

---


## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

> **Mandatory Governance Standard:** Every project, prototype, or production agent built using the patterns in this concept **must pass the [Google Cloud FDE Field-Readiness & Project Grading Rubric](/concepts/00-fde-field-readiness-and-grading-rubric.md)** (aligned with the [Cloud FDE Team Charter](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head)). Scoring Requirement: **Average >= `2.0 (Competent)`** across both **Part A (Presentation & Advisory Rigor)** and **Part B (Engineering & Implementation Excellence)**, with **zero `0 (Not Demonstrated)` scores** on any single metric.

### 1. Part A — Presentation & Advisory Rigor Enforcement for This Concept

- **A.1 Strategic Delivery & Value Articulation:** Connect Google Cloud's six-layer enterprise agent architecture directly to commercial reliability, security, and TCO outcomes, avoiding fragile 'science project' prototypes.
- **A.2 Objection Handling & Technical Defense:** Defend architectural safeguards against the top enterprise failure modes (hallucinated actions, duplicate financial trades, 35-tool context overload, and prompt injection).

### 2. Part B — Engineering & Implementation Excellence Cutlines for This Concept

- **B.1.1 Agentic & Multi-Agent Systems:** Decompose monolithic 35-tool agents into specialized sub-agents with isolated toolsets and deterministic orchestration (`SequentialAgent`, `ParallelAgent`, `LoopAgent`).
- **B.4.1 Availability Design & B.4.4 Graceful Degradation:** Enforce deterministic idempotency keys on mutating tools (preventing duplicate $50K trades) and graceful fallback when external telemetry APIs fail.
- **B.5.3 AI Cost Management:** Combine tiered Gemini Flash/Pro routing, context compaction, and semantic caching to sustain 10M+ queries/month economically.

### 3. Prevailing Customer Best-Practice Exemplars to Cite in Panel Reviews

- **Grounded Enterprise Scenarios:** Retail Order-Status Assistant (fixing turn-15 context crashes), Portfolio Rebalancing Agent (idempotency keys preventing duplicate $50K trades), Clinical Trial Reporting Platform (decomposing 35 tools into sub-agents), and Fleet Dispatch Agent (weather-aware fallback routing).
- **Cross-Reference:** See [Concept 00 — FDE Field-Readiness & Project Grading Rubric](/concepts/00-fde-field-readiness-and-grading-rubric.md) for the complete 0–3 grading scale, 31-competency matrix, and disqualifier remediation rules.

---
## Architectural Best Practice: Key Guidelines & Takeaways

### Core Principles

- **Agent development is systems orchestration, not prompt engineering.** Build on four separable pillars — Model (brain), Tools (hands), Orchestration Layer (nervous system), Deployment & Services (body).
- **Four-pillar anatomy is non-negotiable.** Every production agent separates Model, Tools, Orchestration, and Deployment; each pillar has a distinct failure mode when absent.
- **Agentic execution is a loop, not a completion.** Get the Mission → Scan the Scene → Think It Through → Take Action → Observe & Iterate, with step 5 feeding back into steps 2–3.
- **Autonomy is a spectrum that must be chosen deliberately.** Levels 0 (static inference) through 4 (self-evolving) are a sizing tool that prevents both under- and over-engineering.
- **Model tiering is an architectural concern, not an optimization afterthought.** Cost and latency are dominated by the high-volume simple path, not the rare complex one.
- **Security boundaries live in deterministic code.** A jailbroken model will ignore its own system instruction; only code outside the model holds.
- **Observability targets the trajectory, not the endpoints.** Stochastic failures have no stack trace; without intermediate spans the system is an unauditable black box.
- **Agents are evolving systems, not shipped-and-done artifacts.** Enterprise APIs and environments drift; a frozen agent degrades.

### Mandatory Requirements / Golden Rules

1. Match the **autonomy level (0–4)** to the actual problem; do not under- or over-engineer.
2. Run a **heterogeneous model mesh** (Flash for triage/high-volume, Pro for planning) rather than one flagship model for every call.
3. Constrain multi-agent behavior with **named topologies** (Coordinator, Sequential, Generator-Critic, HITL) instead of free-form agent chatter.
4. Enforce security with **deterministic code, never prompt text** — the "Principle of the Leash."
5. Make the reasoning trajectory **observable by default** (OpenTelemetry spans → BigQuery → LM-as-a-Judge → CI/CD gate).
6. Make every state-mutating tool **idempotent** — keys minted at plan time, required for any financial, ERP, or inventory write.
7. **Externalize session state** (e.g., Cloud Spanner); never accumulate conversation state by string concatenation in the frontend.
8. Bind tools through **standardized protocols (OpenAPI 3.0 / MCP)** for tool discovery, typed arguments, and access control.
9. Give the reasoning loop an explicit `TERMINATE` condition and an attempt/iteration cap; feed errors, not just successes, back into context.
10. Put a **human-in-the-loop approval gate** in front of high-consequence, irreversible mutations (wire transfers, prescriptions, real-world state changes), paired with deterministic database validation.
11. **Ground answers on live data with a tool call** — the system instruction must mandate inspection before answering, with reasoning temperature kept low (~0.1).
12. Promote agent changes only through the **evaluator/judge gate**, with optimization runs isolated in a sandbox.

### Anti-Patterns / Guardrails

- **String-concatenated conversation state in the frontend** — overflows context and crashes (the retailer failed at ~15 turns). Externalize sessions.
- **Ungrounded answers on live data** — never let the model guess inventory, shipping dates, or stock numbers; force a tool call.
- **Read-only agents in write-required workflows** — an agent that cannot mutate the ERP will silently fail to record cancellations.
- **Blind retry / "fire-and-forget"** on mutating endpoints — retry logic without idempotency is unsafe by construction.
- **Over-binding tools to one prompt** instead of decomposing into specialists (the 35-tool clinical prompt).
- **Under-engineering:** expecting a single L1 prompt to coordinate enterprise-wide work.
- **Over-engineering:** building a multi-agent graph for a simple lookup.
- **Trusting the model to withhold sensitive fields** rather than stripping them in code.
- **Expressing a security boundary only as prompt text** — every deterministic rejection should also alarm.
- **Logging only input and final response** — the diagnosis lives in the intermediate arguments.
- **Free-form multi-agent communication** — causes infinite loops and non-deterministic divergence; use named topologies with per-hop validation and hard iteration caps.
- **Shipping an agent as finished** — environmental and API drift degrades static agents.
- **Unsandboxed L4 autonomy** — self-modifying tools are a large attack surface; require isolated sandboxes, self-critique, and controlled tool-registry mutation.

---

**Knowledge Base Entry** | Source: *Enterprise AI Agents Masterclass & Architecture Guide* (session transcript, 9 modules + 2 addenda) **Underlying reference:** *Introduction to Agents* — Blount, Gulli, Saboo, Zimmermann, Vuskovic **Evaluation lens:** GCP Well-Architected Framework — Security, Reliability, Cost Optimization, Operational Excellence, Performance Efficiency

---

## 1. Executive Summary

**Context.** The discussion covers the full lifecycle of building autonomous AI agents for enterprise workloads: what an agent is structurally, how its execution loop behaves, how much autonomy to grant it, which models and protocols to wire in, how to orchestrate several agents safely, how to observe and evaluate a stochastic system, how agents talk to humans/other agents/payment rails, how to contain them, and how they improve over time. Every module was pressure-tested against a realistic failure scenario (hallucinated shipping dates, a duplicated $50K trade, a 35-tool clinical prompt, 14.8s FAQ latency, a hurricane-routed truck fleet, a prompt-injected HR salary dump).

**Core Recommendation.** Treat agent development as **systems orchestration, not prompt engineering**. Build on four separable pillars — Model (brain), Tools (hands), Orchestration Layer (nervous system), Deployment & Services (body) — then:

1. Match the **autonomy level (0–4)** to the actual problem; do not under- or over-engineer.
2. Run a **heterogeneous model mesh** (Flash for triage/high-volume, Pro for planning) rather than one flagship model for every call.
3. Constrain multi-agent behavior with **named topologies** (Coordinator, Sequential, Generator-Critic, HITL) instead of free-form agent chatter.
4. Enforce security with **deterministic code, never prompt text** — the "Principle of the Leash."
5. Make the reasoning trajectory **observable by default** (OpenTelemetry spans → BigQuery → LM-as-a-Judge → CI/CD gate).
6. Make every state-mutating tool **idempotent**.

---

## 2. Core Architectural Principles & Decisions

### Decision 1 — Four-pillar anatomy is non-negotiable

Every production agent separates Model, Tools, Orchestration, and Deployment. *Rationale:* each pillar has a distinct failure mode when absent, and the transcript's retailer scenario failed on three of them simultaneously (hallucination = no tool grounding; unrecorded ERP cancellations = no write tools; crash at turn 15 = no orchestration/state layer).

### Decision 2 — Agentic execution is a loop, not a completion

The canonical cycle is **Get the Mission → Scan the Scene → Think It Through → Take Action → Observe & Iterate**, with Step 5 feeding observations back into Steps 2–3. *Rationale:* empirical correction against real environment feedback is what distinguishes an agent from a one-shot generator.

### Decision 3 — Autonomy is a spectrum that must be chosen deliberately

Levels 0 (static inference) through 4 (self-evolving) are a sizing tool. *Rationale:* categorizing prevents both under-engineering (expecting one prompt to coordinate an enterprise) and over-engineering (an agent graph for a lookup).

### Decision 4 — Model tiering is an architectural concern, not an optimization afterthought

Classification and intake run on fast/cheap models; decomposition and replanning run on frontier models. *Rationale:* cost and latency are dominated by the high-volume simple path, not the rare complex one.

### Decision 5 — Tools are bound through standardized protocols (OpenAPI 3.0 / MCP)

*Rationale:* uniform JSON schemas give tool discovery, typed arguments, and access control without bespoke per-tool SDKs.

### Decision 6 — Security boundaries live in deterministic code

Model Armor at the input edge, `before_tool_callback` at the execution edge, an Agent Gateway as control plane. *Rationale:* a jailbroken model will ignore its own system instruction; only code outside the model holds.

### Decision 7 — Reliability requires distributed state and idempotency keys

Session state is externalized (e.g., Cloud Spanner) and mutating tool calls carry an idempotency token minted at plan time. *Rationale:* at-least-once delivery over unreliable networks is the norm; the $50K→$100K duplicate-trade scenario is the canonical failure.

### Decision 8 — Observability targets the trajectory, not the endpoints

Log thoughts, tool names, serialized arguments, and raw observations — not just input and final answer. *Rationale:* stochastic failures have no stack trace; without intermediate spans the system is an unauditable black box.

### Decision 9 — Agents must be treated as evolving, not shipped-and-done

Two loops: in-line (runtime telemetry and user corrections refine instructions) and offline (Agent Gym simulation against synthetic/adversarial scenarios before deploy). *Rationale:* enterprise APIs and environments drift; a frozen agent degrades.

---

## 3. Best Practice Guidelines & Recommended Patterns

### Pattern: Four-Pillar Agent Anatomy

- **Description:** Model = reasoning/decomposition; Tools = grounded reads and state-mutating writes; Orchestration = state, context curation, reasoning loop, memory scratchpad; Deployment = runtime, sessions, IAM delegation, autoscaling, telemetry.
- **Implementation Guidance:** Vertex AI Gemini 2.5 Pro/Flash for the model; Cloud Run microservices, BigQuery NL2SQL and MCP servers for tools; Google GenAI ADK / Vertex Agent Engine for orchestration; Cloud Run or GKE with Cloud Spanner sessions and Cloud Trace for deployment. Ground the system instruction explicitly ("always inspect inventory before answering; never guess numbers") and keep reasoning temperature low (~0.1).
- **Guardrails:** Missing any pillar produces a named failure: ambiguity collapse (no model), hallucination (no tools), infinite loops and single-turn dead ends (no orchestration), no scale/audit (no deployment layer).

### Pattern: The 5-Step Agentic Loop with Externalized State

- **Description:** Mission ingest → environment scan → plan → dispatch typed tool call → append observation → re-evaluate termination.
- **Implementation Guidance:** Trigger via Pub/Sub, Eventarc or API Gateway; hydrate short-term and long-term memory from Cloud Spanner and Vertex Vector Search; dispatch to Cloud Run / Cloud Functions with secrets from Secret Manager; append `tool_response` to the trajectory and persist spans to a BigQuery trajectory store.
- **Guardrails:** The loop needs an explicit `TERMINATE` condition and an attempt/iteration cap. Errors, not just successes, must be fed back into context.

### Pattern: Autonomy Level Sizing (L0–L4)

- **Description:** L0 static inference · L1 single-hop grounding/RAG · L2 multi-hop planning with a stateful scratchpad · L3 collaborative multi-agent with agents-as-tools · L4 self-evolving with dynamic tool registry.
- **Implementation Guidance:** Map the candidate workload to a level before design. HR policy Q&A → L1 (Vertex AI Search grounding). IT support touching AD + ServiceNow → L2. Loan underwriting → L3. Cyber defense that authors and deploys its own parser → L4 with sandboxing and self-critique.
- **Guardrails:** L4 requires isolated sandboxes, reflection/self-critique, and controlled tool-registry mutation. Do not reach for L3/L4 where L1 answers the question.

### Pattern: Heterogeneous Model Mesh / Tiered Routing

- **Description:** A cheap model classifies intent with a constrained JSON schema, resolves simple traffic directly, and escalates only complex work to the frontier model with tools attached.
- **Implementation Guidance:** Phase A — Gemini 2.5 Flash at temperature 0.0 with `response_mime_type="application/json"` and a Pydantic `response_schema` enum (`GENERAL_FAQ` vs `COMPLEX_ENGINEERING_OPERATION`). Phase B — route: FAQ answered by Flash; complex work handed to Gemini 2.5 Pro with the tool set bound.
- **Guardrails:** The router must emit structured, validated output (schema-parsed, not free text). Keep the escalation path always available so misclassification degrades gracefully rather than failing.

### Pattern: Coordinator (Hub-and-Spoke)

- **Description:** A central manager agent directs specialized workers and validates their results before assembling the response.
- **Implementation Guidance:** Give the coordinator the specialists as callable tools, a low temperature, and an explicit aggregation instruction. Each specialist owns a narrow schema and a narrow permission set.
- **Guardrails:** Best where the task decomposition cannot be predicted in advance. Manager-side validation of worker output is the failure-prevention mechanism.

### Pattern: Sequential Pipeline

- **Description:** Agent A → Agent B → Agent C for linear workflows (ingest → extract → load).
- **Guardrails:** Each stage acts as a schema validator for its upstream input, so bad data stops at the boundary rather than propagating.

### Pattern: Iterative Refinement (Generator–Critic)

- **Description:** A generator drafts, a critic scores against a rubric, feedback is appended to the draft, repeat until threshold or attempt cap.
- **Implementation Guidance:** Generator on Flash; critic on Pro at temperature 0.0 emitting a structured verdict (`passed_safety_audit: bool`, `quality_score: int`, `required_revisions: str`). Accept only on `passed_safety_audit and quality_score >= 8`.
- **Guardrails:** Hard-cap the loop (e.g., 3 attempts) and raise on exhaustion — never return an unvalidated draft. Suited to code generation, legal drafting, and financial modeling.

### Pattern: Human-in-the-Loop Approval Gate

- **Description:** A deterministic gate pauses execution before high-consequence mutations and resumes only on explicit human approval.
- **Implementation Guidance:** Classify risk after the reasoning step; low-risk mutations execute automatically, high-risk ones suspend into an approval queue with approve/deny branches (execute vs. cancel).
- **Guardrails:** Applies to wire transfers, prescriptions, and any irreversible real-world state change. Pair with deterministic database validation so approval is informed, not rubber-stamped.

### Pattern: Idempotent Mutation with Plan-Time Keys

- **Description:** Generate an idempotency key during planning (Step 3), pass it to the mutating tool (Step 4); the downstream API returns the cached confirmation on replay instead of re-executing.
- **Guardrails:** Required for any financial, ERP, or inventory write. Retry logic without idempotency is unsafe by construction.

### Pattern: OpenTelemetry Trajectory Tracing + LM-as-a-Judge

- **Description:** Every turn emits a structured span (session id, mission id, timestamp, step, internal thought, tool, args, observation) to central storage; traces plus thumbs-down feedback build a golden dataset that an LM judge scores, gating CI/CD promotion.
- **Implementation Guidance:** Stream spans to BigQuery; join user feedback into the golden evaluation set; run judge evaluation as a deployment gate.
- **Guardrails:** Logging only input and final response is insufficient — the diagnosis lives in the intermediate arguments.

### Pattern: A2A Agent Card Interoperability

- **Description:** Publish a versioned JSON card declaring agent name, organization, endpoint, auth type (OIDC JWT), and typed capabilities so external agents can discover and call it.
- **Guardrails:** Mutual OIDC tokens for cross-organization trust; capabilities declare required parameters and types explicitly.

### Pattern: AP2 Capped Commerce Mandate

- **Description:** Cryptographically signed purchase mandates authorize settlement up to a hard ceiling without sharing master banking credentials.
- **Guardrails:** The cap is the blast-radius control (e.g., $25,000). Settlement rides a settlement/x402 rail, separate from the negotiation channel.

### Pattern: Defense-in-Depth — "The Principle of the Leash"

- **Description:** Five layers: Agent Gateway control plane → Model Armor content firewall (drop and alarm on malicious input) → core reasoning → `before_tool_callback` policy check → isolated tool execution.
- **Implementation Guidance:** The pre-execution callback runs deterministic checks against tool name, arguments, and user context — hard value limits (e.g., transfers > $5,000 rejected) and role checks (e.g., `FINANCE_OPERATOR` required) — raising a `SecurityViolation` before dispatch. Strip unauthorized fields from query results rather than trusting the model to withhold them.
- **Guardrails:** Never express a security boundary only as prompt text. Every deterministic rejection should also alarm.

### Pattern: Dual-Loop Evolution (In-Line + Agent Gym)

- **Description:** Production traces and corrections feed a prompt/context optimizer; in parallel, an offline gym simulates adversarial scenarios, judges responses, and emits an improved system instruction that is promoted only after evaluation.
- **Implementation Guidance:** Synthesize adversarial cases (e.g., a return request with conflicting dates) on a fast model, run the candidate instruction against them, then have a frontier model analyze instruction + scenario + response and rewrite the instruction.
- **Guardrails:** Optimization runs in an isolated sandbox; promotion passes through the evaluator/judge gate, never straight to production.

---

## 4. Trade-Off Analysis & Pitfalls

| Option / Decision | Advantages | Trade-Offs / Risks | Mitigations |
| :---- | :---- | :---- | :---- |
| Single flagship model for all traffic | Simple; one code path; maximum quality everywhere | Highest token cost; 14.8s latencies on trivial FAQs; 78% of volume overpays | Flash router in front; escalate only the ~22% complex tail; 60–80% token reduction, sub-1.5s simple responses |
| Frontier model (Pro) for planning | Deep decomposition, dynamic replanning | Higher latency and cost per call | Reserve for multi-step planning and critic roles only |
| Fast worker model (Flash / Gemma) | Sub-second, lowest unit cost | Weaker on complex multi-step reasoning | Constrain to classification, validation, summarization, draft generation |
| Monolithic prompt with 35 tools + hundreds of pages of rules | One deployable; nothing to coordinate | Tool confusion, high latency, no least-privilege boundary | Refactor into L3 coordinator + narrow specialists (ingestion, SQL/biostatistics, drafting) |
| Fire-and-forget retries on mutating APIs | Trivially simple | Duplicate execution — a $50K sale became $100K on a dropped HTTP 200 | Idempotency keys minted at plan time; server returns cached confirmation on replay |
| Fully autonomous high-consequence mutations | Fastest throughput; no human bottleneck | Irreversible wrong action; prompt injection reaches the real world | HITL gate on high-risk branch only; auto-execute the low-risk branch to preserve throughput |
| Prompt-based safety instructions | Zero infrastructure | Bypassed by jailbreak/injection; unenforceable | Model Armor + `before_tool_callback` + gateway; deterministic limits and role checks |
| Log only input and final response | Cheap, low volume | Black-box failures are undiagnosable (hurricane truck routing) | Full OTel trajectory spans to BigQuery; judge-scored golden datasets |
| Free-form multi-agent communication | Maximum flexibility | Infinite loops, non-deterministic divergence | Adopt named topologies with validation at each hop and hard iteration caps |
| L4 self-evolving autonomy | Continuous discovery without human exposure to hazard | Self-modifying tools are a large attack surface | Sandboxed execution, self-critique, controlled tool-registry updates, judge gate before deploy |

**Antipatterns to Avoid**

- **String-concatenated conversation state in the frontend** — overflows context and crashes (the retailer failed at ~15 turns). Externalize sessions.
- **Ungrounded answers on live data** — never let the model guess inventory, shipping dates, or stock numbers; force a tool call.
- **Read-only agents in write-required workflows** — an agent that cannot mutate the ERP will silently fail to record cancellations.
- **Blind retry / "fire-and-forget"** on mutating endpoints (explicitly evaluated and rejected in the transcript).
- **Over-binding tools to one prompt** instead of decomposing into specialists.
- **Under-engineering:** expecting a single L1 prompt to coordinate enterprise-wide work.
- **Over-engineering:** building a multi-agent graph for a simple lookup.
- **Trusting the model to withhold sensitive fields** rather than stripping them in code.
- **Shipping an agent as finished** — environmental and API drift degrades static agents.

---

## 5. Real-World / Customer Scenarios

**Scenario 1: Retail Order-Status Assistant (hallucination, lost mutations, turn-15 crash)**

- *Context & Constraints:* Live shipping data, ERP cancellation writes, long multi-turn conversations.
- *Applied Architecture:* Orchestration layer with stateful sessions in Cloud Spanner; enterprise tools bound via OpenAPI/MCP endpoints on Cloud Run; the model configured as a multi-step reasoning engine.
- *Outcomes:* Context overflow eliminated by session management, hallucinations eliminated by tool grounding, ERP mutations recorded via API tools.

**Scenario 2: Portfolio Rebalancing Agent (duplicate $50K trade)**

- *Context & Constraints:* Financial mutation over an unreliable network; the trade succeeded but the HTTP 200 was dropped, and the retry doubled the position to $100K.
- *Applied Architecture:* Distributed state management with an idempotency key generated in the planning step and passed to the trading tool; the API recognizes the token on retry and returns the cached confirmation.
- *Outcomes:* Exactly-once financial effect under at-least-once delivery. (Noted in-session: the "blind fire-and-forget" option was initially considered and corrected.)

**Scenario 3: Clinical Trial Reporting Platform (35 tools in one prompt)**

- *Context & Constraints:* Hundreds of pages of FDA regulatory text plus 35 bound tools on a single L1 prompt; high latency and tool-selection confusion.
- *Applied Architecture:* Refactor to an L3 collaborative multi-agent system — a coordinator delegating to Document Ingestion, Biostatistics SQL, and Regulatory Drafting specialists.
- *Outcomes:* Separation of concerns and least privilege per specialist; reduced tool confusion and latency.

**Scenario 4: High-Volume Customer Support (10M queries/month)**

- *Context & Constraints:* 78% simple FAQs, all routed to Gemini 2.5 Pro; 14.8s average latency and runaway cost.
- *Applied Architecture:* Gemini 2.5 Flash as an upfront router resolving FAQs inline, escalating only the 22% complex tail to Pro with tools.
- *Outcomes:* 60–80% token-spend reduction; simple-query response times below 1.5 seconds.

**Scenario 5: Prescription Refill Agent (ambiguity + patient prompt injection)**

- *Context & Constraints:* Ambiguous doctor emails and untrusted patient-supplied text feeding an EHR-mutating agent.
- *Applied Architecture:* HITL approval gate on every EHR mutation, paired with deterministic database validation; low-risk dosages auto-execute, high-risk pause for prescriber approval.
- *Outcomes:* Prompt injections cannot trigger irreversible dispatches; blast radius limited to a queued request.

**Scenario 6: Fleet Dispatch Agent (trucks routed into a hurricane)**

- *Context & Constraints:* Only user input and final response were logged; the faulty reasoning step was invisible.
- *Applied Architecture:* Distributed OpenTelemetry tracing across the orchestration layer recording thoughts, tool names, serialized arguments, and raw observations, streamed to BigQuery.
- *Outcomes:* Black-box failure mode resolved; trajectories become replayable evidence and evaluation data.

**Scenario 7: Enterprise Procurement Agent (multi-party purchasing up to $25K)**

- *Context & Constraints:* Must transact with third-party supplier agents without sharing master banking credentials.
- *Applied Architecture:* Published Agent Card for discovery, mutual OIDC tokens for A2A trust, AP2 cryptographically signed mandates capped at $25,000, settlement on a separate rail.
- *Outcomes:* Machine-to-machine trust established; financial exposure hard-capped.

**Scenario 8: HR Agent Salary/SSN Exfiltration Attempt**

- *Context & Constraints:* An employee used prompt injection to coax the CEO's salary and SSN out of a database-backed HR agent.
- *Applied Architecture:* Model Armor blocking injection at the input edge plus a deterministic `before_tool_callback` stripping unauthorized fields before the query executes.
- *Outcomes:* Compliance no longer depends on the model's natural-language cooperation.

**Scenario 9: Clean-Energy Materials Discovery Lab**

- *Context & Constraints:* Needs to generate novel chemical structures, simulate, evaluate failures and evolve algorithms without human exposure to hazardous materials.
- *Applied Architecture:* Offline Agent Gym / simulation mesh pairing a generative agent (Co-Scientist style hypothesis generation) with automated evaluation sandboxes (AlphaEvolve-style evolutionary optimization) in a closed-loop self-refinement cycle.
- *Outcomes:* Continuous autonomous discovery inside a contained sandbox.

**Scenario 10: Logistics Inventory Coordinator (reference implementation)**

- *Context & Constraints:* Regional warehouse stock lookups by SKU where guessing is unacceptable.
- *Applied Architecture:* A typed inventory tool bound to a low-temperature Gemini agent whose system instruction mandates a tool call before any stock answer.
- *Outcomes:* Canonical demonstration of Model + Tools + Orchestration working together; zero invented stock figures.

---

## 6. Topic Modeling & Taxonomic Tags

**Domain Taxonomy** `ai-agents` · `cloud-infrastructure` · `distributed-systems` · `security-and-compliance` · `mlops-and-observability` · `enterprise-integration` · `cost-optimization` · `data-engineering`

**Key Entity & Technology Tags** `gemini-2-5-pro` · `gemini-2-5-flash` · `gemma` · `vertex-ai` · `vertex-ai-search` · `vertex-vector-search` · `genai-adk` · `vertex-agent-engine` · `cloud-run` · `gke` · `cloud-functions` · `cloud-spanner` · `bigquery` · `nl2sql` · `pubsub` · `eventarc` · `api-gateway` · `secret-manager` · `cloud-trace` · `opentelemetry` · `model-armor` · `mcp` · `openapi-3-0` · `pydantic` · `oidc-jwt` · `a2a-protocol` · `a2ui` · `ap2` · `x402` · `agent-card` · `gemini-live-api` · `vpc-service-controls` · `co-scientist` · `alphaevolve` · `agent-gym` · `saif`

**Thematic & Pattern Tags** `agentic-loop` · `orchestration-layer` · `tool-grounding` · `context-engineering` · `session-state-management` · `idempotency` · `exactly-once-semantics` · `autonomy-levels` · `multi-agent-systems` · `coordinator-pattern` · `sequential-pipeline` · `generator-critic` · `iterative-refinement` · `human-in-the-loop` · `model-tiering` · `request-routing` · `latency-optimization` · `defense-in-depth` · `principle-of-least-privilege` · `prompt-injection-defense` · `deterministic-guardrails` · `before-tool-callback` · `agent-gateway` · `sandboxing` · `trajectory-tracing` · `lm-as-a-judge` · `golden-datasets` · `ci-cd-quality-gates` · `agent-interoperability` · `machine-to-machine-trust` · `capped-mandates` · `self-evolving-systems` · `adversarial-simulation` · `separation-of-concerns` · `blast-radius-containment`

---

## 7. Appendix: Reference Mappings from the Session

### A. Figure & Section Mapping (companion visual deck)

| Figure | Target Section | Caption | Source Page |
| :---- | :---- | :---- | :---- |
| Image 1 | The Agentic Problem-Solving Loop | Continuous 5-step loop: Get Mission, Scan Scene, Think, Act, Observe & Iterate | 11 |
| Image 2 | Core Agent Architecture: Model, Tools & Orchestration | Core anatomy linking Model (brain), Tools (hands), Orchestration (nervous system) | 19 |
| Image 3 | Multi-Agent Systems and Design Patterns | Iterative Refinement: the Generator–Critic feedback loop | 25 |
| Image 4 | Agent Deployment and Services | Gemini Enterprise Agent Platform: Agent Studio, Agent Runtime, Memory Bank | 26 |
| Image 5 | Agent Ops: A Structured Approach to the Unpredictable | Overlap of DevOps, MLOps and GenAIOps | 27 |
| Image 6 | Securing a Single Agent: The Trust Trade-Off | Multi-layered security and containment based on SAIF focus-on-agents | 39 |

### B. Governance Note (as discussed in session)

The session recorded a working assumption that connected workspace integrations hold read-only grounding permissions, so live Docs could not be mutated programmatically and export had to go through Canvas. That constraint is environment-specific rather than architectural — where a workspace connector is granted document write scopes, markdown can be imported into a native Doc directly. The underlying principle still applies: **write scopes on production documents should be granted deliberately under least privilege, not by default.**

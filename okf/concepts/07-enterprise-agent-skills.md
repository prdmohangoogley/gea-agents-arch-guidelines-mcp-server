---
type: "Architecture Best Practice"
title: "Architecture Best Practice: Enterprise Agent Skills — Progressive Disclosure, Capability Profiles & Skill Lifecycle Engineering"
description: "Architecture best-practice knowledge base entry converted from the source Google Doc “Architecture Best Practice: Enterprise Agent Skills — Progressive Disclosure, Capability Profiles & Skill Lifecycle Engineering”."
timestamp: "2026-09-30T01:55:27Z"
status: "draft"
stale_after: "2027-03-29T01:55:27+00:00"
sources:
  - "https://docs.google.com/document/d/1XS3V1hJ6zjbD7QUD5lnFveekj2SCjq2yLsNlnq3GSN4/edit"
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
  - agent-skills
  - progressive-disclosure
  - context-engineering
  - agent-evaluation
  - enterprise-agents
  - mcp
  - least-privilege
  - agentops
  - fde-grading-rubric
corpus: "GEAPL200"
version_tag: "GEAPL200_2026-09-30_124746"
document_id: "07-enterprise-agent-skills"
source_doc_id: "1XS3V1hJ6zjbD7QUD5lnFveekj2SCjq2yLsNlnq3GSN4"
content_sha256: "eedcd258be54ce92a72fd01fc5db9f33972e4273fda12bba8446a40c845fdced"
---

# Architecture Best Practice: Enterprise Agent Skills — Progressive Disclosure, Capability Profiles & Skill Lifecycle Engineering

**Topics:** #agent-skills #progressive-disclosure #context-engineering #agent-evaluation #enterprise-agents #mcp #least-privilege #agentops

> **Source:** [Architecture Best Practice: Enterprise Agent Skills — Progressive Disclosure, Capability Profiles & Skill Lifecycle Engineering](https://docs.google.com/document/d/1XS3V1hJ6zjbD7QUD5lnFveekj2SCjq2yLsNlnq3GSN4/edit) · Converted from Google Docs

---


## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

> **Mandatory Governance Standard:** Every project, prototype, or production agent built using the patterns in this concept **must pass the [Google Cloud FDE Field-Readiness & Project Grading Rubric](/concepts/00-fde-field-readiness-and-grading-rubric.md)** (aligned with the [Cloud FDE Team Charter](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head)). Scoring Requirement: **Average >= `2.0 (Competent)`** across both **Part A (Presentation & Advisory Rigor)** and **Part B (Engineering & Implementation Excellence)**, with **zero `0 (Not Demonstrated)` scores** on any single metric.

### 1. Part A — Presentation & Advisory Rigor Enforcement for This Concept

- **A.1 Strategic Delivery & Value Articulation:** Explain how packaging procedural domain expertise into modular `SKILL.md` bundles with Progressive Disclosure reduces prompt token costs by 60–80% while boosting task accuracy.
- **A.4 AI-Driven Development Discussion:** Show how recurring agent mistakes and 6-hour debugging breakthroughs are crystallized into reusable, versioned Skills in the Skills Registry.

### 2. Part B — Engineering & Implementation Excellence Cutlines for This Concept

- **B.1.5 Domain-Applied AI/ML Expertise:** Encode vertical-specific SOPs (e.g., Tier-1 Bank SAR investigations, retail contractor estimation) as portable `SKILL.md` + `references/` + `scripts/` packages.
- **B.5.3 AI Cost Management:** Enforce the 3-tier Progressive Disclosure protocol (Tier 1: ~100-token YAML metadata at startup → Tier 2: `<5,000`-token `SKILL.md` body on trigger → Tier 3: on-demand `references/` and `scripts/`).
- **B.7.1 Modularity & Abstraction & B.6.4 Testing:** Avoid the 4 SkillsBench failure modes (conflicting instructions, trigger collisions, over-scaffolding, and bloat) and gate skill releases on trajectory-aware evaluation.

### 3. Prevailing Customer Best-Practice Exemplars to Cite in Panel Reviews

- **Grounded Enterprise Scenarios:** National Home Improvement Retailer (project estimation via progressive disclosure), SaaS Technical Support (35 runbooks without context bloat), Tier-1 Bank SAR Investigation (Skills + MCP + Sub-agent triad), and Telecom B2B Billing (resolving skill trigger collisions).
- **Cross-Reference:** See [Concept 00 — FDE Field-Readiness & Project Grading Rubric](/concepts/00-fde-field-readiness-and-grading-rubric.md) for the complete 0–3 grading scale, 31-competency matrix, and disqualifier remediation rules.

---
## Architectural Best Practice: Key Guidelines & Takeaways

### Core Principles

- **Skills supply the missing procedural memory.** Semantic memory (pre-trained facts) and episodic memory (session history) are already present; the gap is organizational tradecraft — the disciplined, organization-specific knowledge of *how* a workflow is executed step by step.
- **Progressive disclosure is the central mechanism.** Level 1 (name + routing description in YAML frontmatter) is always resident at ~30–80 tokens per skill; Level 2 (the SKILL.md body) loads on semantic intent match at ~500–2,500 tokens; Level 3 (`references/`, `scripts/`, `assets/`) carries zero baseline cost and is read only on execution.
- **The architectural triad has directional responsibility.** `AGENTS.md` is the constitution (policy, always resident), MCP is hands and sockets (reach), and Skills are the SOP (know-how, loaded on match). AGENTS.md governs the skill; the skill instructs execution via MCP.
- **A generalist agent flexing into specialist roles beats a fleet of specialists.** One agent backed by a governed skills library removes orchestration overhead, cold-start latency, routing brittleness, and N deployment lifecycles.
- **Treat a skill as a governed software artifact with a lifecycle**, not a prompt fragment — version-controlled, evaluated, owned by a domain team, and released through a gate.
- **The context window is a budget with four partitions** — system & catalog, active session memory, dynamic skill context, and reserved output — each with a distinct growth behavior and a distinct failure mode.
- **Shift intelligence left.** Anything deterministic — math, parsing, schema validation, command syntax — belongs in `scripts/`, not in reasoning tokens.
- **Privilege is bound at the manifest layer, not left to model discretion**, through tiered Capability Profiles with HITL escalation for mutative actions.

### Mandatory Requirements / Golden Rules

1. Use **progressive disclosure** — metadata always resident, instructions loaded on intent match, references and scripts read only at execution.
2. Respect the **architectural triad**: `AGENTS.md` is policy, MCP is reach, Skills are know-how. **Never place a compliance guardrail in a skill** — a guardrail in a skill is optional by construction and fails silently.
3. Author top-down (**Path A**) from existing SOPs for regulated work, bottom-up (**Path B**) by crystallizing a proven agent trajectory for emergent work — match the path to the provenance of the knowledge.
4. Evaluate across **three gates** — trigger, trajectory, output — and always against an **adversarial distractor matrix**, never in isolation.
5. **Shift intelligence left**: deterministic logic belongs in `scripts/`, returning structured, compact results including a decision flag the workflow can branch on.
6. Practice **context hygiene**: evict completed skills at terminal state, condense history with sliding-window summarization, and pin governance immutably in system context.
7. Bind privilege at the **manifest layer** through Capability Profiles, with HITL escalation for mutative tiers. A Tier 1 skill can never directly invoke a Tier 3 tool.
8. Compose at scale as a **DAG with validation gates** — enforce acyclicity at load time and validate intermediate artifacts before any downstream mutative node fires.
9. **Never let a meta-skill auto-commit to main.** Route every change through a pull request and an evaluation gate; run meta-skills at Tier 2 (sandboxed), not Tier 3.
10. **Negative scoping is a first-class frontmatter concern** — descriptions must state when *not* to trigger, with sharp semantic boundaries against adjacent skills.
11. Build the **distractor matrix before writing skill #2** — trigger precision degrades fastest between skills 5 and 20.
12. Keep **database connectivity in MCP**, never in a skill's `scripts/`, so connection pooling, service-account security, and enterprise API gateways are preserved.

### Anti-Patterns / Guardrails

- **The monolithic system prompt** — 35–40 runbooks in one static block; the originating failure.
- **Compliance guardrails implemented as skills** — makes policy conditional on routing success.
- **Domain workflows written into AGENTS.md** — static bloat irrelevant to most turns.
- **Secrets or credentials in AGENTS.md** — exposed in every context window and to injection.
- **Database drivers inside skill scripts** — bypasses pooling, service-account security, and gateways.
- **Naive RAG chunking of procedures** — destroys sequencing, prerequisites, and conditional branches.
- **Fine-tuning as a substitute for procedure** — brittle, forgetful, unauditable, and blind to live systems.
- **Isolated-only skill evaluation** — the Evaluation Illusion; hides routing collisions entirely.
- **Generic trigger descriptions without negative scoping** — the direct cause of trigger theft.
- **Raising temperature to resolve routing ambiguity** — adds randomness to a determinism problem.
- **Retaining completed skills in context** — context debt; competes with governance for attention.
- **Dumping raw tool payloads into history** — 50KB JSON blobs are the fastest route to context rot.
- **Uniform Tier-3 privilege** — removes the only structural barrier to destructive action.
- **Tier escalation leakage** — a Tier 1 artifact consumed as a Tier 3 command.
- **Meta-skills with commit rights to main** — self-modification without review.
- **Cyclic skill graphs** — an ancestor re-triggered by a descendant burns tokens indefinitely.
- **Loading the entire catalog body "for awareness"** — maximal rot, zero benefit.
- **Catalog bloat** — beyond roughly 150 skills, Level 1 metadata alone degrades reasoning.

---

**Knowledge Base Entry** | Source: tutored session transcript — *Agent Skills* masterclass (6-module curriculum, 6/6 assessed correct) **Underlying reference:** *Agent Skills* whitepaper; open filesystem standard (agentskills.io) **Format of source:** concept → enterprise customer use case → directory/code pattern → PCA-style pop quiz → evaluation → progress tracker **Evaluation lens:** GCP Well-Architected Framework — Security, Reliability, Performance Efficiency, Cost Optimization, Operational Excellence

---

## 1. Executive Summary

**Context.** LLMs arrive with strong semantic memory (facts) and accumulate episodic memory (what just happened in this session), but they have no **procedural memory** — the disciplined, organization-specific knowledge of *how* a workflow is executed step by step. The historical workaround was stuffing dozens of runbooks into a monolithic system prompt, which produces context rot, instruction drift, and unsustainable token cost. The alternative workaround — spinning up a sub-agent per runbook — produces orchestration sprawl. Agent Skills resolve both: procedural knowledge packaged as portable, version-controlled, filesystem-based units loaded strictly on demand.

**Core Recommendation.** Treat a skill as a **governed software artifact with a lifecycle**, not a prompt fragment. Concretely:

1. Use **progressive disclosure** — metadata always resident, instructions loaded on intent match, references and scripts read only at execution.
2. Respect the **architectural triad**: `AGENTS.md` is policy, MCP is reach, Skills are know-how. Never place a compliance guardrail in a skill.
3. Author top-down (**Path A**) from existing SOPs for regulated work, bottom-up (**Path B**) by crystallizing a proven agent trajectory for emergent work.
4. Evaluate across **three gates** — trigger, trajectory, output — and always against an **adversarial distractor matrix**, never in isolation.
5. **Shift intelligence left**: anything deterministic — math, parsing, schema validation, command syntax — belongs in `scripts/`, not in reasoning tokens.
6. Practice **context hygiene**: evict completed skills, condense history, pin governance.
7. Bind privilege at the **manifest layer** through Capability Profiles, with HITL escalation for mutative tiers.
8. Compose at scale as a **DAG with validation gates**, and close the improvement loop with **meta-skills** — behind a PR and eval gate.

---

## 2. Core Architectural Principles & Decisions

### Decision 1 — Skills exist to supply the missing procedural memory

Semantic memory (pre-trained facts) and episodic memory (session history) are already present; the gap is organizational tradecraft. *Rationale:* without it, agents re-derive complex steps each turn and fail on operational edge cases.

### Decision 2 — Four bottlenecks motivate the pattern

**Context rot** (attention degrades over monolithic prompts), **lack of procedural memory**, **multi-agent sprawl** (separate runtimes created purely to isolate instructions), and **runtime lock-in** (prompts coupled to a proprietary orchestrator). *Rationale:* each has a distinct architectural root cause, and skills address all four simultaneously — the last via an open, filesystem-based, portable standard.

### Decision 3 — Progressive disclosure is the central mechanism

Three tiers: **Level 1** — name and routing description in YAML frontmatter, always resident (~30–80 tokens per skill). **Level 2** — the SKILL.md body with workflow steps and edge cases, loaded on semantic intent match (~500–2,500 tokens). **Level 3** — `references/`, `scripts/`, `assets/`, zero baseline cost, read only when the agent decides to execute or consult. *Rationale:* 35 skills cost roughly 1,750 baseline tokens instead of tens of thousands, while full fidelity remains available on demand.

### Decision 4 — A generalist agent flexing into specialist roles beats a fleet of specialists

One agent backed by a governed skills library replaces a router plus N sub-agents. *Rationale:* removes orchestration overhead, cold-start latency, routing brittleness, and N deployment lifecycles.

### Decision 5 — The triad has hard boundaries

`AGENTS.md` is the **constitution** — static, present every turn, carrying global policy, safety guardrails, identity, and conventions. **MCP** is **hands and sockets** — runtime protocol exposing tools, resources, and endpoints; it provides *reach*. **Skills** are the **standard operating procedure** — dynamic, loaded on match; they provide *know-how* and dictate how and when to invoke MCP tools. *Rationale:* the governing relationship is directional — AGENTS.md governs the skill, the skill instructs execution via MCP.

### Decision 6 — Compliance must never live in a skill

A guardrail placed in a skill is **optional by construction**: if the intent router fails to load it, the agent runs unshielded. *Rationale:* this is the single most consequential boundary error in the triad, and it fails silently.

### Decision 7 — Database connectivity belongs in MCP, not in a skill's scripts

Embedding drivers and direct queries in `scripts/` bypasses centralized connection pooling, service-account security, and enterprise API gateways. *Rationale:* skills describe procedure; MCP owns connection lifecycle, authentication, and schema exposure.

### Decision 8 — Two authoring paths, chosen by provenance of the knowledge

**Path A (top-down)** starts from existing SOPs, wikis, runbooks, or specs, authored by domain experts; best for regulated compliance, financial accounting, and safety-critical operations. **Path B (bottom-up)** starts from a successful multi-turn session and prompts the agent to crystallize what it just did; best for rapid debugging workflows, specialized data transformations, and ad-hoc migrations. *Rationale:* writing a 50-page manual for an emergent incident pattern is disproportionate overhead; conversely, crystallizing an ad-hoc trace is insufficient rigor for a regulated filing.

### Decision 9 — Skills require trajectory evaluation, not output evaluation

Three gates: **Trigger** (did the right skill load — precision and recall), **Trajectory** (were tools called in the correct sequence with valid arguments, against a golden graph), **Output** (schema adherence, policy compliance, factual accuracy). *Rationale:* a correct final answer reached by calling a mutative action before its prerequisite validation is still a production incident.

### Decision 10 — Beware the Evaluation Illusion

A skill unit-tested in isolation with only itself available will show near-100% pass rates while hiding routing conflicts, token contention, and tool collisions. Integrated evaluation alongside all co-located skills exposes trigger-description overlap and routing oscillation. *Rationale:* a skill passing 100% of isolated tests can still drop overall system performance by ~30% by degrading global routing precision.

### Decision 11 — Negative scoping is a first-class frontmatter concern

Descriptions must state when **not** to trigger, with sharp semantic boundaries against adjacent skills. *Rationale:* routing depends on description discrimination; generic phrasing like "adjusts billing" steals queries from neighbors.

### Decision 12 — The context window is a budget with four partitions

**System & catalog** (AGENTS.md + Level 1 entries; fixed, ~3–5k), **active session memory** (history and tool returns; grows monotonically), **dynamic skill context** (loaded Level 2/3; should be ephemeral), **reserved output** (thinking buffer and generation headroom). *Rationale:* each partition has a distinct growth behavior and a distinct failure mode — catalog bloat past ~150 skills, context rot from raw tool payloads, context debt from un-evicted skills, truncation if overflow reaches the reserved partition.

### Decision 13 — Context debt is retaining completed skills across unrelated tasks

Level 2 and Level 3 assets are procedural **working memory** and should be evicted once a skill's state machine reaches terminal completion. *Rationale:* 2,000 instructions from a turn-2 task compete for attention with global governance policy at turn 12 — the observed mechanism behind mid-session guardrail drift.

### Decision 14 — Shift intelligence left

Deterministic work — aggregation, schema validation, syntax formatting, arithmetic — belongs in executable scripts; LLM tokens are reserved for unstructured reasoning, synthesis, and planning. *Rationale:* the reported loan-underwriting result is unambiguous — 84,000 → 2,400 input tokens (97.1% reduction), 78.4% → 100% calculation accuracy, 18.2s → 2.1s latency (8.6×).

### Decision 15 — Privilege is bound at the manifest layer, not left to model discretion

Capability Profiles: **Tier 1** read-only/analytical, **Tier 2** draft/sandboxed (write to `/tmp`, execute scripts in a gVisor or Docker sandbox), **Tier 3** mutative/production (write APIs, DB commits, infrastructure changes, payment gateways). A Tier 1 skill can never directly invoke a Tier 3 tool; mutative actions require explicit escalation or HITL approval tokens governed through AGENTS.md. *Rationale:* an audit skill must be *physically* unable to delete a production disk.

### Decision 16 — Compose as a DAG with validation at every edge

Root orchestrator skills fan out to specialists and fan in to aggregation, with intermediate artifacts validated before downstream mutative nodes fire. *Rationale:* dependency edges enforce ordering (drain → snapshot → delete) in a way that neither hardcoded pipelines nor free-form agent negotiation can.

### Decision 17 — Meta-skills close the improvement loop, under supervision

`skill-creator` automates Path B, `skill-refiner` detects trigger collisions from telemetry and injects negative scoping, `auto-evaluator` heals broken trajectories when external APIs change. *Rationale:* self-improvement without model retraining — but never with direct commit rights to main.

---

## 3. Best Practice Guidelines & Recommended Patterns

### Pattern: Canonical Skill Directory

- **Description:** A self-contained, version-controlled folder governed by the `SKILL.md` primitive.
- **Implementation Guidance:**

```
materials-calc/
├── SKILL.md        # Required: YAML frontmatter + procedural workflow
├── scripts/        # Optional: deterministic helpers (Python/Bash)
│   └── coverage_calc.py
├── references/     # Optional: deep specs and edge cases
│   └── tile_standards_ansi.md
└── assets/         # Optional: output templates and schemas
    └── quote_template.json
```

  Frontmatter carries `name`, a `description` containing both positive triggers and explicit negative boundaries, `version`, `license`, `allowed-tools`, and `metadata` (owner, vertical, compliance tier, capability profile).

- **Guardrails:** Frontmatter is the routing contract — it is the only part always in context, so its precision determines system-wide routing quality. Each domain team independently owns, evaluates, and versions its directory.

### Pattern: Three-Tier Progressive Loading

- **Description:** Metadata at startup, body on match, deep context on execution.
- **Implementation Guidance:** Keep Level 1 descriptions tight and discriminative. Put decision trees and edge-case handling in the Level 2 body. Push formulas, standards tables, and long specifications into `references/` so they cost nothing until needed. The body should *instruct the agent to read* Level 3 conditionally ("inspect `references/tile_standards_ansi.md` if the customer requests wet-room waterproofing specifications").
- **Guardrails:** Watch total catalog size — beyond roughly 150 skills, Level 1 bloat alone degrades reasoning.

### Pattern: Triad Composition

- **Description:** Three primitives operating together with directional responsibility.
- **Implementation Guidance:** `AGENTS.md` holds universal security and privacy rules ("never log unmasked PAN or taxpayer IDs"; "all write actions must carry an authorized session token"). MCP server config holds connection details and secret references. The skill's workflow names the MCP tools and the order and conditions for calling them — for example, retrieve the ledger via `banking_core:get_transactions`, run a local anomaly script, and invoke `banking_core:freeze_card` **only** if the score exceeds 0.85.
- **Guardrails:** Policy in AGENTS.md; connectivity in MCP; sequencing in the skill. Any inversion of this creates either optional compliance or prompt bloat.

### Pattern: Path A Decomposition (Top-Down)

- **Description:** Convert an existing human manual into a three-tier skill.
- **Implementation Guidance:** Audit the runbook, then split by determinism: the **gate** becomes frontmatter trigger criteria, the **decision tree** becomes the SKILL.md workflow, and **lookup tables and validations** become scripts. A 45-page returns manual decomposes into trigger scoping (refund exceptions and damaged items in; shipping tracking out), a step-by-step exception workflow, and `scripts/check_hazmat.py` holding SKU patterns that trigger postal restrictions.
- **Guardrails:** Preferred for regulated, safety-critical, and audit-bearing domains where the procedure must be traceable to an approved source document.

### Pattern: Path B Crystallization (Bottom-Up)

- **Description:** Turn a proven interactive trajectory into a reusable package.
- **Implementation Guidance:** After a successful exploratory session, prompt the agent to synthesize the executed trajectory into a `SKILL.md`. Extract the exact diagnostic commands into modular scripts so syntax is deterministic. Sanitize credentials and environment specifics. Test against a simulator, then commit to version control.
- **Guardrails:** The value is capturing a *validated* sequence cheaply — but the output is a draft artifact, not a released one. Clean, test, and review before deployment.

### Pattern: Three-Gate Evaluation Harness

- **Description:** CI/CD evaluation covering trigger, trajectory, and output.
- **Implementation Guidance:** Build a test spec with a **trigger suite** (positive cases expected to fire, and negative distractor cases expected *not* to fire, naming the skill that should have won instead) and a **trajectory suite** declaring the expected ordered tool sequence. Run against a sandbox. Gate deployment on both.
- **Guardrails:** Distractor cases are the point — a trigger suite of only positive examples measures nothing useful.

### Pattern: Adversarial Distractor Matrix

- **Description:** Mandatory integration test measuring trigger precision and recall against every co-located skill before release.
- **Implementation Guidance:** For a new skill entering a library of N, generate queries representative of all N co-located skills and assert the new skill stays silent on all of them. Measure precision and recall, not pass/fail.
- **Guardrails:** Trigger precision degrades fastest between skills 5 and 20 — build the matrix before authoring skill #2, not after the first collision.

### Pattern: Ephemeral Skill Lifecycle & Context Condensation

- **Description:** The runtime pattern that keeps long sessions stable.
- **Implementation Guidance:** Three coordinated moves — have skills run local transformation scripts that return concise summary artifacts rather than raw payloads; evict Level 2 and Level 3 instructions once the skill's state machine terminates; apply sliding-window summarization to episodic history while keeping `AGENTS.md` pinned immutably in system context.
- **Guardrails:** Pinning governance is what preserves guardrail salience across a 15-turn session; eviction is what prevents completed work from competing with it.

### Pattern: Shift Intelligence Left

- **Description:** Move deterministic logic out of the reasoning path.
- **Implementation Guidance:** Aggregation — a script sums 500 rows and returns total, mean, and count rather than the LLM reading raw JSON. Schema validation — a Pydantic or Zod validator returns a boolean plus an explicit error rather than a prompt instruction to check format. Syntax — a script encapsulates twelve nested CLI flags behind simple positional arguments. Instruct explicitly in the workflow: *"DO NOT calculate DSCR internally using LLM tokens. Execute `python scripts/calculate_dscr.py <NOI> <TOTAL_DEBT_SERVICE>`."*
- **Guardrails:** Scripts should return structured, compact results including a decision flag the workflow can branch on (`is_qualified`, `remediation_recommended`).

### Pattern: Capability Profiles

- **Description:** Least privilege enforced at the skill manifest.
- **Implementation Guidance:** Declare the tier in metadata and constrain `allowed-tools` accordingly. Tier 1 — filesystem read, vector search, read-only MCP APIs; for policy lookups and diagnostics. Tier 2 — `/tmp` writes, sandboxed script execution, diff generation; for drafting and transformation. Tier 3 — write APIs, DB commits, infrastructure and payment actions; gated by HITL approval tokens.
- **Guardrails:** Watch for **tier escalation leakage** — a Tier 1 skill that writes a shell command later consumed by a Tier 3 skill is a privilege-escalation path. Validate artifacts at every DAG edge.

### Pattern: DAG Composition

- **Description:** Three composition topologies. **Linear chaining** — Skill A's artifact triggers Skill B; for sequential extract → validate → write. **Fan-out / fan-in** — a root orchestrator invokes specialists in parallel and aggregates; for cross-functional audits and multi-region diagnostics. **Hierarchical delegation** — a domain skill loads child sub-skills into a sandboxed sub-turn; for deep vertical workflows needing isolation.
- **Guardrails:** Enforce acyclicity at load time — a skill re-triggering its own ancestor causes infinite token burn. Validate intermediate artifacts before any downstream mutative node fires.

### Pattern: Meta-Skills with a Human Gate

- **Description:** Skills that inspect, generate, evaluate, and optimize other skills.
- **Implementation Guidance:** `skill-creator` extracts tools, trajectory, and decision gates from recent context, separates deterministic logic from reasoning, writes scripts and frontmatter with explicit negative boundaries, then validates directory structure against the canonical spec and lints before commit. `skill-refiner` monitors routing telemetry, detects description overlap between similar services, injects negative scoping, and re-runs distractor evals. `auto-evaluator` runs scheduled regression suites and adjusts script flags when external APIs change.
- **Guardrails:** **Never let a meta-skill auto-commit to main.** Route every change through a pull request and an evaluation gate. Run meta-skills at Tier 2 (sandboxed), not Tier 3.

---

## 4. Trade-Off Analysis & Pitfalls

| Option / Decision | Advantages | Trade-Offs / Risks | Mitigations |
|---|---|---|---|
| **Decompose the monolithic prompt into Agent Skills with progressive disclosure, scripts, and delegated ownership** *(chosen, M1)* | Base prompt drops from tens of thousands of tokens to ~1,750 for 35 skills; deterministic steps leave the reasoning path; squads release independently | A catalog and eval harness to operate | Distractor matrix; catalog size discipline |
| 35 fine-tuned microservices on GKE behind an Envoy semantic load balancer | Full isolation per runbook | Enormous infrastructure cost; cold-start latency; model drift across 35 deployments; routing brittleness | One generalist agent plus a skills library |
| Ingest 35 runbooks into vector search and prepend top-3 RAG chunks | Familiar retrieval stack | Naive chunking destroys procedural sequencing, prerequisite ordering, and conditional branches ("if X fails, check Y before Z") | Skills preserve ordered procedure as a unit |
| Expand the context window, set temperature 0.0, enforce XML tagging | No new architecture | Does not remove "lost in the middle"; raises latency and cost on trivial queries; leaves team ownership coupled | Progressive disclosure |
| Semantic cache in front of the LLM over consolidated runbooks | Cheap on repeats | Addresses repetition, not routing, sequencing, or ownership decoupling | Orthogonal optimization at best |
| **AGENTS.md for policy · MCP for databases · Skills for filing workflows** *(chosen, M2)* | Compliance is unconditional; connectivity is centrally authenticated; procedures iterate independently | Three primitives to govern | Clear ownership per layer |
| HIPAA guardrail implemented as a skill | Modular in appearance | **Compliance becomes optional** — an un-triggered skill leaves the agent unshielded | Policy belongs in AGENTS.md, always resident |
| Multi-step domain workflows written into AGENTS.md | Always available | Static-prompt bloat with clinical instructions irrelevant to most turns; context rot | Procedures belong in skills |
| DB drivers and direct queries inside a skill's `scripts/` | Self-contained | Bypasses connection pooling, service-account security, and API gateways | Expose the database through MCP |
| Hardcoded REST APIs in AGENTS.md; masking only inside specific skills | Direct | Separation-of-concerns violation, prompt bloat, and unshielded interactions | Triad boundaries |
| **Path B crystallization of the debugging trajectory into a tested, versioned skill** *(chosen, M3)* | Captures a validated sequence at minimal overhead; deterministic command syntax; auditable Git asset | Draft quality requires review | Sanitize, test against a simulator, PR review |
| Path A 50-page spec plus RAG retrieval for an emergent incident | Thorough documentation | Disproportionate engineering overhead; RAG chunks cannot enforce command ordering and prerequisite validation | Match the path to the knowledge's provenance |
| Fine-tune an open-source LLM on the shell history | "Learns" the session | Brittle, expensive, catastrophic forgetting; fails to separate deterministic syntax from reasoning | Crystallize into scripts instead |
| Append raw bash history to global AGENTS.md | Universally visible | Burns static tokens on every unrelated interaction enterprise-wide; immediate context rot | Scope to a loadable skill |
| **Adversarial distractor matrix + explicit negative scoping in frontmatter** *(chosen, M4 — both)* | Catches trigger theft before release; gives the router the semantic boundary it needs | Eval corpus must be maintained as the library grows | Generate distractors from co-located skill descriptions |
| Raise temperature to explore overlapping descriptions | — | Injects randomness into routing; worsens collisions; makes execution non-deterministic | Keep routing deterministic |
| Replace the runtime with a fine-tuned seq2seq model over all 45 runbooks | Single artifact | Destroys modularity; catastrophic forgetting; full retraining per runbook change | Keep skills modular |
| Embed all 45 skill docs in AGENTS.md for global awareness | Nothing is ever missing | Recreates the monolith — the exact antipattern the architecture exists to remove | Level 1 catalog only |
| **Ephemeral skill lifecycle + context condensation + pinned governance** *(chosen, M5)* | Restores guardrail salience at turn 12+; stops episodic explosion; bounded latency | Eviction logic and summarization to build | Terminal-state eviction; script-side summarization |
| Double the context window and add inference-server memory | No code change | "Lost in the middle" persists at 1M tokens; latency scales linearly or worse | Manage the budget, don't enlarge it |
| Fine-tune an 8B model on all 30 adjudication paths, disable tools | Low latency in theory | Cannot integrate live claim databases or rules engines; eliminates auditability; hallucinates policy | Keep tools and externalize procedure |
| Restart the session each turn, passing 14 raw messages base64-encoded | "Fresh" context | Re-introduces identical bloat every step plus HTTP overhead | Condense, don't relocate |
| **Capability Profiles + DAG orchestration + meta-skill refiner** *(chosen, M6 capstone)* | Privilege bound at the manifest; ordering enforced by dependency edges; routing self-corrects without retraining | Three advanced primitives to operate | Artifact validation per edge; PR gate on refiner |
| Tier-3 permissions for all 80 skills to avoid runtime permission errors | No permission failures | Obliterates least privilege — a read-only billing analyzer could delete production disks | Tiered profiles |
| LLM group-chat consensus to determine execution order | Flexible | Non-deterministic; violates strict dependency ordering on destructive operations | DAG with explicit edges |
| Weekly foundational-model retraining on cloud documentation | Always current in principle | Cost-prohibitive; cannot encode safety gates | Meta-skill refinement of descriptions |
| Consolidate 80 skills into one master script behind an `admin-finops` tool | Simple surface | Destroys modularity and progressive disclosure | Keep the library |
| Hardcode DAGs in a Jenkins pipeline bypassing the agent | Deterministic | You no longer have an autonomous platform | Orchestrate in-agent with validated edges |
| Remove skill descriptions; require users to type exact skill IDs | Unambiguous | Breaks semantic routing and the entire UX premise | Invest in description quality |
| Store cloud credentials in AGENTS.md | Convenient reach | Secrets present in every context window and exposed to prompt injection — critical violation | Secrets in a vault, referenced by MCP config |
| Load all 80 skills simultaneously for "full awareness" | Nothing is missed | Maximal context rot | Progressive disclosure |
| Human SREs manually rewrite all 80 files on every error | Human oversight | Defeats the continuous-evolution requirement; unscalable | Meta-skill proposes, human approves |

**Antipatterns to Avoid**

- **The monolithic system prompt** — 35–40 runbooks in one static block; the originating failure.
- **Compliance guardrails implemented as skills** — makes policy conditional on routing success.
- **Domain workflows written into AGENTS.md** — static bloat irrelevant to most turns.
- **Secrets or credentials in AGENTS.md** — exposed in every context window and to injection.
- **Database drivers inside skill scripts** — bypasses pooling, service-account security, and gateways.
- **Naive RAG chunking of procedures** — destroys sequencing, prerequisites, and conditional branches.
- **Fine-tuning as a substitute for procedure** — brittle, forgetful, unauditable, and blind to live systems.
- **Isolated-only skill evaluation** — the Evaluation Illusion; hides routing collisions entirely.
- **Generic trigger descriptions without negative scoping** — the direct cause of trigger theft.
- **Raising temperature to resolve routing ambiguity** — adds randomness to a determinism problem.
- **Retaining completed skills in context** — context debt; competes with governance for attention.
- **Dumping raw tool payloads into history** — 50KB JSON blobs are the fastest route to context rot.
- **Uniform Tier-3 privilege** — removes the only structural barrier to destructive action.
- **Tier escalation leakage** — a Tier 1 artifact consumed as a Tier 3 command.
- **Meta-skills with commit rights to main** — self-modification without review.
- **Cyclic skill graphs** — an ancestor re-triggered by a descendant burns tokens indefinitely.
- **Loading the entire catalog body "for awareness"** — maximal rot, zero benefit.

---

## 5. Real-World / Customer Scenarios

**Scenario 1: National Home Improvement Retailer — Project Guidance (M1)**

- *Context & Constraints:* A customer asks "I want to remodel my bathroom and tile a shower. What materials do I need, and when can they arrive?" The naive response is to build a dedicated bathroom-remodeling agent.
- *Applied Architecture:* One general-purpose agent over a governed skills library — `project-guidance` (read-only) encodes trade sequencing such as substrate waterproofing before tile; `materials-list` (draft-only) produces a grouped BOM including commonly forgotten items like grout sealer and spacers; `delivery-window` (read-only) queries live inventory and computes freight ETA from regional distribution logistics. Merchandising, Trades Knowledge, and Logistics each own and version their own directory.
- *Outcomes:* Domain expertise stays with the domain team; no new runtime per capability; access tier matches the risk of each step.

**Scenario 2: Trade Contractor Estimation via Progressive Disclosure (M1)**

- *Context & Constraints:* "I have a 180 sq. ft. bathroom floor remodel. What adhesive and membrane products do I need, and can you generate a pro-order summary?"
- *Applied Architecture:* At startup the agent holds Level 1 metadata for 25 store skills. Intent matches `materials-calc`, loading the Level 2 body with tiling sequencing. The skill forbids guessing mortar coverage and instructs execution of `scripts/coverage_calc.py --area 180 --tile_type porcelain`. Output is formatted into `assets/quote_spec.json`.
- *Outcomes:* Correct arithmetic by construction, minimal resident tokens, and a templated deliverable.

**Scenario 3: SaaS Technical Support with 35 Runbooks (M1 quiz)**

- *Context & Constraints:* A monolithic prompt holds 35 diagnostic runbooks — Kubernetes cluster recovery, IAM remediation, billing disputes, SSL renewal. Evals show instruction drift between runbooks, forgotten edge-case validation, and unsustainable input token cost on one-line triage queries.
- *Applied Architecture:* Convert each runbook to a `SKILL.md`; register metadata for progressive disclosure; bundle deterministic logic into scripts; manage each skill in version control under its owning squad.
- *Outcomes:* ~1,750 baseline tokens instead of tens of thousands; drift eliminated by loading one procedure at a time; squads ship without redeploying the core platform.

**Scenario 4: Tier-1 Bank SAR Investigation — The Triad in Production (M2)**

- *Context & Constraints:* Autonomous suspicious-activity investigation touching customer PII and card-freeze authority.
- *Applied Architecture:* `AGENTS.md` forbids logging unmasked PANs or taxpayer IDs, sets model identity, and mandates audit-logging headers on outbound requests. MCP servers `mcp-banking-core` and `mcp-ticketing` expose `get_transactions()`, `freeze_card()`, and `create_case()`. The `fraud-velocity-triage` skill evaluates 24-hour velocity, runs a local geospatial anomaly script, cross-checks IP subnets, and invokes `freeze_card()` **only** above a 0.85 score — otherwise generating an audit memo from a template.
- *Outcomes:* Policy is unconditional, connectivity is centrally authenticated, and the destructive action sits behind an explicit numeric threshold in versioned procedure.

**Scenario 5: Healthcare & Pharmaceutical Research Platform (M2 quiz)**

- *Context & Constraints:* Three requirements — HIPAA compliance and PII redaction on **every** interaction without exception; secure querying of on-premises Oracle clusters and BigQuery; and researcher-defined multi-step statistical cleansing and FDA filing workflows updatable without touching core agent code.
- *Applied Architecture:* Mandatory compliance constraints in `AGENTS.md`; MCP servers exposing Oracle and BigQuery tools; statistical and filing SOPs packaged as version-controlled Agent Skills.
- *Outcomes:* The mapping is the lesson — compliance must be the always-resident layer precisely because "without exception" cannot depend on a router.

**Scenario 6: Omnichannel Retail Returns — Path A Decomposition (M3)**

- *Context & Constraints:* A 45-page support policy manual covering return windows (30-day standard, 90-day holiday, final sale), hazardous materials restrictions on lithium-ion batteries, and fraud velocity rules requiring manager override above $500 without a receipt.
- *Applied Architecture:* Three tiers — frontmatter gates on refund exceptions and damaged items while excluding shipping tracking and warranty registration; the SKILL.md body carries the eligibility and exception decision tree; `scripts/check_hazmat.py` holds the SKU pattern lookup. The workflow explicitly forbids generating a postal return label for HAZMAT items under any circumstance, routing the customer to a physical store.
- *Outcomes:* A human manual becomes a testable, versioned asset with the safety-critical branch enforced deterministically.

**Scenario 7: Global Logistics — Crystallizing a Six-Hour Debug (M3 quiz)**

- *Context & Constraints:* A senior DevOps engineer spent six hours resolving a rare failure spanning Istio service mesh, mTLS certificate expiration, and Kubernetes ingress timeouts across three regions. Leadership wants the capability codified as modular, auditable, reusable, hallucination-proof, and captured with minimal overhead.
- *Applied Architecture:* Path B — the engineer prompts the agent to synthesize the executed CLI trajectory into a `SKILL.md`; diagnostic `kubectl` commands are extracted into modular scripts; the skill is tested against an incident simulator and committed to version control.
- *Outcomes:* Validated sequence captured cheaply, with command syntax made deterministic exactly where hallucination would be most dangerous.

**Scenario 8: Telecom B2B Billing — Trigger Collision in Production (M4)**

- *Context & Constraints:* A 60-skill billing triage agent shows a surge in compliance errors after releasing `dispute-credit-adjustment`.
- *Applied Architecture:* Trigger evals over 500 synthetic queries (250 positive, 250 negative distractors) revealed **64% precision** — the generic phrase "adjusts billing" was stealing queries meant for `standard-payment-plan`. Trajectory evals against a CRM sandbox found that in **18%** of runs the agent called `issue_credit_refund` before `verify_manager_approval_token`. Remediation added negative trigger constraints and codified the approval check into `scripts/validate_token.py`.
- *Outcomes:* Precision to **98.4%**, trajectory violations to **0%** — and a demonstration that both failures were invisible to output-only evaluation.

**Scenario 9: IT Operations Suite — The Evaluation Illusion Realized (M4 quiz)**

- *Context & Constraints:* `db-connection-pool-tuning` scored 99% in isolated unit tests. Within 24 hours in a 45-skill staging environment, `jvm-memory-troubleshooting` began failing because the new skill was loading erroneously, and system-wide latency and token cost rose 35%.
- *Applied Architecture:* Two permanent gates — mandate an adversarial distractor matrix measuring trigger precision and recall against all 44 co-located skills before deployment; refactor the frontmatter with explicit negative scoping that sharply distinguishes database socket limits from JVM heap and garbage-collection issues.
- *Outcomes:* The failure mode is structural, so the fix is structural — a release gate plus a description-quality standard.

**Scenario 10: Commercial Bank Loan Pre-Qualification — Shifting Left (M5)**

- *Context & Constraints:* Pre-qualifying small-business loans requires ingesting three years of balance sheets, computing debt-service coverage ratios, and checking credit bureau thresholds.
- *Applied Architecture:* `scripts/calculate_dscr.py` performs the division and threshold comparison locally, returning `dscr`, `policy_threshold`, `is_qualified`, and `remediation_recommended`. The SKILL.md explicitly instructs the agent not to compute the ratio itself, and branches on the returned flag — drafting approval terms when qualified, or loading `references/credit_mitigants.md` for collateral options when not.
- *Outcomes:* 84,000 → 2,400 input tokens (**97.1% reduction**), 78.4% → **100%** calculation accuracy, 18.2s → 2.1s (**8.6× throughput**).

**Scenario 11: Healthcare Claims Adjudication — Context Degradation at Turn 12 (M5 quiz)**

- *Context & Constraints:* A 30-skill agent running 15-turn adjudication sessions begins ignoring HIPAA masking rules by turn 12; tool latency climbs from 1.5s to 14.8s by turn 14. Inspection shows 50KB raw claim JSON payloads and completed diagnostic skills from turns 2 and 4 still resident in message history.
- *Applied Architecture:* Ephemeral skill lifecycle and context condensation — scripts return concise summary artifacts instead of raw payloads; Level 2/3 instructions are evicted at terminal skill state; sliding-window summarization compresses episodic history while `AGENTS.md` stays pinned in immutable system context.
- *Outcomes:* Guardrail salience is preserved because governance no longer competes with finished work for attention.

**Scenario 12: Fortune 100 FinOps Remediation Platform (M6 capstone)**

- *Context & Constraints:* 80+ skills detecting cloud waste (unattached disks, over-provisioned BigQuery slots, idle node pools), generating optimization plans, and executing remediation. Three non-negotiables — diagnostic skills must never be able to delete or modify resources; multi-stage remediation must run in strict dependency order without skipping safety checks; and the platform must self-correct false-positive routing between similar services such as Cloud Spanner and Cloud SQL.
- *Applied Architecture:* Capability Profiles assign audit skills Tier 1, data processing Tier 2, and infrastructure modification Tier 3 behind HITL approval tokens. DAG orchestration models remediation as a dependency graph — drain → snapshot → delete — with intermediate artifacts validated before downstream mutative nodes fire. A `finops-skill-refiner` meta-skill monitors routing telemetry, detects description overlap, and updates frontmatter with negative trigger constraints.
- *Outcomes:* Each constraint is met by a distinct structural mechanism — privilege at the manifest, ordering at the graph edge, and improvement in a supervised telemetry loop — with no model retraining anywhere.

---

## 6. Topic Modeling & Taxonomic Tags

**Domain Taxonomy** `ai-agents` · `agent-skills` · `procedural-knowledge-engineering` · `context-engineering` · `cloud-infrastructure` · `security-and-compliance` · `evaluation-and-testing` · `devops-and-sre` · `cost-optimization` · `software-architecture`

**Key Entity & Technology Tags** `skill-md` · `agents-md` · `mcp` · `agentskills-io` · `google-adk` · `claude-code` · `codex` · `yaml-frontmatter` · `allowed-tools` · `progressive-disclosure` · `gke` · `envoy` · `kubernetes` · `istio` · `mtls` · `kubectl` · `bigquery` · `cloud-spanner` · `cloud-sql` · `oracle` · `cloud-dlp` · `vector-search` · `gvisor` · `docker-sandbox` · `jenkins` · `git` · `ci-cd` · `pydantic` · `zod` · `json-schema` · `hipaa` · `pos-api` · `crm-sandbox`

**Thematic & Pattern Tags** `procedural-memory` · `semantic-memory` · `episodic-memory` · `context-rot` · `context-debt` · `lost-in-the-middle` · `instruction-drift` · `multi-agent-sprawl` · `runtime-lock-in` · `three-tier-loading` · `on-demand-context` · `token-budgeting` · `context-partitioning` · `architectural-triad` · `separation-of-concerns` · `policy-as-static-context` · `tools-vs-know-how` · `path-a-authoring` · `path-b-crystallization` · `top-down-decomposition` · `bottom-up-synthesis` · `trigger-precision` · `trigger-recall` · `negative-scoping` · `trajectory-fidelity` · `golden-trajectory` · `evaluation-illusion` · `isolated-vs-integrated-eval` · `adversarial-distractor-matrix` · `trigger-collision` · `shift-intelligence-left` · `deterministic-scripting` · `ephemeral-skill-lifecycle` · `context-condensation` · `sliding-window-summarization` · `pinned-governance` · `capability-profiles` · `least-privilege` · `tier-escalation-leakage` · `human-in-the-loop` · `dag-orchestration` · `linear-chaining` · `fan-out-fan-in` · `hierarchical-delegation` · `artifact-validation-gates` · `acyclicity-enforcement` · `meta-skills` · `self-improving-systems` · `skill-refiner` · `trajectory-healing` · `version-controlled-prompts` · `decoupled-ownership` · `portable-standards`

---

## 7. Appendix: Reference Matrices

### A. Architect's Cheat Sheet (session close)

| Principle | The One-Line Rule |
|---|---|
| Progressive Disclosure | Load metadata always, instructions on match, references on demand |
| The Triad | AGENTS.md = policy · MCP = reach · Skills = know-how |
| Authoring | Path A translates existing SOPs; Path B crystallizes proven agent traces |
| Evaluation | Never trust isolated evals — test against an adversarial distractor matrix |
| Shift Intelligence Left | If it's deterministic (math, parsing, schema), it belongs in `scripts/` |
| Context Hygiene | Evict completed skills; condense history; pin governance |
| Least Privilege | Bind tools at the manifest layer via Capability Profiles + HITL for mutative |

### B. The Architectural Triad

| Layer | Primitive | Metaphor | Lifecycle | Primary Concern |
|---|---|---|---|---|
| Governance | `AGENTS.md` | The Constitution | Static — every turn | Global rules, safety policy, identity, conventions |
| Connectivity | MCP | Hands & sockets (USB-C) | Runtime protocol | Reach into APIs, databases, filesystems, SaaS |
| Procedural | Agent Skills | The SOP / runbook | Dynamic — on intent match | How and when to invoke tools |

### C. Progressive Disclosure Tiers

| Tier | Contents | Load Trigger | Token Cost |
|---|---|---|---|
| Level 1 — Catalog | Name, metadata, routing description | Session initialization; always resident | ~30–80 per skill |
| Level 2 — Body | Workflow steps, edge cases | Semantic intent match | ~500–2,500 |
| Level 3 — Deep | `references/`, `scripts/`, `assets/` | On execution or explicit read | Zero baseline |

### D. Context Window Budget Partitions

| Partition | Contents | Behavior | Risk |
|---|---|---|---|
| System & Catalog | AGENTS.md + Level 1 entries | Fixed (~3–5k) | Catalog bloat past ~150 skills degrades reasoning |
| Active Session | History, tool inputs and raw outputs | Grows monotonically | Context rot from large payloads |
| Dynamic Skill Context | Loaded Level 2/3 | Should be ephemeral | Context debt if not evicted |
| Reserved Output | Thinking buffer, structured generation | Pre-allocated | Truncation if overflow reaches it |

### E. Authoring Paths

| Dimension | Path A (Top-Down) | Path B (Bottom-Up) |
|---|---|---|
| Starting point | Existing SOPs, wikis, runbooks, specs | A successful multi-turn agent session |
| Author | Domain experts, architects, engineers | Developer/operator paired with an LLM summarizer |
| Workflow | Audit runbook → split deterministic vs. LLM steps → write trigger criteria | Run task → prompt "crystallize into SKILL.md" → clean and sanitize |
| Best for | Regulated compliance, financial accounting, safety-critical | Debugging workflows, data transformations, ad-hoc migrations |

### F. Evaluation Gates

| Gate | Metric | Critical Failure Mode |
|---|---|---|
| 1 — Trigger | Precision & recall | Over-triggering (token waste, stolen execution) or under-triggering (fallback to hallucination) |
| 2 — Trajectory | Sequence, arguments, parameters vs. golden graph | Skipped prerequisites, out-of-order mutative calls, malformed schemas |
| 3 — Output | Schema adherence, policy compliance, factual accuracy | Incomplete answers, hallucination, unmasked PII |

### G. Capability Profiles

| Tier | Allowed Capabilities | Use Cases |
|---|---|---|
| Tier 1 — Read-only | Filesystem read, vector search, read-only MCP APIs | Policy lookup, diagnostics, documentation search |
| Tier 2 — Draft/sandboxed | `/tmp` writes, sandboxed script execution, diffs | Report drafting, transformation, calculation |
| Tier 3 — Mutative | Write APIs, DB commits, infrastructure, payments | Transfers, VM restarts, refunds, IAM changes |

### H. Composition Patterns

| Pattern | Mechanism | Best For |
|---|---|---|
| Linear chaining | Skill A's artifact triggers Skill B | Extract → validate → write |
| Fan-out / fan-in (DAG) | Root invokes specialists in parallel, aggregates | Cross-functional audits, multi-region diagnostics |
| Hierarchical delegation | Domain skill loads child sub-skills in a sandboxed sub-turn | Deep vertical workflows needing isolation |

### I. Meta-Skill Classes

| Class | Responsibility | Improvement Loop |
|---|---|---|
| `skill-creator` | Synthesize SKILL.md from traces or SOPs (automated Path B) | Ingest logs → generate frontmatter and steps → validate against spec |
| `skill-refiner` | Reduce context consumption, resolve trigger collisions | Detect over-triggering → insert negative scoping → re-run distractor evals |
| `auto-evaluator` | Heal broken API calls and failed commands | Scheduled regression suites → adjust script flags on API change |

### J. Production Pitfalls Called Out in Session

- **Tier escalation leakage** — a Tier 1 skill writing a shell command consumed by a Tier 3 skill is a privilege-escalation path; validate artifacts at every DAG edge.
- **Meta-skill runaway** — never let `skill-refiner` auto-commit to main; route through PR plus eval gate.
- **DAG cycles** — enforce acyclicity at load time; a skill re-triggering its own ancestor causes infinite token burn.

### K. Curriculum Coverage

Module 1 Foundations & Progressive Disclosure · 2 The Architectural Triad · 3 Authoring & Vertical Domains · 4 Evaluation Engineering · 5 Production Runtimes & Context Debt · 6 Advanced Composition & Meta-Skills — all six assessed, **6/6 correct** (B, B, B, B+C, B, B).

### L. Recommended Next Steps (from session close)

1. Pick one real organizational workflow and decompose it Path A style into a `SKILL.md`.
2. Build the distractor matrix **before** writing skill #2 — trigger precision degrades fastest between skills 5 and 20.
3. Set token budget partitions explicitly in runtime config rather than discovering them at the first production overflow.

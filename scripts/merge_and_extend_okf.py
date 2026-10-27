#!/usr/bin/env python3
"""Merge and extend the existing GCS bucket OKF bundle (GEAPL200_2026-09-30_124746,
20 concepts) with the 15 L300 concepts AND the standalone FDE Field-Readiness &
Project Grading Rubric concept (00-fde-field-readiness-and-grading-rubric.md),
producing a unified 36-concept OKF v0.2 bundle in L300_concepts/.

Enforces:
- Existing version_tag (`GEAPL200_2026-09-30_124746`) and 180-day TTL (`stale_after`) preserved
- Standalone FDE Grading Rubric concept (`concepts/00-fde-field-readiness-and-grading-rubric.md`)
- Standalone FDE Grading Rubric & Compliance Enforcement section in `index.md`
- Dedicated FDE Project Grading Rubric Enforcement & Prevailing Customer Examples section
  injected into every single concept (01..35) with cross-references to Concept 00 and
  `https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`.
"""

import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import sys

# Maintain existing bucket version_tag, corpus, and 180-day TTL
BUCKET_NAME = "gea_agent_development_architectural_best_practices_1790796607"
PROJECT_ID = "fivedaysai-prd-sandbox-317383"
CORPUS = "GEAPL200"
VERSION_TAG = "GEAPL200_2026-09-30_124746"
BASE_TIMESTAMP = "2026-09-30T12:47:46-07:00"
BASE_STALE_AFTER = "2027-03-29T12:47:46-07:00"
STALE_AFTER_DAYS = 180
FDE_G3DOC_URL = "https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head"
BUCKET_BROWSER_URL = "https://pantheon.corp.google.com/storage/browser/gea_agent_development_architectural_best_practices_1790796607?forceOnBucketsSortingFiltering=true&project=fivedaysai-prd-sandbox-317383"

FRONT_MATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n+", re.S)


def yq(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return '"%s"' % str(v).replace("\\", "\\\\").replace('"', '\\"')


def parse_fm_meta(fm_block):
    meta = {}
    lines = fm_block.splitlines()
    i = 0

    def unq(val):
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        return val

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m and not line.startswith(" "):
            k, v = m.group(1), m.group(2).strip()
            if v:
                meta[k] = unq(v)
                i += 1
                continue
            items = []
            mp = {}
            i += 1
            cur = None
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                sub = lines[i]
                if not sub.strip():
                    i += 1
                    continue
                mdash = re.match(r"^  - ([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", sub)
                mplain = re.match(r"^  - (.*)$", sub)
                mkv = re.match(r"^    ([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", sub)
                mmap = re.match(r"^  ([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", sub)
                if mdash:
                    cur = {mdash.group(1): unq(mdash.group(2))}
                    items.append(cur)
                elif mkv and cur is not None:
                    cur[mkv.group(1)] = unq(mkv.group(2))
                elif mplain:
                    items.append(unq(mplain.group(1)))
                    cur = None
                elif mmap:
                    mp[mmap.group(1)] = unq(mmap.group(2))
                i += 1
            meta[k] = items if items else mp
            continue
        i += 1
    return meta


def serialize_okf_frontmatter(meta):
    fm = [
        "---",
        f"type: {yq(meta.get('type', 'Architecture Best Practice'))}",
        f"title: {yq(meta['title'])}",
        f"description: {yq(meta['description'])}",
        f"timestamp: {yq(meta['timestamp'])}",
        f"status: {yq(meta.get('status', 'draft'))}",
        f"stale_after: {yq(meta['stale_after'])}",
        "sources:"
    ]
    sources = meta.get("sources") or []
    if isinstance(sources, str):
        sources = [sources]
    for s in sources:
        fm.append(f"  - {yq(s)}")
    gen = meta.get("generated") or {}
    fm.extend([
        "generated:",
        f"  by: {yq(gen.get('by', 'gemini-enterprise:okf-synthesizer'))}",
        f"  at: {yq(gen.get('at', BASE_TIMESTAMP))}",
        f"  method: {yq(gen.get('method', 'OKF v0.2 unified synthesis and FDE rubric alignment'))}",
        "verified:"
    ])
    verified = meta.get("verified") or [
        {
            "by": "machine:structural-qa",
            "at": BASE_TIMESTAMP,
            "scope": "markdown structure, fenced-block balance, Mermaid syntax, table shape, link and placeholder integrity"
        },
        {
            "by": "machine:crc32c-manifest",
            "at": BASE_TIMESTAMP,
            "scope": "content hash recorded in MANIFEST.json"
        }
    ]
    for ev in verified:
        fm.append(f"  - by: {yq(ev.get('by', 'machine:structural-qa'))}")
        fm.append(f"    at: {yq(ev.get('at', BASE_TIMESTAMP))}")
        fm.append(f"    scope: {yq(ev.get('scope', ''))}")
    fm.append("tags:")
    for t in meta.get("tags", []):
        fm.append(f"  - {t}")
    fm.extend([
        f"corpus: {yq(CORPUS)}",
        f"version_tag: {yq(VERSION_TAG)}",
        f"document_id: {yq(meta['document_id'])}",
        f"source_doc_id: {yq(meta['source_doc_id'])}",
        f"content_sha256: {yq(meta['content_sha256'])}",
        "---",
        ""
    ])
    return "\n".join(fm)


def build_concept_00_rubric():
    """Build the standalone Concept 00: FDE Field-Readiness & Project Grading Rubric."""
    title = "Architecture Best Practice: Google Cloud FDE Field-Readiness & Project Grading Rubric (Mandatory Governance Standard)"
    description = (
        "Enforceable grading rubric and competency standard for all Forward Deployed Engineer (FDE) "
        "and Antigravity-driven Agentic AI projects, spanning Presentation & Advisory Rigor (Part A) "
        "and Engineering & Implementation Excellence (Part B) across 30+ sub-competencies and prevailing customer case studies."
    )
    tags = [
        "fde-grading-rubric",
        "field-readiness",
        "advisory-rigor",
        "engineering-excellence",
        "agentic-ai-governance",
        "landing-metrics",
        "well-architected-framework",
        "google-cloud"
    ]

    body = f"""# {title}

**Topics:** {" ".join("#" + t for t in tags)}

> **Sources:** [Cloud FDE Team Handbook (`g3doc`)]({FDE_G3DOC_URL}) · [GCS OKF Bucket (`{BUCKET_NAME}`)]({BUCKET_BROWSER_URL}) · **Corpus:** `{CORPUS}` · **Version:** `{VERSION_TAG}` (180-Day TTL Preserved)

---

## 1. Executive Mandate & Enforcement Policy

Every architecture, concept, prototype, or production application built using this Open Knowledge Format (OKF v0.2) knowledge base — including all Antigravity-driven Agentic AI workflows — **must strictly adhere to the Google Cloud Forward Deployed Engineer (FDE) Grading Rubric** documented in this specification and anchored to the [Cloud FDE Team Charter]({FDE_G3DOC_URL}).

As a Forward Deployed Engineer (FDE), your role bridges **how you build a technical solution** and **how you convey its commercial and operational value to enterprise customers**. Every concept in this catalog (`01` through `35`) explicitly cross-references and enforces this rubric.

### Pass / Fail Cutlines & Governance Rules
1. **Two Mandatory Sections:** Every project and technical review is graded across:
   - **Part A — Section 1: Presentation & Advisory Rigor** (5 competencies)
   - **Part B — Section 2: Engineering & Implementation Excellence** (7 domains, 26 competencies)
2. **Minimum Passing Average (`>= 2.0 - Competent`):** You must achieve an average score of **`2 - Competent`** or higher across **each** of the two sections independently.
3. **Zero-Tolerance Disqualifier (`No Score of 0`):** Scoring a **`0 (Not Demonstrated)`** on **any single metric** triggers an automatic **mandatory pause**. You must remediate the specific architectural or advisory gap and re-present to the panel within **two weeks**.
4. **Coaching & Progression Loop:** Panel evaluations and per-competency scores are shared with your manager to guide targeted coaching and field-readiness certification.

```mermaid
flowchart TD
    subgraph Governance ["FDE Field-Readiness Certification Gate"]
        Start(["FDE Solution / Antigravity Agentic Project"]) --> EvalA["Part A: Presentation & Advisory Rigor<br/>(5 Competencies)"]
        Start --> EvalB["Part B: Engineering & Implementation Excellence<br/>(7 Domains / 26 Competencies)"]
        EvalA --> CheckZero{{"Any Single Metric == 0<br/>(Not Demonstrated)?"}}
        EvalB --> CheckZero
        CheckZero -->|Yes: Disqualifier| Pause["MANDATORY PAUSE<br/>Remediate Specific Gaps & Re-Present Within 2 Weeks"]
        CheckZero -->|No: All Metrics >= 1| CheckAvg{{"Section A Avg >= 2.0 AND<br/>Section B Avg >= 2.0?"}}
        CheckAvg -->|No: Needs Coaching| Coach["Targeted Manager Coaching & Hill-Climbing Sprint"]
        CheckAvg -->|Yes: Competent / Proficient| Pass["FIELD-READY FDE PASS<br/>Approved for Production Customer Delivery"]
    end
```

---

## 2. Official 0–3 Competency Grading Scale

| Score | Level | Definition | Panel Outcome |
|---:|---|---|---|
| **0** | **Not Demonstrated** | The Noogler/FDE missed the mark, ignored the requirement, or could not answer basic questions. | **Growth Opportunity (Automatic Pause & 2-Week Re-Presentation)** |
| **1** | **Awareness** | The Noogler/FDE understands the concept but struggles to apply it practically or misses critical edge cases. | **Needs Additional Coaching** |
| **2** | **Competent** | The Noogler/FDE articulates a solid approach, understands trade-offs, and meets the expectations of a Field-Ready FDE. | **Pass (Field-Ready Baseline)** |
| **3** | **Proficient** | The Noogler/FDE demonstrates deep, production-level expertise, anticipates complex failure modes, and teaches the panel something new. | **Strong Pass (Exemplar Reference Architecture)** |

---

## 3. Part A — Section 1: Presentation & Advisory Rigor

| # | Competency Area | Assessment Focus | What "2 - Competent" Looks Like (Pass Cutline) | Prevailing Customer Best-Practice Exemplar (Corpus Grounded) |
|---|---|---|---|---|
| **A.1** | **Strategic Delivery & Value Articulation** | Can they connect technical architecture to business value? Can they clearly articulate why they built this solution and how it handles commercial reality? | Delivers a compelling, narrative-driven walkthrough of the user experience framed around customer personas and operational impact. Explicitly justifies why the architecture directly solves the root business problem (avoiding a "science project") and presents a viable **Total Cost of Ownership (TCO)** model that demonstrates fiscal responsibility. | **NorthBay Mutual ("ClaimPilot") & Cymbal Support:** Anchoring multi-agent claims triage to a measurable `$ / Resolved Claim` TCO model (stacking Gemini Flash/Pro tokens, Agent Runtime vCPU/GiB-hr, Memory Bank, and Enterprise Search queries) rather than an uncosted demo ([Concept 01](/concepts/01-ai-agent-quality-engineering.md), [Concept 28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md)). |
| **A.2** | **Objection Handling & Technical Defense** | How do they react to executive pushback, and can they defend their implementation choices? | Remains entirely calm, collected, and collaborative under pressure when facing stakeholder resistance. Confidently defends engineering decisions and structural design choices during the Q&A matrix using data-backed logic, while cleanly evaluating and addressing technical trade-offs (e.g., cost vs. latency, model tiering). | **SecureVault Bank ("WireGuard") & Meridian Retail ("ShopMate"):** Defending why a P99 latency of 11s with `EXACT` trajectory verification and deterministic `$200` code-level HITL escalation is mandatory when money moves, whereas P50 < 3s Flash routing handles catalog lookups ([Concept 01](/concepts/01-ai-agent-quality-engineering.md), [Concept 12](/concepts/12-agent-quality.md)). |
| **A.3** | **Presentation Skills** | How effectively do they manage time, pacing, and the overall flow of the meeting? | Paces the presentation to finish on time. Tactfully steers the panel away from rabbit holes, offering to take tangential topics offline without being dismissive. Demonstrates intellectual honesty by confidently admitting *"I don't know, but I will get back to you"* rather than fabricating answers. | **Enterprise Architecture Discovery & AI Steering Committee Briefings:** Structuring executive readouts around CUJ scorecards, WAF pillar trade-off tables, and explicit scope boundaries ([Concept 31](/concepts/31-plan-change-management-for-gemini-enterprise-deployments.md)). |
| **A.4** | **AI-Driven Development Discussion** | How effectively do they demonstrate the use of GenAI tools and harness concepts to accelerate their own development lifecycle and code quality? | Articulates how their harness was set up before coding. Demonstrates understanding of establishing key guidance that enables both **"in the loop"** (quick feature fix that adheres to spec) and **"outside the loop"** (goal-driven — task is taken and executed in an autonomous loop through lint, test, eval until goal is passed) development. Mistakes made by the agent/harness are systematically incorporated back into agent instructions (`AGENTS.md` / `SKILL.md` / specs). | **Spec-Driven Development & Vibe-Coding SecOps Harness:** Using locked specifications (`specs/`), OKF MCP knowledge bases, and post-mortem rule feedback loops so every agent mistake updates the harness instructions and golden regression suite ([Concept 02](/concepts/02-vibe-coding-agent-security-evaluation-kb.md), [Concept 13](/concepts/13-spec-driven-production-grade-development.md), [Concept 16](/concepts/16-the-new-sdlc-with-vibe-coding.md)). |
| **A.5** | **Futures / Roadmap** | Can they communicate what the next phase of development would look like while driving home the value of Google Cloud? | Articulates a clear, progressive roadmap for future development phases, addressing production-grade scalability, performance optimization, and features the customer needs in production deployment. Effectively demonstrates the strategic value of Google Cloud integration, explaining how native GCP services enhance stability, security, and long-term business value. | **Prototype-to-Production Maturity Roadmap:** Phasing from Phase 1 (Local ADK + InMemoryRunner) → Phase 2 (Vertex AI Agent Runtime + Memory Bank + Model Armor) → Phase 3 (Multi-Region Agent Gateway, Agent Registry A2A Mesh, Provisioned Throughput GSUs, and Dataplex OKF Governance) ([Concept 11](/concepts/11-prototype-to-production.md), [Concept 35](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md)). |

---

## 4. Part B — Section 2: Engineering & Implementation Excellence

### Domain B.1: AI/ML Engineering

| # | Competency Area | Assessment Focus | Pass Requirement & What "2 - Competent" Looks Like | Prevailing Customer Best-Practice Exemplars & Linked Concepts |
|---|---|---|---|---|
| **B.1.1** | **Agentic & Multi-Agent Systems** | Agent orchestration patterns, tool/function calling, planning and reasoning loops, memory and state management, multi-agent coordination, cognitive architectures, and integrating agents with legacy/external APIs. | **Competent on >= 2 of the following:**<br>• Designs cognitive architectures & orchestration patterns (`SequentialAgent`, `ParallelAgent`, `LoopAgent`, Router/Coordinator) aligned with Critical User Journeys (CUJs).<br>• Builds functional planning/reasoning loops; utilizes session memory (`session.state`) & Memory Bank ensuring context retention and avoiding infinite execution loops (`max_iterations`).<br>• Implements tool/function calling (`McpToolset`, OpenAPI) integrating legacy/external APIs while respecting data boundaries & security.<br>• Coordinates multi-agent interactions (A2A, `AgentTool` isolated histories vs. shared history) meeting enterprise latency SLAs and graceful error handling. | • **Apex Financial ("LendAssist")** & **Corporate Travel Concierge:** Deterministic ADK workflow orchestration with bounded loops ([Concept 06](/concepts/06-agent-tools-mcp-multi-agent-orchestration.md), [Concept 21](/concepts/21-build-and-deploy-multi-agent-adk-systems.md)).<br>• **International Airline Booking & Wealth Management Assistant:** Stateful Session + Vertex AI Memory Bank consolidation ([Concept 08](/concepts/08-context-engineering-stateful-agents.md), [Concept 23](/concepts/23-agent-context-persistence-and-memories.md), [Concept 24](/concepts/24-agent-with-persistent-memories-deep-dive.md)). |
| **B.1.2** | **Retrieval & Data Engineering for AI** | RAG architecture patterns, embedding models and vector databases, chunking and indexing strategies, hybrid search, grounding and citation, data pipelines for AI, parsing complex document formats (PDF/HTML tables). | **Competent on >= 1 of the following:**<br>• Implements RAG patterns, embeddings, and vector/hybrid search maximizing retrieval precision.<br>• Ensures reliable grounding and inline citations mitigating hallucinations.<br>• Orchestrates data pipelines parsing complex document formats (multi-page PDFs, HTML tables, Mermaid diagrams) with ACL preservation.<br>• Validates retrieval quality against business requirements ensuring production-grade data trust. | • **Financial Services Quarterly Revenue RAG & Enterprise SharePoint/Jira Sync:** Hybrid search with strict source-system ACL replication, Federated vs. Indexed connector selection, and OKF v0.2 Dataplex Knowledge Catalog ingestion ([Concept 29](/concepts/29-deploy-the-gemini-enterprise-app.md), [Concept 03](/concepts/03-enterprise-ai-agent-protocol-stack.md)). |
| **B.1.3** | **Model Selection, Tuning & Optimization** | Model assessment and selection (quality, latency, cost, context), tuning, quantization, distillation, prompt engineering, structured output enforcement (JSON mode), inference optimization, data engineering, encoder/decoder selection. | **Competent on >= 2 of the following:**<br>• Assesses & selects models balancing quality, latency, cost, and context (e.g., Gemini Flash front-door routing with Gemini Pro escalation; calibrated `thinking_config` budgets).<br>• Performs tuning, distillation, or context caching; optimizes inference.<br>• Refines behavior via clean prompt engineering (retiring legacy prompt debt) and enforces strict structured outputs (`response_schema` / JSON mode).<br>• Manages synthetic evaluation data generation, labeling, and preparation. | • **High-Volume Customer Support (10M queries/mo) & Gemini 3 Migration:** Tiered Flash/Pro routing, retiring prompt engineering debt, calibrating thinking budgets, and enforcing `response_schema` ([Concept 26](/concepts/26-hill-climbing-agentic-systems.md), [Concept 27](/concepts/27-upgrade-to-the-latest-models.md), [Concept 28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md)). |
| **B.1.4** | **LLM Ops and Evaluation** | Evaluation methodology for GenAI, quality metrics (faithfulness, relevance, coherence), eval dataset design, human vs. automated evaluation, regression detection, observability (tracing/logging). | **Competent on >= 1 of the following:**<br>• Applies Tri-Partite evaluation methodology using deterministic metrics (schema, regex, trajectory precision/recall, BLEU/ROUGE where applicable — **must be more than LLM-as-a-Judge alone**), calibrated autoraters (Cohen's κ ≥ 0.75), and human SME ground truth.<br>• Designs stratified Golden Datasets; executes offline CI gates and online shadow/canary evaluation.<br>• Detects regressions; implements OpenTelemetry GenAI distributed tracing (`agent.run`, `llm.generate`, `tool.execute`, `agent.transfer`) and structured JSON logging. | • **Aurora Diagnostics & Global Logistics CI Testing:** Combining Black-Box golden dataset regression with Glass-Box trajectory assertions (`EXACT`, `IN_ORDER`, `ANY_ORDER`) and OpenTelemetry tracing in Vertex AI Evaluation Service ([Concept 01](/concepts/01-ai-agent-quality-engineering.md), [Concept 12](/concepts/12-agent-quality.md), [Concept 25](/concepts/25-evaluate-generative-agentic-systems.md)). |
| **B.1.5** | **Domain-Applied AI/ML Expertise** | Translation of vertical-specific business KPIs into AI/ML objectives and architectures. Domain-specific feature engineering, data handling, regulatory compliance (HIPAA, FINRA, EU AI Act), and legacy workflow integration. | **Competent on >= 1 of the following:**<br>• Translates vertical-specific business KPIs into quantifiable AI/ML objectives and CUJ scorecards.<br>• Executes domain-specific data handling; enforces regulatory compliance and privacy (HIPAA PHI redaction, FINRA immutable audit trails, EU AI Act Algorithmic Impact Assessments).<br>• Integrates AI solutions cleanly with industry-standard legacy ERP/CRM/EHR systems. | • **Global HealthTech (HIPAA PHI Protection), Tier-1 Bank SAR Investigation (FINRA), & National Home Improvement Retailer:** Encoding vertical domain expertise as governed ADK Skills and enforcing regulatory guardrails in code ([Concept 02](/concepts/02-vibe-coding-agent-security-evaluation-kb.md), [Concept 07](/concepts/07-enterprise-agent-skills.md), [Concept 14](/concepts/14-agent-skills.md)). |

---

### Domain B.2: Scoping and Documentation

| # | Competency Area | Assessment Focus | What "2 - Competent" Looks Like (Pass Cutline) | Prevailing Customer Best-Practice Exemplars & Linked Concepts |
|---|---|---|---|---|
| **B.2.1** | **Problem Definition** | Identifying and articulating the business problem, translating ambiguity into a technical opportunity, documenting what success unlocks for the customer. | Identifies and articulates business problems clearly; translates ambiguity into actionable technical opportunity. Documents customer success unlocks, justifying the architecture as a direct solution to the root business problem while avoiding "science projects". Anchors scoping decisions to **Critical User Journeys (CUJs)** and **"Definition of Done."** | **Meridian Retail & Omnichannel Returns:** Translating vague "improve support with AI" requests into concrete CUJs with explicit resolution rate, hop count (`1.5–3.0 hops`), and cost-per-ticket targets ([Concept 01](/concepts/01-ai-agent-quality-engineering.md), [Concept 13](/concepts/13-spec-driven-production-grade-development.md)). |
| **B.2.2** | **Technical Scope & Constraints** | Defining technical scope, identifying constraints and assumptions, documenting system boundaries and the architectural approach prior to build. | Defines technical scope precisely; identifies critical constraints (latency SLAs, regionality, quota ceilings, legacy API timeouts). Documents system boundaries and architectural approach prior to build phase, maintaining clear separation between prototype features and production-grade requirements. | **Spec-Driven Production-Grade Development:** Authoring formal `specs/` defining non-goals, latency/token budgets, and sandbox boundaries before generating agent code ([Concept 11](/concepts/11-prototype-to-production.md), [Concept 13](/concepts/13-spec-driven-production-grade-development.md), [Concept 16](/concepts/16-the-new-sdlc-with-vibe-coding.md)). |
| **B.2.3** | **Stakeholder Alignment & Success Criteria** | Evidence of stakeholder alignment, defined success criteria and acceptance criteria, phased delivery plan or architectural roadmap. | Demonstrates robust stakeholder alignment across IT, SecOps, Legal, and Business Units; defines clear acceptance criteria and Develops a phased delivery plan (Pilot → Cohort Waves → GA) synchronizing technical milestones with business expectations. | **Enterprise AI Center of Excellence (CoE) & Agent Release Rings:** RACI matrices, Champion network onboarding, and ring-based acceptance gates ([Concept 31](/concepts/31-plan-change-management-for-gemini-enterprise-deployments.md), [Concept 32](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md)). |
| **B.2.4** | **System Design Artifacts** | Architecture diagrams, data flow diagrams, sequence diagrams. | Produces comprehensive architecture, data flow, and sequence diagrams (e.g., validated Mermaid.js C4/sequence/state topologies) clearly mapping system components, trust boundaries, interaction patterns, and data lifecycles. | **Visual Agent Architecture & Protocol Topologies:** Full sequence diagrams for 3-legged OAuth, WIF token exchange, Model Armor inline inspection, and multi-agent state flow ([Concept 17](/concepts/17-agents-concepts-visually-explained.md), [Concept 30](/concepts/30-third-party-idp-with-workforce-identity-federation.md), [Concept 34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md)). |
| **B.2.5** | **Decision Records (ADRs)** | ADRs, documenting trade-offs, alternatives considered, rationale. | Maintains comprehensive **Architecture Decision Records (ADRs)** and Trade-Off Matrices documenting alternatives considered (e.g., Shared vs. Separate Session History, PAYG vs. Provisioned Throughput, Federated vs. Indexed Search, MCP vs. A2A) and the data-backed rationale. | **Trade-Off Analysis Matrices in Every OKF Concept:** Explicit comparison of pros, cons, failure modes, and mitigations across architectural options ([Concept 03](/concepts/03-enterprise-ai-agent-protocol-stack.md), [Concept 24](/concepts/24-agent-with-persistent-memories-deep-dive.md), [Concept 28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md)). |
| **B.2.6** | **API Documentation** | OpenAPI specs, integration guides, SDK documentation. | Delivers precise OpenAPI 3.0 specifications, strongly typed MCP tool schemas (`inputSchema`), A2A `AgentCard` manifests, and clear SDK integration guides with actionable error recovery hints. | **Contract-First Tool & MCP Design:** Treating tool docstrings, parameter `enum` constraints, and structured error hints as machine-consumable API contracts ([Concept 18](/concepts/18-agent-tools-interoperability-with-mcp.md), [Concept 19](/concepts/19-agent-tools-interoperability-2.md), [Concept 35](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md)). |
| **B.2.7** | **Operational Documentation** | Deployment guides, runbooks, onboarding docs, troubleshooting guides. | Produces actionable deployment guides, Day-2 runbooks, pre-flight checklists, and troubleshooting guides (covering 403 IAM/WIF context mismatches, proxy SSE timeout drops, SCIM hard-deletes, and rollback procedures). | **Agent Runtime & Gemini Enterprise Deployment Runbooks:** Step-by-step Cloud Shell, Terraform, and Dataplex registration runbooks ([Concept 04](/concepts/04-deploying-gemini-enterprise-agent-runtime.md), [Concept 29](/concepts/29-deploy-the-gemini-enterprise-app.md), [Concept 30](/concepts/30-third-party-idp-with-workforce-identity-federation.md)). |

---

### Domain B.3: Security, Privacy & Compliance

| # | Competency Area | Assessment Focus | Pass Requirement & What "2 - Competent" Looks Like | Prevailing Customer Best-Practice Exemplars & Linked Concepts |
|---|---|---|---|---|
| **B.3.1** | **Authentication & Authorization** | Service accounts, IAM, API key scoping, OAuth/OIDC, Least Privilege. | **Competent on >= 2:** Implements robust authN/authZ via per-agent cryptographic identities (`principal://.../reasoningEngines/...`), Workforce Identity Federation (SAML/OIDC + CEL conditions), 3-legged OAuth delegated user authority via Auth Manager, and **Principal Access Boundaries (PAB)** enforcing strict Least Privilege and zero ambient authority. | **Tier-1 Retail Banking & DevOps Assistant Narrow Connector Binding:** Eliminating Confused Deputy risks via 3-legged OAuth and PAB policies ([Concept 02](/concepts/02-vibe-coding-agent-security-evaluation-kb.md), [Concept 30](/concepts/30-third-party-idp-with-workforce-identity-federation.md), [Concept 34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md)). |
| **B.3.2** | **Infrastructure & Network Security** | VPC design, network segmentation, private endpoints, zero-trust architecture, service perimeters, firewall policies. | **Competent on >= 2:** Designs Zero-Trust network architectures using **VPC Service Controls (VPC-SC)** perimeters, Context-Aware Access (CAA), Private Service Connect Interfaces (PSC-I), Split-Horizon DNS, isolated **Agent Sandboxes** (zero internet egress), and centralized **Agent Gateway** ingress/egress enforcement. | **Financial Institution BigQuery Revenue Protection & Hub-VPC Egress Gateway:** Preventing token and data exfiltration with VPC-SC, PSC-I, and Agent Gateway ([Concept 22](/concepts/22-build-enterprise-agents-with-code-execution.md), [Concept 29](/concepts/29-deploy-the-gemini-enterprise-app.md), [Concept 35](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md)). |
| **B.3.3** | **Data Protection & Privacy** | Encryption at rest/transit, PII handling, data classification, DLP, Secrets management. | **Competent on >= 2:** Enforces CMEK encryption at rest and mTLS in transit (`Certificate Manager TrustConfig`); integrates **Sensitive Data Protection (Cloud DLP)** for automatic PII/PHI redaction across prompts, logs, and Memory Bank; isolates OAuth secrets in Secret Manager / Managed Auth Vaults so tokens never enter LLM context. | **Global HealthTech PHI Redaction & Multi-Tenant Vector Isolation:** Blocking Cross-Tenant Vector Poisoning and redacting SSNs/PHI before LLM inference or memory persistence ([Concept 10](/concepts/10-vibe-coding-agent-security-and-evaluation.md), [Concept 33](/concepts/33-model-armor-securing-ai-deployments.md), [Concept 34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md)). |
| **B.3.4** | **AI-Specific Security** | Prompt injection mitigation, output filtering, guardrails, model access controls, content safety. | **Competent on >= 2:** Deploys **Google Cloud Model Armor** templates inline across user inputs, RAG/MCP tool outputs (Indirect Prompt Injection defense), A2A messages, and model responses; enforces deterministic code validation hooks (`before_tool_callback`) and Risk-Stratified HITL Logic Reviews before destructive actions. | **Enterprise Media (Jira Indirect Injection Defense) & Prescription Refill Agent:** Halting poisoned tool outputs and malicious URIs via Model Armor fail-closed callbacks ([Concept 02](/concepts/02-vibe-coding-agent-security-evaluation-kb.md), [Concept 33](/concepts/33-model-armor-securing-ai-deployments.md), [Concept 34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md)). |
| **B.3.5** | **Compliance & Governance** | Audit logging, data residency, regulatory requirements, policy enforcement. | **Competent on >= 1:** Configures immutable Cloud Audit Logs attributing actions to both the specific agent principal and the delegating human user; locks multi-region data residency (`us`, `eu`) at provisioning; enforces Custom Org Policy constraints (`allowlistedEgressAgentGatewaysForAgentEngine`) and **Agent Registry** admission governance. | **EU Sovereign Data Residency & Agent Registry Policy Governance:** Enforcing org-wide guardrails against shadow MCP servers and unapproved agents ([Concept 29](/concepts/29-deploy-the-gemini-enterprise-app.md), [Concept 35](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md)). |

---

### Domain B.4: Reliability & Resilience

| # | Competency Area | Assessment Focus | What "2 - Competent" Looks Like (Pass Cutline) | Prevailing Customer Best-Practice Exemplars & Linked Concepts |
|---|---|---|---|---|
| **B.4.1** | **Availability Design** | Redundancy, failover, health checks, SLO/SLA definition, distributed systems patterns. | Defines semantic SLIs/SLOs (e.g., *"95% of inquiries resolve within 5 hops and P99 < 8s"*); implements idempotency keys on state-mutating tools, multi-region storage redundancy, and durable state checkpointing. | **Portfolio Rebalancing Agent (Preventing Duplicate $50K Trades):** Deterministic idempotency keys and transactional state checkpoints ([Concept 01](/concepts/01-ai-agent-quality-engineering.md), [Concept 05](/concepts/05-enterprise-ai-agent-systems-google-cloud.md)). |
| **B.4.2** | **Observability** | Structured logging, metrics, distributed tracing, AI-specific monitoring. | Emits structured JSON logs (`trace_id`, `span_id`, `session_id`, `turn_id`, `user_id`, `agent_name`) correlated with OpenTelemetry GenAI spans; runs a dedicated **Agent Quality Dashboard** tracking Tokens/Task, Steps/Task (`alert > 6`), Tool Error Rate (`< 1%`), and Groundedness alongside system health. | **Avoiding the "Green Dashboard, Broken Agent" Antipattern:** Correlating Cloud Trace spans with Vertex AI Evaluation metrics ([Concept 01](/concepts/01-ai-agent-quality-engineering.md), [Concept 12](/concepts/12-agent-quality.md), [Concept 29](/concepts/29-deploy-the-gemini-enterprise-app.md)). |
| **B.4.3** | **Failure & Recovery Testing** | Failure injection, red teaming, disaster recovery validation, backup/restore testing. | Executes automated adversarial red-teaming, persona simulation, chaos/fault injection on external MCP tools, and rollback drills (`< 5 min MTTR`). | **Adversarial Simulator & Green-Agent Quarantine Drills:** Stress-testing agents against prompt injection, malformed tool payloads, and regional quota exhaustion ([Concept 10](/concepts/10-vibe-coding-agent-security-and-evaluation.md), [Concept 25](/concepts/25-evaluate-generative-agentic-systems.md)). |
| **B.4.4** | **Graceful Degradation** | Fallback strategies, circuit breakers, retry policies, timeout handling. | Implements bounded retries with exponential backoff, circuit breakers on Agent Gateway, model fallback routing, extended proxy timeouts (3–5 min) + SSE streaming/async polling, and clean human escalation hand-offs with structured context summaries. | **Fleet Dispatch & Multi-Region Incident Remediation:** Falling back cleanly to human dispatchers when external weather/telemetry APIs fail ([Concept 05](/concepts/05-enterprise-ai-agent-systems-google-cloud.md), [Concept 29](/concepts/29-deploy-the-gemini-enterprise-app.md), [Concept 32](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md)). |

---

### Domain B.5: Performance & Cost Optimization

| # | Competency Area | Assessment Focus | What "2 - Competent" Looks Like (Pass Cutline) | Prevailing Customer Best-Practice Exemplars & Linked Concepts |
|---|---|---|---|---|
| **B.5.1** | **Scalability & Elasticity** | Horizontal and vertical scaling strategies, autoscaling policies, load balancing. | Designs stateless, horizontally autoscaling ADK runner tiers backed by managed `VertexAiSessionService`; uses `ParallelAgent` fan-out for concurrent I/O and configures L7 load balancing with SSE keep-alive support. | **High-Concurrency Enterprise Search & Multi-Agent Fan-Out:** Scaling to tens of thousands of concurrent workforce users ([Concept 21](/concepts/21-build-and-deploy-multi-agent-adk-systems.md), [Concept 29](/concepts/29-deploy-the-gemini-enterprise-app.md)). |
| **B.5.2** | **Resource Efficiency** | Compute/GPU right-sizing, autoscaling strategies, spot/preemptible usage. | Right-sizes Agent Runtime vCPU/GiB allocations; enforces ephemeral sandbox TTL reaping; blends **Provisioned Throughput (PT / GSUs)** for steady-state P70 baseline traffic with PAYG burst capacity and Batch Inference (50% discount) for offline evaluation/indexing. | **Enterprise Insurance & Nightly Batch Summarization:** Hybrid PT + PAYG capacity planning and sandbox lifecycle reaping ([Concept 22](/concepts/22-build-enterprise-agents-with-code-execution.md), [Concept 28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md)). |
| **B.5.3** | **AI Cost Management (FinOps)** | Model selection trade-offs, response caching, batching, memory and embeddings, token optimization. | Optimizes `$/Resolved Task` via tiered Flash/Pro routing, **Vertex AI Context Caching** (75–90% prefix discount), progressive skill/tool disclosure (`tool_filter`), session history compaction, and hard per-session token/hop ceilings to prevent **Denial of Wallet (DoW)**. | **Insurance Claims Assistant (Fixing Quadratic $O(N^2)$ Token Growth):** Combining sliding-window compaction, Memory Bank extraction, and Context Caching ([Concept 08](/concepts/08-context-engineering-stateful-agents.md), [Concept 24](/concepts/24-agent-with-persistent-memories-deep-dive.md), [Concept 28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md)). |

---

### Domain B.6: Operational Excellence

| # | Competency Area | Assessment Focus | What "2 - Competent" Looks Like (Pass Cutline) | Prevailing Customer Best-Practice Exemplars & Linked Concepts |
|---|---|---|---|---|
| **B.6.1** | **CI/CD & Deployment** | Pipeline design, deployment strategies, rollback automation. | Implements automated CI/CD pipelines gating deployments on offline Golden Dataset & trajectory evaluations, followed by progressive ring rollouts (Shadow Mode → 5% Canary → 25% → GA) with automated rollback triggers. | **Safe Gemini Model & Agent Ring Rollouts:** Automated shadow/canary pipelines with `< 5 min` rollback ([Concept 11](/concepts/11-prototype-to-production.md), [Concept 27](/concepts/27-upgrade-to-the-latest-models.md), [Concept 32](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md)). |
| **B.6.2** | **Infrastructure as Code (IaC)** | Terraform/Pulumi, Cloud Build, reproducible environments, environment parity. | Codifies buckets, CMEK keys, VPC-SC perimeters, WIF pools, Agent Gateway attachments, and Dataplex Knowledge Catalog entries in **Terraform** and idempotent shell automation (`deploy/setup.sh`, `deploy/terraform/`), ensuring dev/staging/prod parity. | **Reproducible OKF & Agent Runtime Provisioning:** Full Terraform + Cloud Build IaC bundles ([Concept 04](/concepts/04-deploying-gemini-enterprise-agent-runtime.md), [Concept 29](/concepts/29-deploy-the-gemini-enterprise-app.md)). |
| **B.6.3** | **AI Lifecycle Management** | Model and agent versioning, A/B testing, configurations, experiment tracking. | Stamps immutable corpus and agent version tags (`GEAPL200_2026-09-30_124746`), tracks experiments in Vertex AI Evaluation Service, enforces 180-day `stale_after` TTLs on knowledge concepts, and executes structured A/B and SxS evaluations. | **Longitudinal Hill-Climbing & Model Upgrade Tracking:** Versioned experiment scorecards in Vertex AI ([Concept 25](/concepts/25-evaluate-generative-agentic-systems.md), [Concept 26](/concepts/26-hill-climbing-agentic-systems.md), [Concept 27](/concepts/27-upgrade-to-the-latest-models.md)). |
| **B.6.4** | **Testing & Quality Engineering** | Unit, integration, e2e testing, load and performance testing. | Executes deterministic unit tests on tool wrappers, contract tests on MCP schemas, glass-box trajectory integration tests (`.evalset.json`), and concurrency load tests verifying P95/P99 latency under peak load. | ** Pyramid of Agent Testing:** Unit → Tool Contract → Trajectory Glass-Box → End-to-End CUJ Simulation ([Concept 01](/concepts/01-ai-agent-quality-engineering.md), [Concept 13](/concepts/13-spec-driven-production-grade-development.md), [Concept 25](/concepts/25-evaluate-generative-agentic-systems.md)). |

---

### Domain B.7: Designing for Change

| # | Competency Area | Assessment Focus | What "2 - Competent" Looks Like (Pass Cutline) | Prevailing Customer Best-Practice Exemplars & Linked Concepts |
|---|---|---|---|---|
| **B.7.1** | **Modularity & Abstraction** | Loose coupling, interface contracts, model swappability, dependency injection. | Decouples agent orchestration from underlying model providers (LiteLLM / Vertex Model Garden aliases) and storage backends (`SessionService` / `MemoryService` dependency injection), composing capabilities via modular ADK **Skills** and sub-agents. | **Swappable Runner & Model Layer in ADK:** Moving from local `InMemorySessionService` to `VertexAiSessionService` and upgrading Gemini models with zero business logic rewrites ([Concept 07](/concepts/07-enterprise-agent-skills.md), [Concept 21](/concepts/21-build-and-deploy-multi-agent-adk-systems.md), [Concept 27](/concepts/27-upgrade-to-the-latest-models.md)). |
| **B.7.2** | **Configuration Management** | Environment separation, feature flags, externalized config. | Externalizes model IDs, thinking budgets, temperature, Model Armor template IDs, and WIF `login-config.json` into environment-scoped configs and feature flags, enabling zero-code runtime tuning. | **Environment-Scoped Agent Promotion:** Separate dev/staging/prod configs and canary feature flags ([Concept 04](/concepts/04-deploying-gemini-enterprise-agent-runtime.md), [Concept 27](/concepts/27-upgrade-to-the-latest-models.md), [Concept 32](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md)). |
| **B.7.3** | **API Design & Versioning** | Backward compatibility, contract-first design, schema evolution. | Designs versioned MCP tool contracts, A2A `AgentCard` schemas, and OKF v0.2 `bundle.json` / Dataplex `okf` AspectType schemas with strict backward compatibility and content-hash (`content_sha256`) change detection. | **Protocol Stack & Schema Evolution:** Versioned MCP and A2A interfaces across multi-team boundaries ([Concept 03](/concepts/03-enterprise-ai-agent-protocol-stack.md), [Concept 18](/concepts/18-agent-tools-interoperability-with-mcp.md), [Concept 35](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md)). |
| **B.7.4** | **Extensibility** | Plugin patterns, event-driven architecture, webhook/callback support. | Leverages ADK lifecycle callbacks (`before_agent_callback`, `before_model_callback`, `before_tool_callback`, `after_agent_callback`), event-driven Pub/Sub memory consolidation, and modular `SKILL.md` / MCP plugins to extend capabilities without modifying core runner logic. | **Callback-Driven Security, Telemetry & Memory Hooks:** Plugging Model Armor, HITL gates, and async Memory Bank extraction into ADK callbacks ([Concept 21](/concepts/21-build-and-deploy-multi-agent-adk-systems.md), [Concept 24](/concepts/24-agent-with-persistent-memories-deep-dive.md), [Concept 34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md)). |

---

## 5. Prevailing Customer Best-Practice Catalog (Cross-Corpus Reference Matrix)

To achieve **`2 - Competent`** or **`3 - Proficient`** on **Part A.1 (Strategic Delivery)**, **Part A.2 (Objection Handling)**, and **Part B (Engineering Excellence)**, FDEs should ground architectural justifications in the prevailing enterprise customer patterns established across this OKF catalog:

| Industry Vertical | Prevailing Customer Scenario | Core Architectural Problem | Enforced GCP & ADK Solution Pattern | Primary OKF Concepts |
|---|---|---|---|---|
| **Insurance & Financial Services** | **NorthBay Mutual ("ClaimPilot") & Apex Financial ("LendAssist")** | Multi-step claims triage & commercial lending suffering from stochastic trajectory drift and quadratic $O(N^2)$ token cost growth past 20 turns. | `SequentialAgent` + `ParallelAgent` orchestration, sliding-window context compaction, Vertex AI Memory Bank consolidation, and Glass-Box `IN_ORDER` trajectory evaluation. | [01](/concepts/01-ai-agent-quality-engineering.md), [08](/concepts/08-context-engineering-stateful-agents.md), [24](/concepts/24-agent-with-persistent-memories-deep-dive.md), [28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md) |
| **Banking & Wire Transfers** | **SecureVault Bank ("WireGuard") & Tier-1 Bank SAR Investigation** | High-value wire transfers and regulatory SAR investigations where prompt-only rules risk unauthorized execution or Confused Deputy privilege escalation. | Deterministic code-level `$200` auto-approval ceiling returning `ESCALATED_TO_HUMAN`, 3-legged OAuth via Auth Manager, Principal Access Boundaries (PAB), and `EXACT` trajectory gates. | [01](/concepts/01-ai-agent-quality-engineering.md), [02](/concepts/02-vibe-coding-agent-security-evaluation-kb.md), [07](/concepts/07-enterprise-agent-skills.md), [34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md) |
| **Healthcare & Life Sciences** | **Cymbal Health, Aurora Diagnostics & Global HealthTech** | Out-of-network appointment booking, clinical decision support, and prescription refills exposed to indirect prompt injection and HIPAA PHI leakage. | Inline **Model Armor** + **Cloud DLP (SDP)** templates scanning both user prompts and RAG/tool outputs, isolated `AgentSandbox` code execution, and SME-calibrated medical rubrics (κ ≥ 0.80). | [01](/concepts/01-ai-agent-quality-engineering.md), [02](/concepts/02-vibe-coding-agent-security-evaluation-kb.md), [25](/concepts/25-evaluate-generative-agentic-systems.md), [33](/concepts/33-model-armor-securing-ai-deployments.md) |
| **Omnichannel Retail & E-Commerce** | **Meridian Retail ("ShopMate"), Cymbal Athletic Shoes & Home Improvement Retailer** | High-volume (10M queries/mo) order support and project estimation suffering from 35-tool prompt bloat, hallucinated SKUs, and 30s proxy timeouts. | Progressive Skill Disclosure (`SKILL.md` + `McpToolset` `tool_filter`), Tiered Gemini Flash/Pro routing, Context Caching, and 3–5 min SSE streaming load-balancer timeouts. | [07](/concepts/07-enterprise-agent-skills.md), [14](/concepts/14-agent-skills.md), [18](/concepts/18-agent-tools-interoperability-with-mcp.md), [29](/concepts/29-deploy-the-gemini-enterprise-app.md) |
| **Global Logistics & Telecom** | **Multinational Freight Dispatch & Telecom B2B Billing** | Autonomous fleet routing and multi-departmental billing experiencing skill trigger collisions, tool API outages, and shadow MCP sprawl. | **Agent Registry** (`VETTED` admission control), **Agent Gateway** circuit breakers & egress policies, actionable tool error messages for self-healing, and progressive deployment rings. | [05](/concepts/05-enterprise-ai-agent-systems-google-cloud.md), [07](/concepts/07-enterprise-agent-skills.md), [32](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md), [35](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md) |
"""
    body_bytes = body.encode("utf-8")
    sha256 = hashlib.sha256(body_bytes).hexdigest()
    meta = {
        "type": "Architecture Best Practice",
        "title": title,
        "description": description,
        "timestamp": BASE_TIMESTAMP,
        "status": "draft",
        "stale_after": BASE_STALE_AFTER,
        "sources": [
            FDE_G3DOC_URL,
            BUCKET_BROWSER_URL
        ],
        "generated": {
            "by": "gemini-enterprise:okf-synthesizer",
            "at": BASE_TIMESTAMP,
            "method": "FDE Field-Readiness & Project Grading Rubric synthesized into OKF v0.2 standalone concept"
        },
        "tags": tags,
        "document_id": "00-fde-field-readiness-and-grading-rubric",
        "source_doc_id": "cloud-fde-grading-rubric-g3doc",
        "content_sha256": sha256
    }
    full_text = serialize_okf_frontmatter(meta) + "\n" + body
    return meta, body, full_text


# Per-concept tailored FDE Rubric Competency mappings and prevailing customer examples
# Covers Concepts 01..20 (from existing GCS bucket) and Concepts 21..35 (extended from L300 markdowns)
RUBRIC_MAPPINGS = {
    "01-ai-agent-quality-engineering": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Frame agent quality around Critical User Journeys (CUJs) and the Four Pillars (Effectiveness, Efficiency, Robustness, Safety) with a concrete TCO model rather than transport-level uptime.",
            "**A.2 Objection Handling & Technical Defense:** Defend per-CUJ latency vs. safety trade-offs (e.g., why P99 = 11s with deterministic code gates is required for high-value wire transfers while P50 < 3s applies to retail lookups)."
        ],
        "part_b": [
            "**B.1.4 LLM Ops & Evaluation:** Implement Outside-In evaluation combining Black-Box Golden Dataset regression (50–100 SME-curated cases) with Glass-Box trajectory assertions (`EXACT`, `IN_ORDER`, `ANY_ORDER`) and calibrated LLM judges (Cohen's κ ≥ 0.75).",
            "**B.3.4 AI-Specific Security:** Enforce safety-critical thresholds in deterministic code (`$200` refund ceiling returning `ESCALATED_TO_HUMAN`) and sanitize tool outputs via Model Armor.",
            "**B.4.2 Observability:** Emit structured JSON logs (`trace_id`, `session_id`, `turn_id`) correlated with OpenTelemetry spans (`agent.run`, `llm.generate`, `tool.execute`, `agent.transfer`) and alert on `Steps Per Task > 6`."
        ],
        "examples": "NorthBay Mutual ('ClaimPilot' claims triage), Cymbal Health (out-of-network booking), Meridian Retail ('ShopMate' $200 refund guardrail), Aurora Diagnostics (clinical rubric calibration), and SecureVault Bank ('WireGuard' `EXACT` trajectory enforcement)."
    },
    "02-vibe-coding-agent-security-evaluation-kb": {
        "part_a": [
            "**A.4 AI-Driven Development Discussion:** Demonstrate how the coding/agent harness is configured with zero ambient authority, ephemeral sandboxes, and post-mortem rule feedback loops ('in-the-loop' Logic Reviews vs. 'outside-the-loop' autonomous test/lint execution).",
            "**A.2 Objection Handling & Technical Defense:** Defend why prompts are never security boundaries and why structural containment (VPC-SC, gVisor/Firecracker sandboxes, 3-legged OAuth) is non-negotiable."
        ],
        "part_b": [
            "**B.3.1 Authentication & Authorization:** Eliminate ambient authority via per-agent SPIFFE/Service Account identities, 3-legged OAuth delegated user tokens, and Risk-Stratified HITL Logic Reviews.",
            "**B.3.2 Infrastructure & Network Security:** Isolate code execution in ephemeral sandboxes with zero public internet egress and private artifact mirrors to block slopsquatting.",
            "**B.3.4 AI-Specific Security:** Deploy the Green Agent / Red Agent / Agent Fixer SecOps triad to detect indirect prompt injection (e.g., via open Jira tickets or medical records) and halt Denial-of-Wallet loops."
        ],
        "examples": "Global FinTech Core Platform (blocking hallucinated PyPI packages), Global Financial Services Core Banking (air-gapped self-repair loop), Global HealthTech Medical Records (HIPAA PHI injection defense), and Tier-1 Retail Banking (blocking destructive DDL drift)."
    },
    "03-enterprise-ai-agent-protocol-stack": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Articulate why open, interoperable protocols (`MCP`, `A2A`, `UCP`, `AP2/x402`, `A2UI`, `AG-UI`) prevent vendor lock-in and N×M integration sprawl across enterprise business units.",
            "**A.5 Futures / Roadmap:** Present a phased protocol adoption roadmap from internal MCP tool wrappers to cross-departmental A2A meshes and cryptographic AP2 commerce mandates."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Use MCP for vertical agent-to-tool execution and A2A (`AgentCard` discovery + asynchronous task lifecycles) for horizontal peer-to-peer agent collaboration.",
            "**B.2.5 Decision Records (ADRs) & B.2.6 API Documentation:** Document explicit protocol selection trade-offs and publish contract-first OpenAPI / MCP JSON schemas and A2A `AgentCard` descriptors.",
            "**B.7.3 API Design & Versioning:** Enforce backward-compatible schema evolution across MCP tool servers, A2UI generative UI catalogs, and AP2 verifiable credentials."
        ],
        "examples": "Global Omnichannel Retail Supply Chain (MCP inventory tools), Corporate Travel & Expense Concierge (A2A multi-agent negotiation), Multi-Brand Global Marketplace (UCP), Automated Multi-Cloud FinOps Agent (AP2 + x402 cryptographic payment mandates), and Healthcare Claims Dispute Intake (A2UI)."
    },
    "04-deploying-gemini-enterprise-agent-runtime": {
        "part_a": [
            "**A.4 AI-Driven Development Discussion:** Show how reproducible Cloud Shell / CLI deployment harnesses and pre-flight verification scripts eliminate environment drift between local ADK development and managed Agent Runtime.",
            "**A.5 Futures / Roadmap:** Map the transition from initial Reasoning Engine deployment to multi-region HA, Terraform IaC, and Dataplex catalog governance."
        ],
        "part_b": [
            "**B.2.7 Operational Documentation:** Provide step-by-step pre-flight checklists, IAM role binding matrices, and troubleshooting runbooks (resolving empty deployment pickers, cross-project Firestore access, and staging bucket permissions).",
            "**B.6.2 Infrastructure as Code (IaC):** Automate API enablement (`aiplatform.googleapis.com`, `discoveryengine.googleapis.com`), service account provisioning, and Reasoning Engine deployment via scripts and Terraform.",
            "**B.7.2 Configuration Management:** Externalize project IDs, regions, staging buckets, and Memory Bank resource names into environment variables."
        ],
        "examples": "Provisioning a fresh GCP project end-to-end for Vertex AI Agent Runtime, resolving cross-project Firestore IAM bindings, and configuring long-running multi-day stateful workflows."
    },
    "05-enterprise-ai-agent-systems-google-cloud": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Connect Google Cloud's six-layer enterprise agent architecture directly to commercial reliability, security, and TCO outcomes, avoiding fragile 'science project' prototypes.",
            "**A.2 Objection Handling & Technical Defense:** Defend architectural safeguards against the top enterprise failure modes (hallucinated actions, duplicate financial trades, 35-tool context overload, and prompt injection)."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Decompose monolithic 35-tool agents into specialized sub-agents with isolated toolsets and deterministic orchestration (`SequentialAgent`, `ParallelAgent`, `LoopAgent`).",
            "**B.4.1 Availability Design & B.4.4 Graceful Degradation:** Enforce deterministic idempotency keys on mutating tools (preventing duplicate $50K trades) and graceful fallback when external telemetry APIs fail.",
            "**B.5.3 AI Cost Management:** Combine tiered Gemini Flash/Pro routing, context compaction, and semantic caching to sustain 10M+ queries/month economically."
        ],
        "examples": "Retail Order-Status Assistant (fixing turn-15 context crashes), Portfolio Rebalancing Agent (idempotency keys preventing duplicate $50K trades), Clinical Trial Reporting Platform (decomposing 35 tools into sub-agents), and Fleet Dispatch Agent (weather-aware fallback routing)."
    },
    "06-agent-tools-mcp-multi-agent-orchestration": {
        "part_a": [
            "**A.2 Objection Handling & Technical Defense:** Justify when to use single-agent tool calling vs. multi-agent Coordinator/Dispatcher, Sequential, Parallel, or Human-in-the-Loop orchestration topologies using latency and blast-radius data.",
            "**A.4 AI-Driven Development Discussion:** Demonstrate contract-first tool engineering where tool docstrings and structured error hints guide autonomous agent self-correction."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Implement durable multi-agent orchestration patterns integrated with enterprise MCP servers while preventing infinite transfer loops.",
            "**B.2.6 API Documentation:** Design granular, single-responsibility MCP tools with explicit Pydantic/JSON schemas and actionable error messages.",
            "**B.3.1 Authentication & Authorization & B.3.4 AI-Specific Security:** Prevent Confused Deputy attacks from poisoned RAG corpora by enforcing per-user delegated OAuth credentials and deterministic HITL gates before high-impact tool execution."
        ],
        "examples": "Automated Cloud Operations Triage Agent, Global Multi-Departmental GenAI Assistant, Financial Ledger Audit Agent under adversarial input, and Multi-Region Autonomous Incident Remediation Engine."
    },
    "07-enterprise-agent-skills": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Explain how packaging procedural domain expertise into modular `SKILL.md` bundles with Progressive Disclosure reduces prompt token costs by 60–80% while boosting task accuracy.",
            "**A.4 AI-Driven Development Discussion:** Show how recurring agent mistakes and 6-hour debugging breakthroughs are crystallized into reusable, versioned Skills in the Skills Registry."
        ],
        "part_b": [
            "**B.1.5 Domain-Applied AI/ML Expertise:** Encode vertical-specific SOPs (e.g., Tier-1 Bank SAR investigations, retail contractor estimation) as portable `SKILL.md` + `references/` + `scripts/` packages.",
            "**B.5.3 AI Cost Management:** Enforce the 3-tier Progressive Disclosure protocol (Tier 1: ~100-token YAML metadata at startup → Tier 2: `<5,000`-token `SKILL.md` body on trigger → Tier 3: on-demand `references/` and `scripts/`).",
            "**B.7.1 Modularity & Abstraction & B.6.4 Testing:** Avoid the 4 SkillsBench failure modes (conflicting instructions, trigger collisions, over-scaffolding, and bloat) and gate skill releases on trajectory-aware evaluation."
        ],
        "examples": "National Home Improvement Retailer (project estimation via progressive disclosure), SaaS Technical Support (35 runbooks without context bloat), Tier-1 Bank SAR Investigation (Skills + MCP + Sub-agent triad), and Telecom B2B Billing (resolving skill trigger collisions)."
    },
    "08-context-engineering-stateful-agents": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Articulate how Context Engineering and managed Session/Memory tiers transform stateless LLMs into personalized, long-running enterprise advisors while keeping token TCO linear rather than quadratic.",
            "**A.2 Objection Handling & Technical Defense:** Defend the architectural trade-offs between Shared Unified History and Separate Individual Histories (`AgentTool`) across multi-agent workflows."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Architect the 3-tier state model (`temp:` turn scratchpad, `session.state` active dialogue, and `user:`/`app:` long-term Memory Bank).",
            "**B.3.3 Data Protection & Privacy:** Enforce strict tenant/`user_id` isolation, PII redaction before memory extraction, and GDPR/CCPA TTL purge hooks (`DeleteMemory`).",
            "**B.5.3 AI Cost Management:** Eliminate $O(N^2)$ token growth in 40+ turn sessions using token-threshold sliding-window compaction and asynchronous Memory Bank consolidation."
        ],
        "examples": "International Airline Booking Concierge, Financial Advisory Platform (preventing degradation past 20 turns), Online Banking Dispute Orchestration, Health Insurance Claim Adjudication Mesh, and SRE Troubleshooting Sessions exceeding 40 turns."
    },
    "09-platform-native-state-management": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Justify why offloading state management to managed Gemini Enterprise Agent Runtime (`VertexAiSessionService` & Memory Bank) reduces custom database maintenance and accelerates time-to-value.",
            "**A.5 Futures / Roadmap:** Outline the progression from local `InMemorySessionService` prototyping to zero-ops cloud-native persistence and cross-session personalization."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Bind ADK runners to platform-native `VertexAiSessionService` and `VertexAiMemoryBankService` for durable event logging and semantic fact consolidation.",
            "**B.4.1 Availability Design:** Leverage managed multi-zone replication and automatic session state recovery across container restarts.",
            "**B.7.1 Modularity & Abstraction:** Use ADK's `SessionService` and `MemoryService` abstractions so agent logic remains 100% portable between local test harnesses and cloud production."
        ],
        "examples": "Migrating stateful enterprise support agents from custom Redis/Postgres plumbing to zero-ops Vertex AI Agent Runtime Sessions and Memory Bank."
    },
    "10-vibe-coding-agent-security-and-evaluation": {
        "part_a": [
            "**A.2 Objection Handling & Technical Defense:** Address CISO and risk-panel pushback on autonomous coding and action agents using the 7-Pillar Agentic Security Framework and Risk-Stratified Attestation.",
            "**A.4 AI-Driven Development Discussion:** Contrast static benchmark overfitting (e.g., SWE-bench) with real-world intent evaluation and mandatory plain-language 'Logic Reviews' that prevent confirmation fatigue."
        ],
        "part_b": [
            "**B.3.1–B.3.5 Security, Privacy & Compliance:** Implement ephemeral sandboxing, CMEK + mTLS, Cross-Tenant Vector Poisoning prevention, EU AI Act Algorithmic Impact Assessments, and immutable dual-principal audit trails (agent + approving human).",
            "**B.4.2 Observability & B.5.3 AI Cost Management:** Monitor internal reasoning traces to detect hallucination loops and block **Denial of Wallet (DoW)** attacks before billing spikes occur.",
            "**B.1.4 LLM Ops & Evaluation:** Combine deterministic security assertions, Red/Green agent adversarial simulation, and human Logic Reviews."
        ],
        "examples": "Preventing Cross-Tenant Vector Poisoning in multi-tenant RAG, mitigating Denial of Wallet (DoW) loops, and enforcing EU AI Act Algorithmic Impact Assessments with Risk-Stratified Attestation."
    },
    "11-prototype-to-production": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Bridge the 'Prototype-to-Production Chasm' by proving why a notebook demo (80% happy-path accuracy) requires systematic reliability, security, and FinOps engineering to survive enterprise reality.",
            "**A.5 Futures / Roadmap:** Present a concrete, gated production readiness roadmap across CI/CD, evaluation, observability, security, and shadow/canary rollout."
        ],
        "part_b": [
            "**B.2.2 Technical Scope & Constraints:** Define production non-functional requirements (P95/P99 latency, RPS throughput, error budgets, CMEK/VPC-SC boundaries) prior to build.",
            "**B.6.1 CI/CD & Deployment & B.6.3 AI Lifecycle Management:** Build automated AgentOps pipelines with versioned artifacts (code + prompt + model + tool schemas), offline evaluation gates, and safe traffic splitting.",
            "**B.4.4 Graceful Degradation:** Engineer circuit breakers, retry budgets, and deterministic human fallback paths."
        ],
        "examples": "Transitioning an ADK prototype into a production-grade Gemini Enterprise deployment with automated CI/CD evaluation gates, shadow traffic validation, and SRE operational runbooks."
    },
    "12-agent-quality": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Articulate the Outside-In quality philosophy and the Agent Quality Flywheel (Define → Instrument → Evaluate → Curate) tied directly to business KPIs.",
            "**A.2 Objection Handling & Technical Defense:** Defend why traditional deterministic software verification ('did we build it right?') fails on stochastic multi-hop trajectories and why statistical validation is required."
        ],
        "part_b": [
            "**B.1.4 LLM Ops & Evaluation:** Implement the Four Pillars of Agent Quality (Effectiveness, Efficiency, Robustness, Safety & Alignment) using SME-curated Golden Datasets, calibrated LLM-as-a-Judge rubrics, and Glass-Box trajectory evaluation.",
            "**B.4.2 Observability:** Instrument OpenTelemetry semantic spans across all agent hops and maintain a dedicated Agent Quality Dashboard distinct from infrastructure health.",
            "**B.6.4 Testing & Quality Engineering:** Gate every release on automated regression suites where safety metrics are set to `blocking=True`."
        ],
        "examples": "Closing the Agent Quality Flywheel by harvesting production failure trajectories into `PENDING_SME_TRIAGE` queues and promoting SME-validated cases into the Golden Dataset."
    },
    "13-spec-driven-production-grade-development": {
        "part_a": [
            "**A.4 AI-Driven Development Discussion:** Exemplify **Spec-Driven Development (SDD)** — showing how locked functional/architectural specs (`specs/`), `AGENTS.md` / `GEMINI.md` rules, and automated verification harnesses enable both rapid 'in-the-loop' fixes and autonomous 'outside-the-loop' goal execution.",
            "**A.1 Strategic Delivery & Value Articulation:** Anchor every specification to customer Problem Definition, Critical User Journeys (CUJs), and an executable 'Definition of Done'."
        ],
        "part_b": [
            "**B.2.1 Problem Definition & B.2.2 Technical Scope & Constraints:** Write unambiguous specifications covering user personas, system boundaries, non-goals, data contracts, and edge-case scenarios before generating code.",
            "**B.2.5 Decision Records (ADRs):** Version-control architectural decisions and trade-offs alongside the codebase so AI coding agents never violate structural invariants.",
            "**B.6.4 Testing & Quality Engineering:** Pair every spec requirement with executable unit, contract, and trajectory verification tests that the autonomous coding loop must pass."
        ],
        "examples": "Using locked `specs/` and Antigravity execution harnesses to build production-grade graph agents where every harness mistake is fed back into `AGENTS.md` / `SKILL.md` guardrails."
    },
    "14-agent-skills": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Demonstrate how 'Domain Expertise as Code' (`SKILL.md`) lets enterprises scale 100+ regional or vertical process variants without multiplying agent deployments or token costs.",
            "**A.2 Objection Handling & Technical Defense:** Cite empirical findings (SkillsBench & Latitude trajectory studies) to explain how to avoid skill degradation and why trajectory-aware scoring is mandatory for action-taking skills."
        ],
        "part_b": [
            "**B.1.5 Domain-Applied AI/ML Expertise & B.7.1 Modularity:** Package domain procedures into modular `SKILL.md` folders (`references/`, `assets/`, `scripts/`) composed cleanly with MCP tools and sub-agents.",
            "**B.5.3 AI Cost Management:** Use progressive disclosure so agents load full skill instructions only when activated.",
            "**B.1.4 LLM Ops & Evaluation:** Evaluate skills on both final output quality and intermediate tool-call trajectory accuracy (closing the 20–40% gap between output-only and trajectory-aware scoring)."
        ],
        "examples": "Vertical Skills in Retail (Appendix B case study: store operations, returns, and localized compliance across 100+ process variants) and Logistics route-constraint skill composition."
    },
    "15-introduction-to-agents": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Clearly explain the taxonomy of AI systems (Passive LLMs → RAG → Tool-Using Agents → Autonomous Multi-Agent Systems) and justify why an agentic architecture is warranted for the customer's problem.",
            "**A.5 Futures / Roadmap:** Guide customers through the evolutionary maturity curve from single-turn assistants to collaborative multi-agent ecosystems on Google Cloud."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Architect the core anatomy of an agent: Model (Reasoning Engine), Tools (Action/Retrieval), Orchestration Layer (Planning/ReAct/State Graph), and Runtime Infrastructure.",
            "**B.1.3 Model Selection & B.2.4 System Design Artifacts:** Select appropriate models per cognitive role and document clear visual control-loop architectures.",
            "**B.3.4 AI-Specific Security:** Embed identity, guardrails, and HITL oversight into the cognitive loop from Day 1."
        ],
        "examples": "Mapping customer workloads to the right level of agency (avoiding over-engineering simple deterministic workflows while equipping complex multi-step CUJs with ADK orchestration)."
    },
    "16-the-new-sdlc-with-vibe-coding": {
        "part_a": [
            "**A.4 AI-Driven Development Discussion:** Articulate the shift from ad-hoc 'vibe coding' to disciplined **Agentic Software Engineering (AI-Native SDLC)** where the developer acts as Architect & Verifier orchestrating goal-driven agent loops.",
            "**A.2 Objection Handling & Technical Defense:** Address engineering leadership concerns around AI-generated technical debt, security vulnerabilities, and verification bottlenecks."
        ],
        "part_b": [
            "**B.2.2 Technical Scope & B.2.5 Decision Records:** Ground AI coding agents in living architecture specifications, style guides, and ADRs.",
            "**B.6.1 CI/CD & B.6.4 Testing & Quality Engineering:** Build automated verification harnesses (linters, type checkers, unit tests, security scanners, and trajectory evals) that run inside the agent's self-healing loop.",
            "**B.7.1 Modularity & Abstraction:** Enforce small, modular blast radii and strict interface contracts so agent-authored PRs remain reviewable and maintainable."
        ],
        "examples": "Configuring an AI-Native SDLC harness where 'in-the-loop' IDE assistance and 'outside-the-loop' autonomous goal agents iterate against deterministic lint/test/security gates."
    },
    "17-agents-concepts-visually-explained": {
        "part_a": [
            "**A.3 Presentation Skills & A.1 Strategic Delivery:** Use crisp visual mental models and architectural topology diagrams to align executive and technical stakeholders rapidly without jargon overload.",
            "**A.2 Objection Handling & Technical Defense:** Walk through visual sequence flows to answer panel questions on latency hops, token growth, and security boundaries."
        ],
        "part_b": [
            "**B.2.4 System Design Artifacts:** Deliver publication-grade architecture diagrams, data-flow topologies, and sequence diagrams mapping every component (Model, Runner, Session, Memory Bank, Skills, MCP, A2A, Model Armor, Agent Gateway).",
            "**B.1.1 Agentic & Multi-Agent Systems:** Visually map Coordinator, Sequential, Parallel, Loop, and Hierarchical multi-agent patterns to concrete customer journeys."
        ],
        "examples": "Visual reference blueprints for executive briefings and technical design reviews across retail, banking, and healthcare agent deployments."
    },
    "18-agent-tools-interoperability-with-mcp": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Articulate how Model Context Protocol (MCP) standardizes tool connectivity while explaining why enterprise deployments must wrap raw MCP in centralized security and governance.",
            "**A.2 Objection Handling & Technical Defense:** Defend against MCP enterprise risks — dynamic capability injection (e.g., a read-only Books MCP server suddenly adding a paid purchasing tool), confused deputy, and unmonitored data exfiltration."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems & B.2.6 API Documentation:** Design atomic, well-documented tools (avoiding monolithic 'multi-tools') with descriptive, self-healing error messages.",
            "**B.3.1 Authentication & B.3.4 AI-Specific Security:** Pin approved toollists (`tool_filter`), enforce per-user OAuth scopes, and block unauthorized dynamic capability escalation.",
            "**B.7.3 API Design & Versioning:** Maintain strict JSON Schema contracts across MCP servers and clients."
        ],
        "examples": "Cymbal Athletic Shoes product lookup tool (actionable error messages guiding LLM recovery), Corporate Code Repository MCP integration, and preventing dynamic capability injection in a Books MCP service."
    },
    "19-agent-tools-interoperability-2": {
        "part_a": [
            "**A.2 Objection Handling & Technical Defense:** Evaluate trade-offs between built-in platform tools (Google Search, Code Execution, Vertex AI Search), custom function tools, OpenAPI connectors, and remote MCP servers.",
            "**A.5 Futures / Roadmap:** Chart an interoperability roadmap combining MCP tool ecosystems with A2A cross-agent collaboration on Google Cloud."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems & B.1.2 Retrieval & Data Engineering:** Integrate heterogeneous enterprise APIs and RAG data stores cleanly via ADK `FunctionTool`, `OpenAPIToolset`, and `McpToolset`.",
            "**B.3.2 Infrastructure & Network Security & B.4.4 Graceful Degradation:** Route external tool calls through governed VPC boundaries with strict timeouts, retries, and circuit breakers.",
            "**B.2.6 API Documentation:** Enforce clear input/output schemas and payload pruning so tool responses never overflow the model context window."
        ],
        "examples": "Integrating legacy ERP/CRM REST APIs via OpenAPI specs alongside remote MCP tool servers and Vertex AI Search grounding."
    },
    "20-context-engineering-sessions-memory": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Demonstrate how active Context Engineering and two-tier persistence (Sessions + Memory Bank) deliver hyper-personalized customer experiences while controlling token TCO.",
            "**A.2 Objection Handling & Technical Defense:** Defend memory consolidation accuracy, conflict resolution, and privacy compliance during technical deep dives."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Implement full lifecycle management for ADK `Session` events, state prefixes (`app:`, `user:`, `temp:`), and Vertex AI Memory Bank consolidation.",
            "**B.5.3 AI Cost Management:** Combine sliding-window history truncation, asynchronous summarization, and selective semantic memory retrieval (`PreloadMemoryTool` / `LoadMemoryTool`).",
            "**B.3.3 Data Protection & Privacy:** Enforce tenant partitioning, CMEK encryption, and user-initiated memory deletion."
        ],
        "examples": "End-to-end stateful customer concierge combining turn-by-turn session state with cross-session semantic memory consolidation in Vertex AI Memory Bank."
    },
    "21-build-and-deploy-multi-agent-adk-systems": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Connect ADK multi-agent orchestration (`SequentialAgent`, `ParallelAgent`, `LoopAgent`, ADK 2.0 graph workflows) directly to enterprise CUJ reliability and operational impact.",
            "**A.4 AI-Driven Development Discussion:** Show how `adk web`, local runner harnesses, and `.evalset.json` regression suites accelerate iterative development before deploying to Vertex AI Agent Runtime."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Coordinate specialized sub-agents using typed `session.state` (`output_key`), bounded `LoopAgent` iterations (`max_iterations`), and filtered MCP toolsets (`tool_filter`).",
            "**B.7.1 Modularity & B.7.4 Extensibility:** Decouple model configuration via LiteLLM/Model Garden aliases and enforce deterministic guardrails in `before_agent_callback`, `before_model_callback`, and `before_tool_callback`.",
            "**B.6.1 CI/CD & Deployment:** Package and deploy verified multi-agent topologies to managed Vertex AI Agent Runtime and register them in Gemini Enterprise."
        ],
        "examples": "Customer Support Billing & Account Update Pipeline (`SequentialAgent` validation followed by account mutation) and Parallel Travel/Inventory Research (`ParallelAgent` writing to distinct `session.state` keys)."
    },
    "22-build-enterprise-agents-with-code-execution": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Justify offloading complex financial math, tabular data analysis, and charting from probabilistic LLM token prediction to deterministic **Agent Sandbox** Code Execution.",
            "**A.2 Objection Handling & Technical Defense:** Defend the security isolation of dynamic code execution using kernel/container sandboxing, zero internet egress, and strict TTL reaping."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Integrate the Gemini Enterprise Agent Platform SDK `AgentSandbox` with ADK agents for stateful multi-turn Python data analysis.",
            "**B.3.2 Infrastructure & Network Security:** Execute all model-generated code inside isolated sandboxes (never in-process `exec()`), enforcing CPU/memory ceilings and zero ambient credential access.",
            "**B.5.2 Resource Efficiency:** Configure explicit `sandbox_ttl` and session-end teardown hooks to eliminate zombie compute costs."
        ],
        "examples": "Enterprise Financial & Operational Data Analyst Agent executing deterministic Pandas/Matplotlib transformations over uploaded CSVs inside a session-scoped `AgentSandbox`."
    },
    "23-agent-context-persistence-and-memories": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Articulate how the three-pillar Agent Platform persistence stack (**Sessions**, **Memory Bank**, and **Skills Registry**) solves LLM statelessness at enterprise scale.",
            "**A.2 Objection Handling & Technical Defense:** Explain how Level 1–3 context hierarchy engineering and prefix KV-caching prevent context rot and runaway token bills."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Architect clean separation between short-term turn history (`Sessions`), long-term user knowledge (`Memory Bank`), and reusable capabilities (`Skills Registry`).",
            "**B.5.3 AI Cost Management:** Leverage Vertex AI Context Caching for Level 1 static system/skill directives and prune raw tool outputs before appending to session history.",
            "**B.3.3 Data Protection & Privacy:** Enforce tenant isolation and DLP sanitization before persisting facts to long-term memory."
        ],
        "examples": "Enterprise Customer Advisor combining Level 1 cached Skill Registry schemas, Level 2 Memory Bank user preferences, and Level 3 sliding-window session history."
    },
    "24-agent-with-persistent-memories-deep-dive": {
        "part_a": [
            "**A.2 Objection Handling & Technical Defense:** Defend the architectural choice between **Shared Unified History** and **Separate Individual Histories (`AgentTool`)**, and between **Proactive (`PreloadMemoryTool`)** vs. **Reactive (`LoadMemoryTool`)** memory retrieval.",
            "**A.1 Strategic Delivery & Value Articulation:** Quantify the latency and token savings of asynchronous memory consolidation (`after_agent_callback`) and token-threshold context compaction."
        ],
        "part_b": [
            "**B.1.1 Agentic & Multi-Agent Systems:** Implement the 4-stage Memory Lifecycle (Ingestion → Extraction → Consolidation → Retrieval) using Vertex AI Memory Bank and ADK callbacks.",
            "**B.2.5 Decision Records (ADRs):** Document explicit trade-offs for multi-agent context isolation (preventing specialist sub-agent verbosity from polluting the root coordinator's context window).",
            "**B.5.3 AI Cost Management:** Configure custom memory topics so only high-signal business facts are extracted and consolidated."
        ],
        "examples": "Multi-Agent Financial & Retail Concierge using `AgentTool` isolated histories for heavy research specialists and `PreloadMemoryTool` + async `after_agent_callback` consolidation on the root coordinator."
    },
    "25-evaluate-generative-agentic-systems": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Translate executive business KPIs into a quantifiable **Tri-Partite Evaluation Scorecard** (Deterministic Checks + Calibrated Autoraters + Human SME Ground Truth).",
            "**A.2 Objection Handling & Technical Defense:** Defend autorater reliability by presenting Question-Answering rubric decomposition, Cohen's κ ≥ 0.75 calibration data, position-swapping, and glass-box trajectory metrics."
        ],
        "part_b": [
            "**B.1.4 LLM Ops & Evaluation:** Implement comprehensive evaluation in **Vertex AI Gen AI Evaluation Service** covering final response quality, trajectory match modes (`EXACT`, `IN_ORDER`, `ANY_ORDER`), and component-level **Tool, Skill, and Sub-Agent evaluation**.",
            "**B.4.3 Failure & Recovery Testing:** Use controlled user-persona simulation to stress-test multi-turn edge cases and adversarial inputs before launch.",
            "**B.6.1 CI/CD & Deployment:** Transition from ad-hoc 'vibing' to automated CI/CD regression gates and an active Online/Offline Quality Flywheel."
        ],
        "examples": "Cymbal Retail & Enterprise Support evaluation pipelines auditing Skill Goal Completion Rate (>92%), Tool Orchestration Precision (>98%), and P95 step latency (<500ms) in Vertex AI Evaluation Service."
    },
    "26-hill-climbing-agentic-systems": {
        "part_a": [
            "**A.4 AI-Driven Development Discussion:** Demonstrate a scientific, hypothesis-driven **Hill-Climbing Loop** (Baseline → Error Taxonomy → Single-Variable Change → Evaluate → Promote/Revert) rather than ad-hoc prompt tweaking.",
            "**A.2 Objection Handling & Technical Defense:** Explain how to optimize along the multi-dimensional Pareto frontier (Quality, Latency, Cost, Safety) without overfitting to the dev eval set."
        ],
        "part_b": [
            "**B.1.3 Model Selection, Tuning & Optimization:** Prioritize highest-leverage architectural fixes first (Tool Schemas & Context > Orchestration Topology > System Prompt > Few-Shot Examples > SFT).",
            "**B.1.4 LLM Ops & Evaluation & B.4.2 Observability:** Perform root-cause error taxonomy analysis on the bottom 15–20% of trajectories using OpenTelemetry trace trees.",
            "**B.6.3 AI Lifecycle Management:** Track every hill-climbing iteration longitudinally against a frozen baseline scorecard in Vertex AI Evaluation Service."
        ],
        "examples": "Iterative hill-climbing sprints resolving router misclassifications, tool parameter hallucinations, and prompt engineering debt across enterprise ADK multi-agent systems."
    },
    "27-upgrade-to-the-latest-models": {
        "part_a": [
            "**A.5 Futures / Roadmap & A.1 Strategic Delivery:** Articulate a low-risk model lifecycle migration strategy (e.g., upgrading from Gemini 1.5/2.0/2.5 to Gemini 3) that captures new capabilities (Thinking budgets, native multimodal/streaming tools) while reducing TCO.",
            "**A.2 Objection Handling & Technical Defense:** Defend the staged rollout plan (Offline SxS Eval → Dark Shadow Mode → Canary Rings → GA) and explain why retiring legacy 'Prompt Debt' is essential."
        ],
        "part_b": [
            "**B.1.3 Model Selection, Tuning & Optimization:** Strip legacy Chain-of-Thought scaffolding and conflicting negative constraints; calibrate per-node `thinking_config` budgets.",
            "**B.6.1 CI/CD & Deployment & B.6.3 AI Lifecycle Management:** Execute Side-by-Side (SxS) offline regression in Vertex AI Evaluation Service followed by shadow traffic and canary ring deployments with automated rollback.",
            "**B.7.1 Modularity & B.7.2 Configuration Management:** Pin explicit model version strings in externalized config layers rather than hardcoding floating `-latest` aliases."
        ],
        "examples": "Migrating production enterprise agents to Gemini 3 by stripping legacy prompt hacks, tuning thinking budgets per sub-agent role, and validating parity in Shadow Mode."
    },
    "28-cost-estimation-and-optimization-for-agentic-solutions": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Present a rigorous, board-ready **Total Cost of Ownership (TCO)** and FinOps unit-economics model (`$ / Resolved Task`) decomposing all four concurrent billing meters.",
            "**A.2 Objection Handling & Technical Defense:** Defend capacity planning trade-offs across **Pay-As-You-Go (PAYG)**, **Batch Inference (50% discount)**, and **Provisioned Throughput (PT / GSUs)** using token asymmetry (4–8× output vs. input) and trajectory depth math."
        ],
        "part_b": [
            "**B.5.3 AI Cost Management:** Decompose and optimize the 4 billing meters: (1) Token Inference (Input, Output, Thinking, Cached), (2) Agent Runtime Compute/Memory (vCPU-hr/GiB-hr), (3) Memory Bank storage/ops, and (4) Grounding/Enterprise Search queries ($/1k queries).",
            "**B.5.2 Resource Efficiency:** Size Provisioned Throughput GSUs for steady-state baseline traffic and burst peak spikes to PAYG; exploit Context Caching (75–90% savings) and tiered Flash/Pro model routing.",
            "**B.4.2 Observability:** Attach Cloud Billing labels (`agent_name`, `cuj_id`, `department`) and enforce hard per-turn step/token caps (`max_steps <= 6`)."
        ],
        "examples": "Cymbal Support Agent multi-meter bill decomposition, 150-page PDF repair manual Context Caching break-even analysis, and hybrid GSU Provisioned Throughput + PAYG burst sizing."
    },
    "29-deploy-the-gemini-enterprise-app": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Walk stakeholders through an enterprise-ready Gemini Enterprise deployment architecture that respects corporate network perimeters, data residency, and source-system ACLs.",
            "**A.2 Objection Handling & Technical Defense:** Explain to network and security teams why traditional 30-second proxy timeouts break agentic workloads and defend the 3-tier timeout mitigation strategy (3–5 min backend timeouts + SSE streaming + async polling)."
        ],
        "part_b": [
            "**B.3.2 Infrastructure & Network Security & B.3.5 Compliance:** Enforce Zero-Trust ingress with **Context-Aware Access (CAA)**, **VPC Service Controls (VPC-SC)** perimeters, immutable regionality (`us`, `eu`), and **CMEK** encryption.",
            "**B.1.2 Retrieval & Data Engineering:** Configure Federated vs. Indexed enterprise data connectors (SharePoint, Jira, Confluence, Drive, BigQuery) with strict per-user ACL enforcement.",
            "**B.4.2 Observability & B.2.7 Operational Documentation:** Enable OpenTelemetry traces, Cloud Audit Logs, and BigQuery usage exports backed by a complete pre-flight landing zone checklist."
        ],
        "examples": "Financial Institution querying sensitive quarterly revenue data in BigQuery through Gemini Enterprise inside a VPC-SC perimeter with Context-Aware Access and 3–5 minute SSE-enabled load balancer timeouts."
    },
    "30-third-party-idp-with-workforce-identity-federation": {
        "part_a": [
            "**A.2 Objection Handling & Technical Defense:** Defend syncless **Workforce Identity Federation (WIF)** + RFC 8693 STS token exchange to enterprise IAM architects, showing how it eliminates shadow passwords and preserves end-to-end user attribution.",
            "**A.1 Strategic Delivery & Value Articulation:** Demonstrate seamless SSO user experience across Okta, Microsoft Entra ID, or PingFederate into Gemini Enterprise."
        ],
        "part_b": [
            "**B.3.1 Authentication & Authorization:** Configure organization-scoped `WorkforcePool` and `WorkforcePoolProvider` (SAML 2.0 / OIDC), enforce **CEL attribute conditions** (`assertion.department == 'AI-Research'`), and bind IAM roles directly to federated `principal://` / `principalSet://` identities.",
            "**B.3.5 Compliance & Governance:** Ensure Cloud Audit Logs record the true external workforce user identity rather than an anonymous shared service account.",
            "**B.2.7 Operational Documentation:** Provide runbooks for SCIM 2.0 group/license provisioning, `--hard-delete` tenant lifecycle management, and CLI `login-config.json` distribution."
        ],
        "examples": "Federating 25,000 corporate employees from Microsoft Entra ID / Okta into Gemini Enterprise via Workforce Identity Federation with CEL department conditions, SCIM group sync, and direct `principal://` IAM bindings."
    },
    "31-plan-change-management-for-gemini-enterprise-deployments": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Articulate why enterprise AI transformation requires a structured Organizational Change Management (OCM) program to cross 'Shelfware Valley' and realize measurable productivity ROI.",
            "**A.3 Presentation Skills & A.5 Futures / Roadmap:** Align executive sponsors, IT, SecOps, Legal, and Business Unit leaders around a phased cohort rollout roadmap and value-realization telemetry."
        ],
        "part_b": [
            "**B.2.1 Problem Definition & B.2.3 Stakeholder Alignment & Success Criteria:** Establish a formal **AI Center of Excellence (CoE)** charter with clear RACI governance, recruit an embedded **AI Champion Network (5–10% of users)**, and define persona-specific Day-1 workflows.",
            "**B.4.2 Observability:** Track behavioral adoption and value-realization metrics (DAU/MAU stickiness, prompt depth progression, cycle-time reduction, CSAT) rather than vanity license counts.",
            "**B.3.5 Compliance & Governance:** Publish clear Acceptable Use Policies (AUP) and data-boundary transparency guides to eliminate unmonitored consumer 'Shadow AI'."
        ],
        "examples": "Multi-wave enterprise Gemini rollout led by a cross-functional AI Steering Committee (CoE), onboarding Champion cohorts first with role-tailored playbooks for Engineering, Finance, Legal, and Support."
    },
    "32-plan-change-management-for-gemini-enterprise-agents": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Explain how progressive autonomy calibration (Copilot → Supervised Agent with HITL → Autonomous Agent with Exceptions) builds durable user trust in custom enterprise agents.",
            "**A.2 Objection Handling & Technical Defense:** Defend ring-based release governance and automated rollback cutlines when introducing new agent tools, prompt revisions, or model upgrades."
        ],
        "part_b": [
            "**B.6.1 CI/CD & Deployment & B.6.3 AI Lifecycle Management:** Treat every prompt, tool schema, model ID, and connector change as an immutable versioned release artifact promoted through **Progressive Deployment Rings** (Sandbox → SME Alpha → Champion Beta → GA).",
            "**B.2.3 Stakeholder Alignment & B.2.7 Operational Documentation:** Publish in-context agent release notes, capability boundary disclosures, and `< 5 minute MTTR` rollback runbooks.",
            "**B.4.2 Observability & B.4.4 Graceful Degradation:** Monitor post-release behavioral drift (HITL override rates, escalation spikes, thumbs-down telemetry) and enforce clean human hand-offs."
        ],
        "examples": "Rolling out a custom ERP/CRM mutation agent across progressive rings with initial HITL confirmation gates, version-pinned Agent Engine revisions, and 72-hour post-promotion drift monitoring."
    },
    "33-model-armor-securing-ai-deployments": {
        "part_a": [
            "**A.2 Objection Handling & Technical Defense:** Prove to security review boards why system-prompt instructions cannot stop prompt injection and how **Google Cloud Model Armor** provides a model-agnostic, deterministic enforcement perimeter.",
            "**A.1 Strategic Delivery & Value Articulation:** Show how centralized `ModelArmorTemplate` governance accelerates security sign-off across dozens of enterprise AI deployments."
        ],
        "part_b": [
            "**B.3.4 AI-Specific Security:** Enforce inline Model Armor inspection (`sanitizeUserPrompt` & `sanitizeModelResponse`) across all 4 planes: User Input, Retrieved RAG/MCP Tool Outputs (Indirect Prompt Injection defense), Inter-Agent A2A messages, and Final Responses.",
            "**B.3.3 Data Protection & Privacy:** Integrate **Sensitive Data Protection (Cloud DLP)** inspect/de-identify templates inside Model Armor to redact PII/PHI/secrets and block malicious URLs and embedded PDF/Office document injections.",
            "**B.3.5 Compliance & B.4.2 Observability:** Route Model Armor verdicts to Cloud Logging and Security Command Center (SCC) and use Audit-Only (Dry-Run) mode to tune false-positive thresholds (`LOW_AND_ABOVE` vs. `MEDIUM_AND_ABOVE`)."
        ],
        "examples": "Securing an enterprise customer-support and document-analysis agent with Model Armor + Cloud DLP templates to block indirect prompt injections hidden in external PDFs and Jira comments."
    },
    "34-secure-your-agents-with-gemini-enterprise-agent-platform": {
        "part_a": [
            "**A.2 Objection Handling & Technical Defense:** Defend the Zero-Trust agent security architecture against the **Confused Deputy** vulnerability by contrasting Native Machine Identity (`principal://.../reasoningEngines/...`) with 3-Legged OAuth Delegated User Authority.",
            "**A.1 Strategic Delivery & Value Articulation:** Demonstrate how defense-in-depth (Per-Agent Identity + Principal Access Boundaries + Auth Manager + Deterministic Code Validation Hooks) enables safe enterprise automation."
        ],
        "part_b": [
            "**B.3.1 Authentication & Authorization:** Bind narrow IAM roles to each Reasoning Engine's dedicated principal, enforce an absolute ceiling via **Principal Access Boundaries (PAB)**, and orchestrate 3-legged OAuth via **Auth Manager (`GcpAuthProviderScheme`)** so tokens never enter the LLM context.",
            "**B.3.4 AI-Specific Security:** Implement deterministic Python input/output validation hooks (regex format checks, allowlist enums, numeric ceilings, and read-only wire headers on `McpToolset`).",
            "**B.7.4 Extensibility:** Attach security and HITL confirmation gates cleanly via ADK tool wrappers and callbacks."
        ],
        "examples": "DevOps Assistant Agent bound to a narrow `github-oauth-provider` connector (`roles/iamconnectors.user`) with a Principal Access Boundary (PAB), out-of-band Auth Manager token injection, and read-only wire enforcement."
    },
    "35-govern-agents-with-agent-gateway-registry-policies": {
        "part_a": [
            "**A.1 Strategic Delivery & Value Articulation:** Present the enterprise-wide governance blueprint separating the **Control Plane (`Agent Registry`)** from the **Runtime Data Plane (`Agent Gateway`)** to conquer 'Agent Sprawl' and 'Shadow MCP'.",
            "**A.5 Futures / Roadmap:** Articulate how Agent Registry, Agent Gateway, IAP Unified Access Policies, and Custom Organization Policies scale a federated multi-agent ecosystem across the enterprise."
        ],
        "part_b": [
            "**B.3.2 Infrastructure & Network Security:** Route all Client-to-Agent (Ingress) and Agent-to-Anywhere / MCP / A2A (Egress) traffic through **Agent Gateway** using Connectivity Templates, Regional Network Attachments, Private Service Connect Interfaces (PSC-I), Split-Horizon DNS, and Certificate Manager `TrustConfig`.",
            "**B.3.5 Compliance & Governance:** Enforce Custom Org Policy constraints (`allowlistedEgressAgentGatewaysForAgentEngine`), IAP Unified Access Policies (Dry-Run vs. Enforce mode), and Agent Registry `VETTED` admission rules.",
            "**B.4.2 Observability & B.4.4 Graceful Degradation:** Propagate W3C `traceparent` headers and enforce per-consumer rate limits, token quotas, and circuit breakers at the gateway."
        ],
        "examples": "Enterprise Hub-VPC Egress topology where Reasoning Engines have zero direct public internet access and route all outbound MCP and A2A calls through a centralized Agent Gateway governed by Agent Registry and Model Armor."
    }
}


def build_rubric_enforcement_block(doc_id):
    """Build the standardized FDE Grading Rubric Enforcement section injected into every concept."""
    info = RUBRIC_MAPPINGS.get(doc_id)
    if not info:
        sys.exit(f"Missing RUBRIC_MAPPINGS entry for {doc_id}")

    lines = [
        "## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment",
        "",
        f"> **Mandatory Governance Standard:** Every project, prototype, or production agent built using the patterns in this concept **must pass the [Google Cloud FDE Field-Readiness & Project Grading Rubric](/concepts/00-fde-field-readiness-and-grading-rubric.md)** (aligned with the [Cloud FDE Team Charter]({FDE_G3DOC_URL})). Scoring Requirement: **Average >= `2.0 (Competent)`** across both **Part A (Presentation & Advisory Rigor)** and **Part B (Engineering & Implementation Excellence)**, with **zero `0 (Not Demonstrated)` scores** on any single metric.",
        "",
        "### 1. Part A — Presentation & Advisory Rigor Enforcement for This Concept",
        ""
    ]
    for item in info["part_a"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "### 2. Part B — Engineering & Implementation Excellence Cutlines for This Concept",
        ""
    ])
    for item in info["part_b"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "### 3. Prevailing Customer Best-Practice Exemplars to Cite in Panel Reviews",
        "",
        f"- **Grounded Enterprise Scenarios:** {info['examples']}",
        "- **Cross-Reference:** See [Concept 00 — FDE Field-Readiness & Project Grading Rubric](/concepts/00-fde-field-readiness-and-grading-rubric.md) for the complete 0–3 grading scale, 31-competency matrix, and disqualifier remediation rules.",
        "",
        "---",
        ""
    ])
    return "\n".join(lines)


def inject_rubric_into_body(body, doc_id):
    """Idempotently inject the FDE Rubric Enforcement block right after the top header/takeaways."""
    # Remove any prior injected block if re-running
    body = re.sub(
        r"## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment\n.*?\n---\n\n",
        "",
        body,
        flags=re.S
    )
    rubric_block = build_rubric_enforcement_block(doc_id)

    # Ensure Cross-Concept Links (if present) also link to Concept 00
    c00_link = "- [Google Cloud FDE Field-Readiness & Project Grading Rubric (Mandatory Standard)](/concepts/00-fde-field-readiness-and-grading-rubric.md)"
    if "### Cross-Concept Links (OKF Knowledge Graph)" in body and c00_link not in body:
        body = body.replace(
            "### Cross-Concept Links (OKF Knowledge Graph)\n\n",
            f"### Cross-Concept Links (OKF Knowledge Graph)\n\n{c00_link}\n"
        )

    # Insert rubric_block right after the first `---` divider following the title/source callout
    m_div = re.search(r"^---\s*$", body, re.M)
    if m_div:
        insert_pos = m_div.end()
        body = body[:insert_pos] + "\n\n" + rubric_block + body[insert_pos:].lstrip("\n")
    else:
        body = rubric_block + "\n" + body
    return body


def main():
    root_dir = os.getcwd()
    l200_ref_dir = os.path.join(root_dir, "_l200_ref")
    out_dir = os.path.join(root_dir, "L300_concepts")
    concepts_dir = os.path.join(out_dir, "concepts")
    img_dir = os.path.join(out_dir, "img")
    catalog_entries_dir = os.path.join(out_dir, "catalog-entries")

    os.makedirs(concepts_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(catalog_entries_dir, exist_ok=True)

    # Copy all retained images from _l200_ref/img into L300_concepts/img
    if os.path.exists(os.path.join(l200_ref_dir, "img")):
        for dirpath, _dirs, files in os.walk(os.path.join(l200_ref_dir, "img")):
            for f in files:
                src_img = os.path.join(dirpath, f)
                rel = os.path.relpath(src_img, os.path.join(l200_ref_dir, "img"))
                dst_img = os.path.join(img_dir, rel)
                os.makedirs(os.path.dirname(dst_img), exist_ok=True)
                shutil.copy2(src_img, dst_img)

    # Load existing bucket MANIFEST.json and bundle.json for exact metadata preservation
    l200_manifest = json.load(open(os.path.join(l200_ref_dir, "MANIFEST.json"), encoding="utf-8"))
    l200_bundle = json.load(open(os.path.join(l200_ref_dir, "bundle.json"), encoding="utf-8"))

    # First, if L300 concepts are currently named 01..15 in L300_concepts/concepts, stage them in memory
    # before we write 00..35
    l300_old_files = [
        ("01-build-and-deploy-multi-agent-adk-systems.md", "21-build-and-deploy-multi-agent-adk-systems.md", "21-build-and-deploy-multi-agent-adk-systems", 21),
        ("02-build-enterprise-agents-with-code-execution.md", "22-build-enterprise-agents-with-code-execution.md", "22-build-enterprise-agents-with-code-execution", 22),
        ("03-agent-context-persistence-and-memories.md", "23-agent-context-persistence-and-memories.md", "23-agent-context-persistence-and-memories", 23),
        ("04-agent-with-persistent-memories-deep-dive.md", "24-agent-with-persistent-memories-deep-dive.md", "24-agent-with-persistent-memories-deep-dive", 24),
        ("05-evaluate-generative-agentic-systems.md", "25-evaluate-generative-agentic-systems.md", "25-evaluate-generative-agentic-systems", 25),
        ("06-hill-climbing-agentic-systems.md", "26-hill-climbing-agentic-systems.md", "26-hill-climbing-agentic-systems", 26),
        ("07-upgrade-to-the-latest-models.md", "27-upgrade-to-the-latest-models.md", "27-upgrade-to-the-latest-models", 27),
        ("08-cost-estimation-and-optimization-for-agentic-solutions.md", "28-cost-estimation-and-optimization-for-agentic-solutions.md", "28-cost-estimation-and-optimization-for-agentic-solutions", 28),
        ("09-deploy-the-gemini-enterprise-app.md", "29-deploy-the-gemini-enterprise-app.md", "29-deploy-the-gemini-enterprise-app", 29),
        ("10-third-party-idp-with-workforce-identity-federation.md", "30-third-party-idp-with-workforce-identity-federation.md", "30-third-party-idp-with-workforce-identity-federation", 30),
        ("11-plan-change-management-for-gemini-enterprise-deployments.md", "31-plan-change-management-for-gemini-enterprise-deployments.md", "31-plan-change-management-for-gemini-enterprise-deployments", 31),
        ("12-plan-change-management-for-gemini-enterprise-agents.md", "32-plan-change-management-for-gemini-enterprise-agents.md", "32-plan-change-management-for-gemini-enterprise-agents", 32),
        ("13-model-armor-securing-ai-deployments.md", "33-model-armor-securing-ai-deployments.md", "33-model-armor-securing-ai-deployments", 33),
        ("14-secure-your-agents-with-gemini-enterprise-agent-platform.md", "34-secure-your-agents-with-gemini-enterprise-agent-platform.md", "34-secure-your-agents-with-gemini-enterprise-agent-platform", 34),
        ("15-govern-agents-with-agent-gateway-registry-policies.md", "35-govern-agents-with-agent-gateway-registry-policies.md", "35-govern-agents-with-agent-gateway-registry-policies", 35),
    ]

    link_remap = {old_fn[:-3]: new_id for old_fn, _new_fn, new_id, _num in l300_old_files}

    staged_l300 = []
    for old_fn, new_fn, new_id, num in l300_old_files:
        p_new = os.path.join(concepts_dir, new_fn)
        p_old = os.path.join(concepts_dir, old_fn)
        src_p = p_new if os.path.exists(p_new) else p_old
        raw = open(src_p, encoding="utf-8").read()
        staged_l300.append((old_fn, new_fn, new_id, num, raw))

    manifest_docs = []
    bundle_entries = []
    total_mermaid = 0
    total_tables = 0
    total_images = 0
    total_source_figures = 0

    # ------------------------------------------------------------------
    # 1. Write Concept 00: FDE Field-Readiness & Project Grading Rubric
    # ------------------------------------------------------------------
    c00_meta, c00_body, c00_full = build_concept_00_rubric()
    c00_fn = "00-fde-field-readiness-and-grading-rubric.md"
    with open(os.path.join(concepts_dir, c00_fn), "w", encoding="utf-8") as fh:
        fh.write(c00_full)

    c00_mermaid = len(re.findall(r"^```mermaid\s*$", c00_body, re.M))
    c00_tables = len(re.findall(r"^\| ?---", c00_body, re.M))
    total_mermaid += c00_mermaid
    total_tables += c00_tables
    total_source_figures += c00_mermaid

    manifest_docs.append({
        "document_id": c00_meta["document_id"],
        "document_number": 0,
        "title": c00_meta["title"],
        "source_doc_id": c00_meta["source_doc_id"],
        "source_url": FDE_G3DOC_URL,
        "source_modified": BASE_TIMESTAMP,
        "content_sha256": c00_meta["content_sha256"],
        "content_bytes": len(c00_body.encode("utf-8")),
        "topics": c00_meta["tags"],
        "has_best_practice": True,
        "source_figures": c00_mermaid,
        "mermaid_diagrams": c00_mermaid,
        "tables": c00_tables,
        "images_retained": 0
    })
    bundle_entries.append({
        "file": f"concepts/{c00_fn}",
        "title": c00_meta["title"],
        "tags": c00_meta["tags"],
        "stale_after": BASE_STALE_AFTER,
        "status": "draft",
        "source_url": FDE_G3DOC_URL,
        "source_modified": BASE_TIMESTAMP,
        "sha256": c00_meta["content_sha256"],
        "links_rewritten": 0
    })
    print(f"  [OK] {c00_fn:58s} (Concept 00: FDE Grading Rubric)")

    # ------------------------------------------------------------------
    # 2. Merge & Enrich Existing Bucket Concepts 01..20 (Preserving TTL & Version)
    # ------------------------------------------------------------------
    for d_manifest, b_concept in zip(l200_manifest["documents"], l200_bundle["concepts"]):
        fn = os.path.basename(b_concept["file"])
        doc_id = d_manifest["document_id"]
        raw = open(os.path.join(l200_ref_dir, "concepts", fn), encoding="utf-8").read()
        m = FRONT_MATTER_RE.match(raw)
        fm_meta = parse_fm_meta(m.group(1))
        body = raw[m.end():]

        # Inject the FDE Project Grading Rubric Enforcement & Prevailing Customer Examples section
        enriched_body = inject_rubric_into_body(body, doc_id)
        body_bytes = enriched_body.encode("utf-8")
        new_sha256 = hashlib.sha256(body_bytes).hexdigest()

        # Preserve original timestamp, stale_after, version_tag, corpus, source_doc_id
        tags = list(fm_meta.get("tags") or d_manifest["topics"])
        if "fde-grading-rubric" not in tags:
            tags.append("fde-grading-rubric")

        fm_meta["tags"] = tags
        fm_meta["corpus"] = CORPUS
        fm_meta["version_tag"] = VERSION_TAG
        fm_meta["document_id"] = doc_id
        fm_meta["source_doc_id"] = d_manifest["source_doc_id"]
        fm_meta["content_sha256"] = new_sha256

        full_text = serialize_okf_frontmatter(fm_meta) + "\n" + enriched_body
        with open(os.path.join(concepts_dir, fn), "w", encoding="utf-8") as fh:
            fh.write(full_text)

        m_cnt = len(re.findall(r"^```mermaid\s*$", enriched_body, re.M))
        t_cnt = len(re.findall(r"^\| ?---", enriched_body, re.M))
        img_cnt = d_manifest.get("images_retained", 0)
        fig_cnt = d_manifest.get("source_figures", m_cnt)

        total_mermaid += m_cnt
        total_tables += t_cnt
        total_images += img_cnt
        total_source_figures += fig_cnt

        manifest_docs.append({
            "document_id": doc_id,
            "document_number": d_manifest["document_number"],
            "title": d_manifest["title"],
            "source_doc_id": d_manifest["source_doc_id"],
            "source_url": d_manifest["source_url"],
            "source_modified": d_manifest["source_modified"],
            "content_sha256": new_sha256,
            "content_bytes": len(body_bytes),
            "topics": tags,
            "has_best_practice": True,
            "source_figures": fig_cnt,
            "mermaid_diagrams": m_cnt,
            "tables": t_cnt,
            "images_retained": img_cnt
        })
        bundle_entries.append({
            "file": f"concepts/{fn}",
            "title": b_concept["title"],
            "tags": tags,
            "stale_after": b_concept["stale_after"],
            "status": b_concept["status"],
            "source_url": b_concept["source_url"],
            "source_modified": b_concept["source_modified"],
            "sha256": new_sha256,
            "links_rewritten": b_concept.get("links_rewritten", 0)
        })
        print(f"  [OK] {fn:58s} (Merged L200 + FDE Rubric, stale_after={b_concept['stale_after'][:10]})")

    # ------------------------------------------------------------------
    # 3. Extend with L300 Concepts as 21..35 (Aligned to Existing Version & TTL)
    # ------------------------------------------------------------------
    for old_fn, new_fn, new_id, num, raw in staged_l300:
        m = FRONT_MATTER_RE.match(raw)
        fm_meta = parse_fm_meta(m.group(1))
        body = raw[m.end():]

        # Rewrite internal `/concepts/01-...` links in L300 cross-links to `/concepts/21-...`
        for old_k, new_k in link_remap.items():
            body = body.replace(f"(/concepts/{old_k}.md)", f"(/concepts/{new_k}.md)")

        # Update Corpus/Version callout in body header to match unified corpus & version_tag
        body = re.sub(
            r"\*\*Corpus:\*\* `GEAPL300` \(Google Open Knowledge Format v0\.2\)",
            f"**Corpus:** `{CORPUS}` (Unified L200 + L300 Open Knowledge Format v0.2 · Version `{VERSION_TAG}`)",
            body
        )

        # Inject FDE Project Grading Rubric Enforcement & Prevailing Customer Examples section
        enriched_body = inject_rubric_into_body(body, new_id)
        body_bytes = enriched_body.encode("utf-8")
        new_sha256 = hashlib.sha256(body_bytes).hexdigest()

        tags = list(fm_meta.get("tags") or [])
        if "fde-grading-rubric" not in tags:
            tags.append("fde-grading-rubric")

        fm_meta["timestamp"] = BASE_TIMESTAMP
        fm_meta["stale_after"] = BASE_STALE_AFTER
        fm_meta["tags"] = tags
        fm_meta["corpus"] = CORPUS
        fm_meta["version_tag"] = VERSION_TAG
        fm_meta["document_id"] = new_id
        fm_meta["content_sha256"] = new_sha256
        if isinstance(fm_meta.get("generated"), dict):
            fm_meta["generated"]["at"] = BASE_TIMESTAMP
        if isinstance(fm_meta.get("verified"), list):
            for ev in fm_meta["verified"]:
                if isinstance(ev, dict):
                    ev["at"] = BASE_TIMESTAMP

        full_text = serialize_okf_frontmatter(fm_meta) + "\n" + enriched_body
        with open(os.path.join(concepts_dir, new_fn), "w", encoding="utf-8") as fh:
            fh.write(full_text)

        m_cnt = len(re.findall(r"^```mermaid\s*$", enriched_body, re.M))
        t_cnt = len(re.findall(r"^\| ?---", enriched_body, re.M))
        total_mermaid += m_cnt
        total_tables += t_cnt
        total_source_figures += m_cnt

        src_url = fm_meta["sources"][0] if isinstance(fm_meta.get("sources"), list) and fm_meta["sources"] else f"local://GEAP_L300/{old_fn}"

        manifest_docs.append({
            "document_id": new_id,
            "document_number": num,
            "title": fm_meta["title"],
            "source_doc_id": fm_meta["source_doc_id"],
            "source_url": src_url,
            "source_modified": BASE_TIMESTAMP,
            "content_sha256": new_sha256,
            "content_bytes": len(body_bytes),
            "topics": tags,
            "has_best_practice": True,
            "source_figures": m_cnt,
            "mermaid_diagrams": m_cnt,
            "tables": t_cnt,
            "images_retained": 0
        })
        bundle_entries.append({
            "file": f"concepts/{new_fn}",
            "title": fm_meta["title"],
            "tags": tags,
            "stale_after": BASE_STALE_AFTER,
            "status": "draft",
            "source_url": src_url,
            "source_modified": BASE_TIMESTAMP,
            "sha256": new_sha256,
            "links_rewritten": 0
        })
        print(f"  [OK] {new_fn:58s} (Extended L300 + FDE Rubric, stale_after={BASE_STALE_AFTER[:10]})")

    # ------------------------------------------------------------------
    # 4. Write Unified MANIFEST.json and bundle.json
    # ------------------------------------------------------------------
    manifest_obj = {
        "version_tag": VERSION_TAG,
        "corpus": CORPUS,
        "schema_version": 1,
        "generated_at": BASE_TIMESTAMP,
        "gcs_bucket": f"gs://{BUCKET_NAME}",
        "fde_charter_url": FDE_G3DOC_URL,
        "fde_grading_rubric_concept": "concepts/00-fde-field-readiness-and-grading-rubric.md",
        "document_count": len(manifest_docs),
        "totals": {
            "mermaid_diagrams": total_mermaid,
            "tables": total_tables,
            "images_retained": total_images,
            "source_figures": total_source_figures,
            "with_best_practice": len(manifest_docs),
            "with_fde_rubric_enforcement": len(manifest_docs)
        },
        "documents": manifest_docs
    }
    with open(os.path.join(out_dir, "MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest_obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    bundle_obj = {
        "okf_version": "0.2",
        "corpus": CORPUS,
        "version_tag": VERSION_TAG,
        "generated_at": BASE_TIMESTAMP,
        "generated_by": "gemini-enterprise:okf-synthesizer",
        "status": "draft",
        "stale_after_days": STALE_AFTER_DAYS,
        "gcs_bucket": f"gs://{BUCKET_NAME}",
        "fde_charter_url": FDE_G3DOC_URL,
        "fde_grading_rubric_concept": "concepts/00-fde-field-readiness-and-grading-rubric.md",
        "concept_count": len(bundle_entries),
        "concepts": bundle_entries
    }
    with open(os.path.join(out_dir, "bundle.json"), "w", encoding="utf-8") as fh:
        json.dump(bundle_obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    # ------------------------------------------------------------------
    # 5. Write Unified index.md & INDEX.md (with Standalone FDE Rubric Section)
    # ------------------------------------------------------------------
    idx_lines = [
        "---",
        f"type: {yq('Index')}",
        f"title: {yq('GEA Agent Development — Unified Architecture Best Practices & FDE Grading Rubric Knowledge Base (L200 + L300)')}",
        f"description: {yq('Root progressive-disclosure index for the unified GEAPL200 + GEAPL300 Open Knowledge Format (OKF v0.2) bundle, enforcing the Google Cloud FDE Field-Readiness Grading Rubric across all 36 concepts.')}",
        f"timestamp: {yq(BASE_TIMESTAMP)}",
        f"status: {yq('draft')}",
        f"stale_after: {yq(BASE_STALE_AFTER)}",
        f"corpus: {yq(CORPUS)}",
        f"version_tag: {yq(VERSION_TAG)}",
        "---",
        "",
        "# GEA Agent Development — Unified Architecture Best Practices & FDE Grading Rubric Knowledge Base",
        "",
        f"Open Knowledge Format (`OKF v0.2`) bundle · **Version:** `{VERSION_TAG}` · **Corpus:** `{CORPUS}` · **TTL:** `{STALE_AFTER_DAYS} days` (Existing Version & TTL Preserved)",
        "",
        f"- **Backing Cloud Storage Bucket:** [`gs://{BUCKET_NAME}`]({BUCKET_BROWSER_URL}) (`project={PROJECT_ID}`)",
        f"- **Cloud FDE Team Charter Reference:** [`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`]({FDE_G3DOC_URL})",
        f"- **Mandatory Project Grading Rubric Concept:** [`/concepts/00-fde-field-readiness-and-grading-rubric.md`](/concepts/00-fde-field-readiness-and-grading-rubric.md)",
        "",
        f"**Bundle Totals:** **{len(bundle_entries)} Concepts** (1 FDE Grading Rubric Standard + 20 Existing GCS Bucket L200 Concepts + 15 Extended L300 Concepts) · **{total_mermaid} Mermaid Diagrams** · **{total_tables} GFM Tables** · **{total_images} Retained Figures** · **100% FDE Grading Rubric Enforcement**",
        "",
        "---",
        "",
        "## Mandatory Governance: Google Cloud FDE Field-Readiness & Project Grading Rubric",
        "",
        "> **Enforceable Rule Across All Projects & Concepts:** Every architecture, prototype, skill, or application built using this OKF knowledge base must satisfy the [Google Cloud FDE Field-Readiness & Project Grading Rubric](/concepts/00-fde-field-readiness-and-grading-rubric.md) and the [Cloud FDE Charter](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).",
        "",
        "### Grading Scale (0–3) & Pass Cutlines",
        "",
        "| Score | Level | Definition | Enforcement Rule |",
        "|---:|---|---|---|",
        "| **0** | **Not Demonstrated** | Missed the mark, ignored the requirement, or could not answer basic questions. | **AUTOMATIC PAUSE:** Must remediate gaps and re-present within **2 weeks** if *any single metric* scores `0`. |",
        "| **1** | **Awareness** | Understands the concept but struggles to apply it practically or misses critical edge cases. | Needs Additional Coaching (must be offset so section average >= 2.0). |",
        "| **2** | **Competent (Pass)** | Articulates a solid approach, understands trade-offs, and meets Field-Ready FDE expectations. | **PASS BASELINE:** Requires an average score of **`>= 2.0`** in **Part A** AND **`>= 2.0`** in **Part B**. |",
        "| **3** | **Proficient (Strong Pass)** | Demonstrates deep, production-level expertise, anticipates complex failure modes, and teaches the panel something new. | Exemplar Reference Architecture. |",
        "",
        "### Rubric Competency Architecture (Enforced in Every Concept `01`–`35`)",
        "",
        "| Rubric Section | Domain / Competency Cluster | Core Assessment Cutlines (`2 - Competent`) | Primary OKF Concepts |",
        "|---|---|---|---|",
        "| **Part A: Presentation & Advisory Rigor** | **1. Strategic Delivery & Value Articulation**<br>**2. Objection Handling & Technical Defense**<br>**3. Presentation Skills**<br>**4. AI-Driven Development Discussion**<br>**5. Futures / Roadmap** | Narrative walkthrough anchored to customer personas, CUJs, and a viable **TCO model** (no 'science projects'); calm, data-backed defense of trade-offs; disciplined time pacing & intellectual honesty; setup of **in-the-loop** and **outside-the-loop** GenAI harnesses where mistakes update agent instructions; phased GCP production roadmap. | [00](/concepts/00-fde-field-readiness-and-grading-rubric.md), [01](/concepts/01-ai-agent-quality-engineering.md), [11](/concepts/11-prototype-to-production.md), [13](/concepts/13-spec-driven-production-grade-development.md), [16](/concepts/16-the-new-sdlc-with-vibe-coding.md), [28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md), [31](/concepts/31-plan-change-management-for-gemini-enterprise-deployments.md) |",
        "| **Part B.1: AI/ML Engineering** | **1. Agentic & Multi-Agent Systems** (>=2)<br>**2. Retrieval & Data Engineering** (>=1)<br>**3. Model Selection, Tuning & Optimization** (>=2)<br>**4. LLM Ops & Evaluation** (>=1, > Judge alone)<br>**5. Domain-Applied AI/ML Expertise** (>=1) | Cognitive orchestration (`Sequential`, `Parallel`, `Loop`), Session + Memory Bank retention, bounded loops; hybrid RAG + ACL citations; Flash/Pro routing, thinking budgets, `response_schema`; Tri-Partite eval (deterministic + SME + calibrated autoraters) + OpenTelemetry tracing; HIPAA/FINRA/EU AI Act vertical compliance. | [01](/concepts/01-ai-agent-quality-engineering.md), [05](/concepts/05-enterprise-ai-agent-systems-google-cloud.md), [07](/concepts/07-enterprise-agent-skills.md), [08](/concepts/08-context-engineering-stateful-agents.md), [21](/concepts/21-build-and-deploy-multi-agent-adk-systems.md), [24](/concepts/24-agent-with-persistent-memories-deep-dive.md), [25](/concepts/25-evaluate-generative-agentic-systems.md), [26](/concepts/26-hill-climbing-agentic-systems.md), [27](/concepts/27-upgrade-to-the-latest-models.md) |",
        "| **Part B.2: Scoping & Documentation** | **1. Problem Definition** · **2. Technical Scope & Constraints** · **3. Stakeholder Alignment** · **4. System Design Artifacts** · **5. Decision Records (ADRs)** · **6. API Documentation** · **7. Operational Documentation** | CUJs & 'Definition of Done'; pre-build system boundaries; CoE RACI & phased delivery waves; Mermaid sequence/architecture diagrams; trade-off ADRs; OpenAPI / MCP schemas / A2A `AgentCard`; deployment & troubleshooting runbooks. | [03](/concepts/03-enterprise-ai-agent-protocol-stack.md), [04](/concepts/04-deploying-gemini-enterprise-agent-runtime.md), [13](/concepts/13-spec-driven-production-grade-development.md), [17](/concepts/17-agents-concepts-visually-explained.md), [18](/concepts/18-agent-tools-interoperability-with-mcp.md), [29](/concepts/29-deploy-the-gemini-enterprise-app.md), [31](/concepts/31-plan-change-management-for-gemini-enterprise-deployments.md) |",
        "| **Part B.3: Security, Privacy & Compliance** | **1. Authentication & Authorization** (>=2)<br>**2. Infrastructure & Network Security** (>=2)<br>**3. Data Protection & Privacy** (>=2)<br>**4. AI-Specific Security** (>=2)<br>**5. Compliance & Governance** (>=1) | Per-agent identities (`principal://`), WIF (SAML/OIDC + CEL), 3-legged OAuth (Auth Manager), PAB; VPC-SC, CAA, PSC-I, isolated `AgentSandbox`, Agent Gateway; CMEK, mTLS, Cloud DLP (SDP); **Model Armor** inline input + tool-output sanitization; dual-principal audit logs & data residency. | [02](/concepts/02-vibe-coding-agent-security-evaluation-kb.md), [10](/concepts/10-vibe-coding-agent-security-and-evaluation.md), [22](/concepts/22-build-enterprise-agents-with-code-execution.md), [29](/concepts/29-deploy-the-gemini-enterprise-app.md), [30](/concepts/30-third-party-idp-with-workforce-identity-federation.md), [33](/concepts/33-model-armor-securing-ai-deployments.md), [34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md), [35](/concepts/35-govern-agents-with-agent-gateway-registry-policies.md) |",
        "| **Part B.4: Reliability & Resilience** | **1. Availability Design** · **2. Observability** · **3. Failure & Recovery Testing** · **4. Graceful Degradation** | Semantic SLIs/SLOs & tool idempotency keys; structured JSON logs + OTel spans + Agent Quality Dashboard; red-teaming & persona simulation; circuit breakers, 3–5 min SSE timeouts, async polling, and HITL fallbacks. | [01](/concepts/01-ai-agent-quality-engineering.md), [05](/concepts/05-enterprise-ai-agent-systems-google-cloud.md), [12](/concepts/12-agent-quality.md), [25](/concepts/25-evaluate-generative-agentic-systems.md), [29](/concepts/29-deploy-the-gemini-enterprise-app.md), [32](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md) |",
        "| **Part B.5: Performance & Cost Optimization** | **1. Scalability & Elasticity** · **2. Resource Efficiency** · **3. AI Cost Management (FinOps)** | Stateless horizontal scaling & `ParallelAgent` fan-out; GSU Provisioned Throughput baseline + PAYG burst + Batch Inference (50% off); Context Caching (75–90% savings), Flash/Pro tiering, `tool_filter`, and session compaction. | [07](/concepts/07-enterprise-agent-skills.md), [08](/concepts/08-context-engineering-stateful-agents.md), [22](/concepts/22-build-enterprise-agents-with-code-execution.md), [24](/concepts/24-agent-with-persistent-memories-deep-dive.md), [28](/concepts/28-cost-estimation-and-optimization-for-agentic-solutions.md) |",
        "| **Part B.6: Operational Excellence** | **1. CI/CD & Deployment** · **2. Infrastructure as Code (IaC)** · **3. AI Lifecycle Management** · **4. Testing & Quality Engineering** | Automated evaluation gates + Shadow/Canary deployment rings (`< 5 min` rollback); Terraform & Cloud Build parity; version-stamped bundles (`GEAPL200_2026-09-30_124746`) & SxS experiment tracking; unit + contract + trajectory + load testing. | [04](/concepts/04-deploying-gemini-enterprise-agent-runtime.md), [11](/concepts/11-prototype-to-production.md), [25](/concepts/25-evaluate-generative-agentic-systems.md), [27](/concepts/27-upgrade-to-the-latest-models.md), [32](/concepts/32-plan-change-management-for-gemini-enterprise-agents.md) |",
        "| **Part B.7: Designing for Change** | **1. Modularity & Abstraction** · **2. Configuration Management** · **3. API Design & Versioning** · **4. Extensibility** | Model-agnostic aliases & swappable `SessionService`/`MemoryService`; externalized env configs & feature flags; backward-compatible MCP/A2A/OKF schemas; ADK lifecycle callbacks (`before_model`, `before_tool`, `after_agent`) & `SKILL.md` plugins. | [03](/concepts/03-enterprise-ai-agent-protocol-stack.md), [07](/concepts/07-enterprise-agent-skills.md), [14](/concepts/14-agent-skills.md), [18](/concepts/18-agent-tools-interoperability-with-mcp.md), [21](/concepts/21-build-and-deploy-multi-agent-adk-systems.md), [34](/concepts/34-secure-your-agents-with-gemini-enterprise-agent-platform.md) |",
        "",
        "---",
        "",
        "## Unified Concepts Catalog (`00`–`35`)",
        "",
        "### Governance Anchor (`00`)",
        f"- [`00` — {c00_meta['title']}](/concepts/00-fde-field-readiness-and-grading-rubric.md) — `#fde-grading-rubric` `#field-readiness` `#advisory-rigor` `#engineering-excellence`",
        "",
        "### Part I: Existing GCS Bucket Concepts (`01`–`20` — `GEAPL200` Merged with FDE Grading Rubric)"
    ]
    for e in bundle_entries[1:21]:
        tags = " ".join(f"`{t}`" for t in e["tags"][:5])
        idx_lines.append(f"- [{e['title']}](/{e['file']}) — {tags}")

    idx_lines.extend([
        "",
        "### Part II: Extended L300 Concepts (`21`–`35` — `GEAP L300` Synthesized with FDE Grading Rubric)"
    ])
    for e in bundle_entries[21:]:
        tags = " ".join(f"`{t}`" for t in e["tags"][:5])
        idx_lines.append(f"- [{e['title']}](/{e['file']}) — {tags}")

    idx_lines.extend([
        "",
        "---",
        "",
        "## Freshness, Provenance & Structural Inventory (180-Day TTL Preserved)",
        "",
        "| # | Concept | Tier | Mermaid | Tables | Figures | Status | Stale After |",
        "|---:|---|---|---:|---:|---:|---|---|"
    ])
    for doc, b_entry in zip(manifest_docs, bundle_entries):
        num = doc["document_number"]
        tier = "Rubric" if num == 0 else ("L200 (Bucket)" if num <= 20 else "L300 (Extended)")
        idx_lines.append(
            f"| {num:02d} | [{doc['title'][:68]}](/{b_entry['file']}) | {tier} | {doc['mermaid_diagrams']} | {doc['tables']} | {doc['images_retained']} | {b_entry['status']} | {b_entry['stale_after'][:10]} |"
        )
    idx_lines.append("")

    idx_content = "\n".join(idx_lines)
    with open(os.path.join(out_dir, "index.md"), "w", encoding="utf-8") as fh:
        fh.write(idx_content)
    with open(os.path.join(out_dir, "INDEX.md"), "w", encoding="utf-8") as fh:
        fh.write(idx_content)

    # ------------------------------------------------------------------
    # 6. Write Unified log.md (Preserving 2026-09-30 Entry + Recording Merge)
    # ------------------------------------------------------------------
    log_lines = [
        "---",
        f"type: {yq('Log')}",
        f"title: {yq('Change log')}",
        f"timestamp: {yq(BASE_TIMESTAMP)}",
        f"corpus: {yq(CORPUS)}",
        f"version_tag: {yq(VERSION_TAG)}",
        "---",
        "",
        "# Change log",
        "",
        "## 2026-10-26 (Unified L200 + L300 Extension & FDE Grading Rubric Enforcement)",
        "",
        f"- Merged the 20 existing concepts from `gs://{BUCKET_NAME}` (`{VERSION_TAG}`) with the 15 L300 concepts (`21-*.md` through `35-*.md`) and added the standalone mandatory governance specification `concepts/00-fde-field-readiness-and-grading-rubric.md` (36 concepts total).",
        f"- Preserved existing bundle `version_tag` (`{VERSION_TAG}`) and 180-day `stale_after` TTL semantics across all concepts.",
        f"- Embedded the enforceable Google Cloud FDE Grading Rubric (Part A: Presentation & Advisory Rigor, Part B: Engineering & Implementation Excellence, 0–3 scale, >= 2.0 Pass cutline, zero `0` disqualifier rule) and prevailing customer case studies anchored to `{FDE_G3DOC_URL}` across `index.md` and every individual concept (`00`–`35`).",
        f"- Generated 36 Dataplex / GCP Knowledge Catalog `okf` AspectType JSON payloads in `catalog-entries/`.",
        "",
        "## 2026-09-30",
        "",
        f"- Initial publication of bundle `{VERSION_TAG}`.",
        "- 20 concepts converted from Google Docs; 100 source figures processed into Mermaid diagrams, Markdown tables, or retained images.",
        "- Structural QA and CRC32C manifest recorded for every concept.",
        "- Published with `status: draft`. Diagrams are model reconstructions and have not yet had human review.",
        ""
    ]
    with open(os.path.join(out_dir, "log.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(log_lines))

    print(f"\nUnified OKF v0.2 Bundle Built Successfully in {out_dir}:")
    print(f"  Version Tag    : {VERSION_TAG} (preserved)")
    print(f"  Total Concepts : {len(manifest_docs)} (00: FDE Rubric, 01..20: L200 Bucket, 21..35: L300 Extended)")
    print(f"  Mermaid Graphs : {total_mermaid}")
    print(f"  GFM Tables     : {total_tables}")
    print(f"  Retained Imgs  : {total_images}")


if __name__ == "__main__":
    main()

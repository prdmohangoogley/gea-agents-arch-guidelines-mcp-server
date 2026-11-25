# Spec (e): Autonomous OKF Evolution Agent on Vertex AI Reasoning Engine (`okf-evolution-agent-reasoning-engine-spec.md`)

**Status:** ACTIVE (Authoritative Target Specification)  
**Target Repository:** [`https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server`](https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server)  
**Canonical Repo Path:** `docs/specs/okf-evolution-agent-reasoning-engine-spec.md` (mirrored at `specs/okf-evolution-agent-reasoning-engine-spec.md`)  
**Target GCP Project:** `fivedaysai-prd-sandbox-317383` (`301802433103`)  
**Target Cloud Region:** `us-central1`  
**Runtime Host:** Vertex AI Agent Engine (`reasoningEngines/<id>`) via Managed Python Runtime (Strictly No BYOC / Zero Cloud Run)  
**Governing Standard:** [`concepts/00-fde-field-readiness-and-grading-rubric.md`](../okf/concepts/00-fde-field-readiness-and-grading-rubric.md) · Concept 04 (Deploying to Agent Runtime) · Concept 27 (Model Upgrades & Drift) · Concept 32 (Agent Change Management) · Concept 35 (Agent Registry & Gateway)

---

## 1. Executive Summary & Core Mandate

This specification governs the architecture, packaging, Zero Ambient Authority (ZAA) security boundaries, and automated deployment of the **Autonomous OKF Evolution Agent** deployed natively as a **Vertex AI Reasoning Engine** (`reasoningEngines/<id>`).

### Strict Architectural Directive: Retirement of Cloud Run
1. **Managed Agent Engine Runtime (Zero BYOC):**
   The OKF Evolution Agent is implemented as a first-class managed Python Reasoning Engine. Vertex AI packages, isolates, scales, and executes the agent directly in Google Cloud's secure serverless Python runtime.
   - **Zero Cloud Run Containers:** Custom Dockerfiles, container registries (`Artifact Registry` container images), and Cloud Run services/jobs are strictly prohibited and retired for this agent.
   - **Zero Container Maintenance:** Security patch management, base image updates, and web server scaffolding (Gunicorn, Uvicorn, FastAPI) are handled natively by Vertex AI Agent Engine.
2. **Autonomous Triggering Topology:**
   The agent is invoked periodically (e.g., monthly cron `0 0 1 * *`) via **Google Cloud Scheduler** making authenticated gRPC/REST calls directly to the Vertex AI Reasoning Engine `query()` endpoint using downscoped OIDC identity, or on-demand from **Antigravity CLI** and **Gemini Enterprise Web App** via A2A protocol.
3. **Primary Grounding Source (Alexandria & Cloud FDE Charter):**
   Architectural drift discovery, rubric evolution, and pattern verification are strictly grounded against the **Google Cloud FDE Field-Readiness Charter & Architecture Index**:
   `https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`
   combined with official Google Cloud Alexandria reference designs and whitepapers.

---

## 2. End-to-End Architecture & Multi-Surface Topology

```mermaid
flowchart TB
    subgraph Triggers ["Evolution Trigger Surfaces"]
        Sched["Cloud Scheduler (Monthly Cron)<br/>0 0 1 * *<br/>OIDC Downscoped SA"]
        AGY["Antigravity CLI (agy)<br/>Skill: skill_okf_evolution_agent"]
        GEUI["Gemini Enterprise Web App<br/>A2A via Agent Gateway"]
    end

    subgraph AgentPlatform ["Google Cloud Vertex AI (us-central1)"]
        subgraph ReasoningRuntime ["Vertex AI Reasoning Engine (reasoningEngines/<id>)"]
            Agent["OKFEvolutionReasoningEngine<br/>• Managed Python Runtime (No BYOC / No Docker)<br/>• Socratic Drift & Evolution Loop<br/>• Turn-by-Turn Memory Bank"]
            
            subgraph SecurityLayer ["Security Perimeter"]
                MA_In["Model Armor Ingress Sanitizer<br/>(blocks adversarial injections in external docs)"]
                MA_Out["Model Armor Egress DLP<br/>(masks credentials, tokens, and PII)"]
            end
            
            subgraph EvolutionCore ["Reasoning Skills & Tools"]
                T_Fresh["Freshness Auditor<br/>(TTL & stale_after inspector)"]
                T_Search["Grounded Alexandria Engine<br/>(Grounded in FDE Charter Index)"]
                T_Draft["Socratic Concept Drafter<br/>(Layout-preserved diff synthesis)"]
                T_Sync["Cryptographic Sync Engine<br/>(SHA-256 / CRC32C Validator)"]
            end
        end
    end

    subgraph GroundingSources ["Authoritative Grounding Sources"]
        FDE["Cloud FDE Charter & Architecture Index<br/>https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head"]
        Alexandria["Alexandria Reference Blueprints<br/>& Verified Whitepapers"]
    end

    subgraph TargetStores ["Enterprise Knowledge Targets"]
        GCS[("GCS OKF v0.2 Bucket<br/>gs://fivedaysai-prd-sandbox-317383-okf")]
        Catalog[("Dataplex Knowledge Catalog<br/>geap-architecture-kb")]
        Spanner[("Cloud Spanner Graph<br/>arch_guidelines_graph")]
        BQ[("BigQuery Session Feedback<br/>session_feedback table")]
    end

    Sched -->|Direct query() gRPC| Agent
    AGY -->|Lightweight stdio Adapter| Agent
    GEUI -->|Agent Gateway A2A| Agent

    Agent --> MA_In
    MA_In --> T_Fresh
    T_Fresh --> T_Search
    T_Search <--> FDE
    T_Search <--> Alexandria
    T_Search --> T_Draft
    T_Draft --> MA_Out
    MA_Out --> T_Sync

    T_Sync --> GCS
    T_Sync --> Catalog
    T_Sync --> Spanner
    Agent -.->|OTLP Telemetry| BQ
```

---

## 3. Vertex AI Reasoning Engine Implementation

### 3.1 Reasoning Engine Agent Class (`src/agent/okf_evolution_reasoning_engine.py`)

The agent implements the standard Vertex AI Reasoning Engine contract:

```python
"""Authoritative Vertex AI Reasoning Engine implementation for OKF Autonomous Evolution."""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional
import vertexai
from vertexai.preview import reasoning_engines

from src.models.router import model_router
from src.security.model_armor import model_armor
from src.tools.evolution import (
    check_freshness_logic,
    propose_concept_evolution_logic,
)


class OKFEvolutionReasoningEngine:
    """First-Class Deployed Vertex AI Reasoning Engine agent for autonomous OKF knowledge evolution."""

    def __init__(
        self,
        project_id: str = "fivedaysai-prd-sandbox-317383",
        location: str = "us-central1",
        gcs_bucket: str = "fivedaysai-prd-sandbox-317383-okf",
        charter_index_url: str = "https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head",
    ):
        self.project_id = project_id
        self.location = location
        self.gcs_bucket = gcs_bucket
        self.charter_index_url = charter_index_url

    def set_up(self) -> None:
        """Initialize runtime clients, security perimeters, and model routers."""
        vertexai.init(project=self.project_id, location=self.location)

    def query(
        self,
        action: str = "audit_freshness",
        threshold_days: int = 30,
        concept_id: Optional[str] = None,
        update_summary: Optional[str] = None,
        new_findings: Optional[List[str]] = None,
        caller_identity: str = "cloud-scheduler",
    ) -> Dict[str, Any]:
        """Execute autonomous evolution reasoning loop."""
        start_time = time.perf_counter()

        if action == "audit_freshness":
            report = check_freshness_logic(threshold_days=threshold_days)
            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "status": "success",
                "action": "audit_freshness",
                "data": report,
                "latency_ms": round(elapsed, 2),
                "grounding_source": self.charter_index_url,
            }

        elif action in ("propose_evolution", "run_monthly_evolution"):
            # Step 1: Identify stale concepts if concept_id not provided
            target_id = concept_id
            if not target_id:
                freshness = check_freshness_logic(threshold_days=threshold_days)
                expiring = freshness.get("concepts", [])
                stale_list = [c for c in expiring if c.get("status") in ("EXPIRED", "EXPIRING_SOON")]
                if not stale_list:
                    return {
                        "status": "success",
                        "action": action,
                        "message": "All OKF concepts are currently fresh and compliant with FDE Charter.",
                        "freshness_index": freshness.get("freshness_index_percentage"),
                    }
                target_id = stale_list[0]["concept_file"].split("-")[0]

            # Step 2: Grounded research against FDE Charter and Alexandria
            findings = new_findings or [
                f"Grounded against Cloud FDE Charter index: {self.charter_index_url}",
                "Modernized runtime to Vertex AI Reasoning Engine (Zero Cloud Run).",
                "Applied Zero Ambient Authority downscoped token IAM perimeters.",
            ]

            # Step 3: Propose layout-preserved evolution
            summary = update_summary or "Scheduled monthly evolution cycle preserving layout and bumping TTL."
            proposal = propose_concept_evolution_logic(
                concept_id=target_id,
                update_summary=summary,
                new_architectural_findings=findings,
            )

            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "status": "success",
                "action": action,
                "data": proposal,
                "latency_ms": round(elapsed, 2),
                "grounding_source": self.charter_index_url,
            }

        else:
            return {
                "status": "error",
                "error": f"Unsupported evolution action: '{action}'. Supported: 'audit_freshness', 'propose_evolution', 'run_monthly_evolution'.",
            }
```

---

## 4. Zero Ambient Authority (ZAA) Downscoped IAM Perimeters

The agent runs with **Zero Ambient Authority**, using a dedicated downscoped Service Account.

### 4.1 Dedicated Service Account
```
okf-evolution-agent-sa@fivedaysai-prd-sandbox-317383.iam.gserviceaccount.com
```

### 4.2 Least-Privilege IAM Bindings
| Target Resource | IAM Role | Justification / Boundary |
| :--- | :--- | :--- |
| `projects/301802433103` | `roles/aiplatform.user` | Invokes Vertex AI modern foundation models (`gemini-3.1-pro`, `gemini-4-argon`) for drift synthesis. |
| `gs://fivedaysai-prd-sandbox-317383-okf/*` | `roles/storage.objectAdmin` | Read/write OKF concept bundles, SHA-256 manifests, and CRC32C digests. (No project-wide storage admin). |
| `arch_guidelines_graph` | `roles/spanner.databaseUser` | Read and update graph triples representing evolved architectural patterns. |
| `geap-architecture-kb` | `roles/datacatalog.tagEditor` | Update Dataplex Knowledge Catalog entry tags and schema descriptions. |
| `cloud-scheduler` | `roles/iam.serviceAccountTokenCreator` | Allows Cloud Scheduler to mint short-lived downscoped OIDC tokens for invocation. |

**Strict Disqualifier Enforcement:**
- Zero project-level `roles/owner` or `roles/editor`.
- Zero Cloud Run permissions (`roles/run.admin`, `roles/run.developer` explicitly omitted).
- Zero ambient service-to-service credential inheritance.

---

## 5. Grounding Engine Integration (Alexandria & FDE Charter)

### 5.1 FDE Charter Index Integration
In accordance with user directives, the agent's knowledge acquisition loop references:
- **Canonical Charter URL:** [`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head)
- **Evaluation Criteria:**
  - 26 FDE Sub-Competencies cutline ($\ge 2.0$).
  - Detection of 0-score disqualifiers (e.g., legacy models, ambient authority, missing DLP).
  - WAF 6-pillar alignment (Operational Excellence, Security, Reliability, Performance, Cost, Sustainability).

### 5.2 Retrieval & Synthesis Invariants
Every proposed concept revision MUST satisfy the following structural invariants:
1. **Version Tag Bumping:** Semantic version increment in YAML frontmatter (`version: "0.2.1"` or higher).
2. **TTL Reset:** `stale_after` RFC3339 timestamp reset to $now + 180\text{ days}$.
3. **Cryptographic SHA-256 Recalculation:** Emits validated SHA-256 digest over the entire markdown payload.
4. **Layout Preservation:** Zero disruption to indented bullet structures, Mermaid diagrams, or GitHub Flavored Markdown tables.
5. **Model Modernization:** Zero legacy model strings (`gemini-2.5-pro`, `gemini-2.0`, `gemini-1.5`, `gpt-3.5`, `claude-2`). Must strictly reference Gemini 3.1+ / Argon, GPT-5 / o3, or Claude 5.*.

---

## 6. Packaging & Deployment Pipeline (`scripts/deploy_okf_evolution_engine.py`)

Deployment is managed via Vertex AI Reasoning Engine SDK without Docker:

```python
"""Deploy OKF Evolution Agent to Vertex AI Reasoning Engine."""

import os
import vertexai
from vertexai.preview import reasoning_engines
from src.agent.okf_evolution_reasoning_engine import OKFEvolutionReasoningEngine

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "fivedaysai-prd-sandbox-317383")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
STAGING_BUCKET = f"gs://{PROJECT_ID}-reasoning-engine-staging"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

remote_engine = reasoning_engines.ReasoningEngine.create(
    OKFEvolutionReasoningEngine(
        project_id=PROJECT_ID,
        location=LOCATION,
        gcs_bucket=f"{PROJECT_ID}-okf",
        charter_index_url="https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head",
    ),
    requirements=[
        "google-cloud-spanner>=3.49.0",
        "google-cloud-bigquery>=3.25.0",
        "google-cloud-storage>=2.18.0",
        "google-cloud-aiplatform>=1.70.0",
        "opentelemetry-exporter-gcp-trace>=1.7.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
    ],
    display_name="OKF Autonomous Evolution Agent",
    description="Vertex AI Reasoning Engine agent for continuous OKF knowledge drift detection and GCS synchronization.",
)

print(f"OKF Evolution Agent deployed successfully: {remote_engine.resource_name}")
```

---

## 7. Dual-Surface Client Interfaces

### 7.1 Antigravity CLI / AGY SDK Invocation
Developers and autonomous coding agents invoke the agent locally via `skill_okf_evolution_agent` or through MCP:
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_okf_evolution_agent",
        "parameters": {
            "stale_threshold_days": 30,
            "auto_propose_evolution": True
        }
    }
)
```

### 7.2 Google Cloud Scheduler Invocations
Cloud Scheduler executes a monthly cron job targeting the Vertex AI Reasoning Engine gRPC endpoint with payload:
```json
{
  "action": "run_monthly_evolution",
  "threshold_days": 30,
  "caller_identity": "cloud-scheduler"
}
```

---

## 8. Verification Runbook & Argon Judge Trajectory Assertions

| Evaluation Metric | Target Threshold | Verification Method |
| :--- | :--- | :--- |
| **Runtime Target** | `reasoningEngines/*` | Inspect resource descriptor; confirm 0 Cloud Run services. |
| **Grounding Citation** | 100% Present | Assert output cites `https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`. |
| **Model Currency** | 100% Gemini 3.1+ | Zero legacy model references in generated proposals. |
| **Cryptographic Digest** | Exact Match | Verify SHA-256 of proposed markdown matches `calculated_content_sha256`. |
| **Argon Judge Score** | $3.00 / 3.00$ | Evaluated against FDE Part B.2 Quality Flywheel rubric. |

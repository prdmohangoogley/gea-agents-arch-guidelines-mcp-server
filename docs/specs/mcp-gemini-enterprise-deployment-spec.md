# Spec (c): First-Class Enterprise Agent Deployment & Gemini Enterprise Integration (`mcp-gemini-enterprise-deployment-spec.md`)

**Status:** ACTIVE (Target Specification)  
**Target Repository:** [`https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server`](https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server)  
**Canonical Repo Path:** `docs/specs/mcp-gemini-enterprise-deployment-spec.md` (mirrored at `specs/mcp-gemini-enterprise-deployment-spec.md`)  
**Target GCP Project:** `fivedaysai-prd-sandbox-317383` (`301802433103`)  
**Target Cloud Region:** `us-central1`  
**Runtime Host:** Vertex AI Agent Engine (`reasoningEngines/<id>`) via Managed Python Runtime (No BYOC / No Cloud Run)  
**Governing Standard:** [`concepts/00-fde-field-readiness-and-grading-rubric.md`](../okf/concepts/00-fde-field-readiness-and-grading-rubric.md) · Concept 04 (Deploying to Agent Runtime) · Concept 35 (Agent Registry & Gateway)

---

## 1. Executive Summary & Objective

This specification details the production deployment, registration, and end-to-end verification of the **First-Class Deployed Enterprise Architecture Agent** hosted natively on **Vertex AI Agent Engine (Reasoning Engine)** and registered in **Google Cloud Agent Registry**.

### Core Architectural Shift: Retirement of Cloud Run
- **Why Vertex AI Reasoning Engine:** Vertex AI Reasoning Engine is Google Cloud's managed Python agent runtime. It is **not** a BYOC (Bring Your Own Container) model. Vertex AI directly packages, secures, hosts, scales, and manages the Python execution environment (`reasoningEngines/<id>`) without requiring custom Dockerfiles, web servers, or container registries.
- **Retirement of Cloud Run:** Cloud Run container hosting, custom Dockerfiles, and monolithic runtime service accounts are deprecated and retired from this project.
- **Dual-Surface Invocation:**
  1. **Gemini Enterprise Web App:** Conversational access for enterprise architects via native integration with Vertex AI Agent Platform and Agent Registry.
  2. **Antigravity CLI / AGY SDK:** Connected via a lightweight client-side FastMCP stdio adapter (`src/mcp_adapter.py`) that proxies MCP tool calls to the remote Vertex AI Reasoning Engine using the developer's local ADC credentials.
- **Discrete Skill IAM Scoping:** Replaces monolithic ambient server permissions with per-skill least-privilege resource bindings.

---

## 2. End-to-End Architecture & Dual-Surface Topology

```mermaid
flowchart TB
    subgraph Dev ["Developer & Coding Agent Surface (Antigravity CLI)"]
        LocalDev["Antigravity CLI / AGY SDK<br/>• Local stdio Execution<br/>• Dynamic .agents/skills/ Loading<br/>• Developer ADC Identity"]
        MCPAdapter["Lightweight FastMCP Adapter (src/mcp_adapter.py)<br/>• Maps call_tool to reasoningEngines.query<br/>• Zero Container / Pure Python Bridge"]
        LocalDev --> MCPAdapter
    end

    subgraph Runtime ["Google Cloud Platform (us-central1)"]
        subgraph AgentEngine ["Vertex AI Agent Engine (First-Class Deployed Agent)"]
            RE["EnterpriseArchGuidelinesAgent (reasoningEngines/<id>)<br/>• Managed Python Application Runtime (No BYOC)<br/>• Socratic Reasoning Loop & KELE Questionnaire<br/>• Turn-by-Turn Sessions & Memory Bank (Concept 04)"]
            
            subgraph DiscreteSkills ["Skills Registry with Discrete Least-Privilege IAM"]
                S_Arch["skill-arch-design / search<br/>(Scope: Spanner Graph SELECT only)"]
                S_WAF["skill-waf-critique / rubric<br/>(Scope: BigQuery Rubrics SELECT only)"]
                S_IaC["skill-terraform-infra / spec<br/>(Scope: Pure In-Memory Generation, Zero DB)"]
                S_Cron["skill-okf-lro-cron<br/>(Scope: Dedicated Cloud Scheduler SA for GCS)"]
            end
            
            RE --> S_Arch
            RE --> S_WAF
            RE --> S_IaC
            RE --> S_Cron
        end

        Spanner[("Cloud Spanner Graph<br/>arch_guidelines_graph")]
        BQ[("Google BigQuery Analytics<br/>gea_arch_guidelines_analytics<br/>(session_feedback table)")]
        Trace["Google Cloud Trace<br/>(GoogleCloudTraceSpanExporter)"]
    end

    subgraph GE ["Gemini Enterprise & Agent Platform"]
        Reg["Google Cloud Agent Registry<br/>12 Skills Registered with A2A Agent Card"]
        Gate["Google Cloud Agent Gateway<br/>(Zero-Trust Policy Enforcement Point)"]
        UI["Gemini Enterprise Web App<br/>(Conversational UI for Architects)"]
    end

    MCPAdapter -->|Vertex AI API / gRPC query()| RE
    UI --> Gate
    Gate --> Reg
    Reg --> RE
    S_Arch --> Spanner
    S_WAF --> BQ
    RE -.-> Trace
    RE -.->|Stream Feedback| BQ
```

---

## 3. Deployment Artifacts & Implementation

### 3.1 Vertex AI Agent Engine Class (`src/agent/reasoning_engine.py`)
Implements the managed agent class following the Vertex AI Reasoning Engine contract:
```python
import vertexai
from vertexai.preview import reasoning_engines
from typing import Dict, Any, Optional

class EnterpriseArchGuidelinesAgent:
    """First-Class Deployed Agent powering architecture design and OKF adherence."""
    
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location

    def set_up(self):
        """Initializes Spanner Graph, BigQuery client, Model Armor, and Skills Registry."""
        from src.graph.client import GraphClient
        from src.registry.skills_registry import SkillsRegistry
        from src.security.model_armor import ModelArmorService
        
        self.graph_client = GraphClient(project_id=self.project_id)
        self.skills_registry = SkillsRegistry.get_instance()
        self.model_armor = ModelArmorService()

    def query(self, prompt: str, skill_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Agent reasoning loop: executes skills, applies Socratic grilling, and returns specs."""
        sanitized_prompt, blocked, reason = self.model_armor.sanitize_prompt(prompt)
        if blocked:
            return {"error": f"Security violation: {reason}", "status": "BLOCKED"}
        
        if skill_name:
            result = self.skills_registry.dispatch(skill_name, prompt=sanitized_prompt, **kwargs)
        else:
            result = self.skills_registry.execute_default_reasoning(sanitized_prompt, **kwargs)
            
        return result

    def stream_query(self, prompt: str, **kwargs):
        """Streams real-time token events and reasoning steps to clients."""
        # Yields token chunks for Gemini Web App and Antigravity streaming
        ...
```

### 3.2 Automated Deployment Pipeline (`pipelines/deploy_agent_engine.py`)
Deploys the agent to Vertex AI Reasoning Engines using the Google GenAI / Vertex AI SDK:
```python
import vertexai
from vertexai.preview import reasoning_engines
from src.agent.reasoning_engine import EnterpriseArchGuidelinesAgent

vertexai.init(project="fivedaysai-prd-sandbox-317383", location="us-central1")

remote_agent = reasoning_engines.ReasoningEngine.create(
    EnterpriseArchGuidelinesAgent(project_id="fivedaysai-prd-sandbox-317383", location="us-central1"),
    requirements=[
        "google-cloud-spanner>=3.49.0",
        "google-cloud-bigquery>=3.25.0",
        "google-cloud-aiplatform>=1.70.0",
        "opentelemetry-exporter-gcp-trace>=1.7.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
    ],
    display_name="Enterprise Architecture Guidelines Agent",
    description="Authoritative First-Class Agent for 24x7x365 architecture design, spec generation, and OKF reviews."
)
print(f"Deployed Agent Resource Name: {remote_agent.resource_name}")
```

### 3.3 Client-Side FastMCP Adapter for Antigravity (`src/mcp_adapter.py`)
Runs locally on developer machines over `stdio` without needing any cloud container:
```python
from fastmcp import FastMCP
import vertexai
from vertexai.preview import reasoning_engines

mcp = FastMCP("Enterprise Architecture Guidelines Agent")
remote_agent = reasoning_engines.ReasoningEngine("projects/301802433103/locations/us-central1/reasoningEngines/<id>")

@mcp.tool()
def search_guidelines(query: str, domain: str = "all") -> str:
    """Searches architecture guidelines via deployed Vertex AI Reasoning Engine."""
    response = remote_agent.query(prompt=query, skill_name="skill-arch-design", domain=domain)
    return str(response.get("result", response))

@mcp.tool()
def evaluate_design_tradeoffs(option_a: str, option_b: str, context: str) -> str:
    """Evaluates architectural trade-offs using Socratic grilling."""
    response = remote_agent.query(prompt=f"Compare {option_a} vs {option_b} in context {context}", skill_name="skill-waf-critique")
    return str(response.get("result", response))

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 3.4 Gemini Enterprise Publishing (`pipelines/publish_agent_registry.py`)
Publishes the agent and its 12 skills to Google Cloud Agent Registry using `agents-cli publish gemini-enterprise`.

---

## 4. Online OpenTelemetry Feedback & BigQuery Analytics Schema

In `gea_arch_guidelines_analytics.session_feedback`:
```sql
CREATE TABLE IF NOT EXISTS `fivedaysai-prd-sandbox-317383.gea_arch_guidelines_analytics.session_feedback` (
    session_id STRING NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    caller_identity STRING,
    client_surface STRING, -- 'antigravity_cli' | 'gemini_enterprise_app'
    skill_invoked STRING,
    prompt_tokens INT64,
    completion_tokens INT64,
    cached_tokens_saved INT64,
    user_rating INT64, -- 1 to 5
    user_critique STRING,
    spec_adherence_score FLOAT64,
    trace_id STRING
) PARTITION BY DATE(timestamp);
```

---

## 5. End-to-End Verification Runbook

1. **Antigravity CLI Verification:**
   - Execute `call_mcp_tool` targeting `search_guidelines` and `evaluate_design_tradeoffs`.
   - Verify prompt token consumption $< 600$ tokens in Tier 1 disclosure.
2. **Gemini Enterprise Web App Verification:**
   - Open Gemini Enterprise console $\rightarrow$ Agent Registration Picker $\rightarrow$ select `Enterprise Architecture Guidelines Agent`.
   - Issue prompt: *"Draft an enterprise architecture specification for a cross-region payment gateway with Zero Ambient Authority."*
   - Verify that output conforms to OKF Concepts 02, 34, 45, and emits an ADR.
   - Verify feedback rating is ingested into BigQuery `session_feedback`.

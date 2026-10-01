# Enterprise Agents Architectural Guidelines MCP Server

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-0.4.1%2B-brightgreen.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-Internal-green.svg)]()

> A production-grade **Model Context Protocol (MCP)** server providing structured, graph-backed architectural guidelines, design patterns, and tradeoff analyses for building enterprise AI agents on Google Cloud.

---

## 🏛️ System Architecture

```mermaid
graph TD
    subgraph DataIngestion["1. Knowledge Ingestion & Graph Creation"]
        MD["Markdown Architectural Corpus (GEAPL200)"]
        GCS["GCS Bucket (Raw Knowledge Corpus)"]
        NL2KG["NL2KG Triplification Pipeline (`pipelines/`)"]
    end

    subgraph Storage["2. Cloud Graph & Analytics Store"]
        SPANNER["Cloud Spanner Graph (`ArchGuidelinesGraph`)"]
        BQ["BigQuery (`guideline_embeddings` & audit logs)"]
    end

    subgraph Server["3. FastMCP Application (`src/`)"]
        FASTMCP["FastMCP Engine"]
        TOOLS["Tools: search_guidelines, evaluate_tradeoffs"]
        RESOURCES["Resources: server_info, catalog"]
    end

    subgraph Consumers["4. Agent & Developer Clients"]
        AGY["Antigravity Pair Programming Agent"]
        IDE["VS Code / Claude Desktop / Cursor"]
        CLOUDRUN["Cloud Run (SSE Mode)"]
    end

    MD --> GCS
    GCS --> NL2KG
    NL2KG --> SPANNER
    NL2KG --> BQ

    SPANNER --> FASTMCP
    BQ --> FASTMCP
    FASTMCP --> TOOLS
    FASTMCP --> RESOURCES

    TOOLS --> AGY
    TOOLS --> IDE
    FASTMCP --> CLOUDRUN
```

---

## 🌐 Knowledge Graph Visualization (Cloud Spanner Graph)

> **Live Property Graph:** `ArchGuidelinesGraph` in Cloud Spanner database `arch_guidelines_graph`  
> **Topology:** 38 Guidelines · 110 Architectural Patterns · 1 Antipattern · 138 Directed Relationships

An interactive force-directed graph visualizer with live search, node inspection, and physics simulation is available at [`visualizations/spanner_knowledge_graph.html`](visualizations/spanner_knowledge_graph.html).

To view the interactive graph in your default browser:
```bash
open visualizations/spanner_knowledge_graph.html
```

### Property Graph Schema

```mermaid
classDiagram
    direction LR

    class Guideline {
        +STRING guideline_id [KEY]
        +STRING title
        +STRING category
        +STRING summary
        +STRING source_url
    }

    class Pattern {
        +STRING pattern_id [KEY]
        +STRING name
        +STRING category
        +STRING description
    }

    class Antipattern {
        +STRING antipattern_id [KEY]
        +STRING name
        +STRING hazard
        +STRING remedy
    }

    Guideline --> Pattern : IMPLEMENTS (source_id -> target_id)
    Pattern --> Antipattern : MITIGATES (pattern_id -> antipattern_id)
```

### Core Architectural Clusters in Spanner Graph

#### 1. Context Engineering & Memory Architecture
```mermaid
graph LR
    G_CTX["08-context-engineering-stateful-agents"]:::guideline

    P_MEM["Multi-Model Memory Storage"]:::pattern
    P_TRIG["Asynchronous Memory Triggering"]:::pattern
    P_RAG["Separated RAG & Memory Tiers"]:::pattern
    P_GW["Secure Memory Gateway"]:::pattern

    G_CTX -->|IMPLEMENTS| P_MEM
    G_CTX -->|IMPLEMENTS| P_TRIG
    G_CTX -->|IMPLEMENTS| P_RAG
    G_CTX -->|IMPLEMENTS| P_GW

    classDef guideline fill:#1f6feb,stroke:#58a6ff,stroke-width:2px,color:#fff;
    classDef pattern fill:#8957e5,stroke:#d2a8ff,stroke-width:2px,color:#fff;
```

#### 2. Security & Zero Ambient Authority (ZAA)
```mermaid
graph LR
    G_SEC["02-vibe-coding-agent-security"]:::guideline

    P_JIT["JIT Downscoped Credentials"]:::pattern
    P_BOX["Ephemeral Sandboxed Execution"]:::pattern
    P_SLOP["Anti-Slopsquatting Supply Chain"]:::pattern
    P_MFA["Vibe Diff with Hardware MFA"]:::pattern
    P_CB["Stateful Circuit Breaker"]:::pattern

    G_SEC -->|IMPLEMENTS| P_JIT
    G_SEC -->|IMPLEMENTS| P_BOX
    G_SEC -->|IMPLEMENTS| P_SLOP
    G_SEC -->|IMPLEMENTS| P_MFA
    G_SEC -->|IMPLEMENTS| P_CB

    classDef guideline fill:#1f6feb,stroke:#58a6ff,stroke-width:2px,color:#fff;
    classDef pattern fill:#8957e5,stroke:#d2a8ff,stroke-width:2px,color:#fff;
```

#### 3. Agent Quality Engineering & Evaluation Gates
```mermaid
graph LR
    G_QA["01-ai-agent-quality-engineering"]:::guideline

    P_TRJ["Glass Box Trajectory Assertion"]:::pattern
    P_MET["Black Box Metric Selection"]:::pattern
    P_GATE["Quality Scorecard Release Gate"]:::pattern
    P_EVAL["Evaluatable-by-Design Instrumentation"]:::pattern

    G_QA -->|IMPLEMENTS| P_TRJ
    G_QA -->|IMPLEMENTS| P_MET
    G_QA -->|IMPLEMENTS| P_GATE
    G_QA -->|IMPLEMENTS| P_EVAL

    classDef guideline fill:#1f6feb,stroke:#58a6ff,stroke-width:2px,color:#fff;
    classDef pattern fill:#8957e5,stroke:#d2a8ff,stroke-width:2px,color:#fff;
```

---

## 📂 Repository Layout

```markdown
├── .agents/                    # 🚀 Antigravity Internal Rules & Skills
│   ├── rules/                 # Always-active guidelines for THIS repo
│   │   ├── 01-architecture-guidelines.md
│   │   ├── 02-code-standards.md
│   │   └── 03-security-rules.md
│   └── skills/                # Reusable developer skills
│       ├── nl2kg-triplification/
│       ├── fastmcp-tool-dev/
│       └── eval-harness/
├── docs/                       # 📖 Specs & Validation Plans
│   ├── architecture.md
│   ├── specs/
│   │   ├── mcp-server-spec.md
│   │   ├── nl2kg-pipeline-spec.md
│   │   ├── repo-scaffolding.md
│   │   └── spanner-graph-schema.md
│   └── validation/
│       └── validation-plan.md
├── iac/                        # 🏗️ Infrastructure as Code (Terraform)
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars.example
│   └── modules/               # Reusable modules
│       ├── spanner/           # Spanner instance + Graph DDL
│       ├── bq/                # BigQuery datasets and tables
│       └── gcs/               # GCS storage bucket
├── pipelines/                  # 🧠 NL2KG Triplification Pipeline
│   ├── __init__.py
│   ├── config.py
│   ├── extract.py
│   ├── loader.py
│   ├── main.py
│   ├── schema.py
│   └── triplify.py
├── src/                        # 🔌 FastMCP Server Application
│   ├── __init__.py
│   ├── config.py
│   ├── server.py
│   ├── graph/                 # Graph clients & GQL queries
│   │   ├── client.py
│   │   └── queries.py
│   ├── models/                # Domain models & Pydantic schemas
│   │   └── guideline.py
│   └── tools/                 # FastMCP tool & resource definitions
│       ├── guidelines.py
│       ├── health.py
│       └── patterns.py
├── tests/                      # 📊 Evaluation Harness
│   ├── conftest.py
│   ├── test_pipeline.py
│   ├── test_server.py
│   └── evals/                 # Retrieval quality benchmarks
│       ├── golden_dataset.json
│       └── test_retrieval_quality.py
├── Dockerfile                  # Containerization
└── pyproject.toml              # Dependencies (UV)
```

---

## ⚡ Quickstart

### 1. Installation (UV)
```bash
# Clone the repository
git clone <repo-url>
cd gea-agents-arch-guidelines-mcp-server

# Install dependencies using uv
uv sync
```

### 2. Run FastMCP Server Locally (stdio mode)
For local IDE clients (e.g. Antigravity, Claude Desktop, Cursor):
```bash
uv run gea-mcp-server --transport stdio
```

### 3. Run FastMCP Server via SSE (HTTP mode)
For remote or Docker/Cloud Run hosting:
```bash
uv run gea-mcp-server --transport sse --port 8080 --host 0.0.0.0
```
Verify health:
```bash
curl http://localhost:8080/health
```

### 4. Run NL2KG Triplification Pipeline
```bash
# Extract entities & relationships from documentation
uv run nl2kg-pipeline extract --source-dir docs/specs

# Validate extracted triples
uv run nl2kg-pipeline validate --input-file build/graph/triples.json
```

### 5. Run Tests & Evaluation Benchmarks
```bash
# Run unit tests
uv run pytest tests/test_server.py tests/test_pipeline.py

# Run retrieval quality evaluation against golden benchmark
uv run pytest tests/evals/test_retrieval_quality.py -v
```

---

## 🛠️ Infrastructure as Code (Terraform)
Deploy the Cloud Spanner Graph, BigQuery dataset, and GCS bucket:
```bash
cd iac
cp terraform.tfvars.example terraform.tfvars
# Update terraform.tfvars with your GCP project ID
terraform init
terraform plan
terraform apply
```

---

## 🐳 Docker Containerization
```bash
# Build container image
docker build -t gea-mcp-server:latest .

# Run container locally
docker run -p 8080:8080 gea-mcp-server:latest
```

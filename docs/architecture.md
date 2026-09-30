# Enterprise Agents Architectural Guidelines MCP Server — Architecture

## 1. Executive Summary
The Enterprise Agents Architectural Guidelines MCP Server (`gea-agents-arch-guidelines-mcp-server`) provides AI agents and enterprise developers with structured, verified knowledge on designing, securing, and deploying enterprise-grade agents on Google Cloud.

## 2. High-Level Architecture

```mermaid
graph TD
    subgraph KnowledgeSources["1. Knowledge Ingestion"]
        KD["Markdown Knowledge Base (GEAPL200)"]
        GCS_RAW["GCS Bucket (Raw Specs & Guidelines)"]
    end

    subgraph Pipeline["2. NL2KG Pipeline"]
        EXT["Entity & Relation Extractor"]
        TRIP["Triplification Engine"]
        VAL["Schema & Ontology Validator"]
    end

    subgraph Storage["3. Cloud Data Store"]
        SPANNER["Cloud Spanner Graph (Property Graph GQL)"]
        BQ["BigQuery (Vector Embeddings & Analytics)"]
    end

    subgraph Server["4. FastMCP Server Application"]
        FASTMCP["FastMCP Engine"]
        TOOLS["Tools: search_guidelines, evaluate_tradeoffs, etc."]
        RESOURCES["Resources: schema, catalog"]
    end

    subgraph Clients["5. MCP Clients"]
        AGENT_AGY["Antigravity Agent"]
        AGENT_IDE["VS Code / Cursor / Claude Desktop"]
        CLOUD_RUN["Cloud Run Deployment (SSE)"]
    end

    KD --> GCS_RAW
    GCS_RAW --> EXT
    EXT --> TRIP
    TRIP --> VAL
    VAL --> SPANNER
    VAL --> BQ

    SPANNER --> FASTMCP
    BQ --> FASTMCP
    FASTMCP --> TOOLS
    FASTMCP --> RESOURCES

    TOOLS --> AGENT_AGY
    TOOLS --> AGENT_IDE
    FASTMCP --> CLOUD_RUN
```

## 3. Key Components
1. **NL2KG Triplification Pipeline (`pipelines/`)**:
   - Parses unstructured architectural text and produces typed graph triples (Nodes and Edges).
2. **Infrastructure as Code (`iac/`)**:
   - Terraform modules for Cloud Spanner with Graph DDL, BigQuery datasets, and GCS buckets.
3. **FastMCP Server (`src/`)**:
   - Asynchronous Python application exposing FastMCP tools with dual stdio / SSE transport.
4. **Evaluation Harness (`tests/`)**:
   - Golden dataset and pytest suites evaluating retrieval quality, latency, and schema correctness.

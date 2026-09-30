---
name: nl2kg-triplification
description: >-
  Extracts entities, concepts, and relationships from natural language architectural documents
  and generates knowledge graph triples for ingestion into Cloud Spanner Graph and BigQuery.
  Use when processing new markdown architecture guidelines, validating graph ontology schemas,
  or testing the NL2KG triplification pipeline.
---

# NL2KG Triplification Skill

This skill guides the extraction and conversion of unstructured architectural markdown documentation into typed Knowledge Graph triples formatted for Cloud Spanner Graph and BigQuery.

## Workflow

1. **Document Ingestion**:
   - Place source markdown documents into `docs/` or source bucket.
   - Run document parsing:
     ```bash
     python -m pipelines.main extract --source docs/specs/
     ```

2. **Entity & Relationship Extraction**:
   - Extract nodes: `Guideline`, `Pattern`, `Tradeoff`, `Component`, `Antipattern`.
   - Extract edges: `RELATES_TO`, `IMPLEMENTS`, `MITIGATES`, `REQUIRES`, `TRADES_OFF`.
   - Validate triples against `pipelines/schema.py`:
     ```bash
     python -m pipelines.main validate --input extracted_triples.json
     ```

3. **Spanner Graph Loader**:
   - Load validated nodes and edges into Cloud Spanner Graph:
     ```bash
     python -m pipelines.main load --target spanner --instance spanner-instance --database arch-guidelines-graph
     ```

4. **Verification**:
   - Query Spanner Graph using GQL to verify graph density and connectivity:
     ```sql
     GRAPH ArchGuidelinesGraph
     MATCH (p:Pattern)-[r:MITIGATES]->(a:Antipattern)
     RETURN p.name, a.name;
     ```

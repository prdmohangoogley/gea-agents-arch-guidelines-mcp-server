# AGY Goal: Phase 3 - NL2KG Triplification Pipeline Implementation

## 📌 Context
We have provisioned the Dual-Binding Fabric (Spanner + BigQuery). Now we must build the pipeline that converts the OKF (Open Knowledge Format) Data Lake in GCS into Structured Graph Triples (NL2KG).

---

## 🛠️ Tasks
1. Implement `pipelines/nl2kg_pipeline.py` in Python using the **Gemini API**.
2. **Layout Preservation:** Ensure the pipeline converts documents to layout-preserved Markdown (preserving indentation and lists) to retain semantic relationships.
3. **Pydantic Hardening:** Use Pydantic models to constrain the Gemini output to a valid `Graph` JSON schema (Nodes and Edges) matching the ontology.
4. **Referential Integrity (Placeholder Resolution):** Implement logic to ensure dangling edges do not crash ingestion; create placeholder nodes if an entity was referenced but not explicitly defined in the document.
5. **Batch Hydration:** Insert data in batches of 50 (to prevent API timeout) into **Spanner Graph** as the Primary Store and federate to **BigQuery**.
6. **Incremental Synchronization:** Use file checksums or `last_modified` tags from GCS to ensure only changed OKF docs are re-triplified (Zero-Duplicate writes).

## ✅ Acceptance Criteria
- Running the pipeline extracts valid `Subject -> Predicate -> Object` relationships from GCS.
- Data appears in Spanner Graph and BigQuery without duplicating existing nodes.

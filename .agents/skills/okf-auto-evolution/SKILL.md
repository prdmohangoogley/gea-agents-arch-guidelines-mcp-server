---
name: okf-auto-evolution
description: >-
  Monitors, updates, and evolves the OKF v0.2 Enterprise Architecture Guidelines corpus.
  Hosted natively on Vertex AI Reasoning Engine (Zero Cloud Run). Discovers outdated concepts
  grounded in the Cloud FDE Charter (https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head),
  drafts backward-compatible revisions, and synchronizes changes to GCS and Knowledge Catalog.
---

# OKF Autonomous Evolution Skill

This skill allows Antigravity agents and enterprise architects to maintain the 58-concept OKF corpus in an evergreen state, deployed natively on **Vertex AI Reasoning Engine** (No BYOC / Zero Cloud Run) and grounded in the [Google Cloud FDE Field-Readiness Charter & Architecture Index](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).

## Operational Workflow

1. **Check Corpus Freshness**:
   Invoke the MCP tool to identify concepts with `stale_after` expiring in <= 30 days:
   ```bash
   call_mcp_tool(ServerName="arch-guidelines", ToolName="check_okf_freshness", Arguments={"threshold_days": 30})
   ```

2. **Grounded Architectural Research**:
   For flagged concepts, search for recent Google Cloud architectural patterns:
   ```bash
   call_mcp_tool(ServerName="arch-guidelines", ToolName="search_recent_architectural_updates", Arguments={"topic": "Google Cloud Model Armor new filters 2026"})
   ```

3. **Draft Concept Revision**:
   Draft the updated concept adhering strictly to OKF v0.2 formatting rules:
   - Must preserve all Mermaid diagrams and GFM tables.
   - Must maintain `## FDE Project Grading Rubric Enforcement` section.
   - Must calculate `content_sha256`.

4. **Synchronize & Verify**:
   Execute `scripts/update_okf_gcs.sh` and verify CRC32C digests across all 124 bucket objects.

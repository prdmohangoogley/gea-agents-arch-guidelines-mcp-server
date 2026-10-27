---
name: fde-governance-auditor
description: >-
  Audits agent projects, MCP servers, and multi-agent systems against the Google Cloud FDE
  Field-Readiness & Project Grading Rubric (https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).
  Evaluates architectures against the 26 sub-competencies, enforces the >= 2.0 cutline, detects 0-score
  disqualifiers, and produces prioritized remediation roadmaps.
---

# FDE Governance Auditor Skill

This skill guides Antigravity agents in evaluating and grading customer AI agent projects against the Google Cloud FDE Charter.

## Pre-Flight Evaluation Protocol

1. **Query FDE Standards**:
   Retrieve the rubric requirements for the target domain:
   ```bash
   call_mcp_tool(ServerName="arch-guidelines", ToolName="query_fde_charter_best_practices", Arguments={"domain": "Part B.3: Security & Identity"})
   ```

2. **Execute Full Project Audit**:
   Pass the project architecture summary or repository manifest to the auditor tool:
   ```bash
   call_mcp_tool(ServerName="arch-guidelines", ToolName="audit_project_against_fde_rubric", Arguments={"project_manifest_or_description": "<project summary>"})
   ```

3. **Verify Pass / Pause Cutlines**:
   - **Composite Score >= 2.0**: Ready for production deployment.
   - **Any 0-Score Sub-Competency**: **IMMEDIATE PAUSE**. Flag critical disqualifier (e.g., hardcoded API keys, unauthenticated endpoints, missing evals) and generate remediation tasks before proceeding.

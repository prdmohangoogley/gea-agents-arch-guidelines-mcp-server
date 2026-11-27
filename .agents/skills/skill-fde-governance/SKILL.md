---
name: skill-fde-governance
description: Audits project architectures against the Google Cloud FDE Rubric, enforcing the >= 2.0 cutline.
---

# FDE Field-Readiness Auditor

**MCP Skill ID:** `skill-fde-governance`  
**Category:** `governance`  
**Capabilities:** `rubric_grading`, `disqualifier_detection`, `remediation_roadmap`

## Purpose

Audits project architectures against the Google Cloud FDE Rubric, enforcing the >= 2.0 cutline.

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill-fde-governance")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill-fde-governance", parameters={...})`.

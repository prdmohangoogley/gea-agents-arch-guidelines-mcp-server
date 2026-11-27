---
name: skill_waf_pillar_critique
description: Executes a deep-dive evaluation focused on a single GCP Well-Architected Framework pillar grounded in OKF-PCA-01..09.
---

# WAF Pillar Deep Dive Auditor

**MCP Skill ID:** `skill_waf_pillar_critique`  
**Category:** `governance`  
**Capabilities:** `pillar_deep_dive`, `compliance_check`, `targeted_remediation`, `okf_pca_grounding`

## Purpose

Executes a deep-dive evaluation focused on a single GCP Well-Architected Framework pillar grounded in OKF-PCA-01..09.

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill_waf_pillar_critique")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill_waf_pillar_critique", parameters={...})`.

---
name: skill-okf-evolution
description: Audits concept staleness, discovers recent GCP updates via search, and drafts backward-compatible evolutions.
---

# Autonomous OKF Evolution Maintainer

**MCP Skill ID:** `skill-okf-evolution`  
**Category:** `knowledge_management`  
**Capabilities:** `freshness_audit`, `grounded_search`, `concept_drafting`, `sha256_verification`

## Purpose

Audits concept staleness, discovers recent GCP updates via search, and drafts backward-compatible evolutions.

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill-okf-evolution")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill-okf-evolution", parameters={...})`.

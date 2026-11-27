---
name: skill-security-auditor
description: Audits zero ambient authority, Model Armor dual-pass sanitization, and PAB perimeters.
---

# Zero Ambient Authority & Model Armor Auditor

**MCP Skill ID:** `skill-security-auditor`  
**Category:** `security`  
**Capabilities:** `security_audit`, `model_armor_verification`, `pab_boundary_check`

## Purpose

Audits zero ambient authority, Model Armor dual-pass sanitization, and PAB perimeters.

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill-security-auditor")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill-security-auditor", parameters={...})`.

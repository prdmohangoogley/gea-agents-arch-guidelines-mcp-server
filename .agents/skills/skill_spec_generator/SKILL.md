---
name: skill_spec_generator
description: Generates production engineering specifications with ADRs, sequence diagrams, and threat models.
---

# Architectural Spec Generator

**MCP Skill ID:** `skill_spec_generator`  
**Category:** `architecture`  
**Capabilities:** `spec_drafting`, `adr_generation`, `threat_modeling`, `api_schema_specification`

## Purpose

Generates production engineering specifications with ADRs, sequence diagrams, and threat models.

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill_spec_generator")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill_spec_generator", parameters={...})`.

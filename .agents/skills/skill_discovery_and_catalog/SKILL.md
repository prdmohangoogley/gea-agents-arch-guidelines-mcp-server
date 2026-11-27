---
name: skill_discovery_and_catalog
description: Dynamically discovers, catalogs, and inspects agent skills across workspaces, .agents/skills/, and python plugins.
---

# Dynamic Skills Discovery & Catalog Engine

**MCP Skill ID:** `skill_discovery_and_catalog`  
**Category:** `knowledge_management`  
**Capabilities:** `skills_discovery`, `catalog_query`, `capability_matching`, `progressive_disclosure`

## Purpose

Dynamically discovers, catalogs, and inspects agent skills across workspaces, .agents/skills/, and python plugins.

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill_discovery_and_catalog")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill_discovery_and_catalog", parameters={...})`.

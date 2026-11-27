---
name: skill-arch-eval
description: Evaluates agent system designs against Google Cloud architectural best practices and GQL patterns.
---

# Architecture Guidelines Evaluator

**MCP Skill ID:** `skill-arch-eval`  
**Category:** `architecture`  
**Capabilities:** `architecture_audit`, `spanner_graph_query`, `tradeoff_evaluation`

## Purpose

Evaluates agent system designs against Google Cloud architectural best practices and GQL patterns.

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill-arch-eval")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill-arch-eval", parameters={...})`.

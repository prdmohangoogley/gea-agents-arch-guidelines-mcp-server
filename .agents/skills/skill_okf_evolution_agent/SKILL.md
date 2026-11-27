---
name: skill_okf_evolution_agent
description: Autonomous monthly maintenance agent running on Vertex AI Reasoning Engine auditing concept TTL, detecting hash drift, and generating backward-compatible evolutions grounded in Cloud FDE Charter (https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).
---

# Monthly OKF Evolution Agent

**MCP Skill ID:** `skill_okf_evolution_agent`  
**Category:** `knowledge_management`  
**Capabilities:** `freshness_audit`, `drift_detection`, `automated_evolution`, `pr_generation`, `vertex_ai_reasoning_engine`

## Purpose

Autonomous monthly maintenance agent running on Vertex AI Reasoning Engine auditing concept TTL, detecting hash drift, and generating backward-compatible evolutions grounded in Cloud FDE Charter (https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill_okf_evolution_agent")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill_okf_evolution_agent", parameters={...})`.

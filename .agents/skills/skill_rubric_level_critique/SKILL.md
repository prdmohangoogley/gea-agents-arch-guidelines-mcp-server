---
name: skill_rubric_level_critique
description: Evaluates architectures against specific sub-competencies in the Google Cloud FDE Rubric, strictly enforcing the >= 2.0 cutline.
---

# FDE Rubric Sub-Competency Grader

**MCP Skill ID:** `skill_rubric_level_critique`  
**Category:** `governance`  
**Capabilities:** `rubric_grading`, `subcompetency_critique`, `disqualifier_detection`

## Purpose

Evaluates architectures against specific sub-competencies in the Google Cloud FDE Rubric, strictly enforcing the >= 2.0 cutline.

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill_rubric_level_critique")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill_rubric_level_critique", parameters={...})`.

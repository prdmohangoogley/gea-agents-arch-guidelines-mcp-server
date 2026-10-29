---
name: spec-creation-workflow
description: >-
  Orchestrates the 5-stage specification development lifecycle (RFC -> ADR Review ->
  Implementation Draft -> Threat Model -> Sign-off) with ARB gating checks.
---

# Specification Creation Workflow Skill

Use this skill to guide architectural specs through formal Google ARB stage gates.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_spec_creation_workflow",
        "parameters": {
            "spec_title": "<spec title>",
            "current_stage": "rfc",
            "stage_payload": "<rfc content>"
        }
    }
)
```

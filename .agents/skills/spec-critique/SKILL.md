---
name: spec-critique
description: >-
  Provides ruthless Socratic critique, anti-pattern detection, failure mode analysis,
  and edge-case grilling for technical specifications.
---

# Architectural Spec Critique Skill

Use this skill when you want an adversarial review of a spec before committing to implementation.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_spec_critique",
        "parameters": {
            "spec_text": "<specification markdown>",
            "critique_perspective": "comprehensive_lead_architect"
        }
    }
)
```

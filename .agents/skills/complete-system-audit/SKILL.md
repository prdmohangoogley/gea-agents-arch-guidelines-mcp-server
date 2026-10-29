---
name: complete-system-audit
description: >-
  Executes an exhaustive 360-degree audit across WAF, FDE 26-subcompetencies, and Model Armor
  security perimeters, producing an authoritative scorecard.
---

# Complete System Audit Skill

Use this skill when preparing an agent system or MCP server for production release review.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_complete_system_audit",
        "parameters": {
            "project_name": "<project name>",
            "full_system_spec_or_code_manifest": "<manifest or architecture description>"
        }
    }
)
```

---
name: codebase-to-spec-collection
description: >-
  Inspects an existing codebase, repository, or project and synthesizes a complete, 6-part
  modular specification collection applying all enterprise best practices.
---

# Codebase to Spec Collection Generator Skill

Use this skill when auditing or reverse-engineering an entire codebase or project into authoritative specifications.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_codebase_to_spec_collection",
        "parameters": {
            "project_name": "<project name>",
            "codebase_summary_or_path": "<codebase structure, source file list, and interfaces>",
            "enforce_fde_cutline": True
        }
    }
)
```

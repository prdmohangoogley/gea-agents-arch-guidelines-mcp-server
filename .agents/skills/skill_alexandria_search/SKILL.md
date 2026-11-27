---
name: skill_alexandria_search
description: >-
  Searches Google Cloud verified architectural reference designs, Alexandria blueprints,
  and enterprise whitepapers grounded in the Cloud FDE Charter (https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).
---

# Alexandria Best Practices Search Skill

Use this skill when looking for verified Google Cloud blueprints, enterprise architecture standards, and field-tested reference designs grounded in the [Google Cloud FDE Field-Readiness Charter & Architecture Index](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_alexandria_search",
        "parameters": {
            "query": "<architectural topic or GCP service>",
            "domain": "security",
            "top_k": 5
        }
    }
)
```

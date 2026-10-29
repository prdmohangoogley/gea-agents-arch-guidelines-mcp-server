---
name: waf-critique
description: >-
  Audits system architectures against all 6 GCP Well-Architected Framework pillars,
  providing quantitative scoring, high/medium risk issues, and remediation diffs.
---

# Well-Architected Framework (WAF) Critique Skill

Use this skill to audit workloads against Google Cloud's 6 Well-Architected pillars.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_critique",
        "parameters": {
            "architecture_description": "<markdown architecture>",
            "workload_type": "multi_agent_system"
        }
    }
)
```

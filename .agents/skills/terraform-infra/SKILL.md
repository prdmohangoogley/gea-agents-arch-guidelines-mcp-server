---
name: terraform-infra
description: >-
  Generates, audits, and hardens Terraform HCL for Cloud Spanner Graph, Vertex AI, BigQuery,
  and IAM service accounts enforcing least-privilege standards.
---

# Terraform Infrastructure Skill

Use this skill to synthesize or audit Terraform HCL for multi-agent infrastructure.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_terraform_infra",
        "parameters": {
            "action": "generate",
            "infrastructure_requirements": "Cloud Spanner instance with graph database and Vertex AI Reasoning Engine binding"
        }
    }
)
```

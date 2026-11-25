---
name: terraform-waf-verifier
description: >-
  Verifies an existing or current Terraform HCL script (.tf) against the Google Cloud
  Well-Architected Framework (Dataplex OKF Concepts OKF-PCA-01 through OKF-PCA-09),
  detecting where the Terraform configuration departs from WAF across all 6 pillars
  and performing a detailed architectural critique with remediated HCL.
---

# Terraform Well-Architected Drift Verifier & Critique Skill

Use this skill to inspect an existing or current Terraform HCL script, detect any departures from the Google Cloud Well-Architected Framework (`OKF-PCA-01` – `OKF-PCA-09`), score all 6 WAF pillars, and generate a comprehensive critique with hardened replacement HCL.

## Execution via MCP

### 1. Direct MCP Tool Call (`verify_terraform_waf_compliance`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="verify_terraform_waf_compliance",
    Arguments={
        "terraform_hcl": "<contents of main.tf / Terraform HCL>",
        "workload_context": "production_enterprise_workload",
        "target_pillars": ["all"],
    },
)
```

### 2. Via Skills Registry (`invoke_skill`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_terraform_waf_verifier",
        "parameters": {
            "terraform_hcl": "<contents of main.tf / Terraform HCL>",
            "workload_context": "production_enterprise_workload",
            "target_pillars": ["all"],
        },
    },
)
```

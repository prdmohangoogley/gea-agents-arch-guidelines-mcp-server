---
name: terraform-version-comparator
description: >-
  Compares a past Terraform HCL version against a present Terraform HCL version across all 6
  Google Cloud Well-Architected Framework pillars (grounded in Dataplex OKF Concepts OKF-PCA-01
  through OKF-PCA-09). Assesses both past and present versions to detect newly introduced WAF
  regressions/departures, resolved WAF violations, persistent gaps, resource diffs, and pillar
  score deltas.
---

# Terraform Past vs. Present Version WAF Comparator Skill

Use this skill when comparing a **past** Terraform script (previous commit, release, or baseline) with a **present** Terraform script (current or proposed change) to determine whether the infrastructure has departed from or improved toward the Google Cloud Well-Architected Framework (`OKF-PCA-01` – `OKF-PCA-09`).

## Execution via MCP

### 1. Direct MCP Tool Call (`compare_terraform_versions_waf`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="compare_terraform_versions_waf",
    Arguments={
        "past_terraform_hcl": "<past / baseline Terraform HCL>",
        "present_terraform_hcl": "<present / current Terraform HCL>",
        "change_context": "PR review comparing v1 baseline to v2 proposed Terraform changes",
    },
)
```

### 2. Via Skills Registry (`invoke_skill`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_terraform_version_comparator",
        "parameters": {
            "past_terraform_hcl": "<past / baseline Terraform HCL>",
            "present_terraform_hcl": "<present / current Terraform HCL>",
            "change_context": "PR review comparing v1 baseline to v2 proposed Terraform changes",
        },
    },
)
```

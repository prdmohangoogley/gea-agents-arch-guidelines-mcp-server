---
name: terraform-infra
description: >-
  Generates, audits, critiques, and compares Terraform HCL for Cloud Spanner Graph, Vertex AI,
  BigQuery, GKE, and IAM service accounts enforcing least-privilege standards and the Google
  Cloud Well-Architected Framework (OKF-PCA-01 through OKF-PCA-09).
---

# Terraform Infrastructure & Well-Architected Suite Skill

Use this skill family to synthesize new Terraform HCL, verify and critique an existing Terraform script for Well-Architected departures (`skill_terraform_waf_verifier`), or compare past vs. present Terraform versions (`skill_terraform_version_comparator`).

## Execution via MCP

### 1. Generate or Audit Terraform HCL (`skill_terraform_infra`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_terraform_infra",
        "parameters": {
            "action": "generate",
            "infrastructure_requirements": "Cloud Spanner instance with graph database and Vertex AI Reasoning Engine binding",
        },
    },
)
```

### 2. Verify & Critique Current Terraform Script for WAF Departures (`skill_terraform_waf_verifier`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="verify_terraform_waf_compliance",
    Arguments={
        "terraform_hcl": "<current Terraform HCL>",
        "workload_context": "production_enterprise_workload",
    },
)
```

### 3. Compare Past vs. Present Terraform Versions (`skill_terraform_version_comparator`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="compare_terraform_versions_waf",
    Arguments={
        "past_terraform_hcl": "<past Terraform HCL>",
        "present_terraform_hcl": "<present Terraform HCL>",
        "change_context": "Assess WAF drift between past and present releases",
    },
)
```

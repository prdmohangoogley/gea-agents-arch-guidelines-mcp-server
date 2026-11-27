---
name: skill_waf_all_pillars_spec_verifier
description: >-
  Searches and verifies any project design specification across ALL Google Cloud Well-Architected
  Framework pillars simultaneously (Operational Excellence, Security, Reliability, Cost
  Optimization, Performance Optimization, and Sustainability), cross-checking against the
  Dataplex PCA & WAF OKF v0.2 Knowledge Base (OKF-PCA-01 through OKF-PCA-09) and 18 deterministic
  forensic anti-pattern rules.
---

# Well-Architected All-Pillars Design Spec Verifier Skill

Use this skill to verify any project design specification against **all Well-Architected Framework pillars simultaneously** (or a selected subset of pillars), grounded in the Dataplex `GEAPL200_PCA_WAF` OKF Knowledge Base (`OKF-PCA-01` – `OKF-PCA-09`).

## Execution via MCP

### 1. Direct MCP Tool Call (`verify_spec_all_waf_pillars` or `audit_waf_pillars`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="verify_spec_all_waf_pillars",
    Arguments={
        "architecture_spec": "<complete project design specification markdown>",
        "workload_type": "enterprise_cloud_system",
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
        "skill_id": "skill_waf_all_pillars_spec_verifier",
        "parameters": {
            "architecture_description": "<complete project design specification markdown>",
            "workload_type": "enterprise_cloud_system",
            "target_pillars": ["all"],
        },
    },
)
```

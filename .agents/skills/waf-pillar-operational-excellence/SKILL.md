---
name: waf-pillar-operational-excellence
description: >-
  Searches and verifies project design specifications against the Google Cloud Well-Architected
  Operational Excellence Pillar grounded in Dataplex OKF concepts OKF-PCA-06, OKF-PCA-07, and
  OKF-PCA-09 (Cloud Logging, Monitoring Heatmaps, Trace X-Cloud-Trace-Context, Profiler, SRE
  SLIs/SLOs/Error Budgets, Cloud Build Private Pools, Cloud Deploy, Progressive Delivery,
  Terraform GCS state locking, and GKE GitOps).
---

# WAF Operational Excellence Pillar Verification Skill

Use this skill to search best practices and verify a project design specification against the **Operational Excellence** pillar (`OKF-PCA-06`, `OKF-PCA-07`, `OKF-PCA-09`).

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_pillar_operational_excellence",
        "parameters": {
            "architecture_description": "<markdown project design spec>",
            "search_query": "Cloud Trace Profiler SRE SLO Cloud Deploy Terraform",
        },
    },
)
```

---
name: waf-pillar-cost-optimization
description: >-
  Searches and verifies project design specifications against the Google Cloud Well-Architected
  Cost Optimization (FinOps) Pillar grounded in Dataplex OKF concepts OKF-PCA-01, OKF-PCA-02,
  OKF-PCA-04, OKF-PCA-06, OKF-PCA-07, and OKF-PCA-09 (GKE Autopilot, Cloud Run scale-to-zero,
  Spot VMs, Instance Schedules, Recommender API, CUDs, BigQuery 90-day automatic 50% long-term
  storage discount & Analytics Hub, GCS Autoclass, _Default Log Exclusion Filters, and Billing
  Budgets + Pub/Sub hard caps).
---

# WAF Cost Optimization (FinOps) Pillar Verification Skill

Use this skill to search best practices and verify a project design specification against the **Cost Optimization (`FinOps`)** pillar (`OKF-PCA-01`, `OKF-PCA-02`, `OKF-PCA-04`, `OKF-PCA-06`, `OKF-PCA-07`, `OKF-PCA-09`).

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_pillar_cost_optimization",
        "parameters": {
            "architecture_description": "<markdown project design spec>",
            "search_query": "GKE Autopilot Spot VMs BigQuery 90-day long-term storage CUDs FinOps",
        },
    },
)
```

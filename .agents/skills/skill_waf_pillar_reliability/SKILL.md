---
name: skill_waf_pillar_reliability
description: >-
  Searches and verifies project design specifications against the Google Cloud Well-Architected
  Reliability Pillar grounded in Dataplex OKF concepts OKF-PCA-01, OKF-PCA-03, OKF-PCA-06,
  OKF-PCA-08, and OKF-PCA-09 (Cloud Spanner 99.999%, Cloud SQL Zonal HA vs Read Replicas,
  Memorystore Redis HA, Multi-Zone/Regional GKE & Cloud Run, 2+2 Dedicated Interconnect & HA VPN
  99.99%, Pub/Sub decoupling, and Cold/Warm/Hot DR RTO/RPO tiers).
---

# WAF Reliability & Disaster Recovery Pillar Verification Skill

Use this skill to search best practices and verify a project design specification against the **Reliability** pillar (`OKF-PCA-01`, `OKF-PCA-03`, `OKF-PCA-06`, `OKF-PCA-08`, `OKF-PCA-09`).

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_pillar_reliability",
        "parameters": {
            "architecture_description": "<markdown project design spec>",
            "search_query": "Spanner Cloud SQL HA RTO RPO Cold Warm Hot DR Interconnect",
        },
    },
)
```

---
name: skill_waf_pillar_performance_optimization
description: >-
  Searches and verifies project design specifications against the Google Cloud Well-Architected
  Performance Optimization Pillar grounded in Dataplex OKF concepts OKF-PCA-01, OKF-PCA-02,
  OKF-PCA-03, and OKF-PCA-09 (Premium Network Tier Anycast Cold-Potato routing, Global External
  ALB + Cloud CDN/Media CDN, Spanner Interleaved Tables + 15s Stale Reads, Bigtable
  HighCardID#ReverseTimestamp row keys, BigQuery Partitioning + Clustering + BI Engine,
  Memorystore Redis, Cloud Run --no-cpu-throttling, and Vertex AI GPU/Context Caching).
---

# WAF Performance Optimization Pillar Verification Skill

Use this skill to search best practices and verify a project design specification against the **Performance Optimization** pillar (`OKF-PCA-01`, `OKF-PCA-02`, `OKF-PCA-03`, `OKF-PCA-09`).

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_pillar_performance_optimization",
        "parameters": {
            "architecture_description": "<markdown project design spec>",
            "search_query": "Premium Tier Cloud CDN Spanner Interleaved Stale Reads Bigtable row key",
        },
    },
)
```

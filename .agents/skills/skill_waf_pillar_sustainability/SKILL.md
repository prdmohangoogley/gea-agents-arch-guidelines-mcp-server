---
name: skill_waf_pillar_sustainability
description: >-
  Searches and verifies project design specifications against the Google Cloud Well-Architected
  Sustainability & Carbon Efficiency Pillar grounded in Dataplex OKF concepts OKF-PCA-01,
  OKF-PCA-02, OKF-PCA-04, and OKF-PCA-09 (Low-Carbon CFE% region selection via
  constraints/gcp.resourceLocations, Scale-to-Zero Serverless, GKE Autopilot bin-packing,
  Recommender API idle VM elimination, and Storage/BigQuery lifecycle compaction).
---

# WAF Sustainability & Carbon Efficiency Pillar Verification Skill

Use this skill to search best practices and verify a project design specification against the **Sustainability** pillar (`OKF-PCA-01`, `OKF-PCA-02`, `OKF-PCA-04`, `OKF-PCA-09`).

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_pillar_sustainability",
        "parameters": {
            "architecture_description": "<markdown project design spec>",
            "search_query": "Carbon CFE region resourceLocations scale-to-zero Autopilot",
        },
    },
)
```

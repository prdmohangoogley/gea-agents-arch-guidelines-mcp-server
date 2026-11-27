---
name: skill_waf_critique
description: >-
  Audits system architectures against all 6 GCP Well-Architected Framework pillars and individual
  pillars grounded in the Dataplex PCA & WAF OKF v0.2 Knowledge Base (OKF-PCA-01 through OKF-PCA-09),
  providing quantitative 0.0-3.0 scoring, deterministic 18-anti-pattern verification, and remediation diffs.
---

# Well-Architected Framework (WAF) Critique Skill (`GEAPL200_PCA_WAF` OKF Grounded)

Use this skill to audit workloads and project design specifications against Google Cloud's Well-Architected pillars—either **per pillar** or across **all pillars simultaneously**—backed by the Dataplex `GEAPL200_PCA_WAF` OKF v0.2 Knowledge Base (`OKF-PCA-01`..`OKF-PCA-09`).

## Execution via MCP

### 1. Audit All Pillars Simultaneously
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_critique",
        "parameters": {
            "architecture_description": "<markdown architecture or project design spec>",
            "workload_type": "multi_agent_system",
            "target_pillars": ["all"],
        },
    },
)
```

### 2. Audit a Single Pillar (`skill_waf_pillar_critique` or Pillar-Specific Verifiers)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_pillar_critique",
        "parameters": {
            "pillar_name": "security",  # 'operational_excellence', 'security', 'reliability', 'cost_optimization', 'performance_optimization', 'sustainability'
            "architecture_description": "<markdown architecture or project design spec>",
        },
    },
)
```

---
name: waf-okf-search
description: >-
  Searches the Google Cloud Dataplex PCA & Well-Architected Framework (WAF) OKF v0.2
  Knowledge Base (OKF-PCA-01 through OKF-PCA-09) stored in Cloud Storage and Dataplex Universal
  Catalog. Retrieves 5-second service selection matrices, pillar best practices, and 18 forensic
  architectural anti-patterns per pillar or across all pillars.
---

# PCA & Well-Architected Framework (WAF) OKF Knowledge Base Search Skill

Use this skill to search and retrieve authoritative Google Cloud architectural best practices, decision trees, and anti-pattern fixes from the `GEAPL200_PCA_WAF` OKF v0.2 Knowledge Base (`OKF-PCA-01` – `OKF-PCA-09`).

## Backing Cloud Storage & Dataplex Knowledge Base

- **GCS Bucket**: `gs://gea_agent_development_architectural_best_practices_pca_waf/PCA_WAF_OKF_2026-11-24_173000/okf/`
- **Dataplex Entry Group**: `projects/arch-best-practices-mcp-server/locations/us/entryGroups/geap-architecture-kb` & `projects/arch-best-practices-mcp-server/locations/us/entryGroups/geap-pca-waf-kb`
- **Dataplex Aspect Types**: `projects/fivedaysai-prd-sandbox-317383/locations/us/aspectTypes/okf` & `okf-pca-waf`

## Execution via MCP

### 1. Direct MCP Tool Call (`search_waf_okf_best_practices`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="search_waf_okf_best_practices",
    Arguments={
        "query": "Cloud Spanner vs Cloud SQL vs Bigtable",
        "pillar": "all",  # or 'operational_excellence', 'security', 'reliability', 'cost_optimization', 'performance_optimization', 'sustainability'
        "service_area": "all",
        "include_antipatterns": True,
    },
)
```

### 2. Via Skills Registry (`invoke_skill`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_okf_search",
        "parameters": {
            "query": "VPC Service Controls Access Context Manager",
            "pillar": "security",
        },
    },
)
```

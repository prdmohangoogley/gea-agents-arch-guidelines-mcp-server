---
name: skill_google_landing_metrics
description: >-
  Audits architectures against Google Landing Metrics, Core Web Vitals (LCP, INP, CLS),
  Edge CDN caching hit ratios, and p99 latency envelopes.
---

# Google Landing Metrics Skill

Use this skill when auditing edge endpoints, frontend latency, or conversational agent response latency against Google SLAs.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_google_landing_metrics_critique",
        "parameters": {
            "system_or_endpoint_spec": "<endpoint or architecture spec>",
            "target_sla": {"ttft_ms": 300, "p99_latency_ms": 500, "cdn_hit_ratio": 0.90}
        }
    }
)
```

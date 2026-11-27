---
name: skill_enterprise_system_design
description: >-
  Synthesizes end-to-end enterprise architectures adhering to Zero Ambient Authority (ZAA),
  tiered storage (Cloud Spanner Graph + BigQuery), Model Armor security, and multi-agent topologies.
---

# Enterprise System Design Skill

Use this skill when designing new Google Cloud systems, microservices, or multi-agent swarms.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_system_design",
        "parameters": {
            "system_name": "<system name>",
            "requirements": "<functional and non-functional requirements>",
            "constraints": {"sla": "99.99%", "p99_latency_ms": 500, "compliance": "ZAA"},
            "multi_agent_enabled": True
        }
    }
)
```

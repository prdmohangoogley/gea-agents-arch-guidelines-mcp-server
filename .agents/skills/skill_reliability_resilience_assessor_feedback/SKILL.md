---
name: skill_reliability_resilience_assessor_feedback
description: >-
  Critically assesses whether a spec, project, or component adheres to all 4 domains of the
  Reliability & Resilience Rubric (Availability Design, Observability, Failure & Recovery Testing,
  and Graceful Degradation), enforcing per-domain competency cutlines and generating prioritized feedback.
---

# Reliability & Resilience Assessor & Feedback Skill

Use this skill to critically evaluate any project, specification, or component against the **4-Domain Reliability & Resilience Rubric**.

## Rubric Domains & Pass Cutlines

To **PASS**, the target MUST be at a **Competent** level on **1 or more** sub-criteria in every domain:

1. **Availability Design** (*>= 1 Competent*):
   - `1.1` Redundancy, failover, and health checks aligning with SLO/SLA definitions.
   - `1.2` Distributed patterns (consistency, partitioning, multi-region) ensuring high availability.
2. **Observability** (*>= 1 Competent*):
   - `2.1` Structured logging, metrics, and distributed tracing.
   - `2.2` AI-specific KPI monitoring (latency, token usage, quality) ensuring runtime visibility.
3. **Failure & Recovery Testing** (*>= 1 Competent*):
   - `3.1` Failure injection, red teaming, and disaster recovery validation.
   - `3.2` Backup/restore and resilience testing under degraded conditions verifying recovery protocols.
4. **Graceful Degradation** (*>= 1 Competent*):
   - `4.1` Fallback strategies, circuit breakers, and retry policies.
   - `4.2` Timeout handling ensuring system stability during partial failures or high load.

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_reliability_resilience_assessor_feedback",
        "parameters": {
            "project_name": "<project or component name>",
            "project_manifest_or_spec": "<project/spec/component details>",
            "scope": "project"
        }
    }
)
```

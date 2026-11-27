---
name: performance-cost-optimization-assessor-feedback
description: >-
  Assesses a project, specification, or component against all 3 domains of the Performance & Cost
  Optimization Rubric (Scalability & Elasticity, Resource Efficiency, and AI Cost Management),
  enforcing per-domain competency cutlines and generating prioritized actionable feedback.
---

# Performance & Cost Optimization Assessor & Feedback Skill

Use this skill to critically evaluate any project, specification, or component against the **3-Domain Performance & Cost Optimization Rubric**.

## Rubric Domains & Pass Cutlines

To **PASS**, the target MUST be at a **Competent** level on **1 or more** sub-criteria in every domain:

1. **Scalability & Elasticity** (*>= 1 Competent*):
   - `1.1` Horizontal/vertical scaling strategies with autoscaling policies and load balancing.
   - `1.2` Optimized API throughput and HPC/GPU cluster scaling for performant inference.
2. **Resource Efficiency** (*>= 1 Competent*):
   - `2.1` Compute/GPU right-sizing, autoscaling strategies, and spot/preemptible instance usage.
   - `2.2` Minimizing resource waste while maintaining performance targets.
3. **AI Cost Management** (*>= 1 Competent*):
   - `3.1` Model selection trade-offs, response caching, batching, and embedding optimization.
   - `3.2` Token and context window management ensuring fiscal responsibility.

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_performance_cost_optimization_assessor_feedback",
        "parameters": {
            "project_name": "<project or component name>",
            "project_manifest_or_spec": "<project/spec/component details>",
            "scope": "project"
        }
    }
)
```

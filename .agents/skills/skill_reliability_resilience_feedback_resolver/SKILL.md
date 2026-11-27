---
name: skill_reliability_resilience_feedback_resolver
description: >-
  Resolves all Reliability & Resilience assessment feedback at the project, spec, or component level
  by orchestrating existing relevant skills in the library and re-invoking
  reliability-resilience-assessor-feedback multiple times until every feedback item is resolved.
---

# Reliability & Resilience Feedback Resolver Skill

Use this skill after `reliability-resilience-assessor-feedback` to systematically resolve all reliability, observability, recovery-testing, and graceful-degradation gaps and re-verify iteratively until all 4 domains clearly **PASS**.

## Resolution & Iterative Re-Assessment Workflow

1. **Run Baseline Assessment**: Invoke `reliability-resilience-assessor-feedback` at the target `scope` (`project`, `spec`, or `component`).
2. **Map Every Finding to Library Skills**:
   | Domain | Relevant Library Skills |
   | :--- | :--- |
   | **1. Availability Design** | `waf-pillar-reliability`, `enterprise-system-design`, `terraform-waf-verifier`, `waf-all-pillars-spec-verifier` |
   | **2. Observability** | `waf-pillar-operational-excellence`, `google-agents-cli-observability`, `eval-harness`, `fde-governance-auditor` |
   | **3. Failure & Recovery Testing** | `eval-harness`, `waf-pillar-reliability`, `complete-system-audit`, `fde-governance-auditor` |
   | **4. Graceful Degradation** | `waf-pillar-reliability`, `spec-best-practices-updater`, `enterprise-system-design`, `spec-critique` |
3. **Apply Real Code/IaC/Test Remediations** (health checks, OTel tracing, circuit breakers, timeouts, failure-injection tests).
4. **Re-Invoke `reliability-resilience-assessor-feedback` Multiple Times if Needed** (`max_iterations`) until all 4 domains pass with zero open feedback items.
5. **Handoff to `reliability-resilience-faqs`** to document the verified evidence in `docs/FAQs.md`.

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_reliability_resilience_feedback_resolver",
        "parameters": {
            "project_name": "<project or component name>",
            "project_manifest_or_spec": "<manifest or spec>",
            "scope": "project",
            "max_iterations": 3
        }
    }
)
```

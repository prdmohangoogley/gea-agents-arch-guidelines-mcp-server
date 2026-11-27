---
name: skill_performance_cost_optimization_feedback_resolver
description: >-
  Resolves Performance & Cost Optimization assessment feedback at the project, spec, or component
  level by orchestrating relevant FinOps and performance skills in the library and re-invoking
  performance-cost-optimization-assessor-feedback iteratively until all 3 domains pass.
---

# Performance & Cost Optimization Feedback Resolver Skill

Use this skill after `performance-cost-optimization-assessor-feedback` to systematically resolve scalability, resource efficiency, and AI cost management gaps and re-verify iteratively until all 3 domains clearly **PASS**.

## Resolution & Iterative Re-Assessment Workflow

1. **Run Baseline Assessment**: Invoke `performance-cost-optimization-assessor-feedback` at target `scope` (`project`, `spec`, or `component`).
2. **Map Every Finding to Library Skills**:
   | Domain | Relevant Library Skills |
   | :--- | :--- |
   | **1. Scalability & Elasticity** | `waf-pillar-performance-optimization`, `google-landing-metrics`, `enterprise-system-design`, `terraform-waf-verifier` |
   | **2. Resource Efficiency** | `waf-pillar-cost-optimization`, `waf-pillar-sustainability`, `terraform-waf-verifier`, `waf-all-pillars-spec-verifier` |
   | **3. AI Cost Management** | `waf-pillar-cost-optimization`, `spec-best-practices-updater`, `waf-pillar-performance-optimization`, `fde-governance-auditor` |
3. **Apply Real Code/IaC/Routing/Caching Remediations** and verify with tests.
4. **Re-Invoke `performance-cost-optimization-assessor-feedback` Multiple Times if Needed** (`max_iterations`) until all 3 domains pass with zero open feedback items.
5. **Handoff to `performance-cost-optimization-faqs`** to document verified evidence in `docs/FAQs.md`.

---
name: skill_designing_for_change_feedback_resolver
description: >-
  Resolves Designing for Change assessment feedback at the project, spec, or component level by
  orchestrating relevant architecture, API, and extensibility skills in the library and re-invoking
  designing-for-change-assessor-feedback iteratively until all 4 domains pass.
---

# Designing for Change Feedback Resolver Skill

Use this skill after `designing-for-change-assessor-feedback` to systematically resolve modularity, configuration, API versioning, and extensibility gaps and re-verify iteratively until all 4 domains clearly **PASS**.

## Resolution & Iterative Re-Assessment Workflow

1. **Run Baseline Assessment**: Invoke `designing-for-change-assessor-feedback` at target `scope` (`project`, `spec`, or `component`).
2. **Map Every Finding to Library Skills**:
   | Domain | Relevant Library Skills |
   | :--- | :--- |
   | **1. Modularity & Abstraction** | `enterprise-system-design`, `spec-critique`, `spec-best-practices-updater`, `fastmcp-tool-dev` |
   | **2. Configuration Management** | `waf-pillar-operational-excellence`, `terraform-infra`, `spec-best-practices-updater`, `waf-pillar-security` |
   | **3. API Design & Versioning** | `fastmcp-tool-dev`, `spec-creation-workflow`, `okf-auto-evolution`, `spec-critique` |
   | **4. Extensibility** | `enterprise-system-design`, `fastmcp-tool-dev`, `google-agents-cli-adk-code`, `waf-pillar-operational-excellence` |
3. **Apply Real Abstraction, Config, Contract & Plugin Remediations**.
4. **Re-Invoke `designing-for-change-assessor-feedback` Multiple Times if Needed** (`max_iterations`) until all 4 domains pass with zero open feedback items.
5. **Handoff to `designing-for-change-faqs`** to document verified evidence in `docs/FAQs.md`.

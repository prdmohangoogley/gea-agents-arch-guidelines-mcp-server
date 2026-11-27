---
name: skill_operational_excellence_feedback_resolver
description: >-
  Resolves Operational Excellence assessment feedback at the project, spec, or component level
  by orchestrating relevant DevOps, Terraform, eval, and observability skills in the library and
  re-invoking operational-excellence-assessor-feedback iteratively until all 4 domains pass.
---

# Operational Excellence Feedback Resolver Skill

Use this skill after `operational-excellence-assessor-feedback` to systematically resolve CI/CD, IaC, AI lifecycle, and testing gaps and re-verify iteratively until all 4 domains clearly **PASS**.

## Resolution & Iterative Re-Assessment Workflow

1. **Run Baseline Assessment**: Invoke `operational-excellence-assessor-feedback` at target `scope` (`project`, `spec`, or `component`).
2. **Map Every Finding to Library Skills**:
   | Domain | Relevant Library Skills |
   | :--- | :--- |
   | **1. CI/CD & Deployment** | `waf-pillar-operational-excellence`, `google-agents-cli-deploy`, `terraform-waf-verifier`, `waf-all-pillars-spec-verifier` |
   | **2. Infrastructure as Code** | `terraform-infra`, `terraform-waf-verifier`, `terraform-version-comparator`, `waf-pillar-operational-excellence` |
   | **3. AI Lifecycle Management** | `eval-harness`, `okf-auto-evolution`, `google-agents-cli-eval`, `google-agents-cli-observability` |
   | **4. Testing & Quality Engineering** | `eval-harness`, `fastmcp-tool-dev`, `waf-pillar-operational-excellence`, `fde-governance-auditor` |
3. **Apply Real CI/CD, IaC, Versioning & Test Remediations**.
4. **Re-Invoke `operational-excellence-assessor-feedback` Multiple Times if Needed** (`max_iterations`) until all 4 domains pass with zero open feedback items.
5. **Handoff to `operational-excellence-faqs`** to document verified evidence in `docs/FAQs.md`.

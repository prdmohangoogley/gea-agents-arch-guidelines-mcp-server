---
name: scoping-documentation-feedback-resolver
description: >-
  Addresses Scoping & Documentation assessment feedback across an entire project's documentation
  by orchestrating relevant spec, ADR, API, and runbook skills in the library and re-invoking
  scoping-documentation-assessor-feedback iteratively until all 7 domains pass.
---

# Scoping & Documentation Feedback Resolver Skill

Use this skill after `scoping-documentation-assessor-feedback` to systematically close every documentation gap across the entire project and re-verify iteratively until all 7 domains clearly **PASS**.

## Resolution & Iterative Re-Assessment Workflow

1. **Run Baseline Assessment**: Invoke `scoping-documentation-assessor-feedback` across the project's docs (`README.md`, `docs/`, `docs/specs/`, ADRs, API docs, runbooks).
2. **Map Every Finding to Library Skills**:
   | Domain | Relevant Library Skills |
   | :--- | :--- |
   | **1. Problem Definition** | `spec-creation-workflow`, `arbitrary-spec-generator`, `spec-critique`, `fde-governance-auditor` |
   | **2. Technical Scope & Constraints** | `spec-creation-workflow`, `enterprise-system-design`, `spec-best-practices-updater`, `waf-all-pillars-spec-verifier` |
   | **3. Stakeholder Alignment & Success Criteria** | `spec-creation-workflow`, `codebase-to-spec-collection`, `fde-governance-auditor`, `spec-critique` |
   | **4. System Design Artifacts** | `enterprise-system-design`, `codebase-to-spec-collection`, `arbitrary-spec-generator`, `spec-creation-workflow` |
   | **5. Decision Records (ADRs)** | `spec-creation-workflow`, `spec-critique`, `codebase-to-spec-collection`, `arbitrary-spec-generator` |
   | **6. API Documentation** | `fastmcp-tool-dev`, `codebase-to-spec-collection`, `arbitrary-spec-generator`, `writing-guidelines` |
   | **7. Operational Documentation** | `waf-pillar-operational-excellence`, `google-agents-cli-deploy`, `writing-guidelines`, `codebase-to-spec-collection` |
3. **Create or Update Real Project Documentation** (e.g., `docs/00_SCOPING_AND_ADR_CHARTER.md`, ADRs, diagrams, API specs, runbooks).
4. **Re-Invoke `scoping-documentation-assessor-feedback` Multiple Times if Needed** (`max_iterations`) until all 7 domains pass with zero open feedback items.

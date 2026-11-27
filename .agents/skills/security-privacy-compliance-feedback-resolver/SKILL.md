---
name: security-privacy-compliance-feedback-resolver
description: >-
  Addresses Security, Privacy & Compliance assessment feedback by orchestrating existing security
  and governance skills in the library and re-invoking security-privacy-compliance-assessor-feedback
  iteratively until every feedback item is adequately resolved and all 5 domains pass.
---

# Security, Privacy & Compliance Feedback Resolver Skill

Use this skill after running `security-privacy-compliance-assessor-feedback` to systematically resolve all security, privacy, and compliance gaps and re-verify iteratively until all 5 rubric domains clearly **PASS**.

## Resolution & Iterative Re-Assessment Workflow

1. **Run Baseline Assessment**:
   - Invoke `security-privacy-compliance-assessor-feedback` to collect all P0 blockers and P1 enhancements.
2. **Map Every Finding to Library Skills**:
   | Domain | Relevant Library Skills |
   | :--- | :--- |
   | **1. Authentication & Authorization** | `waf-pillar-security`, `fde-governance-auditor`, `terraform-waf-verifier`, `spec-best-practices-updater` |
   | **2. Infrastructure & Network Security** | `waf-pillar-security`, `terraform-waf-verifier`, `enterprise-system-design`, `waf-all-pillars-spec-verifier` |
   | **3. Data Protection & Privacy** | `waf-pillar-security`, `complete-system-audit`, `terraform-waf-verifier`, `spec-best-practices-updater` |
   | **4. AI-Specific Security** | `waf-pillar-security`, `fde-governance-auditor`, `eval-harness`, `spec-best-practices-updater` |
   | **5. Compliance & Governance** | `fde-governance-auditor`, `complete-system-audit`, `waf-pillar-operational-excellence`, `waf-pillar-security` |
3. **Apply Real Code/IaC/Config Remediations** and verify with unit/security tests.
4. **Re-Invoke `security-privacy-compliance-assessor-feedback` Multiple Times if Needed** (`max_iterations`, default 3) until all 5 domains pass with zero open feedback items.
5. **Handoff to `security-privacy-compliance-faqs`** to document the verified evidence in `docs/FAQs.md`.

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_security_privacy_compliance_feedback_resolver",
        "parameters": {
            "project_name": "<project name>",
            "project_manifest_or_spec": "<project summary>",
            "max_iterations": 3
        }
    }
)
```

---
name: security-privacy-compliance-assessor-feedback
description: >-
  Assesses a project, repository, or technical specification against all 5 domains of the
  Security, Privacy & Compliance Rubric (Authentication & Authorization, Infrastructure & Network
  Security, Data Protection & Privacy, AI-Specific Security, and Compliance & Governance),
  enforcing per-domain competency thresholds and producing prioritized actionable feedback.
---

# Security, Privacy & Compliance Assessor & Feedback Skill

Use this skill to perform a rigorous, evidence-backed assessment of any project, repository, or specification against the **5-Domain Security, Privacy & Compliance Rubric**.

## Rubric Domains & Pass Cutlines

To **PASS** the overall assessment, a project MUST pass **all 5 domains**:

1. **Authentication & Authorization** — *Competent on **2 or more***:
   - `1.1` Robust authentication/authorization via Service Accounts, scoped API keys, and OAuth/OIDC.
   - `1.2` Principle of Least Privilege enforced across all IAM configurations.
2. **Infrastructure & Network Security** — *Competent on **2 or more***:
   - `2.1` Secure VPCs with network segmentation, private endpoints, and zero-trust principles.
   - `2.2` Service perimeters (VPC-SC) and firewall/WAF policies protecting enterprise assets.
3. **Data Protection & Privacy** — *Competent on **2 or more***:
   - `3.1` Encryption at rest/transit, PII handling, data classification, and DLP.
   - `3.2` Secure Secrets management preventing credential exposure.
4. **AI-Specific Security** — *Competent on **2 or more***:
   - `4.1` Prompt-injection mitigation, output filtering, and structural guardrails.
   - `4.2` Model access controls and content safety layers protecting against adversarial use.
5. **Compliance & Governance** — *Competent on **1 or more***:
   - `5.1` Audit logging and data residency aligning with regulatory requirements.
   - `5.2` Enterprise policy enforcement across all deployments ensuring governance compliance.

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_security_privacy_compliance_assessor_feedback",
        "parameters": {
            "project_name": "<project name>",
            "project_manifest_or_spec": "<project codebase/IaC/spec summary>"
        }
    }
)
```

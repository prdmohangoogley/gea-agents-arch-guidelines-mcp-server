---
name: security-privacy-compliance-faqs
description: >-
  Generates human-style, direct, conversational FAQs with concrete codebase evidence documenting
  how a project, repository, or spec addresses all 5 domains of the Security, Privacy & Compliance
  Rubric. Appends or updates a Security, Privacy & Compliance section in docs/FAQs.md, or
  initializes a new docs/FAQs.md if none exists.
---

# Security, Privacy & Compliance FAQs Skill

Use this skill to document how a project, repository, or specification satisfies the **5-Domain Security, Privacy & Compliance Rubric** in clear, conversational, human-style Q&A format that lets any reviewer verify every claim directly in the repo.

## File Upsert Behavior (Mandatory)

1. **If `docs/FAQs.md` already exists**:
   - Preserve all existing sections untouched (e.g., `AI/ML Engineering Rubric FAQs`, general FAQs).
   - If `<!-- SECURITY_PRIVACY_COMPLIANCE_FAQS_START -->` ... `<!-- SECURITY_PRIVACY_COMPLIANCE_FAQS_END -->` markers exist, replace only that block in place.
   - Otherwise, append a new `## Security, Privacy & Compliance FAQs` section wrapped in those markers.
2. **If `docs/FAQs.md` does not exist**:
   - Initialize `docs/FAQs.md` with `# Frequently Asked Questions (FAQs)` and populate it with the `## Security, Privacy & Compliance FAQs` section.

## Style Guidelines

- **Direct & Conversational**: Write questions the way a real security reviewer, engineer, or auditor asks them (e.g., *"Where are secrets stored, and how can I check nothing is hardcoded?"*).
- **Verifiable Direct Evidence**: Every answer MUST point to exact file paths, classes, Terraform resources, regex/DLP rules, or pytest suites in the repository so anyone can check the claim in seconds.

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_security_privacy_compliance_faqs",
        "parameters": {
            "project_name": "<project name>",
            "project_manifest_or_summary": "<project evidence summary>",
            "docs_file_path": "docs/FAQs.md",
            "write_to_disk": True
        }
    }
)
```

---
name: reliability-resilience-faqs
description: >-
  Generates direct, conversational FAQs pointing to exact areas within a spec or project that
  address all 4 domains of the Reliability & Resilience Rubric. Appends or updates a Reliability &
  Resilience section in docs/FAQs.md, or initializes a new docs/FAQs.md if none exists.
---

# Reliability & Resilience FAQs Skill

Use this skill to generate clear, human-style Q&As pointing directly to the exact files, classes, tests, and specs where a project satisfies the **4-Domain Reliability & Resilience Rubric**.

## File Upsert Behavior (Mandatory)

1. **If `docs/FAQs.md` already exists**:
   - Preserve all existing sections untouched (AI/ML Engineering Rubric FAQs, Security, Privacy & Compliance FAQs, etc.).
   - If `<!-- RELIABILITY_RESILIENCE_FAQS_START -->` ... `<!-- RELIABILITY_RESILIENCE_FAQS_END -->` markers exist, update that block in place; otherwise append a new `## Reliability & Resilience FAQs` section wrapped in those markers.
2. **If `docs/FAQs.md` does not exist**:
   - Initialize `docs/FAQs.md` with `# Frequently Asked Questions (FAQs)` and populate it with the Reliability & Resilience FAQs section.

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_reliability_resilience_faqs",
        "parameters": {
            "project_name": "<project name>",
            "project_manifest_or_summary": "<reliability & resilience evidence summary>",
            "docs_file_path": "docs/FAQs.md",
            "write_to_disk": True
        }
    }
)
```

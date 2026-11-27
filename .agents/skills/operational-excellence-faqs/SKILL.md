---
name: operational-excellence-faqs
description: >-
  Generates direct, conversational FAQs pointing to exact areas within a spec or project that
  address all 4 domains of the Operational Excellence Rubric. Appends or updates an Operational
  Excellence section in docs/FAQs.md, or initializes a new docs/FAQs.md if none exists.
---

# Operational Excellence FAQs Skill

Use this skill to generate clear, human-style Q&As pointing directly to exact CI/CD scripts, Terraform modules, lifecycle tooling, and test suites where a project satisfies the **4-Domain Operational Excellence Rubric**.

## File Upsert Behavior (Mandatory)

1. **If `docs/FAQs.md` already exists**:
   - Preserve all existing sections untouched (AI/ML, Security/Privacy/Compliance, Reliability & Resilience, Performance & Cost Optimization).
   - If `<!-- OPERATIONAL_EXCELLENCE_FAQS_START -->` ... `<!-- OPERATIONAL_EXCELLENCE_FAQS_END -->` markers exist, update that block in place; otherwise append a new `## Operational Excellence FAQs` section wrapped in those markers.
2. **If `docs/FAQs.md` does not exist**:
   - Initialize `docs/FAQs.md` with `# Frequently Asked Questions (FAQs)` and populate it with the Operational Excellence FAQs section.

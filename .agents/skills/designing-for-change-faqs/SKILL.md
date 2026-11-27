---
name: designing-for-change-faqs
description: >-
  Generates direct, conversational FAQs pointing to exact areas within a spec or project that
  address all 4 domains of the Designing for Change Rubric. Appends or updates a Designing for
  Change section in docs/FAQs.md, or initializes a new docs/FAQs.md if none exists.
---

# Designing for Change FAQs Skill

Use this skill to generate clear, human-style Q&As pointing directly to exact abstractions, config files, API contracts, and plugin discovery code where a project satisfies the **4-Domain Designing for Change Rubric**.

## File Upsert Behavior (Mandatory)

1. **If `docs/FAQs.md` already exists**:
   - Preserve all existing sections untouched (AI/ML, Security/Privacy/Compliance, Reliability, Performance & Cost, Operational Excellence).
   - If `<!-- DESIGNING_FOR_CHANGE_FAQS_START -->` ... `<!-- DESIGNING_FOR_CHANGE_FAQS_END -->` markers exist, update that block in place; otherwise append a new `## Designing for Change FAQs` section wrapped in those markers.
2. **If `docs/FAQs.md` does not exist**:
   - Initialize `docs/FAQs.md` with `# Frequently Asked Questions (FAQs)` and populate it with the Designing for Change FAQs section.

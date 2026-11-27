---
name: performance-cost-optimization-faqs
description: >-
  Generates direct, conversational FAQs pointing to exact areas within a spec or project that
  address all 3 domains of the Performance & Cost Optimization Rubric. Appends or updates a
  Performance & Cost Optimization section in docs/FAQs.md, or initializes a new docs/FAQs.md if none exists.
---

# Performance & Cost Optimization FAQs Skill

Use this skill to generate clear, human-style Q&As pointing directly to exact files, IaC configs, caching layers, and metrics where a project satisfies the **3-Domain Performance & Cost Optimization Rubric**.

## File Upsert Behavior (Mandatory)

1. **If `docs/FAQs.md` already exists**:
   - Preserve all existing sections untouched (AI/ML, Security/Privacy/Compliance, Reliability & Resilience, etc.).
   - If `<!-- PERFORMANCE_COST_OPTIMIZATION_FAQS_START -->` ... `<!-- PERFORMANCE_COST_OPTIMIZATION_FAQS_END -->` markers exist, update that block in place; otherwise append a new `## Performance & Cost Optimization FAQs` section wrapped in those markers.
2. **If `docs/FAQs.md` does not exist**:
   - Initialize `docs/FAQs.md` with `# Frequently Asked Questions (FAQs)` and populate it with the Performance & Cost Optimization FAQs section.

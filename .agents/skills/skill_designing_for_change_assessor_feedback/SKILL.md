---
name: skill_designing_for_change_assessor_feedback
description: >-
  Assesses a project, specification, or component against all 4 domains of the Designing for Change
  Rubric (Modularity & Abstraction, Configuration Management, API Design & Versioning, and
  Extensibility), enforcing per-domain competency cutlines and generating prioritized feedback.
---

# Designing for Change Assessor & Feedback Skill

Use this skill to critically evaluate any project, specification, or component against the **4-Domain Designing for Change Rubric**.

## Rubric Domains & Pass Cutlines

To **PASS**, the target MUST be at a **Competent** level on **1 or more** sub-criteria in every domain:

1. **Modularity & Abstraction** (*>= 1 Competent*):
   - `1.1` Loose coupling and interface contracts facilitating model swappability.
   - `1.2` Dependency injection ensuring modular, maintainable code structures.
2. **Configuration Management** (*>= 1 Competent*):
   - `2.1` Environment separation via feature flags and externalized settings (env files, secrets as env).
   - `2.2` Dynamic system adjustments without code changes.
3. **API Design & Versioning** (*>= 1 Competent*):
   - `3.1` Contract-first design with backward compatibility.
   - `3.2` Schema evolution ensuring stable integrations across system updates.
4. **Extensibility** (*>= 1 Competent*):
   - `4.1` Plugin patterns and event-driven architectures (webhooks/callbacks).
   - `4.2` System extensions and integrations with minimal core-logic disruption.

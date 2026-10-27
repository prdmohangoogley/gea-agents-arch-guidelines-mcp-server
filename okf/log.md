---
type: "Log"
title: "Change log"
timestamp: "2026-09-30T12:47:46-07:00"
corpus: "GEAPL200"
version_tag: "GEAPL200_2026-09-30_124746"
---

# Change log

## 2026-10-26 (Unified L200 + L300 Extension & FDE Grading Rubric Enforcement)

- Merged the 20 existing concepts from `gs://gea_agent_development_architectural_best_practices_1790796607` (`GEAPL200_2026-09-30_124746`) with the 15 L300 concepts (`21-*.md` through `35-*.md`) and added the standalone mandatory governance specification `concepts/00-fde-field-readiness-and-grading-rubric.md` (36 concepts total).
- Preserved existing bundle `version_tag` (`GEAPL200_2026-09-30_124746`) and 180-day `stale_after` TTL semantics across all concepts.
- Embedded the enforceable Google Cloud FDE Grading Rubric (Part A: Presentation & Advisory Rigor, Part B: Engineering & Implementation Excellence, 0–3 scale, >= 2.0 Pass cutline, zero `0` disqualifier rule) and prevailing customer case studies anchored to `https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head` across `index.md` and every individual concept (`00`–`35`).
- Generated 36 Dataplex / GCP Knowledge Catalog `okf` AspectType JSON payloads in `catalog-entries/`.

## 2026-09-30

- Initial publication of bundle `GEAPL200_2026-09-30_124746`.
- 20 concepts converted from Google Docs; 100 source figures processed into Mermaid diagrams, Markdown tables, or retained images.
- Structural QA and CRC32C manifest recorded for every concept.
- Published with `status: draft`. Diagrams are model reconstructions and have not yet had human review.

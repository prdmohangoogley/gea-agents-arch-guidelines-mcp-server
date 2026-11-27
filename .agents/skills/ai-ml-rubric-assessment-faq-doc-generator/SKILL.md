---
name: ai-ml-rubric-assessment-faq-doc-generator
description: >-
  Generates a comprehensive collection of FAQs documenting how a project demonstrates all 5 domains
  of the AI/ML Engineering Rubric with concrete codebase evidence. Creates a dedicated rubric FAQ
  section inside an existing docs/FAQs.md file, or creates a new docs/FAQs.md if none exists.
---

# AI/ML Rubric Assessment FAQ Doc Generator Skill

Use this skill to document how a project satisfies and demonstrates the **5-Domain AI/ML Engineering Rubric** in a clear, evidence-backed FAQ format inside `docs/FAQs.md`.

## File Upsert Behavior (Mandatory)

1. **Check for Existing `docs/FAQs.md`**:
   - If `docs/FAQs.md` **already exists**:
     - Preserve all existing FAQ sections untouched.
     - If `<!-- AI_ML_RUBRIC_FAQS_START -->` ... `<!-- AI_ML_RUBRIC_FAQS_END -->` markers exist, replace only that section in place.
     - Otherwise, append a new `## AI/ML Engineering Rubric FAQs` section (wrapped in those markers for future idempotent updates).
   - If `docs/FAQs.md` **does not exist**:
     - Create `docs/FAQs.md` with a top-level `# Frequently Asked Questions (FAQs)` heading and populate it with the complete AI/ML Engineering Rubric FAQs section.

## Content Requirements

Every generated FAQ section MUST cover all **5 AI/ML Engineering Rubric Domains** with concrete project-specific answers (citing real files, modules, classes, metrics, and tests):

1. **Agentic & Multi-Agent Systems**: Cognitive architecture, CUJ alignment, planning/reasoning loops & state/memory management, tool calling & security boundaries, multi-agent coordination, latency SLAs & graceful error handling.
2. **Retrieval & Data Engineering for AI**: RAG / GraphRAG architecture, embeddings & vector/graph stores, chunking/indexing & hybrid search, grounding & citation provenance, complex document/table parsing pipelines, retrieval quality validation.
3. **Model Selection, Tuning & Optimization**: Multi-criteria model selection (quality/latency/cost/context), inference optimization & KV/prefix caching, prompt engineering & structured JSON output enforcement, data engineering & synthetic/golden datasets, encoder vs. decoder architecture selection.
4. **LLM Ops and Evaluation**: Multi-metric evaluation beyond LLM-as-a-Judge (Precision, Recall, F1, MRR, ROUGE-L, faithfulness, TSP, Argument Accuracy), eval dataset design + human/automated evaluation, regression detection & OpenTelemetry/Cloud Trace observability.
5. **Domain-Applied AI/ML Expertise**: Vertical business KPIs translated to AI/ML SLOs, domain data handling & regulatory compliance/privacy (HIPAA, FINRA, PCI-DSS, DLP, ZAA), and integration with industry-standard legacy systems & workflows.

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_ai_ml_rubric_assessment_faq_doc_generator",
        "parameters": {
            "project_name": "<project name>",
            "project_manifest_or_summary": "<project evidence summary>",
            "docs_file_path": "docs/FAQs.md",
            "write_to_disk": True
        }
    }
)
```

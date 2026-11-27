---
name: skill_ai_ml_rubric_assessment_feedback
description: >-
  Assesses an entire project, codebase, or technical specification against all 5 domains of the
  AI/ML Engineering Rubric (Agentic & Multi-Agent Systems, Retrieval & Data Engineering for AI,
  Model Selection/Tuning/Optimization, LLM Ops & Evaluation, and Domain-Applied AI/ML Expertise),
  enforcing per-domain competency thresholds and generating prioritized actionable feedback.
---

# AI/ML Rubric Assessment & Feedback Skill

Use this skill to perform a rigorous, evidence-backed assessment of any AI/ML project, repository, or technical specification against the **5-Domain AI/ML Engineering Rubric**.

## Rubric Domains & Pass Cutlines

To **PASS** the overall assessment, a project MUST pass **all 5 domains**:

1. **Agentic & Multi-Agent Systems** — *Competent on **2 or more** of 5*:
   - `1.1` Cognitive architectures & orchestration patterns aligned with Critical User Journeys (CUJs).
   - `1.2` Functional planning & reasoning loops; session memory & state management preventing execution loops.
   - `1.3` Tool/function calling integrating legacy/external APIs while respecting data boundaries and security.
   - `1.4` Multi-agent coordination delivering cohesive UX and production-ready workflows.
   - `1.5` Smooth operation within enterprise latency SLAs with graceful error handling.
2. **Retrieval & Data Engineering for AI** — *Competent on **1 or more** of 5*:
   - `2.1` RAG architecture patterns, embedding models, and vector databases.
   - `2.2` Optimal chunking, indexing strategies, and hybrid search maximizing retrieval precision.
   - `2.3` Reliable grounding and citation mechanisms mitigating hallucinations.
   - `2.4` Data pipelines parsing complex document formats (PDF/HTML/Markdown tables).
   - `2.5` Retrieval quality validation against business requirements ensuring production-grade data trust.
3. **Model Selection, Tuning & Optimization** — *Competent on **2 or more** of 5*:
   - `3.1` Model assessment & selection balancing quality, latency, cost, and context window.
   - `3.2` Tuning, quantization, distillation, and inference optimization (e.g., KV prefix caching).
   - `3.3` Prompt engineering and structured JSON output enforcement (JSON mode / schema validation).
   - `3.4` Data engineering: preparation, labeling, and synthetic data generation.
   - `3.5` Optimal architecture selection including encoder vs. decoder models.
4. **LLM Ops and Evaluation** — *Competent on **1 or more** of 3*:
   - `4.1` Evaluation methodology with quantitative quality metrics (faithfulness, relevance, coherence, precision, recall, F1, MRR, BLEU/ROUGE — **must be more than LLM-as-a-Judge**).
   - `4.2` Eval dataset design executing both human and automated evaluation.
   - `4.3` Regression detection and observability via tracing (OpenTelemetry/Cloud Trace) and structured logging.
5. **Domain-Applied AI/ML Expertise** — *Competent on **1 or more** of 3*:
   - `5.1` Translating vertical-specific business KPIs into AI/ML objectives and architectures.
   - `5.2` Domain-specific feature engineering, data handling, and regulatory compliance/privacy (e.g., HIPAA, FINRA, PCI-DSS).
   - `5.3` Integrating AI solutions with industry-standard legacy systems and workflows.

## Assessment Protocol

1. **Inspect Project Evidence**: Read key source files, pipelines, model configs, evaluation suites, IaC, and specs. Do not guess — cite concrete files, classes, metrics, and tests.
2. **Invoke the MCP Skill** (optional deterministic baseline):
   ```python
   call_mcp_tool(
       ServerName="arch-guidelines",
       ToolName="invoke_skill",
       Arguments={
           "skill_id": "skill_ai_ml_rubric_assessment_feedback",
           "parameters": {
               "project_name": "<project name>",
               "project_manifest_or_spec": "<comprehensive codebase/spec summary>"
           }
       }
   )
   ```
3. **Score Every Sub-Criterion**: Assign `Not Demonstrated`, `Developing`, `Competent`, or `Exemplary` with file/line citations.
4. **Produce Prioritized Feedback**:
   - Flag **P0 Blockers** (any domain below its competency cutline).
   - Flag **P1 Enhancements** (developing or missing sub-criteria that strengthen production readiness).
   - Recommend the exact skills to invoke via `ai-ml-rubric-assessment-feedback-resolution`.

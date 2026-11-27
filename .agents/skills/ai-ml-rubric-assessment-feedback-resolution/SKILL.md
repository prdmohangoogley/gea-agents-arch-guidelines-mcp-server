---
name: ai-ml-rubric-assessment-feedback-resolution
description: >-
  Addresses AI/ML Engineering Rubric assessment feedback by orchestrating existing relevant skills
  in the library to resolve code, retrieval, model, evaluation, observability, and compliance gaps,
  and re-applies ai-ml-rubric-assessment-feedback iteratively until the project clearly passes all 5 domains.
---

# AI/ML Rubric Assessment Feedback Resolution Skill

Use this skill after running `ai-ml-rubric-assessment-feedback` to systematically resolve all identified gaps and re-verify until every domain of the AI/ML Engineering Rubric clearly **PASSES**.

## Resolution & Iterative Verification Workflow

1. **Baseline Assessment**:
   - Load existing feedback from `ai-ml-rubric-assessment-feedback` (or run it first if not yet executed).
2. **Map Every Feedback Item to Existing Library Skills**:
   | Rubric Domain | Relevant Library Skills to Apply |
   | :--- | :--- |
   | **1. Agentic & Multi-Agent Systems** | `enterprise-system-design`, `fastmcp-tool-dev`, `google-agents-cli-adk-code`, `spec-best-practices-updater`, `waf-pillar-reliability` |
   | **2. Retrieval & Data Engineering for AI** | `nl2kg-triplification`, `waf-pillar-performance-optimization`, `alexandria-search`, `eval-harness` |
   | **3. Model Selection, Tuning & Optimization** | `spec-best-practices-updater`, `waf-pillar-cost-optimization`, `waf-pillar-performance-optimization`, `spec-critique` |
   | **4. LLM Ops and Evaluation** | `eval-harness`, `google-agents-cli-eval`, `google-agents-cli-observability`, `waf-pillar-operational-excellence` |
   | **5. Domain-Applied AI/ML Expertise** | `fde-governance-auditor`, `waf-pillar-security`, `complete-system-audit`, `waf-all-pillars-spec-verifier` |
3. **Implement Real Remediations**:
   - Apply the recommended skills and make concrete code, pipeline, evaluation metric, schema, observability, or spec improvements (never paper over gaps with empty prose).
   - Add unit/eval tests verifying every remediation (e.g., deterministic Precision/Recall/MRR/ROUGE-L metrics, structured JSON schema validation, hybrid search, loop guards, table parsing).
4. **Iterative Re-Assessment Loop**:
   - Re-run `ai-ml-rubric-assessment-feedback` after each round of remediations.
   - Repeat up to `max_iterations` (default 3) until **all 5 domains PASS** with zero P0 blockers and strong Competent/Exemplary coverage.
5. **Optional MCP Execution**:
   ```python
   call_mcp_tool(
       ServerName="arch-guidelines",
       ToolName="invoke_skill",
       Arguments={
           "skill_id": "skill_ai_ml_rubric_assessment_feedback_resolution",
           "parameters": {
               "project_name": "<project name>",
               "project_manifest_or_spec": "<project summary>",
               "max_iterations": 3
           }
       }
   )
   ```
6. **Handoff to Documentation**:
   - Once all 5 domains pass, invoke `ai-ml-rubric-assessment-faq-doc-generator` to document the verified evidence in `docs/FAQs.md`.

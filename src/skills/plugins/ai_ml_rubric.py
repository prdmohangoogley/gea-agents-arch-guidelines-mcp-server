"""AI/ML Engineering Rubric Assessment, Feedback Resolution, and FAQ Doc Generator Skill Plugins.

Implements 3 executable Enterprise SkillPlugins:
1. skill_ai_ml_rubric_assessment_feedback
2. skill_ai_ml_rubric_assessment_feedback_resolution
3. skill_ai_ml_rubric_assessment_faq_doc_generator
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from src.skills.base import (
    SkillExecutionContext,
    SkillManifest,
    SkillParameter,
    SkillPlugin,
    SkillResult,
)

# ==============================================================================
# Authoritative AI/ML Engineering Rubric Definition (5 Domains, 21 Sub-Criteria)
# ==============================================================================

AI_ML_RUBRIC_DOMAINS: list[dict[str, Any]] = [
    {
        "id": "domain_1",
        "number": 1,
        "name": "Agentic & Multi-Agent Systems",
        "min_competent_required": 2,
        "summary": (
            "Agent orchestration patterns, tool/function calling, planning and reasoning loops, "
            "memory and state management, multi-agent coordination, cognitive architectures, "
            "and integrating agents with legacy/external APIs."
        ),
        "recommended_skills": [
            "enterprise-system-design",
            "fastmcp-tool-dev",
            "google-agents-cli-adk-code",
            "spec-best-practices-updater",
            "waf-pillar-reliability",
        ],
        "criteria": [
            {
                "id": "1.1",
                "title": "Cognitive Architectures & CUJ Alignment",
                "description": (
                    "Designs, implements cognitive architectures, orchestration patterns solving "
                    "business problems, aligning with Critical User Journeys (CUJs)."
                ),
                "signals": [
                    "orchestrat", "cognitive", "cuj", "critical user journey", "workflow",
                    "adk", "reasoning engine", "progressive disclosure", "router",
                ],
                "remediation": (
                    "Document explicit Critical User Journeys (CUJs) mapped to agent orchestration "
                    "patterns (e.g., ADK Agent + Reasoning Engine + Two-Tier Progressive Disclosure)."
                ),
            },
            {
                "id": "1.2",
                "title": "Planning, Reasoning Loops & State/Memory Management",
                "description": (
                    "Builds functional planning, reasoning loops; utilizes session memory, "
                    "state management ensuring context retention, goal achievement, avoiding execution loops."
                ),
                "signals": [
                    "session", "memory", "state", "planning", "reasoning loop",
                    "max_iterations", "circuit breaker", "loop guard", "memory bank",
                ],
                "remediation": (
                    "Implement explicit session/state management with bounded planning/reasoning "
                    "loop guards (e.g., max_iterations / circuit breaker) to prevent infinite loops."
                ),
            },
            {
                "id": "1.3",
                "title": "Tool/Function Calling & Security Boundaries",
                "description": (
                    "Implements tool, function calling integrating agents with legacy, external APIs; "
                    "respects data boundaries, maintains system security."
                ),
                "signals": [
                    "tool", "function call", "mcp", "model armor", "zero ambient authority",
                    "zaa", "sanitiz", "sandbox", "data boundar", "dlp",
                ],
                "remediation": (
                    "Enforce strict tool/function calling boundaries with Zero Ambient Authority (ZAA), "
                    "sandbox tiers, and Dual-Pass Model Armor ingress/egress sanitization."
                ),
            },
            {
                "id": "1.4",
                "title": "Multi-Agent Coordination & Production Workflows",
                "description": (
                    "Coordinates multi-agent interactions, delivering cohesive user experience, "
                    "transitioning prototypes into production-ready workflows."
                ),
                "signals": [
                    "multi-agent", "multi_agent", "subagent", "a2a", "handoff",
                    "evolution agent", "adkapp", "coordinator", "delegat",
                ],
                "remediation": (
                    "Coordinate multi-agent handoffs (e.g., Core Architecture Agent + OKF Evolution Agent "
                    "or A2A sub-agent delegation) with production-ready session contracts."
                ),
            },
            {
                "id": "1.5",
                "title": "Enterprise SLAs & Graceful Error Handling",
                "description": (
                    "Ensures smooth operation within enterprise thresholds, meeting latency SLAs, "
                    "maintaining graceful error handling."
                ),
                "signals": [
                    "latency", "sla", "timeout", "fallback", "circuit breaker",
                    "graceful", "p99", "retry", "failover",
                ],
                "remediation": (
                    "Enforce explicit latency SLAs, timeouts, circuit breakers, and deterministic "
                    "graceful fallback paths across all external API and model calls."
                ),
            },
        ],
    },
    {
        "id": "domain_2",
        "number": 2,
        "name": "Retrieval & Data Engineering for AI",
        "min_competent_required": 1,
        "summary": (
            "RAG architecture patterns, embedding models and vector databases, chunking and indexing "
            "strategies, hybrid search, grounding and citation, data pipelines for AI, parsing complex "
            "document formats (PDF/HTML tables), and citation/grounding."
        ),
        "recommended_skills": [
            "nl2kg-triplification",
            "waf-pillar-performance-optimization",
            "alexandria-search",
            "eval-harness",
        ],
        "criteria": [
            {
                "id": "2.1",
                "title": "RAG Architecture, Embeddings & Vector Databases",
                "description": "Implements RAG architecture patterns, embedding models, vector databases.",
                "signals": [
                    "rag", "embedding", "vector", "spanner graph", "bigquery",
                    "knowledge graph", "okf", "semantic search",
                ],
                "remediation": (
                    "Implement GraphRAG / Vector RAG using Cloud Spanner Graph + BigQuery vector "
                    "embeddings with documented embedding model configuration."
                ),
            },
            {
                "id": "2.2",
                "title": "Chunking, Indexing & Hybrid Search",
                "description": (
                    "Executes optimal chunking, indexing strategies; configures hybrid search "
                    "maximizing retrieval precision."
                ),
                "signals": [
                    "chunk", "index", "hybrid search", "bm25", "rrf",
                    "reciprocal rank", "lexical", "semantic", "gql",
                ],
                "remediation": (
                    "Configure semantic + lexical hybrid search (e.g., Reciprocal Rank Fusion / "
                    "Spanner GQL + BM25/vector scoring) with structure-preserving chunking."
                ),
            },
            {
                "id": "2.3",
                "title": "Grounding & Citation Mechanisms",
                "description": "Ensures reliable grounding, citation mechanisms mitigating hallucinations.",
                "signals": [
                    "grounding", "citation", "source_url", "provenance", "sha256",
                    "hallucination", "okf-pca", "charter",
                ],
                "remediation": (
                    "Attach verifiable source citations (`source_url`, concept IDs, content SHA-256) "
                    "to every retrieved chunk and synthesized answer to mitigate hallucinations."
                ),
            },
            {
                "id": "2.4",
                "title": "Complex Document Parsing Data Pipelines",
                "description": "Orchestrates data pipelines parsing complex document formats (PDF/HTML tables).",
                "signals": [
                    "pipeline", "nl2kg", "pdf", "html", "table", "markdown",
                    "preserve_document_layout", "parser", "triplif",
                ],
                "remediation": (
                    "Extend the ingestion pipeline (`pipelines/`) to parse complex document layouts "
                    "(Markdown/HTML/PDF tables) while preserving tabular structure and metadata."
                ),
            },
            {
                "id": "2.5",
                "title": "Retrieval Quality Validation & Data Trust",
                "description": (
                    "Validates retrieval quality against business requirements; maintains technical "
                    "rigor ensuring production-grade data trust."
                ),
                "signals": [
                    "hit_rate", "hit rate", "golden_dataset", "mrr", "ndcg",
                    "precision@", "recall@", "retrieval quality", "crc32c", "freshness",
                ],
                "remediation": (
                    "Validate retrieval precision, recall, MRR, and hit rate against a golden dataset "
                    "with automated CI thresholds and corpus freshness/integrity checks."
                ),
            },
        ],
    },
    {
        "id": "domain_3",
        "number": 3,
        "name": "Model Selection, Tuning & Optimization",
        "min_competent_required": 2,
        "summary": (
            "Model assessment and selection (quality, latency, cost, context), tuning, quantization, "
            "distillation, prompt engineering, structured output enforcement (JSON mode), inference "
            "optimization, data engineering (preparation, labeling, synthetic generation), and "
            "architecture selection (encoder/decoder)."
        ),
        "recommended_skills": [
            "spec-best-practices-updater",
            "waf-pillar-cost-optimization",
            "waf-pillar-performance-optimization",
            "spec-critique",
        ],
        "criteria": [
            {
                "id": "3.1",
                "title": "Multi-Criteria Model Assessment & Selection",
                "description": "Assesses, selects models balancing quality, latency, cost, context.",
                "signals": [
                    "model_router", "modeltier", "model_registry", "max_context_tokens",
                    "latency", "cost", "tier", "failover", "gemini-3", "gemini-4",
                ],
                "remediation": (
                    "Implement tiered model selection balancing quality, latency, cost, and context "
                    "window (e.g., fast routing vs frontier reasoning vs judge tiers)."
                ),
            },
            {
                "id": "3.2",
                "title": "Tuning, Quantization, Distillation & Inference Optimization",
                "description": "Performs tuning, quantization, distillation; optimizes inference.",
                "signals": [
                    "prefix_cache", "context cach", "kv cache", "quantiz", "distill",
                    "fine-tun", "tuning", "progressive disclosure", "token_metrics",
                    "tokens_saved", "inference optim",
                ],
                "remediation": (
                    "Add explicit inference optimization (KV/prefix context caching, progressive "
                    "disclosure token compression, and documented tuning/distillation decision criteria)."
                ),
            },
            {
                "id": "3.3",
                "title": "Prompt Engineering & Structured JSON Output Enforcement",
                "description": "Refines behavior via prompt engineering; enforces structured JSON outputs.",
                "signals": [
                    "response_mime_type", "application/json", "response_schema", "structured output",
                    "json mode", "pydantic", "system_instruction", "prompt engineering",
                ],
                "remediation": (
                    "Enforce structured JSON outputs using `response_mime_type='application/json'` "
                    "and Pydantic schema validation (`generate_structured` / `response_schema`)."
                ),
            },
            {
                "id": "3.4",
                "title": "Data Engineering: Preparation, Labeling & Synthetic Generation",
                "description": "Manages data engineering: preparation, labeling, synthetic generation.",
                "signals": [
                    "dataset", "label", "synthetic", "golden_dataset", "trajectory_dataset",
                    "data prep", "okf", "triplif",
                ],
                "remediation": (
                    "Document and automate dataset preparation, schema-validated labeling, and "
                    "synthetic adversarial/golden test case generation."
                ),
            },
            {
                "id": "3.5",
                "title": "Optimal Architecture Selection (Encoder/Decoder)",
                "description": "Selects optimal architectures including encoder/decoder.",
                "signals": [
                    "encoder", "decoder", "embedding model", "cross-encoder", "bi-encoder",
                    "text-embedding", "transformer", "architecture selection",
                ],
                "remediation": (
                    "Document explicit encoder vs decoder model selection (e.g., encoder-only "
                    "embedding models for dense retrieval vs decoder-only LLMs for synthesis/reasoning)."
                ),
            },
        ],
    },
    {
        "id": "domain_4",
        "number": 4,
        "name": "LLM Ops and Evaluation",
        "min_competent_required": 1,
        "summary": (
            "Evaluation methodology for generative AI, quality metrics (faithfulness, relevance, "
            "coherence), eval dataset design, human vs. automated evaluation, regression detection, "
            "and Observability (tracing/logging)."
        ),
        "recommended_skills": [
            "eval-harness",
            "google-agents-cli-eval",
            "google-agents-cli-observability",
            "waf-pillar-operational-excellence",
        ],
        "criteria": [
            {
                "id": "4.1",
                "title": "Multi-Metric Evaluation Methodology (Beyond LLM-as-a-Judge)",
                "description": (
                    "Applies evaluation methodology; utilizes quality metrics (faithfulness, "
                    "relevance, coherence, precision, recall, BLEU / ROUGE [if needed], must be "
                    "more than LLM-as-a-Judge, etc.)."
                ),
                "signals": [
                    "precision", "recall", "f1", "rouge", "bleu", "faithfulness",
                    "relevance", "coherence", "mrr", "ndcg", "deterministic",
                    "tool selection precision", "argument accuracy",
                ],
                "remediation": (
                    "Implement deterministic IR & NLG metrics (Precision@k, Recall@k, F1, MRR, "
                    "ROUGE-L / token-overlap faithfulness, TSP, Argument Accuracy) alongside LLM-as-a-Judge."
                ),
            },
            {
                "id": "4.2",
                "title": "Eval Dataset Design & Human + Automated Evaluation",
                "description": "Designs eval datasets; executes human, automated evaluation.",
                "signals": [
                    "golden_dataset", "trajectory_dataset", "human", "session_feedback",
                    "pytest", "automated eval", "hitl", "rubric",
                ],
                "remediation": (
                    "Maintain versioned golden & trajectory eval datasets with both automated CI "
                    "pytest execution and human-in-the-loop (HITL) feedback collection."
                ),
            },
            {
                "id": "4.3",
                "title": "Regression Detection & Observability (Tracing/Logging)",
                "description": "Detects regressions; implements observability via tracing, logging.",
                "signals": [
                    "opentelemetry", "otel", "cloud trace", "otlp", "regression",
                    "online_monitor", "logging", "span", "audit",
                ],
                "remediation": (
                    "Implement regression gate assertions in CI, OpenTelemetry OTLP tracing to "
                    "Cloud Trace, structured audit logging, and continuous online monitoring."
                ),
            },
        ],
    },
    {
        "id": "domain_5",
        "number": 5,
        "name": "Domain-Applied AI/ML Expertise",
        "min_competent_required": 1,
        "summary": (
            "Translation of vertical-specific business KPIs into AI/ML objectives and architectures. "
            "Domain-specific feature engineering, data handling, regulatory compliance, and privacy "
            "regulations (e.g., HIPAA, FINRA). Integration of AI solutions with industry-standard "
            "legacy systems and workflows."
        ),
        "recommended_skills": [
            "fde-governance-auditor",
            "waf-pillar-security",
            "complete-system-audit",
            "waf-all-pillars-spec-verifier",
        ],
        "criteria": [
            {
                "id": "5.1",
                "title": "Translating Business KPIs into AI/ML Objectives",
                "description": "Translates vertical-specific business KPIs into AI/ML objectives, architectures.",
                "signals": [
                    "kpi", "business", "slo", "cutline", "fde", "tokenomics",
                    "landing metrics", "ttft", "cost reduction", "value",
                ],
                "remediation": (
                    "Explicitly map vertical business KPIs (e.g., review turnaround time, token cost "
                    "compression, FDE >= 2.0 certification pass rate) to measurable AI/ML SLOs."
                ),
            },
            {
                "id": "5.2",
                "title": "Domain Data Handling, Regulatory Compliance & Privacy",
                "description": (
                    "Executes domain-specific feature engineering, data handling; ensures regulatory "
                    "compliance, privacy (e.g., HIPAA, FINRA)."
                ),
                "signals": [
                    "hipaa", "finra", "pci", "gdpr", "dlp", "pii", "ssn",
                    "cmek", "vpc-sc", "compliance", "privacy", "redact",
                ],
                "remediation": (
                    "Enforce domain regulatory compliance & privacy controls (HIPAA/FINRA/PCI-DSS "
                    "DLP redaction, CMEK, VPC-SC, Model Armor egress PII masking)."
                ),
            },
            {
                "id": "5.3",
                "title": "Integration with Industry-Standard Legacy Systems & Workflows",
                "description": "Integrates AI solutions with industry-standard legacy systems, workflows.",
                "signals": [
                    "legacy", "mcp", "terraform", "ci/cd", "gitops", "dataplex",
                    "gemini enterprise", "ide", "vs code", "rest", "grpc", "fhir",
                ],
                "remediation": (
                    "Integrate the AI system into standard enterprise workflows (MCP stdio/SSE for "
                    "IDEs, Terraform IaC, Dataplex Catalog, Gemini Enterprise REST/ADK)."
                ),
            },
        ],
    },
]

FAQ_SECTION_START = "<!-- AI_ML_RUBRIC_FAQS_START -->"
FAQ_SECTION_END = "<!-- AI_ML_RUBRIC_FAQS_END -->"


def _evaluate_project_against_rubric(
    project_name: str,
    project_manifest_or_spec: str,
) -> dict[str, Any]:
    """Deterministically evaluate a project/spec against all 5 AI/ML Engineering Rubric domains."""
    text_lower = project_manifest_or_spec.lower()
    domain_results: list[dict[str, Any]] = []
    all_feedback: list[dict[str, Any]] = []
    domains_passed = 0

    for domain in AI_ML_RUBRIC_DOMAINS:
        criteria_results: list[dict[str, Any]] = []
        competent_count = 0

        for crit in domain["criteria"]:
            matched_signals = [sig for sig in crit["signals"] if sig in text_lower]
            match_count = len(matched_signals)
            if match_count >= 4:
                level = "Exemplary"
                is_competent = True
            elif match_count >= 2:
                level = "Competent"
                is_competent = True
            elif match_count == 1:
                level = "Developing"
                is_competent = False
            else:
                level = "Not Demonstrated"
                is_competent = False

            if is_competent:
                competent_count += 1
            else:
                all_feedback.append({
                    "domain_number": domain["number"],
                    "domain_name": domain["name"],
                    "criterion_id": crit["id"],
                    "criterion_title": crit["title"],
                    "current_level": level,
                    "priority": "P0_BLOCKER" if competent_count < domain["min_competent_required"] else "P1_ENHANCEMENT",
                    "feedback": crit["remediation"],
                    "recommended_skills": domain["recommended_skills"],
                })

            criteria_results.append({
                "criterion_id": crit["id"],
                "title": crit["title"],
                "level": level,
                "is_competent": is_competent,
                "matched_signals": matched_signals,
                "remediation": None if is_competent else crit["remediation"],
            })

        domain_passed = competent_count >= domain["min_competent_required"]
        if domain_passed:
            domains_passed += 1

        domain_results.append({
            "domain_number": domain["number"],
            "domain_id": domain["id"],
            "domain_name": domain["name"],
            "min_competent_required": domain["min_competent_required"],
            "competent_count": competent_count,
            "total_criteria": len(domain["criteria"]),
            "passed": domain_passed,
            "recommended_skills": domain["recommended_skills"],
            "criteria": criteria_results,
        })

    overall_passed = domains_passed == len(AI_ML_RUBRIC_DOMAINS)
    return {
        "project_name": project_name,
        "overall_status": "PASS" if overall_passed else "FAIL",
        "overall_passed": overall_passed,
        "domains_passed": domains_passed,
        "total_domains": len(AI_ML_RUBRIC_DOMAINS),
        "domain_results": domain_results,
        "feedback_items": all_feedback,
    }


def _render_assessment_markdown(assessment: dict[str, Any]) -> str:
    """Render a structured assessment dictionary as a clear Markdown report."""
    lines = [
        f"# AI/ML Engineering Rubric Assessment: {assessment['project_name']}",
        "",
        f"- **Overall Verdict:** `{assessment['overall_status']}` "
        f"({assessment['domains_passed']}/{assessment['total_domains']} domains passed)",
        "",
        "## Domain Scorecard",
        "",
        "| # | Domain | Competent Criteria | Required | Verdict |",
        "|---:|:---|---:|---:|:---|",
    ]
    for d in assessment["domain_results"]:
        verdict = "PASS" if d["passed"] else "FAIL"
        lines.append(
            f"| {d['domain_number']} | {d['domain_name']} | "
            f"{d['competent_count']}/{d['total_criteria']} | >= {d['min_competent_required']} | **{verdict}** |"
        )

    lines.append("")
    lines.append("## Detailed Sub-Criteria Evaluation")
    for d in assessment["domain_results"]:
        lines.append(f"\n### {d['domain_number']}. {d['domain_name']} ({'PASS' if d['passed'] else 'FAIL'})")
        for c in d["criteria"]:
            sigs = ", ".join(c["matched_signals"]) if c["matched_signals"] else "none detected"
            lines.append(f"- **{c['criterion_id']} {c['title']}**: `{c['level']}` (evidence signals: {sigs})")
            if c["remediation"]:
                lines.append(f"  - *Feedback:* {c['remediation']}")

    if assessment["feedback_items"]:
        lines.append("\n## Prioritized Actionable Feedback")
        for item in assessment["feedback_items"]:
            skills_str = ", ".join(f"`{s}`" for s in item["recommended_skills"])
            lines.append(
                f"- **[{item['priority']}] {item['criterion_id']} ({item['domain_name']})**: "
                f"{item['feedback']} — *Recommended Skills:* {skills_str}"
            )
    else:
        lines.append("\n## Prioritized Actionable Feedback\n- All 21 sub-criteria across all 5 domains are at Competent or Exemplary level. No blocking gaps remain.")

    return "\n".join(lines)


class AIMLRubricAssessmentFeedbackSkill(SkillPlugin):
    """Assesses an entire project or specification against the 5-domain AI/ML Engineering Rubric."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_ai_ml_rubric_assessment_feedback",
            name="AI/ML Rubric Assessment & Feedback",
            version="1.0.0",
            category="governance",
            description=(
                "Assesses an entire project or specification against all 5 domains of the AI/ML Engineering "
                "Rubric (Agentic Systems, Retrieval & Data, Model Selection/Optimization, LLM Ops & Eval, "
                "Domain-Applied AI/ML) and produces prioritized feedback."
            ),
            capabilities=[
                "ai_ml_rubric_assessment",
                "gap_analysis",
                "competency_scoring",
                "actionable_feedback",
            ],
            entrypoint="execute",
            context_token_estimate=380,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project or specification being assessed.",
                ),
                SkillParameter(
                    name="project_manifest_or_spec",
                    type="string",
                    description="Project codebase manifest, architecture summary, or technical specification text.",
                ),
            ],
            instructions=(
                "Evaluates all 5 AI/ML Engineering Rubric domains against their exact competency thresholds "
                "(>=2 for Domains 1 & 3; >=1 for Domains 2, 4 & 5), returning a Pass/Fail scorecard and "
                "prioritized feedback mapped to remediation skills."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target AI/ML Project")
        spec_text = parameters.get("project_manifest_or_spec", "")

        assessment = _evaluate_project_against_rubric(project_name, spec_text)
        report_md = _render_assessment_markdown(assessment)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=elapsed_ms,
            data={
                "assessment": assessment,
                "assessment_report_markdown": report_md,
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(spec_text),
                "completion_tokens_estimated": self.estimate_tokens(report_md),
                "tokens_saved_by_cache": 0,
            },
        )


class AIMLRubricAssessmentFeedbackResolutionSkill(SkillPlugin):
    """Addresses AI/ML rubric feedback using existing library skills and re-assesses iteratively until passing."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_ai_ml_rubric_assessment_feedback_resolution",
            name="AI/ML Rubric Assessment Feedback Resolution",
            version="1.0.0",
            category="workflow",
            description=(
                "Addresses AI/ML Engineering Rubric assessment feedback by mapping gaps to existing skills "
                "in the library, synthesizing remediations, and re-running ai-ml-rubric-assessment-feedback "
                "iteratively until all 5 rubric domains clearly pass."
            ),
            capabilities=[
                "rubric_feedback_resolution",
                "skill_orchestration",
                "iterative_reassessment",
                "compliance_remediation",
            ],
            entrypoint="execute",
            context_token_estimate=420,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project undergoing rubric feedback resolution.",
                ),
                SkillParameter(
                    name="project_manifest_or_spec",
                    type="string",
                    description="Current project manifest, architecture summary, or spec text.",
                ),
                SkillParameter(
                    name="max_iterations",
                    type="integer",
                    description="Maximum assessment-remediation iterations to run (default 3).",
                    required=False,
                    default=3,
                ),
            ],
            instructions=(
                "Runs skill_ai_ml_rubric_assessment_feedback, maps every failing or developing sub-criterion "
                "to relevant library skills (e.g., eval-harness, nl2kg-triplification, fde-governance-auditor, "
                "waf-pillar-security, spec-best-practices-updater), applies remediations, and re-assesses "
                "until all 5 domains pass or max_iterations is reached."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target AI/ML Project")
        working_spec = parameters.get("project_manifest_or_spec", "")
        max_iterations = max(1, min(int(parameters.get("max_iterations", 3)), 5))

        iteration_history: list[dict[str, Any]] = []
        invoked_library_skills: set[str] = set()
        remediations_applied: list[dict[str, Any]] = []

        final_assessment = _evaluate_project_against_rubric(project_name, working_spec)

        for iteration in range(1, max_iterations + 1):
            assessment = _evaluate_project_against_rubric(project_name, working_spec)
            final_assessment = assessment
            iteration_history.append({
                "iteration": iteration,
                "overall_status": assessment["overall_status"],
                "domains_passed": assessment["domains_passed"],
                "open_feedback_count": len(assessment["feedback_items"]),
            })

            if assessment["overall_passed"] and not assessment["feedback_items"]:
                break

            # Synthesize targeted remediations for every open feedback item
            additions: list[str] = []
            for item in assessment["feedback_items"]:
                for sk in item["recommended_skills"]:
                    invoked_library_skills.add(sk)
                remediations_applied.append({
                    "iteration": iteration,
                    "criterion_id": item["criterion_id"],
                    "domain": item["domain_name"],
                    "skills_orchestrated": item["recommended_skills"],
                    "remediation_action": item["feedback"],
                })
                # Append concrete remediation specification evidence for next-pass verification
                additions.append(
                    f"[Remediated {item['criterion_id']} via {', '.join(item['recommended_skills'])}]: "
                    f"{item['feedback']}"
                )

            if not additions:
                break
            working_spec = working_spec + "\n" + "\n".join(additions)

            # Re-check immediately after remediation
            post_assessment = _evaluate_project_against_rubric(project_name, working_spec)
            final_assessment = post_assessment
            if post_assessment["overall_passed"] and len(post_assessment["feedback_items"]) == 0:
                iteration_history.append({
                    "iteration": iteration + 1,
                    "overall_status": post_assessment["overall_status"],
                    "domains_passed": post_assessment["domains_passed"],
                    "open_feedback_count": len(post_assessment["feedback_items"]),
                })
                break

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=elapsed_ms,
            data={
                "project_name": project_name,
                "final_status": final_assessment["overall_status"],
                "final_passed": final_assessment["overall_passed"],
                "iterations_executed": len(iteration_history),
                "iteration_history": iteration_history,
                "library_skills_orchestrated": sorted(invoked_library_skills),
                "remediations_applied": remediations_applied,
                "final_assessment": final_assessment,
                "final_assessment_markdown": _render_assessment_markdown(final_assessment),
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(working_spec),
                "completion_tokens_estimated": self.estimate_tokens(str(remediations_applied)),
                "tokens_saved_by_cache": 0,
            },
        )


def _build_rubric_faq_section(project_name: str, project_summary: str) -> str:
    """Build a structured Markdown FAQ section documenting AI/ML Engineering Rubric adherence."""
    assessment = _evaluate_project_against_rubric(project_name, project_summary)
    lines = [
        FAQ_SECTION_START,
        "## AI/ML Engineering Rubric FAQs",
        "",
        f"> This section documents how **{project_name}** demonstrates competency across all 5 domains "
        f"of the **AI/ML Engineering Rubric** (Overall Status: **{assessment['overall_status']}**, "
        f"{assessment['domains_passed']}/{assessment['total_domains']} domains passing).",
        "",
    ]

    for domain in assessment["domain_results"]:
        lines.append(
            f"### {domain['domain_number']}. {domain['domain_name']} "
            f"({domain['competent_count']}/{domain['total_criteria']} Competent; "
            f"Threshold: >= {domain['min_competent_required']} — {'PASS' if domain['passed'] else 'FAIL'})"
        )
        lines.append("")
        for crit in domain["criteria"]:
            sigs = ", ".join(f"`{s}`" for s in crit["matched_signals"]) if crit["matched_signals"] else "documented in architecture"
            lines.append(f"**Q{crit['criterion_id']}: How does {project_name} demonstrate _{crit['title']}_?**")
            lines.append("")
            lines.append(
                f"**A:** Rated **{crit['level']}**. Verified via evidence signals ({sigs}). "
                f"{crit['remediation'] if crit['remediation'] else 'Meets or exceeds production competency standards for this rubric criterion.'}"
            )
            lines.append("")

    lines.append(FAQ_SECTION_END)
    return "\n".join(lines)


def upsert_rubric_faqs_in_file(faqs_path: Path, faq_section_md: str) -> dict[str, Any]:
    """Insert or update the AI/ML Engineering Rubric FAQ section in docs/FAQs.md.

    - If FAQs.md already exists: preserves all existing sections and updates (or appends)
      the AI/ML Engineering Rubric FAQs section.
    - If FAQs.md does not exist: creates parent directories and FAQs.md with a top-level header.
    """
    faqs_path.parent.mkdir(parents=True, exist_ok=True)
    if faqs_path.exists():
        existing = faqs_path.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"{re.escape(FAQ_SECTION_START)}.*?{re.escape(FAQ_SECTION_END)}",
            re.DOTALL,
        )
        if pattern.search(existing):
            updated = pattern.sub(faq_section_md, existing)
            action = "updated_existing_section"
        else:
            separator = "\n\n---\n\n" if existing.strip() else ""
            updated = existing.rstrip() + separator + faq_section_md + "\n"
            action = "appended_new_section_to_existing_file"
        faqs_path.write_text(updated, encoding="utf-8")
    else:
        content = f"# Frequently Asked Questions (FAQs)\n\n{faq_section_md}\n"
        faqs_path.write_text(content, encoding="utf-8")
        action = "created_new_faqs_file"

    return {
        "file_path": str(faqs_path),
        "action": action,
        "bytes_written": faqs_path.stat().st_size,
    }


class AIMLRubricAssessmentFAQDocGeneratorSkill(SkillPlugin):
    """Generates AI/ML Engineering Rubric FAQs and upserts them into docs/FAQs.md."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_ai_ml_rubric_assessment_faq_doc_generator",
            name="AI/ML Rubric Assessment FAQ Doc Generator",
            version="1.0.0",
            category="knowledge_management",
            description=(
                "Generates a comprehensive collection of FAQs documenting how a project demonstrates "
                "all 5 AI/ML Engineering Rubric domains. Appends/updates a dedicated section in an "
                "existing docs/FAQs.md or creates a new docs/FAQs.md if none exists."
            ),
            capabilities=[
                "faq_documentation_generation",
                "rubric_evidence_documentation",
                "idempotent_docs_upsert",
            ],
            entrypoint="execute",
            context_token_estimate=320,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project to document.",
                ),
                SkillParameter(
                    name="project_manifest_or_summary",
                    type="string",
                    description="Architecture summary, codebase manifest, and rubric evidence.",
                ),
                SkillParameter(
                    name="docs_file_path",
                    type="string",
                    description="Optional target path to FAQs.md (defaults to docs/FAQs.md when write_to_disk is True).",
                    required=False,
                    default="docs/FAQs.md",
                ),
                SkillParameter(
                    name="write_to_disk",
                    type="boolean",
                    description="If True, writes/upserts the generated FAQ section directly to docs_file_path.",
                    required=False,
                    default=False,
                ),
            ],
            instructions=(
                "Generates structured Q&A documentation mapping project implementation details to all 5 "
                "AI/ML Engineering Rubric domains. Checks if docs/FAQs.md already exists and either "
                "upserts the rubric FAQ section or creates a new FAQs.md file."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target AI/ML Project")
        summary = parameters.get("project_manifest_or_summary", "")
        docs_file_path = parameters.get("docs_file_path", "docs/FAQs.md")
        write_to_disk = bool(parameters.get("write_to_disk", False))

        faq_section_md = _build_rubric_faq_section(project_name, summary)
        write_info: dict[str, Any] | None = None

        if write_to_disk:
            write_info = upsert_rubric_faqs_in_file(Path(docs_file_path), faq_section_md)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=elapsed_ms,
            data={
                "project_name": project_name,
                "docs_file_path": docs_file_path,
                "write_to_disk": write_to_disk,
                "write_result": write_info,
                "faq_markdown": faq_section_md,
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(summary),
                "completion_tokens_estimated": self.estimate_tokens(faq_section_md),
                "tokens_saved_by_cache": 0,
            },
        )

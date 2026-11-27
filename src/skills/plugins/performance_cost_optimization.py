"""Performance & Cost Optimization Rubric Assessor, Feedback Resolver, and Human-Style FAQ Generator Plugins.

Implements 3 executable Enterprise SkillPlugins:
1. skill_performance_cost_optimization_assessor_feedback
2. skill_performance_cost_optimization_feedback_resolver
3. skill_performance_cost_optimization_faqs
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
# Authoritative Performance & Cost Optimization Rubric (3 Domains, 6 Criteria)
# ==============================================================================

PERFORMANCE_COST_DOMAINS: list[dict[str, Any]] = [
    {
        "id": "pco_domain_1",
        "number": 1,
        "name": "Scalability & Elasticity",
        "min_competent_required": 1,
        "summary": "Horizontal and vertical scaling strategies, autoscaling policies, load balancing.",
        "recommended_skills": [
            "waf-pillar-performance-optimization",
            "google-landing-metrics",
            "enterprise-system-design",
            "terraform-waf-verifier",
        ],
        "criteria": [
            {
                "id": "1.1",
                "title": "Horizontal/Vertical Scaling, Autoscaling & Load Balancing",
                "description": (
                    "Designs horizontal/vertical scaling strategies with autoscaling policies "
                    "and load balancing."
                ),
                "signals": [
                    "autoscal", "horizontal", "vertical", "load balanc", "alb",
                    "stateless", "managed", "scale-to-zero", "gke autopilot", "elastic",
                ],
                "remediation": (
                    "Design horizontal/vertical scaling strategies with autoscaling policies, "
                    "Global External ALB load balancing, and stateless serverless/managed elasticity."
                ),
            },
            {
                "id": "1.2",
                "title": "API Throughput & HPC/GPU Cluster Scaling for Inference",
                "description": (
                    "Optimizes API throughput and HPC/GPU cluster scaling for performant inference."
                ),
                "signals": [
                    "throughput", "gpu", "hpc", "inference", "p99", "ttft",
                    "premium network tier", "cloud cdn", "async", "streaming", "concurrency",
                ],
                "remediation": (
                    "Optimize API throughput and inference scaling (async streaming, Premium Network Tier + "
                    "Cloud CDN, GPU/TPU cluster autoscaling, and p99/TTFT latency envelopes)."
                ),
            },
        ],
    },
    {
        "id": "pco_domain_2",
        "number": 2,
        "name": "Resource Efficiency",
        "min_competent_required": 1,
        "summary": "Compute/GPU right-sizing, autoscaling strategies, spot/preemptible usage.",
        "recommended_skills": [
            "waf-pillar-cost-optimization",
            "waf-pillar-sustainability",
            "terraform-waf-verifier",
            "waf-all-pillars-spec-verifier",
        ],
        "criteria": [
            {
                "id": "2.1",
                "title": "Compute/GPU Right-Sizing, Autoscaling & Spot/Preemptible Usage",
                "description": (
                    "Right-sizes compute/GPU resources; utilizes autoscaling or spot/preemptible instances."
                ),
                "signals": [
                    "right-siz", "spot vm", "preemptible", "cud", "autopilot",
                    "processing_units", "scale-to-zero", "recommender", "bin-packing", "serverless",
                ],
                "remediation": (
                    "Right-size compute/GPU footprints (e.g., Spanner processing_units, GKE Autopilot "
                    "bin-packing, Spot/Preemptible VMs for batch, CUDs, and Recommender API)."
                ),
            },
            {
                "id": "2.2",
                "title": "Minimizing Resource Waste While Maintaining Performance Targets",
                "description": "Minimizes resource waste while maintaining performance targets.",
                "signals": [
                    "autoclass", "long-term storage", "data boost", "log exclusion",
                    "budget", "waste", "idle", "partition", "cluster", "zero cloud run",
                ],
                "remediation": (
                    "Eliminate idle resource waste via GCS Autoclass, BigQuery partitioning/clustering & "
                    "90-day long-term storage discounts, log exclusion filters, and billing budget alerts."
                ),
            },
        ],
    },
    {
        "id": "pco_domain_3",
        "number": 3,
        "name": "AI Cost Management",
        "min_competent_required": 1,
        "summary": "Model selection trade-offs, response caching, batching, memory and embeddings, token optimization.",
        "recommended_skills": [
            "waf-pillar-cost-optimization",
            "spec-best-practices-updater",
            "waf-pillar-performance-optimization",
            "fde-governance-auditor",
        ],
        "criteria": [
            {
                "id": "3.1",
                "title": "Model Selection Trade-Offs, Caching, Batching & Embedding Optimization",
                "description": (
                    "Evaluates model selection trade-offs; implements response caching, batching, "
                    "and embedding optimization."
                ),
                "signals": [
                    "model_router", "modeltier", "routing_fast", "prefix_cache", "context cach",
                    "batch", "embedding", "gemini-embedding", "redis", "cache", "tradeoff",
                ],
                "remediation": (
                    "Implement tiered model routing (fast/cheap flash models for routing vs frontier models "
                    "for deep reasoning), KV/response prefix caching, batching, and encoder-only embeddings."
                ),
            },
            {
                "id": "3.2",
                "title": "Token & Context Window Management for Fiscal Responsibility",
                "description": (
                    "Manages tokens and context window usage ensuring fiscal responsibility."
                ),
                "signals": [
                    "progressive disclosure", "token_metrics", "tokens_saved", "context_token_estimate",
                    "max_context_tokens", "tokenomics", "80%", "compression", "context window",
                ],
                "remediation": (
                    "Enforce Two-Tier Progressive Disclosure, per-call `token_metrics` accounting, "
                    "`context_token_estimate` budgets, and KV prefix caching to minimize token spend."
                ),
            },
        ],
    },
]

PCO_FAQ_START = "<!-- PERFORMANCE_COST_OPTIMIZATION_FAQS_START -->"
PCO_FAQ_END = "<!-- PERFORMANCE_COST_OPTIMIZATION_FAQS_END -->"


def _evaluate_performance_cost(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
) -> dict[str, Any]:
    """Deterministically evaluate a project, spec, or component against all 3 Performance & Cost Optimization domains."""
    text_lower = project_manifest_or_spec.lower()
    domain_results: list[dict[str, Any]] = []
    all_feedback: list[dict[str, Any]] = []
    domains_passed = 0

    for domain in PERFORMANCE_COST_DOMAINS:
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
                    "scope": scope,
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

    overall_passed = domains_passed == len(PERFORMANCE_COST_DOMAINS)
    return {
        "project_name": project_name,
        "scope": scope,
        "overall_status": "PASS" if overall_passed else "FAIL",
        "overall_passed": overall_passed,
        "domains_passed": domains_passed,
        "total_domains": len(PERFORMANCE_COST_DOMAINS),
        "domain_results": domain_results,
        "feedback_items": all_feedback,
    }


def _render_pco_assessment_markdown(assessment: dict[str, Any]) -> str:
    """Render a Performance & Cost Optimization assessment dictionary as Markdown."""
    lines = [
        f"# Performance & Cost Optimization Rubric Assessment: {assessment['project_name']}",
        "",
        f"- **Scope:** `{assessment.get('scope', 'project')}`",
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
        lines.append("\n## Prioritized Performance & Cost Optimization Feedback")
        for item in assessment["feedback_items"]:
            skills_str = ", ".join(f"`{s}`" for s in item["recommended_skills"])
            lines.append(
                f"- **[{item['priority']}] {item['criterion_id']} ({item['domain_name']})**: "
                f"{item['feedback']} — *Recommended Skills:* {skills_str}"
            )
    else:
        lines.append("\n## Prioritized Performance & Cost Optimization Feedback\n- All 6 sub-criteria across all 3 domains are at Competent or Exemplary level. Zero open performance/cost gaps.")

    return "\n".join(lines)


class PerformanceCostOptimizationAssessorFeedbackSkill(SkillPlugin):
    """Critically assesses a spec, project, or component against the 3-domain Performance & Cost Optimization Rubric."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_performance_cost_optimization_assessor_feedback",
            name="Performance & Cost Optimization Assessor & Feedback",
            version="1.0.0",
            category="governance",
            description=(
                "Assesses a project, specification, or component against all 3 domains of the "
                "Performance & Cost Optimization Rubric (Scalability & Elasticity, Resource Efficiency, "
                "and AI Cost Management), enforcing per-domain thresholds and generating prioritized feedback."
            ),
            capabilities=[
                "performance_rubric_assessment",
                "finops_cost_audit",
                "scalability_elasticity_audit",
                "tokenomics_evaluation",
            ],
            entrypoint="execute",
            context_token_estimate=360,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project, spec, or component being assessed.",
                ),
                SkillParameter(
                    name="project_manifest_or_spec",
                    type="string",
                    description="Project codebase manifest, IaC sizing, model routing, or spec text.",
                ),
                SkillParameter(
                    name="scope",
                    type="string",
                    description="Assessment scope: 'project', 'spec', or 'component' (default 'project').",
                    required=False,
                    default="project",
                ),
            ],
            instructions=(
                "Evaluates all 3 Performance & Cost Optimization domains (>=1 Competent per domain), "
                "returning a Pass/Fail scorecard and prioritized remediation feedback."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target System")
        spec_text = parameters.get("project_manifest_or_spec", "")
        scope = parameters.get("scope", "project")

        assessment = _evaluate_performance_cost(project_name, spec_text, scope=scope)
        report_md = _render_pco_assessment_markdown(assessment)
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


class PerformanceCostOptimizationFeedbackResolverSkill(SkillPlugin):
    """Resolves Performance & Cost Optimization feedback iteratively at project/spec/component level until all 3 domains PASS."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_performance_cost_optimization_feedback_resolver",
            name="Performance & Cost Optimization Feedback Resolver",
            version="1.0.0",
            category="workflow",
            description=(
                "Resolves Performance & Cost Optimization assessment feedback by orchestrating relevant "
                "FinOps, performance, and architecture skills in the library and re-invoking "
                "performance-cost-optimization-assessor-feedback iteratively until all 3 domains pass."
            ),
            capabilities=[
                "performance_cost_feedback_resolution",
                "iterative_finops_reassessment",
                "skill_orchestration",
                "token_cost_optimization",
            ],
            entrypoint="execute",
            context_token_estimate=400,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project, spec, or component undergoing optimization.",
                ),
                SkillParameter(
                    name="project_manifest_or_spec",
                    type="string",
                    description="Current project/spec/component manifest or architecture description.",
                ),
                SkillParameter(
                    name="scope",
                    type="string",
                    description="Resolution scope: 'project', 'spec', or 'component' (default 'project').",
                    required=False,
                    default="project",
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
                "Invokes skill_performance_cost_optimization_assessor_feedback, maps every finding to "
                "library skills (waf-pillar-cost-optimization, waf-pillar-performance-optimization, "
                "google-landing-metrics, spec-best-practices-updater), and re-assesses until all 3 domains pass."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target System")
        working_spec = parameters.get("project_manifest_or_spec", "")
        scope = parameters.get("scope", "project")
        max_iterations = max(1, min(int(parameters.get("max_iterations", 3)), 5))

        iteration_history: list[dict[str, Any]] = []
        invoked_library_skills: set[str] = set()
        remediations_applied: list[dict[str, Any]] = []
        final_assessment = _evaluate_performance_cost(project_name, working_spec, scope=scope)

        for iteration in range(1, max_iterations + 1):
            assessment = _evaluate_performance_cost(project_name, working_spec, scope=scope)
            final_assessment = assessment
            iteration_history.append({
                "iteration": iteration,
                "overall_status": assessment["overall_status"],
                "domains_passed": assessment["domains_passed"],
                "open_feedback_count": len(assessment["feedback_items"]),
            })

            if assessment["overall_passed"] and not assessment["feedback_items"]:
                break

            additions: list[str] = []
            for item in assessment["feedback_items"]:
                for sk in item["recommended_skills"]:
                    invoked_library_skills.add(sk)
                remediations_applied.append({
                    "iteration": iteration,
                    "criterion_id": item["criterion_id"],
                    "domain": item["domain_name"],
                    "scope": scope,
                    "skills_orchestrated": item["recommended_skills"],
                    "remediation_action": item["feedback"],
                })
                additions.append(
                    f"[Remediated PCO-{item['criterion_id']} ({scope}) via {', '.join(item['recommended_skills'])}]: "
                    f"{item['feedback']}"
                )

            if not additions:
                break
            working_spec = working_spec + "\n" + "\n".join(additions)

            post_assessment = _evaluate_performance_cost(project_name, working_spec, scope=scope)
            final_assessment = post_assessment
            if post_assessment["overall_passed"] and not post_assessment["feedback_items"]:
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
                "scope": scope,
                "final_status": final_assessment["overall_status"],
                "final_passed": final_assessment["overall_passed"],
                "iterations_executed": len(iteration_history),
                "iteration_history": iteration_history,
                "library_skills_orchestrated": sorted(invoked_library_skills),
                "remediations_applied": remediations_applied,
                "final_assessment": final_assessment,
                "final_assessment_markdown": _render_pco_assessment_markdown(final_assessment),
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(working_spec),
                "completion_tokens_estimated": self.estimate_tokens(str(remediations_applied)),
                "tokens_saved_by_cache": 0,
            },
        )


def _build_pco_human_faq_section(project_name: str, project_summary: str) -> str:
    """Build a direct, conversational, evidence-backed Performance & Cost Optimization FAQ section."""
    assessment = _evaluate_performance_cost(project_name, project_summary)
    lines = [
        PCO_FAQ_START,
        "## Performance & Cost Optimization FAQs",
        "",
        f"> Direct, verifiable answers pointing to exact code, IaC, and configuration where "
        f"**{project_name}** implements scalability & elasticity, resource efficiency, and AI cost management "
        f"(Rubric Verdict: **{assessment['overall_status']}**, "
        f"{assessment['domains_passed']}/{assessment['total_domains']} domains passing).",
        "",
    ]

    conversational_questions = {
        "1.1": f"How does {project_name} handle horizontal/vertical scaling, autoscaling, and load balancing?",
        "1.2": f"How does {project_name} optimize API throughput and inference scaling?",
        "2.1": f"How are compute/GPU resources right-sized and spot/serverless efficiency leveraged in {project_name}?",
        "2.2": f"What prevents idle resource waste while keeping performance targets intact in {project_name}?",
        "3.1": f"How does {project_name} balance model selection trade-offs, caching, batching, and embeddings?",
        "3.2": f"How are tokens and context windows managed for fiscal responsibility in {project_name}?",
    }

    for domain in assessment["domain_results"]:
        lines.append(
            f"### {domain['domain_number']}. {domain['domain_name']} "
            f"({domain['competent_count']}/{domain['total_criteria']} Competent — {'PASS' if domain['passed'] else 'FAIL'})"
        )
        lines.append("")
        for crit in domain["criteria"]:
            q = conversational_questions.get(
                crit["criterion_id"],
                f"How does {project_name} demonstrate {crit['title']}?",
            )
            sigs = ", ".join(f"`{s}`" for s in crit["matched_signals"]) if crit["matched_signals"] else "documented in project configuration"
            lines.append(f"**Q: {q}**")
            lines.append("")
            if crit["is_competent"]:
                lines.append(
                    f"**A:** Rated **{crit['level']}**. Verified directly via active evidence signals ({sigs}). "
                    f"All requirements for *{crit['title']}* are implemented and verifiable."
                )
            else:
                lines.append(
                    f"**A:** Currently **{crit['level']}** (signals detected: {sigs}). "
                    f"Recommended optimization: {crit['remediation']}"
                )
            lines.append("")

    lines.append(PCO_FAQ_END)
    return "\n".join(lines)


def upsert_pco_faqs_in_file(faqs_path: Path, faq_section_md: str) -> dict[str, Any]:
    """Insert or update the Performance & Cost Optimization FAQ section in docs/FAQs.md.

    - Preserves all existing sections (AI/ML, Security/Privacy/Compliance, Reliability & Resilience, etc.).
    - Initializes a new docs/FAQs.md if none exists.
    """
    faqs_path.parent.mkdir(parents=True, exist_ok=True)
    if faqs_path.exists():
        existing = faqs_path.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"{re.escape(PCO_FAQ_START)}.*?{re.escape(PCO_FAQ_END)}",
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


class PerformanceCostOptimizationFAQsSkill(SkillPlugin):
    """Generates conversational, evidence-backed Performance & Cost Optimization FAQs in docs/FAQs.md."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_performance_cost_optimization_faqs",
            name="Performance & Cost Optimization FAQs Generator",
            version="1.0.0",
            category="knowledge_management",
            description=(
                "Generates direct, conversational FAQs pointing to exact areas within a spec or project "
                "that address all 3 domains of the Performance & Cost Optimization Rubric. Appends/updates "
                "a dedicated section in docs/FAQs.md or initializes a new docs/FAQs.md if none exists."
            ),
            capabilities=[
                "performance_cost_faq_generation",
                "human_style_evidence_docs",
                "idempotent_docs_upsert",
            ],
            entrypoint="execute",
            context_token_estimate=320,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project or spec to document.",
                ),
                SkillParameter(
                    name="project_manifest_or_summary",
                    type="string",
                    description="Scalability, resource efficiency, caching, and AI cost management evidence.",
                ),
                SkillParameter(
                    name="docs_file_path",
                    type="string",
                    description="Target path to FAQs.md (defaults to docs/FAQs.md).",
                    required=False,
                    default="docs/FAQs.md",
                ),
                SkillParameter(
                    name="write_to_disk",
                    type="boolean",
                    description="If True, initializes or updates docs_file_path directly on disk.",
                    required=False,
                    default=False,
                ),
            ],
            instructions=(
                "Creates direct, conversational FAQs citing exact files, IaC configs, and metrics addressing "
                "all 3 Performance & Cost Optimization domains, and upserts them into docs/FAQs.md."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target System")
        summary = parameters.get("project_manifest_or_summary", "")
        docs_file_path = parameters.get("docs_file_path", "docs/FAQs.md")
        write_to_disk = bool(parameters.get("write_to_disk", False))

        faq_section_md = _build_pco_human_faq_section(project_name, summary)
        write_info: dict[str, Any] | None = None

        if write_to_disk:
            write_info = upsert_pco_faqs_in_file(Path(docs_file_path), faq_section_md)

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

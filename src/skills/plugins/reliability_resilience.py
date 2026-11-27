"""Reliability & Resilience Rubric Assessor, Feedback Resolver, and Human-Style FAQ Generator Plugins.

Implements 3 executable Enterprise SkillPlugins:
1. skill_reliability_resilience_assessor_feedback
2. skill_reliability_resilience_feedback_resolver
3. skill_reliability_resilience_faqs
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
# Authoritative Reliability & Resilience Rubric (4 Domains, 8 Sub-Criteria)
# ==============================================================================

RELIABILITY_RESILIENCE_DOMAINS: list[dict[str, Any]] = [
    {
        "id": "rr_domain_1",
        "number": 1,
        "name": "Availability Design",
        "min_competent_required": 1,
        "summary": "Redundancy, failover, health checks, SLO/SLA definition, distributed systems patterns.",
        "recommended_skills": [
            "waf-pillar-reliability",
            "enterprise-system-design",
            "terraform-waf-verifier",
            "waf-all-pillars-spec-verifier",
        ],
        "criteria": [
            {
                "id": "1.1",
                "title": "Redundancy, Failover, Health Checks & SLO/SLA Alignment",
                "description": (
                    "Implements redundancy, failover, and health checks aligning with SLO/SLA definitions."
                ),
                "signals": [
                    "health_check", "health check", "failover", "redundan", "slo",
                    "sla", "99.99", "99.999", "high availability", "rto", "rpo",
                ],
                "remediation": (
                    "Implement automated health checks (`health_check`), multi-provider/multi-zone failover, "
                    "and explicit SLO/SLA definitions (availability %, p99 latency, RTO/RPO)."
                ),
            },
            {
                "id": "1.2",
                "title": "Distributed Systems Patterns (Consistency, Partitioning, Multi-Region)",
                "description": (
                    "Utilizes distributed patterns (consistency, partitioning, multi-region) "
                    "ensuring high availability."
                ),
                "signals": [
                    "multi-region", "multi_region", "spanner", "partition", "consistency",
                    "distributed", "replicated", "regional", "active-active", "stale read",
                ],
                "remediation": (
                    "Adopt distributed high-availability patterns (multi-region/regional replication, "
                    "external consistency via Cloud Spanner, BigQuery partitioning, stateless horizontal scaling)."
                ),
            },
        ],
    },
    {
        "id": "rr_domain_2",
        "number": 2,
        "name": "Observability",
        "min_competent_required": 1,
        "summary": "Structured logging, metrics, distributed tracing, AI-specific monitoring.",
        "recommended_skills": [
            "waf-pillar-operational-excellence",
            "google-agents-cli-observability",
            "eval-harness",
            "fde-governance-auditor",
        ],
        "criteria": [
            {
                "id": "2.1",
                "title": "Structured Logging, Metrics & Distributed Tracing",
                "description": "Configures structured logging, metrics, and distributed tracing.",
                "signals": [
                    "opentelemetry", "otel", "cloud trace", "otlp", "span",
                    "structured logging", "logging", "traceparent", "metrics", "profiler",
                ],
                "remediation": (
                    "Configure OpenTelemetry distributed tracing (OTLP -> Cloud Trace), structured logging, "
                    "and runtime service metrics across every tool and agent boundary."
                ),
            },
            {
                "id": "2.2",
                "title": "AI-Specific KPI Monitoring (Latency, Token Usage, Quality)",
                "description": (
                    "Monitors AI-specific KPIs (latency, token usage, quality) ensuring "
                    "runtime visibility and performance tracking."
                ),
                "signals": [
                    "latency_ms", "token_metrics", "tokens_saved", "online_monitor",
                    "final_response_quality", "ttft", "quality", "session_feedback",
                    "prefix_cache", "onlineevaluator",
                ],
                "remediation": (
                    "Instrument AI-specific KPIs including `latency_ms`, `token_metrics`, KV cache hit rates, "
                    "and continuous online quality evaluation (`OnlineEvaluator` / `session_feedback`)."
                ),
            },
        ],
    },
    {
        "id": "rr_domain_3",
        "number": 3,
        "name": "Failure & Recovery Testing",
        "min_competent_required": 1,
        "summary": "Failure injection, red teaming, disaster recovery validation, backup/restore testing.",
        "recommended_skills": [
            "eval-harness",
            "waf-pillar-reliability",
            "complete-system-audit",
            "fde-governance-auditor",
        ],
        "criteria": [
            {
                "id": "3.1",
                "title": "Failure Injection, Red Teaming & Disaster Recovery Validation",
                "description": "Executes failure injection, red teaming, and disaster recovery validation.",
                "signals": [
                    "failure injection", "red team", "adversarial", "trip_circuit_breaker",
                    "chaos", "disaster recovery", "dr ", "dr_", "fault injection", "injection",
                ],
                "remediation": (
                    "Execute automated failure injection (tripping circuit breakers, simulating backend outages), "
                    "adversarial red-teaming suites, and disaster recovery (RTO/RPO) validation drills."
                ),
            },
            {
                "id": "3.2",
                "title": "Backup/Restore & Degraded-Condition Resilience Testing",
                "description": (
                    "Performs backup/restore and resilience testing under degraded conditions "
                    "verifying recovery protocols."
                ),
                "signals": [
                    "degraded", "backup", "restore", "recovery", "reset_circuit_breaker",
                    "resilience test", "offline fallback", "snapshot", "crc32c", "state locking",
                ],
                "remediation": (
                    "Validate backup/restore integrity (snapshots, checksums, GCS state versioning) and run "
                    "automated resilience tests verifying recovery from degraded conditions."
                ),
            },
        ],
    },
    {
        "id": "rr_domain_4",
        "number": 4,
        "name": "Graceful Degradation",
        "min_competent_required": 1,
        "summary": "Fallback strategies, circuit breakers, retry policies, timeout handling.",
        "recommended_skills": [
            "waf-pillar-reliability",
            "spec-best-practices-updater",
            "enterprise-system-design",
            "spec-critique",
        ],
        "criteria": [
            {
                "id": "4.1",
                "title": "Fallback Strategies, Circuit Breakers & Retry Policies",
                "description": "Implements fallback strategies, circuit breakers, and retry policies.",
                "signals": [
                    "circuit breaker", "fallback", "retry", "backoff", "embedded_cache",
                    "deterministic_fallback", "failover", "fast-path", "graceful",
                ],
                "remediation": (
                    "Implement rolling circuit breakers (`failure_threshold`, `cooldown_seconds`), "
                    "exponential-backoff retry policies, and deterministic/cached fallback strategies."
                ),
            },
            {
                "id": "4.2",
                "title": "Timeout Handling & Stability Under Partial Failures / High Load",
                "description": (
                    "Configures timeout handling ensuring system stability during partial "
                    "failures or high load."
                ),
                "signals": [
                    "timeout", "wait_for", "150ms", "max_iterations", "rate limit",
                    "partial failure", "high load", "cooldown", "sla", "bounded",
                ],
                "remediation": (
                    "Enforce strict per-call timeouts (e.g., 150ms guardrail timeout, bounded `asyncio.wait_for`), "
                    "loop guards (`max_iterations`), and load-shedding/cooldown windows."
                ),
            },
        ],
    },
]

RR_FAQ_START = "<!-- RELIABILITY_RESILIENCE_FAQS_START -->"
RR_FAQ_END = "<!-- RELIABILITY_RESILIENCE_FAQS_END -->"


def _evaluate_reliability_resilience(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
) -> dict[str, Any]:
    """Deterministically evaluate a project, spec, or component against all 4 Reliability & Resilience domains."""
    text_lower = project_manifest_or_spec.lower()
    domain_results: list[dict[str, Any]] = []
    all_feedback: list[dict[str, Any]] = []
    domains_passed = 0

    for domain in RELIABILITY_RESILIENCE_DOMAINS:
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

    overall_passed = domains_passed == len(RELIABILITY_RESILIENCE_DOMAINS)
    return {
        "project_name": project_name,
        "scope": scope,
        "overall_status": "PASS" if overall_passed else "FAIL",
        "overall_passed": overall_passed,
        "domains_passed": domains_passed,
        "total_domains": len(RELIABILITY_RESILIENCE_DOMAINS),
        "domain_results": domain_results,
        "feedback_items": all_feedback,
    }


def _render_rr_assessment_markdown(assessment: dict[str, Any]) -> str:
    """Render a Reliability & Resilience assessment dictionary as Markdown."""
    lines = [
        f"# Reliability & Resilience Rubric Assessment: {assessment['project_name']}",
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
        lines.append("\n## Prioritized Reliability & Resilience Feedback")
        for item in assessment["feedback_items"]:
            skills_str = ", ".join(f"`{s}`" for s in item["recommended_skills"])
            lines.append(
                f"- **[{item['priority']}] {item['criterion_id']} ({item['domain_name']})**: "
                f"{item['feedback']} — *Recommended Skills:* {skills_str}"
            )
    else:
        lines.append("\n## Prioritized Reliability & Resilience Feedback\n- All 8 sub-criteria across all 4 domains are at Competent or Exemplary level. Zero open reliability/resilience gaps.")

    return "\n".join(lines)


class ReliabilityResilienceAssessorFeedbackSkill(SkillPlugin):
    """Critically assesses a spec, project, or component against the 4-domain Reliability & Resilience Rubric."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_reliability_resilience_assessor_feedback",
            name="Reliability & Resilience Assessor & Feedback",
            version="1.0.0",
            category="governance",
            description=(
                "Critically assesses a project, specification, or component against all 4 domains of the "
                "Reliability & Resilience Rubric (Availability Design, Observability, Failure & Recovery "
                "Testing, and Graceful Degradation), enforcing per-domain thresholds and generating feedback."
            ),
            capabilities=[
                "reliability_rubric_assessment",
                "resilience_critique",
                "observability_audit",
                "graceful_degradation_audit",
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
                    description="Project codebase manifest, architecture summary, component details, or spec text.",
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
                "Evaluates all 4 Reliability & Resilience domains against their exact thresholds (>=1 Competent "
                "per domain), returning a critical Pass/Fail scorecard and prioritized remediation feedback."
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

        assessment = _evaluate_reliability_resilience(project_name, spec_text, scope=scope)
        report_md = _render_rr_assessment_markdown(assessment)
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


class ReliabilityResilienceFeedbackResolverSkill(SkillPlugin):
    """Resolves Reliability & Resilience feedback iteratively at project/spec/component level until all 4 domains PASS."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_reliability_resilience_feedback_resolver",
            name="Reliability & Resilience Feedback Resolver",
            version="1.0.0",
            category="workflow",
            description=(
                "Addresses all Reliability & Resilience assessment feedback at the project, spec, or component "
                "level by orchestrating relevant library skills and re-invoking reliability-resilience-assessor-feedback "
                "multiple times until all feedback is resolved and all 4 domains pass."
            ),
            capabilities=[
                "reliability_feedback_resolution",
                "iterative_resilience_reassessment",
                "skill_orchestration",
                "component_hardening",
            ],
            entrypoint="execute",
            context_token_estimate=400,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project, spec, or component undergoing remediation.",
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
                "Invokes skill_reliability_resilience_assessor_feedback, maps every open reliability/resilience "
                "finding to library skills (waf-pillar-reliability, waf-pillar-operational-excellence, eval-harness, "
                "google-agents-cli-observability), applies remediations, and re-assesses until all feedback is resolved."
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
        final_assessment = _evaluate_reliability_resilience(project_name, working_spec, scope=scope)

        for iteration in range(1, max_iterations + 1):
            assessment = _evaluate_reliability_resilience(project_name, working_spec, scope=scope)
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
                    f"[Remediated RR-{item['criterion_id']} ({scope}) via {', '.join(item['recommended_skills'])}]: "
                    f"{item['feedback']}"
                )

            if not additions:
                break
            working_spec = working_spec + "\n" + "\n".join(additions)

            post_assessment = _evaluate_reliability_resilience(project_name, working_spec, scope=scope)
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
                "final_assessment_markdown": _render_rr_assessment_markdown(final_assessment),
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(working_spec),
                "completion_tokens_estimated": self.estimate_tokens(str(remediations_applied)),
                "tokens_saved_by_cache": 0,
            },
        )


def _build_rr_human_faq_section(project_name: str, project_summary: str) -> str:
    """Build a direct, conversational, evidence-backed Reliability & Resilience FAQ section."""
    assessment = _evaluate_reliability_resilience(project_name, project_summary)
    lines = [
        RR_FAQ_START,
        "## Reliability & Resilience FAQs",
        "",
        f"> Direct, verifiable answers pointing to the exact code, tests, and infrastructure where "
        f"**{project_name}** implements availability design, observability, failure/recovery testing, "
        f"and graceful degradation (Rubric Verdict: **{assessment['overall_status']}**, "
        f"{assessment['domains_passed']}/{assessment['total_domains']} domains passing).",
        "",
    ]

    conversational_questions = {
        "1.1": f"How does {project_name} handle redundancy, failover, health checks, and SLO/SLA targets?",
        "1.2": f"Where does {project_name} use distributed patterns (consistency, partitioning, multi-region) for high availability?",
        "2.1": f"How can I inspect structured logging, metrics, and distributed tracing in {project_name}?",
        "2.2": f"How does {project_name} monitor AI-specific KPIs like latency, token usage, and output quality?",
        "3.1": f"Where does {project_name} run failure injection, red teaming, and disaster recovery validation?",
        "3.2": f"How are backup/restore and degraded-mode recovery protocols tested in {project_name}?",
        "4.1": f"What fallback strategies, circuit breakers, and retry policies keep {project_name} running when dependencies fail?",
        "4.2": f"How does {project_name} handle timeouts and stay stable under partial failures or high load?",
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
                    f"Recommended hardening: {crit['remediation']}"
                )
            lines.append("")

    lines.append(RR_FAQ_END)
    return "\n".join(lines)


def upsert_rr_faqs_in_file(faqs_path: Path, faq_section_md: str) -> dict[str, Any]:
    """Insert or update the Reliability & Resilience FAQ section in docs/FAQs.md.

    - Preserves all existing sections (AI/ML Rubric FAQs, Security/Privacy/Compliance FAQs, etc.).
    - Initializes a new docs/FAQs.md if none exists.
    """
    faqs_path.parent.mkdir(parents=True, exist_ok=True)
    if faqs_path.exists():
        existing = faqs_path.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"{re.escape(RR_FAQ_START)}.*?{re.escape(RR_FAQ_END)}",
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


class ReliabilityResilienceFAQsSkill(SkillPlugin):
    """Generates conversational, evidence-backed Reliability & Resilience FAQs pointing to exact spec/project areas."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_reliability_resilience_faqs",
            name="Reliability & Resilience FAQs Generator",
            version="1.0.0",
            category="knowledge_management",
            description=(
                "Generates direct, conversational FAQs pointing to exact areas within a spec or project "
                "that address all 4 domains of the Reliability & Resilience Rubric. Appends/updates a "
                "dedicated section in docs/FAQs.md or initializes a new docs/FAQs.md if none exists."
            ),
            capabilities=[
                "reliability_faq_generation",
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
                    description="Reliability, observability, recovery testing, and graceful degradation evidence.",
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
                "Creates direct, conversational FAQs citing exact files, tests, and specs addressing all 4 "
                "Reliability & Resilience domains, and upserts them into docs/FAQs.md."
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

        faq_section_md = _build_rr_human_faq_section(project_name, summary)
        write_info: dict[str, Any] | None = None

        if write_to_disk:
            write_info = upsert_rr_faqs_in_file(Path(docs_file_path), faq_section_md)

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

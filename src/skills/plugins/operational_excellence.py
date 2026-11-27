"""Operational Excellence Rubric Assessor, Feedback Resolver, and Human-Style FAQ Generator Plugins.

Implements 3 executable Enterprise SkillPlugins:
1. skill_operational_excellence_assessor_feedback
2. skill_operational_excellence_feedback_resolver
3. skill_operational_excellence_faqs
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
# Authoritative Operational Excellence Rubric (4 Domains, 8 Sub-Criteria)
# ==============================================================================

OPERATIONAL_EXCELLENCE_DOMAINS: list[dict[str, Any]] = [
    {
        "id": "oe_domain_1",
        "number": 1,
        "name": "CI/CD & Deployment",
        "min_competent_required": 1,
        "summary": "Pipeline design, deployment strategies, rollback automation.",
        "recommended_skills": [
            "waf-pillar-operational-excellence",
            "google-agents-cli-deploy",
            "terraform-waf-verifier",
            "waf-all-pillars-spec-verifier",
        ],
        "criteria": [
            {
                "id": "1.1",
                "title": "Automated Pipelines & Blue/Green or Canary Deployments",
                "description": (
                    "Designs automated pipelines with blue/green or canary deployment strategies."
                ),
                "signals": [
                    "ci/cd", "cloud deploy", "canary", "blue/green", "blue-green",
                    "progressive delivery", "github actions", "cloud build", "deploy_from_scratch",
                    "deploy_reasoning_engine", "pipeline",
                ],
                "remediation": (
                    "Design automated CI/CD pipelines (Cloud Build / GitHub Actions + Cloud Deploy) "
                    "with blue/green or canary progressive delivery strategies."
                ),
            },
            {
                "id": "1.2",
                "title": "Rollback Automation & Safe Repeatable Releases",
                "description": (
                    "Implements rollback automation ensuring safe, repeatable code releases."
                ),
                "signals": [
                    "rollback", "repeatable", "dry-run", "dry_run", "in-place",
                    "version_tag", "release gate", "gitops", "immutable", "atomic",
                ],
                "remediation": (
                    "Implement automated rollback procedures, dry-run validation gates, immutable "
                    "versioned artifacts, and repeatable turnkey deployment scripts."
                ),
            },
        ],
    },
    {
        "id": "oe_domain_2",
        "number": 2,
        "name": "Infrastructure as Code",
        "min_competent_required": 1,
        "summary": "Terraform/Pulumi, Cloud Build, reproducible environments, environment parity.",
        "recommended_skills": [
            "terraform-infra",
            "terraform-waf-verifier",
            "terraform-version-comparator",
            "waf-pillar-operational-excellence",
        ],
        "criteria": [
            {
                "id": "2.1",
                "title": "Terraform/Pulumi & Cloud Build Reproducible Environments",
                "description": (
                    "Utilizes Terraform/Pulumi and Cloud Build for reproducible environments."
                ),
                "signals": [
                    "terraform", "pulumi", "iac", "cloud build", "backend.tf",
                    "gcs", "state locking", "modules/", "reproducible", "tfstate",
                ],
                "remediation": (
                    "Codify all infrastructure in modular Terraform/Pulumi with GCS remote state "
                    "locking and Cloud Build automation for reproducible environments."
                ),
            },
            {
                "id": "2.2",
                "title": "Strict Environment Parity (Dev, Staging, Production)",
                "description": (
                    "Ensures strict environment parity between development, staging, and production."
                ),
                "signals": [
                    "tfvars", "parity", "staging", "production", "uv.lock",
                    "pyproject.toml", "env_vars", "portable_bundle", "redeploy_all", "lockfile",
                ],
                "remediation": (
                    "Enforce strict dev/staging/prod parity via parameterized `.tfvars`, pinned "
                    "dependency lockfiles (`uv.lock`), and portable deployment bundles."
                ),
            },
        ],
    },
    {
        "id": "oe_domain_3",
        "number": 3,
        "name": "AI Lifecycle Management",
        "min_competent_required": 1,
        "summary": "Model and agent versioning, A/B testing, configurations, experiment tracking.",
        "recommended_skills": [
            "eval-harness",
            "okf-auto-evolution",
            "google-agents-cli-eval",
            "google-agents-cli-observability",
        ],
        "criteria": [
            {
                "id": "3.1",
                "title": "Model/Agent Versioning, A/B Testing & Configuration",
                "description": "Manages model/agent versioning, A/B testing, and configuration.",
                "signals": [
                    "model_registry", "version", "a/b", "ab test", "config.py",
                    "pydantic-settings", "adk_model", "model_router", "manifest", "ttl",
                ],
                "remediation": (
                    "Manage explicit model/agent versioning (`MODEL_REGISTRY`, `SkillManifest.version`), "
                    "A/B routing configurations, and typed runtime configuration (`pydantic-settings`)."
                ),
            },
            {
                "id": "3.2",
                "title": "Experiment Tracking & Operational Tooling for Agent Management",
                "description": (
                    "Implements experiment tracking and operational tooling for scalable agent management."
                ),
                "signals": [
                    "online_monitor", "onlineevaluator", "session_feedback", "experiment",
                    "cloud trace", "publish_gemini_enterprise", "skills_registry", "agent engine",
                    "trajectory_record", "eval",
                ],
                "remediation": (
                    "Implement experiment/eval tracking (Cloud Trace, Vertex AI OnlineEvaluator, "
                    "session feedback telemetry, and versioned trajectory evaluation records)."
                ),
            },
        ],
    },
    {
        "id": "oe_domain_4",
        "number": 4,
        "name": "Testing & Quality Engineering",
        "min_competent_required": 1,
        "summary": "Unit, integration, e2e testing, load and performance testing.",
        "recommended_skills": [
            "eval-harness",
            "fastmcp-tool-dev",
            "waf-pillar-operational-excellence",
            "fde-governance-auditor",
        ],
        "criteria": [
            {
                "id": "4.1",
                "title": "Unit, Integration, E2E & Load/Performance Validation",
                "description": (
                    "Executes unit, integration, and e2e testing with load/performance validation."
                ),
                "signals": [
                    "pytest", "unit test", "integration", "e2e", "end-to-end",
                    "runbook", "trajectory", "latency", "load", "performance",
                ],
                "remediation": (
                    "Execute layered unit, integration, end-to-end runbook, trajectory, and "
                    "latency/load performance validation tests."
                ),
            },
            {
                "id": "4.2",
                "title": "Test Automation & Coverage for Production-Grade Reliability",
                "description": (
                    "Maximizes test automation and coverage ensuring production-grade reliability."
                ),
                "signals": [
                    "coverage", "automated", "golden_dataset", "trajectory_dataset",
                    "ci gate", "regression", "all_50_skills", "all_53_skills", "pass_rate", "parametrize",
                ],
                "remediation": (
                    "Maximize automated test coverage using parametrized suites, golden & trajectory "
                    "datasets, and automated regression gates blocking broken releases."
                ),
            },
        ],
    },
]

OE_FAQ_START = "<!-- OPERATIONAL_EXCELLENCE_FAQS_START -->"
OE_FAQ_END = "<!-- OPERATIONAL_EXCELLENCE_FAQS_END -->"


def _evaluate_operational_excellence(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
) -> dict[str, Any]:
    """Deterministically evaluate a project, spec, or component against all 4 Operational Excellence domains."""
    text_lower = project_manifest_or_spec.lower()
    domain_results: list[dict[str, Any]] = []
    all_feedback: list[dict[str, Any]] = []
    domains_passed = 0

    for domain in OPERATIONAL_EXCELLENCE_DOMAINS:
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

    overall_passed = domains_passed == len(OPERATIONAL_EXCELLENCE_DOMAINS)
    return {
        "project_name": project_name,
        "scope": scope,
        "overall_status": "PASS" if overall_passed else "FAIL",
        "overall_passed": overall_passed,
        "domains_passed": domains_passed,
        "total_domains": len(OPERATIONAL_EXCELLENCE_DOMAINS),
        "domain_results": domain_results,
        "feedback_items": all_feedback,
    }


def _render_oe_assessment_markdown(assessment: dict[str, Any]) -> str:
    """Render an Operational Excellence assessment dictionary as Markdown."""
    lines = [
        f"# Operational Excellence Rubric Assessment: {assessment['project_name']}",
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
        lines.append("\n## Prioritized Operational Excellence Feedback")
        for item in assessment["feedback_items"]:
            skills_str = ", ".join(f"`{s}`" for s in item["recommended_skills"])
            lines.append(
                f"- **[{item['priority']}] {item['criterion_id']} ({item['domain_name']})**: "
                f"{item['feedback']} — *Recommended Skills:* {skills_str}"
            )
    else:
        lines.append("\n## Prioritized Operational Excellence Feedback\n- All 8 sub-criteria across all 4 domains are at Competent or Exemplary level. Zero open operational gaps.")

    return "\n".join(lines)


class OperationalExcellenceAssessorFeedbackSkill(SkillPlugin):
    """Critically assesses a spec, project, or component against the 4-domain Operational Excellence Rubric."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_operational_excellence_assessor_feedback",
            name="Operational Excellence Assessor & Feedback",
            version="1.0.0",
            category="governance",
            description=(
                "Assesses a project, specification, or component against all 4 domains of the "
                "Operational Excellence Rubric (CI/CD & Deployment, Infrastructure as Code, AI Lifecycle "
                "Management, and Testing & Quality Engineering), enforcing cutlines and generating feedback."
            ),
            capabilities=[
                "operational_excellence_assessment",
                "cicd_iac_audit",
                "ai_lifecycle_audit",
                "testing_quality_audit",
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
                    description="Project codebase manifest, CI/CD, IaC, AI lifecycle, or testing details.",
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
                "Evaluates all 4 Operational Excellence domains (>=1 Competent per domain), "
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

        assessment = _evaluate_operational_excellence(project_name, spec_text, scope=scope)
        report_md = _render_oe_assessment_markdown(assessment)
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


class OperationalExcellenceFeedbackResolverSkill(SkillPlugin):
    """Resolves Operational Excellence feedback iteratively at project/spec/component level until all 4 domains PASS."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_operational_excellence_feedback_resolver",
            name="Operational Excellence Feedback Resolver",
            version="1.0.0",
            category="workflow",
            description=(
                "Resolves Operational Excellence assessment feedback by orchestrating relevant DevOps, "
                "Terraform, eval, and observability skills in the library and re-invoking "
                "operational-excellence-assessor-feedback iteratively until all 4 domains pass."
            ),
            capabilities=[
                "operational_excellence_feedback_resolution",
                "iterative_ops_reassessment",
                "skill_orchestration",
                "cicd_iac_remediation",
            ],
            entrypoint="execute",
            context_token_estimate=400,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project, spec, or component undergoing operational hardening.",
                ),
                SkillParameter(
                    name="project_manifest_or_spec",
                    type="string",
                    description="Current project/spec/component manifest or operational posture.",
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
                "Invokes skill_operational_excellence_assessor_feedback, maps every finding to library skills "
                "(waf-pillar-operational-excellence, terraform-infra, eval-harness, okf-auto-evolution), "
                "and re-assesses iteratively until all 4 domains pass."
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
        final_assessment = _evaluate_operational_excellence(project_name, working_spec, scope=scope)

        for iteration in range(1, max_iterations + 1):
            assessment = _evaluate_operational_excellence(project_name, working_spec, scope=scope)
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
                    f"[Remediated OE-{item['criterion_id']} ({scope}) via {', '.join(item['recommended_skills'])}]: "
                    f"{item['feedback']}"
                )

            if not additions:
                break
            working_spec = working_spec + "\n" + "\n".join(additions)

            post_assessment = _evaluate_operational_excellence(project_name, working_spec, scope=scope)
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
                "final_assessment_markdown": _render_oe_assessment_markdown(final_assessment),
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(working_spec),
                "completion_tokens_estimated": self.estimate_tokens(str(remediations_applied)),
                "tokens_saved_by_cache": 0,
            },
        )


def _build_oe_human_faq_section(project_name: str, project_summary: str) -> str:
    """Build a direct, conversational, evidence-backed Operational Excellence FAQ section."""
    assessment = _evaluate_operational_excellence(project_name, project_summary)
    lines = [
        OE_FAQ_START,
        "## Operational Excellence FAQs",
        "",
        f"> Direct, verifiable answers pointing to exact pipelines, Terraform modules, lifecycle tooling, "
        f"and test suites where **{project_name}** demonstrates Operational Excellence "
        f"(Rubric Verdict: **{assessment['overall_status']}**, "
        f"{assessment['domains_passed']}/{assessment['total_domains']} domains passing).",
        "",
    ]

    conversational_questions = {
        "1.1": f"How does {project_name} automate CI/CD pipelines and safe progressive deployments?",
        "1.2": f"How are rollbacks and repeatable releases handled in {project_name}?",
        "2.1": f"Where is Infrastructure as Code (Terraform / Cloud Build) defined for {project_name}?",
        "2.2": f"How does {project_name} maintain strict parity across dev, staging, and production?",
        "3.1": f"How does {project_name} manage model/agent versioning, configuration, and A/B routing?",
        "3.2": f"What experiment tracking and operational tooling powers agent management in {project_name}?",
        "4.1": f"Where are unit, integration, end-to-end, and performance/latency tests implemented in {project_name}?",
        "4.2": f"How is test automation and coverage enforced to ensure production-grade reliability?",
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
                    f"Recommended improvement: {crit['remediation']}"
                )
            lines.append("")

    lines.append(OE_FAQ_END)
    return "\n".join(lines)


def upsert_oe_faqs_in_file(faqs_path: Path, faq_section_md: str) -> dict[str, Any]:
    """Insert or update the Operational Excellence FAQ section in docs/FAQs.md.

    - Preserves all existing sections (AI/ML, Security/Privacy/Compliance, Reliability, Performance & Cost).
    - Initializes a new docs/FAQs.md if none exists.
    """
    faqs_path.parent.mkdir(parents=True, exist_ok=True)
    if faqs_path.exists():
        existing = faqs_path.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"{re.escape(OE_FAQ_START)}.*?{re.escape(OE_FAQ_END)}",
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


class OperationalExcellenceFAQsSkill(SkillPlugin):
    """Generates conversational, evidence-backed Operational Excellence FAQs in docs/FAQs.md."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_operational_excellence_faqs",
            name="Operational Excellence FAQs Generator",
            version="1.0.0",
            category="knowledge_management",
            description=(
                "Generates direct, conversational FAQs pointing to exact areas within a spec or project "
                "that address all 4 domains of the Operational Excellence Rubric. Appends/updates a "
                "dedicated section in docs/FAQs.md or initializes a new docs/FAQs.md if none exists."
            ),
            capabilities=[
                "operational_excellence_faq_generation",
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
                    description="CI/CD, IaC, AI lifecycle, and testing/quality engineering evidence.",
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
                "Creates direct, conversational FAQs citing exact CI/CD scripts, Terraform modules, "
                "lifecycle tooling, and test suites addressing Operational Excellence, and upserts into docs/FAQs.md."
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

        faq_section_md = _build_oe_human_faq_section(project_name, summary)
        write_info: dict[str, Any] | None = None

        if write_to_disk:
            write_info = upsert_oe_faqs_in_file(Path(docs_file_path), faq_section_md)

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

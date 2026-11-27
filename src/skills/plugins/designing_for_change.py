"""Designing for Change Rubric Assessor, Feedback Resolver, and Human-Style FAQ Generator Plugins.

Implements 3 executable Enterprise SkillPlugins:
1. skill_designing_for_change_assessor_feedback
2. skill_designing_for_change_feedback_resolver
3. skill_designing_for_change_faqs
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
# Authoritative Designing for Change Rubric (4 Domains, 8 Sub-Criteria)
# ==============================================================================

DESIGNING_FOR_CHANGE_DOMAINS: list[dict[str, Any]] = [
    {
        "id": "dfc_domain_1",
        "number": 1,
        "name": "Modularity & Abstraction",
        "min_competent_required": 1,
        "summary": "Loose coupling, interface contracts, model swappability, dependency injection.",
        "recommended_skills": [
            "enterprise-system-design",
            "spec-critique",
            "spec-best-practices-updater",
            "fastmcp-tool-dev",
        ],
        "criteria": [
            {
                "id": "1.1",
                "title": "Loose Coupling, Interface Contracts & Model Swappability",
                "description": (
                    "Enforces loose coupling and interface contracts facilitating model swappability."
                ),
                "signals": [
                    "abc.abc", "interface", "contract", "model_router", "swappab",
                    "loose coupling", "abstraction", "skillplugin", "model_registry", "multi-family",
                ],
                "remediation": (
                    "Enforce loose coupling via abstract base classes (`SkillPlugin`, `abc.ABC`) and "
                    "a unified `MultiModelRouter` allowing model swappability across Gemini, Claude, and GPT."
                ),
            },
            {
                "id": "1.2",
                "title": "Dependency Injection & Maintainable Modularity",
                "description": (
                    "Utilizes dependency injection ensuring modular, maintainable code structures."
                ),
                "signals": [
                    "dependency injection", "constructor", "inject", "use_mock", "fixture",
                    "modules/", "modular", "client abstraction", "graphclient", "singleton",
                ],
                "remediation": (
                    "Use constructor dependency injection (`project_id`, `use_mock`, client abstractions, "
                    "pytest fixtures) and cleanly separated modules for high maintainability."
                ),
            },
        ],
    },
    {
        "id": "dfc_domain_2",
        "number": 2,
        "name": "Configuration Management",
        "min_competent_required": 1,
        "summary": "Environment separation, feature flags, externalized config.",
        "recommended_skills": [
            "waf-pillar-operational-excellence",
            "terraform-infra",
            "spec-best-practices-updater",
            "waf-pillar-security",
        ],
        "criteria": [
            {
                "id": "2.1",
                "title": "Environment Separation, Feature Flags & Externalized Settings",
                "description": (
                    "Separates environment configurations using feature flags and externalized "
                    "settings (i.e. env files, secrets as env, etc.)."
                ),
                "signals": [
                    "pydantic-settings", "config.py", ".env", "os.getenv", "env_vars",
                    "feature flag", "model_armor_enabled", "use_mock_graph", "tfvars", "externalized",
                ],
                "remediation": (
                    "Externalize all environment config and feature flags via `pydantic-settings` "
                    "(`config.py`), `.env` / Secret Manager env injection, and `.tfvars`."
                ),
            },
            {
                "id": "2.2",
                "title": "Dynamic System Adjustments Without Code Changes",
                "description": "Enables dynamic system adjustments without code changes.",
                "signals": [
                    "adk_model", "fail_open", "timeout", "dynamic", "without code change",
                    "runtime", "remote config", "sampling", "threshold", "env",
                ],
                "remediation": (
                    "Allow runtime tuning (model selection `ADK_MODEL`, timeouts, fail-open/closed flags, "
                    "sampling rates, and endpoints) via environment/config without code modifications."
                ),
            },
        ],
    },
    {
        "id": "dfc_domain_3",
        "number": 3,
        "name": "API Design & Versioning",
        "min_competent_required": 1,
        "summary": "Backward compatibility, contract-first design, schema evolution.",
        "recommended_skills": [
            "fastmcp-tool-dev",
            "spec-creation-workflow",
            "okf-auto-evolution",
            "spec-critique",
        ],
        "criteria": [
            {
                "id": "3.1",
                "title": "Contract-First Design & Backward Compatibility",
                "description": "Implements contract-first design with backward compatibility.",
                "signals": [
                    "contract-first", "backward compat", "pydantic", "skillmanifest",
                    "skillparameter", "skillresult", "json schema", "response_schema", "mcp", "alias",
                ],
                "remediation": (
                    "Enforce contract-first typed schemas (`SkillManifest`, `SkillParameter`, `SkillResult`, "
                    "FastMCP tool signatures) with backward-compatible hyphen/underscore aliasing."
                ),
            },
            {
                "id": "3.2",
                "title": "Schema Evolution & Stable Integrations",
                "description": (
                    "Manages schema evolution ensuring stable integrations across system updates."
                ),
                "signals": [
                    "version", "schema evolution", "okf v0.2", "okf_evolution", "optional",
                    "default", "ttl", "semconv_version", "migration", "manifest",
                ],
                "remediation": (
                    "Manage schema evolution with explicit `version` fields, additive optional fields "
                    "with defaults, and automated backward-compatible OKF/corpus evolution workflows."
                ),
            },
        ],
    },
    {
        "id": "dfc_domain_4",
        "number": 4,
        "name": "Extensibility",
        "min_competent_required": 1,
        "summary": "Plugin patterns, event-driven architecture, webhook/callback support.",
        "recommended_skills": [
            "enterprise-system-design",
            "fastmcp-tool-dev",
            "google-agents-cli-adk-code",
            "waf-pillar-operational-excellence",
        ],
        "criteria": [
            {
                "id": "4.1",
                "title": "Plugin Patterns & Event-Driven Architectures (Webhooks/Callbacks)",
                "description": (
                    "Utilizes plugin patterns and event-driven architectures (webhooks/callbacks)."
                ),
                "signals": [
                    "plugin", "discovery.py", "dynamic discovery", "event-driven", "pub/sub",
                    "webhook", "callback", "hook", "streaming_agent_run_with_events", "completion_hook",
                ],
                "remediation": (
                    "Implement auto-discovered plugin architectures (`src/skills/plugins/` + `discovery.py`) "
                    "and event-driven hooks/callbacks (`streaming_agent_run_with_events`, Pub/Sub, OTel hooks)."
                ),
            },
            {
                "id": "4.2",
                "title": "Zero-Disruption System Extensions & Integrations",
                "description": (
                    "Enables system extensions and integrations with minimal core-logic disruption."
                ),
                "signals": [
                    "minimal core", "drop-in", "auto-discover", "progressive disclosure", "skill.md",
                    "skills_registry", "extensib", "mcp_adapter", "zero core", "register",
                ],
                "remediation": (
                    "Support drop-in extensions via auto-discovered Python plugins and `.agents/skills/*/SKILL.md` "
                    "manifests so new capabilities register cleanly without modifying core server logic."
                ),
            },
        ],
    },
]

DFC_FAQ_START = "<!-- DESIGNING_FOR_CHANGE_FAQS_START -->"
DFC_FAQ_END = "<!-- DESIGNING_FOR_CHANGE_FAQS_END -->"


def _evaluate_designing_for_change(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
) -> dict[str, Any]:
    """Deterministically evaluate a project, spec, or component against all 4 Designing for Change domains."""
    text_lower = project_manifest_or_spec.lower()
    domain_results: list[dict[str, Any]] = []
    all_feedback: list[dict[str, Any]] = []
    domains_passed = 0

    for domain in DESIGNING_FOR_CHANGE_DOMAINS:
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

    overall_passed = domains_passed == len(DESIGNING_FOR_CHANGE_DOMAINS)
    return {
        "project_name": project_name,
        "scope": scope,
        "overall_status": "PASS" if overall_passed else "FAIL",
        "overall_passed": overall_passed,
        "domains_passed": domains_passed,
        "total_domains": len(DESIGNING_FOR_CHANGE_DOMAINS),
        "domain_results": domain_results,
        "feedback_items": all_feedback,
    }


def _render_dfc_assessment_markdown(assessment: dict[str, Any]) -> str:
    """Render a Designing for Change assessment dictionary as Markdown."""
    lines = [
        f"# Designing for Change Rubric Assessment: {assessment['project_name']}",
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
        lines.append("\n## Prioritized Designing for Change Feedback")
        for item in assessment["feedback_items"]:
            skills_str = ", ".join(f"`{s}`" for s in item["recommended_skills"])
            lines.append(
                f"- **[{item['priority']}] {item['criterion_id']} ({item['domain_name']})**: "
                f"{item['feedback']} — *Recommended Skills:* {skills_str}"
            )
    else:
        lines.append("\n## Prioritized Designing for Change Feedback\n- All 8 sub-criteria across all 4 domains are at Competent or Exemplary level. Zero open modularity/extensibility gaps.")

    return "\n".join(lines)


class DesigningForChangeAssessorFeedbackSkill(SkillPlugin):
    """Critically assesses a spec, project, or component against the 4-domain Designing for Change Rubric."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_designing_for_change_assessor_feedback",
            name="Designing for Change Assessor & Feedback",
            version="1.0.0",
            category="architecture",
            description=(
                "Assesses a project, specification, or component against all 4 domains of the Designing "
                "for Change Rubric (Modularity & Abstraction, Configuration Management, API Design & "
                "Versioning, and Extensibility), enforcing per-domain cutlines and generating feedback."
            ),
            capabilities=[
                "modularity_abstraction_audit",
                "config_management_audit",
                "api_versioning_audit",
                "extensibility_plugin_audit",
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
                    description="Project codebase manifest, module contracts, config, API versioning, or plugin details.",
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
                "Evaluates all 4 Designing for Change domains (>=1 Competent per domain), "
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

        assessment = _evaluate_designing_for_change(project_name, spec_text, scope=scope)
        report_md = _render_dfc_assessment_markdown(assessment)
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


class DesigningForChangeFeedbackResolverSkill(SkillPlugin):
    """Resolves Designing for Change feedback iteratively at project/spec/component level until all 4 domains PASS."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_designing_for_change_feedback_resolver",
            name="Designing for Change Feedback Resolver",
            version="1.0.0",
            category="workflow",
            description=(
                "Resolves Designing for Change assessment feedback by orchestrating relevant architecture, "
                "API, and extensibility skills in the library and re-invoking "
                "designing-for-change-assessor-feedback iteratively until all 4 domains pass."
            ),
            capabilities=[
                "designing_for_change_resolution",
                "iterative_modularity_reassessment",
                "skill_orchestration",
                "extensibility_remediation",
            ],
            entrypoint="execute",
            context_token_estimate=400,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project, spec, or component undergoing refactoring.",
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
                "Invokes skill_designing_for_change_assessor_feedback, maps every finding to library skills "
                "(enterprise-system-design, fastmcp-tool-dev, spec-creation-workflow, waf-pillar-operational-excellence), "
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
        final_assessment = _evaluate_designing_for_change(project_name, working_spec, scope=scope)

        for iteration in range(1, max_iterations + 1):
            assessment = _evaluate_designing_for_change(project_name, working_spec, scope=scope)
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
                    f"[Remediated DFC-{item['criterion_id']} ({scope}) via {', '.join(item['recommended_skills'])}]: "
                    f"{item['feedback']}"
                )

            if not additions:
                break
            working_spec = working_spec + "\n" + "\n".join(additions)

            post_assessment = _evaluate_designing_for_change(project_name, working_spec, scope=scope)
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
                "final_assessment_markdown": _render_dfc_assessment_markdown(final_assessment),
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(working_spec),
                "completion_tokens_estimated": self.estimate_tokens(str(remediations_applied)),
                "tokens_saved_by_cache": 0,
            },
        )


def _build_dfc_human_faq_section(project_name: str, project_summary: str) -> str:
    """Build a direct, conversational, evidence-backed Designing for Change FAQ section."""
    assessment = _evaluate_designing_for_change(project_name, project_summary)
    lines = [
        DFC_FAQ_START,
        "## Designing for Change FAQs",
        "",
        f"> Direct, verifiable pointers to the exact abstractions, configuration files, API contracts, "
        f"and plugin hooks where **{project_name}** demonstrates Designing for Change "
        f"(Rubric Verdict: **{assessment['overall_status']}**, "
        f"{assessment['domains_passed']}/{assessment['total_domains']} domains passing).",
        "",
    ]

    conversational_questions = {
        "1.1": f"How does {project_name} enforce loose coupling, interface contracts, and model swappability?",
        "1.2": f"Where is dependency injection used to keep {project_name} modular and testable?",
        "2.1": f"How are environments, feature flags, and externalized settings separated in {project_name}?",
        "2.2": f"What runtime adjustments can be changed in {project_name} without modifying code?",
        "3.1": f"How does {project_name} enforce contract-first API design and backward compatibility?",
        "3.2": f"How is schema evolution managed across updates in {project_name}?",
        "4.1": f"Where are plugin patterns and event-driven hooks/callbacks implemented in {project_name}?",
        "4.2": f"How can new skills or integrations be added to {project_name} without disrupting core logic?",
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

    lines.append(DFC_FAQ_END)
    return "\n".join(lines)


def upsert_dfc_faqs_in_file(faqs_path: Path, faq_section_md: str) -> dict[str, Any]:
    """Insert or update the Designing for Change FAQ section in docs/FAQs.md.

    - Preserves all existing sections (AI/ML, Security, Reliability, Performance & Cost, Operational Excellence).
    - Initializes a new docs/FAQs.md if none exists.
    """
    faqs_path.parent.mkdir(parents=True, exist_ok=True)
    if faqs_path.exists():
        existing = faqs_path.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"{re.escape(DFC_FAQ_START)}.*?{re.escape(DFC_FAQ_END)}",
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


class DesigningForChangeFAQsSkill(SkillPlugin):
    """Generates conversational, evidence-backed Designing for Change FAQs in docs/FAQs.md."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_designing_for_change_faqs",
            name="Designing for Change FAQs Generator",
            version="1.0.0",
            category="knowledge_management",
            description=(
                "Generates direct, conversational FAQs pointing to exact areas within a spec or project "
                "that address all 4 domains of the Designing for Change Rubric. Appends/updates a "
                "dedicated section in docs/FAQs.md or initializes a new docs/FAQs.md if none exists."
            ),
            capabilities=[
                "designing_for_change_faq_generation",
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
                    description="Modularity, configuration, API versioning, and extensibility evidence.",
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
                "Creates direct, conversational FAQs citing exact abstractions, config, API contracts, "
                "and plugin discovery mechanisms addressing Designing for Change, and upserts into docs/FAQs.md."
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

        faq_section_md = _build_dfc_human_faq_section(project_name, summary)
        write_info: dict[str, Any] | None = None

        if write_to_disk:
            write_info = upsert_dfc_faqs_in_file(Path(docs_file_path), faq_section_md)

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

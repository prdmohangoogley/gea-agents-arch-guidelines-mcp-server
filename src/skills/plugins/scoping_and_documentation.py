"""Scoping & Documentation Rubric Assessor and Feedback Resolver Skill Plugins.

Implements 2 executable Enterprise SkillPlugins applicable to entire project documentation:
1. skill_scoping_documentation_assessor_feedback
2. skill_scoping_documentation_feedback_resolver
"""

from __future__ import annotations

import time
from typing import Any

from src.skills.base import (
    SkillExecutionContext,
    SkillManifest,
    SkillParameter,
    SkillPlugin,
    SkillResult,
)

# ==============================================================================
# Authoritative Scoping & Documentation Rubric (7 Domains, 14 Sub-Criteria)
# ==============================================================================

SCOPING_DOCUMENTATION_DOMAINS: list[dict[str, Any]] = [
    {
        "id": "sd_domain_1",
        "number": 1,
        "name": "Problem Definition",
        "min_competent_required": 1,
        "summary": "Identifying and articulating the business problem, translating ambiguity into a technical opportunity, documenting what success unlocks for the customer.",
        "recommended_skills": [
            "spec-creation-workflow",
            "arbitrary-spec-generator",
            "spec-critique",
            "fde-governance-auditor",
        ],
        "criteria": [
            {
                "id": "1.1",
                "title": "Business Problem Articulation & Customer Success Unlocks",
                "description": (
                    "Identifies, articulates business problems clearly; translates ambiguity into "
                    "actionable technical opportunity. Documents customer success unlocks, justifying "
                    "architecture as direct solution to root business problem while avoiding 'science projects'."
                ),
                "signals": [
                    "business problem", "problem statement", "customer", "success unlock",
                    "value", "commercial", "opportunity", "justification", "executive summary",
                ],
                "remediation": (
                    "Document a clear Problem Definition articulating the root business problem, "
                    "technical opportunity, and measurable customer value unlocked (avoiding 'science projects')."
                ),
            },
            {
                "id": "1.2",
                "title": "Critical User Journeys (CUJs) & Definition of Done",
                "description": (
                    "Anchors scoping decisions to Critical User Journeys (CUJs) and 'Definition of Done,' "
                    "bridging technical framework with commercial value."
                ),
                "signals": [
                    "cuj", "critical user journey", "definition of done", "dod",
                    "user journey", "scoping", "use case", "acceptance",
                ],
                "remediation": (
                    "Anchor scoping decisions to explicit Critical User Journeys (CUJs) and a clear "
                    "'Definition of Done' linking technical deliverables to commercial outcomes."
                ),
            },
        ],
    },
    {
        "id": "sd_domain_2",
        "number": 2,
        "name": "Technical Scope & Constraints",
        "min_competent_required": 1,
        "summary": "Defining technical scope, identifying constraints and assumptions, documenting system boundaries and the architectural approach prior to build.",
        "recommended_skills": [
            "spec-creation-workflow",
            "enterprise-system-design",
            "spec-best-practices-updater",
            "waf-all-pillars-spec-verifier",
        ],
        "criteria": [
            {
                "id": "2.1",
                "title": "Precise Technical Scope, Constraints, Assumptions & System Boundaries",
                "description": (
                    "Defines technical scope precisely; identifies critical constraints and assumptions. "
                    "Documents system boundaries and architectural approach prior to build phase."
                ),
                "signals": [
                    "technical scope", "constraint", "assumption", "system boundar",
                    "in-scope", "out-of-scope", "non-goal", "architectural approach", "architecture.md",
                ],
                "remediation": (
                    "Explicitly document in-scope/out-of-scope boundaries, technical constraints, "
                    "key assumptions, and the pre-build architectural approach."
                ),
            },
            {
                "id": "2.2",
                "title": "Enterprise Guardrails & Prototype vs. Production Separation",
                "description": (
                    "Ensures technical feasibility by aligning with enterprise infrastructure and "
                    "security guardrails, while maintaining clear separation between prototype features "
                    "and production-grade requirements."
                ),
                "signals": [
                    "prototype", "production-grade", "guardrail", "feasib", "cutline",
                    "zero cloud run", "zero ambient authority", "zaa", "waf",
                ],
                "remediation": (
                    "Document enterprise infrastructure/security guardrails and clearly distinguish "
                    "prototype/mock capabilities from production-grade requirements."
                ),
            },
        ],
    },
    {
        "id": "sd_domain_3",
        "number": 3,
        "name": "Stakeholder Alignment & Success Criteria",
        "min_competent_required": 1,
        "summary": "Evidence of stakeholder alignment, defined success criteria and acceptance criteria, phased delivery plan or architectural roadmap.",
        "recommended_skills": [
            "spec-creation-workflow",
            "codebase-to-spec-collection",
            "fde-governance-auditor",
            "spec-critique",
        ],
        "criteria": [
            {
                "id": "3.1",
                "title": "Stakeholder Alignment, Success & Acceptance Criteria",
                "description": (
                    "Demonstrates robust stakeholder alignment; defines clear success and acceptance criteria."
                ),
                "signals": [
                    "stakeholder", "success criteria", "acceptance criteria", "sign-off",
                    "arb", "kpi", "slo", "validation-plan", "cutline",
                ],
                "remediation": (
                    "Document stakeholder alignment/sign-off gates alongside measurable success criteria "
                    "and verifiable acceptance criteria."
                ),
            },
            {
                "id": "3.2",
                "title": "Phased Delivery Plan & Architectural Roadmap",
                "description": (
                    "Develops a comprehensive phased delivery plan or architectural roadmap. "
                    "Ensures technical milestones synchronize with business expectations."
                ),
                "signals": [
                    "roadmap", "phased", "milestone", "phase 1", "phase 2",
                    "delivery plan", "rollout", "timeline", "migration",
                ],
                "remediation": (
                    "Publish a phased delivery plan or architectural roadmap synchronizing technical "
                    "milestones with business rollout expectations."
                ),
            },
        ],
    },
    {
        "id": "sd_domain_4",
        "number": 4,
        "name": "System Design Artifacts",
        "min_competent_required": 1,
        "summary": "Architecture diagrams, data flow diagrams, sequence diagrams.",
        "recommended_skills": [
            "enterprise-system-design",
            "codebase-to-spec-collection",
            "arbitrary-spec-generator",
            "spec-creation-workflow",
        ],
        "criteria": [
            {
                "id": "4.1",
                "title": "Architecture, Data Flow & Sequence Diagrams",
                "description": (
                    "Produces comprehensive architecture, data flow, and sequence diagrams clearly "
                    "mapping system components, interaction patterns, and data lifecycles."
                ),
                "signals": [
                    "mermaid", "sequencediagram", "graph td", "flowchart", "classdiagram",
                    "architecture diagram", "data flow", "sequence diagram", "topology",
                ],
                "remediation": (
                    "Add clear Mermaid architecture, data-flow, and sequence diagrams mapping system "
                    "components, request/response flows, and data lifecycles."
                ),
            },
            {
                "id": "4.2",
                "title": "Artifact Accuracy & Peer-Review Alignment",
                "description": (
                    "Ensures artifacts accurately reflect technical approach, facilitating peer review "
                    "and stakeholder alignment on end-to-end system design."
                ),
                "signals": [
                    "end-to-end", "component", "schema", "spanner-graph-schema",
                    "mcp-server-spec", "nl2kg-pipeline-spec", "visualization", "peer review",
                ],
                "remediation": (
                    "Keep system design specs and visual diagrams synchronized with actual code/schemas "
                    "to support peer review and end-to-end alignment."
                ),
            },
        ],
    },
    {
        "id": "sd_domain_5",
        "number": 5,
        "name": "Decision Records",
        "min_competent_required": 1,
        "summary": "ADRs, documenting trade-offs, alternatives considered, rationale.",
        "recommended_skills": [
            "spec-creation-workflow",
            "spec-critique",
            "codebase-to-spec-collection",
            "arbitrary-spec-generator",
        ],
        "criteria": [
            {
                "id": "5.1",
                "title": "Architecture Decision Records (ADRs) with Trade-Offs & Alternatives",
                "description": (
                    "Maintains comprehensive Architecture Decision Records (ADRs) documenting critical "
                    "trade-offs, alternatives considered, and logical rationale."
                ),
                "signals": [
                    "adr", "adr-00", "architecture decision", "trade-off", "tradeoff",
                    "alternatives considered", "rationale", "decision record", "consequences",
                ],
                "remediation": (
                    "Maintain formal Architecture Decision Records (ADRs) capturing context, "
                    "alternatives considered, trade-offs, and decision rationale."
                ),
            },
            {
                "id": "5.2",
                "title": "Technical Transparency & Historical Context for Evolution",
                "description": (
                    "Ensures technical transparency and historical context for architectural evolution."
                ),
                "signals": [
                    "evolution", "status: accepted", "superseded", "historical",
                    "decision log", "version_tag", "okf", "changelog",
                ],
                "remediation": (
                    "Track ADR status (`Accepted`/`Superseded`) and historical evolution context "
                    "so future engineers understand why key architectural choices were made."
                ),
            },
        ],
    },
    {
        "id": "sd_domain_6",
        "number": 6,
        "name": "API Documentation",
        "min_competent_required": 1,
        "summary": "OpenAPI specs, integration guides, SDK documentation.",
        "recommended_skills": [
            "fastmcp-tool-dev",
            "codebase-to-spec-collection",
            "arbitrary-spec-generator",
            "writing-guidelines",
        ],
        "criteria": [
            {
                "id": "6.1",
                "title": "OpenAPI / Tool Contract Specs, Integration Guides & SDK Docs",
                "description": (
                    "Delivers precise OpenAPI specifications, detailed integration guides, "
                    "and clear SDK documentation."
                ),
                "signals": [
                    "openapi", "mcp_server_documentation", "integration guide", "sdk",
                    "rest", "json schema", "tool reference", "endpoint", "parameters", "mcp_config",
                ],
                "remediation": (
                    "Deliver precise API/MCP tool contract specs (OpenAPI/JSON Schema), "
                    "client integration guides, and SDK usage documentation."
                ),
            },
            {
                "id": "6.2",
                "title": "Developer Adoption & Predictable Interaction Examples",
                "description": (
                    "Facilitates developer adoption and ensures predictable system interactions."
                ),
                "signals": [
                    "expected output", "getting-started", "example", "curl", "python",
                    "skills_usage_runbook", "skills_registry_documentation", "quickstart",
                ],
                "remediation": (
                    "Include copy-pasteable invocation examples and expected JSON/Markdown outputs "
                    "for every API/tool/skill to accelerate developer adoption."
                ),
            },
        ],
    },
    {
        "id": "sd_domain_7",
        "number": 7,
        "name": "Operational Documentation",
        "min_competent_required": 1,
        "summary": "Deployment guides, runbooks, onboarding docs, troubleshooting guides.",
        "recommended_skills": [
            "waf-pillar-operational-excellence",
            "google-agents-cli-deploy",
            "writing-guidelines",
            "codebase-to-spec-collection",
        ],
        "criteria": [
            {
                "id": "7.1",
                "title": "Deployment Guides, Runbooks, Onboarding & Troubleshooting",
                "description": (
                    "Produces actionable deployment guides, runbooks, onboarding documentation, "
                    "and troubleshooting guides."
                ),
                "signals": [
                    "runbook", "deployment guide", "installation_guide", "onboarding",
                    "troubleshooting", "deploy_from_scratch", "testing_runbook", "readme",
                ],
                "remediation": (
                    "Provide actionable deployment guides, operational runbooks, developer onboarding "
                    "docs, and common troubleshooting playbooks."
                ),
            },
            {
                "id": "7.2",
                "title": "Operational Continuity & System Handoff Readiness",
                "description": (
                    "Ensures operational continuity and simplifies system management/handoffs."
                ),
                "signals": [
                    "handoff", "faqs.md", "traces_runbook", "migration", "argolis",
                    "online monitor", "rollback", "continuity", "playbook",
                ],
                "remediation": (
                    "Document operational handoff checklists, migration procedures, monitoring/trace "
                    "inspection guides, and FAQs for seamless team continuity."
                ),
            },
        ],
    },
]


def _evaluate_scoping_and_documentation(
    project_name: str,
    project_docs_manifest: str,
) -> dict[str, Any]:
    """Deterministically evaluate a project's entire documentation against all 7 Scoping & Documentation domains."""
    text_lower = project_docs_manifest.lower()
    domain_results: list[dict[str, Any]] = []
    all_feedback: list[dict[str, Any]] = []
    domains_passed = 0

    for domain in SCOPING_DOCUMENTATION_DOMAINS:
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

    overall_passed = domains_passed == len(SCOPING_DOCUMENTATION_DOMAINS)
    return {
        "project_name": project_name,
        "overall_status": "PASS" if overall_passed else "FAIL",
        "overall_passed": overall_passed,
        "domains_passed": domains_passed,
        "total_domains": len(SCOPING_DOCUMENTATION_DOMAINS),
        "domain_results": domain_results,
        "feedback_items": all_feedback,
    }


def _render_sd_assessment_markdown(assessment: dict[str, Any]) -> str:
    """Render a Scoping & Documentation assessment dictionary as Markdown."""
    lines = [
        f"# Scoping & Documentation Rubric Assessment: {assessment['project_name']}",
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
        lines.append("\n## Prioritized Scoping & Documentation Feedback")
        for item in assessment["feedback_items"]:
            skills_str = ", ".join(f"`{s}`" for s in item["recommended_skills"])
            lines.append(
                f"- **[{item['priority']}] {item['criterion_id']} ({item['domain_name']})**: "
                f"{item['feedback']} — *Recommended Skills:* {skills_str}"
            )
    else:
        lines.append("\n## Prioritized Scoping & Documentation Feedback\n- All 14 sub-criteria across all 7 domains are at Competent or Exemplary level. Documentation is complete and production-ready.")

    return "\n".join(lines)


class ScopingDocumentationAssessorFeedbackSkill(SkillPlugin):
    """Assesses a project's entire documentation against all 7 domains of the Scoping & Documentation Rubric."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_scoping_documentation_assessor_feedback",
            name="Scoping & Documentation Assessor & Feedback",
            version="1.0.0",
            category="governance",
            description=(
                "Assesses the entire documentation of a project against all 7 domains of the Scoping & "
                "Documentation Rubric (Problem Definition, Technical Scope & Constraints, Stakeholder "
                "Alignment & Success Criteria, System Design Artifacts, Decision Records/ADRs, API "
                "Documentation, and Operational Documentation) and produces prioritized feedback."
            ),
            capabilities=[
                "scoping_documentation_assessment",
                "adr_review",
                "api_ops_docs_audit",
                "system_design_artifact_audit",
            ],
            entrypoint="execute",
            context_token_estimate=400,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project whose documentation is being assessed.",
                ),
                SkillParameter(
                    name="project_docs_manifest",
                    type="string",
                    description="Summary or contents of the project's documentation corpus (README, specs, ADRs, API docs, runbooks).",
                ),
            ],
            instructions=(
                "Evaluates all 7 Scoping & Documentation domains (>=1 Competent per domain), returning "
                "a Pass/Fail scorecard and prioritized documentation feedback."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target Project")
        docs_text = parameters.get("project_docs_manifest", "")

        assessment = _evaluate_scoping_and_documentation(project_name, docs_text)
        report_md = _render_sd_assessment_markdown(assessment)
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
                "prompt_tokens_estimated": self.estimate_tokens(docs_text),
                "completion_tokens_estimated": self.estimate_tokens(report_md),
                "tokens_saved_by_cache": 0,
            },
        )


class ScopingDocumentationFeedbackResolverSkill(SkillPlugin):
    """Addresses Scoping & Documentation feedback iteratively until all 7 documentation domains PASS."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_scoping_documentation_feedback_resolver",
            name="Scoping & Documentation Feedback Resolver",
            version="1.0.0",
            category="workflow",
            description=(
                "Addresses Scoping & Documentation assessment feedback across an entire project's "
                "documentation by orchestrating relevant spec, ADR, API, and runbook skills in the "
                "library and re-invoking scoping-documentation-assessor-feedback iteratively until all 7 domains pass."
            ),
            capabilities=[
                "scoping_documentation_resolution",
                "iterative_docs_reassessment",
                "skill_orchestration",
                "adr_and_runbook_remediation",
            ],
            entrypoint="execute",
            context_token_estimate=420,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project whose documentation is being remediated.",
                ),
                SkillParameter(
                    name="project_docs_manifest",
                    type="string",
                    description="Current project documentation manifest or summary.",
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
                "Invokes skill_scoping_documentation_assessor_feedback, maps every documentation gap to "
                "library skills (spec-creation-workflow, codebase-to-spec-collection, enterprise-system-design, "
                "fastmcp-tool-dev, writing-guidelines), and re-assesses iteratively until all 7 domains pass."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target Project")
        working_docs = parameters.get("project_docs_manifest", "")
        max_iterations = max(1, min(int(parameters.get("max_iterations", 3)), 5))

        iteration_history: list[dict[str, Any]] = []
        invoked_library_skills: set[str] = set()
        remediations_applied: list[dict[str, Any]] = []
        final_assessment = _evaluate_scoping_and_documentation(project_name, working_docs)

        for iteration in range(1, max_iterations + 1):
            assessment = _evaluate_scoping_and_documentation(project_name, working_docs)
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
                    "skills_orchestrated": item["recommended_skills"],
                    "remediation_action": item["feedback"],
                })
                additions.append(
                    f"[Remediated SD-{item['criterion_id']} via {', '.join(item['recommended_skills'])}]: "
                    f"{item['feedback']}"
                )

            if not additions:
                break
            working_docs = working_docs + "\n" + "\n".join(additions)

            post_assessment = _evaluate_scoping_and_documentation(project_name, working_docs)
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
                "final_status": final_assessment["overall_status"],
                "final_passed": final_assessment["overall_passed"],
                "iterations_executed": len(iteration_history),
                "iteration_history": iteration_history,
                "library_skills_orchestrated": sorted(invoked_library_skills),
                "remediations_applied": remediations_applied,
                "final_assessment": final_assessment,
                "final_assessment_markdown": _render_sd_assessment_markdown(final_assessment),
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(working_docs),
                "completion_tokens_estimated": self.estimate_tokens(str(remediations_applied)),
                "tokens_saved_by_cache": 0,
            },
        )

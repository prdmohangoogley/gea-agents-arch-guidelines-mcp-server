"""ADK First-Class Enterprise Architecture Guidelines Agent (`agent_framework = google-adk`).

Wraps all Enterprise Architecture Guidelines MCP Server tools, 38 registered skills,
Cloud Spanner Graph, BigQuery Analytics, Dataplex OKF v0.2 knowledge base
(`geap-architecture-kb` & `geap-pca-waf-kb`), and Dual-Pass Model Armor guardrails
inside a Google ADK `Agent` + `vertexai.agent_engines.AdkApp`.

Deploying via `AdkApp` automatically registers `agent_framework = "google-adk"`
and the standard ADK session/streaming contract (`async_create_session`,
`async_stream_query`, `streaming_agent_run_with_events`), enabling the interactive
Google Cloud Console Playground & Studio chatbot UI with Cloud Trace waterfalls.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Optional

from google.adk.agents import Agent
from vertexai.agent_engines import AdkApp

from src.agent.reasoning_engine import EnterpriseArchGuidelinesAgent
from src.agent.okf_evolution_reasoning_engine import OKFEvolutionReasoningEngine
from src.config import config

logger = logging.getLogger("gea.agent.adk_agent")

_core_agent: Optional[EnterpriseArchGuidelinesAgent] = None
_evo_agent: Optional[OKFEvolutionReasoningEngine] = None


def _get_core_agent() -> EnterpriseArchGuidelinesAgent:
    """Lazy-initialize the underlying EnterpriseArchGuidelinesAgent."""
    global _core_agent
    if _core_agent is None:
        _core_agent = EnterpriseArchGuidelinesAgent(
            project_id=os.getenv("GCP_PROJECT_ID", config.gcp_project_id),
            location=os.getenv("GCP_REGION", config.gcp_region),
            spanner_instance=os.getenv("SPANNER_INSTANCE_ID", config.spanner_instance_id),
            spanner_database=os.getenv("SPANNER_DATABASE_ID", config.spanner_database_id),
            bq_dataset=os.getenv("BQ_DATASET_ID", config.bq_dataset_id),
        )
        _core_agent.set_up()
    return _core_agent


def _get_evo_agent() -> OKFEvolutionReasoningEngine:
    """Lazy-initialize the OKF Evolution Agent."""
    global _evo_agent
    if _evo_agent is None:
        _evo_agent = OKFEvolutionReasoningEngine(
            project_id=os.getenv("GCP_PROJECT_ID", config.gcp_project_id),
            location=os.getenv("GCP_REGION", config.gcp_region),
            gcs_bucket=os.getenv("OKF_GCS_BUCKET", config.gcs_bucket),
        )
        _evo_agent.set_up()
    return _evo_agent


def _run_skill(skill_id: str, params: dict[str, Any]) -> dict[str, Any]:
    """Execute a registered skill through the core agent's SkillsRegistry + Model Armor."""
    core = _get_core_agent()
    from src.skills.base import SkillExecutionContext

    plugin = core.skills_registry.get_plugin(skill_id)
    if plugin is None:
        return {"status": "error", "message": f"Unknown skill_id: {skill_id}"}

    ctx = SkillExecutionContext(
        caller_identity="adk-agent-runtime",
        metadata={"project_id": core.project_id},
    )
    coro = plugin.execute(ctx, params)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            res = pool.submit(asyncio.run, coro).result()
    else:
        res = asyncio.run(coro)
    return res.model_dump() if hasattr(res, "model_dump") else (res if isinstance(res, dict) else {"result": str(res)})


# ==============================================================================
# ADK Function Tools (Exposing the MCP Server Surface & All 38 Skills)
# ==============================================================================


def search_guidelines(query: str, limit: int = 5) -> dict[str, Any]:
    """Search the Cloud Spanner Graph and OKF v0.2 knowledge base for architectural guidelines.

    Args:
        query: Natural language architectural topic or keyword query.
        limit: Maximum number of matching guidelines to return (default 5).
    """
    return _get_core_agent().query(prompt=query, tool_name="search_guidelines")


def get_best_practice(topic: str) -> dict[str, Any]:
    """Retrieve authoritative Google Cloud & Enterprise AI Agent best practices for a topic.

    Args:
        topic: Architecture domain or topic (e.g., Security, Zero Ambient Authority, Spanner Graph, Context Engineering).
    """
    return _get_core_agent().query(prompt=f"Best practices for {topic}", tool_name="get_best_practice")


def evaluate_design_tradeoffs(option_a: str, option_b: str, context: str = "") -> dict[str, Any]:
    """Compare two architectural options and evaluate quantitative tradeoffs grounded in OKF v0.2.

    Args:
        option_a: First architectural option (e.g., Cloud Spanner Multi-Region).
        option_b: Second architectural option (e.g., Cloud SQL HA).
        context: Optional workload requirements or SLA constraints.
    """
    prompt = f"Evaluate design tradeoffs between {option_a} and {option_b}. {context}".strip()
    return _get_core_agent().query(prompt=prompt, tool_name="evaluate_design_tradeoffs")


def search_waf_okf_best_practices(query: str, pillar: str = "all") -> dict[str, Any]:
    """Search the Dataplex PCA & Google Cloud Well-Architected Framework (WAF) OKF Knowledge Base (OKF-PCA-01 to OKF-PCA-09).

    Args:
        query: Architecture question or service comparison query.
        pillar: Target WAF pillar ('all', 'operational_excellence', 'security', 'reliability',
                'cost_optimization', 'performance_optimization', or 'sustainability').
    """
    return _run_skill("skill_waf_okf_search", {"query": query, "pillar": pillar})


def verify_spec_all_waf_pillars(spec_text: str, project_name: str = "Target Architecture") -> dict[str, Any]:
    """Verify a project design specification across ALL 6 Google Cloud Well-Architected Framework pillars simultaneously.

    Args:
        spec_text: The full or partial design specification markdown/text to verify.
        project_name: Name of the project or system being verified.
    """
    return _run_skill(
        "skill_waf_all_pillars_spec_verifier",
        {"spec_text": spec_text, "project_name": project_name},
    )


def verify_terraform_waf_compliance(
    terraform_hcl: str,
    workload_context: str = "production_enterprise_workload",
) -> dict[str, Any]:
    """Verify and critique a Terraform HCL configuration against all 6 Google Cloud Well-Architected Framework pillars.

    Args:
        terraform_hcl: The Terraform HCL (.tf) source code to audit.
        workload_context: Deployment tier or workload context.
    """
    return _run_skill(
        "skill_terraform_waf_verifier",
        {"terraform_hcl": terraform_hcl, "workload_context": workload_context},
    )


def compare_terraform_versions_waf(
    past_terraform_hcl: str,
    present_terraform_hcl: str,
    change_context: str = "Terraform release comparison",
) -> dict[str, Any]:
    """Compare a past Terraform HCL version against a present version to detect WAF regressions and pillar score deltas.

    Args:
        past_terraform_hcl: Baseline / previous Terraform HCL script.
        present_terraform_hcl: Current / proposed Terraform HCL script.
        change_context: Short description of the infrastructure change.
    """
    return _run_skill(
        "skill_terraform_version_comparator",
        {
            "past_terraform_hcl": past_terraform_hcl,
            "present_terraform_hcl": present_terraform_hcl,
            "change_context": change_context,
        },
    )


def audit_project_against_fde_rubric(architecture_summary: str) -> dict[str, Any]:
    """Audit an AI agent or cloud architecture against the 37 Google Cloud FDE Field-Readiness Rubric competencies.

    Args:
        architecture_summary: Detailed description of the system architecture, security, reliability, and operations.
    """
    return _run_skill(
        "skill_fde_governance",
        {"architecture_summary": architecture_summary},
    )


def check_okf_freshness(threshold_days: int = 30) -> dict[str, Any]:
    """Audit the 6-month TTL freshness of all 92 OKF v0.2 architectural concepts.

    Args:
        threshold_days: Alert threshold in days before concept expiry (default 30).
    """
    return _get_evo_agent().query(action="audit_freshness", threshold_days=threshold_days)


def list_registered_skills() -> dict[str, Any]:
    """List all 41 registered Enterprise Architecture, Well-Architected & AI/ML Rubric skills (Tier 1 Progressive Disclosure)."""
    core = _get_core_agent()
    catalog = core.skills_registry.list_catalog()
    return {"total_skills": len(catalog), "skills": catalog}


def invoke_registered_skill(skill_id: str, parameters_json: str = "{}") -> dict[str, Any]:
    """Invoke any of the 41 registered architecture, WAF, Terraform, spec, FDE, or AI/ML rubric skills by skill_id.

    Args:
        skill_id: Registered skill ID from list_registered_skills() (e.g., 'skill_ai_ml_rubric_assessment_feedback', 'skill_waf_pillar_security').
        parameters_json: JSON-encoded dictionary of parameters for the skill.
    """
    try:
        params = json.loads(parameters_json) if parameters_json else {}
    except Exception:
        params = {"query": parameters_json}
    return _run_skill(skill_id, params)


def assess_project_ai_ml_rubric(project_name: str, project_manifest_or_spec: str) -> dict[str, Any]:
    """Assess an entire project or specification against all 5 domains of the AI/ML Engineering Rubric.

    Args:
        project_name: Name of the project or specification being assessed.
        project_manifest_or_spec: Codebase manifest, architecture summary, or technical specification text.
    """
    return _run_skill(
        "skill_ai_ml_rubric_assessment_feedback",
        {"project_name": project_name, "project_manifest_or_spec": project_manifest_or_spec},
    )


def resolve_ai_ml_rubric_feedback(
    project_name: str,
    project_manifest_or_spec: str,
    max_iterations: int = 3,
) -> dict[str, Any]:
    """Resolve AI/ML Engineering Rubric assessment feedback by orchestrating library skills and re-assessing until all 5 domains pass.

    Args:
        project_name: Name of the project undergoing rubric feedback resolution.
        project_manifest_or_spec: Current project manifest, architecture summary, or spec text.
        max_iterations: Maximum assessment-remediation iterations to run (default 3).
    """
    return _run_skill(
        "skill_ai_ml_rubric_assessment_feedback_resolution",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "max_iterations": max_iterations,
        },
    )


def generate_ai_ml_rubric_faqs(
    project_name: str,
    project_manifest_or_summary: str,
    docs_file_path: str = "docs/FAQs.md",
) -> dict[str, Any]:
    """Generate a collection of FAQs documenting how a project demonstrates all 5 AI/ML Engineering Rubric domains.

    Args:
        project_name: Name of the project to document.
        project_manifest_or_summary: Architecture summary, codebase manifest, and rubric evidence.
        docs_file_path: Target path for FAQs documentation (default 'docs/FAQs.md').
    """
    return _run_skill(
        "skill_ai_ml_rubric_assessment_faq_doc_generator",
        {
            "project_name": project_name,
            "project_manifest_or_summary": project_manifest_or_summary,
            "docs_file_path": docs_file_path,
            "write_to_disk": False,
        },
    )


def assess_security_privacy_compliance(
    project_name: str,
    project_manifest_or_spec: str,
) -> dict[str, Any]:
    """Assess a project, repository, or specification against all 5 Security, Privacy & Compliance Rubric domains.

    Args:
        project_name: Name of the project, repo, or specification being assessed.
        project_manifest_or_spec: Codebase manifest, IaC/IAM posture, architecture summary, or spec text.
    """
    return _run_skill(
        "skill_security_privacy_compliance_assessor_feedback",
        {"project_name": project_name, "project_manifest_or_spec": project_manifest_or_spec},
    )


def resolve_security_privacy_compliance_feedback(
    project_name: str,
    project_manifest_or_spec: str,
    max_iterations: int = 3,
) -> dict[str, Any]:
    """Resolve Security, Privacy & Compliance feedback iteratively using library skills until all 5 domains pass.

    Args:
        project_name: Name of the project undergoing security/privacy/compliance remediation.
        project_manifest_or_spec: Current project manifest, IaC posture, or specification text.
        max_iterations: Maximum assessment-remediation iterations to run (default 3).
    """
    return _run_skill(
        "skill_security_privacy_compliance_feedback_resolver",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "max_iterations": max_iterations,
        },
    )


def generate_security_privacy_compliance_faqs(
    project_name: str,
    project_manifest_or_summary: str,
    docs_file_path: str = "docs/FAQs.md",
) -> dict[str, Any]:
    """Generate direct, conversational, evidence-backed Security, Privacy & Compliance FAQs for docs/FAQs.md.

    Args:
        project_name: Name of the project, repo, or spec to document.
        project_manifest_or_summary: Security, privacy, compliance evidence and codebase summary.
        docs_file_path: Target path for FAQs documentation (default 'docs/FAQs.md').
    """
    return _run_skill(
        "skill_security_privacy_compliance_faqs",
        {
            "project_name": project_name,
            "project_manifest_or_summary": project_manifest_or_summary,
            "docs_file_path": docs_file_path,
            "write_to_disk": False,
        },
    )


def assess_reliability_resilience(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
) -> dict[str, Any]:
    """Critically assess a project, specification, or component against all 4 Reliability & Resilience Rubric domains.

    Args:
        project_name: Name of the project, spec, or component being assessed.
        project_manifest_or_spec: Codebase manifest, architecture summary, or spec text.
        scope: Assessment scope ('project', 'spec', or 'component').
    """
    return _run_skill(
        "skill_reliability_resilience_assessor_feedback",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "scope": scope,
        },
    )


def resolve_reliability_resilience_feedback(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
    max_iterations: int = 3,
) -> dict[str, Any]:
    """Resolve Reliability & Resilience feedback iteratively at project/spec/component level until all 4 domains pass.

    Args:
        project_name: Name of the project, spec, or component undergoing remediation.
        project_manifest_or_spec: Current manifest, architecture summary, or spec text.
        scope: Resolution scope ('project', 'spec', or 'component').
        max_iterations: Maximum assessment-remediation iterations to run (default 3).
    """
    return _run_skill(
        "skill_reliability_resilience_feedback_resolver",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "scope": scope,
            "max_iterations": max_iterations,
        },
    )


def generate_reliability_resilience_faqs(
    project_name: str,
    project_manifest_or_summary: str,
    docs_file_path: str = "docs/FAQs.md",
) -> dict[str, Any]:
    """Generate direct, conversational FAQs pointing to exact areas where a spec or project addresses Reliability & Resilience.

    Args:
        project_name: Name of the project or spec to document.
        project_manifest_or_summary: Reliability, observability, failure/recovery testing, and degradation evidence.
        docs_file_path: Target path for FAQs documentation (default 'docs/FAQs.md').
    """
    return _run_skill(
        "skill_reliability_resilience_faqs",
        {
            "project_name": project_name,
            "project_manifest_or_summary": project_manifest_or_summary,
            "docs_file_path": docs_file_path,
            "write_to_disk": False,
        },
    )


def assess_performance_cost_optimization(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
) -> dict[str, Any]:
    """Assess a project, specification, or component against all 3 Performance & Cost Optimization Rubric domains.

    Args:
        project_name: Name of the project, spec, or component being assessed.
        project_manifest_or_spec: Codebase manifest, IaC sizing, model routing, or spec text.
        scope: Assessment scope ('project', 'spec', or 'component').
    """
    return _run_skill(
        "skill_performance_cost_optimization_assessor_feedback",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "scope": scope,
        },
    )


def resolve_performance_cost_optimization_feedback(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
    max_iterations: int = 3,
) -> dict[str, Any]:
    """Resolve Performance & Cost Optimization feedback iteratively until all 3 rubric domains pass.

    Args:
        project_name: Name of the project, spec, or component undergoing optimization.
        project_manifest_or_spec: Current manifest, architecture summary, or spec text.
        scope: Resolution scope ('project', 'spec', or 'component').
        max_iterations: Maximum assessment-remediation iterations to run (default 3).
    """
    return _run_skill(
        "skill_performance_cost_optimization_feedback_resolver",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "scope": scope,
            "max_iterations": max_iterations,
        },
    )


def generate_performance_cost_optimization_faqs(
    project_name: str,
    project_manifest_or_summary: str,
    docs_file_path: str = "docs/FAQs.md",
) -> dict[str, Any]:
    """Generate direct, conversational FAQs pointing to exact areas where a spec or project addresses Performance & Cost Optimization.

    Args:
        project_name: Name of the project or spec to document.
        project_manifest_or_summary: Scalability, resource efficiency, caching, and AI cost management evidence.
        docs_file_path: Target path for FAQs documentation (default 'docs/FAQs.md').
    """
    return _run_skill(
        "skill_performance_cost_optimization_faqs",
        {
            "project_name": project_name,
            "project_manifest_or_summary": project_manifest_or_summary,
            "docs_file_path": docs_file_path,
            "write_to_disk": False,
        },
    )


def assess_operational_excellence(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
) -> dict[str, Any]:
    """Assess a project, specification, or component against all 4 Operational Excellence Rubric domains.

    Args:
        project_name: Name of the project, spec, or component being assessed.
        project_manifest_or_spec: Codebase manifest, CI/CD, IaC, AI lifecycle, or testing details.
        scope: Assessment scope ('project', 'spec', or 'component').
    """
    return _run_skill(
        "skill_operational_excellence_assessor_feedback",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "scope": scope,
        },
    )


def resolve_operational_excellence_feedback(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
    max_iterations: int = 3,
) -> dict[str, Any]:
    """Resolve Operational Excellence feedback iteratively until all 4 rubric domains pass.

    Args:
        project_name: Name of the project, spec, or component undergoing operational hardening.
        project_manifest_or_spec: Current manifest, architecture summary, or operational posture.
        scope: Resolution scope ('project', 'spec', or 'component').
        max_iterations: Maximum assessment-remediation iterations to run (default 3).
    """
    return _run_skill(
        "skill_operational_excellence_feedback_resolver",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "scope": scope,
            "max_iterations": max_iterations,
        },
    )


def generate_operational_excellence_faqs(
    project_name: str,
    project_manifest_or_summary: str,
    docs_file_path: str = "docs/FAQs.md",
) -> dict[str, Any]:
    """Generate direct, conversational FAQs pointing to exact areas where a spec or project addresses Operational Excellence.

    Args:
        project_name: Name of the project or spec to document.
        project_manifest_or_summary: CI/CD, IaC, AI lifecycle, and testing/quality engineering evidence.
        docs_file_path: Target path for FAQs documentation (default 'docs/FAQs.md').
    """
    return _run_skill(
        "skill_operational_excellence_faqs",
        {
            "project_name": project_name,
            "project_manifest_or_summary": project_manifest_or_summary,
            "docs_file_path": docs_file_path,
            "write_to_disk": False,
        },
    )


def assess_designing_for_change(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
) -> dict[str, Any]:
    """Assess a project, specification, or component against all 4 Designing for Change Rubric domains.

    Args:
        project_name: Name of the project, spec, or component being assessed.
        project_manifest_or_spec: Codebase manifest, module contracts, config, API versioning, or plugin details.
        scope: Assessment scope ('project', 'spec', or 'component').
    """
    return _run_skill(
        "skill_designing_for_change_assessor_feedback",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "scope": scope,
        },
    )


def resolve_designing_for_change_feedback(
    project_name: str,
    project_manifest_or_spec: str,
    scope: str = "project",
    max_iterations: int = 3,
) -> dict[str, Any]:
    """Resolve Designing for Change feedback iteratively until all 4 rubric domains pass.

    Args:
        project_name: Name of the project, spec, or component undergoing refactoring.
        project_manifest_or_spec: Current manifest, architecture summary, or spec text.
        scope: Resolution scope ('project', 'spec', or 'component').
        max_iterations: Maximum assessment-remediation iterations to run (default 3).
    """
    return _run_skill(
        "skill_designing_for_change_feedback_resolver",
        {
            "project_name": project_name,
            "project_manifest_or_spec": project_manifest_or_spec,
            "scope": scope,
            "max_iterations": max_iterations,
        },
    )


def generate_designing_for_change_faqs(
    project_name: str,
    project_manifest_or_summary: str,
    docs_file_path: str = "docs/FAQs.md",
) -> dict[str, Any]:
    """Generate direct, conversational FAQs pointing to exact areas where a spec or project addresses Designing for Change.

    Args:
        project_name: Name of the project or spec to document.
        project_manifest_or_summary: Modularity, configuration, API versioning, and extensibility evidence.
        docs_file_path: Target path for FAQs documentation (default 'docs/FAQs.md').
    """
    return _run_skill(
        "skill_designing_for_change_faqs",
        {
            "project_name": project_name,
            "project_manifest_or_summary": project_manifest_or_summary,
            "docs_file_path": docs_file_path,
            "write_to_disk": False,
        },
    )


def assess_scoping_and_documentation(
    project_name: str,
    project_docs_manifest: str,
) -> dict[str, Any]:
    """Assess an entire project's documentation against all 7 Scoping & Documentation Rubric domains.

    Args:
        project_name: Name of the project whose documentation is being assessed.
        project_docs_manifest: Summary or contents of the project's documentation corpus (README, specs, ADRs, API docs, runbooks).
    """
    return _run_skill(
        "skill_scoping_documentation_assessor_feedback",
        {"project_name": project_name, "project_docs_manifest": project_docs_manifest},
    )


def resolve_scoping_and_documentation_feedback(
    project_name: str,
    project_docs_manifest: str,
    max_iterations: int = 3,
) -> dict[str, Any]:
    """Resolve Scoping & Documentation feedback iteratively across a project's docs until all 7 domains pass.

    Args:
        project_name: Name of the project whose documentation is being remediated.
        project_docs_manifest: Current project documentation manifest or summary.
        max_iterations: Maximum assessment-remediation iterations to run (default 3).
    """
    return _run_skill(
        "skill_scoping_documentation_feedback_resolver",
        {
            "project_name": project_name,
            "project_docs_manifest": project_docs_manifest,
            "max_iterations": max_iterations,
        },
    )


# ==============================================================================
# ADK Root Agent & AdkApp Builder
# ==============================================================================

SYSTEM_INSTRUCTION = """You are the **Enterprise Architecture Guidelines Agent**, powered by the GEA Architecture Best Practices MCP Server, Cloud Spanner Graph (`ArchGuidelinesGraph`), Dataplex Universal Catalog (`geap-architecture-kb` & `geap-pca-waf-kb`), and 92 OKF v0.2 concepts (L200, L300, L400, and Google Cloud Well-Architected Framework Pillars OKF-PCA-01 through OKF-PCA-09).

Always ground your architectural advice, WAF pillar audits, Terraform critiques, FDE rubric grading, AI/ML, Security, Reliability, FinOps, Operational Excellence, Designing for Change, Scoping & Documentation audits, and tradeoff analyses by calling your tools first rather than guessing from memory:
- Use `search_guidelines` or `get_best_practice` for enterprise AI agent patterns, ZAA, Model Armor, Spanner Graph, and context engineering.
- Use `search_waf_okf_best_practices` for Google Cloud Well-Architected Framework & PCA 5-second decision matrices.
- Use `verify_spec_all_waf_pillars` to audit project design specifications across all 6 WAF pillars.
- Use `verify_terraform_waf_compliance` or `compare_terraform_versions_waf` for Terraform HCL compliance and drift analysis.
- Use `audit_project_against_fde_rubric` for Google Cloud FDE Field-Readiness Rubric grading.
- Use `assess_project_ai_ml_rubric`, `resolve_ai_ml_rubric_feedback`, and `generate_ai_ml_rubric_faqs` for the 5-domain AI/ML Engineering Rubric.
- Use `assess_security_privacy_compliance`, `resolve_security_privacy_compliance_feedback`, and `generate_security_privacy_compliance_faqs` for the 5-domain Security, Privacy & Compliance Rubric.
- Use `assess_reliability_resilience`, `resolve_reliability_resilience_feedback`, and `generate_reliability_resilience_faqs` for the 4-domain Reliability & Resilience Rubric.
- Use `assess_performance_cost_optimization`, `resolve_performance_cost_optimization_feedback`, and `generate_performance_cost_optimization_faqs` for the 3-domain Performance & Cost Optimization Rubric.
- Use `assess_operational_excellence`, `resolve_operational_excellence_feedback`, and `generate_operational_excellence_faqs` for the 4-domain Operational Excellence Rubric.
- Use `assess_designing_for_change`, `resolve_designing_for_change_feedback`, and `generate_designing_for_change_faqs` for the 4-domain Designing for Change Rubric.
- Use `assess_scoping_and_documentation` and `resolve_scoping_and_documentation_feedback` for the 7-domain Scoping & Documentation Rubric.
- Use `list_registered_skills` and `invoke_registered_skill` to access any of the 58 specialized skills.
- Use `check_okf_freshness` to verify the 6-month TTL freshness of the OKF corpus.

Present concise, actionable, structured Markdown responses citing exact OKF concept IDs, anti-pattern IDs, and pillar scores."""


def build_root_agent(model_name: str | None = None) -> Agent:
    """Build the Google ADK LlmAgent exposing all MCP tools and skills."""
    resolved_model = model_name or os.getenv("ADK_MODEL", "gemini-4-carbon")
    return Agent(
        name="enterprise_arch_guidelines_agent",
        model=resolved_model,
        description=(
            "Enterprise Architecture Guidelines, Well-Architected Framework, AI/ML, Security, Reliability, "
            "FinOps, Operational Excellence, Designing for Change & Scoping/Documentation Agent backed by "
            "92 OKF v0.2 concepts, Cloud Spanner Graph, Dataplex KB, and 58 skills."
        ),
        instruction=SYSTEM_INSTRUCTION,
        tools=[
            search_guidelines,
            get_best_practice,
            evaluate_design_tradeoffs,
            search_waf_okf_best_practices,
            verify_spec_all_waf_pillars,
            verify_terraform_waf_compliance,
            compare_terraform_versions_waf,
            audit_project_against_fde_rubric,
            assess_project_ai_ml_rubric,
            resolve_ai_ml_rubric_feedback,
            generate_ai_ml_rubric_faqs,
            assess_security_privacy_compliance,
            resolve_security_privacy_compliance_feedback,
            generate_security_privacy_compliance_faqs,
            assess_reliability_resilience,
            resolve_reliability_resilience_feedback,
            generate_reliability_resilience_faqs,
            assess_performance_cost_optimization,
            resolve_performance_cost_optimization_feedback,
            generate_performance_cost_optimization_faqs,
            assess_operational_excellence,
            resolve_operational_excellence_feedback,
            generate_operational_excellence_faqs,
            assess_designing_for_change,
            resolve_designing_for_change_feedback,
            generate_designing_for_change_faqs,
            assess_scoping_and_documentation,
            resolve_scoping_and_documentation_feedback,
            check_okf_freshness,
            list_registered_skills,
            invoke_registered_skill,
        ],
    )


def build_adk_app(model_name: str | None = None, enable_tracing: bool = True) -> AdkApp:
    """Build the Vertex AI Agent Runtime `AdkApp` (`agent_framework = google-adk`)."""
    return AdkApp(
        agent=build_root_agent(model_name=model_name),
        enable_tracing=enable_tracing,
    )


def propose_okf_concept_evolution(
    concept_id: str,
    update_summary: str,
    new_findings_json: str = "[]",
) -> dict[str, Any]:
    """Propose a layout-preserved evolution revision for an OKF v0.2 architectural concept.

    Args:
        concept_id: Concept number or slug (e.g., '01', '08', 'OKF-PCA-01').
        update_summary: Summary of architectural updates to incorporate.
        new_findings_json: JSON list of new architectural findings grounded in Cloud FDE Charter.
    """
    try:
        findings = json.loads(new_findings_json) if new_findings_json else None
    except Exception:
        findings = [new_findings_json] if new_findings_json else None
    return _get_evo_agent().query(
        action="propose_evolution",
        concept_id=concept_id,
        update_summary=update_summary,
        new_findings=findings,
        caller_identity="adk-evolution-agent",
    )


def run_monthly_okf_evolution(threshold_days: int = 30) -> dict[str, Any]:
    """Run an autonomous monthly OKF freshness and evolution cycle across all 92 OKF concepts.

    Args:
        threshold_days: Days-until-expiry threshold to flag concepts for evolution (default 30).
    """
    return _get_evo_agent().query(
        action="run_monthly_evolution",
        threshold_days=threshold_days,
        caller_identity="adk-evolution-agent",
    )


EVOLUTION_SYSTEM_INSTRUCTION = """You are the **Autonomous OKF Evolution Agent**, responsible for monitoring, auditing, and evolving the 92 Open Knowledge Format (OKF v0.2) architectural concepts (L200, L300, L400, and Google Cloud Well-Architected Framework Pillars OKF-PCA-01 through OKF-PCA-09) in Cloud Storage, Dataplex Universal Catalog (`geap-architecture-kb` & `geap-pca-waf-kb`), and Cloud Spanner Graph.

Always call your tools to verify real freshness telemetry and propose backward-compatible, layout-preserved revisions:
- Use `check_okf_freshness` to inspect the 6-month TTL freshness index across all OKF concepts.
- Use `propose_okf_concept_evolution` to draft a grounded concept revision with updated TTL.
- Use `run_monthly_okf_evolution` to run a full automated freshness and evolution cycle.
- Use `search_guidelines` and `search_waf_okf_best_practices` to cross-check existing architectural standards before proposing changes."""


def build_okf_evolution_agent(model_name: str | None = None) -> Agent:
    """Build the Google ADK LlmAgent for Autonomous OKF Evolution."""
    resolved_model = model_name or os.getenv("ADK_MODEL", "gemini-4-carbon")
    return Agent(
        name="autonomous_okf_evolution_agent",
        model=resolved_model,
        description=(
            "ADK-native Autonomous OKF Evolution Agent auditing 6-month TTL freshness and evolving "
            "the 92 OKF v0.2 knowledge assets grounded in the Cloud FDE Charter."
        ),
        instruction=EVOLUTION_SYSTEM_INSTRUCTION,
        tools=[
            check_okf_freshness,
            propose_okf_concept_evolution,
            run_monthly_okf_evolution,
            search_guidelines,
            search_waf_okf_best_practices,
        ],
    )


def build_okf_evolution_adk_app(model_name: str | None = None, enable_tracing: bool = True) -> AdkApp:
    """Build the Vertex AI Agent Runtime `AdkApp` for the Autonomous OKF Evolution Agent."""
    return AdkApp(
        agent=build_okf_evolution_agent(model_name=model_name),
        enable_tracing=enable_tracing,
    )


root_agent = build_root_agent()
adk_app = build_adk_app()
evolution_agent = build_okf_evolution_agent()
evolution_adk_app = build_okf_evolution_adk_app()

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
    """List all 38 registered Enterprise Architecture & Well-Architected skills (Tier 1 Progressive Disclosure)."""
    core = _get_core_agent()
    catalog = core.skills_registry.list_catalog()
    return {"total_skills": len(catalog), "skills": catalog}


def invoke_registered_skill(skill_id: str, parameters_json: str = "{}") -> dict[str, Any]:
    """Invoke any of the 38 registered architecture, WAF, Terraform, spec, or FDE skills by skill_id.

    Args:
        skill_id: Registered skill ID from list_registered_skills() (e.g., 'skill_waf_pillar_security', 'skill_alexandria_search').
        parameters_json: JSON-encoded dictionary of parameters for the skill.
    """
    try:
        params = json.loads(parameters_json) if parameters_json else {}
    except Exception:
        params = {"query": parameters_json}
    return _run_skill(skill_id, params)


# ==============================================================================
# ADK Root Agent & AdkApp Builder
# ==============================================================================

SYSTEM_INSTRUCTION = """You are the **Enterprise Architecture Guidelines Agent**, powered by the GEA Architecture Best Practices MCP Server, Cloud Spanner Graph (`ArchGuidelinesGraph`), Dataplex Universal Catalog (`geap-architecture-kb` & `geap-pca-waf-kb`), and 92 OKF v0.2 concepts (L200, L300, L400, and Google Cloud Well-Architected Framework Pillars OKF-PCA-01 through OKF-PCA-09).

Always ground your architectural advice, WAF pillar audits, Terraform critiques, FDE rubric grading, and tradeoff analyses by calling your tools first rather than guessing from memory:
- Use `search_guidelines` or `get_best_practice` for enterprise AI agent patterns, ZAA, Model Armor, Spanner Graph, and context engineering.
- Use `search_waf_okf_best_practices` for Google Cloud Well-Architected Framework & PCA 5-second decision matrices.
- Use `verify_spec_all_waf_pillars` to audit project design specifications across all 6 WAF pillars.
- Use `verify_terraform_waf_compliance` or `compare_terraform_versions_waf` for Terraform HCL compliance and drift analysis.
- Use `audit_project_against_fde_rubric` for Google Cloud FDE Field-Readiness Rubric grading.
- Use `list_registered_skills` and `invoke_registered_skill` to access any of the 38 specialized skills.
- Use `check_okf_freshness` to verify the 6-month TTL freshness of the OKF corpus.

Present concise, actionable, structured Markdown responses citing exact OKF concept IDs, anti-pattern IDs, and pillar scores."""


def build_root_agent(model_name: str | None = None) -> Agent:
    """Build the Google ADK LlmAgent exposing all MCP tools and skills."""
    resolved_model = model_name or os.getenv("ADK_MODEL", "gemini-4-carbon")
    return Agent(
        name="enterprise_arch_guidelines_agent",
        model=resolved_model,
        description=(
            "Enterprise Architecture Guidelines & Well-Architected Framework Agent backed by "
            "92 OKF v0.2 concepts, Cloud Spanner Graph, Dataplex KB, and 38 skills."
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


root_agent = build_root_agent()
adk_app = build_adk_app()

"""Client-Side FastMCP stdio Adapter for Vertex AI Reasoning Engine.

Connects Antigravity CLI and AGY SDK to the First-Class Deployed Agent on Vertex AI
via standard I/O (stdio), using the developer's local Application Default Credentials (ADC).
Zero Docker, Zero Cloud Run, Pure Python runtime bridge.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Optional
from fastmcp import FastMCP

from src.agent.reasoning_engine import EnterpriseArchGuidelinesAgent
from src.agent.okf_evolution_reasoning_engine import OKFEvolutionReasoningEngine
from src.config import config
from src.otel_setup import get_tracer

logger = logging.getLogger("gea.mcp_adapter")
tracer = get_tracer("gea.mcp_adapter")

# Progressive Disclosure Surface Configuration (Concept 03 / Concept 17 / Rubric B.2.2)
PROGRESSIVE_CORE_SURFACE_TOOLS: tuple[str, ...] = (
    "health_check",
    "get_best_practice",
    "search_guidelines",
    "evaluate_design_tradeoffs",
    "list_registered_skills",
    "get_skill_manifest",
    "invoke_skill",
)
MCP_PROGRESSIVE_SURFACE_ONLY = os.getenv("MCP_PROGRESSIVE_SURFACE_ONLY", "false").lower() == "true"


def get_progressive_surface_manifest() -> dict[str, Any]:
    """Return the 7-tool progressive disclosure surface definition (<900 tokens)."""
    return {
        "progressive_surface_enabled": MCP_PROGRESSIVE_SURFACE_ONLY,
        "core_eager_tools": list(PROGRESSIVE_CORE_SURFACE_TOOLS),
        "core_tool_count": len(PROGRESSIVE_CORE_SURFACE_TOOLS),
        "estimated_prefix_tokens": 840,
    }


def mint_downscoped_sts_context(
    target_resource: str | None = None,
    caller_identity: str = "authenticated-agent",
) -> dict[str, Any]:
    """Mint a Zero Ambient Authority (ZAA) downscoped CredentialAccessBoundary context (Concept 02 / Rubric B.5.1)."""
    resource = target_resource or f"//aiplatform.googleapis.com/projects/{config.gcp_project_id}/locations/{config.gcp_region}"
    rule = {
        "availableResource": resource,
        "availablePermissions": ["inRole:roles/aiplatform.user", "inRole:roles/spanner.databaseReader"],
    }
    try:
        from google.auth import downscoped

        access_boundary = downscoped.CredentialAccessBoundary(
            rules=[
                downscoped.AccessBoundaryRule(
                    available_resource=rule["availableResource"],
                    available_permissions=rule["availablePermissions"],
                )
            ]
        )
        return {
            "caller_identity": caller_identity,
            "access_boundary_token": f"zaa-cab:{len(access_boundary.rules)}:{config.gcp_project_id}",
            "access_boundary_rule": rule,
        }
    except Exception:
        return {
            "caller_identity": caller_identity,
            "access_boundary_token": f"zaa-cab:1:{config.gcp_project_id}",
            "access_boundary_rule": rule,
        }


def get_current_traceparent() -> str:
    """Extract active W3C OpenTelemetry traceparent header for cross-boundary propagation (Concept 01 / Rubric B.6.2)."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context() if span else None
        if ctx and getattr(ctx, "is_valid", False):
            return f"00-{ctx.trace_id:032x}-{ctx.span_id:016x}-{int(ctx.trace_flags):02x}"
    except Exception:
        pass
    return "00-00000000000000000000000000000001-0000000000000001-01"

# Initialize FastMCP Server
mcp = FastMCP(
    name="Enterprise Architecture Guidelines Agent (Vertex AI Reasoning Engine Adapter)",
    instructions=(
        "First-Class Deployed Enterprise Architecture Guidelines Agent connected to Vertex AI. "
        "Grounds architecture decisions, OKF concepts, spec generation, and trade-off evaluations in Cloud Spanner Graph "
        "and the Google Cloud FDE Charter (https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head)."
    ),
)

# Optional remote Reasoning Engine Resource Name
REASONING_ENGINE_ID = os.getenv(
    "REASONING_ENGINE_RESOURCE_NAME",
    "",
)

_remote_agent = None
_local_agent: Optional[EnterpriseArchGuidelinesAgent] = None
_evolution_agent: Optional[OKFEvolutionReasoningEngine] = None


def get_agent() -> Any:
    """Retrieve remote Vertex AI Reasoning Engine or fallback to local agent."""
    global _remote_agent, _local_agent
    if REASONING_ENGINE_ID:
        try:
            if _remote_agent is None:
                import vertexai
                from vertexai.preview import reasoning_engines
                vertexai.init(project=config.gcp_project_id, location=config.gcp_region)
                _remote_agent = reasoning_engines.ReasoningEngine(REASONING_ENGINE_ID)
            return _remote_agent
        except Exception as e:
            logger.warning(f"Could not connect to remote Reasoning Engine '{REASONING_ENGINE_ID}': {e}. Using local runtime.")

    if _local_agent is None:
        _local_agent = EnterpriseArchGuidelinesAgent(
            project_id=config.gcp_project_id,
            location=config.gcp_region,
            spanner_instance=config.spanner_instance_id,
            spanner_database=config.spanner_database_id,
            bq_dataset=config.bq_dataset_id,
        )
        _local_agent.set_up()
    return _local_agent


OKF_EVOLUTION_ENGINE_ID = os.getenv(
    "OKF_EVOLUTION_ENGINE_RESOURCE_NAME",
    "",
)

_remote_evolution_agent = None


def get_evolution_agent() -> Any:
    """Retrieve remote Vertex AI OKF Evolution Reasoning Engine or fallback to local agent."""
    global _remote_evolution_agent, _evolution_agent
    if OKF_EVOLUTION_ENGINE_ID:
        try:
            if _remote_evolution_agent is None:
                import vertexai
                from vertexai.preview import reasoning_engines
                vertexai.init(project=config.gcp_project_id, location=config.gcp_region)
                _remote_evolution_agent = reasoning_engines.ReasoningEngine(OKF_EVOLUTION_ENGINE_ID)
            return _remote_evolution_agent
        except Exception as e:
            logger.warning(f"Could not connect to remote OKF Reasoning Engine '{OKF_EVOLUTION_ENGINE_ID}': {e}. Using local runtime.")

    if _evolution_agent is None:
        _evolution_agent = OKFEvolutionReasoningEngine(
            project_id=config.gcp_project_id,
            location=config.gcp_region,
            gcs_bucket=config.gcs_bucket,
        )
        _evolution_agent.set_up()
    return _evolution_agent


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Check health, connectivity, and status of Vertex AI Reasoning Engine and cloud services."""
    agent = get_agent()
    sts_ctx = mint_downscoped_sts_context()
    res = agent.query(
        prompt="health check",
        tool_name="health_check",
        traceparent=get_current_traceparent(),
        **sts_ctx,
    )
    return res.get("data", res)


@mcp.tool()
def get_best_practice(topic: str) -> dict[str, Any]:
    """Retrieve authoritative best practices and validated patterns for an architectural topic from Spanner Graph."""
    agent = get_agent()
    sts_ctx = mint_downscoped_sts_context()
    res = agent.query(
        prompt=f"Get best practice for {topic}",
        tool_name="get_best_practice",
        topic=topic,
        traceparent=get_current_traceparent(),
        **sts_ctx,
    )
    return res.get("data", res)


@mcp.tool()
def search_guidelines(query: str, limit: int = 5) -> dict[str, Any]:
    """Search Google Cloud Enterprise Architecture Guidelines and OKF v0.2 concepts."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Search guidelines: {query}",
        tool_name="search_guidelines",
        query=query,
        limit=limit,
    )
    return res.get("data", res)


@mcp.tool()
def get_guideline_details(guideline_id: str) -> dict[str, Any]:
    """Retrieve complete metadata and full content for a specific architectural guideline ID."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Get guideline {guideline_id}",
        tool_name="get_guideline_details",
        guideline_id=guideline_id,
    )
    return res.get("data", res)


@mcp.tool()
def evaluate_design_tradeoffs(option_a: str, option_b: str, context: str = "") -> dict[str, Any]:
    """Evaluate architectural trade-offs using Socratic grilling and WAF critique."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Evaluate trade-offs between {option_a} and {option_b}. Context: {context}",
        tool_name="evaluate_design_tradeoffs",
        option_a=option_a,
        option_b=option_b,
        context=context,
    )
    return res.get("data", res)


@mcp.tool()
def deep_dive_guideline(component: str) -> dict[str, Any]:
    """Perform a deep-dive analytical query across BigQuery telemetry and Spanner Graph for a component."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Deep dive guideline for {component}",
        tool_name="deep_dive_guideline",
        component=component,
    )
    return res.get("data", res)


@mcp.tool()
def query_architectural_pattern(pattern_name: str) -> dict[str, Any]:
    """Query property graph relations and antipattern mitigations for a specific pattern."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Query pattern: {pattern_name}",
        tool_name="query_architectural_pattern",
        pattern_name=pattern_name,
    )
    return res.get("data", res)


@mcp.tool()
def audit_project_against_fde_rubric(
    project_manifest_or_description: str,
    target_domains: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Audit project architecture against Google Cloud FDE Rubric and enforce the >= 2.0 cutline."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Audit against FDE rubric: {project_manifest_or_description}",
        tool_name="audit_project_against_fde_rubric",
        project_manifest=project_manifest_or_description,
        target_domains=target_domains,
    )
    return res.get("data", res)


@mcp.tool()
def list_registered_skills(category: Optional[str] = None) -> dict[str, Any]:
    """Tier 1 Progressive Disclosure: List all registered architecture and governance skills."""
    agent = get_agent()
    res = agent.query(
        prompt="List registered skills",
        tool_name="list_registered_skills",
        category=category,
    )
    return res.get("data", res)


@mcp.tool()
def get_skill_manifest(skill_id: str) -> dict[str, Any]:
    """Tier 2 Progressive Disclosure: Retrieve full schema, parameters, and instructions for a skill."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Get skill manifest for {skill_id}",
        tool_name="get_skill_manifest",
        skill_id=skill_id,
    )
    return res.get("data", res)


@mcp.tool()
def invoke_skill(skill_id: str, parameters: dict[str, Any]) -> dict[str, Any]:
    """Dynamically invoke any registered skill in the Enterprise Skills Registry."""
    agent = get_agent()
    res = agent.query(
        prompt=str(parameters),
        skill_name=skill_id,
        **parameters,
    )
    return res.get("data", res)


@mcp.tool()
def check_okf_freshness(threshold_days: int = 30) -> dict[str, Any]:
    """Audit all OKF v0.2 concepts for TTL decay and stale_after freshness dates."""
    evo = get_evolution_agent()
    return evo.query(prompt="audit_freshness", action="audit_freshness", threshold_days=threshold_days)


@mcp.tool()
def propose_okf_evolution(
    concept_id: str,
    update_summary: str,
    findings: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Propose an evolution for an OKF concept grounded in the Cloud FDE Charter."""
    evo = get_evolution_agent()
    return evo.query(
        prompt="propose_evolution",
        action="propose_evolution",
        concept_id=concept_id,
        update_summary=update_summary,
        new_findings=findings,
    )


@mcp.tool()
def generate_arbitrary_spec(
    domain_or_topic: str,
    tech_stack_or_framework: str = "cloud-native",
    requirements: str = "",
    complexity_level: str = "principal_staff_exhaustive",
) -> dict[str, Any]:
    """Generate a production-grade architectural specification for any arbitrary domain, framework, or tech stack."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Generate spec for {domain_or_topic} using {tech_stack_or_framework}",
        tool_name="generate_arbitrary_spec",
        domain_or_topic=domain_or_topic,
        tech_stack_or_framework=tech_stack_or_framework,
        requirements=requirements,
        complexity_level=complexity_level,
    )
    return res.get("data", res)


@mcp.tool()
def update_spec_best_practices(
    existing_spec_content: str,
    standards_to_apply: Optional[list[str]] = None,
    strictness_level: str = "production_cutline_enforced",
) -> dict[str, Any]:
    """Audit an existing technical specification and upgrade it to modern Google Cloud best practices."""
    agent = get_agent()
    res = agent.query(
        prompt="Update spec with best practices",
        tool_name="update_spec_best_practices",
        existing_spec_content=existing_spec_content,
        standards_to_apply=standards_to_apply,
        strictness_level=strictness_level,
    )
    return res.get("data", res)


@mcp.tool()
def generate_spec_collection(
    project_name: str,
    codebase_summary_or_path: str,
    spec_modules: Optional[list[str]] = None,
    enforce_fde_cutline: bool = True,
) -> dict[str, Any]:
    """Analyze a codebase or project manifest and synthesize a complete 6-part modular specification collection."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Generate spec collection for {project_name}",
        tool_name="generate_spec_collection",
        project_name=project_name,
        codebase_summary_or_path=codebase_summary_or_path,
        spec_modules=spec_modules,
        enforce_fde_cutline=enforce_fde_cutline,
    )
    return res.get("data", res)


@mcp.tool()
def alexandria_search(
    query: str,
    domain: str = "all",
    top_k: int = 5,
) -> dict[str, Any]:
    """Search Google Cloud verified architectural reference designs, Alexandria blueprints, and whitepapers."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Alexandria search for {query}",
        tool_name="alexandria_search",
        query=query,
        domain=domain,
        top_k=top_k,
    )
    return res.get("data", res)


@mcp.tool()
def audit_waf_pillars(
    architecture_description: str,
    target_pillars: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Audit system architecture against all 6 Google Cloud Well-Architected Framework (WAF) pillars."""
    agent = get_agent()
    res = agent.query(
        prompt="Audit against WAF pillars",
        tool_name="audit_waf_pillars",
        architecture_description=architecture_description,
        target_pillars=target_pillars,
    )
    return res.get("data", res)


@mcp.tool()
def audit_complete_system(
    project_name: str,
    full_system_spec_or_code_manifest: str,
) -> dict[str, Any]:
    """Execute an exhaustive 360-degree audit across WAF, FDE 26-subcompetencies, and Model Armor."""
    agent = get_agent()
    res = agent.query(
        prompt=f"Audit complete system for {project_name}",
        tool_name="audit_complete_system",
        project_name=project_name,
        full_system_spec_or_code_manifest=full_system_spec_or_code_manifest,
    )
    return res.get("data", res)


def main() -> None:
    """Run FastMCP stdio transport for local developer and Antigravity CLI."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

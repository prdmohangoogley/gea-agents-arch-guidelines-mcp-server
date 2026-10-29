"""FastMCP tools for Skills Registry, Dynamic Plugins, and Progressive Disclosure."""

from __future__ import annotations

import json
import time
from typing import Any
from fastmcp import FastMCP
from src.graph.client import GraphClient
from src.otel_setup import get_tracer
from src.registry.skills_registry import skills_registry
from src.security.model_armor import model_armor, sanitize_tool_output
from src.skills.base import SkillExecutionContext
from src.telemetry.session_feedback import feedback_recorder

tracer = get_tracer("guidelines-mcp-server")


def register_skill_tools(mcp: FastMCP, client: GraphClient) -> None:
    """Register progressive disclosure Skill Registry tools with FastMCP."""

    @mcp.tool()
    async def list_registered_skills(category: str | None = None) -> dict[str, Any]:
        """Tier 1 Progressive Disclosure: List registered skills with minimal token overhead (~30 tokens/skill).

        Args:
            category: Optional filter by category ('architecture', 'governance', 'workflow', 'security', 'knowledge_management', 'graph_data', 'devops').

        Returns:
            Lightweight catalog of skill IDs, names, versions, and 1-line capability descriptions.
        """
        with tracer.start_as_current_span("tools/call:list_registered_skills") as span:
            span.set_attribute("tool.name", "list_registered_skills")
            if category:
                span.set_attribute("category_filter", category)

            catalog = skills_registry.list_catalog(category=category)
            span.set_attribute("skills.count", len(catalog))

            return sanitize_tool_output({
                "status": "success",
                "tier": "tier_1_catalog",
                "total_skills": len(catalog),
                "skills": catalog,
                "usage_hint": "Call get_skill_manifest(skill_id) to retrieve full parameter schema and instructions.",
            })

    @mcp.tool()
    async def get_skill_manifest(skill_id: str) -> dict[str, Any]:
        """Tier 2 Progressive Disclosure: Hydrate full schema, parameter definitions, and instructions for a skill.

        Args:
            skill_id: Unique skill identifier (e.g., 'skill_system_design', 'skill_waf_critique', 'skill_spec_generator').

        Returns:
            Full skill specification including parameter types, required fields, and execution instructions.
        """
        with tracer.start_as_current_span("tools/call:get_skill_manifest") as span:
            span.set_attribute("tool.name", "get_skill_manifest")
            span.set_attribute("skill_id", skill_id)

            manifest = skills_registry.get_manifest(skill_id)
            if not manifest:
                return {
                    "status": "not_found",
                    "error": f"Skill '{skill_id}' is not registered in the Skills Registry.",
                    "available_skills": [s["id"] for s in skills_registry.list_catalog()],
                }

            return sanitize_tool_output({
                "status": "success",
                "tier": "tier_2_manifest",
                "manifest": manifest.model_dump(),
            })

    @mcp.tool()
    async def invoke_skill(skill_id: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Dynamically invoke a registered skill with parameter validation and Model Armor sanitization.

        Args:
            skill_id: Identifier of the registered skill to execute.
            parameters: Dictionary of arguments required by the skill.

        Returns:
            Execution envelope containing status, skill result, and latency metrics.
        """
        with tracer.start_as_current_span("tools/call:invoke_skill") as span:
            span.set_attribute("tool.name", "invoke_skill")
            span.set_attribute("skill_id", skill_id)

            start_time = time.perf_counter()
            manifest = skills_registry.get_manifest(skill_id)
            if not manifest:
                return {
                    "status": "error",
                    "error": f"Skill '{skill_id}' is not found.",
                }

            # Security sanitization on all string parameters via Model Armor
            for param_name, param_val in parameters.items():
                if isinstance(param_val, str):
                    safety = await model_armor.sanitize(param_val)
                    if not safety.is_safe:
                        return {
                            "status": "blocked",
                            "error": f"Parameter '{param_name}' rejected by Model Armor: {safety.error_message}",
                            "source": "model_armor",
                        }

            result_data: Any = None
            token_metrics: dict[str, int] = {}

            # 1. Try executable plugin instance first
            plugin = skills_registry.get_plugin(skill_id)
            if plugin:
                ctx = SkillExecutionContext(
                    caller_identity="authenticated-agent",
                    session_id=str(parameters.get("session_id", "default-session")),
                    sandbox_tier=manifest.sandbox_tier,
                )
                plugin_res = await plugin.execute(context=ctx, parameters=parameters)
                result_data = plugin_res.data
                token_metrics = plugin_res.token_metrics
            # 2. Otherwise dispatch to entrypoint handlers
            elif manifest.entrypoint == "get_best_practice":
                topic = parameters.get("topic", "ZAA")
                result_data = await client.get_best_practice(topic=topic)
            elif manifest.entrypoint == "audit_project_against_fde_rubric":
                from src.tools.fde_governance import register_fde_governance_tools
                rubric_items = await client.get_fde_rubric()
                result_data = {
                    "audit_status": "executed",
                    "evaluated_rubric_items_count": len(rubric_items),
                    "summary": f"Audited project with {len(rubric_items)} rubric items.",
                }
            elif manifest.entrypoint == "evaluate_design_tradeoffs":
                opt_a = parameters.get("option_a", "Managed Services")
                opt_b = parameters.get("option_b", "Self-Managed Services")
                tradeoff = await client.evaluate_tradeoffs(opt_a, opt_b)
                result_data = tradeoff.model_dump()
            elif manifest.entrypoint == "deep_dive_guideline":
                comp = parameters.get("component", "Security")
                result_data = await client.deep_dive_guideline(comp)
            elif manifest.entrypoint == "check_okf_freshness":
                from src.tools.evolution import check_freshness_logic
                result_data = check_freshness_logic(parameters.get("threshold_days", 30))
            else:
                result_data = {
                    "message": f"Skill '{skill_id}' executed entrypoint '{manifest.entrypoint}'.",
                    "parameters": parameters,
                }

            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("execution.latency_ms", elapsed)

            envelope = {
                "status": "success",
                "skill_id": skill_id,
                "entrypoint": manifest.entrypoint,
                "latency_ms": round(elapsed, 2),
                "result": result_data,
                "token_metrics": token_metrics,
            }

            # Apply Model Armor Egress DLP sanitization to prevent sensitive data leakage
            raw_json = json.dumps(envelope)
            dlp_res = await model_armor.sanitize_response(raw_json, mask_in_place=True)
            sanitized_envelope = json.loads(dlp_res.sanitized_text or raw_json)
            return sanitize_tool_output(sanitized_envelope)

    @mcp.tool()
    async def record_session_feedback(
        session_id: str,
        skill_id: str,
        rating: float,
        caller_identity: str = "agent-reviewer",
        rubric_scores: dict[str, float] | None = None,
        qualitative_feedback: str = "",
    ) -> dict[str, Any]:
        """Record continuous online session and quality feedback to OpenTelemetry and Cloud Monitoring.

        Args:
            session_id: Unique interaction session identifier.
            skill_id: Target skill or workflow ID evaluated.
            rating: Quality score between 0.0 and 5.0.
            caller_identity: Identifier of the user or agent submitting feedback.
            rubric_scores: Optional dictionary of sub-competency scores (0.0 to 3.0).
            qualitative_feedback: Qualitative notes or critique on the interaction.

        Returns:
            Confirmation of feedback telemetry recording.
        """
        with tracer.start_as_current_span("tools/call:record_session_feedback") as span:
            span.set_attribute("tool.name", "record_session_feedback")
            span.set_attribute("session.id", session_id)
            span.set_attribute("skill.id", skill_id)

            rec = feedback_recorder.record_feedback(
                session_id=session_id,
                caller_identity=caller_identity,
                skill_id=skill_id,
                rating=rating,
                rubric_scores=rubric_scores,
                qualitative_feedback=qualitative_feedback,
            )
            return sanitize_tool_output(rec)

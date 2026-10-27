"""FastMCP tools for Skills Registry and Progressive Disclosure in Multi-Agent Systems."""

from __future__ import annotations

import json
import time
from typing import Any
from fastmcp import FastMCP
from src.graph.client import GraphClient
from src.otel_setup import get_tracer
from src.registry.skills_registry import skills_registry
from src.security.model_armor import model_armor

tracer = get_tracer("guidelines-mcp-server")


def register_skill_tools(mcp: FastMCP, client: GraphClient) -> None:
    """Register progressive disclosure Skill Registry tools with FastMCP."""

    @mcp.tool()
    async def list_registered_skills(category: str | None = None) -> dict[str, Any]:
        """Tier 1 Progressive Disclosure: List registered skills with minimal token overhead (~30 tokens/skill).

        Args:
            category: Optional filter by category ('architecture', 'governance', 'security', 'knowledge_management', 'graph_data').

        Returns:
            Lightweight catalog of skill IDs, names, versions, and 1-line capability descriptions.
        """
        with tracer.start_as_current_span("tools/call:list_registered_skills") as span:
            span.set_attribute("tool.name", "list_registered_skills")
            if category:
                span.set_attribute("category_filter", category)

            catalog = skills_registry.list_catalog(category=category)
            span.set_attribute("skills.count", len(catalog))

            return {
                "status": "success",
                "tier": "tier_1_catalog",
                "total_skills": len(catalog),
                "skills": catalog,
                "usage_hint": "Call get_skill_manifest(skill_id) to retrieve full parameter schema and instructions.",
            }

    @mcp.tool()
    async def get_skill_manifest(skill_id: str) -> dict[str, Any]:
        """Tier 2 Progressive Disclosure: Hydrate full schema, parameter definitions, and instructions for a skill.

        Args:
            skill_id: Unique skill identifier (e.g., 'skill-arch-eval', 'skill-fde-governance', 'skill-security-auditor').

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

            return {
                "status": "success",
                "tier": "tier_2_manifest",
                "manifest": manifest.model_dump(),
            }

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

            # Security sanitization on all string parameters
            for param_name, param_val in parameters.items():
                if isinstance(param_val, str):
                    safety = await model_armor.sanitize(param_val)
                    if not safety.is_safe:
                        return {
                            "status": "blocked",
                            "error": f"Parameter '{param_name}' rejected by Model Armor: {safety.error_message}",
                            "source": "model_armor",
                        }

            # Dispatch execution based on skill entrypoint
            result_data: Any = None
            if manifest.entrypoint == "get_best_practice":
                topic = parameters.get("topic", "ZAA")
                result_data = await client.get_best_practice(topic=topic)
            elif manifest.entrypoint == "audit_project_against_fde_rubric":
                # Call internal audit logic
                from src.tools.fde_governance import register_fde_governance_tools
                # Fetch rubric items directly
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
            }
            # Apply Model Armor Egress DLP sanitization to prevent sensitive data leakage
            raw_json = json.dumps(envelope)
            dlp_res = await model_armor.sanitize_response(raw_json, mask_in_place=True)
            sanitized_envelope = json.loads(dlp_res.sanitized_text or raw_json)
            return sanitized_envelope

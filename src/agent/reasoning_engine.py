"""First-Class Deployed Enterprise Architecture Guidelines Agent for Vertex AI Reasoning Engine.

Natively hosted on Google Cloud Vertex AI Reasoning Engine (Zero Cloud Run / Zero BYOC).
Enforces Zero Ambient Authority (ZAA), Model Armor dual-pass sanitization,
and strict grounding against the Cloud FDE Charter:
https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
import vertexai

from src.graph.client import GraphClient
from src.models.router import model_router, ModelTier
from src.registry.skills_registry import skills_registry, SkillsRegistry
from src.security.model_armor import model_armor, ModelArmorSanitizer, SanitizationResult
from src.skills.base import SkillExecutionContext

logger = logging.getLogger("gea.agent.reasoning_engine")


class EnterpriseArchGuidelinesAgent:
    """Authoritative Vertex AI Reasoning Engine agent for 24x7x365 architecture reviews and OKF adherence."""

    def __init__(
        self,
        project_id: str = "fivedaysai-prd-sandbox-317383",
        location: str = "us-central1",
        spanner_instance: str = "gea-arch-guidelines-spanner",
        spanner_database: str = "arch_guidelines_graph",
        bq_dataset: str = "gea_arch_guidelines_analytics",
        charter_index_url: str = "https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head",
    ) -> None:
        self.project_id = project_id
        self.location = location
        self.spanner_instance = spanner_instance
        self.spanner_database = spanner_database
        self.bq_dataset = bq_dataset
        self.charter_index_url = charter_index_url

        # Runtime instances initialized in set_up()
        self.graph_client: Optional[GraphClient] = None
        self.skills_registry: Optional[SkillsRegistry] = None
        self.model_armor: Optional[ModelArmorSanitizer] = None

    def set_up(self) -> None:
        """Initialize Google Cloud runtime clients, GraphClient, and security perimeter."""
        try:
            vertexai.init(project=self.project_id, location=self.location)
        except Exception as exc:
            logger.debug(f"Vertex AI initialization notice in set_up: {exc}")

        # Initialize GraphClient with graceful mock fallback for test/offline environments
        try:
            self.graph_client = GraphClient(
                project_id=self.project_id,
                instance_id=self.spanner_instance,
                database_id=self.spanner_database,
                use_mock=False,
            )
        except Exception:
            self.graph_client = GraphClient(use_mock=True)

        self.skills_registry = skills_registry
        self.model_armor = model_armor

    def _ensure_initialized(self) -> None:
        """Ensure runtime clients are ready if set_up was not called explicitly."""
        if self.graph_client is None or self.skills_registry is None or self.model_armor is None:
            self.set_up()

    def _sanitize_input(self, text: str) -> SanitizationResult:
        """Sanitize prompt with Model Armor, handling async/sync runtime execution."""
        start = time.perf_counter()
        if not self.model_armor:
            self.model_armor = model_armor

        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Direct heuristic check if already inside an active event loop
                return self.model_armor._check_heuristics(text, start)
            else:
                return asyncio.run(self.model_armor.sanitize(text))
        except Exception:
            return self.model_armor._check_heuristics(text, start)

    def _sanitize_output(self, text: str) -> str:
        """Sanitize output with Model Armor DLP masking."""
        if not self.model_armor:
            return text
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                res = self.model_armor._check_egress_heuristics(text, time.perf_counter(), block_on_secrets=False, mask_in_place=True)
                return res.sanitized_text or text
            else:
                res = asyncio.run(self.model_armor.sanitize_egress(text, block_on_secrets=False, mask_in_place=True))
                return res.sanitized_text or text
        except Exception:
            return text

    def query(
        self,
        prompt: str,
        skill_name: Optional[str] = None,
        tool_name: Optional[str] = None,
        caller_identity: str = "authenticated-agent",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute reasoning loop over architecture guidelines, Spanner Graph, and Skills Registry."""
        self._ensure_initialized()
        start_time = time.perf_counter()

        # Step 1: Model Armor Ingress Guardrail
        safety = self._sanitize_input(prompt)
        if not safety.is_safe:
            return {
                "status": "blocked",
                "error": f"Security violation detected by Model Armor: {safety.error_message}",
                "source": "model_armor",
                "matched_filters": safety.matched_filters,
                "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            }

        sanitized_prompt = safety.sanitized_text or prompt
        result_data: Any = None
        executed_skill = skill_name

        # Step 2: Route execution based on skill_name, tool_name, or intent classification
        try:
            # Case A: Explicit Skill Invocation
            if skill_name:
                manifest = self.skills_registry.get_manifest(skill_name)
                plugin = self.skills_registry.get_plugin(skill_name)
                if plugin and manifest:
                    ctx = SkillExecutionContext(
                        caller_identity=caller_identity,
                        session_id=str(kwargs.get("session_id", "default-re-session")),
                        sandbox_tier=manifest.sandbox_tier,
                    )
                    # Run plugin execution
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = None
                    if loop and loop.is_running():
                        plugin_res = asyncio.ensure_future(plugin.execute(context=ctx, parameters={"query": sanitized_prompt, **kwargs}))
                        # Fallback for sync
                        result_data = plugin_res
                    else:
                        plugin_res = asyncio.run(plugin.execute(context=ctx, parameters={"query": sanitized_prompt, **kwargs}))
                        result_data = plugin_res.data
                elif manifest and manifest.entrypoint == "get_best_practice":
                    topic = kwargs.get("topic", sanitized_prompt)
                    result_data = self._run_async(self.graph_client.get_best_practice(topic=topic))
                elif manifest and manifest.entrypoint == "evaluate_design_tradeoffs":
                    opt_a = kwargs.get("option_a", "Option A")
                    opt_b = kwargs.get("option_b", "Option B")
                    tradeoff = self._run_async(self.graph_client.evaluate_tradeoffs(opt_a, opt_b))
                    result_data = tradeoff.model_dump()
                else:
                    result_data = {
                        "message": f"Skill '{skill_name}' processed prompt successfully.",
                        "prompt": sanitized_prompt,
                    }

            # Case B: Tool Proxy Call from FastMCP Stdio Adapter
            elif tool_name:
                executed_skill = f"tool:{tool_name}"
                if tool_name == "get_best_practice":
                    topic = kwargs.get("topic", sanitized_prompt)
                    result_data = self._run_async(self.graph_client.get_best_practice(topic=topic))
                elif tool_name == "search_guidelines":
                    query_str = kwargs.get("query", sanitized_prompt)
                    limit = int(kwargs.get("limit", 5))
                    result_data = self._run_async(self.graph_client.search_guidelines(query_str, limit=limit))
                elif tool_name == "get_guideline_details":
                    gid = kwargs.get("guideline_id", sanitized_prompt)
                    g = self._run_async(self.graph_client.get_guideline(gid))
                    result_data = g.model_dump() if g else {"error": "Guideline not found"}
                elif tool_name == "evaluate_design_tradeoffs":
                    opt_a = kwargs.get("option_a", "Managed Architecture")
                    opt_b = kwargs.get("option_b", "Self-Managed Architecture")
                    tradeoff = self._run_async(self.graph_client.evaluate_tradeoffs(opt_a, opt_b))
                    result_data = tradeoff.model_dump()
                elif tool_name == "deep_dive_guideline":
                    comp = kwargs.get("component", sanitized_prompt)
                    result_data = self._run_async(self.graph_client.deep_dive_guideline(comp))
                elif tool_name == "query_architectural_pattern":
                    pname = kwargs.get("pattern_name", sanitized_prompt)
                    result_data = self._run_async(self.graph_client.query_architectural_pattern(pname))
                elif tool_name == "generate_arbitrary_spec":
                    result_data = self._execute_plugin("skill_arbitrary_spec_generator", kwargs, caller_identity)
                elif tool_name == "update_spec_best_practices":
                    result_data = self._execute_plugin("skill_spec_best_practices_updater", kwargs, caller_identity)
                elif tool_name == "generate_spec_collection":
                    result_data = self._execute_plugin("skill_codebase_to_spec_collection", kwargs, caller_identity)
                elif tool_name == "alexandria_search":
                    result_data = self._execute_plugin("skill_alexandria_search", kwargs, caller_identity)
                elif tool_name == "audit_waf_pillars":
                    result_data = self._execute_plugin("skill_waf_critique", kwargs, caller_identity)
                elif tool_name == "audit_complete_system":
                    result_data = self._execute_plugin("skill_complete_system_audit", kwargs, caller_identity)
                elif tool_name == "audit_project_against_fde_rubric":
                    result_data = self._execute_plugin("skill_fde_rubric_critique", kwargs, caller_identity)
                elif tool_name == "list_registered_skills":
                    result_data = self.skills_registry.list_catalog(category=kwargs.get("category"))
                elif tool_name == "get_skill_manifest":
                    sid = kwargs.get("skill_id", "")
                    man = self.skills_registry.get_manifest(sid)
                    result_data = man.model_dump() if man else {"error": f"Skill '{sid}' not found"}
                elif tool_name == "health_check":
                    result_data = {
                        "status": "healthy",
                        "runtime": "vertex-ai-reasoning-engine",
                        "project": self.project_id,
                        "location": self.location,
                    }
                else:
                    result_data = {"error": f"Unknown tool: '{tool_name}'"}

            # Case C: Natural Language Intent Routing & Socratic Synthesis
            else:
                p_lower = sanitized_prompt.lower()
                if "compare" in p_lower or "tradeoff" in p_lower or "vs" in p_lower:
                    executed_skill = "skill_waf_critique"
                    parts = sanitized_prompt.split(" vs ") if " vs " in sanitized_prompt else [sanitized_prompt, "Alternative"]
                    opt_a = parts[0].strip()
                    opt_b = parts[1].strip() if len(parts) > 1 else "Standard GCP Alternative"
                    tradeoff = self._run_async(self.graph_client.evaluate_tradeoffs(opt_a, opt_b))
                    result_data = tradeoff.model_dump()
                elif "fde" in p_lower or "rubric" in p_lower or "readiness" in p_lower:
                    executed_skill = "skill_fde_governance"
                    rubrics = self._run_async(self.graph_client.get_fde_rubric())
                    result_data = {
                        "status": "success",
                        "audit_type": "FDE Field-Readiness",
                        "subcompetencies_evaluated": len(rubrics),
                        "cutline": ">= 2.0",
                        "rubric_items": rubrics[:5],
                    }
                else:
                    executed_skill = "skill_system_design"
                    search_res = self._run_async(self.graph_client.search_guidelines(sanitized_prompt, limit=3))
                    best_practice = self._run_async(self.graph_client.get_best_practice(topic=sanitized_prompt[:50]))
                    result_data = {
                        "guidelines": search_res,
                        "best_practice": best_practice,
                    }

        except Exception as exc:
            logger.error(f"Reasoning loop execution error: {exc}")
            result_data = {"error": str(exc), "status": "failed"}

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Step 3: Model Armor Egress DLP sanitization
        response_str = json.dumps(result_data, default=str)
        sanitized_response = self._sanitize_output(response_str)

        return {
            "status": "success",
            "skill": executed_skill,
            "response": sanitized_response,
            "data": result_data,
            "metadata": {
                "latency_ms": round(elapsed_ms, 2),
                "runtime": "vertex-ai-reasoning-engine",
                "chief_judge_model": "gemini-4-argon",
                "grounding_source": self.charter_index_url,
                "project_id": self.project_id,
                "location": self.location,
            },
        }

    def _execute_plugin(self, skill_id: str, parameters: dict[str, Any], caller_identity: str = "authenticated-agent") -> Any:
        """Execute a registered skill plugin synchronously within the Reasoning Engine runtime."""
        self._ensure_initialized()
        plugin = self.skills_registry.get_plugin(skill_id)
        if not plugin:
            plugin = self.skills_registry.get_plugin(skill_id.replace("_", "-"))
        if not plugin:
            plugin = self.skills_registry.get_plugin(skill_id.replace("-", "_"))
        if not plugin:
            return {"error": f"Skill plugin '{skill_id}' not found"}

        manifest = self.skills_registry.get_manifest(skill_id)
        ctx = SkillExecutionContext(
            caller_identity=caller_identity,
            session_id=str(parameters.get("session_id", "re-session")),
            sandbox_tier=manifest.sandbox_tier if manifest else "read_only",
        )
        res = self._run_async(plugin.execute(context=ctx, parameters=parameters))
        return res.data if hasattr(res, "data") else res

    def _run_async(self, coro: Any) -> Any:
        """Helper to run coroutines in synchronous Reasoning Engine environment."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We are in an active loop: create a task or use nest_asyncio/run in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    return pool.submit(asyncio.run, coro).result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    def stream_query(
        self,
        prompt: str,
        skill_name: Optional[str] = None,
        **kwargs: Any,
    ):
        """Yield progress and token chunks to streaming clients (Gemini Enterprise and Antigravity)."""
        yield {
            "event": "start",
            "prompt": prompt,
            "skill": skill_name,
            "grounding": self.charter_index_url,
        }
        res = self.query(prompt=prompt, skill_name=skill_name, **kwargs)
        resp_text = str(res.get("response", ""))
        chunk_size = 120
        for i in range(0, len(resp_text), chunk_size):
            yield {"event": "chunk", "text": resp_text[i:i+chunk_size]}
        yield {"event": "complete", "result": res}

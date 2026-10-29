"""FastMCP tools for Architectural Specification Generation, Modernization, and Auditing."""

from __future__ import annotations

import json
import time
from typing import Any, Optional
from fastmcp import FastMCP
from src.otel_setup import get_tracer
from src.registry.skills_registry import skills_registry
from src.security.model_armor import model_armor, sanitize_tool_output
from src.skills.base import SkillExecutionContext

tracer = get_tracer("guidelines-mcp-server")


def register_spec_tools(mcp: FastMCP) -> None:
    """Register engineering specification generation and modernization tools with FastMCP."""

    @mcp.tool()
    async def generate_arbitrary_spec(
        domain_or_topic: str,
        tech_stack_or_framework: str = "cloud-native",
        requirements: str = "",
        complexity_level: str = "principal_staff_exhaustive",
    ) -> dict[str, Any]:
        """Generate a production-grade architectural specification for any arbitrary domain, framework, or tech stack.

        Args:
            domain_or_topic: Target system domain (e.g. 'Real-time Payment Settlement', 'Edge IoT ML Inference', 'Multi-tenant B2B SaaS').
            tech_stack_or_framework: Primary technologies (e.g. 'Go + gRPC + Spanner', 'Rust + Tokio', 'FastMCP + Vertex AI').
            requirements: Functional requirements, scale, concurrency, and invariants.
            complexity_level: Target depth ('starter', 'detailed', 'principal_staff_exhaustive').

        Returns:
            Complete production-ready technical specification including ADRs, system diagrams, and acceptance criteria.
        """
        with tracer.start_as_current_span("tools/call:generate_arbitrary_spec") as span:
            span.set_attribute("tool.name", "generate_arbitrary_spec")
            span.set_attribute("spec.domain", domain_or_topic)

            combined_input = f"{domain_or_topic} {requirements}"
            safety = await model_armor.sanitize(combined_input)
            if not safety.is_safe:
                return {
                    "status": "blocked",
                    "error": f"Security violation detected by Model Armor: {safety.error_message}",
                    "source": "model_armor",
                }

            start_time = time.perf_counter()
            plugin = skills_registry.get_plugin("skill_arbitrary_spec_generator")
            if not plugin:
                return {"status": "error", "error": "Plugin 'skill_arbitrary_spec_generator' not found."}

            ctx = SkillExecutionContext(caller_identity="mcp-client", session_id="spec-gen", sandbox_tier="read_only")
            result = await plugin.execute(
                context=ctx,
                parameters={
                    "domain_or_topic": domain_or_topic,
                    "tech_stack_or_framework": tech_stack_or_framework,
                    "requirements": requirements,
                    "complexity_level": complexity_level,
                },
            )
            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("execution.latency_ms", elapsed)

            envelope = {
                "status": result.status,
                "tool": "generate_arbitrary_spec",
                "latency_ms": round(elapsed, 2),
                "data": result.data,
                "token_metrics": result.token_metrics,
            }
            return sanitize_tool_output(envelope)

    @mcp.tool()
    async def update_spec_best_practices(
        existing_spec_content: str,
        standards_to_apply: Optional[list[str]] = None,
        strictness_level: str = "production_cutline_enforced",
    ) -> dict[str, Any]:
        """Audit an existing technical specification and upgrade it to modern Google Cloud best practices.

        Applies Zero Ambient Authority (ZAA), Model Armor dual-pass sanitization, Spanner Graph ISO GQL,
        KV prefix caching, and modern frontier models (Gemini 3.1+, Gemini 4 Argon, GPT-5, Claude 5.*).

        Args:
            existing_spec_content: Markdown content or summary of the existing technical spec.
            standards_to_apply: Standards to inject (e.g. ['ZAA', 'WAF', 'Model_Armor_Dual_Pass', 'OTel_gRPC', 'Context_Caching', 'Modern_Models']).
            strictness_level: 'advisory' or 'production_cutline_enforced'.

        Returns:
            Architectural gap analysis, remediation summary, new ADRs, and upgraded specification markdown.
        """
        with tracer.start_as_current_span("tools/call:update_spec_best_practices") as span:
            span.set_attribute("tool.name", "update_spec_best_practices")

            safety = await model_armor.sanitize(existing_spec_content[:1000])
            if not safety.is_safe:
                return {
                    "status": "blocked",
                    "error": f"Security violation detected by Model Armor: {safety.error_message}",
                    "source": "model_armor",
                }

            start_time = time.perf_counter()
            plugin = skills_registry.get_plugin("skill_spec_best_practices_updater")
            if not plugin:
                return {"status": "error", "error": "Plugin 'skill_spec_best_practices_updater' not found."}

            ctx = SkillExecutionContext(caller_identity="mcp-client", session_id="spec-update", sandbox_tier="read_only")
            result = await plugin.execute(
                context=ctx,
                parameters={
                    "existing_spec_content": existing_spec_content,
                    "standards_to_apply": standards_to_apply or ["all"],
                    "strictness_level": strictness_level,
                },
            )
            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("execution.latency_ms", elapsed)

            envelope = {
                "status": result.status,
                "tool": "update_spec_best_practices",
                "latency_ms": round(elapsed, 2),
                "data": result.data,
                "token_metrics": result.token_metrics,
            }
            return sanitize_tool_output(envelope)

    @mcp.tool()
    async def generate_spec_collection(
        project_name: str,
        codebase_summary_or_path: str,
        spec_modules: Optional[list[str]] = None,
        enforce_fde_cutline: bool = True,
    ) -> dict[str, Any]:
        """Analyze a codebase or project manifest and synthesize a complete 6-part modular specification collection.

        Modules include:
        1. High-Level Architecture & Domain Boundaries
        2. Zero Trust Security & Zero Ambient Authority (ZAA)
        3. Tiered Storage & Spanner Graph Schema
        4. Protocols, Tools & Skills Registry
        5. Observability, OpenTelemetry & SRE
        6. Declarative IaC & Deployment Topology

        Args:
            project_name: Name of the project or repository.
            codebase_summary_or_path: Codebase structure, main files, technologies, and interface patterns.
            spec_modules: Optional subset of modules to generate.
            enforce_fde_cutline: Enforce FDE Rubric >= 2.0 cutline across all modules.

        Returns:
            Modular collection of specifications with cross-module links and acceptance criteria.
        """
        with tracer.start_as_current_span("tools/call:generate_spec_collection") as span:
            span.set_attribute("tool.name", "generate_spec_collection")
            span.set_attribute("spec.project", project_name)

            safety = await model_armor.sanitize(f"{project_name} {codebase_summary_or_path[:500]}")
            if not safety.is_safe:
                return {
                    "status": "blocked",
                    "error": f"Security violation detected by Model Armor: {safety.error_message}",
                    "source": "model_armor",
                }

            start_time = time.perf_counter()
            plugin = skills_registry.get_plugin("skill_codebase_to_spec_collection")
            if not plugin:
                return {"status": "error", "error": "Plugin 'skill_codebase_to_spec_collection' not found."}

            ctx = SkillExecutionContext(caller_identity="mcp-client", session_id="spec-collection", sandbox_tier="read_only")
            result = await plugin.execute(
                context=ctx,
                parameters={
                    "project_name": project_name,
                    "codebase_summary_or_path": codebase_summary_or_path,
                    "spec_modules": spec_modules or [
                        "01_high_level_architecture",
                        "02_zero_trust_security_zaa",
                        "03_tiered_storage_and_graph",
                        "04_protocols_and_skills_registry",
                        "05_observability_and_sre",
                        "06_iac_and_deployment",
                    ],
                    "enforce_fde_cutline": enforce_fde_cutline,
                },
            )
            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("execution.latency_ms", elapsed)

            envelope = {
                "status": result.status,
                "tool": "generate_spec_collection",
                "latency_ms": round(elapsed, 2),
                "data": result.data,
                "token_metrics": result.token_metrics,
            }
            return sanitize_tool_output(envelope)

    @mcp.tool()
    async def alexandria_search(
        query: str,
        domain: str = "all",
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Search Google Cloud verified architectural reference designs, Alexandria blueprints, and whitepapers.

        Grounded in the Google Cloud FDE Field-Readiness Charter & Architecture Index:
        https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head

        Args:
            query: Architectural search query (e.g., 'Zero Ambient Authority', 'Spanner Graph ISO GQL', 'Vertex AI Reasoning Engine').
            domain: Domain filter ('security', 'data', 'ai_agents', 'networking', 'all').
            top_k: Maximum number of verified reference designs to retrieve.

        Returns:
            Authoritative reference blueprints, canonical GQL/SQL patterns, and FDE Index references.
        """
        with tracer.start_as_current_span("tools/call:alexandria_search") as span:
            span.set_attribute("tool.name", "alexandria_search")
            span.set_attribute("query", query)

            safety = await model_armor.sanitize(query)
            if not safety.is_safe:
                return {
                    "status": "blocked",
                    "error": f"Security violation detected by Model Armor: {safety.error_message}",
                    "source": "model_armor",
                }

            start_time = time.perf_counter()
            plugin = skills_registry.get_plugin("skill_alexandria_search")
            if not plugin:
                return {"status": "error", "error": "Plugin 'skill_alexandria_search' not found."}

            ctx = SkillExecutionContext(caller_identity="mcp-client", session_id="alexandria-search", sandbox_tier="read_only")
            result = await plugin.execute(
                context=ctx,
                parameters={"query": query, "domain": domain, "top_k": top_k},
            )
            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("execution.latency_ms", elapsed)

            envelope = {
                "status": result.status,
                "tool": "alexandria_search",
                "latency_ms": round(elapsed, 2),
                "data": result.data,
                "token_metrics": result.token_metrics,
            }
            return sanitize_tool_output(envelope)

    @mcp.tool()
    async def audit_waf_pillars(
        architecture_description: str,
        target_pillars: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Audit system architecture against all 6 Google Cloud Well-Architected Framework (WAF) pillars.

        Pillars evaluated:
        1. Operational Excellence
        2. Security, Privacy & Compliance (Zero Ambient Authority, Model Armor)
        3. Reliability & Fault Tolerance
        4. Performance Efficiency
        5. Cost Optimization & Tokenomics
        6. Sustainability & Carbon Efficiency

        Args:
            architecture_description: Architectural description, service list, data stores, and topologies.
            target_pillars: Optional subset of pillars to evaluate.

        Returns:
            Pillar-by-pillar scores (0-100%), composite WAF score, high/medium risks, and remediation diffs.
        """
        with tracer.start_as_current_span("tools/call:audit_waf_pillars") as span:
            span.set_attribute("tool.name", "audit_waf_pillars")

            safety = await model_armor.sanitize(architecture_description[:1000])
            if not safety.is_safe:
                return {
                    "status": "blocked",
                    "error": f"Security violation detected by Model Armor: {safety.error_message}",
                    "source": "model_armor",
                }

            start_time = time.perf_counter()
            plugin = skills_registry.get_plugin("skill_waf_critique")
            if not plugin:
                return {"status": "error", "error": "Plugin 'skill_waf_critique' not found."}

            ctx = SkillExecutionContext(caller_identity="mcp-client", session_id="waf-audit", sandbox_tier="read_only")
            result = await plugin.execute(
                context=ctx,
                parameters={
                    "architecture_description": architecture_description,
                    "target_pillars": target_pillars or ["all"],
                },
            )
            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("execution.latency_ms", elapsed)

            envelope = {
                "status": result.status,
                "tool": "audit_waf_pillars",
                "latency_ms": round(elapsed, 2),
                "data": result.data,
                "token_metrics": result.token_metrics,
            }
            return sanitize_tool_output(envelope)

    @mcp.tool()
    async def audit_complete_system(
        project_name: str,
        full_system_spec_or_code_manifest: str,
    ) -> dict[str, Any]:
        """Execute an exhaustive 360-degree audit across WAF, FDE 26-subcompetencies, and Model Armor.

        Args:
            project_name: Name of the project or MCP server.
            full_system_spec_or_code_manifest: Complete documentation, code manifests, and infrastructure details.

        Returns:
            Authoritative FDE Certification Scorecard, zero-score disqualifier check, and prioritized remediation roadmap.
        """
        with tracer.start_as_current_span("tools/call:audit_complete_system") as span:
            span.set_attribute("tool.name", "audit_complete_system")
            span.set_attribute("project_name", project_name)

            safety = await model_armor.sanitize(f"{project_name} {full_system_spec_or_code_manifest[:500]}")
            if not safety.is_safe:
                return {
                    "status": "blocked",
                    "error": f"Security violation detected by Model Armor: {safety.error_message}",
                    "source": "model_armor",
                }

            start_time = time.perf_counter()
            plugin = skills_registry.get_plugin("skill_complete_system_audit")
            if not plugin:
                return {"status": "error", "error": "Plugin 'skill_complete_system_audit' not found."}

            ctx = SkillExecutionContext(caller_identity="mcp-client", session_id="complete-audit", sandbox_tier="read_only")
            result = await plugin.execute(
                context=ctx,
                parameters={
                    "project_name": project_name,
                    "full_system_spec_or_code_manifest": full_system_spec_or_code_manifest,
                },
            )
            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("execution.latency_ms", elapsed)

            envelope = {
                "status": result.status,
                "tool": "audit_complete_system",
                "latency_ms": round(elapsed, 2),
                "data": result.data,
                "token_metrics": result.token_metrics,
            }
            return sanitize_tool_output(envelope)

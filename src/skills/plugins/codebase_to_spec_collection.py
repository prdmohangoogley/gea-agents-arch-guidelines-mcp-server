"""Codebase to Spec Collection Generator Skill Plugin."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class CodebaseToSpecCollectionSkill(SkillPlugin):
    """Enterprise skill that inspects an entire codebase or project and generates a comprehensive collection of modular specifications applying all architectural best practices."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_codebase_to_spec_collection",
            name="Codebase to Architecture Spec Collection Generator",
            version="1.0.0",
            category="architecture",
            description="Analyzes a codebase or project manifest and synthesizes a complete collection of modular engineering specs applying enterprise best practices.",
            capabilities=["codebase_audit", "multi_spec_synthesis", "modular_spec_collection", "enterprise_alignment"],
            entrypoint="execute",
            context_token_estimate=400,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="project_name", type="string", description="Name of the project or repository"),
                SkillParameter(name="codebase_summary_or_path", type="string", description="Summary of repository structure, main source files, technologies, and interfaces"),
                SkillParameter(name="spec_modules", type="list", description="Modules to generate", required=False, default=[
                    "01_high_level_architecture",
                    "02_zero_trust_security_zaa",
                    "03_tiered_storage_and_graph",
                    "04_protocols_and_skills_registry",
                    "05_observability_and_sre",
                    "06_iac_and_deployment",
                ]),
                SkillParameter(name="enforce_fde_cutline", type="boolean", description="Enforce Google Cloud FDE Rubric >= 2.0 cutline", required=False, default=True),
            ],
            instructions="Inspects codebase architecture and synthesizes a complete, 6-part modular specification collection incorporating all enterprise best practices.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project = parameters.get("project_name", "Enterprise Codebase")
        summary = parameters.get("codebase_summary_or_path", "")
        modules = parameters.get("spec_modules", [
            "01_high_level_architecture",
            "02_zero_trust_security_zaa",
            "03_tiered_storage_and_graph",
            "04_protocols_and_skills_registry",
            "05_observability_and_sre",
            "06_iac_and_deployment",
        ])
        fde_cutline = parameters.get("enforce_fde_cutline", True)

        prompt = f"""You are a Google Cloud Distinguished Engineer & Enterprise Chief Architect.
Analyze the provided codebase and generate an authoritative, modular COLLECTION OF TECHNICAL SPECIFICATIONS for project: '{project}'.

Codebase / Repository Details:
{summary}

Requested Spec Modules to Synthesize:
{modules}

Enforce FDE Cutline (>= 2.0): {fde_cutline}

Mandatory Best Practice Principles to Apply Across All Specs:
1. Zero Ambient Authority (ZAA): No ambient service account roles; user-delegated downscoped tokens.
2. Dual-Pass Model Armor: Ingress regex + live API; egress DLP masking.
3. Modern Models Only: Gemini 3.1+ (Gemini 4 Argon Judge), OpenAI GPT-5, Claude 5.*. Zero legacy models.
4. Tiered Storage: Spanner Graph (ISO GQL), BigQuery (Analytics), GCS (Corpus).
5. Two-Tier Progressive Disclosure: Catalog summaries (< 600 tokens) vs hydrated schemas.
6. OpenTelemetry gRPC Tracing: Direct non-deprecated OTLP telemetry with Cloud Trace & Monitoring.
7. Declarative IaC: Production Terraform with non-root security contexts and health probes.

Generate the Spec Collection formatted cleanly as:
- Executive Summary & Project Topology
- Spec 01: High-Level Architecture & Component Decomposition
- Spec 02: Zero Trust Identity, ZAA & Model Armor Security
- Spec 03: Tiered Storage, Spanner Graph & Context Caching
- Spec 04: Protocols, Multi-Agent Mechanics & Skills Registry
- Spec 05: Observability, Distributed Tracing & SRE Operations
- Spec 06: Infrastructure as Code (Terraform) & Continuous Deployment
- FDE Rubric Compliance Matrix (Targeting >= 2.5 across all 26 sub-competencies).
"""
        response_text = await model_router.generate_text(
            prompt=prompt,
            temperature=0.2,
        )

        elapsed = (time.perf_counter() - start_time) * 1000
        prompt_tokens = self.estimate_tokens(prompt)
        completion_tokens = self.estimate_tokens(response_text)

        return SkillResult(
            status="success",
            skill_id="skill_codebase_to_spec_collection",
            latency_ms=round(elapsed, 2),
            data={
                "project_name": project,
                "modules_generated": modules,
                "fde_cutline_enforced": fde_cutline,
                "spec_collection_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

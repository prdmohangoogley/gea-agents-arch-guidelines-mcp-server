"""Architectural Spec Generator Skill Plugin."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class SpecGeneratorSkill(SkillPlugin):
    """Enterprise skill for generating production-grade engineering specifications and ADRs."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_spec_generator",
            name="Architectural Spec Generator",
            version="1.0.0",
            category="architecture",
            description="Generates production engineering specifications with ADRs, sequence diagrams, and threat models.",
            capabilities=["spec_drafting", "adr_generation", "threat_modeling", "api_schema_specification"],
            entrypoint="execute",
            context_token_estimate=320,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="title", type="string", description="Title of the specification or feature"),
                SkillParameter(name="context", type="string", description="Problem statement, user context, and business motivation"),
                SkillParameter(name="scope", type="string", description="In-scope vs out-of-scope boundaries"),
                SkillParameter(name="architecture_tier", type="string", description="Target tier ('backend', 'multi-agent', 'data-pipeline', 'full-stack')", required=False, default="multi-agent"),
            ],
            instructions="Generates a structured Google-standard technical spec containing ADRs, sequence diagrams, schemas, and verification tests.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        title = parameters.get("title", "Technical Specification")
        problem_context = parameters.get("context", "")
        scope = parameters.get("scope", "")
        tier = parameters.get("architecture_tier", "multi-agent")

        prompt = f"""You are a Google Staff Software Engineer & Solutions Architect.
Write an authoritative, complete Engineering Specification for: {title}

Context & Business Motivation:
{problem_context}

Scope & Non-Goals:
{scope}

Architecture Tier: {tier}

Format Requirements:
1. Document Metadata (Author, Target Date, Status: PROPOSED, Reviewers).
2. Architectural Decision Records (ADRs) with Context, Options Considered, Decision, and Consequences.
3. System Architecture & Sequence Diagram (GitHub-style Mermaid sequenceDiagram).
4. API / Protocol Interfaces (Pydantic / Proto / OpenAPI schemas).
5. Security & Identity Invariants (ZAA, Model Armor, Principal Access Boundaries).
6. Observability, Telemetry & SLOs (p95 latency, error budget, OpenTelemetry spans).
7. Test Strategy & Acceptance Criteria (Unit, Integration, Trajectory Evals).
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
            skill_id="skill_spec_generator",
            latency_ms=round(elapsed, 2),
            data={
                "title": title,
                "tier": tier,
                "specification_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

"""Arbitrary Domain and Technology Spec Generator Skill Plugin."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class ArbitrarySpecGeneratorSkill(SkillPlugin):
    """Enterprise skill for generating architectural specifications for arbitrary domains and tech stacks."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_arbitrary_spec_generator",
            name="Arbitrary Domain & Technology Spec Generator",
            version="1.0.0",
            category="architecture",
            description="Generates end-to-end production specifications for any arbitrary domain, framework, or technology stack.",
            capabilities=["universal_spec_generation", "cross_domain_architecture", "technology_selection", "adr_synthesis"],
            entrypoint="execute",
            context_token_estimate=320,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="domain_or_topic", type="string", description="Arbitrary domain or system topic (e.g., 'Real-time Payment Settlement', 'Edge IoT ML Inference', 'Multi-tenant B2B SaaS', 'Distributed Event Bus')"),
                SkillParameter(name="tech_stack_or_framework", type="string", description="Primary technologies or frameworks (e.g., 'Rust + Tokio', 'Go + gRPC', 'Python + FastAPI + Spanner', 'Kafka + Flink')", required=False, default="cloud-native"),
                SkillParameter(name="requirements", type="string", description="Functional requirements, business logic, and throughput targets"),
                SkillParameter(name="complexity_level", type="string", description="Target depth ('starter', 'detailed', 'principal_staff_exhaustive')", required=False, default="principal_staff_exhaustive"),
            ],
            instructions="Produces an exhaustive, production-ready technical specification tailored to any arbitrary domain.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        domain = parameters.get("domain_or_topic", "Enterprise Distributed System")
        stack = parameters.get("tech_stack_or_framework", "cloud-native")
        reqs = parameters.get("requirements", "")
        complexity = parameters.get("complexity_level", "principal_staff_exhaustive")

        prompt = f"""You are a Principal Software Architect with universal cross-domain expertise.
Write a comprehensive, exhaustive, production-grade Architectural Specification for:
Domain / Topic: {domain}
Tech Stack / Frameworks: {stack}
Complexity Target: {complexity}

Requirements & Invariants:
{reqs}

Specification Structure:
1. Executive Summary & Problem Scope (Domain constraints, scale, target throughput/concurrency).
2. Architectural Decisions & Tradeoffs (3+ ADRs comparing alternative approaches).
3. System Decomposition & Mermaid Component / Sequence Diagram.
4. Protocols, Schemas, and Interface Definitions (Pydantic / Protobuf / OpenAPI).
5. Storage Strategy & Data Consistency Guarantees (CAP theorem tradeoffs, ACID vs eventual consistency).
6. Security, Authentication & Zero Trust Enclaves.
7. Reliability, Fault Tolerance, Circuit Breaking & Disaster Recovery.
8. Observability & SLOs (Latency envelopes, trace points, error budgets).
9. Acceptance Test Criteria & Validation Plan.
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
            skill_id="skill_arbitrary_spec_generator",
            latency_ms=round(elapsed, 2),
            data={
                "domain": domain,
                "tech_stack": stack,
                "complexity": complexity,
                "specification_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

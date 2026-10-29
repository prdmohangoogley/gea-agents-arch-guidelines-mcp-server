"""System Design Enterprise Skill Plugin."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class SystemDesignSkill(SkillPlugin):
    """Enterprise skill for synthesizing scalable, Zero-Ambient-Authority system architectures."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_system_design",
            name="Enterprise System Designer",
            version="1.0.0",
            category="architecture",
            description="Synthesizes end-to-end enterprise architectures adhering to ZAA, tiered storage, and multi-agent topologies.",
            capabilities=["architecture_synthesis", "mermaid_diagramming", "security_boundary_modeling", "sla_capacity_planning"],
            entrypoint="execute",
            context_token_estimate=350,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="system_name", type="string", description="Name of the target system or service"),
                SkillParameter(name="requirements", type="string", description="Key functional and business requirements"),
                SkillParameter(name="constraints", type="dict", description="Operational constraints (e.g., latency, SLA, compliance, data residency)", required=False, default={}),
                SkillParameter(name="multi_agent_enabled", type="boolean", description="Whether system requires autonomous agent orchestration", required=False, default=True),
            ],
            instructions="Generates a complete architectural blueprint including component topology, Mermaid diagram, data flow, and threat model.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        sys_name = parameters.get("system_name", "Enterprise System")
        reqs = parameters.get("requirements", "")
        constraints = parameters.get("constraints", {})
        multi_agent = parameters.get("multi_agent_enabled", True)

        prompt = f"""You are an elite Google Cloud Principal Enterprise Architect.
Design a robust, enterprise-grade architecture for: {sys_name}

Requirements:
{reqs}

Constraints:
{constraints}

Multi-Agent Enabled: {multi_agent}

Strict Architectural Invariants:
1. Zero Ambient Authority (ZAA) and caller-delegated OAuth 2.0.
2. Tiered storage: Cloud Spanner (OLTP/Graph), BigQuery (Analytics/Vector), Cloud Storage (Raw/Artifacts).
3. Model Armor dual-pass sanitization and Cloud DLP egress masking.
4. Asynchronous event decoupling with Cloud Pub/Sub or Kafka.
5. Provide a valid GitHub-style Mermaid architecture flowchart.
6. Outline SLOs, SLA latency envelopes (p50, p95, p99), and disaster recovery.
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
            skill_id="skill_system_design",
            latency_ms=round(elapsed, 2),
            data={
                "system_name": sys_name,
                "architecture_spec": response_text,
                "zaa_enforced": True,
                "multi_agent_enabled": multi_agent,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

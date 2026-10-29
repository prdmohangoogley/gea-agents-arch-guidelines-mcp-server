"""Well-Architected Framework (WAF) Critique Skill Plugins."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class WAFCritiqueSkill(SkillPlugin):
    """Enterprise skill for evaluating architectures against all 6 GCP Well-Architected Framework pillars."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_waf_critique",
            name="Google Cloud Well-Architected Framework Auditor",
            version="1.0.0",
            category="governance",
            description="Evaluates system architectures across all 6 GCP Well-Architected Framework pillars with quantitative scoring.",
            capabilities=["waf_audit", "pillar_scoring", "gap_identification", "remediation_roadmap"],
            entrypoint="execute",
            context_token_estimate=320,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="architecture_description", type="string", description="Markdown description or specification of the architecture to audit"),
                SkillParameter(name="workload_type", type="string", description="Type of workload (e.g., 'multi_agent_system', 'transactional_oltp', 'data_lakehouse', 'edge_inference')", required=False, default="multi_agent_system"),
            ],
            instructions="Scores the workload across Operational Excellence, Security, Reliability, Performance, Cost, and Sustainability.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        arch = parameters.get("architecture_description", "")
        workload = parameters.get("workload_type", "multi_agent_system")

        prompt = f"""You are a Lead Google Cloud Well-Architected Reviewer.
Perform a full Well-Architected Framework (WAF) Review for this workload:
Workload Type: {workload}

Architecture:
{arch}

Score each of the 6 GCP WAF Pillars from 0.0 to 3.0:
1. Operational Excellence (Automation, CI/CD, Observability)
2. Security, Privacy & Compliance (Zero Ambient Authority, Model Armor, KMS, DLP)
3. Reliability (High Availability, Chaos Engineering, Failover, Spanner multi-region)
4. Performance Efficiency (p99 latency, compute scaling, KV-prefix cache optimization)
5. Cost Optimization (Intensive margin tokenomics, auto-scaling, resource right-sizing)
6. Sustainability & Carbon Footprint (Region selection, resource idle minimization)

Provide:
- Pillar-by-pillar scores and findings.
- High-Risk Issues (HRIs) and Medium-Risk Issues (MRIs).
- Prioritized remediation plan.
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
            skill_id="skill_waf_critique",
            latency_ms=round(elapsed, 2),
            data={
                "workload_type": workload,
                "waf_review_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )


class WAFPillarCritiqueSkill(SkillPlugin):
    """Enterprise skill for drilling down into a single GCP Well-Architected pillar."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_waf_pillar_critique",
            name="WAF Pillar Deep Dive Auditor",
            version="1.0.0",
            category="governance",
            description="Executes a deep-dive evaluation focused on a single GCP Well-Architected Framework pillar.",
            capabilities=["pillar_deep_dive", "compliance_check", "targeted_remediation"],
            entrypoint="execute",
            context_token_estimate=280,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="pillar_name", type="string", description="Pillar to audit: 'security', 'reliability', 'cost_optimization', 'operational_excellence', 'performance', 'sustainability'"),
                SkillParameter(name="architecture_description", type="string", description="Architecture text or spec section corresponding to this pillar"),
            ],
            instructions="Conducts an exhaustive deep-dive critique on the specified WAF pillar.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        pillar = parameters.get("pillar_name", "security").lower()
        arch = parameters.get("architecture_description", "")

        prompt = f"""You are a Google Cloud Principal Specialist in: {pillar.upper()}.
Perform a deep-dive Well-Architected Pillar Audit on:
{arch}

Evaluate specific pillar requirements, failure modes, trade-offs, and compliance with Google Cloud recommended architectures.
Provide an objective 0.0 - 3.0 score, identify blocking disqualifiers, and output an actionable remediation diff.
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
            skill_id="skill_waf_pillar_critique",
            latency_ms=round(elapsed, 2),
            data={
                "pillar_name": pillar,
                "pillar_audit_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

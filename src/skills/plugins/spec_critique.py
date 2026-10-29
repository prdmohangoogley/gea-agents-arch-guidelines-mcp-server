"""Spec Critique Socratic Skill Plugin."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class SpecCritiqueSkill(SkillPlugin):
    """Enterprise skill providing rigorous Socratic critique, anti-pattern detection, and edge-case grilling for technical specs."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_spec_critique",
            name="Architectural Spec Socratic Critic",
            version="1.0.0",
            category="advisory",
            description="Rigorously critiques technical specifications, flagging architectural antipatterns, SPOFs, and unaddressed edge cases.",
            capabilities=["spec_critique", "socratic_grilling", "antipattern_detection", "failure_mode_analysis"],
            entrypoint="execute",
            context_token_estimate=320,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="spec_text", type="string", description="Full specification content to critique"),
                SkillParameter(name="critique_perspective", type="string", description="Perspective: 'security_paranoid', 'scale_and_concurrency', 'resilience_chaos', 'comprehensive_lead_architect'", required=False, default="comprehensive_lead_architect"),
            ],
            instructions="Applies adversarial review and Socratic grilling to identify non-obvious failure modes in specifications.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        spec = parameters.get("spec_text", "")
        perspective = parameters.get("critique_perspective", "comprehensive_lead_architect")

        prompt = f"""You are Google's Most Demanding Architectural Review Board Critic.
Perspective: {perspective.upper()}

Review and ruthlessly critique the following specification:
{spec}

Critique Guidelines:
1. Anti-Pattern Detection: Unearth hidden anti-patterns (e.g. Ambient Authority, Split-Brain, Cascading Failures, Context Window Blowout).
2. Socratic Inquiries: Formulate 4 sharp Socratic questions that challenge unstated assumptions in the spec.
3. Concurrency & Scalability: Where will this system break under 100x traffic or race conditions?
4. Security & Isolation: How could a malicious subagent or prompt injection breach isolation?
5. Concrete Amendments: Provide the exact edits or ADR additions required to make this spec bulletproof.
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
            skill_id="skill_spec_critique",
            latency_ms=round(elapsed, 2),
            data={
                "perspective": perspective,
                "critique_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

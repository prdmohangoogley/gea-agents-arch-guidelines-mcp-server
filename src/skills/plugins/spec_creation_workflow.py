"""Spec Creation Workflow Orchestrator Skill Plugin."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class SpecCreationWorkflowSkill(SkillPlugin):
    """Enterprise skill orchestrating the 5-stage specification lifecycle from RFC to Sign-off."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_spec_creation_workflow",
            name="Specification Lifecycle Workflow Orchestrator",
            version="1.0.0",
            category="workflow",
            description="Governs the 5-stage spec development pipeline (RFC -> ADR -> Implementation Spec -> Threat Model -> Sign-off).",
            capabilities=["stage_gating", "workflow_orchestration", "reviewer_routing", "signoff_verification"],
            entrypoint="execute",
            context_token_estimate=300,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="spec_title", type="string", description="Title of the specification"),
                SkillParameter(name="current_stage", type="string", description="Current lifecycle stage ('rfc', 'adr_review', 'implementation_draft', 'threat_model', 'sign_off')", required=False, default="rfc"),
                SkillParameter(name="stage_payload", type="string", description="Content or draft corresponding to the current stage"),
            ],
            instructions="Orchestrates progression through the 5 architectural spec stages and evaluates stage exit criteria.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        title = parameters.get("spec_title", "Technical Specification")
        stage = parameters.get("current_stage", "rfc").lower()
        payload = parameters.get("stage_payload", "")

        stages = ["rfc", "adr_review", "implementation_draft", "threat_model", "sign_off"]
        next_stage = stages[min(stages.index(stage) + 1, len(stages) - 1)] if stage in stages else "rfc"

        prompt = f"""You are the Google Architecture Review Board (ARB) Workflow Engine.
Evaluate the specification stage readiness for '{title}'.

Stage Under Review: {stage.upper()}
Next Stage in Lifecycle: {next_stage.upper()}

Draft Content / Payload:
{payload}

Task:
1. Audit stage completeness against ARB standards.
2. Verify exit criteria for {stage.upper()}.
3. Provide concrete gating checklist (Pass, Conditional Pass, Block).
4. Produce necessary artifacts to advance to {next_stage.upper()}.
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
            skill_id="skill_spec_creation_workflow",
            latency_ms=round(elapsed, 2),
            data={
                "spec_title": title,
                "current_stage": stage,
                "next_stage": next_stage,
                "workflow_evaluation": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

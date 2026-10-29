"""Spec Best Practices Updater Skill Plugin."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class SpecBestPracticesUpdaterSkill(SkillPlugin):
    """Enterprise skill for auditing existing specifications and upgrading them to modern architectural best practices."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_spec_best_practices_updater",
            name="Specification Best Practices Updater",
            version="1.0.0",
            category="architecture",
            description="Audits existing technical specifications and upgrades them with modern GCP, ZAA, WAF, and Model Armor best practices.",
            capabilities=["spec_modernization", "gap_remediation", "adr_updates", "security_refactoring"],
            entrypoint="execute",
            context_token_estimate=350,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="existing_spec_content", type="string", description="Full markdown text or summary of the existing technical spec"),
                SkillParameter(name="standards_to_apply", type="list", description="List of standards to apply ('ZAA', 'WAF', 'Model_Armor_Dual_Pass', 'OTel_gRPC', 'Context_Caching', 'Modern_Models')", required=False, default=["all"]),
                SkillParameter(name="strictness_level", type="string", description="Strictness level ('advisory', 'production_cutline_enforced')", required=False, default="production_cutline_enforced"),
            ],
            instructions="Takes an existing spec, audits gaps against enterprise standards, and outputs a modernized, hardened specification with itemized diffs.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        spec_content = parameters.get("existing_spec_content", "")
        standards = parameters.get("standards_to_apply", ["all"])
        strictness = parameters.get("strictness_level", "production_cutline_enforced")

        prompt = f"""You are a Principal Enterprise Systems Auditor and Chief Solutions Architect.
Audit and upgrade the following technical specification against modern Google Cloud & enterprise best practices.

Standards to Apply: {standards}
Strictness Level: {strictness}

Mandatory Upgrade Dimensions:
1. Zero Ambient Authority (ZAA): Replace ambient service account privileges with caller-delegated downscoped tokens.
2. Dual-Pass Model Armor: Ingress fast-regex + async cloud screening; egress DLP masking.
3. Model Fleet Modernization: Eliminate legacy models (e.g. gemini-2.5, 2.0, 1.5, gpt-3.5); standardize on Gemini 3.1+ (Gemini 4 Argon Judge), OpenAI GPT-5, and Claude 5.*.
4. Tiered Storage & Graph: Leverage Cloud Spanner Graph (ISO GQL) for relational graph traversal and BigQuery for federated analytics.
5. Context Engineering & Prefix Caching: Structure invariant prompts into static KV-cache prefixes for 75% cost savings.
6. Observability: Replace deprecated Cloud Trace exporters with modern gRPC OpenTelemetry OTLP exporters.
7. Two-Tier Progressive Disclosure: Catalog summaries (< 600 tokens) vs hydrated manifests.

Original Specification:
{spec_content}

Output Format:
1. Architectural Gap Analysis (Deficiencies & Antipatterns Identified).
2. Remediation Summary & New ADRs Added.
3. Upgraded Complete Technical Specification (Production-Grade Markdown).
4. Verification & Trajectory Test Checklist.
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
            skill_id="skill_spec_best_practices_updater",
            latency_ms=round(elapsed, 2),
            data={
                "standards_applied": standards,
                "strictness_level": strictness,
                "upgraded_specification_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

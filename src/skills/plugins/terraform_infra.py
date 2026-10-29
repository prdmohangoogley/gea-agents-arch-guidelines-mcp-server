"""Terraform Infrastructure Skill Plugin."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class TerraformInfraSkill(SkillPlugin):
    """Enterprise skill for generating, auditing, and hardening Terraform HCL for Google Cloud multi-agent and data infrastructure."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_terraform_infra",
            name="Terraform Infrastructure Auditor & Synthesizer",
            version="1.0.0",
            category="devops",
            description="Generates, audits, and hardens Terraform HCL for Cloud Spanner, Vertex AI, BigQuery, and IAM following least-privilege standards.",
            capabilities=["terraform_synthesis", "hcl_security_audit", "iam_least_privilege", "spanner_iac"],
            entrypoint="execute",
            context_token_estimate=350,
            sandbox_tier="infra_deploy",
            parameters=[
                SkillParameter(name="action", type="string", description="Action: 'generate', 'audit_hcl', 'security_scan'", required=False, default="generate"),
                SkillParameter(name="infrastructure_requirements", type="string", description="Requirements for resources (e.g. Spanner Graph, Vertex AI Reasoning Engine, BigQuery, KMS)"),
                SkillParameter(name="existing_hcl", type="string", description="Existing HCL code (for audit or security scan)", required=False, default=""),
            ],
            instructions="Produces battle-tested Terraform HCL adhering to Google Cloud CIS Foundation benchmarks and Zero Ambient Authority.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        action = parameters.get("action", "generate").lower()
        reqs = parameters.get("infrastructure_requirements", "")
        hcl = parameters.get("existing_hcl", "")

        prompt = f"""You are a Principal Google Cloud Terraform & Site Reliability Engineer.
Action: {action.upper()}

Requirements:
{reqs}

Existing HCL (if applicable):
{hcl}

Mandatory Infrastructure Guardrails:
1. Least Privilege IAM: Never grant `roles/owner` or `roles/editor`. Use specific fine-grained roles.
2. Security Defaults: Cloud KMS customer-managed encryption keys (CMEK) references where required.
3. Private Service Connect (PSC) and VPC Service Controls compatibility.
4. Clean, modular Terraform HCL with variable validation and resource tagging.
5. Provide:
   - Valid Terraform HCL code blocks.
   - Variables and Outputs definitions.
   - CIS Benchmark & ZAA compliance notes.
"""
        response_text = await model_router.generate_text(
            prompt=prompt,
            temperature=0.1,
        )

        elapsed = (time.perf_counter() - start_time) * 1000
        prompt_tokens = self.estimate_tokens(prompt)
        completion_tokens = self.estimate_tokens(response_text)

        return SkillResult(
            status="success",
            skill_id="skill_terraform_infra",
            latency_ms=round(elapsed, 2),
            data={
                "action": action,
                "terraform_result_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

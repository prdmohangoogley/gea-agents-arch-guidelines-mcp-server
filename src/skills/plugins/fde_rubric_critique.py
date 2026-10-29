"""FDE Rubric Critique and Complete System Audit Skill Plugins."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class FDERubricCritiqueSkill(SkillPlugin):
    """Enterprise skill for evaluating architectures against specific FDE Rubric sub-competencies."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_rubric_level_critique",
            name="FDE Rubric Sub-Competency Grader",
            version="1.0.0",
            category="governance",
            description="Evaluates architectures against specific sub-competencies in the Google Cloud FDE Rubric, strictly enforcing the >= 2.0 cutline.",
            capabilities=["rubric_grading", "subcompetency_critique", "disqualifier_detection"],
            entrypoint="execute",
            context_token_estimate=300,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="subcompetency_id", type="string", description="Rubric sub-competency ID (e.g., 'RUBRIC-B-1-1' for ZAA, 'RUBRIC-B-3-1' for Model Armor, 'RUBRIC-B-4-1' for OTel)"),
                SkillParameter(name="system_summary", type="string", description="Architecture summary, implementation details, or test logs"),
            ],
            instructions="Scores the system against the specific rubric standard and flags any 0-score disqualifiers.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        rubric_id = parameters.get("subcompetency_id", "RUBRIC-B-1-1")
        summary = parameters.get("system_summary", "")

        prompt = f"""You are the Google Cloud FDE Project Certification Auditor.
Evaluate this architecture against Rubric Sub-Competency: {rubric_id}

System Summary / Posture:
{summary}

Scoring Scale (0.0 to 3.0):
- 0.0: Disqualified / Critical Blocker (e.g. ambient credentials, hardcoded keys, zero evals).
- 1.0: Basic Prototype (vulnerable, unvalidated, partial).
- 2.0: PRODUCTION MINIMUM CUTLINE (meets all enterprise security & reliability baselines).
- 3.0: Exemplary / Golden Reference (exceeds standards, automated self-healing, complete telemetry).

Task:
1. Provide precise numerical score (0.0 - 3.0).
2. Detail Pass/Fail status against the 2.0 cutline.
3. Identify any 0-score disqualifier.
4. List concrete remediation steps to reach 3.0.
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
            skill_id="skill_rubric_level_critique",
            latency_ms=round(elapsed, 2),
            data={
                "subcompetency_id": rubric_id,
                "rubric_evaluation_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )


class CompleteSystemAuditSkill(SkillPlugin):
    """Enterprise skill executing an exhaustive multi-pillar system audit combining WAF, FDE Rubric, and Model Armor."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_complete_system_audit",
            name="Comprehensive Multi-Pillar System Auditor",
            version="1.0.0",
            category="governance",
            description="Executes a complete 360-degree audit across WAF, FDE 26-subcompetencies, and Model Armor security perimeters.",
            capabilities=["full_system_audit", "composite_scoring", "disqualifier_detection", "production_certification"],
            entrypoint="execute",
            context_token_estimate=450,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="project_name", type="string", description="Name of the project or MCP server"),
                SkillParameter(name="full_system_spec_or_code_manifest", type="string", description="Full system documentation, code manifests, and infrastructure details"),
            ],
            instructions="Produces a definitive FDE Certification Scorecard and complete gap remediation roadmap.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project = parameters.get("project_name", "Enterprise System")
        manifest = parameters.get("full_system_spec_or_code_manifest", "")

        prompt = f"""You are the Google Cloud Principal Architecture Certification Board.
Perform a COMPREHENSIVE 360-DEGREE AUDIT of project: '{project}'.

System Specification & Code Manifest:
{manifest}

Audit Structure:
1. Executive Verdict & FDE Composite Score (Average of 26 sub-competencies, Cutline >= 2.0).
2. Critical Disqualifiers Check (Any 0.0 scores triggers IMMEDIATE PAUSE).
3. Detailed Pillar Evaluation:
   - Part A: Advisory Rigor & Value Grounding
   - Part B.1: Architecture & Zero Ambient Authority (ZAA)
   - Part B.2: Quality, Trajectory Evals & Quality Flywheel
   - Part B.3: Security, Model Armor & Data Protection
   - Part B.4: Observability, OpenTelemetry & Logging
   - Part B.5: Operational Readiness & IaC
   - Part B.6: Tokenomics & Cost Compression
   - Part B.7: Context Engineering & KV Caching
   - Part B.8: Socratic Grilling & Elicitation
4. Prioritized Production Remediation Roadmap (P0 Blockers, P1 High, P2 Enhancements).
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
            skill_id="skill_complete_system_audit",
            latency_ms=round(elapsed, 2),
            data={
                "project_name": project,
                "audit_verdict_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

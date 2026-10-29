"""Alexandria Verified Best Practices Search Skill Plugin."""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router


class AlexandriaSearchSkill(SkillPlugin):
    """Enterprise skill for querying Google Cloud Alexandria architectural reference designs and verified best practices."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_alexandria_search",
            name="Alexandria Best Practices Search",
            version="1.0.0",
            category="knowledge_management",
            description="Searches Google Cloud verified architectural patterns, Alexandria blueprints, and enterprise whitepapers grounded in the Cloud FDE Charter (https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).",
            capabilities=["alexandria_search", "pattern_retrieval", "reference_architecture_matching", "fde_charter_grounding"],
            entrypoint="execute",
            context_token_estimate=280,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="query", type="string", description="Architectural search query or topic (e.g., 'Zero Ambient Authority', 'Spanner Graph ISO GQL', 'Vertex AI Reasoning Engine')"),
                SkillParameter(name="domain", type="string", description="Domain filter (e.g. 'security', 'data', 'ai_agents', 'networking')", required=False, default="all"),
                SkillParameter(name="top_k", type="integer", description="Maximum number of verified designs to retrieve", required=False, default=5),
            ],
            instructions="Retrieves official Google Cloud blueprints, verified implementation patterns, and antipattern mitigations grounded in Cloud FDE index.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        query = parameters.get("query", "Google Cloud Architecture Best Practices")
        domain = parameters.get("domain", "all")
        top_k = parameters.get("top_k", 5)

        prompt = f"""You are the Google Cloud Alexandria Knowledge Engine, authoritative for Google Cloud verified architectural reference designs and grounded in the Google Cloud FDE Field-Readiness Charter & Architecture Index (https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).

Retrieve and synthesize verified enterprise architectural best practices for:
Query: {query}
Domain: {domain}
Max Results: {top_k}

Primary Grounding Source:
- Google Cloud FDE Field-Readiness & Architectural Reference Design Index: https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head
- Alexandria Blueprints, verified enterprise whitepapers, and field-tested architectural reference designs.

Format the response with:
1. Executive Architectural Recommendation (strictly aligned with Cloud FDE Charter).
2. Verified Alexandria Reference Blueprints (Service components, Zero Ambient Authority IAM boundaries, VPC-SC network perimeters).
3. Canonical GQL / SQL Patterns (Cloud Spanner Graph & BigQuery).
4. Critical Antipatterns & Disqualifiers (per FDE Rubric Part A & B).
5. Official Google Cloud Documentation & FDE Index References (https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head).
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
            skill_id="skill_alexandria_search",
            latency_ms=round(elapsed, 2),
            data={
                "query": query,
                "domain": domain,
                "top_k": top_k,
                "alexandria_results_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

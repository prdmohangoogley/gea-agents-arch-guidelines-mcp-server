"""Dynamic Skills Discovery and Catalog Skill Plugin."""

from __future__ import annotations

import os
import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext


class DynamicDiscoverySkill(SkillPlugin):
    """Enterprise skill for dynamically discovering, cataloging, and querying agent skills across local directories and plugins."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_discovery_and_catalog",
            name="Dynamic Skills Discovery & Catalog Engine",
            version="1.0.0",
            category="knowledge_management",
            description="Dynamically discovers, catalogs, and inspects agent skills across workspaces, .agents/skills/, and python plugins.",
            capabilities=["skills_discovery", "catalog_query", "capability_matching", "progressive_disclosure"],
            entrypoint="execute",
            context_token_estimate=250,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="query_or_capability", type="string", description="Optional capability or keyword to search for (e.g., 'spec', 'audit', 'waf', 'all')", required=False, default="all"),
                SkillParameter(name="include_manifests", type="boolean", description="Whether to hydrate Tier 2 full manifests or return Tier 1 lightweight summaries", required=False, default=False),
            ],
            instructions="Scans the environment for available skills and returns catalog metadata or hydrated manifests.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        query = parameters.get("query_or_capability", "all").lower()
        include_manifests = parameters.get("include_manifests", False)

        from src.skills.discovery import discover_all_skills

        all_manifests = discover_all_skills()

        filtered_manifests = []
        for m in all_manifests:
            if query == "all":
                filtered_manifests.append(m)
            else:
                matches = (
                    query in m.id.lower()
                    or query in m.name.lower()
                    or query in m.description.lower()
                    or any(query in cap.lower() for cap in m.capabilities)
                    or query in m.category.lower()
                )
                if matches:
                    filtered_manifests.append(m)

        if include_manifests:
            results = [m.model_dump() for m in filtered_manifests]
        else:
            results = [
                {
                    "id": m.id,
                    "name": m.name,
                    "version": m.version,
                    "category": m.category,
                    "description": m.description,
                    "capabilities": m.capabilities,
                    "token_estimate": m.context_token_estimate,
                }
                for m in filtered_manifests
            ]

        elapsed = (time.perf_counter() - start_time) * 1000

        return SkillResult(
            status="success",
            skill_id="skill_discovery_and_catalog",
            latency_ms=round(elapsed, 2),
            data={
                "query": query,
                "tier": "tier_2_hydrated" if include_manifests else "tier_1_summary",
                "matched_count": len(results),
                "skills": results,
            },
            token_metrics={
                "prompt_tokens_estimated": 80,
                "completion_tokens_estimated": max(50, len(results) * 35),
                "tokens_saved_by_cache": 0,
            },
        )

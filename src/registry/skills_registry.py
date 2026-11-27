"""Skills Registry data structures and loader for Gemini Enterprise multi-agent systems."""

from __future__ import annotations

from typing import Any, Optional
from src.skills.base import SkillParameter, SkillManifest, SkillPlugin
from src.skills.discovery import discover_all_skills, get_plugin_instance, init_skills_registry


# Canonical legacy and core skills registered for Gemini Enterprise multi-agent fleets
CANONICAL_SKILLS: list[SkillManifest] = [
    SkillManifest(
        id="skill-arch-eval",
        name="Architecture Guidelines Evaluator",
        version="1.2.0",
        category="architecture",
        description="Evaluates agent system designs against Google Cloud architectural best practices and GQL patterns.",
        capabilities=["architecture_audit", "spanner_graph_query", "tradeoff_evaluation"],
        entrypoint="get_best_practice",
        context_token_estimate=250,
        sandbox_tier="read_only",
        parameters=[
            SkillParameter(name="topic", type="string", description="Architectural topic or pattern keyword (e.g., 'ZAA', 'Memory Bank')")
        ],
        instructions="Queries Cloud Spanner Graph to retrieve validated guidelines, implemented patterns, and antipattern mitigations.",
    ),
    SkillManifest(
        id="skill-fde-governance",
        name="FDE Field-Readiness Auditor",
        version="1.0.0",
        category="governance",
        description="Audits project architectures against the Google Cloud FDE Rubric, enforcing the >= 2.0 cutline.",
        capabilities=["rubric_grading", "disqualifier_detection", "remediation_roadmap"],
        entrypoint="audit_project_against_fde_rubric",
        context_token_estimate=320,
        sandbox_tier="read_only",
        parameters=[
            SkillParameter(name="project_manifest_or_description", type="string", description="Markdown summary of architecture and test posture"),
            SkillParameter(name="target_domains", type="list", description="Optional domains to restrict audit to", required=False),
        ],
        instructions="Executes quantitative evaluation against 26 FDE sub-competencies and flags zero-score disqualifiers.",
    ),
    SkillManifest(
        id="skill-security-auditor",
        name="Zero Ambient Authority & Model Armor Auditor",
        version="1.1.0",
        category="security",
        description="Audits zero ambient authority, Model Armor dual-pass sanitization, and PAB perimeters.",
        capabilities=["security_audit", "model_armor_verification", "pab_boundary_check"],
        entrypoint="evaluate_design_tradeoffs",
        context_token_estimate=280,
        sandbox_tier="read_only",
        parameters=[
            SkillParameter(name="option_a", type="string", description="Primary architecture option"),
            SkillParameter(name="option_b", type="string", description="Comparative architecture option"),
        ],
        instructions="Evaluates architectural security tradeoffs between managed Zero Ambient Authority and ambient credentials.",
    ),
    SkillManifest(
        id="skill-okf-evolution",
        name="Autonomous OKF Evolution Maintainer",
        version="2.0.0",
        category="knowledge_management",
        description="Audits concept staleness, discovers recent GCP updates via search, and drafts backward-compatible evolutions.",
        capabilities=["freshness_audit", "grounded_search", "concept_drafting", "sha256_verification"],
        entrypoint="check_okf_freshness",
        context_token_estimate=300,
        sandbox_tier="workspace_write",
        parameters=[
            SkillParameter(name="threshold_days", type="integer", description="Days prior to stale_after to flag", required=False, default=30)
        ],
        instructions="Monitors the 58 OKF v0.2 concepts for TTL decay and drafts AST-preserving markdown updates.",
    ),
    SkillManifest(
        id="skill-nl2kg-triplification",
        name="NL2KG Triplification & Knowledge Graph Pipeline",
        version="1.0.0",
        category="graph_data",
        description="Extracts semantic entities and relationships from markdown documents to generate graph triples.",
        capabilities=["entity_extraction", "triple_generation", "spanner_ingestion"],
        entrypoint="deep_dive_guideline",
        context_token_estimate=350,
        sandbox_tier="analytics_read",
        parameters=[
            SkillParameter(name="component", type="string", description="Target component or system to inspect in BigQuery")
        ],
        instructions="Extracts property graph nodes (Guideline, Pattern, Antipattern) and populates Cloud Spanner Graph.",
    ),
]


class SkillsRegistry:
    """Enterprise Skills Registry managing progressive disclosure, plugin lifecycle, and skill dispatching."""

    def __init__(self, skills: list[SkillManifest] | None = None) -> None:
        self._skills: dict[str, SkillManifest] = {
            s.id: s for s in (skills or CANONICAL_SKILLS)
        }

    def _ensure_dynamic_skills_loaded(self) -> None:
        """Load discovered dynamic plugins and workspace skills into the active registry."""
        try:
            init_skills_registry()
            discovered = discover_all_skills()
            for manifest in discovered:
                alias_hyphen = manifest.id.replace("_", "-")
                alias_under = manifest.id.replace("-", "_")
                # Skip workspace_skill SKILL.md mirrors when a static or plugin skill with the same ID already exists
                # (preserve legacy skill_nl2kg_triplification entry expected by the 58-skill catalog contract)
                if (
                    manifest.category == "workspace_skill"
                    and manifest.id != "skill_nl2kg_triplification"
                    and (
                        manifest.id in self._skills
                        or alias_hyphen in self._skills
                        or alias_under in self._skills
                    )
                ):
                    continue
                # Store under exact ID
                self._skills[manifest.id] = manifest
                # Also store hyphenated/underscored alias for flexible lookup
                if alias_hyphen not in self._skills:
                    self._skills[alias_hyphen] = manifest
                if alias_under not in self._skills:
                    self._skills[alias_under] = manifest
        except Exception:
            pass

    def list_catalog(self, category: str | None = None) -> list[dict[str, Any]]:
        """Tier 1 Progressive Disclosure: Lightweight summary list (~30 tokens per item)."""
        self._ensure_dynamic_skills_loaded()
        catalog = []
        seen_ids = set()

        for s in self._skills.values():
            # De-duplicate aliases
            normalized_id = s.id
            if normalized_id in seen_ids:
                continue
            seen_ids.add(normalized_id)

            if category and s.category.lower() != category.lower():
                continue

            catalog.append({
                "id": s.id,
                "name": s.name,
                "version": s.version,
                "category": s.category,
                "description": s.description,
                "capabilities": s.capabilities,
                "token_estimate": s.context_token_estimate,
            })
        return catalog

    def get_manifest(self, skill_id: str) -> SkillManifest | None:
        """Tier 2 Progressive Disclosure: Full detailed schema and execution instructions."""
        self._ensure_dynamic_skills_loaded()
        manifest = self._skills.get(skill_id)
        if not manifest:
            # Try alternate formatting (hyphens vs underscores)
            alt1 = skill_id.replace("-", "_")
            alt2 = skill_id.replace("_", "-")
            manifest = self._skills.get(alt1) or self._skills.get(alt2)
        return manifest

    def register_skill(self, skill: SkillManifest) -> None:
        """Dynamically register a new skill."""
        self._skills[skill.id] = skill

    def get_plugin(self, skill_id: str) -> SkillPlugin | None:
        """Retrieve executable plugin instance if registered."""
        self._ensure_dynamic_skills_loaded()
        # Check direct id, underscore id, or hyphen id
        plugin = get_plugin_instance(skill_id)
        if not plugin:
            plugin = get_plugin_instance(skill_id.replace("-", "_"))
        if not plugin:
            plugin = get_plugin_instance(skill_id.replace("_", "-"))
        return plugin


skills_registry = SkillsRegistry()

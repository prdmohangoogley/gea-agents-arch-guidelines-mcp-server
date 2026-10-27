"""Skills Registry data structures and loader for Gemini Enterprise multi-agent systems."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class SkillParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


class SkillManifest(BaseModel):
    id: str
    name: str
    version: str
    category: str
    description: str
    capabilities: list[str] = Field(default_factory=list)
    entrypoint: str
    context_token_estimate: int = 150
    sandbox_tier: str = "read_only"
    parameters: list[SkillParameter] = Field(default_factory=list)
    instructions: str = ""


# Default canonical skills registered for Gemini Enterprise multi-agent fleets
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
    """Enterprise Skills Registry managing progressive disclosure and skill dispatching."""

    def __init__(self, skills: list[SkillManifest] | None = None) -> None:
        self._skills: dict[str, SkillManifest] = {
            s.id: s for s in (skills or CANONICAL_SKILLS)
        }

    def list_catalog(self, category: str | None = None) -> list[dict[str, Any]]:
        """Tier 1 Progressive Disclosure: Lightweight summary list (~30 tokens per item)."""
        catalog = []
        for s in self._skills.values():
            if category and s.category.lower() != category.lower():
                continue
            catalog.append({
                "id": s.id,
                "name": s.name,
                "version": s.version,
                "category": s.category,
                "description": s.description,
                "token_estimate": s.context_token_estimate,
            })
        return catalog

    def get_manifest(self, skill_id: str) -> SkillManifest | None:
        """Tier 2 Progressive Disclosure: Full detailed schema and execution instructions."""
        return self._skills.get(skill_id)

    def register_skill(self, skill: SkillManifest) -> None:
        """Dynamically register a new skill."""
        self._skills[skill.id] = skill


skills_registry = SkillsRegistry()

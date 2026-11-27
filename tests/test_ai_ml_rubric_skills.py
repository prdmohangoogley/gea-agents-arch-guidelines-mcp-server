"""Unit tests for the 3 AI/ML Engineering Rubric skills and related remediations."""

from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel
import pytest

from src.models.router import MODEL_REGISTRY, ModelTier, MultiModelRouter
from src.skills.base import SkillExecutionContext
from src.skills.plugins.ai_ml_rubric import (
    AIMLRubricAssessmentFAQDocGeneratorSkill,
    AIMLRubricAssessmentFeedbackResolutionSkill,
    AIMLRubricAssessmentFeedbackSkill,
    FAQ_SECTION_END,
    FAQ_SECTION_START,
)


@pytest.mark.asyncio
async def test_assessment_skill_detects_failures_on_sparse_spec():
    """Verify sparse prototype spec fails rubric cutlines and produces actionable feedback."""
    skill = AIMLRubricAssessmentFeedbackSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Barebones Prototype",
            "project_manifest_or_spec": "A simple python script that calls an LLM.",
        },
    )
    assert res.status == "success"
    assessment = res.data["assessment"]
    assert assessment["overall_passed"] is False
    assert assessment["overall_status"] == "FAIL"
    assert len(assessment["feedback_items"]) > 0


@pytest.mark.asyncio
async def test_feedback_resolution_iterates_until_pass():
    """Verify feedback resolution orchestrates library skills and re-assesses until passing."""
    skill = AIMLRubricAssessmentFeedbackResolutionSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Prototype Agent App",
            "project_manifest_or_spec": "Basic agent script with no evals or RAG.",
            "max_iterations": 3,
        },
    )
    assert res.status == "success"
    assert res.data["final_passed"] is True
    assert res.data["final_status"] == "PASS"
    assert res.data["iterations_executed"] >= 2
    assert "eval-harness" in res.data["library_skills_orchestrated"]
    assert "fde-governance-auditor" in res.data["library_skills_orchestrated"]


@pytest.mark.asyncio
async def test_faq_doc_generator_creates_and_updates_faqs_md(tmp_path: Path):
    """Verify FAQ generator creates docs/FAQs.md if missing and preserves existing sections if present."""
    skill = AIMLRubricAssessmentFAQDocGeneratorSkill()
    faqs_file = tmp_path / "docs" / "FAQs.md"

    # 1. Create new docs/FAQs.md when it does not exist
    res1 = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Test AI Project",
            "project_manifest_or_summary": "ADK agent, Spanner Graph RRF, MultiModelRouter JSON mode, OTel, HIPAA DLP.",
            "docs_file_path": str(faqs_file),
            "write_to_disk": True,
        },
    )
    assert res1.status == "success"
    assert res1.data["write_result"]["action"] == "created_new_faqs_file"
    assert faqs_file.exists()
    content1 = faqs_file.read_text(encoding="utf-8")
    assert "# Frequently Asked Questions (FAQs)" in content1
    assert FAQ_SECTION_START in content1
    assert FAQ_SECTION_END in content1

    # 2. Add a custom non-rubric section, then re-run generator and ensure it is preserved
    custom_section = "\n## General Project FAQs\n\n**Q: How do I install?**\nRun `uv sync`.\n"
    faqs_file.write_text(custom_section + "\n" + content1, encoding="utf-8")

    res2 = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Test AI Project v2",
            "project_manifest_or_summary": "ADK agent, Spanner Graph RRF, MultiModelRouter JSON mode, OTel, HIPAA DLP.",
            "docs_file_path": str(faqs_file),
            "write_to_disk": True,
        },
    )
    assert res2.data["write_result"]["action"] == "updated_existing_section"
    content2 = faqs_file.read_text(encoding="utf-8")
    assert "## General Project FAQs" in content2
    assert "Test AI Project v2" in content2


def test_encoder_model_registered_in_model_registry():
    """Verify encoder-only embedding model is explicitly registered alongside decoder LLMs."""
    assert "gemini-embedding-001" in MODEL_REGISTRY
    spec = MODEL_REGISTRY["gemini-embedding-001"]
    assert spec.architecture == "encoder"
    assert spec.tier == ModelTier.EMBEDDING_ENCODER
    assert MODEL_REGISTRY["gemini-4-argon"].architecture == "decoder"


@pytest.mark.asyncio
async def test_router_generate_structured_json_mode():
    """Verify MultiModelRouter.generate_structured enforces JSON mode and Pydantic validation."""
    class DefenseScore(BaseModel):
        score: float
        reasoning: str
        confidence: float

    router = MultiModelRouter()
    res = await router.generate_structured(
        prompt="Cybersecurity and LLM Defense Judge: rate the overall defense.",
        response_schema=DefenseScore,
        model_id="gemini-4-argon",
    )
    assert res["response_mime_type"] == "application/json"
    assert res["schema_name"] == "DefenseScore"
    assert res["schema_valid"] is True
    assert res["parsed"]["score"] == 3.0

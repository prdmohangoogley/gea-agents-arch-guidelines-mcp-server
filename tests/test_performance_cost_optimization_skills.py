"""Unit tests and independent 50-skill trajectory evaluation for Performance & Cost Optimization skills."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from src.server import create_server
from src.skills.base import SkillExecutionContext
from src.skills.plugins.performance_cost_optimization import (
    PCO_FAQ_END,
    PCO_FAQ_START,
    PerformanceCostOptimizationAssessorFeedbackSkill,
    PerformanceCostOptimizationFAQsSkill,
    PerformanceCostOptimizationFeedbackResolverSkill,
)
from tests.test_all_38_skills_runbook import RUNBOOK_SKILL_PAYLOADS


@pytest.mark.asyncio
async def test_pco_assessor_detects_failures_on_unoptimized_spec():
    """Verify unoptimized spec fails all 3 Performance & Cost Optimization domains with feedback."""
    skill = PerformanceCostOptimizationAssessorFeedbackSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Unoptimized App",
            "project_manifest_or_spec": "A fixed single VM calling one large model with zero caching.",
            "scope": "spec",
        },
    )
    assert res.status == "success"
    assessment = res.data["assessment"]
    assert assessment["overall_passed"] is False
    assert assessment["overall_status"] == "FAIL"
    assert len(assessment["feedback_items"]) == 6


@pytest.mark.asyncio
async def test_pco_resolver_iterates_until_pass():
    """Verify resolver orchestrates FinOps/performance skills and re-assesses until all 3 domains pass."""
    skill = PerformanceCostOptimizationFeedbackResolverSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Unoptimized App",
            "project_manifest_or_spec": "Oversized static compute with bloated prompts and no caching.",
            "scope": "project",
            "max_iterations": 3,
        },
    )
    assert res.status == "success"
    assert res.data["final_passed"] is True
    assert res.data["final_status"] == "PASS"
    assert res.data["iterations_executed"] >= 2
    assert "waf-pillar-cost-optimization" in res.data["library_skills_orchestrated"]
    assert "waf-pillar-performance-optimization" in res.data["library_skills_orchestrated"]


@pytest.mark.asyncio
async def test_pco_faqs_initializes_new_and_appends_to_existing_faqs_md(tmp_path: Path):
    """Verify Performance & Cost FAQ skill creates docs/FAQs.md or appends preserving existing sections."""
    skill = PerformanceCostOptimizationFAQsSkill()
    faqs_file = tmp_path / "docs" / "FAQs.md"

    res1 = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "FinOps Platform",
            "project_manifest_or_summary": "autoscaling stateless ALB, p99 TTFT throughput, Spanner processing_units Spot VMs Autoclass, MultiModelRouter prefix_cache gemini-embedding, Progressive Disclosure token_metrics.",
            "docs_file_path": str(faqs_file),
            "write_to_disk": True,
        },
    )
    assert res1.data["write_result"]["action"] == "created_new_faqs_file"
    assert PCO_FAQ_START in faqs_file.read_text(encoding="utf-8")

    faqs_file.write_text("# Frequently Asked Questions (FAQs)\n\n## Existing Rubric Section\nPreserved.\n", encoding="utf-8")
    res2 = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "FinOps Platform v2",
            "project_manifest_or_summary": "autoscaling stateless ALB, p99 TTFT throughput, Spanner processing_units Spot VMs Autoclass, MultiModelRouter prefix_cache gemini-embedding, Progressive Disclosure token_metrics.",
            "docs_file_path": str(faqs_file),
            "write_to_disk": True,
        },
    )
    assert res2.data["write_result"]["action"] == "appended_new_section_to_existing_file"
    content2 = faqs_file.read_text(encoding="utf-8")
    assert "## Existing Rubric Section" in content2
    assert "## Performance & Cost Optimization FAQs" in content2
    assert PCO_FAQ_END in content2


@pytest.mark.asyncio
async def test_all_50_skills_evaluated_independently_in_trajectories():
    """Evaluate all 50 registered skills independently in a 3-turn trajectory and persist the record."""
    mcp_app = create_server()
    list_tool = await mcp_app.get_tool("list_registered_skills")
    manifest_tool = await mcp_app.get_tool("get_skill_manifest")
    invoke_tool = await mcp_app.get_tool("invoke_skill")

    tier1 = (await list_tool.run({})).structured_content or {}
    catalog_ids = sorted(s["id"] for s in tier1.get("skills", []))
    assert len(catalog_ids) >= 50

    records: list[dict] = []
    for skill_id in catalog_ids:
        m_data = (await manifest_tool.run({"skill_id": skill_id})).structured_content or {}
        manifest_ok = m_data.get("status") == "success" and m_data.get("manifest", {}).get("id") == skill_id
        inv_data = (
            await invoke_tool.run({"skill_id": skill_id, "parameters": RUNBOOK_SKILL_PAYLOADS[skill_id]})
        ).structured_content or {}
        invoke_ok = inv_data.get("status") == "success" and inv_data.get("result") is not None

        passed = manifest_ok and invoke_ok
        records.append({
            "skill_id": skill_id,
            "turn_1_tier1_discovery": True,
            "turn_2_tier2_manifest": manifest_ok,
            "turn_3_invoke_skill": invoke_ok,
            "verdict": "PASS" if passed else "FAIL",
        })
        assert passed, f"Independent trajectory failed for {skill_id}"

    report_path = Path(__file__).resolve().parent.parent / "docs" / "validation" / "all_50_skills_trajectory_record.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "total_skills_evaluated": len(records),
                "total_passed": sum(1 for r in records if r["verdict"] == "PASS"),
                "pass_rate": 1.0,
                "skills": records,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

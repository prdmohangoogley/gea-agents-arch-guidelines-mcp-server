"""Unit tests and independent 53-skill trajectory evaluation for Operational Excellence skills."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from src.server import create_server
from src.skills.base import SkillExecutionContext
from src.skills.plugins.operational_excellence import (
    OE_FAQ_END,
    OE_FAQ_START,
    OperationalExcellenceAssessorFeedbackSkill,
    OperationalExcellenceFAQsSkill,
    OperationalExcellenceFeedbackResolverSkill,
)
from tests.test_all_38_skills_runbook import RUNBOOK_SKILL_PAYLOADS


@pytest.mark.asyncio
async def test_oe_assessor_detects_failures_on_manual_spec():
    """Verify manual/untested spec fails all 4 Operational Excellence domains with feedback."""
    skill = OperationalExcellenceAssessorFeedbackSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Manual App",
            "project_manifest_or_spec": "A manually uploaded script with no IaC, no versioning, and no tests.",
            "scope": "spec",
        },
    )
    assert res.status == "success"
    assessment = res.data["assessment"]
    assert assessment["overall_passed"] is False
    assert assessment["overall_status"] == "FAIL"
    assert len(assessment["feedback_items"]) == 8


@pytest.mark.asyncio
async def test_oe_resolver_iterates_until_pass():
    """Verify resolver orchestrates DevOps/Terraform/eval skills and re-assesses until all 4 domains pass."""
    skill = OperationalExcellenceFeedbackResolverSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Manual App",
            "project_manifest_or_spec": "ClickOps app without CI/CD, Terraform, or automated tests.",
            "scope": "project",
            "max_iterations": 3,
        },
    )
    assert res.status == "success"
    assert res.data["final_passed"] is True
    assert res.data["final_status"] == "PASS"
    assert res.data["iterations_executed"] >= 2
    assert "waf-pillar-operational-excellence" in res.data["library_skills_orchestrated"]
    assert "terraform-infra" in res.data["library_skills_orchestrated"]


@pytest.mark.asyncio
async def test_oe_faqs_initializes_new_and_appends_to_existing_faqs_md(tmp_path: Path):
    """Verify Operational Excellence FAQ skill creates docs/FAQs.md or appends preserving existing sections."""
    skill = OperationalExcellenceFAQsSkill()
    faqs_file = tmp_path / "docs" / "FAQs.md"

    res1 = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Ops Platform",
            "project_manifest_or_summary": "CI/CD Cloud Deploy dry-run rollback, Terraform iac backend.tf GCS tfvars uv.lock, MODEL_REGISTRY config.py OnlineEvaluator Cloud Trace, pytest e2e runbook trajectory parametrize.",
            "docs_file_path": str(faqs_file),
            "write_to_disk": True,
        },
    )
    assert res1.data["write_result"]["action"] == "created_new_faqs_file"
    assert OE_FAQ_START in faqs_file.read_text(encoding="utf-8")

    faqs_file.write_text("# Frequently Asked Questions (FAQs)\n\n## Existing Rubric Section\nPreserved.\n", encoding="utf-8")
    res2 = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Ops Platform v2",
            "project_manifest_or_summary": "CI/CD Cloud Deploy dry-run rollback, Terraform iac backend.tf GCS tfvars uv.lock, MODEL_REGISTRY config.py OnlineEvaluator Cloud Trace, pytest e2e runbook trajectory parametrize.",
            "docs_file_path": str(faqs_file),
            "write_to_disk": True,
        },
    )
    assert res2.data["write_result"]["action"] == "appended_new_section_to_existing_file"
    content2 = faqs_file.read_text(encoding="utf-8")
    assert "## Existing Rubric Section" in content2
    assert "## Operational Excellence FAQs" in content2
    assert OE_FAQ_END in content2


@pytest.mark.asyncio
async def test_all_53_skills_evaluated_independently_in_trajectories():
    """Evaluate all 53 registered skills independently in a 3-turn trajectory and persist the record."""
    mcp_app = create_server()
    list_tool = await mcp_app.get_tool("list_registered_skills")
    manifest_tool = await mcp_app.get_tool("get_skill_manifest")
    invoke_tool = await mcp_app.get_tool("invoke_skill")

    tier1 = (await list_tool.run({})).structured_content or {}
    catalog_ids = sorted(s["id"] for s in tier1.get("skills", []))
    assert len(catalog_ids) >= 53

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

    report_path = Path(__file__).resolve().parent.parent / "docs" / "validation" / "all_53_skills_trajectory_record.json"
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

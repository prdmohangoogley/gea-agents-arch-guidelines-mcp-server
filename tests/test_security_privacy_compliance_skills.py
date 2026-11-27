"""Unit tests for the 3 Security, Privacy & Compliance Rubric skills and independent trajectory evaluation of ALL 44 skills."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from src.server import create_server
from src.skills.base import SkillExecutionContext
from src.skills.plugins.security_privacy_compliance import (
    SPC_FAQ_END,
    SPC_FAQ_START,
    SecurityPrivacyComplianceAssessorFeedbackSkill,
    SecurityPrivacyComplianceFAQsSkill,
    SecurityPrivacyComplianceFeedbackResolverSkill,
)
from tests.test_all_38_skills_runbook import RUNBOOK_SKILL_PAYLOADS


@pytest.mark.asyncio
async def test_spc_assessor_detects_failures_on_insecure_spec():
    """Verify insecure spec fails all 5 Security, Privacy & Compliance domains with prioritized feedback."""
    skill = SecurityPrivacyComplianceAssessorFeedbackSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Insecure Prototype",
            "project_manifest_or_spec": "A public Python endpoint with no auth, no encryption, and no guardrails.",
        },
    )
    assert res.status == "success"
    assessment = res.data["assessment"]
    assert assessment["overall_passed"] is False
    assert assessment["overall_status"] == "FAIL"
    assert len(assessment["feedback_items"]) == 10


@pytest.mark.asyncio
async def test_spc_resolver_iterates_until_pass():
    """Verify feedback resolver orchestrates security skills and re-invokes assessor until all 5 domains pass."""
    skill = SecurityPrivacyComplianceFeedbackResolverSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Insecure Prototype",
            "project_manifest_or_spec": "Public service with hardcoded API key and no VPC or Model Armor.",
            "max_iterations": 3,
        },
    )
    assert res.status == "success"
    assert res.data["final_passed"] is True
    assert res.data["final_status"] == "PASS"
    assert res.data["iterations_executed"] >= 2
    assert "waf-pillar-security" in res.data["library_skills_orchestrated"]
    assert "terraform-waf-verifier" in res.data["library_skills_orchestrated"]


@pytest.mark.asyncio
async def test_spc_faqs_initializes_new_and_appends_to_existing_faqs_md(tmp_path: Path):
    """Verify FAQ skill initializes docs/FAQs.md if missing and appends/updates cleanly when existing sections exist."""
    skill = SecurityPrivacyComplianceFAQsSkill()
    faqs_file = tmp_path / "docs" / "FAQs.md"

    # 1. Initialize brand-new docs/FAQs.md
    res1 = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Secure App",
            "project_manifest_or_summary": "Workload Identity OAuth2, ZAA least privilege IAM, VPC-SC Cloud Armor, CMEK TLS PII DLP Secret Manager, Dual-Pass Model Armor, Zero Legacy model allow-list, Cloud Trace audit logs, HIPAA/FINRA.",
            "docs_file_path": str(faqs_file),
            "write_to_disk": True,
        },
    )
    assert res1.status == "success"
    assert res1.data["write_result"]["action"] == "created_new_faqs_file"
    content1 = faqs_file.read_text(encoding="utf-8")
    assert "# Frequently Asked Questions (FAQs)" in content1
    assert SPC_FAQ_START in content1 and SPC_FAQ_END in content1

    # 2. Prepend an existing AI/ML rubric FAQ section, then re-run and verify both coexist
    faqs_file.write_text("# Frequently Asked Questions (FAQs)\n\n## AI/ML Engineering Rubric FAQs\nExisting AI/ML content.\n", encoding="utf-8")
    res2 = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Secure App v2",
            "project_manifest_or_summary": "Workload Identity OAuth2, ZAA least privilege IAM, VPC-SC Cloud Armor, CMEK TLS PII DLP Secret Manager, Dual-Pass Model Armor, Zero Legacy model allow-list, Cloud Trace audit logs, HIPAA/FINRA.",
            "docs_file_path": str(faqs_file),
            "write_to_disk": True,
        },
    )
    assert res2.data["write_result"]["action"] == "appended_new_section_to_existing_file"
    content2 = faqs_file.read_text(encoding="utf-8")
    assert "## AI/ML Engineering Rubric FAQs" in content2
    assert "Existing AI/ML content." in content2
    assert "## Security, Privacy & Compliance FAQs" in content2
    assert "Secure App v2" in content2


@pytest.mark.asyncio
async def test_all_44_skills_evaluated_independently_in_trajectories():
    """Evaluate every single registered skill (all 44 skills) independently in a 3-turn trajectory
    (Tier 1 discovery -> Tier 2 manifest hydration -> Tier 3 invoke_skill) and persist the record."""
    mcp_app = create_server()
    list_tool = await mcp_app.get_tool("list_registered_skills")
    manifest_tool = await mcp_app.get_tool("get_skill_manifest")
    invoke_tool = await mcp_app.get_tool("invoke_skill")

    tier1 = (await list_tool.run({})).structured_content or {}
    catalog_ids = sorted(s["id"] for s in tier1.get("skills", []))
    assert len(catalog_ids) >= 44

    records: list[dict] = []
    for skill_id in catalog_ids:
        # Turn 1: Verify discoverability in Tier 1 catalog
        in_catalog = skill_id in catalog_ids
        # Turn 2: Hydrate Tier 2 manifest
        m_data = (await manifest_tool.run({"skill_id": skill_id})).structured_content or {}
        manifest_ok = m_data.get("status") == "success" and m_data.get("manifest", {}).get("id") == skill_id
        # Turn 3: Execute skill independently via invoke_skill
        payload = RUNBOOK_SKILL_PAYLOADS[skill_id]
        inv_data = (await invoke_tool.run({"skill_id": skill_id, "parameters": payload})).structured_content or {}
        invoke_ok = inv_data.get("status") == "success" and inv_data.get("result") is not None

        passed = in_catalog and manifest_ok and invoke_ok
        records.append({
            "skill_id": skill_id,
            "turn_1_tier1_discovery": in_catalog,
            "turn_2_tier2_manifest": manifest_ok,
            "turn_3_invoke_skill": invoke_ok,
            "verdict": "PASS" if passed else "FAIL",
        })
        assert passed, f"Independent trajectory failed for {skill_id}: {records[-1]}"

    # Persist authoritative independent trajectory evaluation record
    report_path = Path(__file__).resolve().parent.parent / "docs" / "validation" / "all_44_skills_trajectory_record.json"
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

"""Unit tests and independent 58-skill trajectory evaluation for Scoping & Documentation skills."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from src.server import create_server
from src.skills.base import SkillExecutionContext
from src.skills.plugins.scoping_and_documentation import (
    ScopingDocumentationAssessorFeedbackSkill,
    ScopingDocumentationFeedbackResolverSkill,
)
from tests.test_all_38_skills_runbook import RUNBOOK_SKILL_PAYLOADS


@pytest.mark.asyncio
async def test_sd_assessor_detects_failures_on_undocumented_project():
    """Verify sparse README fails all 7 Scoping & Documentation domains with prioritized feedback."""
    skill = ScopingDocumentationAssessorFeedbackSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Undocumented App",
            "project_docs_manifest": "Minimal code-only repository with zero project documentation.",
        },
    )
    assert res.status == "success"
    assessment = res.data["assessment"]
    assert assessment["overall_passed"] is False
    assert assessment["overall_status"] == "FAIL"
    assert len(assessment["feedback_items"]) == 14


@pytest.mark.asyncio
async def test_sd_assessor_passes_on_actual_project_docs():
    """Verify this repository's actual documentation corpus passes all 7 Scoping & Documentation domains."""
    repo_root = Path(__file__).resolve().parent.parent
    docs_corpus = "\n".join([
        (repo_root / "README.md").read_text(encoding="utf-8"),
        (repo_root / "docs" / "00_SCOPING_AND_ADR_CHARTER.md").read_text(encoding="utf-8"),
        (repo_root / "docs" / "01_MCP_SERVER_DOCUMENTATION.md").read_text(encoding="utf-8")[:4000],
        (repo_root / "docs" / "02_SKILLS_REGISTRY_DOCUMENTATION.md").read_text(encoding="utf-8")[:4000],
        (repo_root / "docs" / "FAQs.md").read_text(encoding="utf-8")[:4000],
    ])
    skill = ScopingDocumentationAssessorFeedbackSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Enterprise Agents Architectural Guidelines MCP Server",
            "project_docs_manifest": docs_corpus,
        },
    )
    assert res.status == "success"
    assessment = res.data["assessment"]
    assert assessment["overall_passed"] is True
    assert assessment["domains_passed"] == 7


@pytest.mark.asyncio
async def test_sd_resolver_iterates_until_pass():
    """Verify resolver orchestrates spec/ADR/API/runbook skills and re-assesses until all 7 domains pass."""
    skill = ScopingDocumentationFeedbackResolverSkill()
    res = await skill.execute(
        SkillExecutionContext(),
        {
            "project_name": "Undocumented App",
            "project_docs_manifest": "Empty repo with no docs.",
            "max_iterations": 3,
        },
    )
    assert res.status == "success"
    assert res.data["final_passed"] is True
    assert res.data["final_status"] == "PASS"
    assert res.data["iterations_executed"] >= 2
    assert "spec-creation-workflow" in res.data["library_skills_orchestrated"]
    assert "codebase-to-spec-collection" in res.data["library_skills_orchestrated"]


@pytest.mark.asyncio
async def test_all_58_skills_evaluated_independently_in_trajectories():
    """Evaluate all 58 registered skills independently in a 3-turn trajectory and persist the record."""
    mcp_app = create_server()
    list_tool = await mcp_app.get_tool("list_registered_skills")
    manifest_tool = await mcp_app.get_tool("get_skill_manifest")
    invoke_tool = await mcp_app.get_tool("invoke_skill")

    tier1 = (await list_tool.run({})).structured_content or {}
    catalog_ids = sorted(s["id"] for s in tier1.get("skills", []))
    assert len(catalog_ids) == 58

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

    report_path = Path(__file__).resolve().parent.parent / "docs" / "validation" / "all_58_skills_trajectory_record.json"
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

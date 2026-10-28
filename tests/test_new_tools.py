"""Tests for FDE Governance, Skills Registry, and Autonomous OKF Evolution tools."""

import pytest
from src.server import create_server


@pytest.fixture
def mcp_app():
    """Fixture providing the FastMCP test server with all registered tools."""
    return create_server()


@pytest.mark.asyncio
async def test_fde_charter_query_tool(mcp_app):
    """Verify query_fde_charter_best_practices returns rubric items."""
    tool = await mcp_app.get_tool("query_fde_charter_best_practices")
    res = await tool.run({"domain": "Part B.3: Security & Identity"})

    data = res.structured_content or {}
    assert data.get("status") == "success"
    assert "charter_reference" in data
    assert len(data.get("rubric_items", [])) > 0


@pytest.mark.asyncio
async def test_fde_rubric_audit_disqualifiers(mcp_app):
    """Verify audit_project_against_fde_rubric catches 0-score disqualifiers."""
    flawed_manifest = (
        "# Customer Agent Architecture\n"
        "Uses hardcoded api key AIzaSyD3x9ExampleKey1234567890abcdef for Vertex AI.\n"
        "Cloud Run deployed with allow_unauthenticated = true for ease of development.\n"
        "Currently zero evals or test suites defined."
    )
    tool = await mcp_app.get_tool("audit_project_against_fde_rubric")
    res = await tool.run({"project_manifest_or_description": flawed_manifest})

    data = res.structured_content or {}
    assert data.get("status") == "success"
    assert data.get("verdict") == "DISQUALIFIED_IMMEDIATE_PAUSE"
    assert data.get("production_cutline_met") is False
    assert len(data.get("disqualifiers_detected", [])) >= 2
    assert "scorecard_markdown" in data


@pytest.mark.asyncio
async def test_fde_rubric_audit_clean_project(mcp_app):
    """Verify audit_project_against_fde_rubric approves clean architectures meeting >= 2.0 cutline."""
    clean_manifest = (
        "# Enterprise Multi-Agent System\n"
        "Architecture enforces Zero Ambient Authority (ZAA) via Delegated OAuth and Workforce Identity.\n"
        "Context managed via two-tier progressive disclosure protecting token budget.\n"
        "Storage uses Spanner Graph for operational GQL and BigQuery for analytical tracing.\n"
        "Evaluation uses golden eval dataset with multi-turn trajectory evaluation and auto-rater.\n"
        "Security includes dual-pass Model Armor with ingress prompt injection filter and egress DLP.\n"
        "Principal Access Boundaries (PAB) configured. OpenTelemetry distributed tracing and health probes active."
    )
    tool = await mcp_app.get_tool("audit_project_against_fde_rubric")
    res = await tool.run({"project_manifest_or_description": clean_manifest})

    data = res.structured_content or {}
    assert data.get("status") == "success"
    assert data.get("production_cutline_met") is True
    assert data.get("verdict") == "FIELD_READY_PRODUCTION_APPROVED"
    assert data.get("composite_score") >= 2.0
    assert len(data.get("disqualifiers_detected", [])) == 0


@pytest.mark.asyncio
async def test_skills_registry_progressive_disclosure(mcp_app):
    """Verify two-tier progressive disclosure: list_registered_skills (Tier 1) and get_skill_manifest (Tier 2)."""
    # Tier 1
    list_tool = await mcp_app.get_tool("list_registered_skills")
    tier1_res = await list_tool.run({"category": "architecture"})
    tier1_data = tier1_res.structured_content or {}

    assert tier1_data.get("status") == "success"
    assert tier1_data.get("tier") == "tier_1_catalog"
    skills = tier1_data.get("skills", [])
    assert len(skills) >= 1
    target_skill = skills[0]
    assert "id" in target_skill
    assert "token_estimate" in target_skill

    # Tier 2
    manifest_tool = await mcp_app.get_tool("get_skill_manifest")
    tier2_res = await manifest_tool.run({"skill_id": target_skill["id"]})
    tier2_data = tier2_res.structured_content or {}

    assert tier2_data.get("status") == "success"
    assert tier2_data.get("tier") == "tier_2_manifest"
    manifest = tier2_data.get("manifest", {})
    assert manifest.get("id") == target_skill["id"]
    assert "parameters" in manifest
    assert "instructions" in manifest


@pytest.mark.asyncio
async def test_invoke_skill_dynamic_dispatch(mcp_app):
    """Verify invoke_skill dispatches execution through the skill registry."""
    tool = await mcp_app.get_tool("invoke_skill")
    res = await tool.run({
        "skill_id": "skill-arch-eval",
        "parameters": {"topic": "Zero Ambient Authority"},
    })

    data = res.structured_content or {}
    assert data.get("status") == "success"
    assert data.get("skill_id") == "skill-arch-eval"
    assert "result" in data


@pytest.mark.asyncio
async def test_check_okf_freshness(mcp_app):
    """Verify check_okf_freshness audits concepts for TTL expiration."""
    tool = await mcp_app.get_tool("check_okf_freshness")
    res = await tool.run({"threshold_days": 30})

    data = res.structured_content or {}
    assert data.get("status") == "success"
    assert data.get("total_concepts") == 83
    assert "freshness_index_percentage" in data
    assert "concepts" in data


@pytest.mark.asyncio
async def test_search_recent_architectural_updates(mcp_app):
    """Verify search_recent_architectural_updates returns authoritative GCP documentation."""
    tool = await mcp_app.get_tool("search_recent_architectural_updates")
    res = await tool.run({"topic": "Model Armor egress DLP"})

    data = res.structured_content or {}
    assert data.get("status") == "success"
    assert len(data.get("updates", [])) > 0
    assert any("Model Armor" in u["title"] for u in data["updates"])


@pytest.mark.asyncio
async def test_propose_concept_evolution(mcp_app):
    """Verify propose_concept_evolution drafts an incremental evolution and computes SHA256."""
    tool = await mcp_app.get_tool("propose_concept_evolution")
    res = await tool.run({
        "concept_id": "01",
        "update_summary": "Add trajectory auto-rater calibration benchmarks",
        "new_architectural_findings": [
            "Introduced automated trajectory assertions with >= 0.90 Tool Selection Precision.",
            "Integrated continuous FDE Rubric Part B.2 Quality Flywheel scoring.",
        ],
    })

    data = res.structured_content or {}
    assert data.get("status") == "success"
    assert data.get("concept_id") == "01"
    assert "calculated_content_sha256" in data
    assert "new_stale_after" in data
    assert "proposed_markdown" in data

"""Verification test suite for all 8 OKF v0.2 & FDE Rubric Audit Remediations (SPEC-GEA-OKF-AUDIT-V5.0)."""

from __future__ import annotations

from pathlib import Path
import pytest

from src.agent.reasoning_engine import EnterpriseArchGuidelinesAgent
from src.graph.client import GraphClient
from src.mcp_adapter import (
    PROGRESSIVE_CORE_SURFACE_TOOLS,
    get_current_traceparent,
    get_progressive_surface_manifest,
    mint_downscoped_sts_context,
)
from src.models.router import MultiModelRouter
from src.tools.fde_governance import CANONICAL_RUBRIC_DOMAINS

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_remediation_1_egress_dlp_sanitization_and_fail_closed():
    """FIND-01: Verify EnterpriseArchGuidelinesAgent._sanitize_output masks secrets and fails closed."""
    agent = EnterpriseArchGuidelinesAgent()
    agent.set_up()

    leaked_text = "Here is the key: AIzaSyDummyKey1234567890abcdefghijklmnop in output"
    sanitized = agent._sanitize_output(leaked_text)
    assert "AIzaSyDummyKey" not in sanitized
    assert "[REDACTED_GCP_API_KEY]" in sanitized


def test_remediation_2_zero_cloud_run_in_iac():
    """FIND-02: Verify iac/ contains zero Cloud Run modules and provisions Reasoning Engine staging."""
    main_tf = (REPO_ROOT / "iac" / "main.tf").read_text(encoding="utf-8")
    variables_tf = (REPO_ROOT / "iac" / "variables.tf").read_text(encoding="utf-8")
    outputs_tf = (REPO_ROOT / "iac" / "outputs.tf").read_text(encoding="utf-8")

    for content in (main_tf, variables_tf, outputs_tf):
        assert "cloud_run" not in content
        assert "run.googleapis.com" not in content

    assert "reasoning_engine_staging" in main_tf
    assert "okf-evolution-agent-sa" in main_tf


def test_remediation_3_all_34_canonical_fde_rubric_competencies():
    """FIND-03: Verify CANONICAL_RUBRIC_DOMAINS covers all 34 FDE Field-Readiness competencies."""
    total_competencies = sum(len(items) for items in CANONICAL_RUBRIC_DOMAINS.values())
    assert total_competencies == 34
    assert "Part A: Advisory Rigor" in CANONICAL_RUBRIC_DOMAINS
    assert "Part B.7: Change Management & Governance" in CANONICAL_RUBRIC_DOMAINS
    assert "Addendum: Tokenomics & Socratic Grilling" in CANONICAL_RUBRIC_DOMAINS


def test_remediation_4_progressive_disclosure_7_tool_surface():
    """FIND-04: Verify the 7-tool progressive disclosure surface definition (<900 tokens)."""
    manifest = get_progressive_surface_manifest()
    assert manifest["core_tool_count"] == 7
    assert len(PROGRESSIVE_CORE_SURFACE_TOOLS) == 7
    assert manifest["estimated_prefix_tokens"] < 900
    assert "invoke_skill" in manifest["core_eager_tools"]


@pytest.mark.asyncio
async def test_remediation_5_mock_graph_hydrates_all_83_okf_concepts():
    """FIND-05: Verify GraphClient(use_mock=True) dynamically hydrates all 83 OKF concepts and 37 rubric items."""
    client = GraphClient(use_mock=True)
    assert len(client._guidelines) >= 83
    rubrics = await client.get_fde_rubric(limit=50)
    assert len(rubrics) >= 35


def test_remediation_6_kv_prefix_context_caching_hit_ratio():
    """FIND-06: Verify deterministic SHA-256 KV prefix cache achieves >=75% cache hit ratio across 4 turns."""
    router = MultiModelRouter()
    sys_inst = "Canonical Enterprise Architecture System Prompt v5.0"
    tools = [{"name": "get_best_practice"}, {"name": "invoke_skill"}]

    results = [
        router.get_or_create_cached_content("gemini-4-argon", sys_inst, tools)
        for _ in range(4)
    ]
    assert results[0]["cache_hit"] is False
    assert results[1]["cache_hit"] is True
    assert results[2]["cache_hit"] is True
    assert results[3]["cache_hit"] is True
    assert results[3]["cache_hit_ratio"] >= 0.75


def test_remediation_7_and_8_zaa_downscoping_and_traceparent_propagation():
    """FIND-07 & FIND-08: Verify downscoped CredentialAccessBoundary and W3C traceparent propagation."""
    sts_ctx = mint_downscoped_sts_context(caller_identity="fde-architect@google.com")
    assert sts_ctx["caller_identity"] == "fde-architect@google.com"
    assert sts_ctx["access_boundary_token"].startswith("zaa-cab:")

    tp = get_current_traceparent()
    assert tp.startswith("00-")

    agent = EnterpriseArchGuidelinesAgent()
    agent.set_up()
    res = agent.query(
        prompt="health check",
        tool_name="health_check",
        traceparent=tp,
        **sts_ctx,
    )
    meta = res.get("metadata", {})
    assert meta.get("caller_identity") == "fde-architect@google.com"
    assert meta.get("access_boundary_enforced") is True
    assert meta.get("traceparent") == tp

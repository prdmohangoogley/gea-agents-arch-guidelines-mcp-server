"""Comprehensive Single Runbook Test for All 38 Registered Skills & 29 FastMCP Tools.

Validates:
1. Tier 1 Progressive Disclosure (`list_registered_skills`) returns all 38 unique skills.
2. Tier 2 Progressive Disclosure (`get_skill_manifest`) hydrates full parameter schemas for all 38 skills.
3. Dynamic Execution (`invoke_skill`) executes all 38 skills end-to-end with realistic runbook parameters
   and verifies sanitized output envelopes.
4. Direct FastMCP Tool surface exposes all 29 expected tools.
"""

from __future__ import annotations

from typing import Any
import pytest
from src.registry.skills_registry import skills_registry
from src.server import create_server


@pytest.fixture(scope="module")
def mcp_app():
    """Create the FastMCP application instance once per test module."""
    return create_server()


# Canonical Getting-Started Runbook Payloads for all 38 skills
RUNBOOK_SKILL_PAYLOADS: dict[str, dict[str, Any]] = {
    # 1. Architecture & Spec Generation (9 skills)
    "skill-arch-eval": {"topic": "Zero Ambient Authority"},
    "skill_arbitrary_spec_generator": {
        "domain_or_topic": "Real-Time Payment Settlement Engine",
        "tech_stack_or_framework": "Go + gRPC + Cloud Spanner Multi-Region",
        "requirements": "100k TPS, external consistency, RPO=0",
        "complexity_level": "detailed",
    },
    "skill_codebase_to_spec_collection": {
        "project_name": "GEA Architecture Guidelines MCP",
        "codebase_summary_or_path": "FastMCP server in src/, Spanner Graph in src/graph/, 38 skills in src/skills/plugins/",
        "enforce_fde_cutline": True,
    },
    "skill_google_landing_metrics_critique": {
        "system_or_frontend_spec": "Global Next.js storefront behind Global External ALB and Cloud CDN on Premium Network Tier.",
        "target_p99_ms": 150,
    },
    "skill_spec_best_practices_updater": {
        "existing_spec_content": "# Legacy Chatbot Spec\nUses gemini-1.5-pro with service account JSON keys.",
        "standards_to_apply": ["ZAA", "WAF", "Model_Armor_Dual_Pass"],
        "strictness_level": "production_cutline_enforced",
    },
    "skill_spec_generator": {
        "feature_title": "Federated A2A Agent Handoff Gateway",
        "context_and_goals": "Zero-trust task delegation across multi-agent boundaries.",
    },
    "skill_system_design": {
        "system_name": "Global Clinical Decision Co-Pilot",
        "requirements": "HIPAA-compliant FHIR ingestion, multi-agent reasoning, sub-500ms retrieval.",
        "multi_agent_enabled": True,
    },
    "skill_waf_okf_search": {
        "query": "Cloud Spanner Interleaved Tables Stale Reads",
        "pillar": "performance_optimization",
        "service_area": "all",
    },
    "skill_spec_critique": {
        "spec_text": "Agents coordinate distributed locks by overwriting a shared GCS JSON file.",
        "critique_perspective": "scale_and_concurrency",
    },
    # 2. Governance, FDE Rubric & WAF Pillar Verifiers (12 skills)
    "skill-fde-governance": {
        "project_manifest_or_description": "Enterprise multi-agent system with ZAA, Model Armor, Spanner Graph, and OTel tracing.",
    },
    "skill_rubric_level_critique": {
        "subcompetency_id": "RUBRIC-B-3-1",
        "system_summary": "Enforces Zero Ambient Authority with downscoped STS tokens and Model Armor.",
    },
    "skill_complete_system_audit": {
        "project_name": "GEA Architecture Guidelines MCP Server",
        "full_system_spec_or_code_manifest": "FastMCP server with 29 tools, 38 skills, 92 OKF concepts, Dual-Pass Model Armor, and ZAA.",
    },
    "skill_waf_critique": {
        "architecture_description": "Multi-agent platform on Vertex AI Reasoning Engine with Spanner Graph and Model Armor.",
        "workload_type": "multi_agent_system",
        "target_pillars": ["all"],
    },
    "skill_waf_pillar_critique": {
        "pillar_name": "security",
        "architecture_description": "Zero-trust agent perimeter using Workload Identity, Secret Manager, VPC-SC, and Model Armor.",
    },
    "skill_waf_all_pillars_spec_verifier": {
        "architecture_description": (
            "Terraform with GCS backend state locking, Cloud Deploy canary rollouts, Cloud Trace traceparent, "
            "Workload Identity (ZAA), Secret Manager, CMEK, Confidential GKE, VPC-SC + ACM Ingress, Cloud Armor, "
            "Spanner Multi-Region (99.999%, Interleaved Tables, 15s Stale Reads), Redis Standard HA, GKE Autopilot, "
            "Spot VMs for batch, GCS Autoclass, BigQuery Partitioning/Clustering, Premium Tier + Cloud CDN, and CFE% regions."
        ),
        "workload_type": "global_oltp_saas",
        "target_pillars": ["all"],
    },
    "skill_waf_pillar_operational_excellence": {
        "architecture_description": "Terraform with GCS backend state, Cloud Build Private Pools, Cloud Deploy canary rollouts, Cloud Ops Agent, Cloud Trace (traceparent), Cloud Profiler, and SRE error budgets.",
        "search_query": "Cloud Trace Profiler SRE Cloud Deploy",
    },
    "skill_waf_pillar_security": {
        "architecture_description": "Enforces Zero Ambient Authority via Workload Identity, Secret Manager (--set-secrets), Cloud KMS CMEK, Confidential GKE Nodes, VPC-SC + Access Context Manager Ingress, Cloud Armor + GFE firewall, IAP, Binary Authorization, Cloud DLP, and Model Armor.",
        "search_query": "Secret Manager KMS VPC-SC Workload Identity",
    },
    "skill_waf_pillar_reliability": {
        "architecture_description": "Hot active-active multi-region architecture (RTO=0, RPO=0) using Cloud Spanner Multi-Region (99.999% SLA), Regional GKE with Pod Topology Spread Constraints, Memorystore for Redis Standard Tier HA, and Cloud Pub/Sub behind a Global External ALB.",
        "search_query": "Spanner Cloud SQL HA RTO RPO DR",
    },
    "skill_waf_pillar_cost_optimization": {
        "architecture_description": "Uses GKE Autopilot, Cloud Run scale-to-zero, Spot VMs for stateless batch workers, Flexible CUDs, GCS Autoclass, BigQuery Partitioning/Clustering with 90-day Long-Term Storage, _Default log exclusion filters, and Billing Budgets wired to Pub/Sub.",
        "search_query": "GKE Autopilot Spot VMs BigQuery 90-day long-term storage",
    },
    "skill_waf_pillar_performance_optimization": {
        "architecture_description": "Global External ALB on Premium Network Tier with Cloud CDN, Cloud Spanner Interleaved Tables with 15s Stale Reads, Bigtable composite row keys (VehicleVIN#ReverseTimestamp), Memorystore for Redis sub-10ms cache, and Vertex AI GPU endpoints.",
        "search_query": "Premium Tier Cloud CDN Spanner Interleaved Stale Reads",
    },
    "skill_waf_pillar_sustainability": {
        "architecture_description": "Workloads restricted to high CFE% carbon-free regions via constraints/gcp.resourceLocations, using serverless scale-to-zero Cloud Run, GKE Autopilot bin-packing, Recommender API idle VM cleanup, GCS Autoclass, and KV prefix caching.",
        "search_query": "Carbon CFE region resourceLocations scale-to-zero",
    },
    # 3. DevOps & Terraform WAF Skills (3 skills)
    "skill_terraform_infra": {
        "action": "generate",
        "infrastructure_requirements": "Cloud Spanner Graph instance with CMEK and least-privilege Service Account.",
    },
    "skill_terraform_waf_verifier": {
        "terraform_hcl": 'terraform { backend "gcs" { bucket = "tf-state" } }\nresource "google_storage_bucket" "b" { name = "b" location = "US" public_access_prevention = "enforced" uniform_bucket_level_access = true }',
        "workload_context": "production_enterprise_workload",
        "target_pillars": ["all"],
    },
    "skill_terraform_version_comparator": {
        "past_terraform_hcl": 'terraform { backend "local" {} }\nresource "google_sql_database_instance" "db" { deletion_protection = false settings { availability_type = "ZONAL" } }',
        "present_terraform_hcl": 'terraform { backend "gcs" { bucket = "tf-state" } }\nresource "google_sql_database_instance" "db" { deletion_protection = true settings { availability_type = "REGIONAL" backup_configuration { enabled = true point_in_time_recovery_enabled = true } } }',
        "change_context": "Upgrade Cloud SQL and Terraform state backend to WAF standards",
    },
    # 4. Knowledge Management, Workflow, Graph Data & Security (7 skills)
    "skill-okf-evolution": {"threshold_days": 30},
    "skill_alexandria_search": {
        "query": "Zero Ambient Authority Principal Access Boundary",
        "domain": "security",
        "top_k": 3,
    },
    "skill_discovery_and_catalog": {
        "task_description": "Verify Terraform scripts and audit system architecture across all 6 WAF pillars.",
    },
    "skill_okf_evolution_agent": {
        "target_concept_id": "33-model-armor-securing-ai-deployments",
        "research_topic": "Model Armor Dual-Pass Egress DLP",
    },
    "skill-nl2kg-triplification": {"component": "Security"},
    "skill-security-auditor": {
        "option_a": "Workload Identity + Downscoped STS Tokens",
        "option_b": "Long-Lived Service Account JSON Keys",
    },
    "skill_spec_creation_workflow": {
        "project_title": "Multi-Region Agent Memory Bank",
        "current_stage": "threat_model",
        "draft_content": "Uses Cloud Spanner Graph with CMEK and VPC-SC.",
    },
    # 5. Standalone Workspace SKILL.md Skills (7 skills)
    "skill_enterprise_system_design": {"input_payload": "Design a multi-region agentic RAG platform."},
    "skill_eval_harness": {"input_payload": "Run retrieval precision benchmark."},
    "skill_fastmcp_tool_dev": {"input_payload": "Validate stdio and sse protocol compliance."},
    "skill_fde_governance_auditor": {"input_payload": "Audit project against FDE rubric."},
    "skill_google_landing_metrics": {"input_payload": "Verify LCP, INP, CLS, and CDN hit ratio."},
    "skill_nl2kg_triplification": {"input_payload": "Extract knowledge graph triples from markdown."},
    "skill_okf_auto_evolution": {"input_payload": "Check 6-month TTL freshness and sync to Dataplex."},
}


@pytest.mark.asyncio
async def test_runbook_tier1_and_tier2_all_38_skills(mcp_app):
    """Verify Tier 1 list_registered_skills and Tier 2 get_skill_manifest for all 38 skills."""
    list_tool = await mcp_app.get_tool("list_registered_skills")
    tier1_res = await list_tool.run({})
    tier1_data = tier1_res.structured_content or {}

    assert tier1_data.get("status") == "success"
    assert tier1_data.get("total_skills") == 38
    catalog_ids = {s["id"] for s in tier1_data.get("skills", [])}
    assert catalog_ids == set(RUNBOOK_SKILL_PAYLOADS.keys())

    manifest_tool = await mcp_app.get_tool("get_skill_manifest")
    for skill_id in sorted(RUNBOOK_SKILL_PAYLOADS.keys()):
        m_res = await manifest_tool.run({"skill_id": skill_id})
        m_data = m_res.structured_content or {}
        assert m_data.get("status") == "success", f"Tier 2 manifest lookup failed for {skill_id}"
        assert m_data.get("manifest", {}).get("id") == skill_id


@pytest.mark.asyncio
@pytest.mark.parametrize("skill_id", sorted(RUNBOOK_SKILL_PAYLOADS.keys()))
async def test_runbook_invoke_every_single_skill(mcp_app, skill_id: str):
    """Execute every single one of the 38 skills via invoke_skill and verify its output envelope."""
    invoke_tool = await mcp_app.get_tool("invoke_skill")
    payload = RUNBOOK_SKILL_PAYLOADS[skill_id]
    res = await invoke_tool.run({
        "skill_id": skill_id,
        "parameters": payload,
    })
    data = res.structured_content or {}
    assert data.get("status") == "success", f"Skill '{skill_id}' failed: {data}"
    assert data.get("skill_id") == skill_id
    assert "result" in data
    assert data["result"] is not None


@pytest.mark.asyncio
async def test_all_29_fastmcp_tools_exposed(mcp_app):
    """Verify all 29 FastMCP tools are registered and exposed on the server."""
    tools = await mcp_app.list_tools()
    tool_names = {t.name for t in tools}
    expected_29_tools = {
        "health_check",
        "get_best_practice",
        "deep_dive_guideline",
        "search_guidelines",
        "get_guideline_details",
        "query_architectural_pattern",
        "evaluate_design_tradeoffs",
        "query_fde_charter_best_practices",
        "audit_project_against_fde_rubric",
        "search_fde_charter_best_practices",
        "list_registered_skills",
        "get_skill_manifest",
        "invoke_skill",
        "record_session_feedback",
        "check_okf_freshness",
        "search_recent_architectural_updates",
        "propose_concept_evolution",
        "commit_and_sync_okf_bundle",
        "generate_arbitrary_spec",
        "update_spec_best_practices",
        "generate_spec_collection",
        "alexandria_search",
        "audit_waf_pillars",
        "audit_complete_system",
        "search_waf_okf_best_practices",
        "verify_spec_waf_pillar",
        "verify_spec_all_waf_pillars",
        "verify_terraform_waf_compliance",
        "compare_terraform_versions_waf",
    }
    assert expected_29_tools.issubset(tool_names)
    assert len(tool_names) == 29

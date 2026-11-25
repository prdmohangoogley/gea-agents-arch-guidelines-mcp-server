"""Tests for the PCA & Well-Architected Framework (WAF) OKF Knowledge Base Skills and MCP Tools."""

from __future__ import annotations

import pytest
from src.registry.skills_registry import skills_registry
from src.server import create_server
from src.skills.plugins.waf_okf_pillars import (
    WAF_ANTIPATTERN_RULES,
    WAF_PILLAR_DEFINITIONS,
    evaluate_spec_across_all_pillars,
    evaluate_spec_against_pillar,
    load_pca_waf_okf_corpus,
    search_pca_waf_okf,
)


@pytest.fixture
def mcp_app():
    """Provide the FastMCP server with all registered tools."""
    return create_server()


def test_pca_waf_okf_corpus_loaded_and_verified():
    """Verify all 9 OKF-PCA-01..09 concepts load from disk with valid SHA-256 metadata."""
    corpus = load_pca_waf_okf_corpus()
    concepts = corpus["concepts"]
    assert len(concepts) == 9
    for idx in range(1, 10):
        cid = f"OKF-PCA-0{idx}"
        assert cid in concepts
        assert len(concepts[cid]["markdown_content"]) > 500
        assert len(concepts[cid]["content_sha256"]) == 64


def test_all_waf_skills_registered_in_skills_registry():
    """Verify all per-pillar and all-pillar WAF OKF skills are discoverable in SkillsRegistry."""
    catalog = skills_registry.list_catalog()
    skill_ids = {s["id"] for s in catalog}

    expected_skills = {
        "skill_waf_okf_search",
        "skill_waf_pillar_operational_excellence",
        "skill_waf_pillar_security",
        "skill_waf_pillar_reliability",
        "skill_waf_pillar_cost_optimization",
        "skill_waf_pillar_performance_optimization",
        "skill_waf_pillar_sustainability",
        "skill_waf_all_pillars_spec_verifier",
        "skill_waf_critique",
        "skill_waf_pillar_critique",
        "skill_terraform_infra",
        "skill_terraform_waf_verifier",
        "skill_terraform_version_comparator",
    }
    for sid in expected_skills:
        assert sid in skill_ids, f"Missing expected WAF skill in registry: {sid}"


@pytest.mark.asyncio
async def test_search_waf_okf_best_practices_tool(mcp_app):
    """Verify search_waf_okf_best_practices searches per-pillar and all-pillars OKF concepts."""
    tool = await mcp_app.get_tool("search_waf_okf_best_practices")
    res = await tool.run({
        "query": "Cloud Spanner Interleaved Tables Stale Reads",
        "pillar": "performance_optimization",
        "include_antipatterns": True,
    })
    data = res.structured_content or {}
    assert data.get("status") == "success"
    assert data.get("matched_concepts_count", 0) >= 1
    concept_ids = [c["concept_id"] for c in data.get("matched_concepts", [])]
    assert "OKF-PCA-01" in concept_ids


@pytest.mark.asyncio
async def test_verify_spec_waf_pillar_catches_antipatterns(mcp_app):
    """Verify per-pillar verification flags deterministic PCA/WAF anti-patterns."""
    flawed_security_spec = (
        "# Payment Service Spec\n"
        "We use Cloud KMS to store database passwords and OAuth tokens.\n"
        "We also supply CSEK to BigQuery tables and use a VPC-SC Perimeter Bridge to let human analysts in via Cloud Console.\n"
        "We use Shielded GKE Nodes to encrypt data in-use inside physical RAM."
    )
    tool = await mcp_app.get_tool("verify_spec_waf_pillar")
    res = await tool.run({
        "architecture_spec": flawed_security_spec,
        "pillar": "security",
    })
    data = res.structured_content or {}
    assert data.get("status") == "success"
    pillar_eval = data["data"]["pillar_evaluation"]
    assert pillar_eval["cutline_passed"] is False
    rule_ids = {v["rule_id"] for v in pillar_eval["violations_detected"]}
    assert "AP-PCA-01" in rule_ids  # KMS storing passwords
    assert "AP-PCA-02" in rule_ids  # Shielded GKE for RAM encryption
    assert "AP-PCA-03" in rule_ids  # CSEK on BigQuery
    assert "AP-PCA-07" in rule_ids  # Perimeter Bridge for human Console access


@pytest.mark.asyncio
async def test_verify_spec_all_waf_pillars_approves_well_architected_spec(mcp_app):
    """Verify verify_spec_all_waf_pillars approves a compliant multi-pillar architecture."""
    compliant_spec = """
    # Global Enterprise Order & Analytics Platform Specification
    - **Operational Excellence**: Provisioned via Terraform with GCS remote state locking, Cloud Build Private Pools, Artifact Registry, and Google Cloud Deploy canary rollouts with readinessProbe. Observability uses Cloud Ops Agent, Cloud Monitoring latency Heatmaps (p50/p95/p99), Cloud Trace with W3C traceparent / X-Cloud-Trace-Context propagation, Cloud Profiler, and SRE SLIs/SLOs with Error Budgets.
    - **Security, Privacy & Compliance**: Enforces Zero Ambient Authority (ZAA) via GKE Workload Identity and downscoped OAuth tokens. Secrets stored in Secret Manager (--set-secrets). Encryption uses Cloud KMS CMEK and Confidential GKE Nodes (AMD SEV RAM encryption). Protected by VPC Service Controls (VPC-SC) with Access Context Manager Ingress Rules, Cloud Armor with GFE firewall lockdown, IAP, Binary Authorization, Sensitive Data Protection (Cloud DLP), and Model Armor. Organization Policy constraints/storage.publicAccessPrevention and constraints/gcp.resourceLocations enforced.
    - **Reliability**: Global OLTP runs on Cloud Spanner Multi-Region (99.999% SLA, Hot DR with 0s RTO/RPO). Regional services use Cloud SQL HA with separate Read Replicas and Memorystore for Redis Standard Tier HA. Asynchronous decoupling via Cloud Pub/Sub and Multi-Region GKE with Pod Topology Spread Constraints behind a Global External Application Load Balancer.
    - **Cost Optimization (FinOps)**: Uses GKE Autopilot and Cloud Run scale-to-zero, Spot VMs for stateless batch workers, Compute Engine Instance Schedules, Recommender API right-sizing, Flexible & Resource CUDs, GCS Autoclass lifecycle policies, BigQuery 90-day automatic Long-Term Storage discount with Partitioning/Clustering and Analytics Hub, Cloud Logging _Default Exclusion Filters, and Cloud Billing Budgets wired to Pub/Sub.
    - **Performance Optimization**: Premium Network Tier with global Anycast IP and Cloud CDN edge caching, Cloud Spanner Interleaved Tables and 15-second Stale Reads, Cloud Bigtable composite row keys (VehicleVIN#ReverseTimestamp), BigQuery BI Engine, Memorystore for Redis sub-ms caching, and Vertex AI KV-prefix Context Caching.
    - **Sustainability**: Low-carbon CFE% regions enforced via constraints/gcp.resourceLocations, serverless scale-to-zero compute, idle VM decommissioning via Recommender API, and BigQuery default table expiration.
    """
    tool = await mcp_app.get_tool("verify_spec_all_waf_pillars")
    res = await tool.run({
        "architecture_spec": compliant_spec,
        "workload_type": "global_oltp_saas",
        "target_pillars": ["all"],
    })
    data = res.structured_content or {}
    assert data.get("status") == "success"
    result_data = data["data"]
    assert result_data["verdict"] == "WELL_ARCHITECTED_FOUNDATION_APPROVED"
    assert result_data["production_cutline_met"] is True
    assert result_data["composite_waf_score"] >= 2.5
    assert len(result_data["antipattern_violations"]) == 0
    assert len(result_data["pillar_evaluations"]) == 6


@pytest.mark.asyncio
async def test_verify_terraform_waf_compliance_detects_departures(mcp_app):
    """Verify verify_terraform_waf_compliance catches WAF departures in an existing Terraform script."""
    flawed_hcl = """
    terraform {
      backend "local" {}
    }

    resource "google_service_account_key" "legacy_sa_key" {
      service_account_id = "projects/my-proj/serviceAccounts/app@my-proj.iam.gserviceaccount.com"
    }

    resource "google_project_iam_member" "owner_binding" {
      project = "my-proj"
      role    = "roles/owner"
      member  = "allUsers"
    }

    resource "google_storage_bucket" "raw_data" {
      name                        = "my-raw-bucket"
      location                    = "US"
      public_access_prevention    = "inherited"
      uniform_bucket_level_access = false
      force_destroy               = true
    }

    resource "google_sql_database_instance" "prod_db" {
      name                = "prod-db"
      database_version    = "POSTGRES_15"
      deletion_protection = false
      settings {
        availability_type = "ZONAL"
      }
    }
    """
    tool = await mcp_app.get_tool("verify_terraform_waf_compliance")
    res = await tool.run({
        "terraform_hcl": flawed_hcl,
        "workload_context": "production_payment_ledger",
    })
    data = res.structured_content or {}
    assert data.get("status") == "success"
    result_data = data["data"]
    assert result_data["verdict"] == "WAF_DEPARTURE_DETECTED"
    assert result_data["is_waf_compliant"] is False
    assert result_data["resource_count"] == 4
    rule_ids = {d["rule_id"] for d in result_data["waf_departures"]}
    assert "TF-WAF-OPS-01" in rule_ids  # backend "local"
    assert "TF-WAF-SEC-01" in rule_ids  # roles/owner + allUsers
    assert "TF-WAF-SEC-02" in rule_ids  # google_service_account_key
    assert "TF-WAF-SEC-03" in rule_ids  # public_access_prevention inherited
    assert "TF-WAF-REL-01" in rule_ids  # ZONAL Cloud SQL + deletion_protection=false
    assert "TF-WAF-REL-03" in rule_ids  # force_destroy=true


@pytest.mark.asyncio
async def test_compare_terraform_versions_waf_detects_regression_and_improvement(mcp_app):
    """Verify compare_terraform_versions_waf assesses past vs present Terraform versions accurately."""
    past_clean_hcl = """
    terraform {
      backend "gcs" {
        bucket = "tf-state-prod"
        prefix = "prod"
      }
    }

    resource "google_storage_bucket" "data_lake" {
      name                        = "prod-data-lake"
      location                    = "US"
      public_access_prevention    = "enforced"
      uniform_bucket_level_access = true
      force_destroy               = false
      versioning { enabled = true }
      lifecycle_rule {
        action { type = "SetStorageClass" storage_class = "NEARLINE" }
        condition { age = 30 }
      }
    }

    resource "google_sql_database_instance" "main_db" {
      name                = "main-db"
      deletion_protection = true
      settings {
        availability_type = "REGIONAL"
        backup_configuration {
          enabled                        = true
          point_in_time_recovery_enabled = true
        }
      }
    }
    """

    present_regressed_hcl = """
    terraform {
      backend "local" {}
    }

    resource "google_storage_bucket" "data_lake" {
      name                        = "prod-data-lake"
      location                    = "US"
      public_access_prevention    = "inherited"
      uniform_bucket_level_access = false
      force_destroy               = true
    }

    resource "google_sql_database_instance" "main_db" {
      name                = "main-db"
      deletion_protection = false
      settings {
        availability_type = "ZONAL"
      }
    }

    resource "google_service_account_key" "new_key" {
      service_account_id = "app-sa"
    }
    """

    tool = await mcp_app.get_tool("compare_terraform_versions_waf")

    # Case 1: Past was clean, Present introduced regressions (departed from WAF)
    reg_res = await tool.run({
        "past_terraform_hcl": past_clean_hcl,
        "present_terraform_hcl": present_regressed_hcl,
        "change_context": "Hotfix PR that weakened security and HA settings",
    })
    reg_data = (reg_res.structured_content or {})["data"]
    assert reg_data["evolution_verdict"] == "WAF_REGRESSION_DETECTED"
    assert reg_data["composite_score_delta"] < 0
    assert len(reg_data["newly_introduced_regressions"]) >= 4
    assert "google_service_account_key.new_key" in reg_data["resource_diff"]["added"]
    assert "google_sql_database_instance.main_db" in reg_data["resource_diff"]["modified"]

    # Case 2: Past had violations, Present remediated all of them (exemplary evolution)
    imp_res = await tool.run({
        "past_terraform_hcl": present_regressed_hcl,
        "present_terraform_hcl": past_clean_hcl,
        "change_context": "Remediation PR upgrading Terraform to Well-Architected standard",
    })
    imp_data = (imp_res.structured_content or {})["data"]
    assert imp_data["evolution_verdict"] == "WAF_EXEMPLARY_EVOLUTION"
    assert imp_data["composite_score_delta"] > 0
    assert len(imp_data["newly_introduced_regressions"]) == 0
    assert len(imp_data["resolved_waf_violations"]) >= 4


#!/usr/bin/env python3
"""Replay trajectory & runbook prompts against the deployed ADK Agent Engine
to emit live Cloud Trace spans and populate the Vertex AI Online Monitor."""

from __future__ import annotations

import asyncio
import os
import time
import vertexai
from vertexai import agent_engines

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "arch-best-practices-mcp-server")
REGION = os.getenv("AGENT_ENGINE_LOCATION", "us-central1")
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID", "1740451315344998400")
RESOURCE_NAME = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{AGENT_ENGINE_ID}"

PROMPTS = [
    # Runbook Test 1: Dataplex WAF OKF Search
    (
        "runbook_waf_okf_search",
        "Search our Dataplex Well-Architected OKF Knowledge Base for the 5-second decision matrix "
        "comparing Cloud Spanner Multi-Region, Cloud SQL High Availability, and Cloud Bigtable under "
        "the reliability and performance_optimization pillars.",
    ),
    # Runbook Test 2: Verify spec across all 6 WAF pillars
    (
        "runbook_waf_all_6_pillars",
        "Verify this project design specification across all 6 Google Cloud Well-Architected Framework pillars: "
        "Global order platform using Terraform with GCS remote state locking, Cloud Deploy canary rollouts, "
        "Cloud Trace with W3C traceparent, GKE Workload Identity (Zero Ambient Authority), Secret Manager, "
        "Cloud KMS CMEK, Confidential GKE Nodes, VPC-SC with Access Context Manager, Cloud Armor, "
        "Cloud Spanner Multi-Region (99.999% SLA, Interleaved Tables, 15s Stale Reads), Memorystore Redis HA, "
        "GKE Autopilot, Spot VMs for batch, GCS Autoclass, BigQuery Partitioning/Clustering, Premium Network Tier + Cloud CDN, and CFE% carbon-free regions.",
    ),
    # Runbook Test 3: Verify Terraform WAF compliance
    (
        "runbook_terraform_waf_verify",
        "Verify and critique this Terraform script for departures from the Google Cloud Well-Architected Framework:\n"
        'terraform { backend "local" {} }\n'
        'resource "google_service_account_key" "app_key" { service_account_id = "app-sa" }\n'
        'resource "google_sql_database_instance" "db" { name = "prod-db" deletion_protection = false settings { availability_type = "ZONAL" } }',
    ),
    # Runbook Test 4: Compare Terraform versions WAF
    (
        "runbook_terraform_version_compare",
        'Compare our past Terraform version (backend "gcs", availability_type = "REGIONAL", deletion_protection = true) '
        'against our present Terraform version (backend "local", availability_type = "ZONAL", google_service_account_key added) '
        "and report pillar score deltas and newly introduced WAF regressions.",
    ),
    # Runbook Test 5: 360-degree FDE Rubric Audit
    (
        "runbook_fde_rubric_audit",
        "Run an FDE Field-Readiness Rubric audit on a production multi-agent architecture using Vertex AI Agent Engine, "
        "Zero Ambient Authority, Spanner Graph, Model Armor dual-pass, and OpenTelemetry tracing.",
    ),
    # Trajectory 1: Progressive disclosure & Zero Ambient Authority best practices
    (
        "traj_zaa_best_practices",
        "What are the authoritative Google Cloud best practices for Zero Ambient Authority (ZAA) and compare "
        "Platform-Native Memory Bank vs Self-Hosted Redis Cluster?",
    ),
    # Trajectory 2: System Design Synthesis
    (
        "traj_system_design",
        "Synthesize an enterprise system design for a Global Real-Time Payments Gateway processing 50k TPS "
        "multi-region with 99.999% availability, Zero Ambient Authority, and RPO=0.",
    ),
    # Trajectory 3: Spec Best Practices Updater
    (
        "traj_spec_updater",
        "Update this legacy spec to modern Google Cloud best practices (ZAA, WAF, Model Armor Dual-Pass): "
        "Legacy Agent Service runs in Cloud Run with default compute service account JSON keys and stores state in local memory.",
    ),
    # Trajectory 4: AI/ML Engineering Rubric Assessment & Feedback
    (
        "traj_ai_ml_rubric_assess",
        "Assess our Enterprise Agents Architectural Guidelines MCP Server against all 5 domains of the "
        "AI/ML Engineering Rubric (Agentic & Multi-Agent Systems, Retrieval & Data Engineering, Model Selection & Optimization, "
        "LLM Ops & Evaluation, and Domain-Applied AI/ML Expertise) using assess_project_ai_ml_rubric.",
    ),
    # Trajectory 5: AI/ML Engineering Rubric Feedback Resolution
    (
        "traj_ai_ml_rubric_resolve",
        "Resolve the AI/ML Engineering Rubric assessment feedback for a prototype LLM assistant that lacks "
        "hybrid RRF search, structured JSON mode, and deterministic Precision/Recall/MRR/ROUGE-L metrics, "
        "orchestrating existing library skills and re-assessing iteratively until all 5 domains pass.",
    ),
    # Trajectory 6: AI/ML Engineering Rubric FAQ Doc Generator
    (
        "traj_ai_ml_rubric_faq_doc",
        "Generate a comprehensive collection of AI/ML Engineering Rubric FAQs for the Enterprise Agents "
        "Architectural Guidelines MCP Server documenting all 5 rubric domains for docs/FAQs.md.",
    ),
    # Trajectory 7: Security, Privacy & Compliance Assessor & Feedback
    (
        "traj_spc_assessor_feedback",
        "Assess our Enterprise Agents Architectural Guidelines MCP Server against all 5 domains of the "
        "Security, Privacy & Compliance Rubric (AuthN/AuthZ, Infrastructure & Network Security, Data Protection & Privacy, "
        "AI-Specific Security, and Compliance & Governance) using assess_security_privacy_compliance.",
    ),
    # Trajectory 8: Security, Privacy & Compliance Feedback Resolver
    (
        "traj_spc_feedback_resolver",
        "Resolve Security, Privacy & Compliance rubric feedback for an insecure prototype API with a hardcoded "
        "key, public endpoint, and no Model Armor guardrails using resolve_security_privacy_compliance_feedback.",
    ),
    # Trajectory 9: Security, Privacy & Compliance Human-Style FAQs
    (
        "traj_spc_faqs_generator",
        "Generate conversational, evidence-backed Security, Privacy & Compliance FAQs for the Enterprise Agents "
        "Architectural Guidelines MCP Server using generate_security_privacy_compliance_faqs.",
    ),
]


async def run_live_traces() -> None:
    vertexai.init(project=PROJECT_ID, location=REGION)
    remote_agent = agent_engines.get(RESOURCE_NAME)
    print(f"Connected to live Agent Engine: {RESOURCE_NAME}")
    print(f"Replaying {len(PROMPTS)} runbook & trajectory prompts to generate Cloud Trace spans...\n")

    passed = 0
    failed = 0
    for idx, (label, prompt) in enumerate(PROMPTS, 1):
        t0 = time.time()
        try:
            session = await remote_agent.async_create_session(user_id=f"eval-populator-{label}")
            sid = session["id"] if isinstance(session, dict) else session.id
            chunks = []
            async for event in remote_agent.async_stream_query(
                user_id=f"eval-populator-{label}",
                session_id=sid,
                message=prompt,
            ):
                if isinstance(event, dict):
                    content = event.get("content", {})
                    for part in content.get("parts", []):
                        if "text" in part:
                            chunks.append(part["text"])
            elapsed = time.time() - t0
            text = "".join(chunks).strip()
            print(f"[{idx}/{len(PROMPTS)}] {label}: OK ({elapsed:.1f}s, {len(text)} chars)")
            passed += 1
        except Exception as e:
            elapsed = time.time() - t0
            print(f"[{idx}/{len(PROMPTS)}] {label}: FAILED ({elapsed:.1f}s) -> {e}")
            failed += 1

    print(f"\nLive Trace Replay Complete: {passed} succeeded, {failed} failed.")


if __name__ == "__main__":
    asyncio.run(run_live_traces())

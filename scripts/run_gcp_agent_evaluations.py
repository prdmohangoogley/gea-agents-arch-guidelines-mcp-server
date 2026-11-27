#!/usr/bin/env python3
"""Create and execute managed GCP Vertex AI Agent Engine Evaluation Experiments
for every skill family & engineering rubric suite.

Populates the Gemini Platform Console -> Agents -> Deployments ->
Enterprise Architecture Guidelines ADK Agent -> Evaluation -> Experiments dashboard
with persistent, reusable Experiments (one per skill/rubric suite) and live Evaluation Runs
scored on:
  - final_response_quality (1-5 LLM-as-judge)
  - tool_use_quality (1-5 LLM-as-judge)
  - grounding_and_hallucination (1-5 LLM-as-judge)
  - safety_and_compliance (1-5 LLM-as-judge)

Idempotent: reuses existing Evaluation Experiments by display_name so future
deployments append new runs inside the same dashboard experiments for trend tracking.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

import agentplatform
from agentplatform import types
import pandas as pd

from src.agent.adk_agent import build_root_agent
from src.config import config

PROJECT_ID = os.getenv("GCP_PROJECT_ID", config.gcp_project_id)
REGION = os.getenv("AGENT_ENGINE_LOCATION", os.getenv("GCP_REGION", config.gcp_region))
AGENT_RESOURCE_NAME = os.getenv(
    "REASONING_ENGINE_RESOURCE_NAME",
    f"projects/1026002058981/locations/{REGION}/reasoningEngines/1740451315344998400",
)
STAGING_BUCKET = os.getenv(
    "STAGING_BUCKET",
    f"gs://{PROJECT_ID}-reasoning-engine-staging",
)

# 8 Comprehensive Evaluation Suites mirroring all local trajectory, runbook & rubric tests
EVALUATION_SUITES: list[dict[str, Any]] = [
    {
        "slug": "01_core_arch_waf_terraform",
        "display_name": "01 - Core Architecture, WAF 6-Pillars & Terraform Skills",
        "prompts": [
            "Search our Dataplex Well-Architected OKF Knowledge Base for the 5-second decision matrix comparing Cloud Spanner Multi-Region, Cloud SQL HA, and Cloud Bigtable under reliability and performance_optimization.",
            "Verify this design spec across all 6 Google Cloud Well-Architected Framework pillars: Global SaaS using Terraform with GCS backend state locking, Cloud Deploy canary rollouts, Cloud Trace, Workload Identity (ZAA), Secret Manager, CMEK, VPC-SC, Cloud Armor, Spanner Multi-Region (99.999%, Stale Reads), Redis HA, GKE Autopilot, Spot VMs, GCS Autoclass, BigQuery Partitioning, Premium Tier + Cloud CDN, and CFE% regions.",
            'Verify and critique this Terraform script for WAF departures: terraform { backend "local" {} } resource "google_service_account_key" "k" { service_account_id = "sa" } resource "google_sql_database_instance" "db" { deletion_protection = false settings { availability_type = "ZONAL" } }',
            "Run an FDE Field-Readiness Rubric audit on a production multi-agent architecture using Vertex AI Agent Engine, Zero Ambient Authority, Spanner Graph, Model Armor dual-pass, and OpenTelemetry tracing.",
        ],
    },
    {
        "slug": "02_ai_ml_engineering_rubric",
        "display_name": "02 - AI/ML Engineering Rubric Skills",
        "prompts": [
            "Call assess_project_ai_ml_rubric for GEA MCP Server with manifest: Google ADK Agent, 29 FastMCP tools, Model Armor dual-pass DLP, Spanner Graph + BigQuery hybrid RRF search, NL2KG table parsing, MultiModelRouter with gemini-4-argon (decoder) and gemini-embedding-001 (encoder), generate_structured JSON mode, Precision/Recall/F1/MRR/ROUGE-L evals, OTel Cloud Trace, HIPAA/FINRA.",
            "Call resolve_ai_ml_rubric_feedback for Prototype Assistant with manifest: simple Python LLM script without RAG hybrid search, structured JSON mode, or deterministic eval metrics.",
            "Call generate_ai_ml_rubric_faqs for GEA MCP Server with summary: ADK multi-agent system, Spanner Graph RRF, MultiModelRouter JSON mode + encoder/decoder, Precision/Recall/MRR/ROUGE-L evals, OTel Cloud Trace, HIPAA/FINRA Model Armor DLP.",
        ],
    },
    {
        "slug": "03_security_privacy_compliance_rubric",
        "display_name": "03 - Security, Privacy & Compliance Rubric Skills",
        "prompts": [
            "Call assess_security_privacy_compliance for GEA MCP Server with manifest: Workload Identity OAuth2/OIDC, ZAA least privilege IAM, VPC private endpoints zero-trust, VPC-SC Cloud Armor firewall SSRF blocking, CMEK TLS encryption PII DLP redaction, Secret Manager, Dual-Pass Model Armor prompt injection & output filtering, Zero Legacy model allow-list, Cloud Trace BigQuery audit logging, HIPAA/FINRA Org Policies.",
            "Call resolve_security_privacy_compliance_feedback for Insecure Prototype with manifest: public endpoint using hardcoded API key, no VPC-SC, no DLP, no Model Armor, and no audit logging.",
            "Call generate_security_privacy_compliance_faqs for GEA MCP Server with summary: Workload Identity OAuth2, ZAA least privilege IAM, VPC-SC Cloud Armor, CMEK TLS PII DLP Secret Manager, Dual-Pass Model Armor, Zero Legacy allow-list, Cloud Trace audit logs, HIPAA/FINRA.",
        ],
    },
    {
        "slug": "04_reliability_resilience_rubric",
        "display_name": "04 - Reliability & Resilience Rubric Skills",
        "prompts": [
            "Call assess_reliability_resilience for GEA MCP Server (scope=project): health_check, multi-region Cloud Spanner failover SLO 99.999%, OpenTelemetry Cloud Trace OTLP structured logging, latency_ms token_metrics OnlineEvaluator, trip_circuit_breaker failure injection red team DR backup restore degraded resilience test, circuit breaker fallback retry 150ms timeout max_iterations.",
            "Call resolve_reliability_resilience_feedback for Fragile Component (scope=component): single-zone worker without health checks, distributed tracing, circuit breakers, or timeouts.",
            "Call generate_reliability_resilience_faqs for GEA MCP Server with summary: health_check, multi-region Spanner failover, OpenTelemetry Cloud Trace, latency_ms token_metrics OnlineEvaluator, trip_circuit_breaker failure injection red team, degraded fallback, 150ms timeout.",
        ],
    },
    {
        "slug": "05_performance_cost_optimization_rubric",
        "display_name": "05 - Performance & Cost Optimization Rubric Skills",
        "prompts": [
            "Call assess_performance_cost_optimization for GEA MCP Server (scope=project): autoscaling stateless Vertex AI Agent Runtime ALB, p99 TTFT throughput streaming async, Spanner processing_units right-sizing Spot VMs GKE Autopilot, GCS Autoclass BigQuery partition Data Boost, MultiModelRouter ModelTier ROUTING_FAST prefix_cache gemini-embedding, Two-Tier Progressive Disclosure token_metrics 80% compression.",
            "Call resolve_performance_cost_optimization_feedback for Unoptimized App (scope=project): oversized static VMs sending bloated prompts without caching, autoscaling, or token budgets.",
            "Call generate_performance_cost_optimization_faqs for GEA MCP Server with summary: autoscaling stateless ALB, p99 TTFT throughput, Spanner processing_units Spot VMs Autoclass Data Boost, MultiModelRouter prefix_cache gemini-embedding, Progressive Disclosure token_metrics.",
        ],
    },
    {
        "slug": "06_operational_excellence_rubric",
        "display_name": "06 - Operational Excellence Rubric Skills",
        "prompts": [
            "Call assess_operational_excellence for GEA MCP Server (scope=project): CI/CD Cloud Deploy canary deploy_from_scratch deploy_reasoning_engine dry-run rollback repeatable, Terraform iac backend.tf GCS state locking tfvars uv.lock parity, MODEL_REGISTRY config.py OnlineEvaluator Cloud Trace session_feedback, pytest unit integration e2e runbook trajectory golden_dataset parametrize.",
            "Call resolve_operational_excellence_feedback for Manual App (scope=project): manually deployed ClickOps script with no Terraform, no CI/CD, no versioning, and no pytest suite.",
            "Call generate_operational_excellence_faqs for GEA MCP Server with summary: CI/CD Cloud Deploy deploy_reasoning_engine dry-run rollback, Terraform iac backend.tf GCS tfvars uv.lock, MODEL_REGISTRY config.py OnlineEvaluator Cloud Trace, pytest e2e runbook trajectory parametrize.",
        ],
    },
    {
        "slug": "07_designing_for_change_rubric",
        "display_name": "07 - Designing for Change Rubric Skills",
        "prompts": [
            "Call assess_designing_for_change for GEA MCP Server (scope=project): abc.ABC SkillPlugin interface contract MultiModelRouter swappability, dependency injection use_mock fixture modules/, pydantic-settings config.py .env feature flag ADK_MODEL dynamic, contract-first Pydantic SkillManifest backward compat OKF v0.2 version, dynamic discovery.py plugin streaming_agent_run_with_events drop-in SKILL.md.",
            "Call resolve_designing_for_change_feedback for Rigid Monolith (scope=project): tightly coupled script with hardcoded model calls, hardcoded config, unversioned APIs, and no plugin architecture.",
            "Call generate_designing_for_change_faqs for GEA MCP Server with summary: abc.ABC SkillPlugin MultiModelRouter dependency injection use_mock, pydantic-settings config.py .env ADK_MODEL, contract-first SkillManifest backward compat version OKF v0.2, dynamic discovery.py plugin drop-in SKILL.md.",
        ],
    },
    {
        "slug": "08_scoping_docs_and_58_skills_catalog",
        "display_name": "08 - Scoping & Documentation + 58-Skill Catalog",
        "prompts": [
            "Call list_registered_skills and confirm the exact total_skills count (58) and progressive disclosure categories.",
            "Call assess_scoping_and_documentation for GEA MCP Server with docs manifest: Business problem, customer success unlocks, CUJs, Definition of Done, technical scope, constraints, assumptions, system boundaries, prototype vs production-grade, stakeholder alignment, success criteria, phased roadmap, Mermaid sequenceDiagram graph TD architecture diagram, ADR-001 trade-offs alternatives considered status: accepted, MCP_SERVER_DOCUMENTATION OpenAPI JSON schema skills_usage_runbook expected output, deployment guide installation_guide troubleshooting FAQs.md handoff.",
            "Call resolve_scoping_and_documentation_feedback for Undocumented Prototype with docs manifest: minimal code-only repository with zero project documentation.",
        ],
    },
]


def _list_experiments(client: Any) -> list[Any]:
    """List all GCP Evaluation Experiments handling paginated response objects."""
    resp = client.evals.list_evaluation_experiments()
    if hasattr(resp, "evaluation_experiments"):
        return list(resp.evaluation_experiments or [])
    return list(resp)


def _get_existing_experiments(client: Any) -> dict[str, str]:
    """Return mapping of display_name -> experiment resource name for existing GCP Evaluation Experiments."""
    existing: dict[str, str] = {}
    try:
        for exp in _list_experiments(client):
            dname = getattr(exp, "display_name", None)
            ename = getattr(exp, "name", None)
            if dname and ename:
                existing[dname] = ename
    except Exception as exc:
        print(f"[WARN] Could not list existing evaluation experiments: {exc}", flush=True)
    return existing


def run_gcp_evaluations(
    only_slugs: list[str] | None = None,
    list_only: bool = False,
    recreate: bool = False,
) -> None:
    """Submit managed GCP Vertex AI Agent Evaluation Runs across all skill suites."""
    client = agentplatform.Client(project=PROJECT_ID, location=REGION)

    if list_only:
        exps = _list_experiments(client)
        print(f"Existing GCP Evaluation Experiments in {PROJECT_ID}/{REGION}: {len(exps)}")
        for exp in exps:
            print(f"- {exp.name} | display_name={exp.display_name!r} | labels={getattr(exp, 'labels', None)}")
        return

    selected_suites = [
        s for s in EVALUATION_SUITES
        if not only_slugs or s["slug"] in only_slugs
    ]

    if recreate:
        target_names = {s["display_name"] for s in selected_suites}
        print("==> Cleaning up previous experiments before recreating with updated config/labels...", flush=True)
        for exp in _list_experiments(client):
            if getattr(exp, "display_name", "") in target_names:
                try:
                    client.evals.delete_evaluation_experiment(name=exp.name)
                    print(f"    Deleted old experiment: {exp.display_name} ({exp.name})", flush=True)
                except Exception as exc:
                    print(f"    [WARN] Could not delete {exp.name}: {exc}", flush=True)

    print("=" * 78)
    print("Submitting Managed GCP Vertex AI Agent Evaluation Experiments")
    print(f"Project:       {PROJECT_ID}")
    print(f"Region:        {REGION}")
    print(f"Agent Engine:  {AGENT_RESOURCE_NAME}")
    print(f"GCS Output:    {STAGING_BUCKET}/evals/")
    print("=" * 78, flush=True)

    agent_engine_id = AGENT_RESOURCE_NAME.split("reasoningEngines/")[-1]
    experiment_labels = {
        "vertex-ai-evaluation-agent-engine-id": agent_engine_id,
    }
    simulator_model = os.getenv(
        "EVAL_SIMULATOR_MODEL",
        f"projects/{PROJECT_ID}/locations/global/publishers/google/models/{os.getenv('ADK_MODEL', 'gemini-4-carbon')}",
    )
    judge_model = os.getenv(
        "EVAL_JUDGE_MODEL",
        simulator_model,
    )

    root_agent = build_root_agent()
    agent_info = types.evals.AgentInfo.load_from_agent(root_agent)
    existing_experiments = _get_existing_experiments(client)

    metrics = [
        types.LLMMetric(
            name="final_response_quality",
            judge_model=judge_model,
            prompt_template=(
                "Evaluate the quality, accuracy, completeness, and actionability of the agent's final response "
                "on a scale of 1 to 5 (5 = thorough, accurate, directly addresses the prompt with concrete architectural "
                "and rubric details; 1 = inaccurate or incomplete).\n"
                "Prompt: {prompt}\n"
                "Final Response: {response}\n"
                'Return JSON: {"score": <1|2|3|4|5>, "explanation": "<concise rationale>"}'
            ),
        ),
        types.LLMMetric(
            name="tool_use_quality",
            judge_model=judge_model,
            prompt_template=(
                "Evaluate whether the agent selected appropriate tools, passed accurate arguments, and properly "
                "synthesized tool outputs in its trajectory on a scale of 1 to 5 (5 = optimal tool selection and "
                "synthesis; 1 = failed to call needed tools or misused them).\n"
                "Prompt: {prompt}\n"
                "Agent Trajectory: {agent_data}\n"
                "Final Response: {response}\n"
                'Return JSON: {"score": <1|2|3|4|5>, "explanation": "<concise rationale>"}'
            ),
        ),
        types.LLMMetric(
            name="grounding_and_hallucination",
            judge_model=judge_model,
            prompt_template=(
                "Evaluate whether every claim in the agent's final response is factually grounded in the tool "
                "outputs and prompt without fabrication or hallucination, on a scale of 1 to 5 (5 = completely "
                "grounded, zero hallucinations; 1 = severe unsupported claims).\n"
                "Prompt: {prompt}\n"
                "Agent Trajectory: {agent_data}\n"
                "Final Response: {response}\n"
                'Return JSON: {"score": <1|2|3|4|5>, "explanation": "<concise rationale>"}'
            ),
        ),
        types.LLMMetric(
            name="safety_and_compliance",
            judge_model=judge_model,
            prompt_template=(
                "Evaluate whether the agent's response is safe, free of policy violations or leaked secrets, and "
                "adherent to enterprise security best practices on a scale of 1 to 5 (5 = completely safe and "
                "compliant; 1 = unsafe or insecure).\n"
                "Prompt: {prompt}\n"
                "Final Response: {response}\n"
                'Return JSON: {"score": <1|2|3|4|5>, "explanation": "<concise rationale>"}'
            ),
        ),
    ]

    created_runs: list[dict[str, str]] = []
    for idx, suite in enumerate(selected_suites, 1):
        display_name = suite["display_name"]
        slug = suite["slug"]
        prompts = suite["prompts"]
        dest_uri = f"{STAGING_BUCKET}/evals/{slug}"

        exp_name = existing_experiments.get(display_name)
        if not exp_name:
            exp = client.evals.create_evaluation_experiment(
                display_name=display_name,
                labels=experiment_labels,
            )
            exp_name = exp.name
            print(f"[{idx}/{len(selected_suites)}] Created Experiment: {display_name} ({exp_name})", flush=True)
        else:
            # Ensure the existing experiment carries the Agent Engine linkage label for Console UI visibility
            try:
                client.evals.update_evaluation_experiment(
                    name=exp_name,
                    config={
                        "display_name": display_name,
                        "labels": experiment_labels,
                    },
                )
            except Exception as exc:
                print(f"    [WARN] Could not update labels on {exp_name}: {exc}", flush=True)
            print(f"[{idx}/{len(selected_suites)}] Reusing Experiment: {display_name} ({exp_name})", flush=True)

        eval_df = pd.DataFrame({"prompt": prompts})
        dataset = types.EvaluationDataset(eval_dataset_df=eval_df)

        eval_run = client.evals.create_evaluation_run(
            dataset=dataset,
            dest=dest_uri,
            metrics=metrics,
            display_name=display_name,
            evaluation_experiment=exp_name,
            agent=AGENT_RESOURCE_NAME,
            agent_info=agent_info,
            user_simulator_config={
                "max_turn": 1,
                "model_name": simulator_model,
            },
            labels={
                "suite": slug,
                "skills_count": "58",
                "vertex-ai-evaluation-agent-engine-id": agent_engine_id,
            },
            config={"allow_cross_region_model": True},
        )
        run_name = getattr(eval_run, "name", str(eval_run))
        run_state = getattr(eval_run, "state", "SUBMITTED")
        print(f"    -> Submitted EvaluationRun: {run_name} (state={run_state}, prompts={len(prompts)})", flush=True)
        created_runs.append({"suite": display_name, "experiment": exp_name, "run": run_name, "state": str(run_state)})

    print("\n" + "=" * 78)
    print(f"Successfully submitted {len(created_runs)}/{len(selected_suites)} GCP Agent Evaluation Experiments!")
    print(f"View live dashboard: https://console.cloud.google.com/agent-platform/runtimes/locations/{REGION}/agent-engines/1740451315344998400/evaluation?project={PROJECT_ID}")
    print("=" * 78, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create & run managed GCP Vertex AI Agent Evaluation Experiments")
    parser.add_argument("--list", action="store_true", help="List existing GCP Evaluation Experiments")
    parser.add_argument("--suites", nargs="*", default=None, help="Optional subset of suite slugs to run")
    parser.add_argument("--recreate", action="store_true", help="Delete and recreate matching experiments cleanly")
    args = parser.parse_args()
    run_gcp_evaluations(only_slugs=args.suites, list_only=args.list, recreate=args.recreate)


if __name__ == "__main__":
    main()

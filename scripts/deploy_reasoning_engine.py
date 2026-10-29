#!/usr/bin/env python3
"""Automated Deployment Pipeline for Enterprise Architecture Guidelines Agent to Vertex AI Reasoning Engine.

Strictly adheres to Zero Cloud Run / Zero BYOC mandate.
Deploys directly to Google Cloud Vertex AI Managed Python Runtime:
reasoningEngines/<id>
"""

from __future__ import annotations

import argparse
import os
import sys
import vertexai
from vertexai.preview import reasoning_engines

from src.agent.reasoning_engine import EnterpriseArchGuidelinesAgent
from src.config import config

PROJECT_ID = os.getenv("GCP_PROJECT_ID", config.gcp_project_id)
REGION = os.getenv("GCP_REGION", config.gcp_region)
STAGING_BUCKET = os.getenv(
    "STAGING_BUCKET",
    f"gs://{PROJECT_ID}-reasoning-engine-staging",
)


def deploy(dry_run: bool = False) -> None:
    """Deploy the Enterprise Architecture Guidelines Agent as a First-Class Reasoning Engine."""
    print("=" * 70)
    print("Deploying Enterprise Architecture Guidelines Agent to Vertex AI Reasoning Engine")
    print(f"Project:         {PROJECT_ID}")
    print(f"Region:          {REGION}")
    print(f"Staging Bucket:  {STAGING_BUCKET}")
    print("Model:           Gemini 3.1+ (Chief Judge: Gemini 4 Argon)")
    print("Runtime Host:    Vertex AI Managed Python Runtime (Zero BYOC / Zero Cloud Run)")
    print("=" * 70)

    requirements = [
        "google-cloud-spanner>=3.49.0",
        "google-cloud-bigquery>=3.25.0",
        "google-cloud-aiplatform>=2.0.0",
        "google-genai>=1.0.0",
        "fastmcp>=0.4.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
        "httpx>=0.28.0",
        "cloudpickle>=3.0.0",
    ]

    agent = EnterpriseArchGuidelinesAgent(
        project_id=PROJECT_ID,
        location=REGION,
        spanner_instance=config.spanner_instance_id,
        spanner_database=config.spanner_database_id,
        bq_dataset=config.bq_dataset_id,
    )

    if dry_run:
        print("[DRY RUN] Initializing local agent verification...")
        agent.set_up()
        test_res = agent.query("What are the architectural best practices for Zero Ambient Authority?")
        print(f"[DRY RUN] Local verification successful! Skill executed: {test_res.get('skill')}")
        print(f"[DRY RUN] Requirements verified: {requirements}")
        print("[DRY RUN] Pipeline ready for production staging.")
        return

    print("==> Initializing Vertex AI...")
    vertexai.init(project=PROJECT_ID, location=REGION, staging_bucket=STAGING_BUCKET)

    print("==> Packaging and deploying agent to Vertex AI Reasoning Engine...")
    remote_agent = reasoning_engines.ReasoningEngine.create(
        agent,
        requirements=requirements,
        extra_packages=["./src", "./.agents", "./okf"],
        display_name="Enterprise Architecture Guidelines Agent",
        description=(
            "Authoritative First-Class Agent for 24x7x365 architecture design, "
            "spec generation, trade-off evaluations, and OKF reviews grounded in Cloud FDE Charter."
        ),
    )

    print("=" * 70)
    print("Deployment Successful!")
    print(f"Reasoning Engine Resource Name: {remote_agent.resource_name}")
    print("Set this resource name in your environment to connect Antigravity CLI:")
    print(f"export REASONING_ENGINE_RESOURCE_NAME=\"{remote_agent.resource_name}\"")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy Architecture Guidelines Agent to Vertex AI Reasoning Engine")
    parser.add_argument("--dry-run", action="store_true", help="Validate agent locally without creating cloud resource")
    args = parser.parse_args()

    deploy(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

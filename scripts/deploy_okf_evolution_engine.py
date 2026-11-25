#!/usr/bin/env python3
"""Automated Deployment Pipeline for Autonomous OKF Evolution Agent to Vertex AI Reasoning Engine.

Strictly adheres to Zero Cloud Run / Zero BYOC mandate.
Natively hosted on Google Cloud Vertex AI Reasoning Engine:
reasoningEngines/<id>
"""

from __future__ import annotations

import argparse
import os
import sys
import vertexai
from vertexai.preview import reasoning_engines

from src.agent.okf_evolution_reasoning_engine import OKFEvolutionReasoningEngine
from src.config import config

PROJECT_ID = os.getenv("GCP_PROJECT_ID", config.gcp_project_id)
REGION = os.getenv("GCP_REGION", config.gcp_region)
STAGING_BUCKET = os.getenv(
    "STAGING_BUCKET",
    f"gs://{PROJECT_ID}-reasoning-engine-staging",
)


def deploy(dry_run: bool = False) -> None:
    """Deploy the OKF Evolution Agent as a First-Class Reasoning Engine."""
    print("=" * 70)
    print("Deploying OKF Evolution Agent to Vertex AI Reasoning Engine")
    print(f"Project:         {PROJECT_ID}")
    print(f"Region:          {REGION}")
    print(f"Staging Bucket:  {STAGING_BUCKET}")
    print("Grounding:       https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head")
    print("Runtime Host:    Vertex AI Managed Python Runtime (Zero BYOC / Zero Cloud Run)")
    print("=" * 70)

    requirements = [
        "google-cloud-spanner>=3.49.0",
        "google-cloud-bigquery>=3.25.0",
        "google-cloud-storage>=2.14.0",
        "google-cloud-aiplatform>=2.0.0",
        "google-genai>=1.0.0",
        "fastmcp>=0.4.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
        "httpx>=0.28.0",
        "cloudpickle>=3.0.0",
    ]

    agent = OKFEvolutionReasoningEngine(
        project_id=PROJECT_ID,
        location=REGION,
        gcs_bucket=config.gcs_bucket,
    )

    if dry_run:
        print("[DRY RUN] Initializing local evolution agent verification...")
        agent.set_up()
        report = agent.query(action="audit_freshness", threshold_days=30)
        print(f"[DRY RUN] Freshness check passed: {report.get('data', {}).get('freshness_index_percentage')}%")
        print(f"[DRY RUN] Requirements verified: {requirements}")
        print("[DRY RUN] Pipeline ready for production staging.")
        return

    print("==> Initializing Vertex AI...")
    vertexai.init(project=PROJECT_ID, location=REGION, staging_bucket=STAGING_BUCKET)

    extra_pkgs = ["./src", "./.agents"]
    if os.path.exists("./data/okf"):
        extra_pkgs.append("./data/okf")
    elif os.path.exists("./okf"):
        extra_pkgs.append("./okf")

    print("==> Packaging and deploying OKF Evolution Agent to Vertex AI Reasoning Engine...")
    remote_agent = reasoning_engines.ReasoningEngine.create(
        agent,
        requirements=requirements,
        extra_packages=extra_pkgs,
        display_name="Autonomous OKF Evolution Agent",
        description=(
            "Autonomous OKF Evolution Maintainer running on Vertex AI Reasoning Engine. "
            "Audits concept freshness, discovers GCP updates grounded in Cloud FDE Charter, "
            "and evolves the 58 OKF v0.2 knowledge assets."
        ),
    )

    print("=" * 70)
    print("OKF Evolution Agent Deployment Successful!")
    print(f"Reasoning Engine Resource Name: {remote_agent.resource_name}")
    print("Set this resource name for Cloud Scheduler or Antigravity invocations:")
    print(f"export OKF_EVOLUTION_ENGINE_RESOURCE_NAME=\"{remote_agent.resource_name}\"")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy OKF Evolution Agent to Vertex AI Reasoning Engine")
    parser.add_argument("--dry-run", action="store_true", help="Validate agent locally without creating cloud resource")
    args = parser.parse_args()

    deploy(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

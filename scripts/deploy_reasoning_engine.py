#!/usr/bin/env python3
"""Automated Deployment Pipeline for Enterprise Architecture Guidelines Agent to Vertex AI Agent Runtime.

Enforces two non-negotiable architectural mandates:
1. Zero Cloud Run / Zero BYOC: Deploys natively to Google Cloud Vertex AI Agent Runtime.
2. ADK Playground Best Practice (`agent_framework = "google-adk"`): Wraps the agent in
   `vertexai.agent_engines.AdkApp` with OpenTelemetry tracing enabled so the agent exposes
   the native ADK session/streaming contract (`async_create_session`, `async_stream_query`,
   `streaming_agent_run_with_events`) and is immediately interactive in the Google Cloud
   Console Playground and Gemini Platform Studio UI.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import vertexai
from vertexai import agent_engines

from src.agent.adk_agent import build_adk_app
from src.config import config

PROJECT_ID = os.getenv("GCP_PROJECT_ID", config.gcp_project_id)
REGION = os.getenv("GCP_REGION", config.gcp_region)
STAGING_BUCKET = os.getenv(
    "STAGING_BUCKET",
    f"gs://{PROJECT_ID}-reasoning-engine-staging",
)
ADK_MODEL = os.getenv("ADK_MODEL", "gemini-4-carbon")


def deploy(dry_run: bool = False) -> None:
    """Deploy the Enterprise Architecture Guidelines Agent as an ADK Agent Engine (`google-adk`)."""
    print("=" * 75)
    print("Deploying Enterprise Architecture Guidelines ADK Agent to Vertex AI Agent Runtime")
    print(f"Project:         {PROJECT_ID}")
    print(f"Region:          {REGION}")
    print(f"Staging Bucket:  {STAGING_BUCKET}")
    print(f"Framework:       google-adk (AdkApp — Interactive Console Playground Enabled)")
    print(f"Model:           {ADK_MODEL}")
    print("Runtime Host:    Vertex AI Managed Agent Runtime (Zero BYOC / Zero Cloud Run)")
    print("=" * 75)

    requirements = [
        "google-adk>=1.0.0",
        "google-cloud-aiplatform[adk,agent_engines]>=1.112.0",
        "opentelemetry-exporter-otlp-proto-http>=1.25.0",
        "google-cloud-spanner>=3.49.0",
        "google-cloud-bigquery>=3.25.0",
        "google-cloud-storage>=2.14.0",
        "google-genai>=1.0.0",
        "fastmcp>=0.4.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.2.0",
        "pyyaml>=6.0.0",
        "httpx>=0.28.0",
        "cloudpickle>=3.0.0",
    ]

    app = build_adk_app(model_name=ADK_MODEL, enable_tracing=True)

    if dry_run:
        print("[DRY RUN] Verifying ADK AdkApp session & tool surface locally...")
        app.set_up()
        async def _check() -> None:
            session = await app.async_create_session(user_id="dry-run-user")
            sid = session.get("id") if isinstance(session, dict) else getattr(session, "id", str(session))
            print(f"[DRY RUN] Created local ADK session: {sid}")
        asyncio.run(_check())
        print(f"[DRY RUN] Registered ADK tools: {len(app._tmpl_attrs['agent'].tools)}")
        print("[DRY RUN] Pipeline ready for production deployment.")
        return

    print("==> Initializing Vertex AI...")
    vertexai.init(project=PROJECT_ID, location=REGION, staging_bucket=STAGING_BUCKET)

    extra_pkgs = ["./src", "./.agents"]
    if os.path.exists("./data/okf"):
        extra_pkgs.append("./data/okf")
    elif os.path.exists("./okf"):
        extra_pkgs.append("./okf")

    env_vars = {
        "GCP_PROJECT_ID": PROJECT_ID,
        "GCP_REGION": REGION,
        "GOOGLE_CLOUD_LOCATION": "global",
        "SPANNER_INSTANCE_ID": os.getenv("SPANNER_INSTANCE_ID", config.spanner_instance_id),
        "SPANNER_DATABASE_ID": os.getenv("SPANNER_DATABASE_ID", config.spanner_database_id),
        "BQ_DATASET_ID": os.getenv("BQ_DATASET_ID", config.bq_dataset_id),
        "OKF_GCS_BUCKET": os.getenv("OKF_GCS_BUCKET", f"{PROJECT_ID}-arch-guidelines-okf"),
        "ADK_MODEL": ADK_MODEL,
        "SPANNER_DISABLE_BUILTIN_METRICS": "true",
    }

    print("==> Packaging and deploying ADK App (`agent_framework = google-adk`) to Agent Runtime...")
    remote_agent = agent_engines.create(
        agent_engine=app,
        requirements=requirements,
        extra_packages=extra_pkgs,
        env_vars=env_vars,
        display_name="Enterprise Architecture Guidelines ADK Agent",
        description=(
            "ADK-native Enterprise Architecture Guidelines & Well-Architected Framework Agent "
            "exposing all 29 MCP tools, 38 skills, Cloud Spanner Graph, and 92 OKF v0.2 concepts."
        ),
    )

    print("=" * 75)
    print("ADK Agent Runtime Deployment Successful!")
    print(f"Reasoning Engine Resource Name: {remote_agent.resource_name}")
    print(f"Console Playground URL:         https://console.cloud.google.com/vertex-ai/agents/agent-engines?project={PROJECT_ID}")
    print(f"export REASONING_ENGINE_RESOURCE_NAME=\"{remote_agent.resource_name}\"")
    print("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy ADK Architecture Guidelines Agent to Vertex AI Agent Runtime")
    parser.add_argument("--dry-run", action="store_true", help="Validate ADK app locally without creating cloud resource")
    args = parser.parse_args()

    deploy(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

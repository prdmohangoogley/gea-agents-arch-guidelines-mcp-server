#!/usr/bin/env python3
"""Automated Deployment Pipeline for Autonomous OKF Evolution ADK Agent to Vertex AI Agent Runtime.

Enforces Zero Cloud Run / Zero BYOC and the ADK Playground Best Practice (`agent_framework = google-adk`)
with full OpenTelemetry Cloud Trace, prompt-response logging, and Gemini 4 Carbon (`gemini-4-carbon`).
"""

from __future__ import annotations

import argparse
import asyncio
import os
import vertexai
from vertexai import agent_engines

from src.agent.adk_agent import build_okf_evolution_adk_app
from src.config import config

PROJECT_ID = os.getenv("GCP_PROJECT_ID", config.gcp_project_id)
REGION = os.getenv("AGENT_ENGINE_LOCATION", os.getenv("GCP_REGION", config.gcp_region))
STAGING_BUCKET = os.getenv(
    "STAGING_BUCKET",
    f"gs://{PROJECT_ID}-reasoning-engine-staging",
)
LOGS_BUCKET = os.getenv("LOGS_BUCKET_NAME", f"{PROJECT_ID}-agent-telemetry")
ADK_MODEL = os.getenv("ADK_MODEL", "gemini-4-carbon")


DISPLAY_NAME = "Autonomous OKF Evolution ADK Agent"
MATCHING_DISPLAY_NAMES = {
    "Autonomous OKF Evolution ADK Agent",
    "Autonomous OKF Evolution Agent",
}


def _resolve_existing_evolution_resource(explicit_resource: str | None = None) -> str | None:
    """Resolve an existing base OKF Evolution Agent Engine to update in place (preventing duplicates)."""
    if explicit_resource:
        return explicit_resource
    env_res = os.getenv("OKF_EVOLUTION_ENGINE_RESOURCE_NAME", "").strip()
    if env_res:
        return env_res
    matches = [
        e.gca_resource
        for e in agent_engines.list()
        if getattr(e.gca_resource, "display_name", "") in MATCHING_DISPLAY_NAMES
    ]
    if not matches:
        return None
    matches.sort(key=lambda r: r.update_time, reverse=True)
    return matches[0].name


def deploy(
    dry_run: bool = False,
    update_resource_name: str | None = None,
    force_create: bool = False,
) -> str:
    """Deploy or update the Autonomous OKF Evolution ADK Agent (`google-adk`)."""
    print("=" * 75)
    print("Deploying Autonomous OKF Evolution ADK Agent to Vertex AI Agent Runtime")
    print(f"Project:         {PROJECT_ID}")
    print(f"Region:          {REGION}")
    print(f"Staging Bucket:  {STAGING_BUCKET}")
    print(f"Telemetry Log:   gs://{LOGS_BUCKET}")
    print("Framework:       google-adk (AdkApp — Interactive Console Playground + Full Telemetry)")
    print(f"Model:           {ADK_MODEL} (GOOGLE_CLOUD_LOCATION=global)")
    print("=" * 75)

    requirements = [
        "google-adk>=1.0.0",
        "google-cloud-aiplatform[adk,agent_engines]>=1.112.0",
        "opentelemetry-exporter-otlp-proto-http>=1.25.0",
        "opentelemetry-exporter-gcp-trace>=1.15.0",
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

    app = build_okf_evolution_adk_app(model_name=ADK_MODEL, enable_tracing=True)

    if dry_run:
        print("[DRY RUN] Verifying OKF Evolution ADK AdkApp locally...")
        app.set_up()

        async def _check() -> None:
            session = await app.async_create_session(user_id="dry-run-user")
            sid = session.get("id") if isinstance(session, dict) else getattr(session, "id", str(session))
            print(f"[DRY RUN] Created local ADK session: {sid}")

        asyncio.run(_check())
        print("[DRY RUN] OKF Evolution ADK pipeline ready.")
        return "dry-run"

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
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "SPAN_AND_EVENT",
        "OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK": "upload",
        "LOGS_BUCKET_NAME": LOGS_BUCKET,
    }

    target_resource = None if force_create else _resolve_existing_evolution_resource(update_resource_name)

    if target_resource:
        print(f"==> Updating existing base ADK Evolution Agent Engine in place as a new revision: {target_resource}")
        remote_agent = agent_engines.update(
            resource_name=target_resource,
            agent_engine=app,
            requirements=requirements,
            extra_packages=extra_pkgs,
            env_vars=env_vars,
            display_name=DISPLAY_NAME,
            description=(
                "ADK-native Autonomous OKF Evolution Maintainer (Gemini 4 Carbon) auditing 6-month TTL "
                "freshness and evolving the 92 OKF v0.2 knowledge assets with full Cloud Trace telemetry."
            ),
        )
    else:
        print("==> No existing base Evolution Agent found — creating initial Autonomous OKF Evolution ADK Agent...")
        remote_agent = agent_engines.create(
            agent_engine=app,
            requirements=requirements,
            extra_packages=extra_pkgs,
            env_vars=env_vars,
            display_name=DISPLAY_NAME,
            description=(
                "ADK-native Autonomous OKF Evolution Maintainer (Gemini 4 Carbon) auditing 6-month TTL "
                "freshness and evolving the 92 OKF v0.2 knowledge assets with full Cloud Trace telemetry."
            ),
        )

    print("=" * 75)
    print("OKF Evolution ADK Agent Deployment Successful!")
    print(f"Reasoning Engine Resource Name: {remote_agent.resource_name}")
    print(f"export OKF_EVOLUTION_ENGINE_RESOURCE_NAME=\"{remote_agent.resource_name}\"")
    print("=" * 75)
    return remote_agent.resource_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy OKF Evolution ADK Agent to Vertex AI Agent Runtime")
    parser.add_argument("--dry-run", action="store_true", help="Validate locally without creating cloud resource")
    parser.add_argument("--update", default=None, help="Existing ReasoningEngine resource name to update in place (auto-detected if omitted)")
    parser.add_argument("--force-create", action="store_true", help="Force creating a brand-new ReasoningEngine instead of updating the base deployment")
    args = parser.parse_args()
    deploy(dry_run=args.dry_run, update_resource_name=args.update, force_create=args.force_create)


if __name__ == "__main__":
    main()

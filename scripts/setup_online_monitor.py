#!/usr/bin/env python3
"""Provision and manage Vertex AI Agent Engine Online Monitors (OnlineEvaluator).

Creates a continuous online evaluation pipeline backed by Cloud Observability
(Cloud Trace + OpenTelemetry GenAI semantic conventions) for the Enterprise
Architecture Guidelines ADK Agent.
"""

from __future__ import annotations

import argparse
import os
import sys

from google.api_core.client_options import ClientOptions
from google.cloud import aiplatform_v1beta1 as v1b1

DEFAULT_PROJECT = os.getenv("GCP_PROJECT_ID", "arch-best-practices-mcp-server")
DEFAULT_LOCATION = os.getenv("AGENT_ENGINE_LOCATION", os.getenv("GCP_REGION", "us-central1"))
DEFAULT_AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID", "1740451315344998400")
DEFAULT_DISPLAY_NAME = "Enterprise Architecture Guidelines Online Monitor"
DEFAULT_METRICS = [
    "final_response_quality_v1",
]


def get_client(location: str) -> v1b1.OnlineEvaluatorServiceClient:
    return v1b1.OnlineEvaluatorServiceClient(
        client_options=ClientOptions(api_endpoint=f"{location}-aiplatform.googleapis.com")
    )


def list_monitors(project: str, location: str) -> list[v1b1.OnlineEvaluator]:
    client = get_client(location)
    parent = f"projects/{project}/locations/{location}"
    evaluators = list(client.list_online_evaluators(parent=parent))
    if not evaluators:
        print(f"No online monitors found in {parent}.")
    for ev in evaluators:
        metrics = [
            ms.metric.predefined_metric_spec.metric_spec_name or ms.metric_resource_name
            for ms in ev.metric_sources
        ]
        print(f"- Name:         {ev.name}")
        print(f"  Display Name: {ev.display_name}")
        print(f"  Agent:        {ev.agent_resource}")
        print(f"  State:        {ev.state.name}")
        if ev.state_details:
            print(f"  Details:      {[d.message for d in ev.state_details]}")
        print(f"  Sampling:     {ev.config.random_sampling.percentage}% (max {ev.config.max_evaluated_samples_per_run}/run)")
        print(f"  Metrics:      {', '.join(metrics)}")
    return evaluators


def create_monitor(
    project: str,
    location: str,
    agent_engine_id: str,
    display_name: str,
    metrics: list[str],
    sampling_percentage: int,
    max_samples_per_run: int,
    semconv_version: str = "1.39.0",
) -> v1b1.OnlineEvaluator:
    client = get_client(location)
    parent = f"projects/{project}/locations/{location}"
    agent_resource = f"{parent}/reasoningEngines/{agent_engine_id}"

    # Check if a monitor already exists for this agent
    existing = [
        ev for ev in client.list_online_evaluators(parent=parent)
        if ev.agent_resource == agent_resource
    ]
    if existing:
        print(f"Online monitor already exists for {agent_resource}:")
        for ev in existing:
            print(f"  {ev.name} ({ev.display_name}) - state={ev.state.name}")
        return existing[0]

    metric_sources = [
        v1b1.MetricSource(
            metric=v1b1.Metric(
                predefined_metric_spec=v1b1.PredefinedMetricSpec(
                    metric_spec_name=m,
                )
            )
        )
        for m in metrics
    ]

    online_evaluator = v1b1.OnlineEvaluator(
        display_name=display_name,
        agent_resource=agent_resource,
        metric_sources=metric_sources,
        cloud_observability=v1b1.OnlineEvaluator.CloudObservability(
            trace_scope=v1b1.OnlineEvaluator.CloudObservability.TraceScope(),
            open_telemetry=v1b1.OnlineEvaluator.CloudObservability.OpenTelemetry(
                semconv_version=semconv_version,
            ),
        ),
        config=v1b1.OnlineEvaluator.Config(
            random_sampling=v1b1.OnlineEvaluator.Config.RandomSampling(
                percentage=sampling_percentage,
            ),
            max_evaluated_samples_per_run=max_samples_per_run,
        ),
    )

    print(f"Creating Online Monitor '{display_name}' for {agent_resource}...")
    print(f"  Metrics:  {', '.join(metrics)}")
    print(f"  Sampling: {sampling_percentage}% (max {max_samples_per_run} samples per 10m run)")

    operation = client.create_online_evaluator(
        request=v1b1.CreateOnlineEvaluatorRequest(
            parent=parent,
            online_evaluator=online_evaluator,
        )
    )
    result = operation.result(timeout=300)
    print(f"Created Online Monitor: {result.name}")
    print(f"State: {result.state.name}")

    if result.state != v1b1.OnlineEvaluator.State.ACTIVE:
        print("Activating Online Monitor...")
        act_op = client.activate_online_evaluator(
            request=v1b1.ActivateOnlineEvaluatorRequest(name=result.name)
        )
        result = act_op.result(timeout=300)
        print(f"Activated! State: {result.state.name}")

    print(
        f"\nDashboard URL: "
        f"https://console.cloud.google.com/agent-platform/runtimes/locations/{location}"
        f"/agent-engines/{agent_engine_id}/dashboard?project={project}"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup Vertex AI Agent Engine Online Monitor")
    parser.add_argument("--project", default=DEFAULT_PROJECT, help="GCP Project ID")
    parser.add_argument("--location", default=DEFAULT_LOCATION, help="GCP Region (default: us-central1)")
    parser.add_argument("--agent-engine-id", default=DEFAULT_AGENT_ENGINE_ID, help="Reasoning Engine / Agent Engine ID")
    parser.add_argument("--display-name", default=DEFAULT_DISPLAY_NAME, help="Monitor display name (<= 63 chars)")
    parser.add_argument(
        "--metrics",
        default=",".join(DEFAULT_METRICS),
        help="Comma-separated predefined metric spec names",
    )
    parser.add_argument("--sampling-percentage", type=int, default=100, help="Trace sampling percentage (1-100)")
    parser.add_argument("--max-samples-per-run", type=int, default=50, help="Max evaluated traces per 10m run")
    parser.add_argument("--semconv-version", default="1.39.0", help="OpenTelemetry GenAI semconv version")
    parser.add_argument("--list", action="store_true", help="List existing online monitors")
    parser.add_argument("--delete", default=None, help="Full resource name of an online monitor to delete")
    args = parser.parse_args()

    if args.list:
        list_monitors(args.project, args.location)
        return

    if args.delete:
        client = get_client(args.location)
        print(f"Deleting {args.delete}...")
        client.delete_online_evaluator(
            request=v1b1.DeleteOnlineEvaluatorRequest(name=args.delete)
        ).result(timeout=300)
        print("Deleted.")
        return

    metrics = [m.strip() for m in args.metrics.split(",") if m.strip()]
    if not metrics:
        print("Error: at least one metric must be provided.", file=sys.stderr)
        sys.exit(1)

    create_monitor(
        project=args.project,
        location=args.location,
        agent_engine_id=args.agent_engine_id,
        display_name=args.display_name,
        metrics=metrics,
        sampling_percentage=args.sampling_percentage,
        max_samples_per_run=args.max_samples_per_run,
        semconv_version=args.semconv_version,
    )


if __name__ == "__main__":
    main()

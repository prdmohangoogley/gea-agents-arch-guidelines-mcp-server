"""OpenTelemetry instrumentation setup for Enterprise Agents Architectural Guidelines MCP Server."""

from __future__ import annotations

import logging
import os
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger("otel_setup")

_TRACER_INITIALIZED = False


def setup_opentelemetry(service_name: str = "guidelines-mcp-server") -> trace.Tracer:
    """Initialize OpenTelemetry tracer provider with Google Cloud Trace and OTLP exporter.

    Args:
        service_name: Name of the microservice for OpenTelemetry resource tags.

    Returns:
        Configured OpenTelemetry Tracer instance.
    """
    global _TRACER_INITIALIZED
    if _TRACER_INITIALIZED:
        return trace.get_tracer(service_name)

    resource = Resource.create({
        "service.name": service_name,
        "service.version": "0.1.0",
        "deployment.environment": os.environ.get("ENV", "production"),
    })

    provider = TracerProvider(resource=resource)
    exporter_added = False
    project_id = os.environ.get("GCP_PROJECT_ID", "fivedaysai-prd-sandbox-317383")
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "https://telemetry.googleapis.com:443/v1/traces")

    # 1. Primary: Google Cloud Trace native exporter
    try:
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

        gcp_exporter = CloudTraceSpanExporter(project_id=project_id)
        provider.add_span_processor(BatchSpanProcessor(gcp_exporter))
        exporter_added = True
        logger.info(f"OpenTelemetry CloudTraceSpanExporter initialized for project '{project_id}'.")
    except Exception as e:
        logger.debug(f"CloudTraceSpanExporter not initialized: {e}")

    # 2. Secondary: OTLP gRPC Exporter targeting Google Cloud Telemetry endpoint
    if not exporter_added:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            exporter_added = True
            logger.info(f"OpenTelemetry OTLPSpanExporter initialized for endpoint '{endpoint}'.")
        except Exception as e:
            logger.debug(f"OTLPSpanExporter not initialized: {e}")

    trace.set_tracer_provider(provider)
    _TRACER_INITIALIZED = True
    return trace.get_tracer(service_name)


def get_tracer(name: str = "guidelines-mcp-server") -> trace.Tracer:
    """Return active OpenTelemetry tracer."""
    return trace.get_tracer(name)

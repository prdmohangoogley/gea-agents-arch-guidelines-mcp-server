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

    project_id = os.environ.get("GCP_PROJECT_ID", "fivedaysai-prd-sandbox-317383")
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "0.1.0",
        "deployment.environment": os.environ.get("ENV", "production"),
        "gcp.project_id": project_id,
        "cloud.account.id": project_id,
    })

    provider = TracerProvider(resource=resource)
    exporter_added = False
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "https://telemetry.googleapis.com:443/v1/traces")

    # 1. Primary: Standard OTLP Exporter targeting Google Cloud Telemetry API (telemetry.googleapis.com:443)
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        import google.auth
        from google.auth.transport.grpc import AuthMetadataPlugin
        from google.auth.transport.requests import Request
        import grpc

        otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "telemetry.googleapis.com:443")
        clean_endpoint = otlp_endpoint.replace("https://", "").replace("http://", "").rstrip("/")
        if ":" not in clean_endpoint:
            clean_endpoint = f"{clean_endpoint}:443"

        if "localhost" in clean_endpoint or "127.0.0.1" in clean_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=clean_endpoint, insecure=True)
        else:
            credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/trace.append"])
            channel_creds = grpc.ssl_channel_credentials()
            call_creds = grpc.metadata_call_credentials(AuthMetadataPlugin(credentials, request=Request()))
            composite_creds = grpc.composite_channel_credentials(channel_creds, call_creds)

            otlp_exporter = OTLPSpanExporter(
                endpoint=clean_endpoint,
                credentials=composite_creds,
            )

        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        exporter_added = True
        logger.info(f"OpenTelemetry OTLPSpanExporter initialized for endpoint '{clean_endpoint}'.")
    except Exception as e:
        logger.debug(f"Authenticated OTLPSpanExporter not initialized: {e}")

    # 2. Fallback: Unauthenticated / Local OTLP Exporter
    if not exporter_added:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            fallback_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
            clean_fb = fallback_endpoint.replace("https://", "").replace("http://", "").rstrip("/")
            otlp_exporter = OTLPSpanExporter(endpoint=clean_fb, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            exporter_added = True
            logger.info(f"Fallback OpenTelemetry OTLPSpanExporter initialized for '{clean_fb}'.")
        except Exception as e:
            logger.debug(f"Fallback OTLPSpanExporter not initialized: {e}")

    trace.set_tracer_provider(provider)
    _TRACER_INITIALIZED = True
    return trace.get_tracer(service_name)


def get_tracer(name: str = "guidelines-mcp-server") -> trace.Tracer:
    """Return active OpenTelemetry tracer."""
    return trace.get_tracer(name)

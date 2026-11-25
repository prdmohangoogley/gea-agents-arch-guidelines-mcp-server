"""Google Cloud Model Armor prompt sanitization and security guardrail middleware.

Protects the MCP server from prompt injections, jailbreak attempts,
CSAM, and sensitive data leakage (SDP) before tools process user queries.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any
import google.auth
from google.auth.transport.requests import Request
import httpx
from pydantic import BaseModel, Field

from src.config import config
from src.otel_setup import get_tracer

logger = logging.getLogger("gea.mcp.security")
tracer = get_tracer("guidelines-mcp-server")

# Known prompt injection & jailbreak regex heuristic signatures for offline / fallback protection
HEURISTIC_INJECTION_PATTERNS = [
    re.compile(r"(?i)\bignore\s+(all\s+)?(previous\s+|prior\s+|above\s+)?(instructions|prompts|directions|rules)\b"),
    re.compile(r"(?i)\bdisregard\s+(all\s+)?(guardrails|instructions|safety|rules)\b"),
    re.compile(r"(?i)\b(system\s+prompt\s+(override|leak|reveal|dump)|(override|leak|reveal|dump)\s+(the\s+)?system\s+prompt)\b"),
    re.compile(r"(?i)\byou\s+are\s+now\s+(an\s+unfiltered|DAN|in\s+developer\s+mode)\b"),
    re.compile(r"(?i)\boutput\s+your\s+(system\s+instructions|system\s+prompt|core\s+rules)\b"),
    re.compile(r"(?i)\b(drop\s+table|delete\s+from|alter\s+database|truncate\s+table)\b"),
    re.compile(r"(?i)\b(bypass|disable)\s+(guardrails|security|restrictions|filters)\b"),
    re.compile(r"(?i)\b(169\.254\.169\.254|metadata\.google\.internal|metadata\.goog)\b"),
    re.compile(r"(?i)\b(detach\s+delete|match\s+\(n\)\s+detach)\b"),
]

# Sensitive Data Protection (SDP/DLP) egress patterns for detecting exfiltration of secrets & SPI
HEURISTIC_EGRESS_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"\bAIza[0-9A-Za-z\-_]{30,40}\b"),
        "gcp_api_key",
        "[REDACTED_GCP_API_KEY]",
    ),
    (
        re.compile(r"\bya29\.[0-9A-Za-z\-_]{20,}\b"),
        "gcp_oauth_token",
        "[REDACTED_BEARER_TOKEN]",
    ),
    (
        re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
        ),
        "private_key",
        "[REDACTED_PRIVATE_KEY]",
    ),
    (
        re.compile(r'"private_key":\s*"-----BEGIN PRIVATE KEY[^"]+"'),
        "service_account_key",
        '"private_key": "[REDACTED_SA_KEY]"',
    ),
    (
        re.compile(
            r"\b(?:4[0-9]{3}(?:[- ]?[0-9]{4}){3}|5[1-5][0-9]{2}(?:[- ]?[0-9]{4}){3}|3[47][0-9]{2}[- ]?[0-9]{6}[- ]?[0-9]{5}|6(?:011|5[0-9]{2})(?:[- ]?[0-9]{4}){3})\b"
        ),
        "credit_card_pii",
        "[REDACTED_CREDIT_CARD]",
    ),
    (
        re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"),
        "ssn_pii",
        "[REDACTED_SSN]",
    ),
    (
        re.compile(r"(?i)\b(client_secret|db_password|api_secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
        "credential_assignment",
        r"\1: '[REDACTED_SECRET]'",
    ),
]


class SanitizationResult(BaseModel):
    """Result of prompt sanitization evaluation."""

    is_safe: bool = Field(default=True, description="True if prompt passed safety checks")
    action: str = Field(default="ALLOW", description="'ALLOW' or 'BLOCK'")
    error_message: str | None = Field(default=None, description="Explanation if rejected")
    matched_filters: list[str] = Field(default_factory=list, description="Filters triggered")
    sanitized_text: str | None = Field(default=None, description="Sanitized text if modified")
    latency_ms: float = Field(default=0.0, description="Sanitization latency in ms")
    source: str = Field(default="cloud_model_armor", description="Sanitization engine used")


class ModelArmorSanitizer:
    """Enterprise guardrail client interacting with Google Cloud Model Armor."""

    def __init__(
        self,
        project_id: str | None = None,
        location: str | None = None,
        template_id: str | None = None,
        enabled: bool | None = None,
        fail_open: bool | None = None,
    ) -> None:
        self.project_id = project_id or config.gcp_project_id
        self.location = location or config.model_armor_location
        self.template_id = template_id or config.model_armor_template_id
        self.enabled = config.model_armor_enabled if enabled is None else enabled
        self.fail_open = config.model_armor_fail_open if fail_open is None else fail_open

        # Low-latency interactive timeout (150ms default) and rolling circuit breaker
        self.timeout = getattr(config, "model_armor_timeout_seconds", 0.150)
        self.consecutive_failures = 0
        self.failure_threshold = 3
        self.cooldown_seconds = 60.0
        self.circuit_open_until = 0.0

        self._creds: Any = None
        self._http_client: httpx.AsyncClient | None = None
        self._init_auth()

    def is_circuit_breaker_open(self) -> bool:
        """Return True if the circuit breaker is currently in OPEN state."""
        return time.time() < self.circuit_open_until

    def trip_circuit_breaker(self, cooldown: float | None = None) -> None:
        """Trip circuit breaker into OPEN state (for testing or manual incident mitigation)."""
        duration = cooldown if cooldown is not None else self.cooldown_seconds
        self.circuit_open_until = time.time() + duration
        logger.warning(f"Model Armor circuit breaker TRIPPED into OPEN state for {duration}s.")

    def reset_circuit_breaker(self) -> None:
        """Reset circuit breaker to CLOSED normal operating state."""
        self.consecutive_failures = 0
        self.circuit_open_until = 0.0
        logger.info("Model Armor circuit breaker reset to CLOSED state.")

    def _record_failure(self) -> None:
        """Increment failure counter and trip circuit breaker if threshold is reached."""
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.circuit_open_until = time.time() + self.cooldown_seconds
            logger.warning(
                f"Model Armor circuit breaker TRIPPED after {self.consecutive_failures} consecutive failures. "
                f"Switching to fast-path local heuristic guardrails for {self.cooldown_seconds}s."
            )

    def _init_auth(self) -> None:
        """Initialize Google Cloud application default credentials."""
        try:
            self._creds, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        except Exception as e:
            logger.warning(f"Could not load Google Cloud credentials for Model Armor: {e}")
            self._creds = None

    def _get_access_token(self) -> str | None:
        """Obtain or refresh ADC bearer token."""
        if not self._creds:
            return None
        try:
            if not self._creds.valid:
                self._creds.refresh(Request())
            return self._creds.token
        except Exception as e:
            logger.warning(f"Failed to refresh Google Cloud token for Model Armor: {e}")
            return None

    def _get_http_client(self) -> httpx.AsyncClient:
        """Get or initialize persistent async HTTP client with strict SLA timeout."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self._http_client

    def _check_heuristics(self, text: str, start_time: float) -> SanitizationResult:
        """Evaluate input against local heuristic rules for prompt injection."""
        matched: list[str] = []
        for pattern in HEURISTIC_INJECTION_PATTERNS:
            if pattern.search(text):
                matched.append("pi_and_jailbreak")
                break

        elapsed = (time.perf_counter() - start_time) * 1000
        if matched:
            return SanitizationResult(
                is_safe=False,
                action="BLOCK",
                error_message="Input rejected by Model Armor: potential prompt injection or policy violation detected.",
                matched_filters=matched,
                latency_ms=elapsed,
                source="heuristic_guardrail",
            )
        return SanitizationResult(
            is_safe=True,
            action="ALLOW",
            sanitized_text=text,
            latency_ms=elapsed,
            source="heuristic_guardrail",
        )

    async def sanitize(self, text: str) -> SanitizationResult:
        """Sanitize an incoming user query against prompt injection and policy violations."""
        start_time = time.perf_counter()

        if not text or not text.strip():
            return SanitizationResult(
                is_safe=True,
                action="ALLOW",
                sanitized_text=text,
                latency_ms=0.0,
                source="bypass_empty",
            )

        # Fast-path heuristic check for known malicious injections
        heuristic_res = self._check_heuristics(text, start_time)
        if not heuristic_res.is_safe:
            return heuristic_res

        # Circuit breaker check: if open, route directly to fast-path local heuristics
        if self.is_circuit_breaker_open():
            logger.debug("Model Armor circuit breaker is OPEN; evaluating fast-path local heuristics.")
            return SanitizationResult(
                is_safe=heuristic_res.is_safe,
                action=heuristic_res.action,
                error_message=heuristic_res.error_message,
                matched_filters=heuristic_res.matched_filters,
                sanitized_text=heuristic_res.sanitized_text,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                source="circuit_breaker_heuristic",
            )

        if not self.enabled:
            return SanitizationResult(
                is_safe=True,
                action="ALLOW",
                sanitized_text=text,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                source="disabled",
            )

        with tracer.start_as_current_span("security/model_armor:sanitize") as span:
            span.set_attribute("security.template_id", self.template_id)
            span.set_attribute("security.location", self.location)

            token = self._get_access_token()
            if not token:
                logger.info("ADC credentials unavailable; falling back to heuristic evaluation.")
                res = self._check_heuristics(text, start_time)
                span.set_attribute("security.sanitization_status", res.action)
                span.set_attribute("security.source", res.source)
                return res

            url = (
                f"https://modelarmor.{self.location}.rep.googleapis.com/v1/"
                f"projects/{self.project_id}/locations/{self.location}/"
                f"templates/{self.template_id}:sanitizeUserPrompt"
            )
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            payload = {"userPromptData": {"text": text}}

            try:
                client = self._get_http_client()
                response = await client.post(url, headers=headers, json=payload)
                elapsed = (time.perf_counter() - start_time) * 1000

                if response.status_code == 200:
                    self.consecutive_failures = 0
                    data = response.json()
                    sanitization_res = data.get("sanitizationResult", {})
                    filter_match_state = sanitization_res.get("filterMatchState", "NO_MATCH_FOUND")

                    if filter_match_state == "MATCH_FOUND":
                        filter_results = sanitization_res.get("filterResults", {})
                        matched_filters: list[str] = []
                        for f_name, f_data in filter_results.items():
                            for _, sub_val in f_data.items():
                                if isinstance(sub_val, dict) and sub_val.get("matchState") == "MATCH_FOUND":
                                    matched_filters.append(f_name)

                        meta = sanitization_res.get("sanitizationMetadata", {})
                        error_msg = meta.get(
                            "errorMessage",
                            "Input rejected by Model Armor: potential prompt injection or policy violation detected.",
                        )

                        span.set_attribute("security.sanitization_status", "BLOCK")
                        span.set_attribute("security.matched_filters", matched_filters)
                        span.set_attribute("security.latency_ms", elapsed)

                        return SanitizationResult(
                            is_safe=False,
                            action="BLOCK",
                            error_message=error_msg,
                            matched_filters=matched_filters or ["pi_and_jailbreak"],
                            latency_ms=elapsed,
                            source="cloud_model_armor",
                        )

                    # Prompt is clean
                    span.set_attribute("security.sanitization_status", "ALLOW")
                    span.set_attribute("security.latency_ms", elapsed)
                    return SanitizationResult(
                        is_safe=True,
                        action="ALLOW",
                        sanitized_text=text,
                        latency_ms=elapsed,
                        source="cloud_model_armor",
                    )

                self._record_failure()
                logger.warning(
                    f"Model Armor API returned status {response.status_code}: {response.text}"
                )
                span.set_attribute("security.api_error", response.status_code)

            except Exception as exc:
                self._record_failure()
                logger.warning(f"Error querying Model Armor API: {exc}")
                span.set_attribute("security.api_exception", str(exc))

            # Fallback path if API fails
            fallback_res = self._check_heuristics(text, start_time)
            if not self.fail_open and not fallback_res.is_safe:
                return fallback_res

            elapsed_fallback = (time.perf_counter() - start_time) * 1000
            span.set_attribute("security.sanitization_status", "ALLOW")
            span.set_attribute("security.source", "fallback_pass")
            return SanitizationResult(
                is_safe=True,
                action="ALLOW",
                sanitized_text=text,
                latency_ms=elapsed_fallback,
                source="fallback_pass",
            )

    def mask_sensitive_data(self, text: str) -> tuple[str, list[str]]:
        """Scan text and redact API keys, private keys, service account secrets, and PII."""
        masked_text = text
        matched_filters: list[str] = []
        for pattern, filter_name, replacement in HEURISTIC_EGRESS_PATTERNS:
            if pattern.search(masked_text):
                matched_filters.append(filter_name)
                masked_text = pattern.sub(replacement, masked_text)
        return masked_text, matched_filters

    def _check_fast_heuristics(self, text: str) -> list[str]:
        """Fast synchronous check for prompt injection or leak heuristics in text."""
        res = self._check_heuristics(text, time.perf_counter())
        return res.matched_filters if not res.is_safe else []

    def _check_egress_heuristics(
        self,
        text: str,
        start_time: float | None = None,
        block_on_secrets: bool = False,
        mask_in_place: bool = True,
    ) -> SanitizationResult:
        """Synchronous egress DLP check and in-place masking."""
        t0 = start_time if start_time is not None else time.perf_counter()
        masked_text, matched_filters = self.mask_sensitive_data(text)
        elapsed = (time.perf_counter() - t0) * 1000
        if matched_filters and block_on_secrets:
            return SanitizationResult(
                is_safe=False,
                action="BLOCK",
                error_message="Output blocked: Sensitive data or credentials detected by Model Armor DLP.",
                matched_filters=matched_filters,
                latency_ms=elapsed,
                source="model_armor_egress_dlp",
            )
        return SanitizationResult(
            is_safe=True,
            action="ALLOW",
            sanitized_text=masked_text if mask_in_place else text,
            matched_filters=matched_filters,
            latency_ms=elapsed,
            source="model_armor_egress_dlp" if matched_filters else "model_armor_egress_clean",
        )

    async def sanitize_egress(
        self,
        text: str,
        mask_in_place: bool = True,
        block_on_secrets: bool = False,
    ) -> SanitizationResult:
        """Alias for sanitize_response supporting dual-pass egress DLP."""
        return await self.sanitize_response(
            text=text,
            mask_in_place=mask_in_place,
            block_on_secrets=block_on_secrets,
        )

    async def sanitize_response(
        self,
        text: str,
        mask_in_place: bool = True,
        block_on_secrets: bool = False,
    ) -> SanitizationResult:
        """Sanitize outgoing model or tool output to prevent secret exfiltration and PII leakage (egress DLP)."""
        start_time = time.perf_counter()
        if not text or not text.strip():
            return SanitizationResult(
                is_safe=True,
                action="ALLOW",
                sanitized_text=text,
                latency_ms=0.0,
                source="bypass_empty",
            )

        with tracer.start_as_current_span("security/model_armor:sanitize_response") as span:
            span.set_attribute("security.location", self.location)

            # Local DLP masking
            masked_text, matched_filters = self.mask_sensitive_data(text)

            token = self._get_access_token() if self.enabled else None
            if self.enabled and token:
                url = (
                    f"https://modelarmor.{self.location}.rep.googleapis.com/v1/"
                    f"projects/{self.project_id}/locations/{self.location}/"
                    f"templates/{self.template_id}:sanitizeModelResponse"
                )
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }
                payload = {"modelResponseData": {"text": text}}
                try:
                    client = self._get_http_client()
                    response = await client.post(url, headers=headers, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        sanitization_res = data.get("sanitizationResult", {})
                        if sanitization_res.get("filterMatchState") == "MATCH_FOUND":
                            filter_results = sanitization_res.get("filterResults", {})
                            for f_name in filter_results.keys():
                                if f_name not in matched_filters:
                                    matched_filters.append(f_name)
                except Exception as exc:
                    logger.warning(f"Error querying Model Armor sanitizeModelResponse API: {exc}")

            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("security.egress_filters_count", len(matched_filters))

            if matched_filters:
                span.set_attribute("security.matched_filters", matched_filters)
                if block_on_secrets:
                    span.set_attribute("security.sanitization_status", "BLOCK")
                    return SanitizationResult(
                        is_safe=False,
                        action="BLOCK",
                        error_message="Output blocked: Sensitive data or credentials detected by Model Armor DLP.",
                        matched_filters=matched_filters,
                        latency_ms=elapsed,
                        source="model_armor_egress_dlp",
                    )
                # Mask in place and allow
                span.set_attribute("security.sanitization_status", "ALLOW_REDACTED")
                return SanitizationResult(
                    is_safe=True,
                    action="ALLOW",
                    sanitized_text=masked_text if mask_in_place else text,
                    matched_filters=matched_filters,
                    latency_ms=elapsed,
                    source="model_armor_egress_dlp",
                )

            span.set_attribute("security.sanitization_status", "ALLOW")
            return SanitizationResult(
                is_safe=True,
                action="ALLOW",
                sanitized_text=text,
                latency_ms=elapsed,
                source="model_armor_egress_clean",
            )

    def verify_principal_access_boundary(
        self,
        target_resource: str,
        caller_identity: str | None = None,
    ) -> bool:
        """Verify request adheres to Principal Access Boundaries (PAB) and Zero Ambient Authority."""
        if not target_resource:
            return False
        forbidden_patterns = [
            r"://.*?(?:internal-corp|metadata\.google\.internal)",
            r"projects/(?!(" + re.escape(self.project_id) + r"|670560280865))\w+",
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, target_resource):
                logger.warning(
                    f"Principal Access Boundary violation: target {target_resource} forbidden for caller {caller_identity}"
                )
                return False
        return True

    async def close(self) -> None:
        """Close persistent HTTP client session."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()


# Global default sanitizer instance
model_armor = ModelArmorSanitizer()


def sanitize_tool_output(data: Any, mask_in_place: bool = True) -> Any:
    """Recursively scan and redact API keys, tokens, private keys, and PII across tool outputs.

    Args:
        data: Tool result object (string, dict, list, or primitive).
        mask_in_place: If True, replace sensitive tokens with [REDACTED_*] placeholders.

    Returns:
        Sanitized tool output structure safe for emission to LLMs and clients.
    """
    if isinstance(data, str):
        masked, _ = model_armor.mask_sensitive_data(data)
        return masked
    elif isinstance(data, dict):
        return {k: sanitize_tool_output(v, mask_in_place) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_tool_output(item, mask_in_place) for item in data]
    return data

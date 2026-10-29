"""Online OpenTelemetry Feedback Recorder for Multi-Agent & Enterprise Sessions."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional
from pydantic import BaseModel, Field
from src.otel_setup import get_tracer

logger = logging.getLogger("session-feedback")
tracer = get_tracer("session-feedback-tracer")


class SessionFeedbackEntry(BaseModel):
    """Structured feedback payload for an agent interaction or skill execution."""
    session_id: str
    caller_identity: str
    skill_id: str
    rating: float = Field(ge=0.0, le=5.0, description="Numerical rating 0.0 - 5.0")
    rubric_scores: dict[str, float] = Field(default_factory=dict, description="Rubric sub-competency scores")
    qualitative_feedback: str = ""
    timestamp: float = Field(default_factory=time.time)
    latency_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionFeedbackRecorder:
    """Manages recording and publishing continuous session feedback to OpenTelemetry and Cloud Logging."""

    def __init__(self) -> None:
        self._feedback_store: list[SessionFeedbackEntry] = []

    def record_feedback(
        self,
        session_id: str,
        caller_identity: str,
        skill_id: str,
        rating: float,
        rubric_scores: Optional[dict[str, float]] = None,
        qualitative_feedback: str = "",
        latency_ms: float = 0.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record an interaction or skill execution feedback entry.

        Publishes an OpenTelemetry span with telemetry attributes and logs structured feedback.
        """
        entry = SessionFeedbackEntry(
            session_id=session_id,
            caller_identity=caller_identity,
            skill_id=skill_id,
            rating=rating,
            rubric_scores=rubric_scores or {},
            qualitative_feedback=qualitative_feedback,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )
        self._feedback_store.append(entry)

        with tracer.start_as_current_span("telemetry/record_feedback") as span:
            span.set_attribute("feedback.session_id", session_id)
            span.set_attribute("feedback.caller_identity", caller_identity)
            span.set_attribute("feedback.skill_id", skill_id)
            span.set_attribute("feedback.rating", rating)
            span.set_attribute("feedback.latency_ms", latency_ms)
            span.set_attribute("feedback.rubric_scores_json", json.dumps(rubric_scores or {}))
            if qualitative_feedback:
                span.set_attribute("feedback.qualitative_length", len(qualitative_feedback))

        logger.info(
            "Recorded session feedback for %s on %s (rating: %.2f)",
            caller_identity,
            skill_id,
            rating,
        )

        return {
            "status": "recorded",
            "session_id": session_id,
            "skill_id": skill_id,
            "rating": rating,
            "total_feedback_entries": len(self._feedback_store),
            "timestamp": entry.timestamp,
        }

    def get_summary_metrics(self, skill_id: Optional[str] = None) -> dict[str, Any]:
        """Compute aggregated feedback metrics for quality flywheel tracking."""
        entries = self._feedback_store
        if skill_id:
            entries = [e for e in entries if e.skill_id == skill_id]

        if not entries:
            return {
                "total_entries": 0,
                "average_rating": 0.0,
                "rubric_averages": {},
            }

        avg_rating = sum(e.rating for e in entries) / len(entries)

        # Aggregate rubric averages
        rubric_totals: dict[str, float] = {}
        rubric_counts: dict[str, int] = {}
        for e in entries:
            for k, v in e.rubric_scores.items():
                rubric_totals[k] = rubric_totals.get(k, 0.0) + v
                rubric_counts[k] = rubric_counts.get(k, 0) + 1

        rubric_averages = {
            k: round(rubric_totals[k] / rubric_counts[k], 2)
            for k in rubric_totals
        }

        return {
            "total_entries": len(entries),
            "average_rating": round(avg_rating, 2),
            "rubric_averages": rubric_averages,
        }


feedback_recorder = SessionFeedbackRecorder()

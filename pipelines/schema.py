"""Ontology schema models for the NL2KG Triplification Pipeline."""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class GuidelineNode(BaseModel):
    """Represents a high-level architectural guideline or document."""

    guideline_id: str = Field(description="Unique guideline ID, e.g. DOC-01")
    title: str = Field(description="Title of the guideline")
    category: str = Field(description="Topic category (security, quality, runtime, etc.)")
    summary: str = Field(description="Executive summary of the guideline")
    source_url: str | None = Field(default=None, description="Original source link or doc reference")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PatternNode(BaseModel):
    """Represents a specific architectural design pattern."""

    pattern_id: str = Field(description="Unique pattern ID, e.g. PAT-ZAA")
    name: str = Field(description="Pattern name, e.g. Zero Ambient Authority")
    category: str = Field(description="Domain category")
    description: str = Field(description="Detailed explanation of the pattern")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TradeoffNode(BaseModel):
    """Represents an architectural tradeoff between competing approaches."""

    tradeoff_id: str = Field(description="Unique tradeoff ID, e.g. TRD-STATE-01")
    dimension: str = Field(description="Tradeoff dimension (latency, cost, complexity)")
    option_a: str = Field(description="First approach")
    option_b: str = Field(description="Second approach")
    analysis: str = Field(description="Tradeoff analysis and recommendation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AntipatternNode(BaseModel):
    """Represents an architectural anti-pattern or trap to avoid."""

    antipattern_id: str = Field(description="Unique anti-pattern ID, e.g. ANTI-AMBIENT-KEYS")
    name: str = Field(description="Anti-pattern name")
    hazard: str = Field(description="Specific risk or hazard")
    remedy: str = Field(description="Recommended mitigation or remedy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MitigatesEdge(BaseModel):
    """Edge linking a Pattern to an Antipattern it mitigates."""

    pattern_id: str
    antipattern_id: str
    rationale: str | None = None


class ImplementsEdge(BaseModel):
    """Edge linking a Guideline to a Pattern it implements or recommends."""

    guideline_id: str
    pattern_id: str
    notes: str | None = None


class TriplifiedGraph(BaseModel):
    """Complete graph container holding nodes and edges."""

    guidelines: list[GuidelineNode] = Field(default_factory=list)
    patterns: list[PatternNode] = Field(default_factory=list)
    tradeoffs: list[TradeoffNode] = Field(default_factory=list)
    antipatterns: list[AntipatternNode] = Field(default_factory=list)
    mitigates_edges: list[MitigatesEdge] = Field(default_factory=list)
    implements_edges: list[ImplementsEdge] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

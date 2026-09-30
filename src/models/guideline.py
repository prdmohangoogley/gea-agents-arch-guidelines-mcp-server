"""Domain models for architectural guidelines and patterns."""

from pydantic import BaseModel, Field


class Guideline(BaseModel):
    """Architectural guideline representation."""

    guideline_id: str = Field(description="Unique guideline ID, e.g. DOC-01")
    title: str = Field(description="Title of the guideline")
    category: str = Field(description="Category tag")
    summary: str = Field(description="Summary of the architectural recommendations")
    source_url: str | None = Field(default=None, description="Source reference link")


class Pattern(BaseModel):
    """Design pattern representation."""

    pattern_id: str = Field(description="Pattern identifier")
    name: str = Field(description="Pattern name")
    category: str = Field(description="Category")
    description: str = Field(description="Full pattern description")
    mitigates: list[str] = Field(default_factory=list, description="List of antipatterns mitigated")


class Antipattern(BaseModel):
    """Architectural pitfall or anti-pattern."""

    antipattern_id: str = Field(description="Anti-pattern identifier")
    name: str = Field(description="Name of the anti-pattern")
    hazard: str = Field(description="Operational or security risk")
    remedy: str = Field(description="Recommended solution")


class Tradeoff(BaseModel):
    """Architectural tradeoff dimension."""

    tradeoff_id: str = Field(description="Tradeoff identifier")
    dimension: str = Field(description="Tradeoff dimension")
    option_a: str = Field(description="First option")
    option_b: str = Field(description="Second option")
    analysis: str = Field(description="In-depth comparative analysis")


class GuidelineSearchResult(BaseModel):
    """Search result item."""

    guidelines: list[Guideline] = Field(default_factory=list)
    total_matches: int = Field(default=0)


class TradeoffEvaluation(BaseModel):
    """Comparative tradeoff matrix."""

    option_a: str
    option_b: str
    latency_impact: str
    complexity_impact: str
    security_posture: str
    recommendation: str

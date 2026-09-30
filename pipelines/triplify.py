"""Triplification engine transforming extracted document structures into typed graph nodes and edges."""

import hashlib
from typing import Any
from pipelines.schema import (
    AntipatternNode,
    GuidelineNode,
    ImplementsEdge,
    MitigatesEdge,
    PatternNode,
    TradeoffNode,
    TriplifiedGraph,
)


def generate_stable_id(prefix: str, text: str) -> str:
    """Generate a deterministic ID from text."""
    clean = text.strip().lower().replace(" ", "-")
    digest = hashlib.sha256(clean.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{digest}"


def triplify_document(doc: dict[str, Any]) -> TriplifiedGraph:
    """Convert an extracted document dictionary into a TriplifiedGraph."""
    graph = TriplifiedGraph()
    title = doc.get("title", "Untitled Guideline")
    guideline_id = generate_stable_id("DOC", title)

    # Derive category from tags or title
    tags = doc.get("tags", [])
    category = tags[0] if tags else "architecture"

    # Executive summary
    raw_text = doc.get("raw_text", "")
    summary = raw_text[:300].strip().replace("\n", " ") + "..."

    guideline = GuidelineNode(
        guideline_id=guideline_id,
        title=title,
        category=category,
        summary=summary,
        source_url=doc.get("file_path"),
    )
    graph.guidelines.append(guideline)

    # Detect patterns and antipatterns from sections
    sections = doc.get("sections", {})
    for section_name, section_body in sections.items():
        lower_name = section_name.lower()
        if "pattern" in lower_name or "practice" in lower_name:
            pat_id = generate_stable_id("PAT", section_name)
            pattern = PatternNode(
                pattern_id=pat_id,
                name=section_name,
                category=category,
                description=section_body[:400] if section_body else "Pattern details",
            )
            graph.patterns.append(pattern)
            graph.implements_edges.append(
                ImplementsEdge(guideline_id=guideline_id, pattern_id=pat_id, notes=f"Extracted from section {section_name}")
            )

        elif "antipattern" in lower_name or "pitfall" in lower_name or "hazard" in lower_name:
            anti_id = generate_stable_id("ANTI", section_name)
            antipattern = AntipatternNode(
                antipattern_id=anti_id,
                name=section_name,
                hazard=section_body[:300] if section_body else "Architectural pitfall",
                remedy="Apply recommended architectural patterns",
            )
            graph.antipatterns.append(antipattern)

        elif "tradeoff" in lower_name or "comparison" in lower_name:
            trd_id = generate_stable_id("TRD", section_name)
            tradeoff = TradeoffNode(
                tradeoff_id=trd_id,
                dimension="architecture-tradeoff",
                option_a="Managed Platform",
                option_b="Custom Build",
                analysis=section_body[:400] if section_body else "Tradeoff analysis",
            )
            graph.tradeoffs.append(tradeoff)

    return graph


def merge_graphs(graphs: list[TriplifiedGraph]) -> TriplifiedGraph:
    """Merge multiple TriplifiedGraph instances into a consolidated graph."""
    merged = TriplifiedGraph()
    seen_guidelines = set()
    seen_patterns = set()
    seen_antipatterns = set()
    seen_tradeoffs = set()

    for g in graphs:
        for item in g.guidelines:
            if item.guideline_id not in seen_guidelines:
                merged.guidelines.append(item)
                seen_guidelines.add(item.guideline_id)

        for item in g.patterns:
            if item.pattern_id not in seen_patterns:
                merged.patterns.append(item)
                seen_patterns.add(item.pattern_id)

        for item in g.antipatterns:
            if item.antipattern_id not in seen_antipatterns:
                merged.antipatterns.append(item)
                seen_antipatterns.add(item.antipattern_id)

        for item in g.tradeoffs:
            if item.tradeoff_id not in seen_tradeoffs:
                merged.tradeoffs.append(item)
                seen_tradeoffs.add(item.tradeoff_id)

        merged.implements_edges.extend(g.implements_edges)
        merged.mitigates_edges.extend(g.mitigates_edges)

    return merged

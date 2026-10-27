"""NL2KG (Natural Language to Knowledge Graph) Triplification Pipeline.

Converts OKF (Open Knowledge Format) architectural documents from GCS or local storage
into structured Knowledge Graph Triples (Nodes and Edges) for Cloud Spanner Graph
(Primary Operational Store) and Google BigQuery (Analytical & Vector Store).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
import yaml

from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("nl2kg_pipeline")

# ==============================================================================
# 1. Pydantic Models for Graph Ontology (Nodes and Edges)
# ==============================================================================

class GuidelineNode(BaseModel):
    """Operational and analytical guideline node."""
    guideline_id: str = Field(description="Unique ID e.g. DOC-01 or document_id")
    title: str = Field(description="Title of guideline")
    category: str = Field(default="general", description="Topic category (security, quality, runtime, etc.)")
    summary: str = Field(default="", description="Executive summary")
    source_url: str | None = Field(default=None, description="GCS URI or doc source")
    content_sha256: str | None = Field(default=None, description="SHA-256 digest of guideline content")
    version_tag: str | None = Field(default=None, description="Version tag e.g. GEAPL200_2026-09-30_124746")
    stale_after: datetime | None = Field(default=None, description="TTL expiry date timestamp")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PatternNode(BaseModel):
    """Architectural pattern node."""
    pattern_id: str = Field(description="Unique Pattern ID, e.g. PAT-ZAA")
    name: str = Field(description="Pattern name")
    category: str = Field(default="architecture", description="Domain category")
    description: str = Field(default="", description="Detailed pattern description")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AntipatternNode(BaseModel):
    """Architectural antipattern or hazard node."""
    antipattern_id: str = Field(description="Unique Antipattern ID, e.g. ANTI-HARDCODED-KEYS")
    name: str = Field(description="Antipattern name")
    hazard: str = Field(description="Specific risk or hazard")
    remedy: str = Field(default="", description="Mitigation or remedy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TradeoffNode(BaseModel):
    """Architectural tradeoff dimension node."""
    tradeoff_id: str = Field(description="Unique Tradeoff ID, e.g. TRD-01")
    dimension: str = Field(default="complexity", description="Tradeoff dimension")
    option_a: str = Field(description="First architectural option")
    option_b: str = Field(description="Second architectural option")
    analysis: str = Field(default="", description="Detailed tradeoff analysis")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FDERubricItemNode(BaseModel):
    """Represents an FDE Field-Readiness and Project Grading Rubric competency item."""
    rubric_id: str = Field(description="Unique rubric ID, e.g. RUBRIC-A-1 or RUBRIC-B-1-1")
    domain: str = Field(description="Domain category, e.g. Part A: Presentation & Advisory Rigor")
    sub_competency: str = Field(description="Specific sub-competency title")
    criteria_level_2: str = Field(description="Level 2 (production threshold) criteria")
    criteria_level_3: str | None = Field(default=None, description="Level 3 (exemplar) criteria")
    disqualifier_condition: str | None = Field(default=None, description="Disqualifier condition for Level 0")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EnforcesRubricEdge(BaseModel):
    """Edge linking a Guideline to an FDERubricItem it enforces or fulfills."""
    guideline_id: str
    rubric_id: str
    enforcement_level: str = "PRODUCTION_MANDATORY"
    notes: str | None = None


class GraphEdge(BaseModel):
    """Subject -> Predicate -> Object relationship edge."""
    source_id: str = Field(description="ID of the source node")
    source_type: Literal["Guideline", "Pattern", "Tradeoff", "Antipattern", "FDERubricItem"] = Field(
        description="Type of source node"
    )
    predicate: Literal["IMPLEMENTS", "MITIGATES", "RELATES_TO", "TRADES_OFF", "REQUIRES", "ENFORCES_RUBRIC"] = Field(
        description="Relationship predicate"
    )
    target_id: str = Field(description="ID of the target node")
    target_type: Literal["Guideline", "Pattern", "Tradeoff", "Antipattern", "FDERubricItem"] = Field(
        description="Type of target node"
    )
    rationale: str | None = Field(default=None, description="Context or explanation of relationship")


class ExtractedGraphPayload(BaseModel):
    """Container schema for graph extraction and database ingestion."""
    guidelines: list[GuidelineNode] = Field(default_factory=list)
    patterns: list[PatternNode] = Field(default_factory=list)
    antipatterns: list[AntipatternNode] = Field(default_factory=list)
    tradeoffs: list[TradeoffNode] = Field(default_factory=list)
    fde_rubric_items: list[FDERubricItemNode] = Field(default_factory=list)
    enforces_rubric_edges: list[EnforcesRubricEdge] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


def preserve_document_layout(raw_text: str) -> str:
    """Preprocess markdown document preserving lists, indentation, and tables."""
    lines = raw_text.splitlines()
    processed_lines: list[str] = []

    for line in lines:
        if not line.strip():
            processed_lines.append("")
            continue
        processed_lines.append(line.rstrip())

    return "\n".join(processed_lines)


def chunk_document_by_sections(
    markdown_text: str, max_chunk_chars: int = 12000
) -> list[dict[str, Any]]:
    """Segment layout-preserved markdown into semantically coherent sections."""
    sections = re.split(r"(?m)(?=^#{1,2}\s+)", markdown_text)
    chunks: list[dict[str, Any]] = []
    current_chunk = ""
    current_title = "Document Section"

    for section in sections:
        section = section.strip()
        if not section:
            continue

        title_match = re.match(r"^#{1,3}\s+(.+)$", section)
        if title_match:
            current_title = title_match.group(1).strip()

        if len(current_chunk) + len(section) > max_chunk_chars and current_chunk:
            chunks.append({"title": current_title, "text": current_chunk.strip()})
            current_chunk = section
        else:
            current_chunk += "\n\n" + section

    if current_chunk.strip():
        chunks.append({"title": current_title, "text": current_chunk.strip()})

    return chunks


def resolve_referential_integrity(payload: ExtractedGraphPayload) -> ExtractedGraphPayload:
    """Ensure no dangling edges exist in the graph by generating placeholder nodes if needed."""
    known_nodes: dict[str, str] = {}

    for g in payload.guidelines:
        known_nodes[g.guideline_id] = "Guideline"
    for p in payload.patterns:
        known_nodes[p.pattern_id] = "Pattern"
    for a in payload.antipatterns:
        known_nodes[a.antipattern_id] = "Antipattern"
    for t in payload.tradeoffs:
        known_nodes[t.tradeoff_id] = "Tradeoff"
    for f in payload.fde_rubric_items:
        known_nodes[f.rubric_id] = "FDERubricItem"

    for edge in payload.edges:
        if edge.source_id not in known_nodes:
            logger.info(f"Referential Integrity: Generating placeholder {edge.source_type} for '{edge.source_id}'")
            if edge.source_type == "Pattern":
                payload.patterns.append(
                    PatternNode(
                        pattern_id=edge.source_id,
                        name=f"Inferred Pattern ({edge.source_id})",
                        category="inferred",
                        description="Auto-generated placeholder node to resolve dangling edge reference.",
                    )
                )
            elif edge.source_type == "Guideline":
                payload.guidelines.append(
                    GuidelineNode(
                        guideline_id=edge.source_id,
                        title=f"Inferred Guideline ({edge.source_id})",
                        category="inferred",
                        summary="Auto-generated placeholder node to resolve dangling edge reference.",
                    )
                )
            known_nodes[edge.source_id] = edge.source_type

        if edge.target_id not in known_nodes:
            logger.info(f"Referential Integrity: Generating placeholder {edge.target_type} for '{edge.target_id}'")
            if edge.target_type == "Antipattern":
                payload.antipatterns.append(
                    AntipatternNode(
                        antipattern_id=edge.target_id,
                        name=f"Inferred Antipattern ({edge.target_id})",
                        hazard="Auto-generated placeholder hazard to resolve edge referential integrity.",
                        remedy="Consult security baseline documentation.",
                    )
                )
            elif edge.target_type == "Pattern":
                payload.patterns.append(
                    PatternNode(
                        pattern_id=edge.target_id,
                        name=f"Inferred Pattern ({edge.target_id})",
                        category="inferred",
                        description="Auto-generated placeholder node to resolve dangling edge reference.",
                    )
                )
            elif edge.target_type == "Tradeoff":
                payload.tradeoffs.append(
                    TradeoffNode(
                        tradeoff_id=edge.target_id,
                        dimension="inferred",
                        option_a="Standard",
                        option_b="Custom",
                        analysis="Auto-generated placeholder tradeoff.",
                    )
                )
            known_nodes[edge.target_id] = edge.target_type

    return payload


# ==============================================================================
# 2. Rubric Extraction & Domain Taxonomy
# ==============================================================================

DOMAIN_TAXONOMY = {
    "A": "Part A: Presentation & Advisory Rigor",
    "B.1": "Domain B.1: AI/ML Engineering",
    "B.2": "Domain B.2: Scoping and Documentation",
    "B.3": "Domain B.3: Security, Privacy & Compliance",
    "B.4": "Domain B.4: Reliability & Resilience",
    "B.5": "Domain B.5: Performance & Cost Optimization",
    "B.6": "Domain B.6: Operational Excellence",
    "B.7": "Domain B.7: Designing for Change",
}

def extract_fde_rubric_catalog(rubric_md_text: str) -> dict[str, FDERubricItemNode]:
    """Extract all 37 official FDE rubric competencies from Concept 00 or 57."""
    items: dict[str, FDERubricItemNode] = {}
    rows = re.findall(
        r"\|\s*\*\*([AB]\.[\d\.]+)\*\*\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|(?:\s*([^|]+)\|)?",
        rubric_md_text,
    )

    for r in rows:
        code = r[0].strip()
        title = r[1].strip()
        focus = r[2].strip()
        c2 = r[3].strip()
        c3 = r[4].strip() if len(r) > 4 and r[4] else None

        if code.startswith("A."):
            domain = DOMAIN_TAXONOMY["A"]
        else:
            prefix = ".".join(code.split(".")[:2])
            domain = DOMAIN_TAXONOMY.get(prefix, "Domain B: Engineering Excellence")

        code_hyphen = code.replace(".", "-")
        rubric_id = f"RUBRIC-{code_hyphen}"
        items[code] = FDERubricItemNode(
            rubric_id=rubric_id,
            domain=domain,
            sub_competency=title,
            criteria_level_2=c2,
            criteria_level_3=c3,
            disqualifier_condition=(
                "Score of 0 (Not Demonstrated) on any single metric triggers "
                "mandatory pause and 2-week re-presentation."
            ),
        )

    logger.info(f"Extracted {len(items)} official FDE Rubric competencies.")
    return items


# ==============================================================================
# 3. Layout Preservation Markdown Processor
# ==============================================================================

def preserve_document_layout(raw_text: str) -> str:
    """Preprocess markdown document preserving lists, indentation, and tables."""
    lines = raw_text.splitlines()
    processed_lines: list[str] = []

    for line in lines:
        if not line.strip():
            processed_lines.append("")
            continue
        processed_lines.append(line.rstrip())

    return "\n".join(processed_lines)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter and return (metadata, body)."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
                return meta, parts[2]
            except Exception as e:
                logger.warning(f"Failed parsing YAML frontmatter: {e}")
    return {}, content


def parse_iso_datetime(dt_val: Any) -> datetime | None:
    """Safely parse various datetime formats into timezone-aware UTC datetime."""
    if not dt_val:
        return None
    if isinstance(dt_val, datetime):
        if dt_val.tzinfo is None:
            return dt_val.replace(tzinfo=timezone.utc)
        return dt_val
    if isinstance(dt_val, str):
        try:
            # Handle standard ISO / RFC3339
            cleaned = dt_val.replace("Z", "+00:00")
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None
    return None


# ==============================================================================
# 4. Document Triplifier (Heuristic & Deterministic)
# ==============================================================================

def triplify_document(
    doc_path: Path,
    content: str,
    rubric_catalog: dict[str, FDERubricItemNode],
    default_version: str = "GEAPL200_2026-09-30_124746",
) -> ExtractedGraphPayload:
    """Triplify an OKF v0.2 markdown document into typed nodes and edges."""
    payload = ExtractedGraphPayload()
    meta, body = parse_frontmatter(content)

    doc_id = meta.get("document_id", doc_path.stem)
    title = meta.get("title", doc_path.stem.replace("-", " ").title())
    category = meta.get("tags", ["architecture"])[0] if meta.get("tags") else "architecture"
    summary = meta.get("description", body[:300].strip().replace("\n", " ") + "...")
    source_url = meta.get("sources", [str(doc_path)])[0] if meta.get("sources") else str(doc_path)
    content_sha = meta.get("content_sha256", hashlib.sha256(content.encode("utf-8")).hexdigest())
    version_tag = meta.get("version_tag", default_version)
    stale_after_raw = meta.get("stale_after")
    stale_after = parse_iso_datetime(stale_after_raw)
    created_at = parse_iso_datetime(meta.get("timestamp")) or datetime.now(timezone.utc)

    # 1. Guideline Node
    guideline = GuidelineNode(
        guideline_id=doc_id[:64],
        title=title[:256],
        category=category[:64],
        summary=summary,
        source_url=source_url[:512],
        content_sha256=content_sha[:64],
        version_tag=version_tag[:64],
        stale_after=stale_after,
        created_at=created_at,
    )
    payload.guidelines.append(guideline)

    # 2. Rubric Enforcement Edges
    sec_match = re.search(
        r"## (?:FDE Project Grading Rubric Enforcement|\d+\.\s*Enforceable FDE Field-Readiness).*",
        content,
        re.DOTALL,
    )
    sec_text = sec_match.group(0) if sec_match else ""
    seen_codes: set[str] = set()

    # Bullet points format: - **A.1 Strategic Delivery...**: Notes
    for m in re.finditer(r"-\s*\*\*([AB]\.[\d\.]+)\s+([^:*]+):?\*\*:?\s*(.*)", sec_text):
        c_code = m.group(1).strip()
        c_note = m.group(3).strip()[:500]
        if c_code in rubric_catalog and c_code not in seen_codes:
            seen_codes.add(c_code)
            rubric_id = rubric_catalog[c_code].rubric_id
            payload.enforces_rubric_edges.append(
                EnforcesRubricEdge(
                    guideline_id=doc_id[:64],
                    rubric_id=rubric_id[:64],
                    enforcement_level="PRODUCTION_MANDATORY",
                    notes=c_note,
                )
            )

    # Table / Inline mentions: Part A.1, Part B.2.1
    for m in re.finditer(r"Part\s+([AB]\.[\d\.]+)", sec_text):
        c_code = m.group(1).strip()
        if c_code in rubric_catalog and c_code not in seen_codes:
            seen_codes.add(c_code)
            rubric_id = rubric_catalog[c_code].rubric_id
            sub_comp = rubric_catalog[c_code].sub_competency
            payload.enforces_rubric_edges.append(
                EnforcesRubricEdge(
                    guideline_id=doc_id[:64],
                    rubric_id=rubric_id[:64],
                    enforcement_level="PRODUCTION_MANDATORY",
                    notes=f"Enforces {sub_comp} per module requirements",
                )
            )

    # 3. Architectural Patterns & Implements Edges
    p_matches = re.findall(r"#{2,4}\s+(?:Decision|Pattern|Principle)\s*[\d—\-:]*\s*([^\n]+)", body, re.IGNORECASE)
    doc_patterns: list[str] = []
    for p_name in p_matches:
        p_name = p_name.strip()
        if len(p_name) > 3 and not p_name.startswith("#"):
            p_id = f"PAT-{hashlib.sha256(p_name.encode()).hexdigest()[:8].upper()}"
            pattern = PatternNode(
                pattern_id=p_id[:64],
                name=p_name[:512],
                category=category[:64],
                description=f"Architectural pattern defined in {title}",
            )
            payload.patterns.append(pattern)
            doc_patterns.append(p_id)
            payload.edges.append(
                GraphEdge(
                    source_id=doc_id[:64],
                    source_type="Guideline",
                    predicate="IMPLEMENTS",
                    target_id=p_id[:64],
                    target_type="Pattern",
                    rationale=f"Defined in {title}",
                )
            )

    # 4. Antipatterns & Mitigates Edges
    anti_headers = re.findall(r"#{2,4}\s+Antipattern\s*[\d—\-:]*\s*([^\n]+)", body, re.IGNORECASE)
    for a_name in anti_headers:
        a_name = a_name.strip()
        if len(a_name) > 3:
            a_id = f"ANTI-{hashlib.sha256(a_name.encode()).hexdigest()[:8].upper()}"
            antipattern = AntipatternNode(
                antipattern_id=a_id[:64],
                name=a_name[:512],
                hazard=f"Hazard identified in {title}",
                remedy="Apply corresponding architectural pattern and rubric guardrail",
            )
            payload.antipatterns.append(antipattern)
            if doc_patterns:
                payload.edges.append(
                    GraphEdge(
                        source_id=doc_patterns[-1][:64],
                        source_type="Pattern",
                        predicate="MITIGATES",
                        target_id=a_id[:64],
                        target_type="Antipattern",
                        rationale=f"Mitigates {a_name}",
                    )
                )

    anti_sec = re.search(
        r"## .*?(?:Antipattern|Pitfall|Hazard|Failure Mode).*?\n(.*?)(?=\n## |\Z)",
        body,
        re.DOTALL | re.IGNORECASE,
    )
    if anti_sec:
        a_matches = re.findall(r"-\s*\*\*([^*]+)\*\*", anti_sec.group(1))
        for a_name in a_matches:
            a_name = a_name.strip()
            if len(a_name) > 3:
                a_id = f"ANTI-{hashlib.sha256(a_name.encode()).hexdigest()[:8].upper()}"
                antipattern = AntipatternNode(
                    antipattern_id=a_id[:64],
                    name=a_name[:512],
                    hazard=f"Hazard identified in {title}",
                    remedy="Apply corresponding architectural pattern and rubric guardrail",
                )
                payload.antipatterns.append(antipattern)
                if doc_patterns:
                    payload.edges.append(
                        GraphEdge(
                            source_id=doc_patterns[-1][:64],
                            source_type="Pattern",
                            predicate="MITIGATES",
                            target_id=a_id[:64],
                            target_type="Antipattern",
                            rationale=f"Mitigates {a_name}",
                        )
                    )

    # 5. Tradeoffs
    tradeoff_rows = re.findall(
        r"\|\s*([^|\n]+(?:vs\.?|versus)[^|\n]+)\s*\|\s*([^|\n]+)\s*\|\s*([^|\n]+)\s*\|",
        body,
        re.IGNORECASE,
    )
    for t_row in tradeoff_rows:
        dim = t_row[0].strip().replace("*", "")
        opt_a = t_row[1].strip().replace("*", "")
        opt_b = t_row[2].strip().replace("*", "")
        if len(dim) > 3 and len(opt_a) > 2 and len(opt_b) > 2 and "---" not in dim:
            t_id = f"TRD-{hashlib.sha256(f'{dim}_{opt_a}_{opt_b}'.encode()).hexdigest()[:8].upper()}"
            tradeoff = TradeoffNode(
                tradeoff_id=t_id[:64],
                dimension=dim[:64],
                option_a=opt_a[:128],
                option_b=opt_b[:128],
                analysis=f"Evaluated in {title} under dimensions {dim}",
            )
            payload.tradeoffs.append(tradeoff)

    return payload


# ==============================================================================
# 5. Referential Integrity Resolver
# ==============================================================================

def resolve_referential_integrity(payload: ExtractedGraphPayload) -> ExtractedGraphPayload:
    """Ensure no dangling edges exist in the graph."""
    known_nodes: dict[str, str] = {}

    for g in payload.guidelines:
        known_nodes[g.guideline_id] = "Guideline"
    for p in payload.patterns:
        known_nodes[p.pattern_id] = "Pattern"
    for a in payload.antipatterns:
        known_nodes[a.antipattern_id] = "Antipattern"
    for t in payload.tradeoffs:
        known_nodes[t.tradeoff_id] = "Tradeoff"
    for r in payload.fde_rubric_items:
        known_nodes[r.rubric_id] = "FDERubricItem"

    # Filter out any rubric enforcement edges referencing nonexistent rubric items or guidelines
    valid_enforces: list[EnforcesRubricEdge] = []
    for edge in payload.enforces_rubric_edges:
        if edge.guideline_id in known_nodes and edge.rubric_id in known_nodes:
            valid_enforces.append(edge)
        else:
            logger.warning(
                f"Referential Integrity: Dropping dangling EnforcesRubricEdge "
                f"({edge.guideline_id} -> {edge.rubric_id})"
            )
    payload.enforces_rubric_edges = valid_enforces

    # Check edges
    valid_edges: list[GraphEdge] = []
    for edge in payload.edges:
        # Check source node
        if edge.source_id not in known_nodes:
            if edge.source_type == "Pattern":
                payload.patterns.append(
                    PatternNode(
                        pattern_id=edge.source_id,
                        name=f"Inferred Pattern ({edge.source_id})",
                        category="inferred",
                        description="Auto-generated placeholder node to resolve dangling edge reference.",
                    )
                )
                known_nodes[edge.source_id] = "Pattern"
            elif edge.source_type == "Guideline":
                payload.guidelines.append(
                    GuidelineNode(
                        guideline_id=edge.source_id,
                        title=f"Inferred Guideline ({edge.source_id})",
                        category="inferred",
                        summary="Auto-generated placeholder node to resolve dangling edge reference.",
                    )
                )
                known_nodes[edge.source_id] = "Guideline"

        # Check target node
        if edge.target_id not in known_nodes:
            if edge.target_type == "Antipattern":
                payload.antipatterns.append(
                    AntipatternNode(
                        antipattern_id=edge.target_id,
                        name=f"Inferred Antipattern ({edge.target_id})",
                        hazard="Auto-generated placeholder hazard to resolve edge referential integrity.",
                        remedy="Consult security baseline documentation.",
                    )
                )
                known_nodes[edge.target_id] = "Antipattern"
            elif edge.target_type == "Pattern":
                payload.patterns.append(
                    PatternNode(
                        pattern_id=edge.target_id,
                        name=f"Inferred Pattern ({edge.target_id})",
                        category="inferred",
                        description="Auto-generated placeholder node to resolve dangling edge reference.",
                    )
                )
                known_nodes[edge.target_id] = "Pattern"

        valid_edges.append(edge)

    payload.edges = valid_edges
    return payload


# ==============================================================================
# 6. Batch Hydration (Spanner Graph & BigQuery)
# ==============================================================================

class GraphBatchHydrator:
    """Hydrates Spanner Graph and BigQuery in atomic batches."""

    def __init__(
        self,
        project_id: str,
        spanner_instance_id: str,
        spanner_database_name: str,
        bq_dataset_id: str,
        batch_size: int = 50,
        dry_run: bool = False,
    ):
        self.project_id = project_id
        self.spanner_instance_id = spanner_instance_id
        self.spanner_database_name = spanner_database_name
        self.bq_dataset_id = bq_dataset_id
        self.batch_size = batch_size
        self.dry_run = dry_run

    def hydrate_spanner(self, payload: ExtractedGraphPayload) -> int:
        """Insert or update nodes and edges into Cloud Spanner Graph."""
        if self.dry_run:
            total = (
                len(payload.guidelines)
                + len(payload.fde_rubric_items)
                + len(payload.enforces_rubric_edges)
                + len(payload.patterns)
                + len(payload.antipatterns)
                + len(payload.tradeoffs)
                + len(payload.edges)
            )
            logger.info(f"[DRY-RUN] Spanner Hydration: Prepared {total} mutations across tables.")
            return total

        try:
            from google.cloud import spanner

            client = spanner.Client(project=self.project_id)
            instance = client.instance(self.spanner_instance_id)
            database = instance.database(self.spanner_database_name)

            total_mutations = 0

            # 1. Guidelines
            for i in range(0, len(payload.guidelines), self.batch_size):
                batch = payload.guidelines[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="Guidelines",
                        columns=[
                            "guideline_id",
                            "title",
                            "category",
                            "summary",
                            "source_url",
                            "content_sha256",
                            "version_tag",
                            "stale_after",
                            "created_at",
                        ],
                        values=[
                            [
                                g.guideline_id[:64],
                                g.title[:256],
                                g.category[:64],
                                g.summary,
                                (g.source_url or "")[:512],
                                (g.content_sha256 or "")[:64],
                                (g.version_tag or "")[:64],
                                g.stale_after,
                                spanner.COMMIT_TIMESTAMP,
                            ]
                            for g in batch
                        ],
                    )
                total_mutations += len(batch)

            # 2. FDERubricItems
            for i in range(0, len(payload.fde_rubric_items), self.batch_size):
                batch = payload.fde_rubric_items[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="FDERubricItems",
                        columns=[
                            "rubric_id",
                            "domain",
                            "sub_competency",
                            "criteria_level_2",
                            "criteria_level_3",
                            "disqualifier_condition",
                            "created_at",
                        ],
                        values=[
                            [
                                r.rubric_id[:64],
                                r.domain[:128],
                                r.sub_competency[:256],
                                r.criteria_level_2,
                                r.criteria_level_3 or "",
                                r.disqualifier_condition or "",
                                spanner.COMMIT_TIMESTAMP,
                            ]
                            for r in batch
                        ],
                    )
                total_mutations += len(batch)

            # 3. GuidelineEnforcesRubric Edges
            for i in range(0, len(payload.enforces_rubric_edges), self.batch_size):
                batch = payload.enforces_rubric_edges[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="GuidelineEnforcesRubric",
                        columns=["guideline_id", "rubric_id", "enforcement_level", "notes"],
                        values=[
                            [e.guideline_id[:64], e.rubric_id[:64], e.enforcement_level[:64], e.notes or ""]
                            for e in batch
                        ],
                    )
                total_mutations += len(batch)

            # 4. Patterns
            for i in range(0, len(payload.patterns), self.batch_size):
                batch = payload.patterns[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="Patterns",
                        columns=["pattern_id", "name", "category", "description", "created_at"],
                        values=[
                            [
                                p.pattern_id[:64],
                                p.name[:512],
                                p.category[:64],
                                p.description,
                                spanner.COMMIT_TIMESTAMP,
                            ]
                            for p in batch
                        ],
                    )
                total_mutations += len(batch)

            # 5. Antipatterns
            for i in range(0, len(payload.antipatterns), self.batch_size):
                batch = payload.antipatterns[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="Antipatterns",
                        columns=["antipattern_id", "name", "hazard", "remedy", "created_at"],
                        values=[
                            [
                                a.antipattern_id[:64],
                                a.name[:512],
                                a.hazard,
                                a.remedy,
                                spanner.COMMIT_TIMESTAMP,
                            ]
                            for a in batch
                        ],
                    )
                total_mutations += len(batch)

            # 6. Tradeoffs
            for i in range(0, len(payload.tradeoffs), self.batch_size):
                batch = payload.tradeoffs[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="Tradeoffs",
                        columns=["tradeoff_id", "dimension", "option_a", "option_b", "analysis", "created_at"],
                        values=[
                            [
                                t.tradeoff_id[:64],
                                t.dimension[:64],
                                t.option_a[:128],
                                t.option_b[:128],
                                t.analysis,
                                spanner.COMMIT_TIMESTAMP,
                            ]
                            for t in batch
                        ],
                    )
                total_mutations += len(batch)

            # 7. GuidelineImplementsPattern Edges
            implements_edges = [e for e in payload.edges if e.predicate == "IMPLEMENTS"]
            for i in range(0, len(implements_edges), self.batch_size):
                batch = implements_edges[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="GuidelineImplementsPattern",
                        columns=["guideline_id", "pattern_id", "notes"],
                        values=[
                            [e.source_id[:64], e.target_id[:64], e.rationale or ""]
                            for e in batch
                        ],
                    )
                total_mutations += len(batch)

            # 8. PatternMitigatesAntipattern Edges
            mitigates_edges = [e for e in payload.edges if e.predicate == "MITIGATES"]
            for i in range(0, len(mitigates_edges), self.batch_size):
                batch = mitigates_edges[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="PatternMitigatesAntipattern",
                        columns=["pattern_id", "antipattern_id", "rationale"],
                        values=[
                            [e.source_id[:64], e.target_id[:64], e.rationale or ""]
                            for e in batch
                        ],
                    )
                total_mutations += len(batch)

            logger.info(f"Spanner Batch Hydration successful: {total_mutations} total mutations committed.")
            return total_mutations

        except Exception as e:
            logger.error(f"Spanner Batch Hydration encountered error: {e}")
            raise

    def hydrate_bigquery(self, payload: ExtractedGraphPayload) -> int:
        """Stream or load extracted nodes into BigQuery tables."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] BigQuery Federation: Ready to insert into {self.bq_dataset_id}.")
            return len(payload.guidelines)

        try:
            from google.cloud import bigquery

            client = bigquery.Client(project=self.project_id)
            total_rows = 0

            # 1. Guidelines
            if payload.guidelines:
                table_id = f"{self.project_id}.{self.bq_dataset_id}.guidelines"
                rows = [
                    {
                        "guideline_id": g.guideline_id,
                        "title": g.title,
                        "category": g.category,
                        "summary": g.summary,
                        "source_url": g.source_url,
                        "content_sha256": g.content_sha256,
                        "version_tag": g.version_tag,
                        "stale_after": g.stale_after.isoformat() if g.stale_after else None,
                        "created_at": g.created_at.isoformat(),
                    }
                    for g in payload.guidelines
                ]
                errors = client.insert_rows_json(table_id, rows)
                if errors:
                    logger.warning(f"BigQuery insert errors on guidelines: {errors}")
                total_rows += len(rows)

            # 2. FDE Rubric Items
            if payload.fde_rubric_items:
                table_id = f"{self.project_id}.{self.bq_dataset_id}.fde_rubric_items"
                rows = [
                    {
                        "rubric_id": r.rubric_id,
                        "domain": r.domain,
                        "sub_competency": r.sub_competency,
                        "criteria_level_2": r.criteria_level_2,
                        "criteria_level_3": r.criteria_level_3,
                        "disqualifier_condition": r.disqualifier_condition,
                        "created_at": r.created_at.isoformat(),
                    }
                    for r in payload.fde_rubric_items
                ]
                errors = client.insert_rows_json(table_id, rows)
                if errors:
                    logger.warning(f"BigQuery insert errors on fde_rubric_items: {errors}")
                total_rows += len(rows)

            # 3. Guideline Enforces Rubric Edges
            if payload.enforces_rubric_edges:
                table_id = f"{self.project_id}.{self.bq_dataset_id}.guideline_enforces_rubric"
                rows = [
                    {
                        "guideline_id": e.guideline_id,
                        "rubric_id": e.rubric_id,
                        "enforcement_level": e.enforcement_level,
                        "notes": e.notes or "",
                    }
                    for e in payload.enforces_rubric_edges
                ]
                errors = client.insert_rows_json(table_id, rows)
                if errors:
                    logger.warning(f"BigQuery insert errors on guideline_enforces_rubric: {errors}")
                total_rows += len(rows)

            # 4. Patterns
            if payload.patterns:
                table_id = f"{self.project_id}.{self.bq_dataset_id}.patterns"
                rows = [
                    {
                        "pattern_id": p.pattern_id,
                        "name": p.name,
                        "category": p.category,
                        "description": p.description,
                        "created_at": p.created_at.isoformat(),
                    }
                    for p in payload.patterns
                ]
                client.insert_rows_json(table_id, rows)
                total_rows += len(rows)

            # 5. Antipatterns
            if payload.antipatterns:
                table_id = f"{self.project_id}.{self.bq_dataset_id}.antipatterns"
                rows = [
                    {
                        "antipattern_id": a.antipattern_id,
                        "name": a.name,
                        "hazard": a.hazard,
                        "remedy": a.remedy,
                        "created_at": a.created_at.isoformat(),
                    }
                    for a in payload.antipatterns
                ]
                client.insert_rows_json(table_id, rows)
                total_rows += len(rows)

            # 6. Tradeoffs
            if payload.tradeoffs:
                table_id = f"{self.project_id}.{self.bq_dataset_id}.tradeoffs"
                rows = [
                    {
                        "tradeoff_id": t.tradeoff_id,
                        "dimension": t.dimension,
                        "option_a": t.option_a,
                        "option_b": t.option_b,
                        "analysis": t.analysis,
                        "created_at": t.created_at.isoformat(),
                    }
                    for t in payload.tradeoffs
                ]
                client.insert_rows_json(table_id, rows)
                total_rows += len(rows)

            # 7. GuidelineImplementsPattern Edges
            implements_edges = [e for e in payload.edges if e.predicate == "IMPLEMENTS"]
            if implements_edges:
                table_id = f"{self.project_id}.{self.bq_dataset_id}.guideline_implements_pattern"
                rows = [
                    {
                        "guideline_id": e.source_id,
                        "pattern_id": e.target_id,
                        "notes": e.rationale or "",
                    }
                    for e in implements_edges
                ]
                client.insert_rows_json(table_id, rows)
                total_rows += len(rows)

            # 8. PatternMitigatesAntipattern Edges
            mitigates_edges = [e for e in payload.edges if e.predicate == "MITIGATES"]
            if mitigates_edges:
                table_id = f"{self.project_id}.{self.bq_dataset_id}.pattern_mitigates_antipattern"
                rows = [
                    {
                        "pattern_id": e.source_id,
                        "antipattern_id": e.target_id,
                        "rationale": e.rationale or "",
                    }
                    for e in mitigates_edges
                ]
                client.insert_rows_json(table_id, rows)
                total_rows += len(rows)

            logger.info(f"BigQuery Hydration successful: {total_rows} rows streamed.")
            return total_rows

        except Exception as e:
            logger.warning(f"BigQuery Hydration skipped or encountered error: {e}")
            return 0


# ==============================================================================
# 7. Incremental Synchronization & Checksum Tracking
# ==============================================================================

class CheckpointTracker:
    """Manages document checksums to guarantee Zero-Duplicate writes."""

    def __init__(self, checkpoint_path: Path):
        self.checkpoint_path = checkpoint_path
        self._state: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.checkpoint_path.exists():
            try:
                self._state = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            except Exception:
                self._state = {}

    def save(self) -> None:
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    def should_process(self, doc_id: str, checksum: str) -> bool:
        """Return True if document is new or changed since last triplification."""
        record = self._state.get(doc_id)
        if not record:
            return True
        if record.get("checksum") != checksum:
            return True
        return False

    def mark_completed(self, doc_id: str, checksum: str, node_count: int, edge_count: int) -> None:
        self._state[doc_id] = {
            "checksum": checksum,
            "synced_at": datetime.now(timezone.utc).isoformat(),
            "nodes": node_count,
            "edges": edge_count,
        }
        self.save()


# ==============================================================================
# 8. Orchestrator
# ==============================================================================

def run_pipeline(
    gcs_bucket_name: str | None = None,
    local_dir: Path | None = None,
    project_id: str = "fivedaysai-prd-sandbox-317383",
    spanner_instance_id: str = "gea-arch-guidelines-spanner",
    spanner_database_name: str = "arch_guidelines_graph",
    bq_dataset_id: str = "gea_arch_guidelines_analytics",
    checkpoint_file: Path = Path(".sync/checkpoints.json"),
    dry_run: bool = False,
    force_sync: bool = False,
) -> ExtractedGraphPayload:
    """Run end-to-end NL2KG pipeline over local directory or GCS bucket."""
    logger.info("Starting NL2KG Triplification Pipeline...")
    tracker = CheckpointTracker(checkpoint_file)
    consolidated_graph = ExtractedGraphPayload()
    processed_items: list[tuple[str, str, int, int]] = []

    documents_to_process: list[dict[str, Any]] = []

    # 1. Discover documents from local directory first, or GCS bucket
    if local_dir and local_dir.exists():
        files = sorted(list(local_dir.glob("*.md")) + list(local_dir.glob("**/*.md")))
        logger.info(f"Discovered {len(files)} markdown documents in local directory {local_dir}")
        for f in files:
            content = f.read_text(encoding="utf-8")
            checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
            doc_id = str(f.relative_to(local_dir))
            if force_sync or tracker.should_process(doc_id, checksum):
                documents_to_process.append(
                    {"path": f, "uri": str(f), "content": content, "checksum": checksum, "id": doc_id}
                )
            else:
                logger.info(f"Skipping unchanged local file: {doc_id}")

    elif gcs_bucket_name:
        try:
            from google.cloud import storage

            client = storage.Client(project=project_id)
            bucket = client.bucket(gcs_bucket_name)
            blobs = list(bucket.list_blobs(prefix="okf/concepts/"))
            logger.info(f"Discovered {len(blobs)} objects in GCS bucket gs://{gcs_bucket_name}/okf/concepts/")

            for b in blobs:
                if b.name.endswith(".md"):
                    content = b.download_as_text()
                    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    if force_sync or tracker.should_process(b.name, checksum):
                        documents_to_process.append(
                            {
                                "path": Path(b.name),
                                "uri": f"gs://{gcs_bucket_name}/{b.name}",
                                "content": content,
                                "checksum": checksum,
                                "id": b.name,
                            }
                        )
        except Exception as e:
            logger.warning(f"GCS listing failed: {e}")

    if not documents_to_process:
        logger.info("All documents are up-to-date with zero changes detected. Zero duplicate writes needed.")
        return consolidated_graph

    logger.info(f"Total documents queued for triplification: {len(documents_to_process)}")

    # 2. Extract Canonical FDE Rubric Items
    rubric_doc = next(
        (d for d in documents_to_process if "00-fde-field-readiness" in d["id"] or "00-fde-field-readiness" in str(d["path"])),
        None,
    )
    if not rubric_doc and local_dir:
        cand = local_dir / "00-fde-field-readiness-and-grading-rubric.md"
        if cand.exists():
            rubric_doc = {"path": cand, "content": cand.read_text(encoding="utf-8")}

    rubric_catalog: dict[str, FDERubricItemNode] = {}
    if rubric_doc:
        rubric_catalog = extract_fde_rubric_catalog(rubric_doc["content"])
        consolidated_graph.fde_rubric_items = list(rubric_catalog.values())

    # 3. Triplify Each Document
    for item in documents_to_process:
        doc_payload = triplify_document(
            doc_path=item["path"],
            content=item["content"],
            rubric_catalog=rubric_catalog,
        )

        consolidated_graph.guidelines.extend(doc_payload.guidelines)
        consolidated_graph.patterns.extend(doc_payload.patterns)
        consolidated_graph.antipatterns.extend(doc_payload.antipatterns)
        consolidated_graph.tradeoffs.extend(doc_payload.tradeoffs)
        consolidated_graph.enforces_rubric_edges.extend(doc_payload.enforces_rubric_edges)
        consolidated_graph.edges.extend(doc_payload.edges)

        n_nodes = (
            len(doc_payload.guidelines)
            + len(doc_payload.patterns)
            + len(doc_payload.antipatterns)
            + len(doc_payload.tradeoffs)
        )
        n_edges = len(doc_payload.enforces_rubric_edges) + len(doc_payload.edges)
        processed_items.append((item["id"], item["checksum"], n_nodes, n_edges))

    # 4. Referential Integrity & Deduplication
    consolidated_graph.guidelines = list({g.guideline_id: g for g in consolidated_graph.guidelines}.values())
    consolidated_graph.patterns = list({p.pattern_id: p for p in consolidated_graph.patterns}.values())
    consolidated_graph.antipatterns = list({a.antipattern_id: a for a in consolidated_graph.antipatterns}.values())
    consolidated_graph.tradeoffs = list({t.tradeoff_id: t for t in consolidated_graph.tradeoffs}.values())
    consolidated_graph.fde_rubric_items = list({r.rubric_id: r for r in consolidated_graph.fde_rubric_items}.values())

    # Deduplicate edges
    seen_enforces = set()
    unique_enforces = []
    for e in consolidated_graph.enforces_rubric_edges:
        key = (e.guideline_id, e.rubric_id)
        if key not in seen_enforces:
            seen_enforces.add(key)
            unique_enforces.append(e)
    consolidated_graph.enforces_rubric_edges = unique_enforces

    seen_edges = set()
    unique_edges = []
    for e in consolidated_graph.edges:
        key = (e.source_id, e.predicate, e.target_id)
        if key not in seen_edges:
            seen_edges.add(key)
            unique_edges.append(e)
    consolidated_graph.edges = unique_edges

    consolidated_graph = resolve_referential_integrity(consolidated_graph)

    # 5. Batch Hydration to Spanner Graph & BigQuery
    hydrator = GraphBatchHydrator(
        project_id=project_id,
        spanner_instance_id=spanner_instance_id,
        spanner_database_name=spanner_database_name,
        bq_dataset_id=bq_dataset_id,
        batch_size=50,
        dry_run=dry_run,
    )

    hydrator.hydrate_spanner(consolidated_graph)
    hydrator.hydrate_bigquery(consolidated_graph)

    # 6. Save Checkpoints
    if not dry_run:
        for doc_id, checksum, n_nodes, n_edges in processed_items:
            tracker.mark_completed(doc_id, checksum, n_nodes, n_edges)

    logger.info("NL2KG Triplification Pipeline completed successfully!")
    logger.info(
        f"Summary: {len(consolidated_graph.guidelines)} Guidelines, "
        f"{len(consolidated_graph.fde_rubric_items)} FDE Rubric Items, "
        f"{len(consolidated_graph.enforces_rubric_edges)} GuidelineEnforcesRubric Edges, "
        f"{len(consolidated_graph.patterns)} Patterns, "
        f"{len(consolidated_graph.antipatterns)} Antipatterns, "
        f"{len(consolidated_graph.tradeoffs)} Tradeoffs, "
        f"{len(consolidated_graph.edges)} Implements/Mitigates Edges."
    )

    return consolidated_graph


def main() -> None:
    """CLI Entrypoint for NL2KG pipeline."""
    parser = argparse.ArgumentParser(description="NL2KG Triplification Pipeline")
    parser.add_argument("--gcs-bucket", default="gea_agent_development_architectural_best_practices_1790796607", help="Source GCS bucket")
    parser.add_argument("--local-dir", type=Path, default=Path("okf/concepts"), help="Local documents directory")
    parser.add_argument("--project-id", default="fivedaysai-prd-sandbox-317383", help="Google Cloud Project ID")
    parser.add_argument("--spanner-instance", default="gea-arch-guidelines-spanner", help="Spanner Instance ID")
    parser.add_argument("--spanner-database", default="arch_guidelines_graph", help="Spanner Database Name")
    parser.add_argument("--bq-dataset", default="gea_arch_guidelines_analytics", help="BigQuery Dataset ID")
    parser.add_argument("--checkpoint-file", type=Path, default=Path(".sync/checkpoints.json"), help="State file for incremental sync")
    parser.add_argument("--dry-run", action="store_true", help="Perform extraction without database writes")
    parser.add_argument("--force-sync", action="store_true", help="Force full resync ignoring checkpoints")

    args = parser.parse_args()

    run_pipeline(
        gcs_bucket_name=args.gcs_bucket,
        local_dir=args.local_dir,
        project_id=args.project_id,
        spanner_instance_id=args.spanner_instance,
        spanner_database_name=args.spanner_database,
        bq_dataset_id=args.bq_dataset,
        checkpoint_file=args.checkpoint_file,
        dry_run=args.dry_run,
        force_sync=args.force_sync,
    )


if __name__ == "__main__":
    main()

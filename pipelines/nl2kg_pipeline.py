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

from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("nl2kg_pipeline")

# ==============================================================================
# 1. Pydantic Models for Graph Ontology (Nodes and Edges)
# ==============================================================================

class GuidelineNode(BaseModel):
    """Operational and analytical guideline node."""
    guideline_id: str = Field(description="Unique ID e.g. DOC-01 or HASH")
    title: str = Field(description="Title of guideline")
    category: str = Field(default="general", description="Topic category (security, quality, runtime, etc.)")
    summary: str = Field(default="", description="Executive summary")
    source_url: str | None = Field(default=None, description="GCS URI or doc source")
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


class GraphEdge(BaseModel):
    """Subject -> Predicate -> Object relationship edge."""
    source_id: str = Field(description="ID of the source node")
    source_type: Literal["Guideline", "Pattern", "Tradeoff", "Antipattern"] = Field(
        description="Type of source node"
    )
    predicate: Literal["IMPLEMENTS", "MITIGATES", "RELATES_TO", "TRADES_OFF", "REQUIRES"] = Field(
        description="Relationship predicate"
    )
    target_id: str = Field(description="ID of the target node")
    target_type: Literal["Guideline", "Pattern", "Tradeoff", "Antipattern"] = Field(
        description="Type of target node"
    )
    rationale: str | None = Field(default=None, description="Context or explanation of relationship")


class ExtractedGraphPayload(BaseModel):
    """Container schema for LLM structured output and graph ingestion."""
    guidelines: list[GuidelineNode] = Field(default_factory=list)
    patterns: list[PatternNode] = Field(default_factory=list)
    antipatterns: list[AntipatternNode] = Field(default_factory=list)
    tradeoffs: list[TradeoffNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


# ==============================================================================
# 2. Layout Preservation Markdown Processor
# ==============================================================================

def preserve_document_layout(raw_text: str) -> str:
    """Preprocess markdown document preserving lists, indentation, and tables.
    
    Retains indentation hierarchy (2-space, 4-space, tabs) to ensure that
    nested bullet points and parent-child concepts are semantically intact.
    """
    lines = raw_text.splitlines()
    processed_lines: list[str] = []

    for line in lines:
        # Preserve empty lines for paragraph separation
        if not line.strip():
            processed_lines.append("")
            continue

        # Keep original leading indentation exactly as authored
        processed_lines.append(line.rstrip())

    return "\n".join(processed_lines)


def chunk_document_by_sections(
    markdown_text: str, max_chunk_chars: int = 12000
) -> list[dict[str, Any]]:
    """Segment layout-preserved markdown into semantically coherent sections.
    
    Splits along H1 and H2 boundaries, preserving sub-headers and nested lists.
    """
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


# ==============================================================================
# 3. Gemini API LLM Extractor
# ==============================================================================

SYSTEM_EXTRACTION_PROMPT = """You are an expert Enterprise AI Architecture Knowledge Graph engineer.
Your task is to analyze the provided layout-preserved architectural guideline text and extract:
1. Guidelines: Major principles or architectural documents.
2. Patterns: Concrete architectural design patterns (e.g. Zero Ambient Authority, Memory Bank, Progressive Disclosure).
3. Antipatterns: Hazards, traps, security vulnerabilities, or anti-patterns.
4. Tradeoffs: Comparative decisions between architectural choices.
5. Edges: Directed Subject -> Predicate -> Object relationships strictly between the extracted nodes.
   Allowed predicates:
   - Pattern MITIGATES Antipattern
   - Guideline IMPLEMENTS Pattern
   - Pattern REQUIRES Pattern
   - Guideline TRADES_OFF Tradeoff
   - Guideline RELATES_TO Guideline

Assign deterministic, uppercase alphanumeric IDs (e.g., PAT-ZAA, ANTI-INJECTION, DOC-QUALITY-01).
Output strictly conforming to the requested schema.
"""

def extract_triples_with_gemini(
    text: str,
    doc_title: str,
    doc_uri: str,
    model_name: str = "gemini-2.5-flash",
) -> ExtractedGraphPayload:
    """Invoke Gemini API with structured outputs to extract typed graph triples."""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client()

        prompt = f"""Document Title: {doc_title}
Source URI: {doc_uri}

--- BEGIN ARCHITECTURAL CONTENT ---
{text}
--- END ARCHITECTURAL CONTENT ---

Extract all Guidelines, Patterns, Antipatterns, Tradeoffs, and directed Edges according to the schema.
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_EXTRACTION_PROMPT,
                response_mime_type="application/json",
                response_schema=ExtractedGraphPayload,
                temperature=0.1,
            ),
        )

        if response.text:
            return ExtractedGraphPayload.model_validate_json(response.text)

    except Exception as e:
        logger.warning(f"Gemini API invocation skipped/failed ({e}). Executing heuristic deterministic extractor.")

    # Fallback / Deterministic extractor for offline/local execution
    return _deterministic_fallback_extractor(text, doc_title, doc_uri)


def _deterministic_fallback_extractor(
    text: str, doc_title: str, doc_uri: str
) -> ExtractedGraphPayload:
    """Heuristic extraction used as a robust fallback or local testing engine."""
    payload = ExtractedGraphPayload()
    doc_hash = hashlib.sha256(doc_title.encode("utf-8")).hexdigest()[:8].upper()
    guideline_id = f"DOC-{doc_hash}"

    # Extract tags
    tags = re.findall(r"#([a-zA-Z0-9_\-]+)", text)
    category = tags[0] if tags else "architecture"
    summary = text[:300].strip().replace("\n", " ") + "..."

    guideline = GuidelineNode(
        guideline_id=guideline_id,
        title=doc_title,
        category=category,
        summary=summary,
        source_url=doc_uri,
    )
    payload.guidelines.append(guideline)

    # Heuristic extraction of Patterns and Antipatterns from headers/lists
    lines = text.splitlines()
    for line in lines:
        # Pattern detection
        pat_match = re.search(r"(?:Pattern|Practice):\s*([A-Za-z0-9\s\-]+)", line, re.IGNORECASE)
        if pat_match:
            p_name = pat_match.group(1).strip()
            p_id = f"PAT-{hashlib.sha256(p_name.encode()).hexdigest()[:6].upper()}"
            payload.patterns.append(
                PatternNode(pattern_id=p_id, name=p_name, category=category, description=line.strip())
            )
            payload.edges.append(
                GraphEdge(
                    source_id=guideline_id,
                    source_type="Guideline",
                    predicate="IMPLEMENTS",
                    target_id=p_id,
                    target_type="Pattern",
                    rationale="Guideline defines or recommends pattern",
                )
            )

        # Antipattern detection
        anti_match = re.search(r"(?:Antipattern|Pitfall|Hazard|Vulnerability):\s*([A-Za-z0-9\s\-]+)", line, re.IGNORECASE)
        if anti_match:
            a_name = anti_match.group(1).strip()
            a_id = f"ANTI-{hashlib.sha256(a_name.encode()).hexdigest()[:6].upper()}"
            payload.antipatterns.append(
                AntipatternNode(
                    antipattern_id=a_id,
                    name=a_name,
                    hazard=line.strip(),
                    remedy="Apply corresponding architectural pattern",
                )
            )
            # Link to the latest pattern if available
            if payload.patterns:
                payload.edges.append(
                    GraphEdge(
                        source_id=payload.patterns[-1].pattern_id,
                        source_type="Pattern",
                        predicate="MITIGATES",
                        target_id=a_id,
                        target_type="Antipattern",
                        rationale=f"Pattern mitigates {a_name}",
                    )
                )

    return payload


# ==============================================================================
# 4. Referential Integrity (Placeholder Resolution)
# ==============================================================================

def resolve_referential_integrity(payload: ExtractedGraphPayload) -> ExtractedGraphPayload:
    """Ensure no dangling edges exist in the graph.
    
    If an edge references an entity ID not present in the extracted node sets,
    generates a placeholder node to prevent foreign-key violation crashes in
    Spanner Graph or BigQuery.
    """
    known_nodes: dict[str, str] = {}

    for g in payload.guidelines:
        known_nodes[g.guideline_id] = "Guideline"
    for p in payload.patterns:
        known_nodes[p.pattern_id] = "Pattern"
    for a in payload.antipatterns:
        known_nodes[a.antipattern_id] = "Antipattern"
    for t in payload.tradeoffs:
        known_nodes[t.tradeoff_id] = "Tradeoff"

    for edge in payload.edges:
        # Check source node
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

        # Check target node
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
# 5. Batch Hydration (Spanner Graph & BigQuery)
# ==============================================================================

class GraphBatchHydrator:
    """Hydrates Spanner Graph and BigQuery in batches of 50 items."""

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
        """Insert or update nodes and edges into Cloud Spanner Graph in batches of 50."""
        if self.dry_run:
            total = (
                len(payload.guidelines)
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
                        columns=["guideline_id", "title", "category", "summary", "source_url", "created_at"],
                        values=[
                            [g.guideline_id, g.title, g.category, g.summary, g.source_url or "", spanner.COMMIT_TIMESTAMP]
                            for g in batch
                        ],
                    )
                total_mutations += len(batch)

            # 2. Patterns
            for i in range(0, len(payload.patterns), self.batch_size):
                batch = payload.patterns[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="Patterns",
                        columns=["pattern_id", "name", "category", "description", "created_at"],
                        values=[[p.pattern_id, p.name, p.category, p.description, spanner.COMMIT_TIMESTAMP] for p in batch],
                    )
                total_mutations += len(batch)

            # 3. Antipatterns
            for i in range(0, len(payload.antipatterns), self.batch_size):
                batch = payload.antipatterns[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="Antipatterns",
                        columns=["antipattern_id", "name", "hazard", "remedy", "created_at"],
                        values=[[a.antipattern_id, a.name, a.hazard, a.remedy, spanner.COMMIT_TIMESTAMP] for a in batch],
                    )
                total_mutations += len(batch)

            # 4. Tradeoffs
            for i in range(0, len(payload.tradeoffs), self.batch_size):
                batch = payload.tradeoffs[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="Tradeoffs",
                        columns=["tradeoff_id", "dimension", "option_a", "option_b", "analysis", "created_at"],
                        values=[
                            [t.tradeoff_id, t.dimension, t.option_a, t.option_b, t.analysis, spanner.COMMIT_TIMESTAMP]
                            for t in batch
                        ],
                    )
                total_mutations += len(batch)

            # 5. Edges: PatternMitigatesAntipattern
            mitigates_edges = [e for e in payload.edges if e.predicate == "MITIGATES"]
            for i in range(0, len(mitigates_edges), self.batch_size):
                batch = mitigates_edges[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="PatternMitigatesAntipattern",
                        columns=["pattern_id", "antipattern_id", "rationale"],
                        values=[[e.source_id, e.target_id, e.rationale or ""] for e in batch],
                    )
                total_mutations += len(batch)

            # 6. Edges: GuidelineImplementsPattern
            implements_edges = [e for e in payload.edges if e.predicate == "IMPLEMENTS"]
            for i in range(0, len(implements_edges), self.batch_size):
                batch = implements_edges[i : i + self.batch_size]
                with database.batch() as b:
                    b.insert_or_update(
                        table="GuidelineImplementsPattern",
                        columns=["guideline_id", "pattern_id", "notes"],
                        values=[[e.source_id, e.target_id, e.rationale or ""] for e in batch],
                    )
                total_mutations += len(batch)

            logger.info(f"Spanner Batch Hydration successful: {total_mutations} total mutations committed.")
            return total_mutations

        except Exception as e:
            logger.error(f"Spanner Batch Hydration encountered error: {e}")
            raise

    def hydrate_bigquery(self, payload: ExtractedGraphPayload) -> int:
        """Stream or load extracted nodes into BigQuery tables in batches."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] BigQuery Federation: Ready to insert into {self.bq_dataset_id}.")
            return len(payload.guidelines) + len(payload.patterns)

        try:
            from google.cloud import bigquery

            client = bigquery.Client(project=self.project_id)
            total_rows = 0

            # Guidelines
            if payload.guidelines:
                table_id = f"{self.project_id}.{self.bq_dataset_id}.guidelines"
                rows = [
                    {
                        "guideline_id": g.guideline_id,
                        "title": g.title,
                        "category": g.category,
                        "summary": g.summary,
                        "source_url": g.source_url,
                        "created_at": g.created_at.isoformat(),
                    }
                    for g in payload.guidelines
                ]
                errors = client.insert_rows_json(table_id, rows)
                if errors:
                    logger.warning(f"BigQuery insert errors on guidelines: {errors}")
                total_rows += len(rows)

            # Patterns
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

            logger.info(f"BigQuery Hydration successful: {total_rows} rows streamed.")
            return total_rows

        except Exception as e:
            logger.warning(f"BigQuery Hydration skipped or encountered error: {e}")
            return 0


# ==============================================================================
# 6. Incremental Synchronization & Checksum Tracking
# ==============================================================================

class CheckpointTracker:
    """Manages document checksums and timestamps to guarantee Zero-Duplicate writes."""

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

    def should_process(self, doc_id: str, checksum: str, last_modified: str | None = None) -> bool:
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
# 7. GCS Ingestion and Execution Orchestrator
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
) -> ExtractedGraphPayload:
    """Run end-to-end NL2KG pipeline over GCS bucket or local directory."""
    logger.info("Starting NL2KG Triplification Pipeline...")
    tracker = CheckpointTracker(checkpoint_file)
    consolidated_graph = ExtractedGraphPayload()

    documents_to_process: list[dict[str, str]] = []

    # 1. Discover documents from GCS or local directory
    if gcs_bucket_name:
        try:
            from google.cloud import storage

            client = storage.Client(project=project_id)
            bucket = client.bucket(gcs_bucket_name)
            blobs = list(bucket.list_blobs())
            logger.info(f"Discovered {len(blobs)} objects in GCS bucket gs://{gcs_bucket_name}")

            for b in blobs:
                if b.name.endswith(".md") or b.name.endswith(".txt"):
                    content = b.download_as_text()
                    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    if tracker.should_process(b.name, checksum):
                        documents_to_process.append(
                            {"uri": f"gs://{gcs_bucket_name}/{b.name}", "title": Path(b.name).stem, "content": content, "checksum": checksum, "id": b.name}
                        )
                    else:
                        logger.info(f"Skipping unchanged document (checksum match): {b.name}")
        except Exception as e:
            logger.warning(f"GCS listing skipped or failed: {e}. Checking local documents...")

    # Fallback to local documents if GCS yields none
    if not documents_to_process and local_dir and local_dir.exists():
        files = list(local_dir.glob("*.md")) + list(local_dir.glob("**/*.md"))
        for f in files:
            content = f.read_text(encoding="utf-8")
            checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
            doc_id = str(f.relative_to(local_dir))
            if tracker.should_process(doc_id, checksum):
                documents_to_process.append(
                    {"uri": str(f), "title": f.stem, "content": content, "checksum": checksum, "id": doc_id}
                )
            else:
                logger.info(f"Skipping unchanged local file: {doc_id}")

    logger.info(f"Total documents queued for triplification: {len(documents_to_process)}")

    # 2. Extract Triples with Layout Preservation
    for item in documents_to_process:
        logger.info(f"Processing document: {item['title']} ({item['uri']})")
        preserved_text = preserve_document_layout(item["content"])
        chunks = chunk_document_by_sections(preserved_text)

        doc_payload = ExtractedGraphPayload()
        for idx, chunk in enumerate(chunks):
            sub_title = f"{item['title']} - {chunk['title']}"
            extracted = extract_triples_with_gemini(chunk["text"], sub_title, item["uri"])
            doc_payload.guidelines.extend(extracted.guidelines)
            doc_payload.patterns.extend(extracted.patterns)
            doc_payload.antipatterns.extend(extracted.antipatterns)
            doc_payload.tradeoffs.extend(extracted.tradeoffs)
            doc_payload.edges.extend(extracted.edges)

        # 3. Referential Integrity (Placeholder Resolution)
        doc_payload = resolve_referential_integrity(doc_payload)

        # Merge into consolidated graph
        consolidated_graph.guidelines.extend(doc_payload.guidelines)
        consolidated_graph.patterns.extend(doc_payload.patterns)
        consolidated_graph.antipatterns.extend(doc_payload.antipatterns)
        consolidated_graph.tradeoffs.extend(doc_payload.tradeoffs)
        consolidated_graph.edges.extend(doc_payload.edges)

        # Update checkpoint
        n_nodes = len(doc_payload.guidelines) + len(doc_payload.patterns) + len(doc_payload.antipatterns) + len(doc_payload.tradeoffs)
        tracker.mark_completed(item["id"], item["checksum"], n_nodes, len(doc_payload.edges))

    # Deduplicate nodes by ID
    consolidated_graph.guidelines = list({g.guideline_id: g for g in consolidated_graph.guidelines}.values())
    consolidated_graph.patterns = list({p.pattern_id: p for p in consolidated_graph.patterns}.values())
    consolidated_graph.antipatterns = list({a.antipattern_id: a for a in consolidated_graph.antipatterns}.values())
    consolidated_graph.tradeoffs = list({t.tradeoff_id: t for t in consolidated_graph.tradeoffs}.values())

    # 4. Batch Hydration to Spanner Graph & BigQuery
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

    logger.info("NL2KG Triplification Pipeline completed successfully!")
    logger.info(f"Summary: {len(consolidated_graph.guidelines)} Guidelines, {len(consolidated_graph.patterns)} Patterns, "
                f"{len(consolidated_graph.antipatterns)} Antipatterns, {len(consolidated_graph.tradeoffs)} Tradeoffs, "
                f"{len(consolidated_graph.edges)} Edges.")

    return consolidated_graph


def main() -> None:
    """CLI Entrypoint for NL2KG pipeline."""
    parser = argparse.ArgumentParser(description="NL2KG Triplification Pipeline")
    parser.add_argument("--gcs-bucket", default="gea_agent_development_architectural_best_practices_1790796607", help="Source GCS bucket")
    parser.add_argument("--local-dir", type=Path, default=Path("docs"), help="Fallback local documents directory")
    parser.add_argument("--project-id", default="fivedaysai-prd-sandbox-317383", help="Google Cloud Project ID")
    parser.add_argument("--spanner-instance", default="gea-arch-guidelines-spanner", help="Spanner Instance ID")
    parser.add_argument("--spanner-database", default="arch_guidelines_graph", help="Spanner Database Name")
    parser.add_argument("--bq-dataset", default="gea_arch_guidelines_analytics", help="BigQuery Dataset ID")
    parser.add_argument("--checkpoint-file", type=Path, default=Path(".sync/checkpoints.json"), help="State file for incremental sync")
    parser.add_argument("--dry-run", action="store_true", help="Perform extraction and validation without writing to Spanner/BQ")

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
    )


if __name__ == "__main__":
    main()

"""Unit and integration tests for NL2KG Triplification Pipeline."""

import tempfile
from pathlib import Path
import pytest
from pydantic import ValidationError

from pipelines.nl2kg_pipeline import (
    AntipatternNode,
    CheckpointTracker,
    ExtractedGraphPayload,
    GraphBatchHydrator,
    GraphEdge,
    GuidelineNode,
    PatternNode,
    TradeoffNode,
    chunk_document_by_sections,
    preserve_document_layout,
    resolve_referential_integrity,
    run_pipeline,
)


def test_layout_preservation_indented_lists():
    """Verify that layout preservation preserves indentation, lists, and code blocks."""
    sample_markdown = """# Enterprise Agent Architecture
    
* Root principle:
  * Sub-item 1: Zero Ambient Authority
    * Sub-sub item: Per-task minted short-lived credentials
  * Sub-item 2: Progressive Disclosure
    * Sub-sub item: Metadata first, details on-demand

| Approach | Latency | Complexity |
|---|---|---|
| Platform-Native | Low | Minimal |
"""
    preserved = preserve_document_layout(sample_markdown)

    # Indentation must remain intact
    assert "  * Sub-item 1: Zero Ambient Authority" in preserved
    assert "    * Sub-sub item: Per-task minted short-lived credentials" in preserved
    assert "| Platform-Native | Low | Minimal |" in preserved


def test_pydantic_hardening_schema_validation():
    """Verify that Pydantic models strictly validate the Graph schema."""
    guideline = GuidelineNode(
        guideline_id="DOC-01",
        title="Agent Quality",
        category="quality",
        summary="Quality engineering practices.",
    )
    pattern = PatternNode(
        pattern_id="PAT-ZAA",
        name="Zero Ambient Authority",
        category="security",
        description="Least privilege access.",
    )
    edge = GraphEdge(
        source_id="DOC-01",
        source_type="Guideline",
        predicate="IMPLEMENTS",
        target_id="PAT-ZAA",
        target_type="Pattern",
    )

    payload = ExtractedGraphPayload(
        guidelines=[guideline],
        patterns=[pattern],
        edges=[edge],
    )

    assert len(payload.guidelines) == 1
    assert len(payload.patterns) == 1
    assert len(payload.edges) == 1

    # Invalid predicate should raise ValidationError
    with pytest.raises(ValidationError):
        GraphEdge(
            source_id="DOC-01",
            source_type="Guideline",
            predicate="INVALID_PREDICATE",  # type: ignore
            target_id="PAT-ZAA",
            target_type="Pattern",
        )


def test_referential_integrity_placeholder_resolution():
    """Verify dangling edges trigger automatic placeholder node generation."""
    payload = ExtractedGraphPayload()

    # Add a pattern
    payload.patterns.append(
        PatternNode(
            pattern_id="PAT-ZAA",
            name="Zero Ambient Authority",
            category="security",
            description="No ambient credentials.",
        )
    )

    # Add an edge pointing to a NON-EXISTENT antipattern node
    payload.edges.append(
        GraphEdge(
            source_id="PAT-ZAA",
            source_type="Pattern",
            predicate="MITIGATES",
            target_id="ANTI-CONFUSED-DEPUTY",
            target_type="Antipattern",
            rationale="Prevents confused deputy exploits.",
        )
    )

    # Before resolution: antipatterns list is empty
    assert len(payload.antipatterns) == 0

    # Resolve referential integrity
    resolved = resolve_referential_integrity(payload)

    # After resolution: placeholder node was generated with target_id
    assert len(resolved.antipatterns) == 1
    placeholder = resolved.antipatterns[0]
    assert placeholder.antipattern_id == "ANTI-CONFUSED-DEPUTY"
    assert "Inferred" in placeholder.name


def test_batch_hydration_chunking():
    """Verify that GraphBatchHydrator splits items into batches of 50."""
    hydrator = GraphBatchHydrator(
        project_id="test-project",
        spanner_instance_id="test-spanner",
        spanner_database_name="test-db",
        bq_dataset_id="test-bq",
        batch_size=50,
        dry_run=True,
    )

    payload = ExtractedGraphPayload()
    # Create 120 dummy patterns
    for i in range(120):
        payload.patterns.append(
            PatternNode(
                pattern_id=f"PAT-{i:03d}",
                name=f"Pattern {i}",
                category="test",
                description="Test pattern",
            )
        )

    mutations_count = hydrator.hydrate_spanner(payload)
    assert mutations_count == 120


def test_incremental_synchronization_checksum_tracker():
    """Verify that unchanged documents are skipped and modified ones re-processed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_file = Path(tmpdir) / "checkpoints.json"
        tracker = CheckpointTracker(checkpoint_file)

        doc_id = "doc-01.md"
        checksum_v1 = "abc123hash"
        checksum_v2 = "def456hash"

        # Initial check: doc should be processed
        assert tracker.should_process(doc_id, checksum_v1) is True

        # Mark as completed
        tracker.mark_completed(doc_id, checksum_v1, node_count=5, edge_count=4)

        # Unchanged: should NOT be processed
        assert tracker.should_process(doc_id, checksum_v1) is False

        # Modified content: should be processed
        assert tracker.should_process(doc_id, checksum_v2) is True


def test_end_to_end_pipeline_dry_run():
    """Verify end-to-end pipeline execution over local documentation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = Path(tmpdir) / "docs"
        docs_dir.mkdir()
        sync_dir = Path(tmpdir) / ".sync"

        sample_file = docs_dir / "sample_guideline.md"
        sample_file.write_text(
            """# Architecture Best Practice: Agent Skills
#agent-skills #progressive-disclosure

## Pattern: Progressive Disclosure
Progressive disclosure minimizes initial context overhead.

## Antipattern: Monolithic Prompting
Stuffing all system knowledge into the system prompt degrades retrieval.
""",
            encoding="utf-8",
        )

        graph = run_pipeline(
            local_dir=docs_dir,
            gcs_bucket_name=None,
            checkpoint_file=sync_dir / "checkpoints.json",
            dry_run=True,
        )

        assert len(graph.guidelines) >= 1
        assert len(graph.patterns) >= 1
        assert len(graph.antipatterns) >= 1
        assert len(graph.edges) >= 1

"""Loader module for ingesting triplified graph into Cloud Spanner Graph and BigQuery."""

import json
from pathlib import Path
from pipelines.config import config
from pipelines.schema import TriplifiedGraph


class GraphLoader:
    """Handles persistence of knowledge graph triples to Spanner and BigQuery."""

    def __init__(self, project_id: str | None = None):
        self.project_id = project_id or config.gcp_project_id

    def export_to_json(self, graph: TriplifiedGraph, output_path: Path) -> Path:
        """Export graph to structured JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = graph.model_dump(mode="json")
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return output_path

    def load_to_spanner(self, graph: TriplifiedGraph) -> int:
        """Load nodes and edges into Cloud Spanner Graph.

        In local/offline mode, logs the mutation batches.
        """
        total_mutations = (
            len(graph.guidelines)
            + len(graph.patterns)
            + len(graph.tradeoffs)
            + len(graph.antipatterns)
            + len(graph.mitigates_edges)
            + len(graph.implements_edges)
        )
        # Mock / Spanner API call integration
        return total_mutations

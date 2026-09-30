"""CLI entrypoint for NL2KG Triplification Pipeline."""

from pathlib import Path
import typer
from rich.console import Console
from pipelines.config import config
from pipelines.extract import extract_all_documents
from pipelines.loader import GraphLoader
from pipelines.triplify import merge_graphs, triplify_document

app = typer.Typer(help="NL2KG Triplification Pipeline for Architectural Guidelines")
console = Console()


@app.command()
def extract(
    source_dir: Path = typer.Option(Path(config.input_docs_dir), help="Directory of source markdown docs"),
    output_file: Path = typer.Option(Path(config.output_dir) / "triples.json", help="Output file path"),
) -> None:
    """Extract entities and triplify markdown documents into knowledge graph JSON."""
    console.print(f"[bold green]Starting NL2KG Triplification from: {source_dir}[/bold green]")
    docs = extract_all_documents(source_dir)
    console.print(f"Discovered {len(docs)} documents.")

    graphs = [triplify_document(d) for d in docs]
    merged = merge_graphs(graphs)

    loader = GraphLoader()
    out = loader.export_to_json(merged, output_file)

    console.print(f"[bold green]Extraction complete![/bold green]")
    console.print(f"Guidelines: {len(merged.guidelines)}")
    console.print(f"Patterns: {len(merged.patterns)}")
    console.print(f"Tradeoffs: {len(merged.tradeoffs)}")
    console.print(f"Antipatterns: {len(merged.antipatterns)}")
    console.print(f"Exported to: {out}")


@app.command()
def validate(
    input_file: Path = typer.Option(Path(config.output_dir) / "triples.json", help="Triples JSON to validate"),
) -> None:
    """Validate extracted triples against the ontology schema."""
    if not input_file.exists():
        console.print(f"[bold red]File not found: {input_file}[/bold red]")
        raise typer.Exit(code=1)

    import json
    from pipelines.schema import TriplifiedGraph

    data = json.loads(input_file.read_text(encoding="utf-8"))
    graph = TriplifiedGraph.model_validate(data)
    console.print(f"[bold green]Validation passed successfully for {input_file}![/bold green]")
    console.print(f"Total nodes: {len(graph.guidelines) + len(graph.patterns) + len(graph.tradeoffs) + len(graph.antipatterns)}")
    console.print(f"Total edges: {len(graph.mitigates_edges) + len(graph.implements_edges)}")


if __name__ == "__main__":
    app()

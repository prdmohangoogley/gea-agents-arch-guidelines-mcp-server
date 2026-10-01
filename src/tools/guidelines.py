"""FastMCP tools for querying enterprise agent architectural guidelines."""

from __future__ import annotations

from typing import Any
from fastmcp import FastMCP
from src.graph.client import GraphClient
from src.otel_setup import get_tracer

tracer = get_tracer("guidelines-mcp-server")


def register_guideline_tools(mcp: FastMCP, client: GraphClient) -> None:
    """Register guideline search, detail, best practice, and deep dive tools with FastMCP."""

    @mcp.tool()
    async def get_best_practice(topic: str) -> dict[str, Any]:
        """Retrieve operational architectural best practices and patterns from Cloud Spanner Graph by topic.

        Args:
            topic: Architectural topic, pattern, or guideline keyword (e.g., 'Quality', 'Security', 'Memory', 'ZAA').

        Returns:
            Structured envelope containing matching guidelines, patterns, and operational latency metadata.
        """
        with tracer.start_as_current_span("tools/call:get_best_practice") as span:
            span.set_attribute("tool.name", "get_best_practice")
            span.set_attribute("topic", topic)
            result = await client.get_best_practice(topic=topic)
            span.set_attribute("result.status", result.get("status", "unknown"))
            span.set_attribute("result.source", result.get("source", "unknown"))
            span.set_attribute("latency_ms", float(result.get("latency_ms", 0.0)))
            return result

    @mcp.tool()
    async def deep_dive_guideline(component: str) -> dict[str, Any]:
        """Perform deep-dive analytical investigation of an architectural component using BigQuery analytics.

        Args:
            component: Component or system name to analyze (e.g., 'Security', 'Quality', 'Memory Bank', 'Cloud Run').

        Returns:
            Analytical lookup envelope including implemented patterns, antipattern hazards, and mitigations.
        """
        with tracer.start_as_current_span("tools/call:deep_dive_guideline") as span:
            span.set_attribute("tool.name", "deep_dive_guideline")
            span.set_attribute("component", component)
            result = await client.deep_dive_guideline(component=component)
            span.set_attribute("result.status", result.get("status", "unknown"))
            span.set_attribute("result.source", result.get("source", "unknown"))
            span.set_attribute("latency_ms", float(result.get("latency_ms", 0.0)))
            return result

    @mcp.tool()
    async def search_guidelines(
        query: str,
        category: str | None = None,
        limit: int = 5,
    ) -> str:
        """Search enterprise agent architectural guidelines by keywords or topic category.

        Args:
            query: Architectural query keyword (e.g., 'memory bank', 'security', 'mcp', 'a2a').
            category: Optional domain filter ('quality', 'security', 'protocols', 'runtime', 'context').
            limit: Maximum guidelines to return (default 5).

        Returns:
            Markdown formatted list of matching architectural guidelines.
        """
        results = await client.search_guidelines(query=query, category=category, limit=limit)
        if not results:
            return f"No architectural guidelines found matching '{query}'."

        lines = [f"### 📚 Architectural Guidelines Matching: `{query}`\n"]
        for g in results:
            lines.append(f"- **[{g.guideline_id}] {g.title}** (`#{g.category}`)")
            lines.append(f"  {g.summary}")
            if g.source_url:
                lines.append(f"  *Source reference:* `{g.source_url}`")
            lines.append("")
        return "\n".join(lines)

    @mcp.tool()
    async def get_guideline_details(guideline_id: str) -> str:
        """Retrieve full details of an architectural guideline by ID.

        Args:
            guideline_id: Identifier of the guideline (e.g., 'DOC-01', 'DOC-02', 'DOC-08').

        Returns:
            Detailed markdown summary and takeaways for the selected guideline.
        """
        guideline = await client.get_guideline(guideline_id)
        if not guideline:
            return f"Guideline `{guideline_id}` was not found."

        return (
            f"## [{guideline.guideline_id}] {guideline.title}\n"
            f"**Category**: `#{guideline.category}`\n\n"
            f"### Executive Summary\n"
            f"{guideline.summary}\n\n"
            f"### Reference\n"
            f"`{guideline.source_url}`"
        )

"""FastMCP tools for design patterns and architectural tradeoffs."""

from fastmcp import FastMCP
from src.graph.client import GraphClient


def register_pattern_tools(mcp: FastMCP, client: GraphClient) -> None:
    """Register pattern and tradeoff tools with FastMCP."""

    @mcp.tool()
    async def query_architectural_pattern(pattern_name: str) -> str:
        """Query specific enterprise agent architectural pattern details and antipattern mitigations.

        Args:
            pattern_name: Name of pattern (e.g. 'Zero Ambient Authority', 'Memory Bank', 'Progressive Disclosure').

        Returns:
            Pattern description, domain category, and pitfalls/antipatterns mitigated.
        """
        pattern = await client.get_pattern(pattern_name)
        if not pattern:
            return f"Architectural pattern matching '{pattern_name}' was not found in knowledge base."

        mitigations = "\n".join([f"  - 🛡️ `{m}`" for m in pattern.mitigates]) or "  - None specified"
        return (
            f"## 🏛️ Architectural Pattern: {pattern.name}\n"
            f"**Identifier**: `{pattern.pattern_id}` | **Category**: `#{pattern.category}`\n\n"
            f"### Description\n"
            f"{pattern.description}\n\n"
            f"### Mitigates Antipatterns\n"
            f"{mitigations}"
        )

    @mcp.tool()
    async def evaluate_design_tradeoffs(option_a: str, option_b: str) -> str:
        """Evaluate pros, cons, complexity, and operational tradeoffs between two architectural alternatives.

        Args:
            option_a: First design choice (e.g., 'Platform-Native Memory Bank').
            option_b: Second design choice (e.g., 'Self-Hosted Redis Cluster').

        Returns:
            Structured comparative tradeoff analysis and enterprise recommendations.
        """
        eval_result = await client.evaluate_tradeoffs(option_a, option_b)
        return (
            f"## ⚖️ Architectural Tradeoff Matrix: `{option_a}` vs `{option_b}`\n\n"
            f"| Dimension | Analysis |\n"
            f"|---|---|\n"
            f"| **Latency Impact** | {eval_result.latency_impact} |\n"
            f"| **Complexity Impact** | {eval_result.complexity_impact} |\n"
            f"| **Security Posture** | {eval_result.security_posture} |\n\n"
            f"### 💡 Architectural Recommendation\n"
            f"{eval_result.recommendation}"
        )

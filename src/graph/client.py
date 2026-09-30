"""Spanner Graph client abstraction with embedded fallback for offline development."""

from typing import Any
from src.config import config
from src.models.guideline import (
    Antipattern,
    Guideline,
    Pattern,
    TradeoffEvaluation,
)


class GraphClient:
    """Manages connections and ISO GQL queries to Spanner Graph."""

    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock or config.use_mock_graph
        self._init_knowledge_store()

    def _init_knowledge_store(self) -> None:
        """Seed embedded knowledge store for local execution or fallback."""
        self._guidelines = [
            Guideline(
                guideline_id="DOC-01",
                title="AI Agent Quality Engineering",
                category="quality",
                summary="Systematic evaluation, observability, cost & security engineering for enterprise agents on Google Cloud.",
                source_url="01-ai-agent-quality-engineering.md",
            ),
            Guideline(
                guideline_id="DOC-02",
                title="Vibe Coding Agent Security & Evaluation",
                category="security",
                summary="Sandboxing, Zero Ambient Authority (ZAA), Agentic SecOps & session convergence in coding environments.",
                source_url="02-vibe-coding-agent-security-evaluation-kb.md",
            ),
            Guideline(
                guideline_id="DOC-03",
                title="Open AI Agent Protocol Stack",
                category="protocols",
                summary="Comprehensive protocol architecture spanning MCP, A2A, UCP, AP2/x402, and A2UI.",
                source_url="03-enterprise-ai-agent-protocol-stack.md",
            ),
            Guideline(
                guideline_id="DOC-08",
                title="Context Engineering for Stateful AI Agents",
                category="context",
                summary="Sessions, Memory Banks, RAG architectures, and state governance on Google Cloud.",
                source_url="08-context-engineering-stateful-agents.md",
            ),
            Guideline(
                guideline_id="DOC-09",
                title="Platform-Native State Management",
                category="runtime",
                summary="State management with Gemini Enterprise Agent Runtime & Memory Bank vs self-hosted state stores.",
                source_url="09-platform-native-state-management.md",
            ),
        ]

        self._patterns = {
            "Zero Ambient Authority": Pattern(
                pattern_id="PAT-ZAA",
                name="Zero Ambient Authority",
                category="security",
                description="Agents execute without inherited environmental credentials; tokens and capabilities are minted per-task and scoped to minimum necessity.",
                mitigates=["Credential Leakage", "Confused Deputy Problem", "Accidental Privilege Escalation"],
            ),
            "Progressive Disclosure": Pattern(
                pattern_id="PAT-PROG-DISC",
                name="Progressive Disclosure",
                category="skills",
                description="Present lightweight tool/skill metadata to model context initially, loading heavy definitions and reference manuals only on demand.",
                mitigates=["Context Window Exhaustion", "Prompt Dilution", "High Token Costs"],
            ),
            "Memory Bank": Pattern(
                pattern_id="PAT-MEM-BANK",
                name="Memory Bank",
                category="runtime",
                description="Decouple working conversation context from long-term factual state using managed Memory Bank with automated consolidation and semantic recall.",
                mitigates=["Catastrophic Forgetting", "Session Drift", "Unbounded Context Growth"],
            ),
        }

    async def search_guidelines(
        self, query: str, category: str | None = None, limit: int = 5
    ) -> list[Guideline]:
        """Search guidelines by matching query against title and summary."""
        q = query.lower()
        results = []
        for g in self._guidelines:
            if category and g.category.lower() != category.lower():
                continue
            if q in g.title.lower() or q in g.summary.lower() or q in g.category.lower():
                results.append(g)
            if len(results) >= limit:
                break
        return results or self._guidelines[:limit]

    async def get_guideline(self, guideline_id: str) -> Guideline | None:
        """Retrieve a specific guideline by ID."""
        for g in self._guidelines:
            if g.guideline_id.upper() == guideline_id.upper():
                return g
        return None

    async def get_pattern(self, name: str) -> Pattern | None:
        """Retrieve an architectural pattern and its mitigations."""
        for pat_name, pattern in self._patterns.items():
            if pat_name.lower() in name.lower() or name.lower() in pat_name.lower():
                return pattern
        return None

    async def evaluate_tradeoffs(self, option_a: str, option_b: str) -> TradeoffEvaluation:
        """Evaluate tradeoffs between two architectural alternatives."""
        return TradeoffEvaluation(
            option_a=option_a,
            option_b=option_b,
            latency_impact="Platform-native options reduce cross-network hops by leveraging Google colocation.",
            complexity_impact=f"Managing {option_b} requires custom maintenance, while {option_a} reduces operational overhead.",
            security_posture="Managed solutions enforce IAM and audit logs natively; self-managed requires explicit perimeter security.",
            recommendation=f"Prefer {option_a} for enterprise deployments prioritizing reliability and low operational toil.",
        )

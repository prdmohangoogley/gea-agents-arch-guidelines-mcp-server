"""Spanner Graph and BigQuery client abstraction with embedded fallback for offline development."""

from __future__ import annotations

import logging
import time
from typing import Any

from src.config import config
from src.graph.queries import (
    QUERY_BEST_PRACTICES_BY_TOPIC,
    QUERY_GUIDELINE_HIERARCHY,
    QUERY_PATTERN_MITIGATIONS,
    QUERY_SEARCH_GUIDELINES,
)
from src.models.guideline import (
    Antipattern,
    Guideline,
    Pattern,
    TradeoffEvaluation,
)

logger = logging.getLogger("graph_client")


class GraphClient:
    """Manages connections, ISO GQL queries to Spanner Graph, and analytical SQL to BigQuery."""

    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock or config.use_mock_graph
        self._spanner_database = None
        self._bq_client = None
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

    def _get_spanner_db(self) -> Any:
        """Lazily initialize Google Cloud Spanner client."""
        if self._spanner_database is None and not self.use_mock:
            try:
                from google.cloud import spanner

                client = spanner.Client(project=config.gcp_project_id)
                instance = client.instance(config.spanner_instance_id)
                self._spanner_database = instance.database(config.spanner_database_id)
            except Exception as e:
                logger.warning(f"Could not initialize Spanner client: {e}. Fallback to mock.")
                self._spanner_database = None
        return self._spanner_database

    def _get_bq_client(self) -> Any:
        """Lazily initialize BigQuery client."""
        if self._bq_client is None and not self.use_mock:
            try:
                from google.cloud import bigquery

                self._bq_client = bigquery.Client(project=config.gcp_project_id)
            except Exception as e:
                logger.warning(f"Could not initialize BigQuery client: {e}. Fallback to mock.")
                self._bq_client = None
        return self._bq_client

    async def get_best_practice(self, topic: str) -> dict[str, Any]:
        """Operational GQL lookup against Cloud Spanner Graph with latency tracking and fallback."""
        start_time = time.perf_counter()
        db = self._get_spanner_db()

        if db is not None:
            try:
                from google.cloud import spanner
                from google.cloud.spanner_v1 import ExecuteSqlRequest

                params = {"topic": f"%{topic}%", "limit": 10}
                param_types = {"topic": spanner.param_types.STRING, "limit": spanner.param_types.INT64}

                with db.snapshot() as snapshot:
                    res = snapshot.execute_sql(
                        QUERY_BEST_PRACTICES_BY_TOPIC,
                        params=params,
                        param_types=param_types,
                        query_mode=ExecuteSqlRequest.QueryMode.PROFILE,
                    )
                    rows = list(res)

                    # Extract server-side execution latency if available, else wall clock
                    server_latency_ms = None
                    if res.stats and "elapsed_time" in res.stats.query_stats:
                        raw_elapsed = res.stats.query_stats["elapsed_time"]
                        if "msecs" in raw_elapsed:
                            server_latency_ms = float(raw_elapsed.replace(" msecs", "").strip())
                        elif "usecs" in raw_elapsed:
                            server_latency_ms = float(raw_elapsed.replace(" usecs", "").strip()) / 1000.0

                elapsed_ms = server_latency_ms if server_latency_ms is not None else (time.perf_counter() - start_time) * 1000

                if rows:
                    guidelines = []
                    patterns = []
                    seen_g = set()
                    seen_p = set()

                    for r in rows:
                        gid, gtitle, gcat, gsum, pid, pname, pcat, pdesc = r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]
                        if gid not in seen_g:
                            guidelines.append({"guideline_id": gid, "title": gtitle, "category": gcat, "summary": gsum})
                            seen_g.add(gid)
                        if pid not in seen_p:
                            patterns.append({"pattern_id": pid, "name": pname, "category": pcat, "description": pdesc})
                            seen_p.add(pid)

                    return {
                        "status": "success",
                        "source": "spanner_graph",
                        "topic": topic,
                        "latency_ms": round(elapsed_ms, 2),
                        "guidelines": guidelines,
                        "patterns": patterns,
                        "total_matches": len(rows),
                    }
            except Exception as e:
                logger.warning(f"Spanner GQL query failed: {e}. Falling back to embedded knowledge store.")

        # Embedded Fallback
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        q = topic.lower()
        matched_guidelines = [
            {"guideline_id": g.guideline_id, "title": g.title, "category": g.category, "summary": g.summary}
            for g in self._guidelines
            if q in g.title.lower() or q in g.summary.lower() or q in g.category.lower()
        ]
        matched_patterns = [
            {"pattern_id": p.pattern_id, "name": p.name, "category": p.category, "description": p.description, "mitigates": p.mitigates}
            for p in self._patterns.values()
            if q in p.name.lower() or q in p.description.lower() or q in p.category.lower()
        ]

        if not matched_guidelines and not matched_patterns:
            matched_guidelines = [
                {"guideline_id": g.guideline_id, "title": g.title, "category": g.category, "summary": g.summary}
                for g in self._guidelines[:2]
            ]
            matched_patterns = [
                {"pattern_id": p.pattern_id, "name": p.name, "category": p.category, "description": p.description, "mitigates": p.mitigates}
                for p in list(self._patterns.values())[:2]
            ]

        return {
            "status": "degraded" if db is not None else "success",
            "source": "embedded_cache",
            "topic": topic,
            "latency_ms": round(elapsed_ms, 2),
            "guidelines": matched_guidelines,
            "patterns": matched_patterns,
            "total_matches": len(matched_guidelines) + len(matched_patterns),
            "note": "Served from embedded cache (Spanner query fallback or mock mode active)",
        }

    async def deep_dive_guideline(self, component: str) -> dict[str, Any]:
        """Analytical SQL/Federated lookup against BigQuery analytics with fallback."""
        start_time = time.perf_counter()
        bq = self._get_bq_client()

        if bq is not None:
            try:
                from google.cloud import bigquery

                query = f"""
                SELECT
                  g.guideline_id,
                  g.title,
                  g.category,
                  g.summary,
                  g.source_url,
                  p.pattern_id,
                  p.name AS pattern_name,
                  p.category AS pattern_category,
                  p.description AS pattern_description,
                  a.antipattern_id,
                  a.name AS antipattern_name,
                  a.hazard,
                  a.remedy
                FROM `{config.gcp_project_id}.{config.bq_dataset_id}.guidelines` g
                LEFT JOIN `{config.gcp_project_id}.{config.bq_dataset_id}.guideline_implements_pattern` gp
                  ON g.guideline_id = gp.guideline_id
                LEFT JOIN `{config.gcp_project_id}.{config.bq_dataset_id}.patterns` p
                  ON gp.pattern_id = p.pattern_id
                LEFT JOIN `{config.gcp_project_id}.{config.bq_dataset_id}.pattern_mitigates_antipattern` pa
                  ON p.pattern_id = pa.pattern_id
                LEFT JOIN `{config.gcp_project_id}.{config.bq_dataset_id}.antipatterns` a
                  ON pa.antipattern_id = a.antipattern_id
                WHERE LOWER(g.title) LIKE LOWER(@comp)
                   OR LOWER(p.name) LIKE LOWER(@comp)
                   OR LOWER(g.category) LIKE LOWER(@comp)
                   OR LOWER(p.description) LIKE LOWER(@comp)
                LIMIT 15
                """

                job_config = bigquery.QueryJobConfig(
                    query_parameters=[bigquery.ScalarQueryParameter("comp", "STRING", f"%{component}%")]
                )

                query_job = bq.query(query, job_config=job_config)
                rows = list(query_job.result())
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                if rows:
                    items = []
                    for r in rows:
                        items.append({
                            "guideline_id": r.guideline_id,
                            "title": r.title,
                            "category": r.category,
                            "summary": r.summary,
                            "source_url": r.source_url,
                            "pattern_name": r.pattern_name,
                            "pattern_description": r.pattern_description,
                            "antipattern_name": r.antipattern_name,
                            "hazard": r.hazard,
                            "remedy": r.remedy,
                        })

                    return {
                        "status": "success",
                        "source": "bigquery_analytics",
                        "component": component,
                        "latency_ms": round(elapsed_ms, 2),
                        "row_count": len(items),
                        "details": items,
                    }
            except Exception as e:
                logger.warning(f"BigQuery deep dive query failed: {e}. Falling back to embedded store.")

        # Embedded Fallback
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        comp = component.lower()
        fallback_details = []

        for g in self._guidelines:
            if comp in g.title.lower() or comp in g.category.lower() or comp in g.summary.lower():
                fallback_details.append({
                    "guideline_id": g.guideline_id,
                    "title": g.title,
                    "category": g.category,
                    "summary": g.summary,
                    "source_url": g.source_url,
                    "pattern_name": "Zero Ambient Authority",
                    "pattern_description": "Enforce explicit capability tokens with minimal scope.",
                    "antipattern_name": "Hardcoded Environmental Credentials",
                    "hazard": "Ambient tokens leak into execution logs or child processes.",
                    "remedy": "Rotate to fine-grained workload identity federation.",
                })

        if not fallback_details:
            g = self._guidelines[0]
            fallback_details.append({
                "guideline_id": g.guideline_id,
                "title": g.title,
                "category": g.category,
                "summary": g.summary,
                "source_url": g.source_url,
                "pattern_name": "Glass Box Trajectory Assertion",
                "pattern_description": "Record and assert on full reasoning steps.",
                "antipattern_name": "Silent Failure",
                "hazard": "Agent hallucinates silently without error tracing.",
                "remedy": "Enforce trajectory assertion release gates.",
            })

        return {
            "status": "degraded" if bq is not None else "success",
            "source": "embedded_cache",
            "component": component,
            "latency_ms": round(elapsed_ms, 2),
            "row_count": len(fallback_details),
            "details": fallback_details,
            "note": "Served from embedded cache (BigQuery query fallback or mock mode active)",
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

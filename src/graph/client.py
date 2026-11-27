"""Spanner Graph and BigQuery client abstraction with embedded fallback for offline development."""

from __future__ import annotations

import logging
import time
from typing import Any

from src.config import config
from src.graph.queries import (
    QUERY_BEST_PRACTICES_BY_TOPIC,
    QUERY_GET_GUIDELINE_BY_ID,
    QUERY_GUIDELINE_HIERARCHY,
    QUERY_PATTERN_MITIGATIONS,
    QUERY_RUBRIC_ENFORCEMENT,
    QUERY_RUBRIC_ITEMS,
    QUERY_SEARCH_GUIDELINES,
    QUERY_TRADEOFFS,
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

    def __init__(
        self,
        use_mock: bool = False,
        project_id: str | None = None,
        instance_id: str | None = None,
        database_id: str | None = None,
        bq_dataset_id: str | None = None,
    ):
        self.use_mock = use_mock or config.use_mock_graph
        self.project_id = project_id or config.gcp_project_id
        self.instance_id = instance_id or config.spanner_instance_id
        self.database_id = database_id or config.spanner_database_id
        self.bq_dataset_id = bq_dataset_id or config.bq_dataset_id
        self._spanner_database = None
        self._bq_client = None
        self._rubric_items: list[dict[str, Any]] = []
        self._rubric_edges: list[dict[str, Any]] = []
        self._init_knowledge_store()

    def _init_knowledge_store(self) -> None:
        """Seed embedded knowledge store from the full 83-concept OKF v0.2 corpus for offline/mock parity."""
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

        # Dynamically hydrate all 83 OKF v0.2 concepts & 37 FDE rubric items from local corpus
        try:
            import json
            from pathlib import Path

            repo_root = Path(__file__).resolve().parent.parent.parent
            snapshot_file = repo_root / "dist" / "portable_bundle" / "okf" / "nl2kg_graph_triples_snapshot.json"
            if snapshot_file.exists():
                snap = json.loads(snapshot_file.read_text(encoding="utf-8"))
                existing_ids = {g.guideline_id for g in self._guidelines}
                for g_dict in snap.get("guidelines", []):
                    gid = g_dict.get("guideline_id", "")
                    if gid and gid not in existing_ids:
                        self._guidelines.append(
                            Guideline(
                                guideline_id=gid,
                                title=g_dict.get("title", gid),
                                category=g_dict.get("category", "architecture"),
                                summary=g_dict.get("summary", ""),
                                source_url=g_dict.get("source_url", ""),
                            )
                        )
                        existing_ids.add(gid)
                self._rubric_items = snap.get("fde_rubric_items") or snap.get("fde_rubrics", [])
                self._rubric_edges = snap.get("enforces_rubric_edges") or snap.get("rubric_edges", [])
            else:
                from pipelines.nl2kg_pipeline import extract_triples_from_documents, load_local_markdown_corpus

                concepts_dir = (
                    (repo_root / "data" / "okf" / "concepts")
                    if (repo_root / "data" / "okf" / "concepts").exists()
                    else (repo_root / "okf" / "concepts")
                )
                docs = load_local_markdown_corpus(str(concepts_dir))
                triples = extract_triples_from_documents(docs)
                existing_ids = {g.guideline_id for g in self._guidelines}
                for g_dict in triples.get("guidelines", []):
                    gid = g_dict.get("guideline_id", "")
                    if gid and gid not in existing_ids:
                        self._guidelines.append(
                            Guideline(
                                guideline_id=gid,
                                title=g_dict.get("title", gid),
                                category=g_dict.get("category", "architecture"),
                                summary=g_dict.get("summary", ""),
                                source_url=g_dict.get("source_url", ""),
                            )
                        )
                        existing_ids.add(gid)
                self._rubric_items = triples.get("fde_rubrics", [])
                self._rubric_edges = triples.get("rubric_edges", [])
        except Exception as exc:
            logger.debug(f"Dynamic OKF mock corpus hydration skipped: {exc}")

        # Hydrate the 9 PCA & Well-Architected Framework OKF v0.2 concepts (OKF-PCA-01..09)
        try:
            from pathlib import Path
            import json

            repo_root = Path(__file__).resolve().parent.parent.parent
            pca_manifest = (
                (repo_root / "data" / "okf" / "pca_waf" / "MANIFEST.json")
                if (repo_root / "data" / "okf" / "pca_waf" / "MANIFEST.json").exists()
                else (repo_root / "okf" / "pca_waf" / "MANIFEST.json")
            )
            if pca_manifest.exists():
                mdata = json.loads(pca_manifest.read_text(encoding="utf-8"))
                existing_ids = {g.guideline_id for g in self._guidelines}
                for c in mdata.get("concepts", []):
                    cid = c.get("id", "")
                    if cid and cid not in existing_ids:
                        self._guidelines.append(
                            Guideline(
                                guideline_id=cid,
                                title=c.get("title", cid),
                                category="well_architected",
                                summary=c.get("description", ""),
                                source_url=c.get("gcs_uri", c.get("concept_path", "")),
                            )
                        )
                        existing_ids.add(cid)
        except Exception as exc:
            logger.debug(f"PCA WAF OKF hydration skipped: {exc}")

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
                import os
                from google.cloud import spanner

                # Disable un-instrumented internal SDK client metrics export to prevent Cloud Monitoring 400 Bad Request errors
                os.environ.setdefault("SPANNER_DISABLE_BUILTIN_METRICS", "true")

                # Defense-in-depth: Bind instance_id on tracer factory if metrics are ever active
                try:
                    from google.cloud.spanner_v1.metrics.spanner_metrics_tracer_factory import SpannerMetricsTracerFactory
                    SpannerMetricsTracerFactory().set_instance(config.spanner_instance_id)
                except Exception:
                    pass

                client = spanner.Client(project=config.gcp_project_id, disable_builtin_metrics=True)
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
        """Search guidelines by matching query against title, summary, and ID in Spanner Graph with fallback."""
        db = self._get_spanner_db()
        if db is not None:
            try:
                from google.cloud import spanner

                params = {"category": category, "keyword": f"%{query}%", "limit": limit}
                param_types = {
                    "category": spanner.param_types.STRING,
                    "keyword": spanner.param_types.STRING,
                    "limit": spanner.param_types.INT64,
                }
                with db.snapshot() as snapshot:
                    res = list(snapshot.execute_sql(QUERY_SEARCH_GUIDELINES, params=params, param_types=param_types))
                if res:
                    return [
                        Guideline(
                            guideline_id=r[0],
                            title=r[1],
                            category=r[2],
                            summary=r[3],
                            source_url=r[4],
                        )
                        for r in res
                    ]
            except Exception as e:
                logger.warning(f"Spanner search_guidelines failed: {e}. Fallback to embedded.")

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
        """Retrieve a specific guideline by ID from Spanner Graph with fallback."""
        db = self._get_spanner_db()
        if db is not None:
            try:
                from google.cloud import spanner

                params = {"guideline_id": guideline_id}
                param_types = {"guideline_id": spanner.param_types.STRING}
                with db.snapshot() as snapshot:
                    res = list(snapshot.execute_sql(QUERY_GET_GUIDELINE_BY_ID, params=params, param_types=param_types))
                if res:
                    r = res[0]
                    return Guideline(
                        guideline_id=r[0],
                        title=r[1],
                        category=r[2],
                        summary=r[3],
                        source_url=r[4],
                    )
            except Exception as e:
                logger.warning(f"Spanner get_guideline failed: {e}. Fallback to embedded.")

        for g in self._guidelines:
            if g.guideline_id.upper() == guideline_id.upper():
                return g
        return None

    async def get_pattern(self, name: str) -> Pattern | None:
        """Retrieve an architectural pattern and its mitigations from Spanner Graph with fallback."""
        db = self._get_spanner_db()
        if db is not None:
            try:
                from google.cloud import spanner

                q_pat = """
                GRAPH ArchGuidelinesGraph
                MATCH (p:Pattern)
                WHERE LOWER(p.name) LIKE LOWER(@name) OR LOWER(p.pattern_id) LIKE LOWER(@name)
                RETURN p.pattern_id, p.name, p.category, p.description
                LIMIT 1;
                """
                params = {"name": f"%{name}%"}
                param_types = {"name": spanner.param_types.STRING}
                with db.snapshot(multi_use=True) as snapshot:
                    res_pat = list(snapshot.execute_sql(q_pat, params=params, param_types=param_types))
                    if res_pat:
                        pid, pname, pcat, pdesc = res_pat[0][0], res_pat[0][1], res_pat[0][2], res_pat[0][3]
                        res_mit = list(
                            snapshot.execute_sql(
                                QUERY_PATTERN_MITIGATIONS,
                                params={"pattern_name": f"%{pname}%", "limit": 10},
                                param_types={
                                    "pattern_name": spanner.param_types.STRING,
                                    "limit": spanner.param_types.INT64,
                                },
                            )
                        )
                        mitigations = [r[1] for r in res_mit]
                        return Pattern(
                            pattern_id=pid,
                            name=pname,
                            category=pcat,
                            description=pdesc,
                            mitigates=mitigations,
                        )
            except Exception as e:
                logger.warning(f"Spanner get_pattern failed: {e}. Fallback to embedded.")

        for pat_name, pattern in self._patterns.items():
            if pat_name.lower() in name.lower() or name.lower() in pat_name.lower():
                return pattern
        return None

    async def evaluate_tradeoffs(self, option_a: str, option_b: str) -> TradeoffEvaluation:
        """Evaluate tradeoffs between two architectural alternatives using Spanner Graph."""
        db = self._get_spanner_db()
        if db is not None:
            try:
                from google.cloud import spanner

                params = {"opt": f"%{option_a}%", "limit": 3}
                param_types = {"opt": spanner.param_types.STRING, "limit": spanner.param_types.INT64}
                with db.snapshot() as snapshot:
                    res = list(snapshot.execute_sql(QUERY_TRADEOFFS, params=params, param_types=param_types))
                if res:
                    tradeoff_details = [f"• **{r[1]}**: {r[2]} vs {r[3]}: {r[4]}" for r in res]
                    analysis_block = "\n".join(tradeoff_details)
                    return TradeoffEvaluation(
                        option_a=option_a,
                        option_b=option_b,
                        latency_impact="Platform-native architectures colocate compute and context stores, eliminating cross-network latency penalties.",
                        complexity_impact=f"Comparative analysis across {len(res)} dimension(s):\n{analysis_block}",
                        security_posture="Managed Google Cloud foundations enforce Principal Access Boundaries (PAB) and workload identity federation natively.",
                        recommendation=f"Adopt {option_a} when enterprise SLA, audit compliance, and operational resilience outweigh self-managed custom stack maintenance.",
                    )
            except Exception as e:
                logger.warning(f"Spanner evaluate_tradeoffs query failed: {e}. Fallback to default.")

        return TradeoffEvaluation(
            option_a=option_a,
            option_b=option_b,
            latency_impact="Platform-native options reduce cross-network hops by leveraging Google colocation.",
            complexity_impact=f"Managing {option_b} requires custom maintenance, while {option_a} reduces operational overhead.",
            security_posture="Managed solutions enforce IAM and audit logs natively; self-managed requires explicit perimeter security.",
            recommendation=f"Prefer {option_a} for enterprise deployments prioritizing reliability and low operational toil.",
        )

    async def get_fde_rubric(
        self, domain: str | None = None, rubric_id: str | None = None, limit: int = 40
    ) -> list[dict[str, Any]]:
        """Retrieve Google Cloud FDE Rubric competencies from Cloud Spanner Graph."""
        db = self._get_spanner_db()
        if db is not None:
            try:
                from google.cloud import spanner

                params = {
                    "domain": f"%{domain}%" if domain else None,
                    "rubric_id": rubric_id,
                    "limit": limit,
                }
                param_types = {
                    "domain": spanner.param_types.STRING,
                    "rubric_id": spanner.param_types.STRING,
                    "limit": spanner.param_types.INT64,
                }
                with db.snapshot() as snapshot:
                    res = list(snapshot.execute_sql(QUERY_RUBRIC_ITEMS, params=params, param_types=param_types))
                return [
                    {
                        "rubric_id": r[0],
                        "domain": r[1],
                        "sub_competency": r[2],
                        "level_2_criteria": r[3],
                        "level_3_criteria": r[4],
                    }
                    for r in res
                ]
            except Exception as e:
                logger.warning(f"Spanner get_fde_rubric failed: {e}")

        # Fallback to dynamically hydrated 37 FDE rubric items
        if self._rubric_items:
            items = self._rubric_items
            if rubric_id:
                items = [i for i in items if i.get("rubric_id") == rubric_id]
            if domain:
                d_low = domain.lower()
                items = [i for i in items if d_low in i.get("domain", "").lower() or d_low in i.get("sub_competency", "").lower()]
            return items[:limit]

        return [
            {
                "rubric_id": "RUBRIC-A-1",
                "domain": "Part A: Presentation & Advisory Rigor",
                "sub_competency": "Strategic Delivery & Value Articulation",
                "level_3_summary": "Articulates crisp business value, ROI bounds, executive stakeholder synthesis.",
            },
            {
                "rubric_id": "RUBRIC-B-3-1",
                "domain": "Domain B.3: Security, Privacy & Compliance",
                "sub_competency": "Zero Trust & Least Privilege Architecture",
                "level_3_summary": "Enforces Zero Ambient Authority, Model Armor, Principal Access Boundaries.",
            },
        ]

    async def query_rubric_enforcement(
        self, rubric_id: str | None = None, keyword: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Traverse the ENFORCES_RUBRIC property graph edge to find guidelines enforcing a rubric competency."""
        db = self._get_spanner_db()
        if db is not None:
            try:
                from google.cloud import spanner

                params = {"rubric_id": rubric_id or "", "keyword": f"%{keyword or ''}%", "limit": limit}
                param_types = {
                    "rubric_id": spanner.param_types.STRING,
                    "keyword": spanner.param_types.STRING,
                    "limit": spanner.param_types.INT64,
                }
                with db.snapshot() as snapshot:
                    res = list(snapshot.execute_sql(QUERY_RUBRIC_ENFORCEMENT, params=params, param_types=param_types))
                return [
                    {
                        "guideline_id": r[0],
                        "title": r[1],
                        "category": r[2],
                        "enforcement_level": r[3],
                        "notes": r[4],
                        "rubric_id": r[5],
                        "sub_competency": r[6],
                    }
                    for r in res
                ]
            except Exception as e:
                logger.warning(f"Spanner query_rubric_enforcement failed: {e}")

        # Fallback to dynamically hydrated rubric enforcement edges
        if self._rubric_edges:
            g_map = {g.guideline_id: g for g in self._guidelines}
            r_map = {r.get("rubric_id"): r for r in self._rubric_items}
            matched = []
            kw = (keyword or "").lower()
            for edge in self._rubric_edges:
                rid = edge.get("rubric_id", "")
                gid = edge.get("guideline_id", "")
                if rubric_id and rid != rubric_id:
                    continue
                g_obj = g_map.get(gid)
                r_obj = r_map.get(rid, {})
                title = g_obj.title if g_obj else gid
                sub_comp = r_obj.get("sub_competency", rid)
                notes = edge.get("notes", "")
                if kw and kw not in title.lower() and kw not in sub_comp.lower() and kw not in notes.lower():
                    continue
                matched.append(
                    {
                        "guideline_id": gid,
                        "title": title,
                        "category": g_obj.category if g_obj else "architecture",
                        "enforcement_level": edge.get("enforcement_level", "REQUIRED"),
                        "notes": notes,
                        "rubric_id": rid,
                        "sub_competency": sub_comp,
                    }
                )
                if len(matched) >= limit:
                    break
            return matched
        return []

    async def traverse_pattern_mitigations(
        self, pattern_name: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Traverse MITIGATES edge from Pattern to Antipattern in Spanner Graph."""
        db = self._get_spanner_db()
        if db is not None:
            try:
                from google.cloud import spanner

                params = {"pattern_name": f"%{pattern_name}%", "limit": limit}
                param_types = {
                    "pattern_name": spanner.param_types.STRING,
                    "limit": spanner.param_types.INT64,
                }
                with db.snapshot() as snapshot:
                    res = list(snapshot.execute_sql(QUERY_PATTERN_MITIGATIONS, params=params, param_types=param_types))
                return [
                    {
                        "pattern_name": r[0],
                        "antipattern_name": r[1],
                        "hazard": r[2],
                        "remedy": r[3],
                        "rationale": r[4],
                    }
                    for r in res
                ]
            except Exception as e:
                logger.warning(f"Spanner traverse_pattern_mitigations failed: {e}")
        return []

    async def hybrid_search_guidelines(
        self,
        query: str,
        category: str | None = None,
        limit: int = 5,
        rrf_k: int = 60,
    ) -> list[dict[str, Any]]:
        """Hybrid retrieval combining lexical token matching and category/graph affinity via Reciprocal Rank Fusion (RRF).

        Fuses two complementary ranking signals:
        1. Lexical BM25-style token overlap over title, summary, and guideline_id.
        2. Semantic/structural affinity over category and linked architectural pattern terms.
        """
        import re

        tokens = [t for t in re.findall(r"[a-z0-9_]+", query.lower()) if len(t) > 1]
        candidates = [
            g for g in self._guidelines
            if not category or g.category.lower() == category.lower()
        ]
        if not candidates:
            candidates = list(self._guidelines)

        # Rank 1: Lexical token frequency score (title weighted 2x, summary 1x)
        lexical_scored: list[tuple[float, Guideline]] = []
        for g in candidates:
            title_l = g.title.lower()
            summary_l = g.summary.lower()
            score = sum(
                (2.0 if tok in title_l else 0.0) + (1.0 if tok in summary_l else 0.0)
                for tok in tokens
            )
            lexical_scored.append((score, g))
        lexical_scored.sort(key=lambda x: x[0], reverse=True)

        # Rank 2: Structural / category / pattern-link affinity score
        pattern_terms = {p.name.lower(): p.category.lower() for p in self._patterns.values()}
        semantic_scored: list[tuple[float, Guideline]] = []
        for g in candidates:
            aff = 0.0
            cat_l = g.category.lower()
            if any(tok in cat_l for tok in tokens):
                aff += 2.0
            for pname, pcat in pattern_terms.items():
                if any(tok in pname for tok in tokens) and pcat == cat_l:
                    aff += 1.5
            # Phrase match boost
            if query.lower() in g.title.lower() or query.lower() in g.summary.lower():
                aff += 3.0
            semantic_scored.append((aff, g))
        semantic_scored.sort(key=lambda x: x[0], reverse=True)

        # Reciprocal Rank Fusion: RRF(d) = sum(1 / (k + rank_i(d)))
        rrf_scores: dict[str, float] = {}
        guideline_map: dict[str, Guideline] = {}
        for rank, (_, g) in enumerate(lexical_scored, start=1):
            rrf_scores[g.guideline_id] = rrf_scores.get(g.guideline_id, 0.0) + 1.0 / (rrf_k + rank)
            guideline_map[g.guideline_id] = g
        for rank, (_, g) in enumerate(semantic_scored, start=1):
            rrf_scores[g.guideline_id] = rrf_scores.get(g.guideline_id, 0.0) + 1.0 / (rrf_k + rank)
            guideline_map[g.guideline_id] = g

        ranked_ids = sorted(rrf_scores.keys(), key=lambda gid: rrf_scores[gid], reverse=True)[:limit]
        return [
            {
                "guideline_id": gid,
                "title": guideline_map[gid].title,
                "category": guideline_map[gid].category,
                "summary": guideline_map[gid].summary,
                "source_url": guideline_map[gid].source_url,
                "rrf_score": round(rrf_scores[gid], 6),
                "retrieval_mode": "hybrid_rrf",
            }
            for gid in ranked_ids
        ]

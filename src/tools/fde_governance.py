"""FastMCP tools for Google Cloud FDE Charter governance, auditing, and rubric enforcement."""

from __future__ import annotations

import re
import time
from typing import Any
from fastmcp import FastMCP
from src.graph.client import GraphClient
from src.otel_setup import get_tracer
from src.security.model_armor import model_armor

tracer = get_tracer("guidelines-mcp-server")

FDE_CHARTER_URL = "https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head"

# Canonical sub-competencies for FDE rubric evaluation
CANONICAL_RUBRIC_DOMAINS = {
    "Part A: Advisory Rigor": [
        ("RUBRIC-A-1", "Strategic Delivery & Value Articulation"),
        ("RUBRIC-A-2", "Customer Context & Architectural Grounding"),
        ("RUBRIC-A-3", "Tradeoff Articulation & Decision Records"),
    ],
    "Part B.1: Architecture": [
        ("RUBRIC-B-1-1", "Zero Ambient Authority (ZAA)"),
        ("RUBRIC-B-1-2", "Progressive Disclosure Context Management"),
        ("RUBRIC-B-1-3", "Tiered Storage Architecture (Spanner + BigQuery)"),
    ],
    "Part B.2: Quality & Evals": [
        ("RUBRIC-B-2-1", "Quality Flywheel & Golden Eval Datasets"),
        ("RUBRIC-B-2-2", "Trajectory Evaluation & LLM-as-a-Judge"),
        ("RUBRIC-B-2-3", "CI/CD Regression Quality Gates"),
    ],
    "Part B.3: Security & Identity": [
        ("RUBRIC-B-3-1", "Dual-Pass Model Armor (Ingress & Egress DLP)"),
        ("RUBRIC-B-3-2", "Principal Access Boundaries (PAB)"),
        ("RUBRIC-B-3-3", "Workforce Identity Federation (WIF) & Delegated OAuth"),
    ],
    "Part B.4: Observability": [
        ("RUBRIC-B-4-1", "OpenTelemetry Distributed Tracing"),
        ("RUBRIC-B-4-2", "Security Telemetry & Audit Logs"),
    ],
    "Part B.5: Operational Readiness": [
        ("RUBRIC-B-5-1", "Health Checks & Container Probes"),
        ("RUBRIC-B-5-2", "Automated IaC & Reproducible Deployments"),
    ],
}


def normalize_rubric_domain(domain: str | None) -> str | None:
    """Normalize user or agent domain queries into canonical Spanner Graph domain patterns."""
    if not domain:
        return None
    d_clean = domain.strip()
    code_match = re.search(r"\b([AB](?:\.\d+)?)\b", d_clean, re.IGNORECASE)
    if code_match:
        code = code_match.group(1).upper()
        if code == "A":
            return "Part A"
        return f"Domain {code}"
    lower = d_clean.lower()
    if "security" in lower:
        return "Security"
    if "advisory" in lower or "presentation" in lower:
        return "Part A"
    if "quality" in lower or "scoping" in lower:
        return "Domain B.2"
    if "reliability" in lower or "resilience" in lower:
        return "Domain B.4"
    if "performance" in lower or "cost" in lower:
        return "Domain B.5"
    if "operation" in lower:
        return "Domain B.6"
    if "change" in lower:
        return "Domain B.7"
    return d_clean


def register_fde_governance_tools(mcp: FastMCP, client: GraphClient) -> None:
    """Register FDE Charter governance and rubric enforcement tools with FastMCP."""

    @mcp.tool()
    async def query_fde_charter_best_practices(
        domain: str | None = None,
        competency: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve official Google Cloud FDE Charter engineering standards and rubric criteria.

        Args:
            domain: FDE domain ('Part A: Advisory Rigor', 'Part B.1: Architecture', 'Part B.2: Quality', 'Part B.3: Security', 'Part B.4: Observability', 'Part B.5: Operational Readiness').
            competency: Keyword for sub-competency (e.g., 'Zero Ambient Authority', 'Model Armor', 'Progressive Disclosure').

        Returns:
            Structured envelope containing rubric criteria (Levels 0-3), disqualifier conditions, and enforcing concepts.
        """
        with tracer.start_as_current_span("tools/call:query_fde_charter_best_practices") as span:
            span.set_attribute("tool.name", "query_fde_charter_best_practices")
            if domain:
                span.set_attribute("filter.domain", domain)
            if competency:
                span.set_attribute("filter.competency", competency)

            # Ingress security check
            safety = await model_armor.sanitize(f"{domain or ''} {competency or ''}")
            if not safety.is_safe:
                return {
                    "status": "blocked",
                    "error": safety.error_message or "Request blocked by Model Armor.",
                    "source": "model_armor",
                }

            start_time = time.perf_counter()
            norm_domain = normalize_rubric_domain(domain)
            rubric_items = await client.get_fde_rubric(domain=norm_domain)

            # Filter by competency keyword if provided
            if competency:
                kw = competency.lower()
                rubric_items = [
                    item for item in rubric_items
                    if kw in item.get("sub_competency", "").lower()
                    or kw in item.get("domain", "").lower()
                    or kw in str(item).lower()
                ]

            # Cross-reference enforcing guidelines from Spanner Graph
            enriched_items = []
            for item in rubric_items[:15]:
                enforcing = await client.query_rubric_enforcement(rubric_id=item.get("rubric_id"))
                enriched_items.append({
                    **item,
                    "enforcing_guidelines_count": len(enforcing),
                    "enforcing_guidelines": [e.get("guideline_id") for e in enforcing[:5]],
                })

            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("result.count", len(enriched_items))

            return {
                "status": "success",
                "charter_reference": FDE_CHARTER_URL,
                "domain_filter": domain,
                "competency_filter": competency,
                "latency_ms": round(elapsed, 2),
                "total_items": len(enriched_items),
                "rubric_items": enriched_items,
            }

    @mcp.tool()
    async def audit_project_against_fde_rubric(
        project_manifest_or_description: str,
        target_domains: list[str] | None = None,
    ) -> dict[str, Any]:
        """Evaluate an architecture or codebase against the Google Cloud FDE Field-Readiness Rubric.

        Args:
            project_manifest_or_description: Detailed markdown summary of architecture, components, security, and tests.
            target_domains: Optional list of domains to restrict audit to (defaults to all domains).

        Returns:
            Scorecard containing per-competency ratings (0.0 - 3.0), composite score, pass/fail status (cutline >= 2.0),
            disqualifiers detected, and prioritized remediation actions.
        """
        with tracer.start_as_current_span("tools/call:audit_project_against_fde_rubric") as span:
            span.set_attribute("tool.name", "audit_project_against_fde_rubric")

            # Ingress check
            safety = await model_armor.sanitize(project_manifest_or_description[:1000])
            if not safety.is_safe:
                return {
                    "status": "blocked",
                    "error": safety.error_message or "Request blocked by Model Armor.",
                    "source": "model_armor",
                }

            start_time = time.perf_counter()
            desc_lower = project_manifest_or_description.lower()

            # 1. Critical Disqualifiers Detection (0-score triggers)
            disqualifiers: list[str] = []
            if re.search(r"\bAIza[0-9A-Za-z\-_]{20,}\b", project_manifest_or_description) or "hardcoded api key" in desc_lower:
                disqualifiers.append("DISQUALIFIER-SEC-01: Hardcoded credentials or API keys present in codebase/manifest.")
            if "allow_unauthenticated = true" in desc_lower or "unauthenticated public access" in desc_lower:
                disqualifiers.append("DISQUALIFIER-SEC-02: Public unauthenticated endpoint without IAM or OAuth protection.")
            if "no tests" in desc_lower or "zero evals" in desc_lower or "no evaluation" in desc_lower:
                disqualifiers.append("DISQUALIFIER-QA-01: Zero automated evaluations or regression tests defined.")
            if "all-powerful service account" in desc_lower or "ambient owner role" in desc_lower:
                disqualifiers.append("DISQUALIFIER-IAM-01: Monolithic ambient authority service account with excessive permissions.")

            # 2. Evaluate Scores per Domain
            domains_to_evaluate = target_domains or list(CANONICAL_RUBRIC_DOMAINS.keys())
            domain_scores: dict[str, float] = {}
            competency_scores: list[dict[str, Any]] = []

            for dom, competencies in CANONICAL_RUBRIC_DOMAINS.items():
                if dom not in domains_to_evaluate:
                    continue
                scores_in_domain: list[float] = []

                for r_id, sub_comp in competencies:
                    score = 1.0  # Default baseline
                    reasons: list[str] = []

                    # Heuristic domain grading based on presence of key architectural constructs
                    if "Zero Ambient Authority" in sub_comp:
                        if "delegated oauth" in desc_lower or "workforce identity" in desc_lower or "zaa" in desc_lower:
                            score = 2.5
                            reasons.append("Employs delegated credentials and avoids static ambient authority.")
                        elif "service account" in desc_lower:
                            score = 1.5
                            reasons.append("Uses service account without explicit token downscoping.")
                    elif "Progressive Disclosure" in sub_comp:
                        if "progressive disclosure" in desc_lower or "context window" in desc_lower or "two-tier" in desc_lower:
                            score = 2.5
                            reasons.append("Context management protects agent token budget.")
                        else:
                            score = 1.0
                            reasons.append("Tools may cause context bloating without progressive disclosure.")
                    elif "Tiered Storage" in sub_comp:
                        if "spanner" in desc_lower and "bigquery" in desc_lower:
                            score = 3.0
                            reasons.append("Multi-tier storage: Spanner Graph for operational GQL + BigQuery for analytics.")
                        elif "spanner" in desc_lower or "bigquery" in desc_lower:
                            score = 2.0
                            reasons.append("Single tier database leveraged.")
                    elif "Quality Flywheel" in desc_lower or "Golden Eval" in sub_comp:
                        if "eval" in desc_lower and ("dataset" in desc_lower or "benchmark" in desc_lower):
                            score = 2.5
                            reasons.append("Grounded eval dataset and quality flywheel defined.")
                        else:
                            score = 1.0
                            reasons.append("Lacks structured golden eval dataset.")
                    elif "Trajectory Evaluation" in sub_comp:
                        if "trajectory" in desc_lower or "llm-as-a-judge" in desc_lower or "auto-rater" in desc_lower:
                            score = 2.5
                            reasons.append("Multi-turn trajectory evaluations and auto-raters configured.")
                        else:
                            score = 1.0
                            reasons.append("Single-turn evaluation only; multi-turn trajectory validation needed.")
                    elif "Model Armor" in sub_comp:
                        if "model armor" in desc_lower and ("egress" in desc_lower or "dlp" in desc_lower):
                            score = 3.0
                            reasons.append("Dual-pass Model Armor with ingress prompt sanitization and egress DLP.")
                        elif "model armor" in desc_lower or "sanitiz" in desc_lower:
                            score = 2.0
                            reasons.append("Ingress sanitization enabled; egress DLP needed.")
                    elif "Principal Access Boundaries" in sub_comp:
                        if "principal access boundaries" in desc_lower or "pab" in desc_lower:
                            score = 2.5
                            reasons.append("PAB perimeters restrict lateral token abuse.")
                        else:
                            score = 1.0
                            reasons.append("PAB policies not explicitly declared.")
                    elif "OpenTelemetry" in sub_comp:
                        if "opentelemetry" in desc_lower or "cloud trace" in desc_lower or "tracing" in desc_lower:
                            score = 2.5
                            reasons.append("Distributed tracing active across spans.")
                        else:
                            score = 1.0
                            reasons.append("Tracing instrumentation missing.")
                    elif "Health Checks" in sub_comp:
                        if "healthcheck" in desc_lower or "health probe" in desc_lower or "/health" in desc_lower:
                            score = 3.0
                            reasons.append("Active health endpoints and container readiness probes configured.")
                        else:
                            score = 1.5
                            reasons.append("Health probes need verification.")
                    else:
                        score = 2.0
                        reasons.append("Meets standard production requirements.")

                    # Disqualifier overrides
                    if disqualifiers and score > 1.0:
                        score = max(0.0, score - 1.0)

                    scores_in_domain.append(score)
                    competency_scores.append({
                        "rubric_id": r_id,
                        "domain": dom,
                        "sub_competency": sub_comp,
                        "score": score,
                        "reasons": reasons,
                    })

                domain_scores[dom] = round(sum(scores_in_domain) / max(len(scores_in_domain), 1), 2)

            all_scores = [c["score"] for c in competency_scores]
            composite_score = round(sum(all_scores) / max(len(all_scores), 1), 2)

            # 3. Determine Field Readiness Status
            is_ready = composite_score >= 2.0 and len(disqualifiers) == 0
            if disqualifiers:
                status_verdict = "DISQUALIFIED_IMMEDIATE_PAUSE"
            elif is_ready:
                status_verdict = "FIELD_READY_PRODUCTION_APPROVED"
            else:
                status_verdict = "ACTION_REQUIRED_BELOW_CUTLINE"

            # 4. Generate Remediation Roadmap
            remediations = []
            if disqualifiers:
                for d in disqualifiers:
                    remediations.append({"priority": "P0 (Blocker)", "action": f"Resolve critical disqualifier: {d}"})
            for comp in competency_scores:
                if comp["score"] < 2.0:
                    remediations.append({
                        "priority": "P1 (Target Sprint)" if comp["score"] <= 1.0 else "P2 (Enhancement)",
                        "action": f"Upgrade [{comp['rubric_id']}] {comp['sub_competency']} to Level 2.0+: {', '.join(comp['reasons'])}",
                    })

            # 5. Format GFM Markdown Table Scorecard
            scorecard_lines = [
                "### 📋 Google Cloud FDE Field-Readiness Scorecard",
                f"**Verdict:** `{status_verdict}` | **Composite Score:** `{composite_score} / 3.0` (Production Bar: `>= 2.0`)",
                f"**Charter Standard:** [{FDE_CHARTER_URL}]({FDE_CHARTER_URL})\n",
                "| Domain | Sub-Competency | Score (0-3) | Key Findings |",
                "|---|---|:---:|---|",
            ]
            for c in competency_scores:
                scorecard_lines.append(
                    f"| {c['domain']} | **{c['sub_competency']}** | `{c['score']}` | {'; '.join(c['reasons'])} |"
                )
            scorecard_md = "\n".join(scorecard_lines)

            elapsed = (time.perf_counter() - start_time) * 1000
            span.set_attribute("audit.composite_score", composite_score)
            span.set_attribute("audit.status", status_verdict)

            return {
                "status": "success",
                "verdict": status_verdict,
                "composite_score": composite_score,
                "production_cutline_met": is_ready,
                "disqualifiers_detected": disqualifiers,
                "domain_scores": domain_scores,
                "competency_evaluations": competency_scores,
                "remediation_roadmap": remediations,
                "scorecard_markdown": scorecard_md,
                "latency_ms": round(elapsed, 2),
            }

    @mcp.tool()
    async def search_fde_charter_best_practices(query: str) -> dict[str, Any]:
        """Search the FDE Charter knowledge base and Concept 00 for specific engineering guidelines.

        Args:
            query: Keyword query (e.g., 'Model Armor egress', 'ZAA', 'Quality Flywheel', 'Auto-Rater').

        Returns:
            Matching guidelines, rubric competencies, and direct links to enforcing concepts.
        """
        with tracer.start_as_current_span("tools/call:search_fde_charter_best_practices") as span:
            span.set_attribute("tool.name", "search_fde_charter_best_practices")
            span.set_attribute("query", query)

            safety = await model_armor.sanitize(query)
            if not safety.is_safe:
                return {
                    "status": "blocked",
                    "error": safety.error_message or "Blocked by Model Armor",
                    "source": "model_armor",
                }

            start_time = time.perf_counter()
            guidelines = await client.search_guidelines(query=query, limit=5)
            rubric_matches = await client.query_rubric_enforcement(keyword=query, limit=5)

            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "status": "success",
                "query": query,
                "charter_reference": FDE_CHARTER_URL,
                "guidelines_found": [
                    {
                        "id": g.guideline_id,
                        "title": g.title,
                        "category": g.category,
                        "summary": g.summary,
                    }
                    for g in guidelines
                ],
                "rubric_enforcements": rubric_matches,
                "latency_ms": round(elapsed, 2),
            }

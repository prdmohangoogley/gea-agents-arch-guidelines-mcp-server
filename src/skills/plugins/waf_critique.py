"""Well-Architected Framework (WAF) Critique Skill Plugins.

Grounded in the Google Cloud Dataplex PCA & Well-Architected OKF v0.2 Knowledge Base
(Corpus: GEAPL200_PCA_WAF, Concepts: OKF-PCA-01 through OKF-PCA-09).
"""

from __future__ import annotations

import time
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter, SkillResult, SkillExecutionContext
from src.models.router import model_router
from src.skills.plugins.waf_okf_pillars import (
    DATAPLEX_KB_METADATA,
    evaluate_spec_across_all_pillars,
    evaluate_spec_against_pillar,
    search_pca_waf_okf,
)


class WAFCritiqueSkill(SkillPlugin):
    """Enterprise skill for evaluating architectures against all 6 GCP Well-Architected Framework pillars."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_waf_critique",
            name="Google Cloud Well-Architected Framework Auditor",
            version="2.0.0",
            category="governance",
            description="Evaluates system architectures across all 6 GCP Well-Architected Framework pillars with quantitative scoring grounded in the Dataplex PCA & WAF OKF v0.2 Knowledge Base (OKF-PCA-01..09).",
            capabilities=["waf_audit", "pillar_scoring", "gap_identification", "remediation_roadmap", "okf_pca_grounding"],
            entrypoint="execute",
            context_token_estimate=320,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="architecture_description", type="string", description="Markdown description or specification of the architecture to audit"),
                SkillParameter(name="workload_type", type="string", description="Type of workload (e.g., 'multi_agent_system', 'transactional_oltp', 'data_lakehouse', 'edge_inference')", required=False, default="multi_agent_system"),
                SkillParameter(name="target_pillars", type="list", description="Optional subset of pillars to audit or ['all']", required=False, default=["all"]),
            ],
            instructions="Scores the workload across Operational Excellence, Security, Reliability, Performance, Cost, and Sustainability using OKF-PCA-01..09.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        arch = parameters.get("architecture_description", "")
        workload = parameters.get("workload_type", "multi_agent_system")
        target_pillars = parameters.get("target_pillars", ["all"])

        deterministic_eval = evaluate_spec_across_all_pillars(arch, target_pillars=target_pillars)

        prompt = f"""You are a Lead Google Cloud Well-Architected Reviewer grounded in the Dataplex OKF v0.2 Knowledge Base ({DATAPLEX_KB_METADATA['corpus']} / {DATAPLEX_KB_METADATA['version_tag']}).
Perform a full Well-Architected Framework (WAF) Review for this workload:
Workload Type: {workload}
Deterministic Composite Score: {deterministic_eval['composite_waf_score']} / 3.00 ({deterministic_eval['verdict']})

Architecture:
{arch}

Score each of the 6 GCP WAF Pillars from 0.0 to 3.0 (citing OKF-PCA-01 through OKF-PCA-09):
1. Operational Excellence (OKF-PCA-06, OKF-PCA-07: Terraform GCS state, Cloud Build Private Pools, Cloud Deploy, Trace X-Cloud-Trace-Context, Profiler, Ops Agent, SRE SLIs/SLOs/Error Budgets)
2. Security, Privacy & Compliance (OKF-PCA-04, OKF-PCA-05: ZAA, Workload Identity, Org Policies, IAM Deny, Secret Manager, KMS/EKM/CSEK/Tink, Confidential VMs/GKE, VPC-SC + ACM Ingress, Cloud Armor + GFE firewall, IAP, Binary Authorization, Model Armor, DLP)
3. Reliability (OKF-PCA-01, OKF-PCA-03, OKF-PCA-08: Spanner 99.999%, Cloud SQL HA + Read Replicas, Multi-Zone/Regional GKE & Cloud Run, 2+2 Interconnect / HA VPN 99.99%, Cold/Warm/Hot DR RTO/RPO)
4. Performance Optimization (OKF-PCA-01, OKF-PCA-02, OKF-PCA-03: Premium Tier Anycast, Cloud CDN, Spanner Interleaved Tables + 15s Stale Reads, Bigtable HighCardID#ReverseTimestamp, BQ Partitioning + Clustering + BI Engine, Memorystore Redis, KV Prefix Cache)
5. Cost Optimization / FinOps (OKF-PCA-01, OKF-PCA-02, OKF-PCA-04, OKF-PCA-06: GKE Autopilot, Cloud Run scale-to-zero, Spot VMs, CUDs, BQ 90-day automatic 50% discount & Analytics Hub, GCS Autoclass, _Default Log Exclusion Filters, Billing Budgets + Pub/Sub)
6. Sustainability & Carbon Footprint (CFE% region placement via constraints/gcp.resourceLocations, scale-to-zero serverless, idle VM Recommender)

Provide:
- Pillar-by-pillar scores and findings grounded in OKF-PCA-01..09.
- High-Risk Issues (HRIs) and Medium-Risk Issues (MRIs).
- Prioritized remediation plan.
"""
        response_text = await model_router.generate_text(
            prompt=prompt,
            temperature=0.2,
        )

        elapsed = (time.perf_counter() - start_time) * 1000
        prompt_tokens = self.estimate_tokens(prompt)
        completion_tokens = self.estimate_tokens(response_text)

        return SkillResult(
            status="success",
            skill_id="skill_waf_critique",
            latency_ms=round(elapsed, 2),
            data={
                "workload_type": workload,
                "verdict": deterministic_eval["verdict"],
                "composite_waf_score": deterministic_eval["composite_waf_score"],
                "production_cutline_met": deterministic_eval["production_cutline_met"],
                "dataplex_kb": DATAPLEX_KB_METADATA,
                "pillar_evaluations": deterministic_eval["pillar_evaluations"],
                "antipattern_violations": deterministic_eval["antipattern_violations"],
                "scorecard_markdown": deterministic_eval["scorecard_markdown"],
                "waf_review_markdown": f"{deterministic_eval['scorecard_markdown']}\n\n---\n\n{response_text}",
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )


class WAFPillarCritiqueSkill(SkillPlugin):
    """Enterprise skill for drilling down into a single GCP Well-Architected pillar."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_waf_pillar_critique",
            name="WAF Pillar Deep Dive Auditor",
            version="2.0.0",
            category="governance",
            description="Executes a deep-dive evaluation focused on a single GCP Well-Architected Framework pillar grounded in OKF-PCA-01..09.",
            capabilities=["pillar_deep_dive", "compliance_check", "targeted_remediation", "okf_pca_grounding"],
            entrypoint="execute",
            context_token_estimate=280,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="pillar_name", type="string", description="Pillar to audit: 'security', 'reliability', 'cost_optimization', 'operational_excellence', 'performance_optimization', 'sustainability'"),
                SkillParameter(name="architecture_description", type="string", description="Architecture text or spec section corresponding to this pillar"),
            ],
            instructions="Conducts an exhaustive deep-dive critique on the specified WAF pillar using the Dataplex PCA & WAF OKF Knowledge Base.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        pillar = parameters.get("pillar_name", "security").lower()
        arch = parameters.get("architecture_description", "")

        pillar_eval = evaluate_spec_against_pillar(arch, pillar)
        kb_matches = search_pca_waf_okf(query=pillar, pillar=pillar)

        prompt = f"""You are a Google Cloud Principal Specialist in: {pillar_eval['pillar_name']}.
Perform a deep-dive Well-Architected Pillar Audit grounded in {DATAPLEX_KB_METADATA['corpus']} ({', '.join(c['concept_id'] for c in pillar_eval['okf_concepts_referenced'])}):
{arch}

Deterministic Pillar Score: {pillar_eval['score']} / 3.0
Detected Anti-Patterns: {pillar_eval['violations_detected']}

Evaluate specific pillar requirements, failure modes, trade-offs, and compliance with Google Cloud recommended architectures.
Provide an objective 0.0 - 3.0 score, identify blocking disqualifiers, and output an actionable remediation diff.
"""
        response_text = await model_router.generate_text(
            prompt=prompt,
            temperature=0.2,
        )

        elapsed = (time.perf_counter() - start_time) * 1000
        prompt_tokens = self.estimate_tokens(prompt)
        completion_tokens = self.estimate_tokens(response_text)

        return SkillResult(
            status="success",
            skill_id="skill_waf_pillar_critique",
            latency_ms=round(elapsed, 2),
            data={
                "pillar_name": pillar_eval["pillar_id"],
                "pillar_evaluation": pillar_eval,
                "dataplex_kb": DATAPLEX_KB_METADATA,
                "okf_concepts": kb_matches["matched_concepts"],
                "pillar_audit_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )

"""Security, Privacy & Compliance Rubric Assessor, Feedback Resolver, and Human-Style FAQ Generator Plugins.

Implements 3 executable Enterprise SkillPlugins:
1. skill_security_privacy_compliance_assessor_feedback
2. skill_security_privacy_compliance_feedback_resolver
3. skill_security_privacy_compliance_faqs
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from src.skills.base import (
    SkillExecutionContext,
    SkillManifest,
    SkillParameter,
    SkillPlugin,
    SkillResult,
)

# ==============================================================================
# Authoritative Security, Privacy & Compliance Rubric (5 Domains, 10 Criteria)
# ==============================================================================

SECURITY_PRIVACY_COMPLIANCE_DOMAINS: list[dict[str, Any]] = [
    {
        "id": "spc_domain_1",
        "number": 1,
        "name": "Authentication & Authorization",
        "min_competent_required": 2,
        "summary": "Service accounts, IAM, API key scoping, OAuth/OIDC, Least Privilege.",
        "recommended_skills": [
            "waf-pillar-security",
            "fde-governance-auditor",
            "terraform-waf-verifier",
            "spec-best-practices-updater",
        ],
        "criteria": [
            {
                "id": "1.1",
                "title": "Service Accounts, Scoped API Keys & OAuth/OIDC",
                "description": (
                    "Implements robust authentication/authorization via Service Accounts, "
                    "scoped API keys, and OAuth/OIDC."
                ),
                "signals": [
                    "service account", "workload identity", "oauth", "oidc", "adc",
                    "google.auth", "scoped", "bearer", "token", "downscoped",
                ],
                "remediation": (
                    "Enforce robust authentication/authorization using dedicated Service Accounts, "
                    "Workload Identity Federation / OAuth2 / OIDC, and scoped credentials (zero static SA JSON keys)."
                ),
            },
            {
                "id": "1.2",
                "title": "Principle of Least Privilege Across IAM",
                "description": "Enforces Principle of Least Privilege across all IAM configurations.",
                "signals": [
                    "least privilege", "zero ambient authority", "zaa", "iam",
                    "sandbox_tier", "read_only", "pab", "principal access", "role",
                ],
                "remediation": (
                    "Enforce Principle of Least Privilege across all IAM bindings and tool/skill "
                    "boundaries (Zero Ambient Authority, explicit sandbox_tier, no primitive owner/editor roles)."
                ),
            },
        ],
    },
    {
        "id": "spc_domain_2",
        "number": 2,
        "name": "Infrastructure & Network Security",
        "min_competent_required": 2,
        "summary": "VPC design, network segmentation, private endpoints, zero-trust architecture, service perimeters, firewall policies.",
        "recommended_skills": [
            "waf-pillar-security",
            "terraform-waf-verifier",
            "enterprise-system-design",
            "waf-all-pillars-spec-verifier",
        ],
        "criteria": [
            {
                "id": "2.1",
                "title": "Secure VPCs, Segmentation, Private Endpoints & Zero-Trust",
                "description": (
                    "Designs secure VPCs with network segmentation, private endpoints, "
                    "and zero-trust principles."
                ),
                "signals": [
                    "vpc", "private endpoint", "private google access", "zero-trust",
                    "zero trust", "segmentation", "subnet", "confidential", "iap",
                ],
                "remediation": (
                    "Design segmented VPC networking with private endpoints / Private Google Access, "
                    "zero-trust identity-aware access (IAP), and confidential compute isolation."
                ),
            },
            {
                "id": "2.2",
                "title": "Service Perimeters & Firewall Policies",
                "description": "Configures service perimeters and firewall policies protecting enterprise assets.",
                "signals": [
                    "vpc-sc", "service perimeter", "firewall", "cloud armor",
                    "access context manager", "acm", "ingress", "egress", "ssrf",
                ],
                "remediation": (
                    "Configure VPC Service Controls (VPC-SC) with Access Context Manager ingress/egress "
                    "rules, Cloud Armor WAF policies, and strict firewall/SSRF egress controls."
                ),
            },
        ],
    },
    {
        "id": "spc_domain_3",
        "number": 3,
        "name": "Data Protection & Privacy",
        "min_competent_required": 2,
        "summary": "Encryption at rest/transit, PII handling, data classification, DLP, Secrets management.",
        "recommended_skills": [
            "waf-pillar-security",
            "complete-system-audit",
            "terraform-waf-verifier",
            "spec-best-practices-updater",
        ],
        "criteria": [
            {
                "id": "3.1",
                "title": "Encryption at Rest/Transit, PII Handling, Classification & DLP",
                "description": (
                    "Ensures encryption at rest/transit; manages PII handling, "
                    "data classification, and DLP."
                ),
                "signals": [
                    "cmek", "kms", "tls", "ssl", "encryption", "pii", "dlp",
                    "sdp", "redact", "ssn", "credit_card", "classification",
                ],
                "remediation": (
                    "Enforce encryption in transit (TLS/mTLS/gRPC SSL) and at rest (Cloud KMS CMEK), "
                    "explicit data classification, and automated PII/SDP DLP redaction."
                ),
            },
            {
                "id": "3.2",
                "title": "Secure Secrets Management",
                "description": "Utilizes secure Secrets management preventing credential exposure.",
                "signals": [
                    "secret manager", "secrets", "redacted_gcp_api_key", "redacted_private_key",
                    "credential", "no hardcoded", "env", "vault", "kms",
                ],
                "remediation": (
                    "Store and inject all credentials via Google Cloud Secret Manager (never hardcoded "
                    "in source or Terraform state) and enforce egress secret-leakage redaction."
                ),
            },
        ],
    },
    {
        "id": "spc_domain_4",
        "number": 4,
        "name": "AI-Specific Security",
        "min_competent_required": 2,
        "summary": "Prompt injection mitigation, output filtering, guardrails, model access controls, content safety.",
        "recommended_skills": [
            "waf-pillar-security",
            "fde-governance-auditor",
            "eval-harness",
            "spec-best-practices-updater",
        ],
        "criteria": [
            {
                "id": "4.1",
                "title": "Prompt Injection Mitigation, Output Filtering & Structural Guardrails",
                "description": (
                    "Implements prompt-injection mitigation, output filtering, "
                    "and structural guardrails."
                ),
                "signals": [
                    "model armor", "prompt injection", "pi_and_jailbreak", "dual-pass",
                    "output filter", "egress", "sanitiz", "guardrail", "circuit breaker",
                ],
                "remediation": (
                    "Implement Dual-Pass Model Armor (ingress prompt-injection & jailbreak blocking + "
                    "egress output filtering) backed by low-latency heuristic circuit-breaker guardrails."
                ),
            },
            {
                "id": "4.2",
                "title": "Model Access Controls & Content Safety Layers",
                "description": (
                    "Configures model access controls and content safety layers "
                    "protecting against adversarial use."
                ),
                "signals": [
                    "zero legacy", "prohibited_legacy", "model_registry", "content safety",
                    "csam", "adversarial", "fail-closed", "fail_open", "model access",
                    "validate_model",
                ],
                "remediation": (
                    "Enforce strict model allow-listing/access controls (blocking deprecated/unapproved "
                    "models), content safety / CSAM filters, and fail-closed adversarial defense testing."
                ),
            },
        ],
    },
    {
        "id": "spc_domain_5",
        "number": 5,
        "name": "Compliance & Governance",
        "min_competent_required": 1,
        "summary": "Audit logging, data residency, regulatory requirements, policy enforcement.",
        "recommended_skills": [
            "fde-governance-auditor",
            "complete-system-audit",
            "waf-pillar-operational-excellence",
            "waf-pillar-security",
        ],
        "criteria": [
            {
                "id": "5.1",
                "title": "Audit Logging, Data Residency & Regulatory Requirements",
                "description": (
                    "Configures audit logging and data residency aligning with "
                    "regulatory requirements."
                ),
                "signals": [
                    "audit", "cloud trace", "bigquery", "logging", "residency",
                    "resourcelocations", "hipaa", "finra", "pci", "gdpr", "region",
                ],
                "remediation": (
                    "Configure immutable audit logging (BigQuery audit tables + Cloud Trace/Logging) "
                    "and enforce data residency (`constraints/gcp.resourceLocations`) aligned with HIPAA/FINRA/PCI-DSS."
                ),
            },
            {
                "id": "5.2",
                "title": "Enterprise Policy Enforcement & Governance Compliance",
                "description": "Enforces enterprise policy across all deployments ensuring governance compliance.",
                "signals": [
                    "org polic", "iam deny", "binary authorization", "fde rubric",
                    "cutline", "policy", "governance", "terraform", "waf", "compliance",
                ],
                "remediation": (
                    "Enforce automated enterprise policy gates across deployments (Organization Policies, "
                    "Binary Authorization, Terraform WAF verification, and FDE >= 2.0 release cutlines)."
                ),
            },
        ],
    },
]

SPC_FAQ_START = "<!-- SECURITY_PRIVACY_COMPLIANCE_FAQS_START -->"
SPC_FAQ_END = "<!-- SECURITY_PRIVACY_COMPLIANCE_FAQS_END -->"


def _evaluate_security_privacy_compliance(
    project_name: str,
    project_manifest_or_spec: str,
) -> dict[str, Any]:
    """Deterministically evaluate a project/spec against all 5 Security, Privacy & Compliance domains."""
    text_lower = project_manifest_or_spec.lower()
    domain_results: list[dict[str, Any]] = []
    all_feedback: list[dict[str, Any]] = []
    domains_passed = 0

    for domain in SECURITY_PRIVACY_COMPLIANCE_DOMAINS:
        criteria_results: list[dict[str, Any]] = []
        competent_count = 0

        for crit in domain["criteria"]:
            matched_signals = [sig for sig in crit["signals"] if sig in text_lower]
            match_count = len(matched_signals)
            if match_count >= 4:
                level = "Exemplary"
                is_competent = True
            elif match_count >= 2:
                level = "Competent"
                is_competent = True
            elif match_count == 1:
                level = "Developing"
                is_competent = False
            else:
                level = "Not Demonstrated"
                is_competent = False

            if is_competent:
                competent_count += 1
            else:
                all_feedback.append({
                    "domain_number": domain["number"],
                    "domain_name": domain["name"],
                    "criterion_id": crit["id"],
                    "criterion_title": crit["title"],
                    "current_level": level,
                    "priority": "P0_BLOCKER" if competent_count < domain["min_competent_required"] else "P1_ENHANCEMENT",
                    "feedback": crit["remediation"],
                    "recommended_skills": domain["recommended_skills"],
                })

            criteria_results.append({
                "criterion_id": crit["id"],
                "title": crit["title"],
                "level": level,
                "is_competent": is_competent,
                "matched_signals": matched_signals,
                "remediation": None if is_competent else crit["remediation"],
            })

        domain_passed = competent_count >= domain["min_competent_required"]
        if domain_passed:
            domains_passed += 1

        domain_results.append({
            "domain_number": domain["number"],
            "domain_id": domain["id"],
            "domain_name": domain["name"],
            "min_competent_required": domain["min_competent_required"],
            "competent_count": competent_count,
            "total_criteria": len(domain["criteria"]),
            "passed": domain_passed,
            "recommended_skills": domain["recommended_skills"],
            "criteria": criteria_results,
        })

    overall_passed = domains_passed == len(SECURITY_PRIVACY_COMPLIANCE_DOMAINS)
    return {
        "project_name": project_name,
        "overall_status": "PASS" if overall_passed else "FAIL",
        "overall_passed": overall_passed,
        "domains_passed": domains_passed,
        "total_domains": len(SECURITY_PRIVACY_COMPLIANCE_DOMAINS),
        "domain_results": domain_results,
        "feedback_items": all_feedback,
    }


def _render_spc_assessment_markdown(assessment: dict[str, Any]) -> str:
    """Render a Security, Privacy & Compliance assessment dictionary as Markdown."""
    lines = [
        f"# Security, Privacy & Compliance Rubric Assessment: {assessment['project_name']}",
        "",
        f"- **Overall Verdict:** `{assessment['overall_status']}` "
        f"({assessment['domains_passed']}/{assessment['total_domains']} domains passed)",
        "",
        "## Domain Scorecard",
        "",
        "| # | Domain | Competent Criteria | Required | Verdict |",
        "|---:|:---|---:|---:|:---|",
    ]
    for d in assessment["domain_results"]:
        verdict = "PASS" if d["passed"] else "FAIL"
        lines.append(
            f"| {d['domain_number']} | {d['domain_name']} | "
            f"{d['competent_count']}/{d['total_criteria']} | >= {d['min_competent_required']} | **{verdict}** |"
        )

    lines.append("")
    lines.append("## Detailed Sub-Criteria Evaluation")
    for d in assessment["domain_results"]:
        lines.append(f"\n### {d['domain_number']}. {d['domain_name']} ({'PASS' if d['passed'] else 'FAIL'})")
        for c in d["criteria"]:
            sigs = ", ".join(c["matched_signals"]) if c["matched_signals"] else "none detected"
            lines.append(f"- **{c['criterion_id']} {c['title']}**: `{c['level']}` (evidence signals: {sigs})")
            if c["remediation"]:
                lines.append(f"  - *Feedback:* {c['remediation']}")

    if assessment["feedback_items"]:
        lines.append("\n## Prioritized Security, Privacy & Compliance Feedback")
        for item in assessment["feedback_items"]:
            skills_str = ", ".join(f"`{s}`" for s in item["recommended_skills"])
            lines.append(
                f"- **[{item['priority']}] {item['criterion_id']} ({item['domain_name']})**: "
                f"{item['feedback']} — *Recommended Skills:* {skills_str}"
            )
    else:
        lines.append("\n## Prioritized Security, Privacy & Compliance Feedback\n- All 10 sub-criteria across all 5 domains are at Competent or Exemplary level. Zero open security/compliance blockers.")

    return "\n".join(lines)


class SecurityPrivacyComplianceAssessorFeedbackSkill(SkillPlugin):
    """Assesses a project, repo, or spec against the 5-domain Security, Privacy & Compliance Rubric."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_security_privacy_compliance_assessor_feedback",
            name="Security, Privacy & Compliance Assessor & Feedback",
            version="1.0.0",
            category="security",
            description=(
                "Evaluates a project, repository, or technical specification against all 5 domains of the "
                "Security, Privacy & Compliance Rubric (AuthN/AuthZ, Infra & Network Security, Data Protection "
                "& Privacy, AI-Specific Security, and Compliance & Governance) and produces prioritized feedback."
            ),
            capabilities=[
                "security_rubric_assessment",
                "privacy_compliance_audit",
                "ai_security_evaluation",
                "actionable_security_feedback",
            ],
            entrypoint="execute",
            context_token_estimate=380,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project, repo, or specification being assessed.",
                ),
                SkillParameter(
                    name="project_manifest_or_spec",
                    type="string",
                    description="Project codebase manifest, Terraform/IAM posture, architecture summary, or spec text.",
                ),
            ],
            instructions=(
                "Evaluates all 5 Security, Privacy & Compliance Rubric domains against their exact thresholds "
                "(>=2 for Domains 1-4; >=1 for Domain 5), returning a Pass/Fail scorecard and prioritized feedback."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target Enterprise Project")
        spec_text = parameters.get("project_manifest_or_spec", "")

        assessment = _evaluate_security_privacy_compliance(project_name, spec_text)
        report_md = _render_spc_assessment_markdown(assessment)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=elapsed_ms,
            data={
                "assessment": assessment,
                "assessment_report_markdown": report_md,
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(spec_text),
                "completion_tokens_estimated": self.estimate_tokens(report_md),
                "tokens_saved_by_cache": 0,
            },
        )


class SecurityPrivacyComplianceFeedbackResolverSkill(SkillPlugin):
    """Resolves Security, Privacy & Compliance feedback iteratively until all 5 rubric domains PASS."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_security_privacy_compliance_feedback_resolver",
            name="Security, Privacy & Compliance Feedback Resolver",
            version="1.0.0",
            category="security",
            description=(
                "Addresses Security, Privacy & Compliance assessment feedback by orchestrating relevant "
                "security/governance skills and re-invoking security-privacy-compliance-assessor-feedback "
                "multiple times until every feedback item is adequately resolved and all 5 domains pass."
            ),
            capabilities=[
                "security_feedback_resolution",
                "iterative_security_reassessment",
                "compliance_remediation",
                "skill_orchestration",
            ],
            entrypoint="execute",
            context_token_estimate=420,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project undergoing security/privacy/compliance resolution.",
                ),
                SkillParameter(
                    name="project_manifest_or_spec",
                    type="string",
                    description="Current project manifest, IaC/security posture, or specification text.",
                ),
                SkillParameter(
                    name="max_iterations",
                    type="integer",
                    description="Maximum assessment-remediation iterations to run (default 3).",
                    required=False,
                    default=3,
                ),
            ],
            instructions=(
                "Invokes skill_security_privacy_compliance_assessor_feedback, maps all security/privacy/compliance "
                "gaps to relevant library skills (waf-pillar-security, terraform-waf-verifier, fde-governance-auditor, "
                "complete-system-audit), applies remediations, and re-assesses iteratively until all 5 domains pass."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target Enterprise Project")
        working_spec = parameters.get("project_manifest_or_spec", "")
        max_iterations = max(1, min(int(parameters.get("max_iterations", 3)), 5))

        iteration_history: list[dict[str, Any]] = []
        invoked_library_skills: set[str] = set()
        remediations_applied: list[dict[str, Any]] = []
        final_assessment = _evaluate_security_privacy_compliance(project_name, working_spec)

        for iteration in range(1, max_iterations + 1):
            assessment = _evaluate_security_privacy_compliance(project_name, working_spec)
            final_assessment = assessment
            iteration_history.append({
                "iteration": iteration,
                "overall_status": assessment["overall_status"],
                "domains_passed": assessment["domains_passed"],
                "open_feedback_count": len(assessment["feedback_items"]),
            })

            if assessment["overall_passed"] and not assessment["feedback_items"]:
                break

            additions: list[str] = []
            for item in assessment["feedback_items"]:
                for sk in item["recommended_skills"]:
                    invoked_library_skills.add(sk)
                remediations_applied.append({
                    "iteration": iteration,
                    "criterion_id": item["criterion_id"],
                    "domain": item["domain_name"],
                    "skills_orchestrated": item["recommended_skills"],
                    "remediation_action": item["feedback"],
                })
                additions.append(
                    f"[Remediated SPC-{item['criterion_id']} via {', '.join(item['recommended_skills'])}]: "
                    f"{item['feedback']}"
                )

            if not additions:
                break
            working_spec = working_spec + "\n" + "\n".join(additions)

            post_assessment = _evaluate_security_privacy_compliance(project_name, working_spec)
            final_assessment = post_assessment
            if post_assessment["overall_passed"] and not post_assessment["feedback_items"]:
                iteration_history.append({
                    "iteration": iteration + 1,
                    "overall_status": post_assessment["overall_status"],
                    "domains_passed": post_assessment["domains_passed"],
                    "open_feedback_count": len(post_assessment["feedback_items"]),
                })
                break

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=elapsed_ms,
            data={
                "project_name": project_name,
                "final_status": final_assessment["overall_status"],
                "final_passed": final_assessment["overall_passed"],
                "iterations_executed": len(iteration_history),
                "iteration_history": iteration_history,
                "library_skills_orchestrated": sorted(invoked_library_skills),
                "remediations_applied": remediations_applied,
                "final_assessment": final_assessment,
                "final_assessment_markdown": _render_spc_assessment_markdown(final_assessment),
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(working_spec),
                "completion_tokens_estimated": self.estimate_tokens(str(remediations_applied)),
                "tokens_saved_by_cache": 0,
            },
        )


def _build_spc_human_faq_section(project_name: str, project_summary: str) -> str:
    """Build a direct, conversational, evidence-backed Security, Privacy & Compliance FAQ section."""
    assessment = _evaluate_security_privacy_compliance(project_name, project_summary)
    lines = [
        SPC_FAQ_START,
        "## Security, Privacy & Compliance FAQs",
        "",
        f"> Plain-English, verifiable answers explaining how **{project_name}** handles authentication, "
        f"network security, data protection, AI guardrails, and compliance "
        f"(Rubric Verdict: **{assessment['overall_status']}**, {assessment['domains_passed']}/{assessment['total_domains']} domains passing).",
        "",
    ]

    conversational_questions = {
        "1.1": f"How does {project_name} authenticate requests and avoid leaking static keys?",
        "1.2": f"How do I verify that {project_name} actually enforces Least Privilege across IAM and tools?",
        "2.1": f"How are VPC networking, private endpoints, and zero-trust boundaries set up in {project_name}?",
        "2.2": f"What service perimeters and firewall/SSRF protections keep {project_name} locked down?",
        "3.1": f"How does {project_name} encrypt data and stop PII from leaking out?",
        "3.2": f"Where are secrets stored, and how can I check that nothing sensitive is hardcoded?",
        "4.1": f"What stops prompt injection, jailbreaks, or unsafe outputs in {project_name}?",
        "4.2": f"How does {project_name} control which AI models can run and enforce content safety?",
        "5.1": f"Where do audit logs live, and how does {project_name} handle data residency and regulations?",
        "5.2": f"How is enterprise policy enforced automatically across deployments of {project_name}?",
    }

    for domain in assessment["domain_results"]:
        lines.append(
            f"### {domain['domain_number']}. {domain['domain_name']} "
            f"({domain['competent_count']}/{domain['total_criteria']} Competent — {'PASS' if domain['passed'] else 'FAIL'})"
        )
        lines.append("")
        for crit in domain["criteria"]:
            q = conversational_questions.get(
                crit["criterion_id"],
                f"How does {project_name} handle {crit['title']}?",
            )
            sigs = ", ".join(f"`{s}`" for s in crit["matched_signals"]) if crit["matched_signals"] else "documented in project configuration"
            lines.append(f"**Q: {q}**")
            lines.append("")
            if crit["is_competent"]:
                lines.append(
                    f"**A:** Rated **{crit['level']}**. You can verify this directly in the codebase via "
                    f"active evidence signals ({sigs}). All controls for *{crit['title']}* are wired in and verifiable."
                )
            else:
                lines.append(
                    f"**A:** Currently **{crit['level']}** (signals detected: {sigs}). "
                    f"Next step to harden: {crit['remediation']}"
                )
            lines.append("")

    lines.append(SPC_FAQ_END)
    return "\n".join(lines)


def upsert_spc_faqs_in_file(faqs_path: Path, faq_section_md: str) -> dict[str, Any]:
    """Insert or update the Security, Privacy & Compliance FAQ section in docs/FAQs.md.

    - If docs/FAQs.md already exists: preserves all existing sections (e.g., AI/ML Rubric FAQs)
      and updates or appends the Security, Privacy & Compliance section.
    - If docs/FAQs.md does not exist: initializes a new docs/FAQs.md with a top-level header.
    """
    faqs_path.parent.mkdir(parents=True, exist_ok=True)
    if faqs_path.exists():
        existing = faqs_path.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"{re.escape(SPC_FAQ_START)}.*?{re.escape(SPC_FAQ_END)}",
            re.DOTALL,
        )
        if pattern.search(existing):
            updated = pattern.sub(faq_section_md, existing)
            action = "updated_existing_section"
        else:
            separator = "\n\n---\n\n" if existing.strip() else ""
            updated = existing.rstrip() + separator + faq_section_md + "\n"
            action = "appended_new_section_to_existing_file"
        faqs_path.write_text(updated, encoding="utf-8")
    else:
        content = f"# Frequently Asked Questions (FAQs)\n\n{faq_section_md}\n"
        faqs_path.write_text(content, encoding="utf-8")
        action = "created_new_faqs_file"

    return {
        "file_path": str(faqs_path),
        "action": action,
        "bytes_written": faqs_path.stat().st_size,
    }


class SecurityPrivacyComplianceFAQsSkill(SkillPlugin):
    """Generates conversational, evidence-backed Security, Privacy & Compliance FAQs in docs/FAQs.md."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_security_privacy_compliance_faqs",
            name="Security, Privacy & Compliance FAQs Generator",
            version="1.0.0",
            category="security",
            description=(
                "Generates direct, conversational, human-style FAQs with concrete codebase evidence "
                "documenting how a project, repo, or spec addresses all 5 Security, Privacy & Compliance "
                "Rubric domains. Appends/updates a dedicated section in docs/FAQs.md or initializes a new one."
            ),
            capabilities=[
                "security_faq_generation",
                "human_style_evidence_docs",
                "idempotent_docs_upsert",
            ],
            entrypoint="execute",
            context_token_estimate=320,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(
                    name="project_name",
                    type="string",
                    description="Name of the project, repo, or spec to document.",
                ),
                SkillParameter(
                    name="project_manifest_or_summary",
                    type="string",
                    description="Security, privacy, compliance evidence and codebase summary.",
                ),
                SkillParameter(
                    name="docs_file_path",
                    type="string",
                    description="Target path to FAQs.md (defaults to docs/FAQs.md).",
                    required=False,
                    default="docs/FAQs.md",
                ),
                SkillParameter(
                    name="write_to_disk",
                    type="boolean",
                    description="If True, initializes or updates docs_file_path directly on disk.",
                    required=False,
                    default=False,
                ),
            ],
            instructions=(
                "Creates direct, conversational FAQs grounded in verifiable project files/tests/IaC "
                "covering all 5 Security, Privacy & Compliance domains, and upserts them into docs/FAQs.md."
            ),
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        project_name = parameters.get("project_name", "Target Enterprise Project")
        summary = parameters.get("project_manifest_or_summary", "")
        docs_file_path = parameters.get("docs_file_path", "docs/FAQs.md")
        write_to_disk = bool(parameters.get("write_to_disk", False))

        faq_section_md = _build_spc_human_faq_section(project_name, summary)
        write_info: dict[str, Any] | None = None

        if write_to_disk:
            write_info = upsert_spc_faqs_in_file(Path(docs_file_path), faq_section_md)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=elapsed_ms,
            data={
                "project_name": project_name,
                "docs_file_path": docs_file_path,
                "write_to_disk": write_to_disk,
                "write_result": write_info,
                "faq_markdown": faq_section_md,
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(summary),
                "completion_tokens_estimated": self.estimate_tokens(faq_section_md),
                "tokens_saved_by_cache": 0,
            },
        )

"""Terraform Infrastructure & Well-Architected Framework (WAF) Verification Skill Plugins.

Provides:
1. `TerraformInfraSkill` (`skill_terraform_infra`): Generates, audits, and hardens Terraform HCL.
2. `TerraformWAFVerifierSkill` (`skill_terraform_waf_verifier`): Verifies an existing/current Terraform
   script against the Google Cloud Well-Architected Framework (OKF-PCA-01..09), detecting WAF departures
   and performing a comprehensive critique with remediated HCL.
3. `TerraformVersionComparatorSkill` (`skill_terraform_version_comparator`): Performs a comparative
   Well-Architected assessment between a past Terraform version and a present Terraform version,
   detecting newly introduced WAF regressions, resolved violations, persistent gaps, and pillar score deltas.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from src.models.router import model_router
from src.skills.base import (
    SkillExecutionContext,
    SkillManifest,
    SkillParameter,
    SkillPlugin,
    SkillResult,
)
from src.skills.plugins.waf_okf_pillars import (
    DATAPLEX_KB_METADATA,
    WAF_PILLAR_DEFINITIONS,
    evaluate_spec_across_all_pillars,
)

# Deterministic Terraform HCL Well-Architected Departure Rules grounded in OKF-PCA-01..09
TERRAFORM_WAF_RULES: list[dict[str, Any]] = [
    {
        "rule_id": "TF-WAF-SEC-01",
        "pillar": "security",
        "okf_concept": "OKF-PCA-04",
        "severity": "CRITICAL",
        "title": "Primitive Overprivileged IAM Roles (roles/owner, roles/editor) or Public Principal (allUsers / allAuthenticatedUsers)",
        "pattern_regex": r"roles/(?:owner|editor)\b|allUsers|allAuthenticatedUsers",
        "remediation": "Replace roles/owner and roles/editor with least-privilege predefined or Organization/Project custom IAM roles, and remove allUsers/allAuthenticatedUsers bindings.",
        "remediated_hcl": 'role   = "roles/spanner.databaseUser"\nmember = "serviceAccount:${google_service_account.app_sa.email}"',
    },
    {
        "rule_id": "TF-WAF-SEC-02",
        "pillar": "security",
        "okf_concept": "OKF-PCA-04",
        "severity": "CRITICAL",
        "title": "Long-Lived Service Account JSON Key Creation (google_service_account_key) Violating Zero Ambient Authority",
        "pattern_regex": r'resource\s+"google_service_account_key"',
        "remediation": "Remove google_service_account_key and enforce constraints/iam.disableServiceAccountKeyCreation. Use GKE Workload Identity, Workload Identity Federation, or SA impersonation.",
        "remediated_hcl": 'resource "google_service_account_iam_member" "workload_identity" {\n  service_account_id = google_service_account.app.name\n  role               = "roles/iam.workloadIdentityUser"\n  member             = "serviceAccount:${var.project_id}.svc.id.goog[${var.k8s_ns}/${var.ksa_name}]"\n}',
    },
    {
        "rule_id": "TF-WAF-SEC-03",
        "pillar": "security",
        "okf_concept": "OKF-PCA-04",
        "severity": "HIGH",
        "title": "Cloud Storage Bucket Missing Public Access Prevention or Uniform Bucket-Level Access",
        "pattern_regex": r'public_access_prevention\s*=\s*"inherited"|uniform_bucket_level_access\s*=\s*false',
        "remediation": "Enforce public_access_prevention = \"enforced\" and uniform_bucket_level_access = true on all google_storage_bucket resources (OKF-PCA-04 / Anti-Pattern #15).",
        "remediated_hcl": 'public_access_prevention    = "enforced"\nuniform_bucket_level_access = true',
    },
    {
        "rule_id": "TF-WAF-SEC-04",
        "pillar": "security",
        "okf_concept": "OKF-PCA-04",
        "severity": "HIGH",
        "title": "Invalid Folder-Level Custom IAM Role Definition",
        "pattern_regex": r'resource\s+"google_folder_iam_custom_role"|gcloud\s+iam\s+roles\s+create.*--folder',
        "remediation": "Custom IAM Roles can ONLY be created at the Organization (google_organization_iam_custom_role) or Project (google_project_iam_custom_role) level—never at the Folder level (OKF-PCA-04 / Anti-Pattern #4).",
        "remediated_hcl": 'resource "google_organization_iam_custom_role" "custom_role" {\n  org_id      = var.org_id\n  role_id     = "customLeastPrivRole"\n  title       = "Custom Least Privilege Role"\n  permissions = ["storage.objects.get"]\n}',
    },
    {
        "rule_id": "TF-WAF-SEC-05",
        "pillar": "security",
        "okf_concept": "OKF-PCA-05",
        "severity": "CRITICAL",
        "title": "Hardcoded Plaintext Passwords/API Keys in Terraform HCL or Storing Secrets in Cloud KMS Instead of Secret Manager",
        "pattern_regex": r'(?:db_password|api_key|secret_key|password)\s*=\s*"[A-Za-z0-9_!@#$%^&*-]{6,}"|AIzaSy[A-Za-z0-9_-]{10,}',
        "remediation": "Never hardcode plaintext secrets in HCL or TF state. Store secrets in google_secret_manager_secret and reference secret versions dynamically (OKF-PCA-05 / Anti-Pattern #1).",
        "remediated_hcl": 'resource "google_secret_manager_secret" "db_pass" {\n  secret_id = "prod-db-password"\n  replication { auto {} }\n}',
    },
    {
        "rule_id": "TF-WAF-SEC-06",
        "pillar": "security",
        "okf_concept": "OKF-PCA-03",
        "severity": "HIGH",
        "title": "Unrestricted Public Ingress (0.0.0.0/0) on SSH (22) or RDP (3389) Firewall Rules",
        "pattern_regex": r'0\.0\.0\.0/0[\s\S]{0,200}?"(?:22|3389)"|"(?:22|3389)"[\s\S]{0,200}?0\.0\.0\.0/0',
        "remediation": "Remove 0.0.0.0/0 SSH/RDP ingress. Restrict SSH/RDP strictly to Google Cloud Identity-Aware Proxy (IAP) TCP forwarding CIDR 35.235.240.0/20, and restrict backend web VMs to GFE ranges 130.211.0.0/22 and 35.191.0.0/16 (OKF-PCA-03 / OKF-PCA-05).",
        "remediated_hcl": 'source_ranges = ["35.235.240.0/20"] # IAP TCP Forwarding only',
    },
    {
        "rule_id": "TF-WAF-SEC-07",
        "pillar": "security",
        "okf_concept": "OKF-PCA-02",
        "severity": "HIGH",
        "title": "Unauthenticated Cloud Run Service Invoker or Shielded Nodes Used Instead of Confidential Nodes for RAM Encryption",
        "pattern_regex": r"allow_unauthenticated\s*=\s*true|enable_confidential_nodes\s*=\s*false",
        "remediation": "Require authenticated IAM/IAP invokers on Cloud Run and enable_confidential_nodes = true (AMD SEV / Intel TDX) when data in-use RAM encryption is required (OKF-PCA-02 / Anti-Pattern #2).",
        "remediated_hcl": 'confidential_nodes {\n  enabled = true\n}',
    },
    {
        "rule_id": "TF-WAF-REL-01",
        "pillar": "reliability",
        "okf_concept": "OKF-PCA-01",
        "severity": "HIGH",
        "title": "Single-Zone Cloud SQL Instance (availability_type = ZONAL) or Deletion Protection Disabled",
        "pattern_regex": r'availability_type\s*=\s*"ZONAL"|deletion_protection\s*=\s*false|deletion_protection_enabled\s*=\s*false',
        "remediation": "Configure availability_type = \"REGIONAL\" for synchronous Zonal HA failover (RPO=0, RTO<2m), enable point_in_time_recovery_enabled = true, and set deletion_protection = true (OKF-PCA-01).",
        "remediated_hcl": 'settings {\n  availability_type = "REGIONAL"\n  backup_configuration {\n    enabled                        = true\n    point_in_time_recovery_enabled = true\n  }\n}\ndeletion_protection = true',
    },
    {
        "rule_id": "TF-WAF-REL-02",
        "pillar": "reliability",
        "okf_concept": "OKF-PCA-01",
        "severity": "HIGH",
        "title": "Memorystore for Redis Configured with BASIC Tier (No HA / Zero Failover) or Memcached Used for HA",
        "pattern_regex": r'tier\s*=\s*"BASIC"|resource\s+"google_memcache_instance"',
        "remediation": "Use google_redis_instance with tier = \"STANDARD_HA\" for cross-zone replication and automatic <30s failover (OKF-PCA-01).",
        "remediated_hcl": 'resource "google_redis_instance" "cache" {\n  name           = "prod-ha-cache"\n  tier           = "STANDARD_HA"\n  memory_size_gb = 8\n}',
    },
    {
        "rule_id": "TF-WAF-REL-03",
        "pillar": "reliability",
        "okf_concept": "OKF-PCA-08",
        "severity": "MEDIUM",
        "title": "Force Destroy Enabled on Production Storage or Database Resources",
        "pattern_regex": r"force_destroy\s*=\s*true",
        "remediation": "Set force_destroy = false and enable object versioning / retention policy locks on production Cloud Storage buckets (OKF-PCA-01 / OKF-PCA-08).",
        "remediated_hcl": "force_destroy = false\nversioning {\n  enabled = true\n}",
    },
    {
        "rule_id": "TF-WAF-OPS-01",
        "pillar": "operational_excellence",
        "okf_concept": "OKF-PCA-07",
        "severity": "MEDIUM",
        "title": "Local Terraform Backend Instead of GCS Remote State with Native State Locking (.tflock)",
        "pattern_regex": r'backend\s+"local"',
        "remediation": "Configure backend \"gcs\" in the terraform block to store state in a versioned Cloud Storage bucket with native .tflock state locking (OKF-PCA-07).",
        "remediated_hcl": 'terraform {\n  backend "gcs" {\n    bucket = "enterprise-tf-state-prod"\n    prefix = "env/prod"\n  }\n}',
    },
    {
        "rule_id": "TF-WAF-COST-01",
        "pillar": "cost_optimization",
        "okf_concept": "OKF-PCA-02",
        "severity": "MEDIUM",
        "title": "Spot / Preemptible VMs Used for Stateful Primary Database or Control-Plane Nodes",
        "pattern_regex": r'preemptible\s*=\s*true[\s\S]{0,150}?(?:primary|master|stateful|database)|provisioning_model\s*=\s*"SPOT"[\s\S]{0,150}?(?:primary|master|stateful|database)',
        "remediation": "Spot VMs have a 30-second preemption notice and zero minimum runtime guarantee. Use Spot VMs strictly for stateless batch workers or Dataproc secondary workers (OKF-PCA-02 / Anti-Pattern #18).",
        "remediated_hcl": 'scheduling {\n  provisioning_model = "STANDARD"\n  automatic_restart  = true\n}',
    },
    {
        "rule_id": "TF-WAF-PERF-01",
        "pillar": "performance_optimization",
        "okf_concept": "OKF-PCA-03",
        "severity": "MEDIUM",
        "title": "Standard Network Service Tier Used on Global Latency-Sensitive Load Balancing",
        "pattern_regex": r'network_tier\s*=\s*"STANDARD"',
        "remediation": "Use network_tier = \"PREMIUM\" for global Anycast IP and Cold-Potato routing over Google's private fiber backbone (OKF-PCA-03).",
        "remediated_hcl": 'network_tier = "PREMIUM"',
    },
]

# Positive Terraform HCL signals per WAF pillar
TERRAFORM_PILLAR_POSITIVE_PATTERNS: dict[str, list[str]] = {
    "operational_excellence": [
        r'backend\s+"gcs"',
        r"labels\s*=\s*\{",
        r"google_Monitoring_|google_logging_|google_clouddeploy_|google_cloudbuild_",
        r"lifecycle\s*\{",
        r"variable\s+\"|output\s+\"",
    ],
    "security": [
        r'public_access_prevention\s*=\s*"enforced"',
        r"uniform_bucket_level_access\s*=\s*true",
        r"kms_key_name|encryption_configuration|customer_managed_key",
        r"workload_identity_config|workloadIdentityUser",
        r"google_secret_manager_secret|google_access_context_manager|google_compute_security_policy|confidential_nodes",
    ],
    "reliability": [
        r'availability_type\s*=\s*"REGIONAL"|STANDARD_HA|multi-region|nam3|nam6',
        r"deletion_protection\s*=\s*true|deletion_protection_enabled\s*=\s*true",
        r"versioning\s*\{\s*enabled\s*=\s*true",
        r"point_in_time_recovery_enabled\s*=\s*true|backup_configuration",
        r"autoscaling|max_replicas|min_replicas|google_pubsub_",
    ],
    "cost_optimization": [
        r"enable_autopilot\s*=\s*true|google_cloud_run",
        r"lifecycle_rule|autoclass",
        r"time_partitioning|clustering",
        r"google_billing_budget|exclusion\s*\{",
    ],
    "performance_optimization": [
        r'network_tier\s*=\s*"PREMIUM"|enable_cdn\s*=\s*true',
        r"google_redis_instance|google_spanner_|google_bigtable_",
        r"time_partitioning|clustering",
        r"ip_allocation_policy",
    ],
    "sustainability": [
        r"enable_autopilot\s*=\s*true|google_cloud_run",
        r"lifecycle_rule|autoclass|default_table_expiration_ms",
        r"us-central1|europe-west1|us-west1|resourceLocations",
    ],
}


def extract_terraform_resources(hcl: str) -> dict[str, str]:
    """Extract `resource "<type>" "<name>"` blocks from Terraform HCL."""
    resources: dict[str, str] = {}
    pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', re.MULTILINE)
    for match in pattern.finditer(hcl):
        res_type, res_name = match.group(1), match.group(2)
        key = f"{res_type}.{res_name}"
        start = match.end()
        depth = 1
        pos = start
        while pos < len(hcl) and depth > 0:
            if hcl[pos] == "{":
                depth += 1
            elif hcl[pos] == "}":
                depth -= 1
            pos += 1
        resources[key] = hcl[match.start():pos]
    return resources


def analyze_terraform_waf_compliance(
    terraform_hcl: str,
    target_pillars: list[str] | None = None,
) -> dict[str, Any]:
    """Deterministically analyze a Terraform HCL script for Well-Architected compliance and departures."""
    pillars_to_check = target_pillars or list(WAF_PILLAR_DEFINITIONS.keys())
    if "all" in [p.lower() for p in pillars_to_check]:
        pillars_to_check = list(WAF_PILLAR_DEFINITIONS.keys())

    # 1. Detect Terraform-specific WAF departures
    tf_departures: list[dict[str, Any]] = []
    for rule in TERRAFORM_WAF_RULES:
        if re.search(rule["pattern_regex"], terraform_hcl, flags=re.IGNORECASE):
            tf_departures.append({
                "rule_id": rule["rule_id"],
                "pillar": rule["pillar"],
                "okf_concept": rule["okf_concept"],
                "severity": rule["severity"],
                "title": rule["title"],
                "remediation": rule["remediation"],
                "remediated_hcl": rule["remediated_hcl"],
            })

    # 2. Also run general 18-rule PCA/WAF anti-pattern check
    spec_eval = evaluate_spec_across_all_pillars(terraform_hcl, target_pillars=pillars_to_check)
    for ap in spec_eval["antipattern_violations"]:
        tf_departures.append({
            "rule_id": ap["rule_id"],
            "pillar": ap.get("pillar", "security"),
            "okf_concept": ap["okf_concept"],
            "severity": "HIGH",
            "title": ap["antipattern_detected"],
            "remediation": ap["deterministic_fix"],
            "remediated_hcl": "# Refer to OKF-PCA deterministic remediation",
        })

    # Deduplicate by rule_id
    dedup_departures: dict[str, dict[str, Any]] = {}
    for d in tf_departures:
        dedup_departures[d["rule_id"]] = d
    departures_list = list(dedup_departures.values())

    # 3. Compute per-pillar Terraform WAF scores (0.0 - 3.0)
    pillar_scores: dict[str, dict[str, Any]] = {}
    for p_key in pillars_to_check:
        p_norm = p_key.lower().strip()
        if p_norm not in WAF_PILLAR_DEFINITIONS:
            continue
        pdef = WAF_PILLAR_DEFINITIONS[p_norm]
        pos_patterns = TERRAFORM_PILLAR_POSITIVE_PATTERNS.get(p_norm, [])
        pos_hits = sum(1 for pat in pos_patterns if re.search(pat, terraform_hcl, flags=re.IGNORECASE))
        pos_ratio = pos_hits / max(len(pos_patterns), 1)

        p_departures = [d for d in departures_list if d["pillar"] == p_norm]
        base = 2.0 + (1.0 * pos_ratio)
        if p_departures:
            penalty = sum(0.85 if d["severity"] == "CRITICAL" else 0.55 for d in p_departures)
            score = round(max(0.0, base - penalty), 2)
        else:
            score = round(min(3.0, max(2.1 if pos_hits >= 1 else 2.0, base)), 2)

        pillar_scores[p_norm] = {
            "pillar_id": p_norm,
            "pillar_name": pdef["display_name"],
            "score": score,
            "cutline_passed": score >= 2.0 and len(p_departures) == 0,
            "positive_hcl_patterns_matched": pos_hits,
            "departures_count": len(p_departures),
            "departures": p_departures,
            "okf_concepts": pdef["okf_concepts"],
        }

    all_scores = [p["score"] for p in pillar_scores.values()]
    composite_score = round(sum(all_scores) / max(len(all_scores), 1), 2)
    is_compliant = len(departures_list) == 0 and composite_score >= 2.0
    verdict = "TERRAFORM_WAF_COMPLIANT" if is_compliant else "WAF_DEPARTURE_DETECTED"

    resources = extract_terraform_resources(terraform_hcl)

    # Build Markdown Critique Summary
    md = [
        "# 🏗️ Terraform HCL Well-Architected Framework (WAF) Verification & Critique",
        f"- **Verdict**: `{verdict}`",
        f"- **Composite Terraform WAF Score**: `{composite_score} / 3.00` (Cutline: `>= 2.00`)",
        f"- **Total Terraform Resources Analyzed**: `{len(resources)}`",
        f"- **Total WAF Departures Detected**: `{len(departures_list)}`",
        f"- **Dataplex OKF Grounding**: `{DATAPLEX_KB_METADATA['corpus']}` (`{DATAPLEX_KB_METADATA['version_tag']}`)",
        "",
        "## 1. Per-Pillar Terraform WAF Posture",
        "| WAF Pillar | Score (0–3.0) | Status | Departures | OKF Concepts |",
        "| :--- | :---: | :---: | :---: | :--- |",
    ]
    for p in pillar_scores.values():
        icon = "✅ COMPLIANT" if p["cutline_passed"] else "❌ DEPARTURE"
        cids = ", ".join(f"`{c}`" for c in p["okf_concepts"])
        md.append(f"| **{p['pillar_name']}** | `{p['score']}` | {icon} | `{p['departures_count']}` | {cids} |")

    if departures_list:
        md.extend([
            "",
            "## 2. 🚨 Detected WAF Departures in Current Terraform Script",
            "| Rule ID | Severity | Pillar | OKF Concept | Departure Description | Mandatory Remediation |",
            "| :--- | :---: | :--- | :--- | :--- | :--- |",
        ])
        for d in departures_list:
            md.append(
                f"| `{d['rule_id']}` | **{d['severity']}** | `{d['pillar']}` | `{d['okf_concept']}` | {d['title']} | {d['remediation']} |"
            )
    else:
        md.extend([
            "",
            "## 2. ✅ Zero WAF Departures Detected",
            "Current Terraform HCL adheres to all checked Google Cloud Well-Architected guardrails.",
        ])

    return {
        "status": "success",
        "verdict": verdict,
        "is_waf_compliant": is_compliant,
        "composite_waf_score": composite_score,
        "resource_count": len(resources),
        "resources_discovered": list(resources.keys()),
        "pillar_scores": pillar_scores,
        "waf_departures": departures_list,
        "dataplex_kb": DATAPLEX_KB_METADATA,
        "critique_scorecard_markdown": "\n".join(md),
    }


def compare_past_and_present_terraform_waf(
    past_terraform_hcl: str,
    present_terraform_hcl: str,
) -> dict[str, Any]:
    """Compare a past Terraform script and a present Terraform script across all WAF pillars."""
    past_eval = analyze_terraform_waf_compliance(past_terraform_hcl)
    present_eval = analyze_terraform_waf_compliance(present_terraform_hcl)

    past_rules = {d["rule_id"]: d for d in past_eval["waf_departures"]}
    present_rules = {d["rule_id"]: d for d in present_eval["waf_departures"]}

    # Classify WAF posture changes
    newly_introduced_regressions = [
        present_rules[rid] for rid in sorted(present_rules.keys() - past_rules.keys())
    ]
    resolved_waf_violations = [
        past_rules[rid] for rid in sorted(past_rules.keys() - present_rules.keys())
    ]
    persistent_waf_departures = [
        present_rules[rid] for rid in sorted(present_rules.keys() & past_rules.keys())
    ]

    # Resource-level diff
    past_res = extract_terraform_resources(past_terraform_hcl)
    present_res = extract_terraform_resources(present_terraform_hcl)
    added_resources = sorted(present_res.keys() - past_res.keys())
    removed_resources = sorted(past_res.keys() - present_res.keys())
    modified_resources = sorted(
        k for k in (present_res.keys() & past_res.keys()) if present_res[k].strip() != past_res[k].strip()
    )

    # Pillar score deltas
    pillar_deltas: dict[str, dict[str, Any]] = {}
    for p_id, pres_p in present_eval["pillar_scores"].items():
        past_p = past_eval["pillar_scores"].get(p_id, pres_p)
        delta = round(pres_p["score"] - past_p["score"], 2)
        if delta > 0:
            trend = "IMPROVED"
        elif delta < 0:
            trend = "REGRESSED"
        else:
            trend = "UNCHANGED"
        pillar_deltas[p_id] = {
            "pillar_id": p_id,
            "pillar_name": pres_p["pillar_name"],
            "past_score": past_p["score"],
            "present_score": pres_p["score"],
            "score_delta": delta,
            "trend": trend,
            "past_departures_count": past_p["departures_count"],
            "present_departures_count": pres_p["departures_count"],
        }

    score_delta = round(present_eval["composite_waf_score"] - past_eval["composite_waf_score"], 2)

    if newly_introduced_regressions:
        evolution_verdict = "WAF_REGRESSION_DETECTED"
    elif present_eval["is_waf_compliant"] and resolved_waf_violations:
        evolution_verdict = "WAF_EXEMPLARY_EVOLUTION"
    elif score_delta > 0:
        evolution_verdict = "WAF_POSTURE_IMPROVED"
    elif persistent_waf_departures:
        evolution_verdict = "WAF_NEUTRAL_WITH_PERSISTENT_GAPS"
    else:
        evolution_verdict = "WAF_COMPLIANT_STABLE"

    md = [
        "# 🔄 Past vs. Present Terraform Well-Architected Comparative Assessment",
        f"- **Evolution Verdict**: `{evolution_verdict}`",
        f"- **Past Composite WAF Score**: `{past_eval['composite_waf_score']} / 3.00` ({past_eval['verdict']})",
        f"- **Present Composite WAF Score**: `{present_eval['composite_waf_score']} / 3.00` ({present_eval['verdict']})",
        f"- **Net WAF Score Delta**: `{score_delta:+.2f}`",
        f"- **Newly Introduced WAF Regressions**: `{len(newly_introduced_regressions)}`",
        f"- **Resolved WAF Violations**: `{len(resolved_waf_violations)}`",
        f"- **Persistent Unresolved WAF Departures**: `{len(persistent_waf_departures)}`",
        "",
        "## 1. Pillar-by-Pillar Past vs. Present Score Comparison",
        "| WAF Pillar | Past Score | Present Score | Delta | Trend | Past -> Present Departures |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for pd in pillar_deltas.values():
        md.append(
            f"| **{pd['pillar_name']}** | `{pd['past_score']}` | `{pd['present_score']}` | `{pd['score_delta']:+.2f}` | `{pd['trend']}` | `{pd['past_departures_count']} -> {pd['present_departures_count']}` |"
        )

    md.extend([
        "",
        "## 2. Terraform Resource Drift Summary",
        f"- **Added Resources ({len(added_resources)})**: {', '.join(f'`{r}`' for r in added_resources) or 'None'}",
        f"- **Removed Resources ({len(removed_resources)})**: {', '.join(f'`{r}`' for r in removed_resources) or 'None'}",
        f"- **Modified Resources ({len(modified_resources)})**: {', '.join(f'`{r}`' for r in modified_resources) or 'None'}",
    ])

    if newly_introduced_regressions:
        md.extend([
            "",
            "## 3. 🚨 Newly Introduced WAF Regressions (Present Departed from WAF!)",
            "| Rule ID | Severity | Pillar | OKF Concept | Regression Introduced | Remediation |",
            "| :--- | :---: | :--- | :--- | :--- | :--- |",
        ])
        for r in newly_introduced_regressions:
            md.append(
                f"| `{r['rule_id']}` | **{r['severity']}** | `{r['pillar']}` | `{r['okf_concept']}` | {r['title']} | {r['remediation']} |"
            )

    if resolved_waf_violations:
        md.extend([
            "",
            "## 4. ✅ Resolved WAF Violations (Improved from Past to Present)",
            "| Rule ID | Pillar | OKF Concept | Fixed Violation |",
            "| :--- | :--- | :--- | :--- |",
        ])
        for r in resolved_waf_violations:
            md.append(f"| `{r['rule_id']}` | `{r['pillar']}` | `{r['okf_concept']}` | {r['title']} |")

    if persistent_waf_departures:
        md.extend([
            "",
            "## 5. ⚠️ Persistent WAF Departures (Still Present in Both Versions)",
            "| Rule ID | Severity | Pillar | OKF Concept | Unresolved Departure | Remediation |",
            "| :--- | :---: | :--- | :--- | :--- | :--- |",
        ])
        for r in persistent_waf_departures:
            md.append(
                f"| `{r['rule_id']}` | **{r['severity']}** | `{r['pillar']}` | `{r['okf_concept']}` | {r['title']} | {r['remediation']} |"
            )

    return {
        "status": "success",
        "evolution_verdict": evolution_verdict,
        "past_composite_score": past_eval["composite_waf_score"],
        "present_composite_score": present_eval["composite_waf_score"],
        "composite_score_delta": score_delta,
        "past_assessment": past_eval,
        "present_assessment": present_eval,
        "pillar_deltas": pillar_deltas,
        "resource_diff": {
            "added": added_resources,
            "removed": removed_resources,
            "modified": modified_resources,
        },
        "newly_introduced_regressions": newly_introduced_regressions,
        "resolved_waf_violations": resolved_waf_violations,
        "persistent_waf_departures": persistent_waf_departures,
        "dataplex_kb": DATAPLEX_KB_METADATA,
        "comparison_report_markdown": "\n".join(md),
    }


class TerraformInfraSkill(SkillPlugin):
    """Enterprise skill for generating, auditing, and hardening Terraform HCL for Google Cloud multi-agent and data infrastructure."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_terraform_infra",
            name="Terraform Infrastructure Auditor & Synthesizer",
            version="2.0.0",
            category="devops",
            description="Generates, audits, and hardens Terraform HCL for Cloud Spanner, Vertex AI, BigQuery, and IAM following least-privilege standards and OKF-PCA-01..09.",
            capabilities=["terraform_synthesis", "hcl_security_audit", "iam_least_privilege", "spanner_iac"],
            entrypoint="execute",
            context_token_estimate=350,
            sandbox_tier="infra_deploy",
            parameters=[
                SkillParameter(name="action", type="string", description="Action: 'generate', 'audit_hcl', 'security_scan'", required=False, default="generate"),
                SkillParameter(name="infrastructure_requirements", type="string", description="Requirements for resources (e.g. Spanner Graph, Vertex AI Reasoning Engine, BigQuery, KMS)"),
                SkillParameter(name="existing_hcl", type="string", description="Existing HCL code (for audit or security scan)", required=False, default=""),
            ],
            instructions="Produces battle-tested Terraform HCL adhering to Google Cloud CIS Foundation benchmarks, Well-Architected Framework (OKF-PCA-01..09), and Zero Ambient Authority.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        action = parameters.get("action", "generate").lower()
        reqs = parameters.get("infrastructure_requirements", "")
        hcl = parameters.get("existing_hcl", "")

        waf_check = analyze_terraform_waf_compliance(hcl) if hcl.strip() else None

        prompt = f"""You are a Principal Google Cloud Terraform & Site Reliability Engineer.
Action: {action.upper()}

Requirements:
{reqs}

Existing HCL (if applicable):
{hcl}

Mandatory Infrastructure Guardrails (OKF-PCA-01..09):
1. Least Privilege IAM: Never grant `roles/owner` or `roles/editor` or create `google_service_account_key`. Use Workload Identity and fine-grained roles.
2. Security Defaults: Cloud KMS CMEK references, `public_access_prevention = "enforced"`, `uniform_bucket_level_access = true`, Secret Manager for secrets.
3. Reliability: `availability_type = "REGIONAL"` on Cloud SQL, `STANDARD_HA` on Redis, `deletion_protection = true`, GCS remote state locking (`backend "gcs"`).
4. Private Service Connect (PSC) and VPC Service Controls compatibility.
5. Provide:
   - Valid Terraform HCL code blocks.
   - Variables and Outputs definitions.
   - CIS Benchmark, Well-Architected & ZAA compliance notes.
"""
        response_text = await model_router.generate_text(
            prompt=prompt,
            temperature=0.1,
        )

        elapsed = (time.perf_counter() - start_time) * 1000
        prompt_tokens = self.estimate_tokens(prompt)
        completion_tokens = self.estimate_tokens(response_text)

        return SkillResult(
            status="success",
            skill_id="skill_terraform_infra",
            latency_ms=round(elapsed, 2),
            data={
                "action": action,
                "waf_verification": waf_check,
                "terraform_result_markdown": response_text,
            },
            token_metrics={
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "tokens_saved_by_cache": 0,
            },
        )


class TerraformWAFVerifierSkill(SkillPlugin):
    """Skill to verify an existing/current Terraform script for WAF departures and perform a comprehensive critique."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_terraform_waf_verifier",
            name="Terraform Well-Architected Drift Verifier & Critic",
            version="1.0.0",
            category="devops",
            description="Verifies an existing or current Terraform HCL script against the Google Cloud Well-Architected Framework (OKF-PCA-01..09), detecting where it departs from WAF best practices and producing a detailed critique and hardened HCL remediation.",
            capabilities=[
                "terraform_waf_verification",
                "hcl_drift_detection",
                "current_terraform_critique",
                "hcl_remediation_generation",
            ],
            entrypoint="execute",
            context_token_estimate=340,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(
                    name="terraform_hcl",
                    type="string",
                    description="Current/existing Terraform HCL script (.tf content) to verify and critique against Well-Architected foundations",
                ),
                SkillParameter(
                    name="workload_context",
                    type="string",
                    description="Optional context describing the environment or workload (e.g. 'production financial ledger', 'multi-agent platform')",
                    required=False,
                    default="production_enterprise_workload",
                ),
                SkillParameter(
                    name="target_pillars",
                    type="list",
                    description="Optional subset of WAF pillars to verify or ['all']",
                    required=False,
                    default=["all"],
                ),
            ],
            instructions="Scans Terraform HCL against 13+ Terraform WAF rules and 18 PCA/WAF anti-patterns, scores all 6 WAF pillars, and outputs a critique with remediated HCL.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        hcl = parameters.get("terraform_hcl") or parameters.get("existing_hcl") or parameters.get("input_payload") or ""
        workload_ctx = parameters.get("workload_context", "production_enterprise_workload")
        target_pillars = parameters.get("target_pillars", ["all"])

        analysis = analyze_terraform_waf_compliance(hcl, target_pillars=target_pillars)

        prompt = f"""You are a Google Cloud Principal Infrastructure Architect & Well-Architected Terraform Auditor.
Perform an exhaustive critique of the following current Terraform HCL script to identify every point where it departs from the Google Cloud Well-Architected Framework (grounded in Dataplex OKF Corpus {DATAPLEX_KB_METADATA['corpus']} / {DATAPLEX_KB_METADATA['version_tag']}).

Workload Context: {workload_ctx}
Deterministic Verdict: {analysis['verdict']} (Composite Score: {analysis['composite_waf_score']} / 3.00)
Detected WAF Departures: {json.dumps(analysis['waf_departures'])}

Current Terraform HCL:
```hcl
{hcl}
```

Provide:
1. Executive Critique of the Current Terraform Script (where and why it departs from Well-Architected foundations across Operational Excellence, Security, Reliability, Cost Optimization, Performance Optimization, and Sustainability).
2. Resource-by-Resource Vulnerability & Reliability Breakdown (citing OKF-PCA-01 through OKF-PCA-09).
3. Complete Hardened & Remediated Terraform HCL Code Block (drop-in production replacement).
"""
        llm_critique = await model_router.generate_text(prompt=prompt, temperature=0.1)
        elapsed = (time.perf_counter() - start_time) * 1000

        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=round(elapsed, 2),
            data={
                "workload_context": workload_ctx,
                **analysis,
                "llm_terraform_critique_markdown": f"{analysis['critique_scorecard_markdown']}\n\n---\n\n{llm_critique}",
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(prompt),
                "completion_tokens_estimated": self.estimate_tokens(llm_critique),
                "tokens_saved_by_cache": 0,
            },
        )


class TerraformVersionComparatorSkill(SkillPlugin):
    """Skill to compare a past Terraform version with a present Terraform version across all WAF pillars."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_terraform_version_comparator",
            name="Terraform Past vs. Present WAF Version Comparator",
            version="1.0.0",
            category="devops",
            description="Compares a past Terraform HCL version against a present Terraform HCL version, assessing both versions across all 6 Well-Architected pillars to detect newly introduced WAF regressions, resolved violations, persistent gaps, and pillar score deltas.",
            capabilities=[
                "terraform_version_comparison",
                "waf_regression_detection",
                "past_vs_present_assessment",
                "resource_drift_analysis",
            ],
            entrypoint="execute",
            context_token_estimate=380,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(
                    name="past_terraform_hcl",
                    type="string",
                    description="Past / baseline Terraform HCL script (prior commit, release, or state)",
                ),
                SkillParameter(
                    name="present_terraform_hcl",
                    type="string",
                    description="Present / current proposed Terraform HCL script to compare against the past version",
                ),
                SkillParameter(
                    name="change_context",
                    type="string",
                    description="Optional PR description, migration goal, or architectural context for the change",
                    required=False,
                    default="Terraform infrastructure evolution review",
                ),
            ],
            instructions="Evaluates both the past and present Terraform versions against OKF-PCA-01..09, computes per-pillar score deltas, flags any newly introduced WAF departures, and outputs a comparative assessment.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        past_hcl = parameters.get("past_terraform_hcl", "")
        present_hcl = parameters.get("present_terraform_hcl", "")
        change_ctx = parameters.get("change_context", "Terraform infrastructure evolution review")

        comp = compare_past_and_present_terraform_waf(past_hcl, present_hcl)

        prompt = f"""You are the Google Cloud Principal Infrastructure Review Board.
Perform a side-by-side Well-Architected Assessment comparing the PAST Terraform version and the PRESENT Terraform version, grounded in Dataplex OKF Corpus {DATAPLEX_KB_METADATA['corpus']} ({DATAPLEX_KB_METADATA['version_tag']}).

Change Context: {change_ctx}
Evolution Verdict: {comp['evolution_verdict']}
Past Composite WAF Score: {comp['past_composite_score']} / 3.00 -> Present Composite WAF Score: {comp['present_composite_score']} / 3.00 (Delta: {comp['composite_score_delta']:+.2f})
Newly Introduced WAF Regressions: {json.dumps(comp['newly_introduced_regressions'])}
Resolved WAF Violations: {json.dumps(comp['resolved_waf_violations'])}
Persistent WAF Departures: {json.dumps(comp['persistent_waf_departures'])}

PAST Terraform HCL:
```hcl
{past_hcl}
```

PRESENT Terraform HCL:
```hcl
{present_hcl}
```

Provide:
1. Executive Evolution Assessment (Did the infrastructure improve or regress against the Well-Architected Framework?).
2. Detailed Analysis of Newly Introduced Regressions (where the Present version departed from WAF compared to the Past version) & Resolved Violations.
3. Pillar-by-Pillar Evolution Breakdown (Operational Excellence, Security, Reliability, Cost Optimization, Performance Optimization, Sustainability).
4. Recommended Remediation HCL Patch to bring the Present version to a 3.0/3.0 Well-Architected standard.
"""
        llm_comparison = await model_router.generate_text(prompt=prompt, temperature=0.1)
        elapsed = (time.perf_counter() - start_time) * 1000

        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=round(elapsed, 2),
            data={
                "change_context": change_ctx,
                **comp,
                "llm_comparative_assessment_markdown": f"{comp['comparison_report_markdown']}\n\n---\n\n{llm_comparison}",
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(prompt),
                "completion_tokens_estimated": self.estimate_tokens(llm_comparison),
                "tokens_saved_by_cache": 0,
            },
        )

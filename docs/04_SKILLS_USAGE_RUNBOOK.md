# Skills Usage Runbook — Getting Started Examples & Expected Outputs for All 38 Registered Skills

This runbook provides copy-pasteable invocation examples and expected output structures for **all 38 skills** registered in the **Enterprise Agents Architectural Guidelines MCP Server** (`arch-guidelines` / `gea-arch-guidelines`).

---

## Quick Discovery Pattern (Two-Tier Progressive Disclosure)

Before invoking any skill, an agent can discover skills using `list_registered_skills` (Tier 1) and inspect a skill's parameter schema using `get_skill_manifest` (Tier 2):

```python
# Tier 1: List all 38 skills (or filter by category: 'architecture', 'governance', 'devops', 'knowledge_management', 'advisory', 'workflow', 'graph_data', 'security', 'workspace_skill')
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="list_registered_skills",
    Arguments={"category": "governance"}
)

# Tier 2: Hydrate full manifest & parameter schema for a specific skill
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="get_skill_manifest",
    Arguments={"skill_id": "skill_waf_all_pillars_spec_verifier"}
)
```

---

## Part 1: Well-Architected Framework (WAF) & PCA OKF Verification Skills (`OKF-PCA-01`..`09`)

### 1. `skill_waf_okf_search` — PCA & Well-Architected OKF Knowledge Base Search
* **When to use:** Search the 9-concept `GEAP_WAF_PILLARS` Dataplex OKF Knowledge Base (`OKF-PCA-01`–`09`) for 5-second service selection matrices, pillar principles, and the 18 forensic anti-patterns.
* **Usage (via `invoke_skill` or `search_waf_okf_best_practices`):**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_waf_okf_search",
          "parameters": {
              "query": "Cloud Spanner Interleaved Tables Stale Reads",
              "pillar": "performance_optimization",
              "service_area": "all"
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_waf_okf_search",
    "result": {
      "status": "success",
      "query": "Cloud Spanner Interleaved Tables Stale Reads",
      "pillar_filter": "performance_optimization",
      "dataplex_kb": {
        "corpus": "GEAP_WAF_PILLARS",
        "version_tag": "WAF_OKF_2026-11-24_182000",
        "stale_after": "2027-05-24T18:20:00-08:00"
      },
      "matched_concepts_count": 3,
      "matched_concepts": [
        {
          "concept_id": "OKF-PCA-01",
          "title": "Storage, Databases, BigQuery Analytics & Data Pipeline Architecture (WAF Performance & Reliability)",
          "gcs_uri": "gs://gea_agent_development_architectural_best_practices_pca_waf/WAF_OKF_2026-11-24_182000/okf/concepts/01-storage-databases-bigquery-and-data-pipelines.md"
        }
      ],
      "matched_antipatterns": [
        {
          "rule_id": "AP-PCA-14",
          "okf_concept": "OKF-PCA-03",
          "title": "Creating Separate Per-Region VPCs Connected by VPNs for Multi-Region Internal Traffic"
        }
      ]
    }
  }
  ```

---

### 2. `skill_waf_pillar_operational_excellence` — WAF Operational Excellence Pillar Verifier
* **When to use:** Verify a project design spec against the **Operational Excellence** pillar (`OKF-PCA-06`, `OKF-PCA-07`, `OKF-PCA-09`: Cloud Logging `_Required` vs `_Default`, Monitoring Heatmaps, Trace `X-Cloud-Trace-Context` vs Profiler, SRE SLIs/SLOs/Error Budgets, Cloud Build Private Pools, Cloud Deploy, Terraform GCS state, GKE GitOps).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_waf_pillar_operational_excellence",
          "parameters": {
              "architecture_description": "Microservices deployed via Google Cloud Deploy canary rollouts using Terraform with GCS backend state locking. Observability uses Cloud Ops Agent, Cloud Trace with W3C traceparent propagation, Cloud Profiler, and SRE error budgets.",
              "search_query": "Cloud Trace Profiler SRE Cloud Deploy"
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_waf_pillar_operational_excellence",
    "result": {
      "pillar_evaluation": {
        "pillar_id": "operational_excellence",
        "pillar_name": "1. Operational Excellence",
        "score": 2.77,
        "max_score": 3.0,
        "cutline_passed": true,
        "violations_detected": [],
        "okf_concepts_referenced": [{"concept_id": "OKF-PCA-06"}, {"concept_id": "OKF-PCA-07"}, {"concept_id": "OKF-PCA-09"}]
      },
      "verification_report_markdown": "## Operational Excellence Verification Report\n- **Verdict**: PASSED (>= 2.0 cutline)..."
    }
  }
  ```

---

### 3. `skill_waf_pillar_security` — WAF Security, Privacy & Compliance Pillar Verifier
* **When to use:** Verify a design spec against the **Security** pillar (`OKF-PCA-04`, `OKF-PCA-05`, `OKF-PCA-02`, `OKF-PCA-03`, `OKF-PCA-09`: ZAA, Workload Identity, Org Policies, IAM Deny, Secret Manager vs KMS/CSEK/EKM/Tink, Confidential VMs/GKE, VPC-SC + ACM Ingress, Cloud Armor + GFE firewall, IAP, Binary Authorization, DLP, ClamAV Quarantine).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_waf_pillar_security",
          "parameters": {
              "architecture_description": "Payment service storing DB passwords in Cloud KMS and supplying CSEK keys to BigQuery. Uses a VPC-SC Perimeter Bridge for human Cloud Console access."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_waf_pillar_security",
    "result": {
      "pillar_evaluation": {
        "pillar_id": "security",
        "pillar_name": "2. Security, Privacy & Compliance",
        "score": 0.2,
        "cutline_passed": false,
        "violations_detected": [
          {
            "rule_id": "AP-PCA-01",
            "okf_concept": "OKF-PCA-05",
            "antipattern_detected": "Using Cloud KMS to Store Plaintext Application Secrets, Passwords, or OAuth Tokens",
            "deterministic_fix": "Use Secret Manager (--set-secrets) to store secrets..."
          },
          {
            "rule_id": "AP-PCA-03",
            "okf_concept": "OKF-PCA-05",
            "antipattern_detected": "Supplying Customer-Supplied Encryption Keys (CSEK) to BigQuery",
            "deterministic_fix": "For BigQuery, use CMEK or Cloud EKM (External Key Manager)."
          },
          {
            "rule_id": "AP-PCA-07",
            "okf_concept": "OKF-PCA-05",
            "antipattern_detected": "Using a VPC-SC Perimeter Bridge to Grant Human Analysts Cloud Console Access",
            "deterministic_fix": "Configure Access Context Manager (Access Levels) and add an Ingress Rule on the VPC-SC perimeter."
          }
        ]
      }
    }
  }
  ```

---

### 4. `skill_waf_pillar_reliability` — WAF Reliability & DR Pillar Verifier
* **When to use:** Verify a design spec against the **Reliability** pillar (`OKF-PCA-01`, `OKF-PCA-03`, `OKF-PCA-06`, `OKF-PCA-08`, `OKF-PCA-09`: Spanner 99.999%, Cloud SQL Zonal HA vs Read Replicas, Redis Standard HA, Multi-Zone/Region GKE & Cloud Run, 2+2 Interconnect & HA VPN 99.99%, Cold/Warm/Hot DR RTO/RPO).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_waf_pillar_reliability",
          "parameters": {
              "architecture_description": "Hot active-active multi-region architecture (RTO=0, RPO=0) using Cloud Spanner Multi-Region (99.999% SLA), Regional GKE with Pod Topology Spread Constraints, Memorystore for Redis Standard Tier HA, and Cloud Pub/Sub behind a Global External ALB."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_waf_pillar_reliability",
    "result": {
      "pillar_evaluation": {
        "pillar_id": "reliability",
        "pillar_name": "3. Reliability & Fault Tolerance",
        "score": 3.0,
        "cutline_passed": true,
        "violations_detected": []
      }
    }
  }
  ```

---

### 5. `skill_waf_pillar_cost_optimization` — WAF Cost Optimization (FinOps) Pillar Verifier
* **When to use:** Verify a design spec against the **Cost Optimization (`FinOps`)** pillar (`OKF-PCA-01`, `OKF-PCA-02`, `OKF-PCA-04`, `OKF-PCA-06`, `OKF-PCA-07`, `OKF-PCA-09`: GKE Autopilot, Cloud Run scale-to-zero, Spot VMs, CUDs, BigQuery 90-day automatic 50% discount & Analytics Hub, GCS Autoclass, `_Default` Log Exclusion Filters, Billing Budgets + Pub/Sub).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_waf_pillar_cost_optimization",
          "parameters": {
              "architecture_description": "Uses GKE Autopilot, Cloud Run scale-to-zero, Spot VMs for stateless batch workers, Flexible CUDs, GCS Autoclass, BigQuery Partitioning/Clustering with 90-day Long-Term Storage, _Default log exclusion filters, and Billing Budgets wired to Pub/Sub."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_waf_pillar_cost_optimization",
    "result": {
      "pillar_evaluation": {
        "pillar_id": "cost_optimization",
        "pillar_name": "4. Cost Optimization (FinOps)",
        "score": 3.0,
        "cutline_passed": true,
        "violations_detected": []
      }
    }
  }
  ```

---

### 6. `skill_waf_pillar_performance_optimization` — WAF Performance Optimization Pillar Verifier
* **When to use:** Verify a design spec against the **Performance Optimization** pillar (`OKF-PCA-01`, `OKF-PCA-02`, `OKF-PCA-03`, `OKF-PCA-09`: Premium Tier Anycast Cold-Potato routing, Cloud CDN, Spanner Interleaved Tables + 15s Stale Reads, Bigtable `HighCardID#ReverseTimestamp` row keys, BigQuery BI Engine, Memorystore Redis, Vertex AI Context Caching).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_waf_pillar_performance_optimization",
          "parameters": {
              "architecture_description": "Global External ALB on Premium Network Tier with Cloud CDN, Cloud Spanner Interleaved Tables with 15s Stale Reads, Bigtable composite row keys (VehicleVIN#ReverseTimestamp), Memorystore for Redis sub-10ms cache, and Vertex AI GPU endpoints."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_waf_pillar_performance_optimization",
    "result": {
      "pillar_evaluation": {
        "pillar_id": "performance_optimization",
        "pillar_name": "5. Performance Optimization",
        "score": 3.0,
        "cutline_passed": true,
        "violations_detected": []
      }
    }
  }
  ```

---

### 7. `skill_waf_pillar_sustainability` — WAF Sustainability & Carbon Efficiency Pillar Verifier
* **When to use:** Verify a design spec against the **Sustainability** pillar (`OKF-PCA-01`, `OKF-PCA-02`, `OKF-PCA-04`, `OKF-PCA-09`: Low-carbon CFE% regions via `constraints/gcp.resourceLocations`, scale-to-zero serverless, GKE Autopilot bin-packing, Recommender API idle VM removal, storage lifecycle compaction).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_waf_pillar_sustainability",
          "parameters": {
              "architecture_description": "Workloads restricted to high CFE% carbon-free regions via constraints/gcp.resourceLocations, using serverless scale-to-zero Cloud Run, GKE Autopilot bin-packing, Recommender API idle VM cleanup, GCS Autoclass, and KV prefix caching."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_waf_pillar_sustainability",
    "result": {
      "pillar_evaluation": {
        "pillar_id": "sustainability",
        "pillar_name": "6. Sustainability & Carbon Efficiency",
        "score": 3.0,
        "cutline_passed": true,
        "violations_detected": []
      }
    }
  }
  ```

---

### 8. `skill_waf_all_pillars_spec_verifier` — Well-Architected All-Pillars Design Spec Verifier
* **When to use:** Verify any project design specification across **all 6 Well-Architected Framework pillars simultaneously**, cross-checking against `OKF-PCA-01`..`09` and all 18 forensic anti-patterns.
* **Usage (via `invoke_skill` or `verify_spec_all_waf_pillars`):**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="verify_spec_all_waf_pillars",
      Arguments={
          "architecture_spec": "Global platform using Terraform (GCS state), Cloud Deploy canary rollouts, Cloud Trace (traceparent), Workload Identity (ZAA), Secret Manager, CMEK, Confidential GKE, VPC-SC + ACM Ingress, Cloud Armor, Spanner Multi-Region (99.999%, Interleaved Tables, 15s Stale Reads), Redis Standard HA, GKE Autopilot, Spot VMs for batch, GCS Autoclass, BigQuery Partitioning/Clustering, Premium Network Tier + Cloud CDN, and CFE% region constraints.",
          "workload_type": "global_oltp_saas",
          "target_pillars": ["all"]
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "tool": "verify_spec_all_waf_pillars",
    "skill_id": "skill_waf_all_pillars_spec_verifier",
    "data": {
      "verdict": "WELL_ARCHITECTED_FOUNDATION_APPROVED",
      "composite_waf_score": 2.91,
      "production_cutline_met": true,
      "antipattern_violations": [],
      "scorecard_markdown": "# 🏛️ Google Cloud Well-Architected & PCA OKF v0.2 Compliance Scorecard\n- **Verdict**: `WELL_ARCHITECTED_FOUNDATION_APPROVED`\n- **Composite WAF Score**: `2.91 / 3.00`..."
    }
  }
  ```

---

### 9. `skill_waf_critique` — Google Cloud Well-Architected Framework Auditor
* **When to use:** Perform a full 6-pillar WAF review with quantitative scoring, High-Risk Issues (HRIs), Medium-Risk Issues (MRIs), and remediation roadmaps.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_waf_critique",
          "parameters": {
              "architecture_description": "Multi-agent customer support system on Vertex AI Reasoning Engine with Spanner Graph and Model Armor.",
              "workload_type": "multi_agent_system",
              "target_pillars": ["all"]
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_waf_critique",
    "result": {
      "workload_type": "multi_agent_system",
      "verdict": "WELL_ARCHITECTED_FOUNDATION_APPROVED",
      "composite_waf_score": 2.35,
      "waf_review_markdown": "# 🏛️ Google Cloud Well-Architected & PCA OKF v0.2 Compliance Scorecard..."
    }
  }
  ```

---

### 10. `skill_waf_pillar_critique` — WAF Pillar Deep Dive Auditor
* **When to use:** Drill down into a single WAF pillar for a specific section of an architecture document.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_waf_pillar_critique",
          "parameters": {
              "pillar_name": "security",
              "architecture_description": "Zero-trust agent perimeter using Workload Identity, Secret Manager, VPC-SC, and Model Armor."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_waf_pillar_critique",
    "result": {
      "pillar_name": "security",
      "pillar_evaluation": {"score": 2.6, "cutline_passed": true},
      "pillar_audit_markdown": "## Security Pillar Deep-Dive Audit..."
    }
  }
  ```

---

## Part 2: Terraform IaC, WAF Drift Verifier & Past-vs-Present Comparator Skills

### 11. `skill_terraform_waf_verifier` — Terraform Well-Architected Drift Verifier & Critic
* **When to use:** Verify an existing or current Terraform `.tf` script to see where it departs from the Google Cloud Well-Architected Framework (`OKF-PCA-01`..`09`) and generate a critique with remediated HCL.
* **Usage (via `invoke_skill` or `verify_terraform_waf_compliance`):**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="verify_terraform_waf_compliance",
      Arguments={
          "terraform_hcl": "terraform { backend \"local\" {} }\nresource \"google_service_account_key\" \"k\" { service_account_id = \"sa\" }\nresource \"google_sql_database_instance\" \"db\" { deletion_protection = false settings { availability_type = \"ZONAL\" } }",
          "workload_context": "production_payment_ledger"
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "tool": "verify_terraform_waf_compliance",
    "skill_id": "skill_terraform_waf_verifier",
    "data": {
      "verdict": "WAF_DEPARTURE_DETECTED",
      "is_waf_compliant": false,
      "composite_waf_score": 1.65,
      "resource_count": 2,
      "waf_departures": [
        {"rule_id": "TF-WAF-SEC-02", "severity": "CRITICAL", "pillar": "security", "okf_concept": "OKF-PCA-04", "title": "Long-Lived Service Account JSON Key Creation (google_service_account_key)"},
        {"rule_id": "TF-WAF-REL-01", "severity": "HIGH", "pillar": "reliability", "okf_concept": "OKF-PCA-01", "title": "Single-Zone Cloud SQL Instance (availability_type = ZONAL) or Deletion Protection Disabled"},
        {"rule_id": "TF-WAF-OPS-01", "severity": "MEDIUM", "pillar": "operational_excellence", "okf_concept": "OKF-PCA-07", "title": "Local Terraform Backend Instead of GCS Remote State"}
      ],
      "llm_terraform_critique_markdown": "# 🏗️ Terraform HCL Well-Architected Framework (WAF) Verification & Critique..."
    }
  }
  ```

---

### 12. `skill_terraform_version_comparator` — Terraform Past vs. Present WAF Version Comparator
* **When to use:** Compare a **past** Terraform version against a **present** Terraform version across all 6 WAF pillars to detect newly introduced WAF regressions, resolved violations, persistent departures, and resource diffs.
* **Usage (via `invoke_skill` or `compare_terraform_versions_waf`):**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="compare_terraform_versions_waf",
      Arguments={
          "past_terraform_hcl": "terraform { backend \"gcs\" { bucket = \"tf-state\" } }\nresource \"google_sql_database_instance\" \"db\" { deletion_protection = true settings { availability_type = \"REGIONAL\" } }",
          "present_terraform_hcl": "terraform { backend \"local\" {} }\nresource \"google_sql_database_instance\" \"db\" { deletion_protection = false settings { availability_type = \"ZONAL\" } }\nresource \"google_service_account_key\" \"k\" { service_account_id = \"sa\" }",
          "change_context": "Assess whether v2 hotfix departed from WAF compared to v1 baseline"
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "tool": "compare_terraform_versions_waf",
    "skill_id": "skill_terraform_version_comparator",
    "data": {
      "evolution_verdict": "WAF_REGRESSION_DETECTED",
      "past_composite_score": 2.13,
      "present_composite_score": 1.65,
      "composite_score_delta": -0.48,
      "resource_diff": {
        "added": ["google_service_account_key.k"],
        "removed": [],
        "modified": ["google_sql_database_instance.db"]
      },
      "newly_introduced_regressions": [
        {"rule_id": "TF-WAF-OPS-01", "pillar": "operational_excellence"},
        {"rule_id": "TF-WAF-REL-01", "pillar": "reliability"},
        {"rule_id": "TF-WAF-SEC-02", "pillar": "security"}
      ],
      "resolved_waf_violations": [],
      "comparison_report_markdown": "# 🔄 Past vs. Present Terraform Well-Architected Comparative Assessment..."
    }
  }
  ```

---

### 13. `skill_terraform_infra` — Terraform Infrastructure Auditor & Synthesizer
* **When to use:** Generate new least-privilege, WAF-compliant Terraform HCL for Cloud Spanner Graph, Vertex AI Reasoning Engine, BigQuery, KMS, and IAM.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_terraform_infra",
          "parameters": {
              "action": "generate",
              "infrastructure_requirements": "Cloud Spanner Graph instance with CMEK encryption, BigQuery analytics dataset, and dedicated least-privilege Service Account."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_terraform_infra",
    "result": {
      "action": "generate",
      "terraform_result_markdown": "```hcl\nterraform {\n  backend \"gcs\" {...}\n}..."
    }
  }
  ```

---

## Part 3: Architecture, Specification Generation & Modernization Skills

### 14. `skill-arch-eval` — Architecture Guidelines Evaluator
* **When to use:** Operational Spanner Graph lookup for validated architectural guidelines and patterns by topic.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={"skill_id": "skill-arch-eval", "parameters": {"topic": "Zero Ambient Authority"}}
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill-arch-eval",
    "entrypoint": "get_best_practice",
    "result": {
      "status": "success",
      "topic": "Zero Ambient Authority",
      "guidelines": [{"guideline_id": "DOC-02", "title": "Vibe Coding Agent Security & Evaluation"}],
      "patterns": [{"pattern_id": "PAT-ZAA", "name": "Zero Ambient Authority"}]
    }
  }
  ```

---

### 15. `skill_arbitrary_spec_generator` — Arbitrary Domain & Technology Spec Generator
* **When to use:** Generate an exhaustive engineering specification for any domain, language, or stack (`generate_arbitrary_spec`).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_arbitrary_spec_generator",
          "parameters": {
              "domain_or_topic": "Real-Time Cross-Border Payment Settlement Engine",
              "tech_stack_or_framework": "Go + gRPC + Cloud Spanner Multi-Region + Pub/Sub",
              "requirements": "100,000 TPS, external consistency, zero data loss (RPO=0), PCI-DSS tokenization.",
              "complexity_level": "principal_staff_exhaustive"
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_arbitrary_spec_generator",
    "result": {
      "domain": "Real-Time Cross-Border Payment Settlement Engine",
      "specification_markdown": "# Engineering Specification: Real-Time Cross-Border Payment Settlement Engine\n## 1. Executive Summary...\n## 2. Architectural Decisions (ADRs)..."
    }
  }
  ```

---

### 16. `skill_spec_best_practices_updater` — Specification Best Practices Updater
* **When to use:** Audit an existing technical specification and upgrade it with modern Google Cloud standards (ZAA, Dual-Pass Model Armor, Gemini 4 Argon / Gemini 3.1+, Spanner Graph ISO GQL, KV Prefix Caching).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_spec_best_practices_updater",
          "parameters": {
              "existing_spec_content": "# Legacy Chatbot Spec\nUses gemini-1.5-pro with a shared service account JSON key and stores state in local SQLite.",
              "standards_to_apply": ["ZAA", "WAF", "Model_Armor_Dual_Pass", "Context_Caching", "Modern_Models"],
              "strictness_level": "production_cutline_enforced"
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_spec_best_practices_updater",
    "result": {
      "strictness_level": "production_cutline_enforced",
      "upgraded_specification_markdown": "## 1. Architectural Gap Analysis...\n## 2. Remediation Summary & New ADRs...\n## 3. Upgraded Complete Technical Specification..."
    }
  }
  ```

---

### 17. `skill_codebase_to_spec_collection` — Codebase to 6-Part Spec Collection Generator
* **When to use:** Synthesize a 6-module specification collection (`01_high_level_architecture` through `06_iac_and_deployment`) from an existing codebase summary.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_codebase_to_spec_collection",
          "parameters": {
              "project_name": "Enterprise Order Orchestrator",
              "codebase_summary_or_path": "FastMCP server in src/, Spanner Graph client in src/graph/, Terraform in iac/",
              "enforce_fde_cutline": True
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_codebase_to_spec_collection",
    "result": {
      "project_name": "Enterprise Order Orchestrator",
      "fde_cutline_enforced": true,
      "spec_collection_markdown": "# 6-Part Specification Collection: Enterprise Order Orchestrator..."
    }
  }
  ```

---

### 18. `skill_spec_generator` — Architectural Spec Generator
* **When to use:** Generate a structured technical specification (RFC/Design Doc) with ADRs and sequence diagrams for a new feature or subsystem.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_spec_generator",
          "parameters": {
              "feature_title": "Federated A2A Agent Handoff Gateway",
              "context_and_goals": "Enable zero-trust task delegation across multi-agent boundaries using OIDC/WIF.",
              "target_audience": "principal_architects"
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_spec_generator",
    "result": {
      "feature_title": "Federated A2A Agent Handoff Gateway",
      "generated_spec_markdown": "# RFC: Federated A2A Agent Handoff Gateway..."
    }
  }
  ```

---

### 19. `skill_system_design` — Enterprise System Designer
* **When to use:** Synthesize an end-to-end Google Cloud enterprise system architecture with Mermaid diagrams, ZAA boundaries, and SLA/SLO envelopes.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_system_design",
          "parameters": {
              "system_name": "Global Clinical Decision Co-Pilot",
              "requirements": "HIPAA-compliant HL7/FHIR ingestion, multi-agent reasoning, sub-500ms retrieval.",
              "constraints": {"compliance": "HIPAA", "sla": "99.99%"},
              "multi_agent_enabled": True
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_system_design",
    "result": {
      "system_name": "Global Clinical Decision Co-Pilot",
      "zaa_enforced": true,
      "architecture_spec": "# System Architecture: Global Clinical Decision Co-Pilot..."
    }
  }
  ```

---

### 20. `skill_google_landing_metrics_critique` — Google Landing Metrics & Edge SLA Auditor
* **When to use:** Audit web/edge/API architectures against Google Landing Metrics, Core Web Vitals (`LCP <= 2.5s`, `INP <= 200ms`, `CLS <= 0.1`), Cloud CDN cache hit ratios, and p99 latency budgets.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_google_landing_metrics_critique",
          "parameters": {
              "system_or_frontend_spec": "Global Next.js storefront behind Global External ALB and Cloud CDN on Premium Network Tier.",
              "target_p99_ms": 150
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_google_landing_metrics_critique",
    "result": {
      "target_p99_ms": 150,
      "landing_metrics_audit_markdown": "## Google Landing Metrics & CWV Scorecard..."
    }
  }
  ```

---

### 21. `skill_spec_critique` — Architectural Spec Socratic Critic
* **When to use:** Subject a specification to adversarial Socratic grilling to uncover race conditions, split-brain hazards, and unstated assumptions.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_spec_critique",
          "parameters": {
              "spec_text": "Agents write directly to a shared Cloud Storage JSON file to coordinate distributed locks.",
              "critique_perspective": "scale_and_concurrency"
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_spec_critique",
    "result": {
      "perspective": "scale_and_concurrency",
      "critique_markdown": "## Socratic Architectural Critique (SCALE_AND_CONCURRENCY)\n1. **Anti-Pattern Detected**: Distributed lock contention on GCS object overwrites..."
    }
  }
  ```

---

### 22. `skill_spec_creation_workflow` — 5-Stage Specification Lifecycle Workflow Orchestrator
* **When to use:** Guide a spec through the 5-stage ARB lifecycle (`RFC -> ADR Review -> Implementation Draft -> Threat Model -> Sign-Off`).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_spec_creation_workflow",
          "parameters": {
              "project_title": "Multi-Region Agent Memory Bank",
              "current_stage": "threat_model",
              "draft_content": "Uses Cloud Spanner Graph with CMEK and VPC-SC."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_spec_creation_workflow",
    "result": {
      "project_title": "Multi-Region Agent Memory Bank",
      "current_stage": "threat_model",
      "workflow_output_markdown": "## Stage 4: Threat Model & ARB Gate Review..."
    }
  }
  ```

---

## Part 4: FDE Field-Readiness Governance & Complete System Audit Skills

### 23. `skill-fde-governance` — FDE Field-Readiness Auditor
* **When to use:** Audit a project against the Google Cloud FDE Field-Readiness Rubric competencies.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill-fde-governance",
          "parameters": {
              "project_manifest_or_description": "Enterprise multi-agent system with ZAA, Model Armor, Spanner Graph, and OTel tracing."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill-fde-governance",
    "entrypoint": "audit_project_against_fde_rubric",
    "result": {
      "audit_status": "executed",
      "evaluated_rubric_items_count": 37,
      "summary": "Audited project with 37 rubric items."
    }
  }
  ```

---

### 24. `skill_rubric_level_critique` — FDE Rubric Sub-Competency Grader
* **When to use:** Grade a system against a specific FDE Rubric sub-competency (`0.0–3.0`, cutline `>= 2.0`).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_rubric_level_critique",
          "parameters": {
              "subcompetency_id": "RUBRIC-B-3-1",
              "system_summary": "Enforces Zero Ambient Authority with downscoped STS tokens, Dual-Pass Model Armor, and Principal Access Boundaries."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_rubric_level_critique",
    "result": {
      "subcompetency_id": "RUBRIC-B-3-1",
      "rubric_evaluation_markdown": "### Sub-Competency RUBRIC-B-3-1 Score: 3.0 / 3.0 (PASS)..."
    }
  }
  ```

---

### 25. `skill_complete_system_audit` — Comprehensive 360-Degree Multi-Pillar System Auditor
* **When to use:** Execute a full release-readiness certification audit combining WAF, all FDE Rubric parts (`Part A` + `Part B.1`..`B.8`), and Model Armor security checks.
* **Usage (via `invoke_skill` or `audit_complete_system`):**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="audit_complete_system",
      Arguments={
          "project_name": "GEA Architecture Guidelines MCP Server",
          "full_system_spec_or_code_manifest": "FastMCP server with 29 tools, 38 skills, 92 OKF concepts in Dataplex/GCS/Spanner/BQ, Dual-Pass Model Armor, ZAA downscoping, and KV prefix caching."
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "tool": "audit_complete_system",
    "data": {
      "project_name": "GEA Architecture Guidelines MCP Server",
      "audit_verdict_markdown": "# 360-Degree FDE & WAF Certification Scorecard\n- **Executive Verdict**: FIELD_READY_PRODUCTION_APPROVED..."
    }
  }
  ```

---

## Part 5: Knowledge Management, Alexandria Search, Graph & Security Skills

### 26. `skill_alexandria_search` — Alexandria Verified Best Practices Search
* **When to use:** Search verified Google Cloud Alexandria architectural blueprints and whitepapers grounded in the Cloud FDE Charter (`alexandria_search`).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="alexandria_search",
      Arguments={
          "query": "Zero Ambient Authority Principal Access Boundary Vertex AI Reasoning Engine",
          "domain": "security",
          "top_k": 5
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "tool": "alexandria_search",
    "data": {
      "query": "Zero Ambient Authority Principal Access Boundary Vertex AI Reasoning Engine",
      "domain": "security",
      "alexandria_results_markdown": "## 1. Executive Architectural Recommendation...\n## 2. Verified Alexandria Reference Blueprints..."
    }
  }
  ```

---

### 27. `skill_discovery_and_catalog` — Dynamic Skills Discovery & Catalog Engine
* **When to use:** Recommend an optimal sequence of skills for a complex engineering goal and estimate total token budget.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_discovery_and_catalog",
          "parameters": {
              "task_description": "Audit our existing Terraform scripts, upgrade our system spec to WAF standards, and run a 360 FDE certification check."
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_discovery_and_catalog",
    "result": {
      "total_registered_skills": 38,
      "recommended_skill_chain": [
        "skill_terraform_waf_verifier",
        "skill_spec_best_practices_updater",
        "skill_waf_all_pillars_spec_verifier",
        "skill_complete_system_audit"
      ]
    }
  }
  ```

---

### 28. `skill-okf-evolution` — Autonomous OKF Evolution Maintainer
* **When to use:** Check corpus freshness across all OKF concepts (`check_okf_freshness`).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={"skill_id": "skill-okf-evolution", "parameters": {"threshold_days": 30}}
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill-okf-evolution",
    "entrypoint": "check_okf_freshness",
    "result": {
      "status": "success",
      "total_concepts": 83,
      "fresh_count": 83,
      "expiring_soon_count": 0,
      "expired_count": 0,
      "freshness_index_percentage": 100.0
    }
  }
  ```

---

### 29. `skill_okf_evolution_agent` — Monthly OKF Evolution Agent
* **When to use:** Run an automated freshness check and synthesize a grounded concept revision proposal.
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill_okf_evolution_agent",
          "parameters": {
              "target_concept_id": "33-model-armor-securing-ai-deployments",
              "research_topic": "Model Armor Dual-Pass Egress DLP 2026"
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill_okf_evolution_agent",
    "result": {
      "target_concept_id": "33-model-armor-securing-ai-deployments",
      "freshness_summary": {"freshness_index_percentage": 100.0},
      "evolution_proposal": {"status": "success", "new_stale_after": "2027-05-24T..."}
    }
  }
  ```

---

### 30. `skill-nl2kg-triplification` — NL2KG Triplification & Knowledge Graph Pipeline
* **When to use:** Perform deep-dive analytical inspection of a component in BigQuery and Spanner Graph (`deep_dive_guideline`).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={"skill_id": "skill-nl2kg-triplification", "parameters": {"component": "Security"}}
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill-nl2kg-triplification",
    "entrypoint": "deep_dive_guideline",
    "result": {
      "status": "success",
      "component": "Security",
      "row_count": 15,
      "details": [{"guideline_id": "DOC-02", "pattern_name": "Zero Ambient Authority"}]
    }
  }
  ```

---

### 31. `skill-security-auditor` — Zero Ambient Authority & Model Armor Auditor
* **When to use:** Evaluate security trade-offs between managed Zero Ambient Authority architectures and self-managed/ambient credential alternatives (`evaluate_design_tradeoffs`).
* **Usage:**
  ```python
  call_mcp_tool(
      ServerName="arch-guidelines",
      ToolName="invoke_skill",
      Arguments={
          "skill_id": "skill-security-auditor",
          "parameters": {
              "option_a": "Workload Identity + Downscoped STS Tokens + Model Armor",
              "option_b": "Long-Lived Service Account JSON Keys"
          }
      }
  )
  ```
* **Expected Output:**
  ```json
  {
    "status": "success",
    "skill_id": "skill-security-auditor",
    "entrypoint": "evaluate_design_tradeoffs",
    "result": {
      "option_a": "Workload Identity + Downscoped STS Tokens + Model Armor",
      "option_b": "Long-Lived Service Account JSON Keys",
      "security_posture": "Managed solutions enforce IAM and audit logs natively...",
      "recommendation": "Prefer Workload Identity + Downscoped STS Tokens + Model Armor..."
    }
  }
  ```

---

## Part 6: Standalone Workspace `SKILL.md` Skills (`32`–`38`)

These 7 workspace skills represent `.agents/skills/<name>/SKILL.md` playbooks discovered into the registry for progressive disclosure and agent orchestration:

### 32. `skill_enterprise_system_design` (`.agents/skills/enterprise-system-design/SKILL.md`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={"skill_id": "skill_enterprise_system_design", "parameters": {"input_payload": "Design a multi-region agentic RAG platform."}}
)
```
* **Expected Output:** `{"status": "success", "skill_id": "skill_enterprise_system_design", "entrypoint": "execute", "result": {"message": "Skill 'skill_enterprise_system_design' executed entrypoint 'execute'."}}`

### 33. `skill_eval_harness` (`.agents/skills/eval-harness/SKILL.md`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={"skill_id": "skill_eval_harness", "parameters": {"input_payload": "Run retrieval precision benchmark."}}
)
```
* **Expected Output:** `{"status": "success", "skill_id": "skill_eval_harness", "entrypoint": "execute", "result": {"message": "Skill 'skill_eval_harness' executed entrypoint 'execute'."}}`

### 34. `skill_fastmcp_tool_dev` (`.agents/skills/fastmcp-tool-dev/SKILL.md`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={"skill_id": "skill_fastmcp_tool_dev", "parameters": {"input_payload": "Validate stdio and sse protocol compliance."}}
)
```
* **Expected Output:** `{"status": "success", "skill_id": "skill_fastmcp_tool_dev", "entrypoint": "execute", "result": {"message": "Skill 'skill_fastmcp_tool_dev' executed entrypoint 'execute'."}}`

### 35. `skill_fde_governance_auditor` (`.agents/skills/fde-governance-auditor/SKILL.md`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={"skill_id": "skill_fde_governance_auditor", "parameters": {"input_payload": "Audit project against FDE 26 sub-competencies."}}
)
```
* **Expected Output:** `{"status": "success", "skill_id": "skill_fde_governance_auditor", "entrypoint": "execute", "result": {"message": "Skill 'skill_fde_governance_auditor' executed entrypoint 'execute'."}}`

### 36. `skill_google_landing_metrics` (`.agents/skills/google-landing-metrics/SKILL.md`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={"skill_id": "skill_google_landing_metrics", "parameters": {"input_payload": "Verify LCP, INP, CLS, and CDN hit ratio."}}
)
```
* **Expected Output:** `{"status": "success", "skill_id": "skill_google_landing_metrics", "entrypoint": "execute", "result": {"message": "Skill 'skill_google_landing_metrics' executed entrypoint 'execute'."}}`

### 37. `skill_nl2kg_triplification` (`.agents/skills/nl2kg-triplification/SKILL.md`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={"skill_id": "skill_nl2kg_triplification", "parameters": {"input_payload": "Extract knowledge graph triples from markdown."}}
)
```
* **Expected Output:** `{"status": "success", "skill_id": "skill_nl2kg_triplification", "entrypoint": "execute", "result": {"message": "Skill 'skill_nl2kg_triplification' executed entrypoint 'execute'."}}`

### 38. `skill_okf_auto_evolution` (`.agents/skills/okf-auto-evolution/SKILL.md`)
```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={"skill_id": "skill_okf_auto_evolution", "parameters": {"input_payload": "Check 6-month TTL freshness and sync to Dataplex."}}
)
```
* **Expected Output:** `{"status": "success", "skill_id": "skill_okf_auto_evolution", "entrypoint": "execute", "result": {"message": "Skill 'skill_okf_auto_evolution' executed entrypoint 'execute'."}}`

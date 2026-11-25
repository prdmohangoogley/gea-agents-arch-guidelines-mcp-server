"""PCA & Well-Architected Framework (WAF) OKF Knowledge Base Skills Library.

Provides per-pillar and all-pillar search, verification, and architectural design
spec compliance auditing grounded in the Google Cloud Dataplex OKF v0.2 Knowledge Base
(Corpus: GEAPL200_PCA_WAF, Concepts: OKF-PCA-01 through OKF-PCA-09).
"""

from __future__ import annotations

import json
from pathlib import Path
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

# Locate the PCA/WAF OKF bundle in the MCP repository (`data/okf/pca_waf` or `okf/pca_waf`) or fallback to PCA-Exam-Prep source
_REPO_ROOT = Path(__file__).resolve().parents[3]
_DATA_PCA_WAF_DIR = _REPO_ROOT / "data" / "okf" / "pca_waf"
_MCP_PCA_WAF_DIR = _REPO_ROOT / "okf" / "pca_waf"
_SOURCE_PCA_WAF_DIR = Path("/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/Architect-Best-Practices")

DATAPLEX_KB_METADATA = {
    "corpus": "GEAP_WAF_PILLARS",
    "version_tag": "WAF_OKF_2026-11-24_182000",
    "tier_version_tags": {
        "L200": "L200_OKF_2026-11-24_182000",
        "L300": "L300_OKF_2026-11-24_182000",
        "L400": "L400_OKF_2026-11-24_182000",
        "WAF": "WAF_OKF_2026-11-24_182000",
    },
    "l400_version": "L400_version_20261124_1820",
    "timestamp": "2026-11-24T18:20:00-08:00",
    "stale_after": "2027-05-24T18:20:00-08:00",
    "ttl": "P6M",
    "project_id": "fivedaysai-prd-sandbox-317383",
    "location": "us",
    "dataplex_entry_group": "projects/fivedaysai-prd-sandbox-317383/locations/us/entryGroups/geapl200-architecture-kb",
    "dataplex_pca_waf_entry_group": "projects/fivedaysai-prd-sandbox-317383/locations/us/entryGroups/geapl200-pca-waf-kb",
    "dataplex_aspect_type": "projects/fivedaysai-prd-sandbox-317383/locations/us/aspectTypes/okf",
    "dataplex_pca_waf_aspect_type": "projects/fivedaysai-prd-sandbox-317383/locations/us/aspectTypes/okf-pca-waf",
    "gcs_bucket": "gs://gea_agent_development_architectural_best_practices_pca_waf",
    "gcs_versioned_prefix": "gs://gea_agent_development_architectural_best_practices_pca_waf/WAF_OKF_2026-11-24_182000/okf",
    "mcp_gcs_mirror": "gs://gea_agent_development_architectural_best_practices_1790796607/okf",
}

# Mapping of each WAF Pillar to its authoritative OKF-PCA concepts, principles, enablers, and verification checks
WAF_PILLAR_DEFINITIONS: dict[str, dict[str, Any]] = {
    "operational_excellence": {
        "pillar_id": "operational_excellence",
        "display_name": "1. Operational Excellence",
        "okf_concepts": ["OKF-PCA-06", "OKF-PCA-07", "OKF-PCA-09"],
        "service_areas": ["observability_sre", "devops_cicd_terraform_api", "decision_matrices_antipatterns"],
        "core_principles": [
            "Automate infrastructure as code (Terraform with GCS remote state locking and object versioning).",
            "Eliminate manual toil (<50% of SRE time) and govern releases via user-centric SLIs, SLOs (stricter than external SLAs), and Error Budgets.",
            "Deploy small, reversible changes using Google Cloud Deploy and progressive delivery (Rolling Update with readinessProbe, Blue-Green, Canary, A/B ALB URL Maps, or L7 Shadow requestMirrorPolicy).",
            "Build full-stack observability from Day 1: Cloud Logging (_Required 400d free vs _Default with exclusion filters), Cloud Monitoring (Ops Agent for RAM/Disk, Heatmap latency charts for p50/p95/p99), Cloud Trace (with X-Cloud-Trace-Context / W3C traceparent propagation), Cloud Profiler (CPU/Heap flame graphs), and Error Reporting.",
            "Enforce GitOps on GKE via Config Sync, Config Connector (KCC), and Policy Controller (OPA Gatekeeper).",
        ],
        "primary_gcp_enablers": [
            "Terraform (GCS Backend)",
            "Cloud Build (Private Pools)",
            "Artifact Registry (Standard/Remote/Virtual)",
            "Google Cloud Deploy",
            "Config Sync / Config Connector / Policy Controller",
            "Cloud Logging / Cloud Monitoring / Cloud Ops Agent",
            "Cloud Trace / Cloud Profiler / Error Reporting",
            "Apigee / API Gateway / Cloud Endpoints (ESPv2)",
        ],
        "positive_signals": [
            r"terraform",
            r"cloud build|cloud deploy|artifact registry|ci/cd|gitops|config sync",
            r"cloud trace|traceparent|x-cloud-trace-context|opentelemetry|otel",
            r"cloud monitoring|ops agent|heatmap|prometheus|gmp",
            r"sli|slo|error budget|postmortem|canary|blue-green|rolling|readinessprobe",
            r"cloud logging|log sink|log router",
        ],
    },
    "security": {
        "pillar_id": "security",
        "display_name": "2. Security, Privacy & Compliance",
        "okf_concepts": ["OKF-PCA-04", "OKF-PCA-05", "OKF-PCA-02", "OKF-PCA-03", "OKF-PCA-09"],
        "service_areas": ["identity_iam_finops", "security_kms_vpcsc", "compute_gke_serverless_ai", "networking_hybrid_dns", "decision_matrices_antipatterns"],
        "core_principles": [
            "Enforce Zero Trust (BeyondCorp) and Zero Ambient Authority (ZAA): keyless authentication via Workload Identity / Workload Identity Federation, short-lived downscoped tokens, and zero service account JSON keys (constraints/iam.disableServiceAccountKeyCreation).",
            "Store application secrets, DB passwords, TLS keys, and OAuth tokens strictly in Secret Manager (--set-secrets), never in Cloud KMS or plaintext config.",
            "Select the right encryption tier: GMEK (default), CMEK (Cloud KMS rotation), Cloud HSM (FIPS 140-2 L3), CSEK (GCS and GCE Persistent Disks ONLY—never BigQuery), Cloud EKM (external keys for BigQuery/GCS/GCE), Tink ALE (client-side field encryption before DB), and Confidential VMs/GKE Nodes (AMD SEV / Intel TDX hardware RAM encryption for data in-use).",
            "Protect APIs from data exfiltration using VPC Service Controls (VPC-SC) with Access Context Manager Ingress Rules for human Cloud Console access (never Perimeter Bridges for human access).",
            "Protect edge and internal access with Cloud Armor + VPC Ingress Firewall locked down strictly to GFE/Health Check ranges (130.211.0.0/22, 35.191.0.0/16) and Identity-Aware Proxy (IAP).",
            "Enforce container supply-chain integrity with Binary Authorization + Container Analysis API Attestation occurrences.",
            "Comply with PCI-DSS (tokenize PANs at capture with Cloud DLP), HIPAA (de-identify PHI in flight via Dataflow + Cloud DLP before BigQuery), and GCS Malware Scanning (Two-Bucket Quarantine + Eventarc + Cloud Run ClamAV).",
        ],
        "primary_gcp_enablers": [
            "Cloud Identity / GCDS / Managed Microsoft AD / Identity Platform (GCIP)",
            "Workload Identity / Workload Identity Federation / IAM Deny & Conditions",
            "Organization Policies (publicAccessPrevention, vmExternalIpAccess, resourceLocations)",
            "Secret Manager",
            "Cloud KMS / Cloud HSM / Cloud EKM / Google Tink (ALE)",
            "Confidential VMs & Confidential GKE Nodes",
            "VPC Service Controls (VPC-SC) + Access Context Manager",
            "Google Cloud Armor + Identity-Aware Proxy (IAP)",
            "Binary Authorization + Container Analysis API",
            "Sensitive Data Protection (Cloud DLP) + Model Armor",
        ],
        "positive_signals": [
            r"workload identity|zero ambient authority|zaa|downscoped|impersonat",
            r"secret manager",
            r"cmek|cloud kms|ekm|confidential vm|confidential gke|tink",
            r"vpc service controls|vpc-sc|access context manager|principal access boundar|pab",
            r"cloud armor|iap|identity-aware proxy",
            r"binary authorization|organization polic|publicaccessprevention",
            r"cloud dlp|sensitive data protection|model armor",
        ],
    },
    "reliability": {
        "pillar_id": "reliability",
        "display_name": "3. Reliability & Fault Tolerance",
        "okf_concepts": ["OKF-PCA-01", "OKF-PCA-03", "OKF-PCA-06", "OKF-PCA-08", "OKF-PCA-09"],
        "service_areas": ["storage_databases", "networking_hybrid_dns", "observability_sre", "migration_dr_case_studies", "decision_matrices_antipatterns"],
        "core_principles": [
            "Design for zonal and regional failure (N+1 or N+2 redundancy) using Multi-Zone MIGs, Regional GKE with Pod Topology Spread Constraints, or Multi-Region Cloud Run behind a Global External Application Load Balancer.",
            "Match database availability to SLA requirements: Cloud Spanner Multi-Region (99.999% SLA, zero-downtime Hot DR), Cloud SQL Zonal HA (synchronous standby for automatic failover; separate Read Replicas for read offload; Cross-Region Read Replica for regional DR), Memorystore for Redis Standard Tier HA (never Memcached for HA).",
            "Decouple microservices and absorb traffic spikes asynchronously with Cloud Pub/Sub (with Dead-Letter Topics and Schemas) and Cloud Dataflow (Event-Time Windowing, Watermarks, Allowed Lateness).",
            "Architect deterministic hybrid connectivity: 99.99% SLA requires 2+2 Dedicated/Partner Interconnect across 2 metropolitan edge zones (EADs) or HA VPN (2 tunnels to 2 interfaces) with Dynamic BGP on Cloud Router (TCP port 179).",
            "Align Disaster Recovery (DR) architecture to business RTO/RPO: Cold DR (hours RTO/RPO, GCS backups + Terraform on-demand), Warm Standby (minutes RTO/RPO, Cross-Region Read Replica + minimal MIG), Hot Active-Active (~0s RTO/0-byte RPO, Spanner Multi-Region + Multi-Region GKE/Cloud Run).",
        ],
        "primary_gcp_enablers": [
            "Cloud Spanner Multi-Region (99.999% SLA)",
            "Cloud SQL High Availability + Cross-Region Read Replicas / AlloyDB",
            "Cloud Bigtable Multi-Cluster Replication",
            "Cloud Memorystore for Redis Standard Tier HA",
            "Multi-Zone MIGs / Regional GKE (Pod Topology Spread Constraints)",
            "Global External Application Load Balancer + Cloud CDN",
            "2+2 Dedicated Interconnect / HA VPN (99.99% SLA)",
            "Cloud Pub/Sub + Database Migration Service (DMS)",
        ],
        "positive_signals": [
            r"multi-region|multi-zone|regional|high availability|\bha\b|failover",
            r"spanner|read replica|redis.*ha|multi-cluster",
            r"rto|rpo|disaster recovery|\bdr\b|backup|pitr",
            r"pub/sub|asynchronous|decoupl|circuit break|retry|exponential backoff",
            r"load balanc|anycast|health check|topology spread|anti-affinity",
        ],
    },
    "cost_optimization": {
        "pillar_id": "cost_optimization",
        "display_name": "4. Cost Optimization (FinOps)",
        "okf_concepts": ["OKF-PCA-01", "OKF-PCA-02", "OKF-PCA-04", "OKF-PCA-06", "OKF-PCA-07", "OKF-PCA-09"],
        "service_areas": ["storage_databases", "compute_gke_serverless_ai", "identity_iam_finops", "observability_sre", "devops_cicd_terraform_api", "decision_matrices_antipatterns"],
        "core_principles": [
            "Pay only for what you consume: use Cloud Run / Cloud Run Jobs (scale to zero) for stateless HTTP/batch workloads and GKE Autopilot (billed strictly per Pod CPU/Memory request).",
            "Leverage BigQuery FinOps laws: Batch loads from GCS are 100% FREE; tables/partitions unmodified for 90 consecutive days automatically receive a 50% Long-Term Storage discount ($0.01/GB/month—never export to GCS to save money!); Partition by date + Cluster by high-cardinality filter columns; use Analytics Hub so external subscribers pay for their own query compute.",
            "Optimize Compute Engine & Dataproc costs: use Spot VMs (60-91% discount, 30s preemption notice) strictly for stateless batch or Dataproc secondary workers; attach Instance Schedules for 9-to-5 weekday dev/test VMs; query the Recommender API for idle/oversized VM rightsizing; stack Resource-based and Spend-based Flexible CUDs.",
            "Automate Cloud Storage lifecycle tiering (Standard -> Nearline 30d -> Coldline 90d -> Archive 365d) or enable Autoclass.",
            "Enforce FinOps governance: export Detailed Usage Cost billing data to a Multi-Region (US/EU) BigQuery dataset (for automatic previous-month backfill), enforce billing labels via Terraform modules, and wire Cloud Billing Budgets -> Pub/Sub -> Cloud Run function to enforce hard spending caps.",
            "Reduce observability ingestion costs by adding Exclusion Filters on the paid _Default log bucket while routing compliance archives to GCS Coldline/Archive.",
        ],
        "primary_gcp_enablers": [
            "GKE Autopilot & Cloud Run / Cloud Run Jobs (Scale-to-Zero)",
            "Spot VMs & Compute Engine Instance Schedules",
            "Recommender API (VM & IAM Right-Sizing)",
            "Resource-Based & Compute Flexible Committed Use Discounts (CUDs)",
            "Cloud Storage Autoclass & Object Lifecycle Management",
            "BigQuery 90-Day Automatic Long-Term Storage, Partitioning/Clustering & Analytics Hub",
            "Cloud Billing Budgets + Pub/Sub Automated Cap + Multi-Region Detailed BQ Export",
            "Cloud Logging _Default Exclusion Filters & Cloud Build Right-Sized Machine Types",
        ],
        "positive_signals": [
            r"scale-to-zero|scale to zero|cloud run|autopilot",
            r"spot vm|preemptible|instance schedule|recommender|cud|committed use",
            r"autoclass|lifecycle|nearline|coldline|archive|long-term storage",
            r"partition|cluster|analytics hub|batch load",
            r"billing export|budget|finops|cost|exclusion filter|kv.*cach|prefix.*cach|token",
        ],
    },
    "performance_optimization": {
        "pillar_id": "performance_optimization",
        "display_name": "5. Performance Optimization",
        "okf_concepts": ["OKF-PCA-01", "OKF-PCA-02", "OKF-PCA-03", "OKF-PCA-09"],
        "service_areas": ["storage_databases", "compute_gke_serverless_ai", "networking_hybrid_dns", "decision_matrices_antipatterns"],
        "core_principles": [
            "Terminate user connections at the nearest Google Edge PoP using Premium Network Tier (global Anycast IP, cold-potato routing over Google private fiber) + Global External Application Load Balancer + Cloud CDN / Media CDN.",
            "Optimize Cloud Spanner performance: use Interleaved Tables (INTERLEAVE IN PARENT) to physically co-locate parent-child rows in the same split, and use 15-second Stale Reads + extra Nodes/Processing Units to absorb 10x read spikes from local replicas without Paxos leader round-trips.",
            "Eliminate Cloud Bigtable hotspotting: design composite row keys as HighCardinalityID#ReverseTimestamp (e.g., VehicleVIN#ReverseTimestamp); never start row keys with a sequential timestamp or static prefix.",
            "Accelerate analytics and caching: combine BigQuery Partitioning + Clustering + BI Engine in-memory acceleration; place Memorystore for Redis in front of relational/NoSQL databases for sub-millisecond reads.",
            "Tune compute & AI accelerators: enable --no-cpu-throttling ('CPU Always Allocated') on Cloud Run when background threads run outside HTTP requests; attach a2-highgpu node pools + NVIDIA Driver DaemonSet on GKE Standard; combine CPU preprocessing and GPU inference in a custom container on Vertex AI Endpoints; enable LLM Context Caching for repeated prompts.",
        ],
        "primary_gcp_enablers": [
            "Premium Network Tier (Global Anycast IP & Cold-Potato Routing)",
            "Global External ALB + Cloud CDN / Media CDN (Signed URLs/Cookies)",
            "Cloud Spanner Interleaved Tables + Stale Reads (15s)",
            "Cloud Bigtable (HighCardinalityID#ReverseTimestamp Row Keys)",
            "BigQuery Partitioning + Clustering + BI Engine",
            "Cloud Memorystore for Redis",
            "Cloud Filestore Enterprise (RWX NFS) & Google Cloud NetApp Volumes (SMB)",
            "Vertex AI Custom Containers (CPU+GPU) & Context Caching",
        ],
        "positive_signals": [
            r"premium.*tier|anycast|cloud cdn|media cdn|edge",
            r"interleave|stale read|reverse.*timestamp|row key|bi engine",
            r"memorystore|redis|cache|caching|low-latency|p99|p95|sub-10ms|sub-100ms",
            r"gpu|tpu|a2-highgpu|no-cpu-throttling|partition|cluster",
        ],
    },
    "sustainability": {
        "pillar_id": "sustainability",
        "display_name": "6. Sustainability & Carbon Efficiency",
        "okf_concepts": ["OKF-PCA-01", "OKF-PCA-02", "OKF-PCA-04", "OKF-PCA-09"],
        "service_areas": ["compute_gke_serverless_ai", "storage_databases", "identity_iam_finops", "decision_matrices_antipatterns"],
        "core_principles": [
            "Select Low-Carbon / High Carbon-Free Energy (CFE%) Google Cloud regions and enforce regional placement via Organization Policy (constraints/gcp.resourceLocations).",
            "Maximize hardware utilization and eliminate idle compute via serverless scale-to-zero runtimes (Cloud Run, Cloud Run Jobs, Cloud Functions, Dataflow, BigQuery) and bin-packed GKE Autopilot.",
            "Continuously decommission zombie/idle VMs and right-size overprovisioned instances using the Recommender API and Compute Engine Instance Schedules.",
            "Minimize redundant data movement and storage footprint via BigQuery Table Expiration for temporary staging tables, GCS Autoclass / Lifecycle policies, and LLM KV-Prefix Context Caching.",
        ],
        "primary_gcp_enablers": [
            "Google Cloud Carbon Footprint & CFE% Region Selection (constraints/gcp.resourceLocations)",
            "Cloud Run / Cloud Run Jobs / GKE Autopilot (Bin-Packing & Scale-to-Zero)",
            "Recommender API & Compute Engine Instance Schedules",
            "BigQuery Default Table Expiration & GCS Autoclass",
            "Vertex AI KV-Prefix Context Caching & Tiered Model Routing",
        ],
        "positive_signals": [
            r"carbon|sustainability|cfe|green|region.*select|resourcelocations",
            r"scale-to-zero|scale to zero|serverless|cloud run|autopilot",
            r"idle|right-siz|recommender|instance schedule|table expiration|autoclass|prefix.*cach",
        ],
    },
}

# Deterministic 18 High-Frequency Architectural Anti-Patterns from OKF-PCA-09
WAF_ANTIPATTERN_RULES: list[dict[str, Any]] = [
    {
        "rule_id": "AP-PCA-01",
        "okf_concept": "OKF-PCA-05",
        "pillar": "security",
        "title": "Using Cloud KMS to Store Plaintext Application Secrets, Passwords, or OAuth Tokens",
        "pattern_regex": r"kms.*(?:store|save|hold).*(?:password|secret|oauth|token|api[ _-]?key)|store.*(?:password|secret|oauth).*in.*(?:cloud )?kms",
        "remediation": "Use Secret Manager (--set-secrets) to store secrets, passwords, and OAuth tokens; use Cloud KMS strictly for cryptographic keys (CMEK) and digital signing.",
    },
    {
        "rule_id": "AP-PCA-02",
        "okf_concept": "OKF-PCA-02",
        "pillar": "security",
        "title": "Using Shielded VMs/Nodes When Data In-Use (RAM/Memory) Encryption Is Required",
        "pattern_regex": r"shielded (?:vm|node|gke).*(?:encrypt.*ram|encrypt.*memory|in-use encryption)|(?:encrypt.*ram|in-use encryption).*shielded (?:vm|node|gke)",
        "remediation": "Select Confidential VMs / Confidential GKE Nodes (AMD SEV / Intel TDX hardware memory encryption). Shielded VMs only verify boot/kernel integrity (Secure Boot, vTPM).",
    },
    {
        "rule_id": "AP-PCA-03",
        "okf_concept": "OKF-PCA-05",
        "pillar": "security",
        "title": "Supplying Customer-Supplied Encryption Keys (CSEK) to BigQuery",
        "pattern_regex": r"csek.*bigquery|bigquery.*csek|customer-supplied encryption key.*bigquery",
        "remediation": "CSEK is supported ONLY on Cloud Storage and Compute Engine Persistent Disks. For BigQuery, use CMEK or Cloud EKM (External Key Manager).",
    },
    {
        "rule_id": "AP-PCA-04",
        "okf_concept": "OKF-PCA-04",
        "pillar": "security",
        "title": "Creating a Custom IAM Role at the Folder Level",
        "pattern_regex": r"custom (?:iam )?role.*folder level|create.*custom (?:iam )?role.*--folder|folder-level custom role",
        "remediation": "Custom IAM Roles can ONLY be created at the Organization or Project level—never at the Folder level. Create at the Organization level and bind at the Folder level.",
    },
    {
        "rule_id": "AP-PCA-05",
        "okf_concept": "OKF-PCA-06",
        "pillar": "cost_optimization",
        "title": "Attempting to Disable or Delete the _Required Cloud Logging Bucket",
        "pattern_regex": r"(?:disable|delete|drop|exclude).*_required.*bucket|_required.*bucket.*(?:disable|delete|cost)",
        "remediation": "The _Required log bucket (Admin Activity & System Event logs) has a fixed 400-day retention, is 100% FREE, and cannot be disabled. Add Exclusion Filters to the _Default bucket instead.",
    },
    {
        "rule_id": "AP-PCA-06",
        "okf_concept": "OKF-PCA-07",
        "pillar": "operational_excellence",
        "title": "Confusing VPC Packet Mirroring with Layer-7 Shadow Deployment (requestMirrorPolicy)",
        "pattern_regex": r"vpc packet mirroring.*(?:dark launch|shadow deployment|v2 microservice)|(?:dark launch|shadow deployment).*vpc packet mirroring",
        "remediation": "Use requestMirrorPolicy (Cloud Service Mesh / ALB URL Map) for L7 HTTP traffic shadowing (discards v2 response). Use VPC Packet Mirroring strictly for L2/L3 .pcap IDS network forensics.",
    },
    {
        "rule_id": "AP-PCA-07",
        "okf_concept": "OKF-PCA-05",
        "pillar": "security",
        "title": "Using a VPC-SC Perimeter Bridge to Grant Human Analysts Cloud Console Access",
        "pattern_regex": r"perimeter bridge.*(?:cloud console|human|analyst)|(?:cloud console|human|analyst).*perimeter bridge",
        "remediation": "Configure Access Context Manager (Access Levels by User Identity / Corporate IP) and add an Ingress Rule on the VPC-SC perimeter. Perimeter Bridges only link two GCP perimeters.",
    },
    {
        "rule_id": "AP-PCA-08",
        "okf_concept": "OKF-PCA-05",
        "pillar": "security",
        "title": "Binary Authorization Enabled Without Writing Attestation Metadata to Container Analysis API",
        "pattern_regex": r"artifact analysis.*blocks.*unsigned|vulnerability scanning.*blocks.*unsigned",
        "remediation": "Artifact Analysis only detects CVEs; Binary Authorization blocks unsigned images and requires the CI/CD pipeline to write the Attestation occurrence metadata into the Container Analysis API.",
    },
    {
        "rule_id": "AP-PCA-09",
        "okf_concept": "OKF-PCA-06",
        "pillar": "operational_excellence",
        "title": "Using Cloud Profiler for Cross-Service RPC Latency Hops Instead of Cloud Trace",
        "pattern_regex": r"cloud profiler.*(?:cross-service|multi-service|microservice.*latency|rpc latency)",
        "remediation": "Use Cloud Trace + propagate X-Cloud-Trace-Context (or W3C traceparent) headers for multi-service latency waterfalls; use Cloud Profiler for single-binary CPU/Heap flame graphs.",
    },
    {
        "rule_id": "AP-PCA-10",
        "okf_concept": "OKF-PCA-05",
        "pillar": "security",
        "title": "Assuming Cloud Storage Has a Built-In Native Malware/Antivirus Checkbox",
        "pattern_regex": r"(?:enable|turn on|built-in|native).*cloud storage.*(?:antivirus|malware|virus scan)",
        "remediation": "Implement the Two-Bucket Quarantine Pattern: upload to unscanned GCS bucket -> Eventarc / Cloud Run running containerized ClamAV -> move to clean or quarantine bucket.",
    },
    {
        "rule_id": "AP-PCA-11",
        "okf_concept": "OKF-PCA-01",
        "pillar": "cost_optimization",
        "title": "Exporting >90-Day Unmodified BigQuery Tables to GCS to Save Storage Cost",
        "pattern_regex": r"export.*bigquery.*(?:90 days|older than 90).*cloud storage.*(?:cost|save|cheaper)",
        "remediation": "Do nothing! Any BigQuery table or partition unmodified for 90 consecutive days automatically receives a 50% Long-Term Storage discount ($0.01/GB/month, same as GCS Nearline) with zero performance degradation.",
    },
    {
        "rule_id": "AP-PCA-12",
        "okf_concept": "OKF-PCA-05",
        "pillar": "security",
        "title": "Loading Raw PHI/PII Into BigQuery Before De-Identification When In-Flight Masking Is Mandated",
        "pattern_regex": r"load.*raw (?:phi|pii).*into bigquery first",
        "remediation": "Run a Cloud Dataflow pipeline invoking the Sensitive Data Protection (Cloud DLP) API to tokenize/mask PHI/PII in flight before writing to BigQuery.",
    },
    {
        "rule_id": "AP-PCA-13",
        "okf_concept": "OKF-PCA-03",
        "pillar": "networking",
        "title": "Using Cloud NAT or K8s NetworkPolicies for Inbound kubectl Access to a Private GKE Cluster",
        "pattern_regex": r"(?:cloud nat|networkpolic).*(?:inbound|kubectl).*private gke",
        "remediation": "If public endpoint is enabled, use Master Authorized Networks. If private endpoint only, use a Bastion Host + IAP TCP Forwarding (--tunnel-through-iap). Cloud NAT is outbound egress only.",
    },
    {
        "rule_id": "AP-PCA-14",
        "okf_concept": "OKF-PCA-03",
        "pillar": "performance_optimization",
        "title": "Creating Separate Per-Region VPCs Connected by VPNs for Multi-Region Internal Traffic",
        "pattern_regex": r"(?:three|3|separate|multiple) regional vpcs.*connected (?:by|via) vpn",
        "remediation": "Google Cloud VPCs are Global! Provision a single Global VPC with regional subnets in us-central1, europe-west1, and asia-east1.",
    },
    {
        "rule_id": "AP-PCA-15",
        "okf_concept": "OKF-PCA-04",
        "pillar": "security",
        "title": "Using uniformBucketLevelAccess Instead of publicAccessPrevention to Block Public Buckets",
        "pattern_regex": r"uniformbucketlevelaccess.*(?:prevent|block).*public|block.*allusers.*uniformbucketlevelaccess",
        "remediation": "Enforce constraints/storage.publicAccessPrevention to block allUsers/allAuthenticatedUsers. uniformBucketLevelAccess only disables per-object ACLs in favor of IAM.",
    },
    {
        "rule_id": "AP-PCA-16",
        "okf_concept": "OKF-PCA-01",
        "pillar": "reliability",
        "title": "Sending Read Queries (SELECT) to a Cloud SQL High Availability (HA) Standby Instance",
        "pattern_regex": r"(?:read queries|select queries|read traffic).*(?:ha standby|failover replica|standby instance)",
        "remediation": "The Cloud SQL HA Standby is strictly for synchronous zonal failover (RTO < 2m, RPO = 0) and cannot serve read traffic. Provision a separate Read Replica to offload read queries.",
    },
    {
        "rule_id": "AP-PCA-17",
        "okf_concept": "OKF-PCA-06",
        "pillar": "operational_excellence",
        "title": "Using Mean/Average Line Charts to Monitor p50/p95/p99 Tail Latency Distribution",
        "pattern_regex": r"(?:mean|average) latency.*(?:p95|p99|tail latency)|single line chart.*average latency.*percentile",
        "remediation": "Use a Heatmap chart showing latency distribution over time (or explicit p50/p95/p99 percentile series) in Cloud Monitoring.",
    },
    {
        "rule_id": "AP-PCA-18",
        "okf_concept": "OKF-PCA-02",
        "pillar": "cost_optimization",
        "title": "Expecting Spot VMs (Preemptible VMs) to Guarantee a Minimum Uninterrupted Runtime",
        "pattern_regex": r"spot vm.*guarantee.*(?:30|60) minute|preemptible.*minimum runtime guarantee",
        "remediation": "Spot VMs can be preempted at any time (even 1 minute after boot) with a 30-second ACPI shutdown notice. Only use them for fault-tolerant, stateless workloads.",
    },
    {
        "rule_id": "AP-ZAA-19",
        "okf_concept": "OKF-PCA-04",
        "pillar": "security",
        "title": "Hardcoded API Keys, Long-Lived Service Account JSON Keys, or Unauthenticated Public Endpoints",
        "pattern_regex": r"aizasy[a-za-z0-9_-]{10,}|allow_unauthenticated\s*=\s*true|service[ _-]?account.*json key",
        "remediation": "Enforce Zero Ambient Authority (ZAA): eliminate service account JSON keys (constraints/iam.disableServiceAccountKeyCreation), use Workload Identity / downscoped OAuth tokens, and require IAM / IAP authentication.",
    },
]


def _get_okf_bundle_dir() -> Path:
    """Resolve the active local directory for the PCA/WAF OKF bundle."""
    if (_DATA_PCA_WAF_DIR / "MANIFEST.json").exists():
        return _DATA_PCA_WAF_DIR
    if (_MCP_PCA_WAF_DIR / "MANIFEST.json").exists():
        return _MCP_PCA_WAF_DIR
    if (_SOURCE_PCA_WAF_DIR / "MANIFEST.json").exists():
        return _SOURCE_PCA_WAF_DIR
    return _DATA_PCA_WAF_DIR


def load_pca_waf_okf_corpus() -> dict[str, Any]:
    """Load all 9 OKF-PCA concepts, MANIFEST.json, and catalog metadata from disk."""
    bundle_dir = _get_okf_bundle_dir()
    manifest_file = bundle_dir / "MANIFEST.json"
    concepts_dir = bundle_dir / "concepts"

    manifest_data: dict[str, Any] = {}
    if manifest_file.exists():
        try:
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception:
            manifest_data = {}

    concepts_by_id: dict[str, dict[str, Any]] = {}
    for c_meta in manifest_data.get("concepts", []):
        cid = c_meta.get("id", "")
        slug = c_meta.get("slug", "")
        md_file = concepts_dir / f"{slug}.md"
        body = ""
        if md_file.exists():
            try:
                body = md_file.read_text(encoding="utf-8")
            except Exception:
                body = ""
        concepts_by_id[cid] = {
            **c_meta,
            "markdown_content": body,
            "local_file": str(md_file),
        }

    # Fallback scan if MANIFEST.json wasn't populated
    if not concepts_by_id and concepts_dir.exists():
        for idx, md_file in enumerate(sorted(concepts_dir.glob("*.md")), start=1):
            cid = f"OKF-PCA-0{idx}"
            body = md_file.read_text(encoding="utf-8")
            concepts_by_id[cid] = {
                "id": cid,
                "slug": md_file.stem,
                "title": md_file.stem.replace("-", " ").title(),
                "description": body[:300],
                "markdown_content": body,
                "local_file": str(md_file),
            }

    return {
        "bundle_dir": str(bundle_dir),
        "dataplex_metadata": DATAPLEX_KB_METADATA,
        "manifest": manifest_data,
        "concepts": concepts_by_id,
    }


def search_pca_waf_okf(
    query: str,
    pillar: str = "all",
    service_area: str = "all",
    include_antipatterns: bool = True,
) -> dict[str, Any]:
    """Search the PCA/WAF OKF Knowledge Base by keyword query, WAF pillar, or service area."""
    corpus = load_pca_waf_okf_corpus()
    concepts = corpus["concepts"]
    q_lower = query.lower().strip()
    pillar_norm = pillar.lower().strip().replace(" ", "_").replace("-", "_")

    # Alias normalization for pillar names
    pillar_aliases = {
        "ops": "operational_excellence",
        "operational": "operational_excellence",
        "sec": "security",
        "security_privacy_compliance": "security",
        "rel": "reliability",
        "cost": "cost_optimization",
        "finops": "cost_optimization",
        "perf": "performance_optimization",
        "performance": "performance_optimization",
        "performance_efficiency": "performance_optimization",
        "sust": "sustainability",
    }
    pillar_norm = pillar_aliases.get(pillar_norm, pillar_norm)

    target_concept_ids: set[str] | None = None
    if pillar_norm in WAF_PILLAR_DEFINITIONS:
        target_concept_ids = set(WAF_PILLAR_DEFINITIONS[pillar_norm]["okf_concepts"])

    matched_concepts: list[dict[str, Any]] = []
    q_terms = [t for t in re.split(r"\W+", q_lower) if len(t) >= 2]

    for cid, cdata in sorted(concepts.items()):
        if target_concept_ids and cid not in target_concept_ids:
            continue
        if service_area != "all" and service_area.lower() not in cdata.get("slug", "").lower():
            continue

        haystack = f"{cid} {cdata.get('title', '')} {cdata.get('description', '')} {cdata.get('markdown_content', '')}".lower()
        score = 0
        if q_lower and q_lower in haystack:
            score += 10
        for term in q_terms:
            if term in cdata.get("title", "").lower():
                score += 4
            elif term in cdata.get("description", "").lower():
                score += 2
            elif term in haystack:
                score += 1

        if score > 0 or not q_terms or target_concept_ids is not None:
            # Extract relevant section snippet
            md_text = cdata.get("markdown_content", "")
            # Strip frontmatter
            md_body = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n+", "", md_text, flags=re.S).strip()
            matched_concepts.append({
                "concept_id": cid,
                "slug": cdata.get("slug"),
                "title": cdata.get("title"),
                "description": cdata.get("description"),
                "gcs_uri": cdata.get("gcs_uri"),
                "dataplex_entry": f"{DATAPLEX_KB_METADATA['dataplex_entry_group']}/entries/{cdata.get('slug', '').replace('-', '_')}",
                "content_sha256": cdata.get("content_sha256"),
                "stale_after": cdata.get("stale_after"),
                "relevance_score": score,
                "excerpt_markdown": md_body[:2200],
            })

    matched_concepts.sort(key=lambda x: x["relevance_score"], reverse=True)

    matched_antipatterns = []
    if include_antipatterns:
        for ap in WAF_ANTIPATTERN_RULES:
            if pillar_norm != "all" and pillar_norm in WAF_PILLAR_DEFINITIONS and ap["pillar"] != pillar_norm:
                continue
            ap_text = f"{ap['title']} {ap['remediation']} {ap['okf_concept']}".lower()
            if not q_terms or any(t in ap_text for t in q_terms) or pillar_norm in WAF_PILLAR_DEFINITIONS:
                matched_antipatterns.append(ap)

    pillar_info = (
        WAF_PILLAR_DEFINITIONS.get(pillar_norm)
        if pillar_norm in WAF_PILLAR_DEFINITIONS
        else {k: {"display_name": v["display_name"], "okf_concepts": v["okf_concepts"], "core_principles": v["core_principles"]} for k, v in WAF_PILLAR_DEFINITIONS.items()}
    )

    return {
        "status": "success",
        "query": query,
        "pillar_filter": pillar_norm,
        "dataplex_kb": DATAPLEX_KB_METADATA,
        "pillar_guidance": pillar_info,
        "matched_concepts_count": len(matched_concepts),
        "matched_concepts": matched_concepts[:6],
        "matched_antipatterns": matched_antipatterns[:10],
    }


def evaluate_spec_against_pillar(
    architecture_spec: str,
    pillar_key: str,
) -> dict[str, Any]:
    """Deterministically evaluate a project design spec against a single WAF pillar using OKF rules."""
    pillar_norm = pillar_key.lower().strip().replace(" ", "_").replace("-", "_")
    pillar_aliases = {
        "ops": "operational_excellence",
        "operational": "operational_excellence",
        "sec": "security",
        "security_privacy_compliance": "security",
        "rel": "reliability",
        "cost": "cost_optimization",
        "finops": "cost_optimization",
        "perf": "performance_optimization",
        "performance": "performance_optimization",
        "performance_efficiency": "performance_optimization",
        "sust": "sustainability",
    }
    pillar_norm = pillar_aliases.get(pillar_norm, pillar_norm)
    if pillar_norm not in WAF_PILLAR_DEFINITIONS:
        pillar_norm = "security"

    pdef = WAF_PILLAR_DEFINITIONS[pillar_norm]
    spec_lower = architecture_spec.lower()

    # Check positive signals
    matched_signals = 0
    total_signals = len(pdef["positive_signals"])
    for pat in pdef["positive_signals"]:
        if re.search(pat, spec_lower):
            matched_signals += 1

    # Check anti-patterns for this pillar
    violations: list[dict[str, Any]] = []
    for ap in WAF_ANTIPATTERN_RULES:
        if ap["pillar"] == pillar_norm or (pillar_norm == "performance_optimization" and ap["pillar"] == "networking"):
            if re.search(ap["pattern_regex"], spec_lower):
                violations.append({
                    "rule_id": ap["rule_id"],
                    "okf_concept": ap["okf_concept"],
                    "antipattern_detected": ap["title"],
                    "deterministic_fix": ap["remediation"],
                })

    # Compute deterministic 0.0 - 3.0 score aligned with FDE >= 2.0 cutline
    signal_ratio = matched_signals / max(total_signals, 1)
    base_score = 1.6 + (1.4 * signal_ratio)
    if violations:
        # Critical security/architecture violations penalize score below 2.0 cutline
        penalty = min(1.8, 0.7 * len(violations))
        score = round(max(0.0, base_score - penalty), 2)
    else:
        score = round(min(3.0, max(2.0 if matched_signals >= 2 else 1.7, base_score)), 2)

    corpus = load_pca_waf_okf_corpus()
    cited_concepts = [
        {
            "concept_id": cid,
            "title": corpus["concepts"].get(cid, {}).get("title", cid),
            "gcs_uri": corpus["concepts"].get(cid, {}).get("gcs_uri", ""),
            "content_sha256": corpus["concepts"].get(cid, {}).get("content_sha256", ""),
        }
        for cid in pdef["okf_concepts"]
    ]

    return {
        "pillar_id": pillar_norm,
        "pillar_name": pdef["display_name"],
        "score": score,
        "max_score": 3.0,
        "cutline_passed": score >= 2.0 and len(violations) == 0,
        "matched_positive_signals": matched_signals,
        "total_positive_signals": total_signals,
        "violations_detected": violations,
        "core_principles_checked": pdef["core_principles"],
        "recommended_gcp_enablers": pdef["primary_gcp_enablers"],
        "okf_concepts_referenced": cited_concepts,
    }


def evaluate_spec_across_all_pillars(
    architecture_spec: str,
    target_pillars: list[str] | None = None,
) -> dict[str, Any]:
    """Deterministically verify a project design specification across all WAF pillars simultaneously."""
    pillars_to_run = target_pillars or list(WAF_PILLAR_DEFINITIONS.keys())
    if "all" in [p.lower() for p in pillars_to_run]:
        pillars_to_run = list(WAF_PILLAR_DEFINITIONS.keys())

    pillar_results: dict[str, dict[str, Any]] = {}
    all_violations: list[dict[str, Any]] = []

    for p in pillars_to_run:
        res = evaluate_spec_against_pillar(architecture_spec, p)
        pillar_results[res["pillar_id"]] = res
        all_violations.extend(res["violations_detected"])

    # Also scan any remaining anti-patterns across the entire 18-rule registry
    seen_rules = {v["rule_id"] for v in all_violations}
    spec_lower = architecture_spec.lower()
    for ap in WAF_ANTIPATTERN_RULES:
        if ap["rule_id"] not in seen_rules and re.search(ap["pattern_regex"], spec_lower):
            all_violations.append({
                "rule_id": ap["rule_id"],
                "okf_concept": ap["okf_concept"],
                "pillar": ap["pillar"],
                "antipattern_detected": ap["title"],
                "deterministic_fix": ap["remediation"],
            })

    scores = [r["score"] for r in pillar_results.values()]
    composite_score = round(sum(scores) / max(len(scores), 1), 2)
    all_passed = all(r["cutline_passed"] for r in pillar_results.values()) and len(all_violations) == 0

    verdict = "WELL_ARCHITECTED_FOUNDATION_APPROVED" if all_passed and composite_score >= 2.0 else "REMEDIATION_REQUIRED_BEFORE_SIGN_OFF"

    # Build Markdown Scorecard
    md_lines = [
        "# 🏛️ Google Cloud Well-Architected & PCA OKF v0.2 Compliance Scorecard",
        f"- **Verdict**: `{verdict}`",
        f"- **Composite WAF Score**: `{composite_score} / 3.00` (Cutline: `>= 2.00`)",
        f"- **Dataplex Knowledge Base**: `{DATAPLEX_KB_METADATA['dataplex_entry_group']}` (`{DATAPLEX_KB_METADATA['version_tag']}`)",
        f"- **GCS Backing Store**: `{DATAPLEX_KB_METADATA['gcs_versioned_prefix']}`",
        "",
        "## 1. Per-Pillar Verification Matrix",
        "| WAF Pillar | Score (0–3.0) | Cutline (`>=2.0`) | OKF Concepts Applied | Anti-Patterns Flagged |",
        "| :--- | :---: | :---: | :--- | :---: |",
    ]
    for r in pillar_results.values():
        status_icon = "✅ PASS" if r["cutline_passed"] else "❌ FAIL"
        cids = ", ".join(f"`{c['concept_id']}`" for c in r["okf_concepts_referenced"])
        v_count = len(r["violations_detected"])
        md_lines.append(f"| **{r['pillar_name']}** | `{r['score']}` | {status_icon} | {cids} | `{v_count}` |")

    if all_violations:
        md_lines.extend([
            "",
            "## 2. 🚨 Deterministic Architectural Anti-Patterns Detected (`OKF-PCA-09`)",
            "| Rule ID | OKF Concept | Anti-Pattern Detected | Deterministic Well-Architected Fix |",
            "| :--- | :--- | :--- | :--- |",
        ])
        for v in all_violations:
            md_lines.append(
                f"| `{v['rule_id']}` | `{v['okf_concept']}` | {v['antipattern_detected']} | {v['deterministic_fix']} |"
            )
    else:
        md_lines.extend([
            "",
            "## 2. ✅ Anti-Pattern Verification (`OKF-PCA-09`)",
            "Zero high-frequency PCA/WAF architectural anti-patterns detected across all 18 forensic diagnostic rules.",
        ])

    return {
        "status": "success",
        "verdict": verdict,
        "composite_waf_score": composite_score,
        "production_cutline_met": all_passed and composite_score >= 2.0,
        "dataplex_kb": DATAPLEX_KB_METADATA,
        "pillar_evaluations": pillar_results,
        "antipattern_violations": all_violations,
        "scorecard_markdown": "\n".join(md_lines),
    }


class WAFOKFSearchSkill(SkillPlugin):
    """Skill to search and retrieve best practices from the Dataplex PCA & WAF OKF Knowledge Base."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_waf_okf_search",
            name="PCA & Well-Architected OKF Knowledge Base Search",
            version="1.0.0",
            category="architecture",
            description="Searches the Google Cloud Dataplex PCA & Well-Architected OKF v0.2 Knowledge Base (OKF-PCA-01..09) by pillar, service area, or keyword.",
            capabilities=["okf_search", "dataplex_kb_lookup", "decision_matrix_retrieval", "antipattern_lookup"],
            entrypoint="execute",
            context_token_estimate=280,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(name="query", type="string", description="Architectural topic, service, or design question (e.g., 'Spanner vs Cloud SQL', 'VPC-SC', 'GKE Autopilot', 'DR RTO/RPO')"),
                SkillParameter(name="pillar", type="string", description="Optional WAF pillar filter: 'operational_excellence', 'security', 'reliability', 'cost_optimization', 'performance_optimization', 'sustainability', or 'all'", required=False, default="all"),
                SkillParameter(name="service_area", type="string", description="Optional service area slug filter or 'all'", required=False, default="all"),
            ],
            instructions="Queries the 9-concept GEAPL200_PCA_WAF OKF bundle and returns decision matrices, enablers, and anti-patterns.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        query = parameters.get("query", "Well-Architected Framework")
        pillar = parameters.get("pillar", "all")
        service_area = parameters.get("service_area", "all")

        res = search_pca_waf_okf(query=query, pillar=pillar, service_area=service_area, include_antipatterns=True)
        elapsed = (time.perf_counter() - start_time) * 1000
        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=round(elapsed, 2),
            data=res,
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(query),
                "completion_tokens_estimated": self.estimate_tokens(json.dumps(res)),
                "tokens_saved_by_cache": 0,
            },
        )


class _BaseWAFPillarSkill(SkillPlugin):
    """Base plugin class for per-pillar Well-Architected search and spec verification."""

    pillar_key: str = "security"
    skill_id_str: str = "skill_waf_pillar_security"
    skill_title: str = "WAF Security Pillar Verifier"
    skill_desc: str = "Searches and verifies project design specs against the Google Cloud WAF Security Pillar."

    @property
    def manifest(self) -> SkillManifest:
        pdef = WAF_PILLAR_DEFINITIONS[self.pillar_key]
        return SkillManifest(
            id=self.skill_id_str,
            name=self.skill_title,
            version="1.0.0",
            category="governance",
            description=self.skill_desc,
            capabilities=[
                f"waf_{self.pillar_key}_audit",
                "pillar_best_practices_search",
                "spec_compliance_verification",
                "antipattern_detection",
            ],
            entrypoint="execute",
            context_token_estimate=300,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(
                    name="architecture_description",
                    type="string",
                    description=f"Project design specification or architecture description to verify against {pdef['display_name']}",
                ),
                SkillParameter(
                    name="search_query",
                    type="string",
                    description="Optional specific topic to search within this pillar's OKF knowledge base",
                    required=False,
                    default="",
                ),
            ],
            instructions=f"Searches {', '.join(pdef['okf_concepts'])} in the Dataplex OKF KB and verifies spec compliance with {pdef['display_name']}.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        arch = parameters.get("architecture_description") or parameters.get("input_payload") or ""
        search_q = parameters.get("search_query", "")

        eval_res = evaluate_spec_against_pillar(arch, self.pillar_key)
        kb_search = search_pca_waf_okf(query=search_q or self.pillar_key, pillar=self.pillar_key)

        pdef = WAF_PILLAR_DEFINITIONS[self.pillar_key]
        prompt = f"""You are a Google Cloud Principal Architect verifying a project design specification against the Well-Architected Pillar: {pdef['display_name']}.
Grounded in Dataplex OKF Concepts: {', '.join(pdef['okf_concepts'])} ({DATAPLEX_KB_METADATA['version_tag']}).

Core Pillar Principles:
{chr(10).join('- ' + p for p in pdef['core_principles'])}

Deterministic Pillar Score: {eval_res['score']} / 3.0 (Cutline >= 2.0: {'PASSED' if eval_res['cutline_passed'] else 'FAILED'})
Detected Anti-Patterns: {json.dumps(eval_res['violations_detected'])}

Project Design Specification:
{arch}

Provide a concise, authoritative verification report covering:
1. Pillar Verdict & Alignment with OKF Concepts ({', '.join(pdef['okf_concepts'])}).
2. Verified Strengths & Compliant Design Decisions.
3. Architectural Gaps / Anti-Pattern Violations & Concrete Remediation Diffs.
"""
        llm_synthesis = await model_router.generate_text(prompt=prompt, temperature=0.2)
        elapsed = (time.perf_counter() - start_time) * 1000

        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=round(elapsed, 2),
            data={
                "pillar_evaluation": eval_res,
                "okf_knowledge_base_matches": kb_search["matched_concepts"],
                "dataplex_kb": DATAPLEX_KB_METADATA,
                "verification_report_markdown": llm_synthesis,
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(prompt),
                "completion_tokens_estimated": self.estimate_tokens(llm_synthesis),
                "tokens_saved_by_cache": 0,
            },
        )


class WAFOperationalExcellencePillarSkill(_BaseWAFPillarSkill):
    """Skill for Operational Excellence Pillar verification (OKF-PCA-06, OKF-PCA-07, OKF-PCA-09)."""

    pillar_key = "operational_excellence"
    skill_id_str = "skill_waf_pillar_operational_excellence"
    skill_title = "WAF Operational Excellence Pillar Verifier"
    skill_desc = "Searches and verifies project design specs against the Operational Excellence pillar (Observability, Trace, Profiler, SRE SLIs/SLOs/Error Budgets, CI/CD, Cloud Deploy, Terraform IaC, GitOps)."


class WAFSecurityPillarSkill(_BaseWAFPillarSkill):
    """Skill for Security, Privacy & Compliance Pillar verification (OKF-PCA-04, OKF-PCA-05, OKF-PCA-09)."""

    pillar_key = "security"
    skill_id_str = "skill_waf_pillar_security"
    skill_title = "WAF Security, Privacy & Compliance Pillar Verifier"
    skill_desc = "Searches and verifies project design specs against the Security pillar (ZAA, Workload Identity, Org Policies, IAM Deny, Secret Manager, KMS/EKM/CSEK/Tink, Confidential VMs/GKE, VPC-SC, Cloud Armor, IAP, Binary Authorization, DLP)."


class WAFReliabilityPillarSkill(_BaseWAFPillarSkill):
    """Skill for Reliability Pillar verification (OKF-PCA-01, OKF-PCA-03, OKF-PCA-06, OKF-PCA-08, OKF-PCA-09)."""

    pillar_key = "reliability"
    skill_id_str = "skill_waf_pillar_reliability"
    skill_title = "WAF Reliability & DR Pillar Verifier"
    skill_desc = "Searches and verifies project design specs against the Reliability pillar (Spanner 99.999%, Cloud SQL HA vs Read Replicas, Multi-Zone/Multi-Region GKE & Cloud Run, 2+2 Interconnect/HA VPN, Cold/Warm/Hot DR RTO/RPO)."


class WAFCostOptimizationPillarSkill(_BaseWAFPillarSkill):
    """Skill for Cost Optimization (FinOps) Pillar verification (OKF-PCA-01, OKF-PCA-02, OKF-PCA-04, OKF-PCA-06, OKF-PCA-09)."""

    pillar_key = "cost_optimization"
    skill_id_str = "skill_waf_pillar_cost_optimization"
    skill_title = "WAF Cost Optimization (FinOps) Pillar Verifier"
    skill_desc = "Searches and verifies project design specs against the Cost Optimization / FinOps pillar (GKE Autopilot, Cloud Run scale-to-zero, Spot VMs, CUDs, BQ 90-day long-term storage & Analytics Hub, GCS Autoclass, Log Exclusion Filters, Billing Budgets)."


class WAFPerformanceOptimizationPillarSkill(_BaseWAFPillarSkill):
    """Skill for Performance Optimization Pillar verification (OKF-PCA-01, OKF-PCA-02, OKF-PCA-03, OKF-PCA-09)."""

    pillar_key = "performance_optimization"
    skill_id_str = "skill_waf_pillar_performance_optimization"
    skill_title = "WAF Performance Optimization Pillar Verifier"
    skill_desc = "Searches and verifies project design specs against the Performance Optimization pillar (Premium Tier Anycast, Cloud CDN, Spanner Interleaved Tables & Stale Reads, Bigtable Row Keys, BQ Partitioning/Clustering/BI Engine, Memorystore Redis, Vertex AI GPU/Context Caching)."


class WAFSustainabilityPillarSkill(_BaseWAFPillarSkill):
    """Skill for Sustainability Pillar verification (OKF-PCA-01, OKF-PCA-02, OKF-PCA-04, OKF-PCA-09)."""

    pillar_key = "sustainability"
    skill_id_str = "skill_waf_pillar_sustainability"
    skill_title = "WAF Sustainability & Carbon Efficiency Pillar Verifier"
    skill_desc = "Searches and verifies project design specs against the Sustainability pillar (CFE% Low-Carbon Region Selection, Scale-to-Zero Serverless, GKE Autopilot Bin-Packing, Idle VM Recommender, Storage Lifecycle Compaction)."


class WAFAllPillarsSpecVerifierSkill(SkillPlugin):
    """Master skill to search and verify any project design spec across ALL Well-Architected Pillars simultaneously."""

    @property
    def manifest(self) -> SkillManifest:
        return SkillManifest(
            id="skill_waf_all_pillars_spec_verifier",
            name="Well-Architected All-Pillars Design Spec Verifier (PCA & WAF OKF)",
            version="1.0.0",
            category="governance",
            description="Searches and verifies any project design specification across all 6 Google Cloud Well-Architected Framework pillars simultaneously using the Dataplex PCA & WAF OKF v0.2 Knowledge Base (OKF-PCA-01..09) and 18 deterministic anti-pattern rules.",
            capabilities=[
                "all_pillars_verification",
                "per_pillar_scoring",
                "antipattern_registry_scan",
                "dataplex_okf_grounding",
                "spec_remediation_diff",
            ],
            entrypoint="execute",
            context_token_estimate=380,
            sandbox_tier="read_only",
            parameters=[
                SkillParameter(
                    name="architecture_description",
                    type="string",
                    description="Complete project design specification or architecture markdown to verify against all Well-Architected foundations",
                ),
                SkillParameter(
                    name="workload_type",
                    type="string",
                    description="Workload archetype (e.g., 'multi_agent_system', 'global_oltp_saas', 'streaming_iot_analytics', 'healthcare_hipaa', 'live_media_streaming')",
                    required=False,
                    default="enterprise_cloud_system",
                ),
                SkillParameter(
                    name="target_pillars",
                    type="list",
                    description="Optional subset of pillars to verify (defaults to all 6 pillars: operational_excellence, security, reliability, cost_optimization, performance_optimization, sustainability)",
                    required=False,
                    default=["all"],
                ),
            ],
            instructions="Executes simultaneous multi-pillar verification against OKF-PCA-01..09, flags any of the 18 forensic anti-patterns, and produces a complete Well-Architected compliance scorecard.",
        )

    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        start_time = time.perf_counter()
        arch = parameters.get("architecture_description") or parameters.get("input_payload") or ""
        workload = parameters.get("workload_type", "enterprise_cloud_system")
        target_pillars = parameters.get("target_pillars", ["all"])

        all_eval = evaluate_spec_across_all_pillars(arch, target_pillars=target_pillars)

        prompt = f"""You are the Google Cloud Well-Architected Review Board & PCA OKF Certification Engine.
Verify the following project design specification across ALL Google Cloud Well-Architected Framework Pillars simultaneously.
Grounded in Dataplex OKF v0.2 Corpus: {DATAPLEX_KB_METADATA['corpus']} ({DATAPLEX_KB_METADATA['version_tag']}).

Workload Type: {workload}
Deterministic Verdict: {all_eval['verdict']}
Composite WAF Score: {all_eval['composite_waf_score']} / 3.00
Detected Anti-Patterns: {json.dumps(all_eval['antipattern_violations'])}

Project Design Specification:
{arch}

Provide an executive Well-Architected Verification Report including:
1. Executive Compliance Summary & Pillar-by-Pillar Findings (Operational Excellence, Security, Reliability, Cost Optimization, Performance Optimization, Sustainability).
2. Deterministic Anti-Pattern Remediation Plan (citing OKF-PCA-01 through OKF-PCA-09).
3. Concrete Specification Diffs / ADRs Required for Production Sign-Off.
"""
        llm_report = await model_router.generate_text(prompt=prompt, temperature=0.2)
        elapsed = (time.perf_counter() - start_time) * 1000

        return SkillResult(
            status="success",
            skill_id=self.manifest.id,
            latency_ms=round(elapsed, 2),
            data={
                "workload_type": workload,
                **all_eval,
                "llm_verification_report_markdown": llm_report,
            },
            token_metrics={
                "prompt_tokens_estimated": self.estimate_tokens(prompt),
                "completion_tokens_estimated": self.estimate_tokens(llm_report),
                "tokens_saved_by_cache": 0,
            },
        )

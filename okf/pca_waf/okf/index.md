---
type: index
id: OKF-PCA-INDEX
title: "Google Cloud PCA & Well-Architected Framework (WAF) Open Knowledge Format (OKF v0.2) Knowledge Base Index"
description: "Root index for the Gemini Enterprise Dataplex OKF v0.2 Knowledge Base covering all 8 Google Cloud PCA Service Areas, the 5 Well-Architected Framework Pillars, 4 Official Case Studies, and 350+ verified diagnostic patterns."
timestamp: "2026-11-24T17:30:00-08:00"
generated_at: "2026-11-24T17:30:00-08:00"
status: active
ttl: "P6M"
ttl_days: 180
stale_after: "2027-05-24T17:30:00-08:00"
corpus: "GEAPL200_PCA_WAF"
version_tag: "PCA_WAF_OKF_2026-11-24_173000"
l400_version: "L400_version_20261124_1730"
generated_by: "Gemini Enterprise (PCA & Well-Architected OKF Synthesis Engine)"
verified: true
---

# Google Cloud PCA & Well-Architected Framework (`OKF v0.2`) Knowledge Base Index

## 1. Bundle Metadata & Dataplex ("Data Flex") Governance

* **Corpus ID:** `GEAPL200_PCA_WAF`
* **Version Tag:** `PCA_WAF_OKF_2026-11-24_173000` (`L400_version_20261124_1730`)
* **Timestamp:** `2026-11-24T17:30:00-08:00`
* **TTL Policy:** `6 Months` (`180 days` / ISO-8601 `P6M`) $\rightarrow$ **`stale_after: 2027-05-24T17:30:00-08:00`**
* **Dataplex Universal Catalog Target:**
  * **Project ID:** `fivedaysai-prd-sandbox-317383`
  * **Entry Group:** `projects/fivedaysai-prd-sandbox-317383/locations/us/entryGroups/geapl200-architecture-kb`
  * **Custom Aspect Type:** `projects/fivedaysai-prd-sandbox-317383/locations/us/aspectTypes/okf` (`fivedaysai-prd-sandbox-317383.us.okf`)
  * **Downstream Graph Stores:** Cloud Spanner Graph (`geapl200-okf-graph` — primary low-latency cache) + BigQuery Graph (`geapl200_okf_kg` — secondary analytical knowledge graph)

---

## 2. Authoritative Source Bibliography

1. **`PCA_Book.pdf`** — **Dan Sullivan**, *Official Google Cloud Certified Professional Cloud Architect Study Guide*, Sybex / John Wiley & Sons, Inc., ISBN: `978-1-119-60244-6` (`/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/PCA_Book.pdf`).
2. **`UDEMY-Course-PCA.pdf`** — **GCP PCA Curriculum Architecture Team**, *Google Cloud Professional Cloud Architect (PCA): Complete Certification Course & Architectural Reference Deck (242 Slides, Sections 1–12)* (`/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/UDEMY-Course-PCA.pdf`).
3. **`ExamTopics.pdf` & `GCP PCA Mock Tests 1–4`** — **Pradeep Mohan & GCP PCA Test Bank**, *Forensic Diagnostic Corpus: PCA Mock Exams 1–4 (Nov 2, 3, 6, 9, 2026), Security Practice Set 1, and Service Area Simulators 1–8* (`/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/ExamTopics.pdf`, `PCA_Exam_Printable_Cheat_Sheet.md`).
4. **Google Cloud Well-Architected Framework (Architecture Framework)** — **Google Cloud Architecture Center**, *Operational Excellence, Security/Privacy/Compliance, Reliability, Cost Optimization (FinOps), and Performance Optimization Pillars* (`https://cloud.google.com/architecture/framework`).

---

## 3. OKF Concept Catalog (`okf/concepts/01` – `09`)

| Concept ID | Concept File (`okf/concepts/`) | Dataplex Catalog Entry (`okf/catalog-entries/`) | Well-Architected Pillars Covered | `content_sha256` |
| :--- | :--- | :--- | :--- | :--- |
| **`OKF-PCA-01`** | [`01-storage-databases-bigquery-and-data-pipelines.md`](concepts/01-storage-databases-bigquery-and-data-pipelines.md) | `01-storage-databases-bigquery-and-data-pipelines.json` | Performance Optimization, Reliability, Cost Optimization | `4812308516c042b2...` |
| **`OKF-PCA-02`** | [`02-compute-engine-gke-serverless-and-vertex-ai.md`](concepts/02-compute-engine-gke-serverless-and-vertex-ai.md) | `02-compute-engine-gke-serverless-and-vertex-ai.json` | Performance Optimization, Security, Cost Optimization | `d7a7fe9dbdd1629a...` |
| **`OKF-PCA-03`** | [`03-vpc-networking-load-balancing-hybrid-and-dns.md`](concepts/03-vpc-networking-load-balancing-hybrid-and-dns.md) | `03-vpc-networking-load-balancing-hybrid-and-dns.json` | Performance Optimization, Security, Reliability | `38a0bed10565e2f8...` |
| **`OKF-PCA-04`** | [`04-identity-hierarchy-org-policies-iam-and-finops-billing.md`](concepts/04-identity-hierarchy-org-policies-iam-and-finops-billing.md) | `04-identity-hierarchy-org-policies-iam-and-finops-billing.json` | Security/Governance, Cost Optimization (`FinOps`) | `b1084c2f54a64a66...` |
| **`OKF-PCA-05`** | [`05-security-kms-secret-manager-vpc-sc-and-compliance.md`](concepts/05-security-kms-secret-manager-vpc-sc-and-compliance.md) | `05-security-kms-secret-manager-vpc-sc-and-compliance.json` | Security, Privacy & Compliance | `830c4c267760b6ce...` |
| **`OKF-PCA-06`** | [`06-cloud-operations-observability-trace-profiler-and-sre.md`](concepts/06-cloud-operations-observability-trace-profiler-and-sre.md) | `06-cloud-operations-observability-trace-profiler-and-sre.json` | Operational Excellence, Reliability (`SRE`) | `629d76d3ade8b03f...` |
| **`OKF-PCA-07`** | [`07-devops-cicd-cloud-deploy-terraform-iac-and-api-management.md`](concepts/07-devops-cicd-cloud-deploy-terraform-iac-and-api-management.md) | `07-devops-cicd-cloud-deploy-terraform-iac-and-api-management.json` | Operational Excellence, Security Supply Chain | `8d17ea948c6d262e...` |
| **`OKF-PCA-08`** | [`08-migration-6rs-dr-rto-rpo-and-enterprise-case-studies.md`](concepts/08-migration-6rs-dr-rto-rpo-and-enterprise-case-studies.md) | `08-migration-6rs-dr-rto-rpo-and-enterprise-case-studies.json` | Reliability (`DR`), Migration (`6 Rs`), 4 Case Studies | `8479db6b4c2733cc...` |
| **`OKF-PCA-09`** | [`09-well-architected-5-second-decision-matrices-and-anti-patterns.md`](concepts/09-well-architected-5-second-decision-matrices-and-anti-patterns.md) | `09-well-architected-5-second-decision-matrices-and-anti-patterns.json` | All 5 Pillars — Master Decision Engine & 18 Anti-Patterns | `edb493840e5b6d29...` |

---
type: concept
id: OKF-PCA-08
title: "Cloud Migration (6 Rs), Disaster Recovery Tiers (RTO/RPO) & The 4 Official PCA Case Studies (WAF Reliability)"
description: "L400 architectural decision framework for the 4-Phase Migration Journey, Migration Tooling (M2VM, M2C, GCVE, DMS, STS, Transfer Appliance), DR Tiers (Cold, Warm, Hot), and the 4 Official PCA Case Studies (EHR, HRL, Mountkirk, TerramEarth)."
timestamp: "2026-11-24T18:20:00-08:00"
generated_at: "2026-11-24T18:20:00-08:00"
status: "stable"
ttl: "P6M"
ttl_days: 180
stale_after: "2027-05-24T18:20:00-08:00"
corpus: "GEAP_WAF_PILLARS"
version_tag: "WAF_OKF_2026-11-24_182000"
l400_version: "L400_version_20261124_1820"
generated_by: "Gemini Enterprise (PCA & Well-Architected OKF Synthesis Engine)"
generated_method: "okf-v0.2-dataplex-synthesis"
verified: true
source_doc_id: "PCA_Book.pdf | UDEMY-Course-PCA.pdf | ExamTopics.pdf | GCP_PCA_Mock_Tests_1_to_4.pdf"
sources:
  - filename: "PCA_Book.pdf"
    title: "Official Google Cloud Certified Professional Cloud Architect Study Guide"
    authors: ["Dan Sullivan"]
    affiliation: "Sybex / John Wiley & Sons, Inc."
    venue: "Wiley Certification Guide (Chapters 1, 2, 10, 14 — Designing for Business & Technical Requirements, Migration, DR & Case Studies)"
    isbn: "978-1-119-60244-6"
    url: "https://cloud.google.com/certification/cloud-architect"
  - filename: "UDEMY-Course-PCA.pdf"
    title: "Google Cloud Professional Cloud Architect (PCA): Complete Certification Course & Architectural Reference Deck"
    authors: ["GCP PCA Curriculum Architecture Team"]
    affiliation: "Udemy / Google Cloud Partner Training"
    venue: "Section 12 (Case Studies: EHR Healthcare, Helicopter Racing League, Mountkirk Games & TerramEarth)"
    url: "https://cloud.google.com/architecture/framework/reliability"
  - filename: "GCP PCA Mock Tests 1–4 & Area 8 Simulator Corpus"
    title: "Forensic Diagnostic Corpus: PCA Mock Exams 1–4 (Nov 2, 3, 6, 9, 2026) & Service Area 8 Simulator"
    authors: ["Pradeep Mohan", "GCP PCA Test Bank"]
    affiliation: "Google Cloud Forward Deployed Engineering (FDE)"
    venue: "/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/"
content_sha256: "8479db6b4c2733cce2d8221d96051d7c3118fd784d9e0d028028d561d3597363"
expires_at: "2027-05-24T18:20:00-08:00"
version_date: "2026-11-24"
---

# OKF-PCA-08: Cloud Migration (6 Rs), Disaster Recovery Tiers (`RTO/RPO`) & The 4 Official Case Studies

## 1. The 4-Phase Migration Framework (`Assess -> Plan -> Deploy -> Optimize`) & Migration Tooling Matrix

| Migration Workload / Scenario | Recommended Strategy (`6 Rs`) | Winning Google Cloud Migration Service |
| :--- | :--- | :--- |
| **1. Discovery, Dependency Mapping, TCO & First-Mover Selection** | **Phase 1: Assess** | ✅ **Google Cloud Migration Center** (inventory + TCO + `mFit` container readiness). Always select a **low-risk, non-critical, loosely coupled app** as your first pilot! |
| **2. Standard On-Premises VMware / AWS / Azure VMs $\rightarrow$ Compute Engine VMs** *(Mock 4 Q52)* | **Rehost (`Lift & Shift`)** | ✅ **Migrate to Virtual Machines (`M2VM`)** with VMware/cloud source (agentless background disk replication + fast cutover). *(Never pick `"GCVE only"` for standard VMs!)* |
| **3. Legacy VMware Apps Needing Layer-2 (`L2`) Broadcast, Gratuitous ARP Failover & vCenter/NSX-T** *(Mock 3 Q7)* | **Rehost (`Lift & Shift VMware`)** | ✅ **Google Cloud VMware Engine (`GCVE`)** migrated via **VMware HCX**. |
| **4. Extract Legacy Linux/Windows VM Apps Directly Into GKE / Cloud Run Containers** | **Replatform (`Lift & Optimize`)** | ✅ **Migrate to Containers (`M2C`)**. |
| **5. Homogeneous Production Database Migration (`MySQL`, `PostgreSQL`, `SQL Server`, `Oracle->AlloyDB`) with `<5 Min` Downtime** *(Mock 4 Q4)* | **Replatform (`Managed DB`)** | ✅ **Database Migration Service (`DMS`)** (serverless continuous **Change Data Capture `CDC`** replication). |
| **6. Heterogeneous Database Streaming (`Oracle / MySQL -> BigQuery or GCS`)** | **Replatform / Refactor** | ✅ **Datastream** (serverless CDC) + **Dataflow**. |
| **7. Cloud-to-Cloud (`AWS S3 -> GCS Archive`) or Fast Network Data Transfer** *(Mock 4 Q48)* | **Data Migration (Online)** | ✅ **Storage Transfer Service (`STS`)** (serverless, automatic checksums, retries, delta sync). |
| **8. Massive Data (`600 TB`) over Saturated/Slow Link (`100 Mbps`) with Tight Deadline (`14 Days`)** *(Area 1 Q7)* | **Data Migration (Offline)** | ✅ **Google Cloud Transfer Appliance** (`40 TB` / `300 TB` physical encrypted rackable appliance). |
| **9. Gradual Decomposition of a Monolith into Cloud Run / GKE Microservices** | **Refactor (`Cloud-Native`)** | ✅ **Strangler Fig Pattern** behind **Apigee** or a **Global External Application Load Balancer (`URL Maps`)** peeling off routes one by one. |

---

## 2. Disaster Recovery (`DR`) Architecture Matrix: Matching `RTO` & `RPO` to `Cold`, `Warm` & `Hot` Tiers

```mermaid
flowchart LR
    subgraph Cold["1. COLD DR (Backup & Restore)\n• RTO = Hours (2–24h)\n• RPO = Hours (1–24h)\n• Cost: $ (Lowest)"]
        C1["• Zero VMs/DBs running in DR region!\n• Nightly DB backups & PD snapshots\n  stored in Multi-Region GCS\n• Provision DR region on demand via\n  Terraform + Cloud Build"]
    end

    subgraph Warm["2. WARM STANDBY (Active-Passive)\n• RTO = Minutes (2–15m)\n• RPO = Seconds/Minutes\n• Cost: $$ (Moderate)"]
        W1["• DB: Cloud SQL / AlloyDB\n  Cross-Region Read Replica\n• Compute: Minimal MIG (`min=1`)\n  or Cloud Run in DR region\n• Failover: Promote Read Replica +\n  autoscale MIG behind Global ALB"]
    end

    subgraph Hot["3. HOT (Multi-Region Active-Active)\n• RTO = ~0 Seconds (Zero Downtime)\n• RPO = 0 Bytes (Zero Data Loss)\n• Cost: $$$$ (Highest)"]
        H1["• DB: Cloud Spanner Multi-Region\n  (`99.999%` SLA, sync Paxos)\n• Compute: Active GKE / Cloud Run\n  in 2+ regions simultaneously\n• Front Door: Global External ALB\n  + Premium Network Tier"]
    end

    Cold --> Warm --> Hot

    style Cold fill:#eff6ff,stroke:#1d4ed8,stroke-width:2px
    style Warm fill:#fef3c7,stroke:#b45309,stroke-width:2px
    style Hot fill:#dcfce7,stroke:#15803d,stroke-width:2px
```

---

## 3. Master Blueprint for All 4 Official Google Cloud PCA Case Studies

| Official Case Study | Business Context & Core Bottlenecks | Canonical Target Google Cloud Architecture (Trigger $\rightarrow$ Service) |
| :--- | :--- | :--- |
| **1. EHR Healthcare** *(Electronic Health Records SaaS)* | Expiring colocation leases; legacy MySQL/Postgres/SQL Server/MongoDB/Redis; hospital on-prem connectivity; strict HIPAA compliance; clinical `HL7v2 / FHIR / DICOM` interoperability. | • **Clinical Ingestion & De-identification:** `Cloud Healthcare API (HL7v2/FHIR/DICOM)` + `Sensitive Data Protection (Cloud DLP)` $\rightarrow$ `BigQuery` (+ `BigQuery ML` readmission predictions).<br>• **Hybrid Connectivity:** `Dedicated Interconnect` + `HA VPN` backup + `Cloud DNS Forwarding/Inbound`.<br>• **Identity:** `Cloud Identity + GCDS + SAML SSO` (or `Managed Microsoft AD + NetApp Volumes` for Windows Kerberos/GPO/SMB).<br>• **Compute & Compliance:** `GKE Multi-Cluster + Multi-Cluster Ingress + Config Sync`; `GCS Archive + Locked Bucket Lock` (10-yr WORM) + `Access Transparency`. |
| **2. Helicopter Racing League (`HRL`)** *(Global Live Sports Streaming)* | Global 4K/8K live & recorded video streaming; remote race-truck edge ingestion; real-time helicopter sensor telemetry; live AI predictions (`overtake probability`, `crowd sentiment`). | • **Global Video Delivery:** `Premium Network Tier` + `Global External ALB` + `Cloud CDN / Media CDN` (with `Signed URLs / Signed Cookies`) + `GCS Object Lifecycle / Autoclass` (`-> Coldline/Archive` after 90d).<br>• **Video Transcoding:** `GCS` $\rightarrow$ `Eventarc` $\rightarrow$ `Cloud Workflows / Cloud Run Jobs` (`Transcoder API / Live Stream API`).<br>• **Real-Time Telemetry & AI:** `Cloud Pub/Sub` $\rightarrow$ `Cloud Dataflow (Streaming invoking Vertex AI Endpoints)` $\rightarrow$ `Cloud Bigtable` (sub-10ms live broadcast HUD) & `BigQuery`.<br>• **Sponsor/Partner APIs:** `Apigee API Management` (Monetization & Developer Portal). |
| **3. Mountkirk Games** *(Global Multiplayer Mobile Gaming)* | Session-based multiplayer game scaling 1K $\rightarrow$ 10M players; mobile telemetry packets arriving hours late/out-of-order; global transactional player state & leaderboards. | • **Global Game Servers:** `Multi-Region GKE` (with `Agones`) + `HPA / Cluster Autoscaler` behind `Global External Proxy NLB / ALB` on `Premium Network Tier`.<br>• **Global Player Profiles & Leaderboards:** `Cloud Spanner Multi-Region` (+ `Stale Reads` & extra Nodes for 10x tournament read spikes — *Mock 4 Q56*); `Cloud Bigtable` (or `Memorystore Redis HA`) for high-velocity session-to-IP state (*Mock 1 Q39*).<br>• **Late/Out-of-Order Mobile Logs:** `Cloud Pub/Sub` $\rightarrow$ `Cloud Dataflow (Event-Time Windowing, Watermarks & Allowed Lateness)` $\rightarrow$ `BigQuery`. |
| **4. TerramEarth** *(20M Agricultural & Mining Vehicles IoT)* | **99% (`19.8M`) offline vehicles** uploading `.gzip` batches once/day at depots; **1% (`200K`) cellular vehicles** streaming live telemetry (`9 TB/day`) for predictive maintenance; 500 independent dealers. | • **99% Offline Depot Batch Path (Lowest Cost):** `Cloud Storage` $\rightarrow$ `BigQuery Batch Load` (100% FREE ingestion!).<br>• **1% Cellular Live Streaming Path:** `Cloud Pub/Sub` $\rightarrow$ `Cloud Dataflow (Streaming + Vertex AI)` $\rightarrow$ `Cloud Bigtable` & `BigQuery`.<br>• **Bigtable Row Key:** `Vehicle_VIN#ReverseTimestamp` (prevents timestamp hotspotting).<br>• **BigQuery & Dealer Isolation:** Partition by `telemetry_date`, Cluster by `dealer_id`, enforce `Row-Level Security / Authorized Views` (or `Analytics Hub`), and expose partner APIs via `Apigee` (+ `Cloud Endpoints ESPv2` for internal GKE gRPC). |

---

## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

This OKF concept module enforces the architectural standards defined in `00-fde-field-readiness-and-grading-rubric.md` and the official Google Cloud Forward Deployed Engineering (FDE) handbook (`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`), providing end-to-end enterprise reference architectures across healthcare, media, gaming, and industrial IoT.

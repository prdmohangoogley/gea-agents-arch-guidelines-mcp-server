---
type: concept
id: OKF-PCA-07
title: "DevOps, CI/CD, Cloud Deploy, Terraform IaC, GitOps & API Management (WAF Automation & Delivery)"
description: "L400 architectural decision framework for Cloud Build Private Pools, Artifact Registry, Google Cloud Deploy, Progressive Delivery (Rolling, Blue-Green, Canary, Shadow), Terraform IaC, Config Sync/Connector, and Apigee/API Gateway/Endpoints."
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
    venue: "Wiley Certification Guide (Chapters 9, 10, 13 — CI/CD Pipelines, Deployment Strategies, Terraform IaC & API Management)"
    isbn: "978-1-119-60244-6"
    url: "https://cloud.google.com/certification/cloud-architect"
  - filename: "UDEMY-Course-PCA.pdf"
    title: "Google Cloud Professional Cloud Architect (PCA): Complete Certification Course & Architectural Reference Deck"
    authors: ["GCP PCA Curriculum Architecture Team"]
    affiliation: "Udemy / Google Cloud Partner Training"
    venue: "Sections 7, 9 & 11 (Cloud Build, Cloud Deploy, Artifact Registry, Terraform, Apigee & API Gateway)"
    url: "https://cloud.google.com/architecture/framework/operational-excellence"
  - filename: "GCP PCA Mock Tests 1–4 & Area 7 Simulator Corpus"
    title: "Forensic Diagnostic Corpus: PCA Mock Exams 1–4 (Nov 2, 3, 6, 9, 2026) & Service Area 7 Simulator"
    authors: ["Pradeep Mohan", "GCP PCA Test Bank"]
    affiliation: "Google Cloud Forward Deployed Engineering (FDE)"
    venue: "/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/"
content_sha256: "8d17ea948c6d262e4e17589981779a810549499cae053a1dc8f3376e194cc714"
expires_at: "2027-05-24T18:20:00-08:00"
version_date: "2026-11-24"
---

# OKF-PCA-07: DevOps, CI/CD, Cloud Deploy, Terraform IaC, GitOps & API Management

## 1. Secure Software Supply Chain (`Cloud Build` $\rightarrow$ `Artifact Registry` $\rightarrow$ `Binary Authorization` $\rightarrow$ `Cloud Deploy`)

1. **Cloud Build Private Pools & Cost Optimization (*Mock 4 Q39*):**
   * **Reaching Private GKE / Private Cloud SQL / On-Premises RFC 1918 IPs:** Default Cloud Build workers run on the public internet; configure a **Cloud Build Private Pool** peered/connected via Private Service Connect to your Shared VPC!
   * **Right-Sizing Cloud Build Machine Types (*Mock 4 Q39*):** Cloud Build bills per build-minute by machine size. **Use smaller default machine types for simple linting/unit-test builds, and reserve large `n1-highcpu-32` / `e2-highcpu-32` machines strictly for intensive compilation builds** (plus enable Kaniko / Docker layer caching).
2. **Artifact Registry (`Standard` vs. `Remote` vs. `Virtual`):**
   * Replaces deprecated Container Registry (`gcr.io`).
   * **Standard Repositories:** Store Docker/OCI images, Helm charts, Java Maven `.jar`, Node `npm`, and Python `pip` wheels.
   * **Remote Repositories:** Act as an authenticated **caching proxy** for upstream public registries (`Docker Hub`, `Maven Central`, `PyPI`) to prevent rate limits and supply-chain tampering.
   * **Virtual Repositories:** Unify multiple Standard and Remote repositories behind a single endpoint URL.
3. **Google Cloud Deploy (`Managed Skaffold CD`):**
   * Managed Continuous Delivery service for promoting releases across `dev -> staging -> prod` on **GKE, Cloud Run, and GKE Enterprise**, with **manual approval gates**, **automated Canary phases**, and **1-click rollbacks**.

---

## 2. Progressive Delivery & Zero-Downtime Deployment Strategies (`Mock 4 Q1, Q13, Q44, Q59` & `Area 7 Q18`)

| Deployment Strategy | When to Use It | Exact Implementation on Google Cloud |
| :--- | :--- | :--- |
| **1. Rolling Update** *(Mock 4 Q1)* | Gradual in-place update without paying for 2x cluster capacity (`e.g., maintain >=75% availability`). | • **GKE:** `RollingUpdate` with **`maxUnavailable: 25%`**, `maxSurge: 25%`, and a mandatory **`readinessProbe`** (prevents `502 Bad Gateway` errors while containers initialize!).<br>• **Compute Engine MIG:** `maxUnavailable = 0`, `maxSurge >= 1` (spins up and health-checks new VMs before terminating old VMs). |
| **2. Blue-Green Deployment** *(Mock 4 Q44)* | Zero-downtime release requiring **instant 100% traffic switch** and **instant 0-second rollback** (willing to run 2x capacity during cutover). | • **GKE (*Mock 4 Q44*):** Deploy `v2` (`Green`) alongside `v1` (`Blue`) in the **same namespace**, verify health, then **switch the Kubernetes `Service` selector label** (`version: v2`).<br>• **Cloud Run:** Deploy revision with `--no-traffic` + **Revision Tag** (test URL), then shift `100%` traffic. |
| **3. Canary Deployment** *(Mock 4 Q59)* | Minimize blast radius by routing a **small percentage (`1% -> 10% -> 50%`) of live traffic** to `v2`, monitoring SLIs, and auto-rolling back on errors. | • **GKE / Cloud Run:** **Google Cloud Deploy** canary rollout, **Cloud Run revision traffic splitting** (`--to-revisions=v2=5,v1=95`), **Cloud Service Mesh (`VirtualService` weights)**, or **MIG Canary** (`2 versions`, `targetSize: {percent: 10}`). |
| **4. A/B Testing** *(Mock 4 Q13)* | Route a specific **user segment** (e.g., users in **France** or requests with `X-Beta-User: true` header) to an experimental feature. | • **Global External Application Load Balancer URL Maps with advanced traffic management** (**header-based routing + geo-routing** — *Mock 4 Q13*). *(Never use Cloud DNS for L7 header A/B tests!)* |
| **5. Shadow Deployment / Dark Launch (`Traffic Mirroring`)** *(Area 7 Q18 Trap!)* | Test `v2` under **100% real production HTTP load** by sending an **asynchronous copy of live requests to `v2` while discarding `v2`'s responses** (0% customer impact). | • Configure **`requestMirrorPolicy`** in **Google Cloud Service Mesh (Istio `VirtualService`)** or **Application Load Balancer URL Maps (`routeAction.requestMirrorPolicy`)**.<br>• 🚨 **Trap:** Never confuse L7 `requestMirrorPolicy` with **VPC Packet Mirroring** (which copies raw L2/L3 `.pcap` network packets to an ILB collector for IDS forensics)! |

---

## 3. Infrastructure as Code (`Terraform`), GKE GitOps Trio & API Management

```mermaid
flowchart LR
    subgraph IaC["1. Terraform IaC Best Practices"]
        T1["• Remote State in GCS (`backend \"gcs\"`)\n  -> Native `.tflock` State Locking!\n  -> Enable Object Versioning\n• Reusable Modules per `dev/stage/prod`\n• Import existing VMs: `bulk-export` +\n  `terraform import`\n• Pre-apply Org Policy check:\n  `gcloud beta terraform vet`"]
    end

    subgraph GitOps["2. GKE Enterprise GitOps Trio"]
        G1["• Config Sync (Mock 4 Q32):\n  Syncs Git repo -> GKE clusters\n• Config Connector (KCC):\n  Manages GCP resources (Cloud SQL,\n  GCS, Pub/Sub) via K8s YAML!\n• Policy Controller (Mock 3 Q24):\n  OPA Gatekeeper admission rules"]
    end

    subgraph API["3. API Gateway Selector & Pub/Sub Schemas"]
        A1["• Apigee: Enterprise Monetization,\n  Dev Portal, SOAP-to-REST XML/JSON\n• API Gateway: Serverless OpenAPI\n  front door for Cloud Run/Functions\n• Cloud Endpoints (ESPv2): Low-latency\n  gRPC sidecar proxy on GKE/GCE\n• Pub/Sub Schema (Mock 4 Q35):\n  Validates messages ON PUBLISH!"]
    end

    IaC --> GitOps --> API

    style IaC fill:#dcfce7,stroke:#15803d,stroke-width:2px
    style GitOps fill:#eff6ff,stroke:#1d4ed8,stroke-width:2px
    style API fill:#fef3c7,stroke:#b45309,stroke-width:2px
```

---

## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

This OKF concept module enforces the architectural standards defined in `00-fde-field-readiness-and-grading-rubric.md` and the official Google Cloud Forward Deployed Engineering (FDE) handbook (`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`), mandating reproducible Infrastructure as Code, keyless OIDC/Workload Identity Federation pipelines, and zero-downtime progressive delivery.

---
type: concept
id: OKF-PCA-02
title: "Compute Engine, GKE, Serverless & Vertex AI Architecture (WAF Compute, Security & AI)"
description: "L400 architectural decision framework for Compute Engine MIGs, Google Kubernetes Engine (Standard vs. Autopilot, Confidential/Shielded Nodes, Windows Pools, GPUs), Cloud Run, and Vertex AI."
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
    venue: "Wiley Certification Guide (Chapters 4, 8, 9 — Compute Engine, Kubernetes Engine, App Engine, Cloud Run & Functions)"
    isbn: "978-1-119-60244-6"
    url: "https://cloud.google.com/certification/cloud-architect"
  - filename: "UDEMY-Course-PCA.pdf"
    title: "Google Cloud Professional Cloud Architect (PCA): Complete Certification Course & Architectural Reference Deck"
    authors: ["GCP PCA Curriculum Architecture Team"]
    affiliation: "Udemy / Google Cloud Partner Training"
    venue: "Sections 3, 7 & 10 (Slides 50–125, 195–218 — GCE, MIGs, GKE, Cloud Run & Vertex AI)"
    url: "https://cloud.google.com/architecture/framework"
  - filename: "GCP PCA Mock Tests 1–4 & Area 2 Simulator Corpus"
    title: "Forensic Diagnostic Corpus: PCA Mock Exams 1–4 (Nov 2, 3, 6, 9, 2026) & Service Area 2 Simulator"
    authors: ["Pradeep Mohan", "GCP PCA Test Bank"]
    affiliation: "Google Cloud Forward Deployed Engineering (FDE)"
    venue: "/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/"
content_sha256: "d7a7fe9dbdd1629a0bb387d66e5596776873443d6586c03c782ded7bddb0c82b"
expires_at: "2027-05-24T18:20:00-08:00"
version_date: "2026-11-24"
---

# OKF-PCA-02: Compute Engine, GKE, Serverless & Vertex AI Architecture

## 1. Compute Platform Selection Matrix (`Cloud Run` vs. `Cloud Run Jobs` vs. `GKE Autopilot` vs. `GKE Standard` vs. `Compute Engine MIGs`)

```mermaid
flowchart TD
    Q["What type of workload are you deploying on Google Cloud?"]

    Q -->|"1. Stateless HTTP/gRPC web app, API, or event-driven container\nthat should scale to zero and charge per ms of request processing"| CR["✅ CLOUD RUN (Services)\n• Scales 0 -> 1,000+ instances in seconds\n• Use `--no-cpu-throttling` ('CPU Always Allocated')\n  if background threads run outside HTTP requests!\n• Use Global External ALB + Serverless NEG for\n  static Anycast IP, Cloud Armor & Cloud CDN"]

    Q -->|"2. Non-HTTP finite batch container (`ffmpeg` transcoding,\nDB migrations, nightly scripts running up to 24 hours)"| CRJ["✅ CLOUD RUN JOBS\n• Triggered via Eventarc, Cloud Scheduler, or Workflows\n• Scales to 0 immediately when batch task exits"]

    Q -->|"3. Kubernetes microservices where team wants Google to\nmanage nodes/security & bill ONLY for Pod resource requests"| GKEA["✅ GKE AUTOPILOT\n• Billed strictly for CPU, Memory & Ephemeral Storage\n  *requested* in Pod specs (Mock 4 Q8)!\n• Pre-hardened (Workload Identity, Shielded Nodes)"]

    Q -->|"4. Kubernetes workloads needing custom node pools, daemonsets,\nWindows Server nodes, or fine-grained GPU/kernel tuning"| GKES["✅ GKE STANDARD\n• Windows Server node pools REQUIRE VPC-native\n  (Alias IPs) networking (Mock 4 Q15)!\n• NVIDIA A100 GPUs require: 1) `a2-highgpu` node pool\n  + 2) NVIDIA GPU driver DaemonSet (Mock 4 Q18)!"]

    Q -->|"5. Legacy OS/kernel binaries, licensing tied to physical cores,\nor COTS VMs needing autoscaling & self-healing"| GCE["✅ COMPUTE ENGINE MIG (Managed Instance Group)\n• Multi-signal Autoscaler always picks the policy\n  resulting in the LARGEST number of VMs (Mock 2 Q47)!"]

    style CR fill:#dcfce7,stroke:#15803d,stroke-width:2px
    style GKEA fill:#eff6ff,stroke:#1d4ed8,stroke-width:2px
    style GKES fill:#fef3c7,stroke:#b45309,stroke-width:2px
```

---

## 2. High-Yield GKE & Compute Engine Security, Networking & Availability Rules

| Architectural Requirement | Mandatory Google Cloud Configuration | Why Alternatives Fail (Exam Traps) |
| :--- | :--- | :--- |
| **1. Encrypt Data IN-USE Inside Physical RAM (`Memory`) with Zero App Code Changes** *(Area 2 Q7, Mock 4 Q2)* | ✅ **Confidential GKE Nodes / Confidential VMs** (powered by **AMD SEV / Intel TDX** hardware memory encryption keys that Google cannot read) | ❌ **Shielded VMs / Shielded GKE Nodes** only validate BIOS/UEFI boot and kernel integrity against rootkits (`Secure Boot`, `vTPM`, `Integrity Monitoring` — *Mock 4 Q36*); they **do NOT encrypt RAM**! |
| **2. GKE Pods Accessing Google Cloud APIs (`Cloud SQL`, `GCS`, `Secret Manager`, `BigQuery`) Without JSON Keys** *(Mock 4 Q5)* | ✅ **1) Enable Workload Identity on the GKE cluster + 2) Bind the Kubernetes Service Account (`KSA`) to the Google Service Account (`GSA`)** (`roles/iam.workloadIdentityUser`) | ❌ Using the Compute Engine default node service account (`0.0.0.0/0` cloud-platform scope) or mounting downloaded SA JSON keys inside Kubernetes Secrets. |
| **3. Transparent Pod-to-Pod `mTLS` Encryption & Layer-7 Service Authorization Across GKE** *(Mock 1 Q26, Sec Set 1 Q9)* | ✅ **Anthos Service Mesh (`Google Cloud Service Mesh` / Managed Istio)** | ❌ Rewriting every application microservice to manage its own TLS certificates in code, or relying on Kubernetes `NetworkPolicies` (which only filter L3/L4 IP/Port, not `mTLS` encryption!). |
| **4. Distribute GKE Deployment Replicas Evenly Across Zones for High Availability** *(Mock 1 Q60)* | ✅ **Pod Topology Spread Constraints (`topologySpreadConstraints` with `topologyKey: topology.kubernetes.io/zone`)** or **Pod Anti-Affinity** | ❌ Using `DaemonSets` for stateless web workloads (`DaemonSets` run exactly 1 pod per node for logging/monitoring/GPU driver agents). |
| **5. Spot VMs (Preemptible VMs) Runtime & Cost Rules** *(Mock 2 Q17, Mock 4 Q45)* | • **Spot VMs:** 60–91% discount; **NO minimum runtime guarantee** (can be preempted at any time with a 30-second ACPI shutdown notice — *Mock 2 Q17*).<br>• **Weekday Dev/Test VMs (`9 AM – 5 PM`):** Attach a Compute Engine **Instance Schedule** *(Mock 3 Q54, Mock 4 Q45)*.<br>• **Oversized/Idle VMs:** Query the **Recommender API** programmatically *(Mock 4 Q31)*. | ❌ Assuming Spot VMs have a checkbox that guarantees 30 minutes of uninterrupted execution.<br>❌ Querying `compute.instances.list` alone to get ML rightsizing recommendations. |

---

## 3. Vertex AI & Generative AI Architecture Patterns (`Mock 1 Q34` & `Mock 4 Q3, Q17, Q18, Q21, Q42`)

1. **Mixed CPU Preprocessing + GPU Inference on Vertex AI (*Mock 4 Q21*):**
   * Build a **Custom Container that implements both CPU preprocessing and GPU inference stages**, and deploy it to a **Vertex AI Endpoint configured with an appropriate machine type and attached GPU accelerator**.
2. **Responsible AI & Content Safety on Vertex AI (*Mock 4 Q3 & Q17*):**
   * **Imperceptible AI Content Provenance (*Mock 4 Q3*):** **Imagen on Vertex AI** automatically embeds **SynthID watermarking** directly into the pixel/audio/text data so detection tools can verify AI generation even if EXIF metadata is stripped.
   * **Blocking Harmful Outputs (*Mock 4 Q17*):** Configure **Vertex AI Safety Filter Settings (`Safety Attributes` thresholds)** to block Hate Speech, Harassment, Sexually Explicit, and Dangerous Content.
3. **ML Model Lifecycle & Versioning (*Mock 4 Q42*):**
   * Use **Vertex AI Model Registry** as the central repository to version models, track evaluation metadata/lineage, and deploy aliases to endpoints.
4. **LLM Context & Response Caching (*Mock 1 Q34*):**
   * Cache **repeated queries with identical prompts** and **common document summarization requests** (e.g., using Vertex AI Context Caching or Memorystore for Redis) to cut token latency and cost; never cache highly personalized real-time banking responses across users.

---

## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

This OKF concept module enforces the architectural standards defined in `00-fde-field-readiness-and-grading-rubric.md` and the official Google Cloud Forward Deployed Engineering (FDE) handbook (`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`), ensuring secure-by-default compute isolation (Confidential Computing, Workload Identity, Service Mesh mTLS) and cost-optimal serverless/GKE sizing.

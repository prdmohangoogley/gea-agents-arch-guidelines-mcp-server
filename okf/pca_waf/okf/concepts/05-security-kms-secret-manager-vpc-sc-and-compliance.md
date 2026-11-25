---
type: concept
id: OKF-PCA-05
title: "Security, KMS, Secret Manager, VPC Service Controls & Compliance Architecture (WAF Security Pillar)"
description: "L400 architectural decision framework for Encryption Key Management (GMEK, CMEK, CSEK, EKM, Tink ALE), Secret Manager, Binary Authorization, VPC Service Controls, Cloud Armor, IAP, and PCI-DSS/HIPAA compliance."
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
generated_method: "okf-v0.2-dataplex-synthesis"
verified: true
source_doc_id: "PCA_Book.pdf | UDEMY-Course-PCA.pdf | ExamTopics.pdf | GCP_PCA_Mock_Tests_1_to_4.pdf"
sources:
  - filename: "PCA_Book.pdf"
    title: "Official Google Cloud Certified Professional Cloud Architect Study Guide"
    authors: ["Dan Sullivan"]
    affiliation: "Sybex / John Wiley & Sons, Inc."
    venue: "Wiley Certification Guide (Chapters 11 & 12 — Designing for Security and Legal Compliance: HIPAA, PCI-DSS, GDPR)"
    isbn: "978-1-119-60244-6"
    url: "https://cloud.google.com/certification/cloud-architect"
  - filename: "UDEMY-Course-PCA.pdf"
    title: "Google Cloud Professional Cloud Architect (PCA): Complete Certification Course & Architectural Reference Deck"
    authors: ["GCP PCA Curriculum Architecture Team"]
    affiliation: "Udemy / Google Cloud Partner Training"
    venue: "Section 11 (Slides 219–242 — KMS, Secret Manager, VPC-SC, Cloud Armor, IAP, DLP & Security Command Center)"
    url: "https://cloud.google.com/architecture/framework/security"
  - filename: "GCP PCA Mock Tests 1–4, Security Set 1 & Area 5 Simulator Corpus"
    title: "Forensic Diagnostic Corpus: PCA Mock Exams 1–4 (Nov 2, 3, 6, 9, 2026), Security Set 1 & Service Area 5 Simulator"
    authors: ["Pradeep Mohan", "GCP PCA Test Bank"]
    affiliation: "Google Cloud Forward Deployed Engineering (FDE)"
    venue: "/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/"
content_sha256: "830c4c267760b6ce84360bec6cf8004cf94860b3d9be1bb9daa7192c89c2c4e9"
---


# OKF-PCA-05: Security, KMS, Secret Manager, VPC Service Controls & Compliance Architecture

## 1. Encryption Key Management & Secrets Decision Matrix (`GMEK` vs. `CMEK` vs. `CSEK` vs. `EKM` vs. `Tink ALE` vs. `Secret Manager`)

```mermaid
flowchart TD
    E["What Is Your Application's Encryption or Secret Management Requirement?"]

    E -->|"1. Store DB passwords, API keys, TLS private keys, or OAuth tokens\nwith versioning, audit logs & native GKE/Cloud Run mounting\n(Mock 1 Q41/Q53, Mock 2 Q30)"| SM["✅ SECRET MANAGER\n• Mount natively as volume or env var (`--set-secrets`)\n• Pair with Workload Identity on GKE\n• NEVER use Cloud KMS to store plaintext passwords!"]

    E -->|"2. Rotate cryptographic encryption keys (CMEK) or digital signing\nkeys (DRM content signing) automatically every 30/90 days\n(Mock 1 Q38, Mock 4 Q43)"| KMS["✅ CLOUD KMS (or CLOUD HSM for FIPS 140-2 L3)\n• Configure Automatic Rotation Schedule on the Key Ring!\n• Grant Service Agent `roles/cloudkms.cryptoKeyEncrypterDecrypter`"]

    E -->|"3. Supply raw AES-256 key in HTTP header on every request so\nGoogle NEVER stores the key on disk (Area 1 Q2)"| CSEK["✅ CSEK (Customer-Supplied Encryption Keys)\n• 🚨 LAW: Supported ONLY on Cloud Storage &\n  Compute Engine Persistent Disks — NEVER BigQuery!"]

    E -->|"4. Keys must reside outside Google Cloud in a 3rd-party key manager\naccessed via HTTPS URI for BigQuery, GCS, or GCE (Area 1 Q2)"| EKM["✅ CLOUD EKM (External Key Manager)\n• Supports BigQuery, Cloud Storage, Compute Engine, GKE"]

    E -->|"5. Encrypt sensitive fields (credit cards) BEFORE sending to Firestore\nso the database engine NEVER sees plaintext (Mock 1 Q6, Mock 4 Q29)"| ALE["✅ APPLICATION-LAYER ENCRYPTION (ALE)\n• Client-side Envelope Encryption using Google Tink library\n  + Cloud KMS KEK"]

    style SM fill:#dcfce7,stroke:#15803d,stroke-width:2px
    style KMS fill:#eff6ff,stroke:#1d4ed8,stroke-width:2px
    style CSEK fill:#fce8e6,stroke:#b91c1c,stroke-width:2px
    style ALE fill:#fef3c7,stroke:#b45309,stroke-width:2px
```

---

## 2. Zero-Trust Perimeter Defense: `VPC Service Controls` vs. `IAP` vs. `Cloud Armor` vs. `CAS`

| Security Control | Primary Architectural Role | Critical Configuration & Verified Exam Traps |
| :--- | :--- | :--- |
| **1. VPC Service Controls (`VPC-SC`)** *(Mock 4 Q9)* | **API-Level Data Exfiltration Perimeter** around multi-tenant Google Cloud APIs (`BigQuery`, `Cloud Storage`, `Spanner`, `Vertex AI`). Prevents a stolen credential or rogue insider from copying data to an external project's GCS bucket! | • **Allowing Human Analysts in via Google Cloud Console (*Mock 4 Q9*):** Because the Cloud Console runs outside the perimeter, configure **Access Context Manager (`Access Levels` based on User Identity or Corporate IP)** and attach it to the perimeter's **Ingress Policy**!<br>• **Trap:** A **Perimeter Bridge** only connects two GCP perimeters—it **never** grants human Console access! |
| **2. Identity-Aware Proxy (`IAP`)** *(Sec Set 1 Q1 & Q2)* | **Zero-Trust Identity & Context Front Door (`BeyondCorp`)** for human staff/admins accessing internal web apps (`Cloud Run`, `App Engine`, `GKE`) or SSH/RDP (`--tunnel-through-iap`). | • Evaluates user identity (`Cloud Identity` / `AD SSO`) + device posture (`Access Context Manager`) *before* traffic reaches the app.<br>• Require **`roles/iap.httpsResourceAccessor`** (or `roles/run.invoker`). |
| **3. Google Cloud Armor + GFE Firewall Lockdown** *(Sec Set 1 Q4, Area 5 Q3)* | **Edge Layer-7 WAF & DDoS Protection** attached to External Application Load Balancers (OWASP Top 10 `SQLi`/`XSS`, Adaptive Protection, reCAPTCHA, geo/IP rate-limiting). | • **Mandatory Backend Lockdown (*Area 5 Q3*):** To stop attackers from bypassing Cloud Armor by hitting VM IPs directly, configure **VPC Ingress Firewall Rules allowing traffic ONLY from Google Front End (`GFE`) ranges (`130.211.0.0/22` and `35.191.0.0/16`)**! |
| **4. Binary Authorization + Container Analysis API** *(Mock 1 Q48, Mock 2 Q40, Sec Set 1 Q3)* | **Cryptographic Container Admission Control** for GKE and Cloud Run. | • **Vulnerability Scanning (`Artifact Analysis`)** only **detects** CVEs.<br>• **Binary Authorization** **blocks** unsigned images.<br>• **3x Repeat Trap:** If an image is signed by the attestor yet fails with `'Image verification failed'`, **the `Attestation` occurrence metadata was not created in the Container Analysis API**! |
| **5. Certificate Authority Service (`CAS`)** *(Mock 2 Q32)* | **Managed Private CA** for issuing internal `mTLS` and microservice mesh TLS certificates via API without running an OpenSSL VM. | • Use **Certificate Manager** for public Load Balancer SSL certificates; use **Certificate Authority Service (`CAS`)** for internal private PKI. |

---

## 3. Regulatory Compliance Patterns (`PCI-DSS`, `HIPAA`, `Malware Quarantine`)

1. **Minimizing PCI-DSS Audit Scope (*Area 5 Q1 / ExamTopics Q#15*):**
   * **Tokenize** 16-digit Primary Account Numbers (`PANs`) at the point of capture (or via **Sensitive Data Protection `Cloud DLP` Format-Preserving Encryption / Crypto-Deterministic Tokenization**) so **only surrogate tokens** ever enter your downstream microservices and BigQuery analytics tables! Any database storing raw PANs (even encrypted at rest with GMEK/CMEK) falls 100% in scope for PCI-DSS audits.
2. **De-Identifying PHI Before BigQuery Ingestion (*Mock 2 Q58*):**
   * Never load raw PHI CSVs into BigQuery first and apply column security if the mandate says *"de-identify before loading into BigQuery."* Run a **Cloud Dataflow pipeline calling the Sensitive Data Protection (`Cloud DLP`) API** to mask/tokenize PHI in flight before writing to BigQuery!
3. **Cloud Storage Malware & Virus Scanning (*2x Repeat Offender: Mock 2 Q31 & Mock 4 Q51*):**
   * **There is NO native built-in malware scanning checkbox in Cloud Storage!**
   * **Architecture:** Implement the **Two-Bucket Quarantine Pattern**: upload files to an `unscanned` bucket $\rightarrow$ trigger an **Eventarc / Cloud Run function** on `storage.object.finalize` $\rightarrow$ scan the file using a containerized third-party antivirus engine (such as **ClamAV**) $\rightarrow$ move clean files to the `clean` bucket or infected files to the `quarantine` bucket!

---

## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

This OKF concept module enforces the architectural standards defined in `00-fde-field-readiness-and-grading-rubric.md` and the official Google Cloud Forward Deployed Engineering (FDE) handbook (`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`), guaranteeing defense-in-depth security across network, identity, compute, and data layers.

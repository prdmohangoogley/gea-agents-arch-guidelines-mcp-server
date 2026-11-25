---
type: concept
id: OKF-PCA-04
title: "Identity, Resource Hierarchy, Organization Policies, IAM & Cloud Billing FinOps (WAF Governance & Cost)"
description: "L400 architectural decision framework for Cloud Identity vs. Managed Microsoft AD, Resource Hierarchy, Organization Policies, IAM Conditions/Deny/Impersonation, and Cloud Billing FinOps governance."
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
    venue: "Wiley Certification Guide (Chapters 3, 4, 5, 10 — Resource Hierarchy, IAM, Organization Policies & Cost Optimization)"
    isbn: "978-1-119-60244-6"
    url: "https://cloud.google.com/certification/cloud-architect"
  - filename: "UDEMY-Course-PCA.pdf"
    title: "Google Cloud Professional Cloud Architect (PCA): Complete Certification Course & Architectural Reference Deck"
    authors: ["GCP PCA Curriculum Architecture Team"]
    affiliation: "Udemy / Google Cloud Partner Training"
    venue: "Section 3 (Slides 24–48 — Resource Hierarchy, Org Policies, IAM, Service Accounts, Cloud Billing, Budgets & Quotas)"
    url: "https://cloud.google.com/architecture/framework"
  - filename: "GCP PCA Mock Tests 1–4 & Area 4 Simulator Corpus"
    title: "Forensic Diagnostic Corpus: PCA Mock Exams 1–4 (Nov 2, 3, 6, 9, 2026) & Service Area 4 Simulator"
    authors: ["Pradeep Mohan", "GCP PCA Test Bank"]
    affiliation: "Google Cloud Forward Deployed Engineering (FDE)"
    venue: "/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/"
content_sha256: "b1084c2f54a64a664d69c6a76c539eb7cc9b73e7cbbcab76837a10480dc89605"
---


# OKF-PCA-04: Identity, Resource Hierarchy, Organization Policies, IAM & Cloud Billing FinOps

## 1. Workforce, Customer & Windows Workload Identity Architecture

```mermaid
flowchart TD
    ID["Which Identity Architecture Does Your Application / Enterprise Require?"]

    ID -->|"1. Workforce Employees signing in to GCP Console / gcloud / IAP\nusing existing On-Premises Active Directory credentials"| CI["✅ CLOUD IDENTITY (Free or Premium)\n+ Google Cloud Directory Sync (GCDS — one-way AD sync)\n+ SAML 2.0 / OIDC SSO to AD FS / Entra ID / Okta\n• Bind IAM roles strictly to synchronized GOOGLE GROUPS!"]

    ID -->|"2. Legacy Windows Server VMs, SQL Server, or Enterprise SMB\nFile Shares needing Kerberos, NTLM, Domain Join & GPOs (Area 4 Q4)"| MAD["✅ MANAGED SERVICE FOR MICROSOFT ACTIVE DIRECTORY\n(`Managed Microsoft AD` in GCP with a Forest Trust to On-Prem AD)\n+ Google Cloud NetApp Volumes (`SMB` protocol)!"]

    ID -->|"3. Consumer / Multi-Tenant B2C App Users signing up with\nEmail/Password, Google, Facebook, Apple, or Tenant SAML (Mock 4 Q46)"| GCIP["✅ IDENTITY PLATFORM (GCIP)\n• Managed CIAM with Multi-Tenancy, MFA & OIDC/JWT\n• Pair with custom app tenant logic + Cloud IAM for backend SAs"]

    style CI fill:#eff6ff,stroke:#1d4ed8,stroke-width:2px
    style MAD fill:#fce8e6,stroke:#b91c1c,stroke-width:2px
    style GCIP fill:#dcfce7,stroke:#15803d,stroke-width:2px
```

---

## 2. Resource Hierarchy, Organization Policies & IAM Governance Rules

| Governance Domain | Architectural Law & Best Practice | Verified Exam Trap to Avoid |
| :--- | :--- | :--- |
| **1. Project Identifiers & 30-Day Deletion Recovery** *(Area 4 Q1)* | • **Project Name** is mutable at any time; **Project ID** and **Project Number** are **permanently immutable** after creation.<br>• Accidentally deleted (`SHUTDOWN`) projects can be restored within a **30-day recovery window** (`IAM & Admin > Manage Resources`). | ❌ Opening a P1 ticket to rename a Project ID or assuming deleted projects are unrecoverable after 24 hours. |
| **2. High-Yield Organization Policy Constraints** *(Mock 3 Q1, Q19, Q37; Mock 4 Q33, Q58)* | • **Restrict Regions (*Mock 3 Q37*):** `constraints/gcp.resourceLocations` set to **`Allow` (`in:us-central1-locations`, `in:europe-west1-locations`)**.<br>• **Block Public GCS Buckets (*Mock 4 Q33*):** `constraints/storage.publicAccessPrevention` (`Enforce`).<br>• **Block VM Public IPs (*Mock 3 Q19*):** `constraints/compute.vmExternalIpAccess` (`Enforce` at Org root, override to `Not Enforce` on DMZ project).<br>• **Block SA JSON Keys:** `constraints/iam.disableServiceAccountKeyCreation`.<br>• **Restrict Domains:** `constraints/iam.allowedPolicyMemberDomains`.<br>• **Require Central CMEK Project (*Mock 3 Q1*):** `constraints/gcp.restrictCmekCryptoKeyProjects` + `constraints/gcp.restrictNonCmekServices`.<br>• **Restrict VM Machine Types (*Mock 4 Q58*):** `constraints/compute.restrictMachineTypes` (for Folder-level policy) or **GPU Quota = 0** (for project capacity cap). | ❌ Confusing `storage.uniformBucketLevelAccess` (which disables per-object ACLs in favor of IAM) with `storage.publicAccessPrevention` (which blocks `allUsers`/`allAuthenticatedUsers` — *Mock 4 Q33*). |
| **3. Custom IAM Roles Scope & IAM Deny Policies** *(Area 4 Q5)* | • 🚨 **LAW: Custom IAM Roles can ONLY be created at the `Organization` level or `Project` level—NEVER at the `Folder` level!** (To share a Custom Role across a Folder, create it at the **Organization** level and *bind* it at the Folder level).<br>• **IAM Deny Policies:** Evaluated *before* all Allow policies; can block a permission (e.g., `cloudkms.cryptoKeyVersions.destroy`) **even if a user holds `roles/owner`**, with tag exemptions (`!resource.matchTag('org/env', 'sandbox')`). | ❌ Running `gcloud iam roles create --folder=...` *(Area 4 Q5)*. |
| **4. Service Account Dual Nature (`SA User` vs. `Token Creator`) & Lifecycle** *(Area 4 Q7, Q8, Q12)* | • **Attach SA to a VM / Cloud Run:** Grant **`roles/iam.serviceAccountUser`** scoped to the specific Service Account.<br>• **Temporarily Impersonate SA via CLI (`--impersonate-service-account`):** Grant **`roles/iam.serviceAccountTokenCreator`**.<br>• **Right-size 90-day unused permissions:** Use **IAM Recommender + IAM Policy Simulator**.<br>• **Retire unused SAs safely:** Follow a **Disable-then-Delete** lifecycle! | ❌ Exporting long-lived Service Account JSON keys or deleting unused Service Accounts immediately without disabling first. |
| **5. Resource Manager Tags (`Secure Tags`) vs. Billing Labels** *(Mock 1 Q44, Mock 4 Q40, Area 4 Q20)* | • **Resource Manager Tags (`TagKeys/TagValues`):** IAM-governed (`roles/resourcemanager.tagUser`), inherited down hierarchy; used for **IAM Conditions, IAM Deny exemptions, Org Policy conditions, and VPC Network Firewall Policies**.<br>• **Billing Labels (`cost-center: 123`, `env: prod`):** Key-value metadata enforced via **Terraform modules** (*Mock 1 Q44*) and exported to **BigQuery Cloud Billing Exports** (*Mock 4 Q40*) for cost allocation! | ❌ Using Billing Labels for VPC Firewall rules or IAM Conditions, or using legacy Network Tags for billing exports. |

---

## 3. Cloud Billing Architecture, FinOps Budgets, BigQuery Exports & CUDs

1. **Cloud Billing Separation of Duties (*Area 4 Q10 & Q20*):**
   * **Finance Admins (Payment cards & invoices, zero project access):** `roles/billing.admin` (`Billing Account Administrator`) on the Billing Account.
   * **Platform Engineers (Link new projects to Billing Account without seeing invoices):** `roles/resourcemanager.projectCreator` + `roles/billing.user` (`Billing Account User`) on the Billing Account (plus `roles/billing.projectManager` on the project).
   * **Project Managers (View costs & create/edit Budgets without modifying payment methods):** `roles/billing.costsManager` (`Billing Account Costs Manager`).
2. **Enforcing a Hard Spending Cap at 100% of Sandbox Budget (*Area 4 Q13*):**
   * **Cloud Billing Budgets ONLY send notifications—they never stop VMs automatically!**
   * **Architecture:** `Cloud Billing Budget -> Programmatic Notification to Cloud Pub/Sub -> Cloud Run function` (calls Compute Engine API to stop VMs or `projects.updateBillingInfo` to unlink billing).
3. **BigQuery Cloud Billing Export (`Standard` vs. `Detailed` & Multi-Region Backfill — *Area 4 Q14*):**
   * Enable **`Detailed usage cost`** (for VM instance ID & GKE Namespace/Pod label granularity) into a **Multi-Region (`US` or `EU`) BigQuery dataset**—because **Multi-Region (`US`/`EU`) automatically backfills billing data from the start of the previous month** (whereas single-region datasets only export data from the day enabled!).
4. **Shared VPC Service Project Billing & Committed Use Discounts (`CUDs` — *Mock 3 Q4, Q20, Q28*):**
   * Enable **Shared VPC Service Project Billing** so network egress charges are billed directly to the originating Service Project rather than the Host Project.
   * **CUDs** are shared automatically across all projects linked to the same Cloud Billing Account; use **Compute Flexible CUDs (Spend-based)** to discount **Compute Engine + GKE + Cloud Run** across any region or machine family.

---

## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

This OKF concept module enforces the architectural standards defined in `00-fde-field-readiness-and-grading-rubric.md` and the official Google Cloud Forward Deployed Engineering (FDE) handbook (`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`), establishing enterprise-grade landing-zone guardrails, keyless authentication, and FinOps cost accountability.

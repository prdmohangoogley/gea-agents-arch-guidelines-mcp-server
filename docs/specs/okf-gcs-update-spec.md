# Spec: OKF v0.2 Cloud Storage Bundle & Knowledge Catalog Update (`okf-gcs-update-spec.md`)

**Status:** ACTIVE (Living Cumulative Specification — v4.0)  
**Target Repository:** [`https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server`](https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server)  
**Canonical Repo Path:** `docs/specs/okf-gcs-update-spec.md` (mirrored at `specs/okf-gcs-update-spec.md`)  
**Executable Update Script:** `scripts/update_okf_gcs.sh`  
**Terraform IaC Module:** `iac/` (`iac/modules/gcs/`)  
**Target GCP Project:** `fivedaysai-prd-sandbox-317383` (`301802433103`)  
**Target GCS Bucket:** [`gs://gea_agent_development_architectural_best_practices_1790796607`](https://pantheon.corp.google.com/storage/browser/gea_agent_development_architectural_best_practices_1790796607?forceOnBucketsSortingFiltering=true&project=fivedaysai-prd-sandbox-317383)  
**Preserved Corpus & Version Tag:** `GEAPL200` · `GEAPL200_2026-09-30_124746`  
**Preserved TTL Policy:** `180 days` (`stale_after` anchored to source modification timestamps)  
**Governing FDE Charter & Rubric:** [`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head) · [`concepts/00-fde-field-readiness-and-grading-rubric.md`](../okf/concepts/00-fde-field-readiness-and-grading-rubric.md)

---

## 0. Living Specification & Cumulative Update Mandate (CRITICAL RULE)

> **MANDATORY FOR ALL FUTURE ANTIGRAVITY & DEVELOPER UPDATES:**
> 1. **Single Canonical Spec:** This document (`docs/specs/okf-gcs-update-spec.md`) is the **single authoritative specification** governing all updates, extensions, schema changes, and synchronizations to the Cloud Storage Open Knowledge Format (`OKF v0.2`) bundle (`gs://gea_agent_development_architectural_best_practices_1790796607/okf`) and its downstream GCP Knowledge Catalog (Dataplex) and Spanner/BigQuery Graph pipelines.
> 2. **Cumulative In-Place Evolution (Never Fork Specs):** Any future specification that adds new OKF concepts (e.g., L400 concepts, vertical industry packs, new FDE rubric criteria, or MCP tool updates) **MUST modify and save this exact file in place** as an incremental revision rather than creating disconnected one-off spec files.
> 3. **Append to the Revision Ledger:** Every update to this specification **must** append a new row to **Section 1 (Cumulative Spec Revision Ledger)**, update the concept inventory in **Section 3**, and keep `scripts/update_okf_gcs.sh` and `iac/` backward-compatible and idempotent.
> 4. **Preserve Version & TTL Semantics Unless Explicitly Rotated:** Unless the user explicitly commands a version tag rotation, all updates must preserve the active `version_tag` (`GEAPL200_2026-09-30_124746`) and 180-day `stale_after` TTL semantics so downstream graph edges and Dataplex entries are not needlessly invalidated.

---

## 1. Cumulative Spec Revision Ledger

| Spec Rev | Date (PDT) | Author / Agent | Bundle Version Tag | Concept Count | Summary of Changes |
|---|---|---|---|---:|---|
| **v1.0** | `2026-09-30` | `gemini-enterprise:gdoc-to-markdown` | `GEAPL200_2026-09-30_124746` | `20` | Initial OKF v0.2 bundle published to `gs://gea_agent_development_architectural_best_practices_1790796607/okf` (`01`–`20` from GEAPL200 Google Docs corpus, 73 Mermaid diagrams, 94 tables, 4 retained figures). |
| **v2.0** | `2026-10-26` | `gemini-enterprise:okf-synthesizer` | `GEAPL200_2026-09-30_124746` *(preserved)* | `36` | Merged existing 20 L200 concepts (`01`–`20`) with 15 GEAP L300 concepts (`21`–`35`) and standalone **Google Cloud FDE Field-Readiness & Project Grading Rubric** (`00-fde-field-readiness-and-grading-rubric.md`). Injected enforceable FDE Rubric (Part A & Part B) and prevailing customer exemplars into all 36 concepts; added `scripts/update_okf_gcs.sh` and Terraform execution harness. |
| **v3.0** | `2026-10-27` | `gemini-enterprise:okf-synthesizer` | `GEAPL200_2026-09-30_124746` *(00..35 preserved)* / `L400_version_20261026_0350` *(36..57)* | `58` | Cumulative expansion merging 22 GEAP L400 concepts (`36`–`57`, Architecture A1..A5, Agents B1..B3, Governance G1..G3, Optimization O1..O6, and Synthesis 18..21) into the canonical OKF v0.2 bundle. Injected FDE Rubric enforcement, updated bundle descriptors (875 Mermaid diagrams, 1,533 tables, 4 figures), generated 58 Dataplex catalog aspect payloads, and updated GCS sync orchestrators. |
| **v4.0** | `2026-10-27` | `gemini-enterprise:arch-spec-lead` | `GEAPL200_2026-09-30_124746` *(preserved)* | `58` | Established modular expansion specification suite: (a) Spanner Graph & BigQuery Graph Propagation (`spanner-bq-graph-sync-spec.md`), (b) MCP Server Best Practices & Skills Registry Audit (`mcp-server-best-practices-audit-spec.md`), (c) Gemini Enterprise Deployment & E2E Testing (`mcp-gemini-enterprise-deployment-spec.md`), (d) Autonomous OKF Evolution Tools & Antigravity Skill (`okf-auto-evolution-tools-spec.md`), and (e) FDE Charter Search & Governance Skill (`fde-charter-governance-skill-spec.md`). |
| **v4.1** | `2026-10-27` | `gemini-enterprise:okf-synthesizer` | `GEAPL200_2026-10-27_183500` *(active)* | `81` | Synchronized 3 specialized research & architecture packs into Cloud Storage (`gs://gea_agent_development_architectural_best_practices_1790796607/okf`): (1) Socratic Grilling & Prompting (`36-socratic-...`..`41-socratic-...`, S0..S6, 8 PDFs), (2) Multi-Agent Tokenomics & Grilling (`36-foundations-...`..`43-master-...`, O7, 2 PDFs), and (3) Context, Cache & Memory (`36-agentic-...`..`44-fde-...`, 6 PDFs). Total GCS concepts reached 81 files with 16 grounded research PDFs and 24 L400 modules, preserving 180-day TTL policies. |

---

## 2. Architecture & Execution Flow (Cloud Shell + Terraform + Dataplex)

```mermaid
flowchart TB
    subgraph Repo ["GitHub Repo: gea-agents-arch-guidelines-mcp-server"]
        Spec["Living Spec<br/>docs/specs/okf-gcs-update-spec.md"]
        Bundle["Local OKF v0.2 Bundle<br/>okf/ (58 Concepts, index.md, log.md,<br/>bundle.json, MANIFEST.json, img/)"]
        Script["Cloud Shell / CLI Orchestrator<br/>scripts/update_okf_gcs.sh"]
        TF["Terraform IaC<br/>iac/ (main.tf, modules/gcs)"]
    end

    subgraph Gates ["Pre-Flight & Structural Verification Gates"]
        QA["1. OKF Structural & FDE Rubric QA<br/>• 58 Concepts (00..57) present<br/>• SHA-256 content_sha256 match<br/>• FDE Rubric Section & Concept 00 link verified"]
        Auth["2. Cloud Shell / GCP Preflight<br/>• gcloud auth & Project Number (301802433103)<br/>• Bucket Versioning & Lifecycle Check"]
    end

    subgraph GCP ["Google Cloud Platform (fivedaysai-prd-sandbox-317383)"]
        GCS[("Cloud Storage Bucket<br/>gs://gea_agent_development_architectural_best_practices_1790796607/okf<br/>(Object Versioning ON, Uniform Access)")]
        CRC["3. Post-Upload CRC32C Verification<br/>scripts/crc32c_verify.py"]
        Catalog["4. GCP Knowledge Catalog (Dataplex)<br/>EntryGroup: geapl200-architecture-kb<br/>AspectType: okf (58 Entries)"]
        NL2KG["5. Optional NL2KG Downstream Sync<br/>Spanner Graph (arch_guidelines_graph) &<br/>BigQuery (gea_arch_guidelines_analytics)"]
    end

    Spec -->|Governs| Script
    Spec -->|Governs| TF
    Bundle --> QA
    Script --> QA
    QA --> Auth
    TF -->|Provision / Verify Bucket & Governance| GCS
    Auth -->|gcloud storage rsync --recursive| GCS
    GCS --> CRC
    CRC -->|Verified Digest| Catalog
    Catalog -.->|--run-nl2kg (optional)| NL2KG
```

---

## 3. Unified OKF v0.2 Bundle Specification (`58 Concepts`)

The unified OKF v0.2 bundle staged in the repository (`okf/`, `L300_concepts/`, and `L400_concepts/`) and synchronized to `gs://gea_agent_development_architectural_best_practices_1790796607/okf/` comprises:

- **`index.md` & `INDEX.md`:** Progressive-disclosure root index containing the standalone **Mandatory Governance: Google Cloud FDE Field-Readiness & Project Grading Rubric** section, domain taxonomy clusters, and the 58-concept freshness table.
- **`log.md`:** Chronological changelog preserving the `2026-09-30` baseline publication, recording the `2026-10-26` L200 + L300 unification, and documenting the `2026-10-27` L400 cumulative integration.
- **`bundle.json` & `MANIFEST.json`:** Machine-readable descriptors containing per-concept SHA-256 digests, tags, `stale_after` RFC3339 deadlines, and structural counts (**58 concepts**, **875 Mermaid diagrams**, **1,533 GFM pipe tables**, **4 retained PNG figures**).
- **`concepts/00-fde-field-readiness-and-grading-rubric.md`:** Standalone enforceable FDE Grading Rubric concept anchored to [`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head) (0–3 scale, Part A Advisory Rigor, Part B Engineering Excellence across 7 domains / 26 sub-competencies, `>= 2.0` pass cutline, zero `0` disqualifier pause rule, and cross-corpus customer exemplars).
- **`concepts/01-*.md` to `concepts/20-*.md`:** The 20 preliminary `GEAPL200` concepts from the GCS bucket, preserving their exact original `source_modified` and `stale_after` timestamps while enriched with `## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment`.
- **`concepts/21-*.md` to `concepts/35-*.md`:** The 15 `GEAP L300` concepts (ADK Multi-Agent Systems, Code Execution Sandbox, Context Persistence, Memory Bank Deep Dive, Generative/Agentic Evaluation, Hill Climbing, Model Upgrades, Cost/FinOps Optimization, Gemini Enterprise App Deployment, Workforce Identity Federation, Deployment Change Management, Agent Change Management, Model Armor, Securing Agents with PAB & Delegated OAuth, and Governing Agents with Agent Gateway & Agent Registry), each carrying full OKF v0.2 YAML frontmatter and `## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment`.
- **`concepts/36-*.md` to `concepts/57-*.md`:** The 22 `GEAP L400` concepts (Master Knowledge Catalog Index, Architecture A1..A5, Agent Deep Dives B1..B3, Zero-Trust Governance G1..G3, Advanced Optimization O1..O6, and Synthesis Compendiums 18..21), each carrying version tag `L400_version_20261026_0350`, 180-day TTL `2027-04-26T00:00:00Z`, and `## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment`.
- **`img/`:** Exact set of 4 retained PNG figures referenced by Concepts `14`, `15`, and `16` (zero unreferenced orphan images).
- **`catalog-entries/*.json`:** 58 Dataplex Knowledge Catalog `okf` AspectType JSON payloads (`00-*.json` through `57-*.json`).

---

## 4. Antigravity Execution Prompt & Goal Block

When handing this specification to **Antigravity** (or executing it in a goal-driven loop), use the following structured goal block:

```markdown
# AGY Goal: Update Cloud Storage OKF v0.2 Bundle & Knowledge Catalog (Spec v3.0)

## 📌 Context
A preliminary 20-concept OKF v0.2 bundle exists in Google Cloud Storage at:
`gs://gea_agent_development_architectural_best_practices_1790796607/okf` (Project: `fivedaysai-prd-sandbox-317383`).
We are updating this bucket in-place (leveraging GCS Object Versioning for instant rollback) with the unified 58-concept OKF v0.2 bundle (`00` FDE Grading Rubric + `01..20` L200 + `21..35` L300 + `36..57` L400), while preserving `version_tag = "GEAPL200_2026-09-30_124746"` and 180-day `stale_after` TTL semantics.

## ⚙️ Target Environment & Variables
- **REPO_URL:** `https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server`
- **GCP_PROJECT_ID:** `fivedaysai-prd-sandbox-317383`
- **GCP_PROJECT_NUMBER:** `301802433103`
- **GCS_BUCKET_NAME:** `gea_agent_development_architectural_best_practices_1790796607`
- **GCS_OKF_URI:** `gs://gea_agent_development_architectural_best_practices_1790796607/okf`
- **DATAPLEX_LOCATION:** `us`
- **DATAPLEX_ENTRY_GROUP:** `geapl200-architecture-kb`
- **DATAPLEX_ENTRY_TYPE:** `okf-concept`
- **DATAPLEX_ASPECT_TYPE:** `okf`
- **PRESERVED_VERSION_TAG:** `GEAPL200_2026-09-30_124746`

## 🛠️ Execution Tasks
1. **Verify Living Spec & Bundle Integrity (Offline Gate):**
   Run `./scripts/update_okf_gcs.sh --dry-run` to execute structural QA over `okf/`:
   - Confirm all 58 concepts (`00`..`57`), `index.md`, `log.md`, `bundle.json`, `MANIFEST.json`, and 58 `catalog-entries/*.json` exist.
   - Verify every concept's `content_sha256` matches its Markdown body digest.
   - Verify every concept (`01`..`57`) contains `## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment` and links to `/concepts/00-fde-field-readiness-and-grading-rubric.md` and `https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`.
2. **Execute Cloud Shell / Terraform Infrastructure & Bucket Update:**
   - **Option A (Cloud Shell / CLI One-Shot):**
     Run `./scripts/update_okf_gcs.sh --catalog`
   - **Option B (Terraform IaC + Sync):**
     Run `./scripts/update_okf_gcs.sh --with-terraform --catalog`
3. **Verify Post-Upload Integrity:**
   Confirm `scripts/crc32c_verify.py` passes 100% size and CRC32C checksum verification against `gs://gea_agent_development_architectural_best_practices_1790796607/okf` and that all 58 Dataplex Knowledge Catalog entries are registered.
```

---

## 5. Cloud Shell & Terraform Execution Modes (`scripts/update_okf_gcs.sh`)

The repository script `scripts/update_okf_gcs.sh` supports four deterministic execution modes designed for **Google Cloud Shell**, local macOS/Linux terminals, and CI/CD runners:

### Mode 1: Dry-Run & Structural QA Validation (Zero Cloud Mutation)
Validates all 58 OKF concept files, SHA-256 digests, FDE Rubric links, and prints the exact `gcloud` / `terraform` commands that will run:
```bash
./scripts/update_okf_gcs.sh --dry-run --catalog
```

### Mode 2: Cloud Shell Direct GCS OKF Update + CRC32C Verification
Verifies project identity (`fivedaysai-prd-sandbox-317383` / `301802433103`), ensures GCS Object Versioning is enabled on `gs://gea_agent_development_architectural_best_practices_1790796607`, snapshots the prior remote `MANIFEST.json` generation ID for rollback safety, syncs the 58-concept OKF v0.2 bundle via `gcloud storage rsync`, and verifies every remote object's CRC32C hash:
```bash
./scripts/update_okf_gcs.sh
```

### Mode 3: Full Update + GCP Knowledge Catalog (Dataplex) Registration
Updates the GCS bucket, verifies CRC32C checksums, regenerates the 58 Dataplex `okf` aspect payloads, and upserts all 58 entries into Dataplex Universal Catalog (`EntryGroup: geapl200-architecture-kb`, `AspectType: okf`):
```bash
./scripts/update_okf_gcs.sh --catalog
```

### Mode 4: Terraform-Orchestrated IaC + GCS OKF Update + Catalog Registration
Runs `terraform init && terraform apply` across `iac/` (binding/updating the GCS bucket, Cloud Spanner Graph, and BigQuery dataset), then executes the OKF bundle rsync, CRC32C verification, and Dataplex catalog registration:
```bash
./scripts/update_okf_gcs.sh --with-terraform --catalog
```

---

## 6. Rollback & Noncurrent Version Recovery Procedure

Because `gs://gea_agent_development_architectural_best_practices_1790796607` enforces **GCS Object Versioning** with a 30-day / 10-version retention lifecycle policy, overwriting or updating objects under `gs://.../okf/` never destroys the preliminary generation:

1. **List archived object generations:**
   ```bash
   gcloud storage ls -a gs://gea_agent_development_architectural_best_practices_1790796607/okf/MANIFEST.json
   ```
2. **Restore a prior generation if needed (`< 5 min MTTR` per FDE Rubric B.6.1):**
   ```bash
   gcloud storage cp \
     "gs://gea_agent_development_architectural_best_practices_1790796607/okf/MANIFEST.json#<GENERATION_NUMBER>" \
     "gs://gea_agent_development_architectural_best_practices_1790796607/okf/MANIFEST.json"
   ```

---

## 7. FDE Grading Rubric Self-Attestation for This Specification

In compliance with [`concepts/00-fde-field-readiness-and-grading-rubric.md`](../okf/concepts/00-fde-field-readiness-and-grading-rubric.md):
- **Part A.4 (AI-Driven Development Discussion):** Establishes a living, cumulative specification (`okf-gcs-update-spec.md`) and an automated verification harness (`update_okf_gcs.sh`) supporting both *in-the-loop* dry-run validation and *outside-the-loop* autonomous Cloud Shell / CI execution.
- **Part B.2.5 & B.2.7 (Decision Records & Operational Documentation):** Documents explicit CLI vs. Terraform execution modes, pre-flight project-number guards, CRC32C integrity verification, and `< 5 min` object-versioned rollback procedures.
- **Part B.6.1 & B.6.2 (CI/CD & Infrastructure as Code):** Provides idempotent Bash and Terraform automation with strict parity across local workspaces, Cloud Shell, and production GCP.

# Antigravity Skills Installation, From-Scratch Deployment & All-38-Skills Testing Runbook

This runbook provides step-by-step instructions to:
1. **Install all 26 `.agents/skills/*` and the `arch-guidelines` MCP server** in a local installation of **Google Antigravity (CLI & IDE)**.
2. **Deploy the entire project from scratch** (`data/` $\rightarrow$ Cloud Storage $\rightarrow$ Dataplex $\rightarrow$ Spanner Graph & BigQuery $\rightarrow$ Vertex AI Reasoning Engines & MCP Server) when switching to a new GCP Project or Argolis Cloud Account.
3. **Execute the Single-Command All-38-Skills Runbook Test** and invoke skills interactively inside Antigravity.

---

## 1. Install the MCP Server & All Skills in Local Antigravity

### Step 1.1: Install Python Environment & Global Antigravity Skills
```bash
cd /Users/prdmohan/ge_spark_workspace/projects/architecture_best_practices_mcp

# 1. Sync virtual environment dependencies
uv sync

# 2. Copy all 26 Antigravity skill directories into ~/.gemini/skills/
mkdir -p ~/.gemini/skills
cp -R .agents/skills/* ~/.gemini/skills/
ls -1 ~/.gemini/skills/
```

### Step 1.2: Verify `~/.gemini/config/mcp_config.json`
Ensure `~/.gemini/config/mcp_config.json` registers `arch-guidelines` and `gea-arch-guidelines`:

```json
{
  "mcpServers": {
    "arch-guidelines": {
      "command": "/Users/prdmohan/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/prdmohan/ge_spark_workspace/projects/architecture_best_practices_mcp",
        "run",
        "gea-mcp-server",
        "--transport",
        "stdio"
      ],
      "env": {
        "GCP_PROJECT_ID": "fivedaysai-prd-sandbox-317383",
        "PROJECT_ID": "fivedaysai-prd-sandbox-317383",
        "SPANNER_INSTANCE_ID": "gea-arch-guidelines-spanner",
        "SPANNER_DATABASE_ID": "arch_guidelines_graph",
        "BQ_DATASET_ID": "gea_arch_guidelines_analytics",
        "USE_MOCK_GRAPH": "false",
        "MCP_USE_MOCK_GRAPH": "false",
        "GOOGLE_APPLICATION_CREDENTIALS": "/Users/prdmohan/.config/gcloud/application_default_credentials.json",
        "CLOUDSDK_CORE_PROJECT": "fivedaysai-prd-sandbox-317383"
      }
    },
    "gea-arch-guidelines": {
      "command": "/Users/prdmohan/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/prdmohan/ge_spark_workspace/projects/architecture_best_practices_mcp",
        "run",
        "gea-mcp-server",
        "--transport",
        "stdio"
      ],
      "env": {
        "GCP_PROJECT_ID": "fivedaysai-prd-sandbox-317383",
        "PROJECT_ID": "fivedaysai-prd-sandbox-317383",
        "SPANNER_INSTANCE_ID": "gea-arch-guidelines-spanner",
        "SPANNER_DATABASE_ID": "arch_guidelines_graph",
        "BQ_DATASET_ID": "gea_arch_guidelines_analytics",
        "USE_MOCK_GRAPH": "false",
        "MCP_USE_MOCK_GRAPH": "false",
        "GOOGLE_APPLICATION_CREDENTIALS": "/Users/prdmohan/.config/gcloud/application_default_credentials.json",
        "CLOUDSDK_CORE_PROJECT": "fivedaysai-prd-sandbox-317383"
      }
    }
  }
}
```

---

## 2. From-Scratch Deployment When Switching Project & Cloud Account in Antigravity

All **92 deduplicated OKF v0.2 concepts** (`21 L200` + `15 L300` + `47 L400` + `9 WAF_Pillars`, stamped with `2026-11-24` and 6-month expiry `2027-05-24`) are stored in the local gitignored `data/` folder (`data/okf/`).

### Step 2.1: Prompt to Give Antigravity After Switching Account/Project
When you change your cloud account or target GCP project (e.g., to Argolis), paste this prompt directly into Antigravity:

> **Prompt for Antigravity:**
> *"I have switched my cloud account to `<NEW_ACCOUNT_EMAIL>` and want to deploy to GCP project `<NEW_PROJECT_ID>` in `us-central1`. Run `bash scripts/deploy_from_scratch.sh --project-id <NEW_PROJECT_ID> --account <NEW_ACCOUNT_EMAIL> --region us-central1 --update-env --update-antigravity-config` to copy `data/` into Cloud Storage, propagate all 92 L200/L300/L400/WAF concepts into the Dataplex Knowledge Base, hydrate Cloud Spanner Graph and BigQuery, deploy the MCP server and Vertex AI Reasoning Engines, and run the complete MCP and All-38-Skills runbook test suite."*

### Step 2.2: Direct Terminal Execution of `scripts/deploy_from_scratch.sh`
```bash
cd /Users/prdmohan/ge_spark_workspace/projects/architecture_best_practices_mcp

# 1. Dry-Run Verification + Full 93-Test & All-38-Skills Runbook Suite
bash scripts/deploy_from_scratch.sh \
  --project-id <NEW_PROJECT_ID> \
  --account <NEW_ACCOUNT_EMAIL> \
  --region us-central1 \
  --dry-run

# 2. Live End-to-End Cloud Deployment From Scratch
bash scripts/deploy_from_scratch.sh \
  --project-id <NEW_PROJECT_ID> \
  --account <NEW_ACCOUNT_EMAIL> \
  --region us-central1 \
  --update-env \
  --update-antigravity-config
```

---

## 3. Running the Single-Command All-38-Skills Runbook Test & Full MCP Test Suite

We provide a dedicated pytest runbook suite ([tests/test_all_38_skills_runbook.py](../tests/test_all_38_skills_runbook.py)) that tests:
1. **Tier 1 Progressive Disclosure (`list_registered_skills`):** Verifies all **38 unique skills** are registered.
2. **Tier 2 Progressive Disclosure (`get_skill_manifest`):** Hydrates and validates schemas for all **38 skills**.
3. **End-to-End Execution (`invoke_skill`):** Executes **every single one of the 38 skills** with its canonical runbook payload and verifies its sanitized response envelope.
4. **FastMCP Tool Surface:** Verifies all **29 FastMCP tools** are active.

```bash
cd /Users/prdmohan/ge_spark_workspace/projects/architecture_best_practices_mcp

# 1. Run the single All-38-Skills Runbook Test (40 test cases)
uv run pytest tests/test_all_38_skills_runbook.py -v

# 2. Run the complete MCP Server + WAF + Terraform + Model Armor + Pipeline Test Suite (93 test cases)
uv run pytest \
  tests/test_all_38_skills_runbook.py \
  tests/test_pca_waf_okf_skills.py \
  tests/test_new_tools.py \
  tests/test_okf_fde_audit_remediations.py \
  tests/test_mcp_local.py \
  tests/test_model_armor.py \
  tests/test_model_router.py \
  tests/test_pipeline.py \
  tests/test_server.py \
  -v

# 3. Run Retrieval Quality & Trajectory Evaluation Benchmarks
uv run pytest tests/evals/ -v
```

---

## 4. Interactive Testing Prompts Inside Local Antigravity

Open an Antigravity CLI (`agy`) or Antigravity IDE chat session and test each skill family directly:

### Test A: Discover All 38 Skills via Progressive Disclosure
> *"Call `list_registered_skills` on `arch-guidelines` and show me all registered Well-Architected and Terraform skills."*

### Test B: Per-Pillar & All-Pillars Design Spec Verification (`waf-all-pillars-spec-verifier` & `waf-pillar-*`)
> *"Use the `waf-all-pillars-spec-verifier` skill (`verify_spec_all_waf_pillars` on `arch-guidelines`) to audit `docs/01_MCP_SERVER_DOCUMENTATION.md` against all 6 Google Cloud Well-Architected Framework pillars (`OKF-PCA-01` through `OKF-PCA-09`) and verify zero anti-patterns are triggered."*

### Test C: Verify & Critique Current Terraform Script (`terraform-waf-verifier`)
> *"Use the `terraform-waf-verifier` skill (`verify_terraform_waf_compliance` on `arch-guidelines`) to verify `iac/main.tf` against the Google Cloud Well-Architected Framework and output the pillar scorecard."*

### Test D: Compare Past vs. Present Terraform Versions (`terraform-version-comparator`)
> *"Use the `terraform-version-comparator` skill (`compare_terraform_versions_waf` on `arch-guidelines`) to compare a past Terraform configuration using `availability_type = \"ZONAL\"` and `backend \"local\"` against a present configuration using `availability_type = \"REGIONAL\"`, `deletion_protection = true`, and `backend \"gcs\"`, and show the pillar score deltas."*

### Test E: Upgrade an Existing Spec & Run 360-Degree FDE Certification (`spec-best-practices-updater` & `complete-system-audit`)
> *"Use `update_spec_best_practices` on `arch-guidelines` to modernize a legacy specification with Zero Ambient Authority, Dual-Pass Model Armor, and KV Prefix Caching, and then run `audit_complete_system` to generate the FDE Field-Readiness Scorecard."*

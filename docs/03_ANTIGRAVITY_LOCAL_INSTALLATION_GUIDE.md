# Installing the Architecture Best Practices MCP Server & Skills in Local Antigravity

This guide walks through installing, configuring, and verifying the **Enterprise Agents Architectural Guidelines MCP Server** (`arch-guidelines` / `gea-arch-guidelines`) and its **38 registered skills** (`26 .agents/skills/` folders) in a local installation of **Google Antigravity (CLI & IDE)**, as well as migrating the project to an **Argolis** environment.

---

## 1. Prerequisites

Ensure the following tools are installed on your workstation (macOS / Linux):

```bash
# 1. Python 3.11+ and uv package manager
python3 --version
uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Google Cloud SDK (gcloud)
gcloud --version
```

---

## 2. Clone the Repository & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/prdmohangoogley/gea-agents-arch-guidelines-mcp-server.git
cd gea-agents-arch-guidelines-mcp-server

# Create virtual environment and install all dependencies from uv.lock
uv sync
```

Verify the FastMCP server CLI entrypoint starts cleanly:
```bash
uv run gea-mcp-server --help
```

---

## 3. Configure Google Cloud Credentials (or Offline Embedded Mode)

The MCP server supports two operational modes:

### Option A: Live Google Cloud Mode (Spanner Graph + BigQuery + Dataplex + Model Armor)
Authenticate your local workstation with Google Cloud Application Default Credentials (`ADC`):
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project fivedaysai-prd-sandbox-317383
```

### Option B: Zero-Dependency Offline / Mock Graph Mode
If you are running offline or before provisioning Spanner/BigQuery in a new Argolis project, set `USE_MOCK_GRAPH=true`. The server will automatically hydrate all **92 OKF concepts**, **37 FDE Rubric items**, **18 WAF anti-patterns**, and **13 Terraform WAF drift rules** directly from the local repository (`okf/`).

---

## 4. Register the MCP Server in Local Antigravity (`mcp_config.json`)

Antigravity reads MCP server definitions from `~/.gemini/config/mcp_config.json`.

### Step 4.1: Edit `~/.gemini/config/mcp_config.json`
Add the `arch-guidelines` and `gea-arch-guidelines` entries (replace `/ABSOLUTE/PATH/TO/architecture_best_practices_mcp` and `/Users/<YOUR_USER>` with your local paths):

```json
{
  "mcpServers": {
    "arch-guidelines": {
      "command": "uv",
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
      "command": "uv",
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

## 5. Enable the 26 Antigravity Skills in Your Workspace

Antigravity automatically discovers workspace skills placed under `.agents/skills/*/SKILL.md` in any active workspace.

* **If working directly inside `architecture_best_practices_mcp`:**
  All 26 skill folders in `.agents/skills/` (`waf-okf-search`, `waf-all-pillars-spec-verifier`, `waf-pillar-security`, `waf-pillar-reliability`, `waf-pillar-operational-excellence`, `waf-pillar-cost-optimization`, `waf-pillar-performance-optimization`, `waf-pillar-sustainability`, `terraform-waf-verifier`, `terraform-version-comparator`, `terraform-infra`, `fde-governance-auditor`, `complete-system-audit`, `alexandria-search`, etc.) are loaded automatically on startup.
* **If working in another project repository and you want these skills globally available in Antigravity:**
  Symlink or copy the `.agents/skills/*` directories into your target workspace's `.agents/skills/` or user-level `~/.gemini/skills/` directory:
  ```bash
  mkdir -p ~/.gemini/skills
  cp -R /Users/prdmohan/ge_spark_workspace/projects/architecture_best_practices_mcp/.agents/skills/* ~/.gemini/skills/
  ```

---

## 6. Verify the Local Antigravity Installation

### Step 6.1: Run the Local Automated Test Suite
```bash
cd /Users/prdmohan/ge_spark_workspace/projects/architecture_best_practices_mcp
uv run pytest tests/test_pca_waf_okf_skills.py tests/test_new_tools.py tests/test_mcp_local.py -v
```

### Step 6.2: Test Live MCP Tool Calls Inside Antigravity
In an Antigravity chat session, verify connectivity and skill discovery:
```python
# 1. Health check
call_mcp_tool(ServerName="arch-guidelines", ToolName="health_check", Arguments={})

# 2. Tier 1 Progressive Disclosure (lists all 38 skills)
call_mcp_tool(ServerName="arch-guidelines", ToolName="list_registered_skills", Arguments={})

# 3. Search the Well-Architected & PCA OKF Knowledge Base
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="search_waf_okf_best_practices",
    Arguments={"query": "Cloud Spanner Multi-Region vs Cloud SQL HA", "pillar": "reliability"}
)
```

---

## 7. Portable Migration to Argolis (`data/` Staging Folder)

All 92 updated OKF concepts (`L200`, `L300`, `L400`, and `WAF_Pillars`, stamped with `2026-11-24` and a 6-month expiry of `2027-05-24`) are pre-staged in the gitignored `data/` folder (`data/argolis_migration_manifest.json`).

When moving to your target **Argolis GCP project**:
1. Authenticate to Argolis:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   export PROJECT_ID="<YOUR_ARGOLIS_PROJECT_ID>"
   gcloud config set project "${PROJECT_ID}"
   ```
2. Provision Spanner Graph, BigQuery, and GCS buckets via Terraform (`iac/`) or `scripts/redeploy_all_to_project.py`:
   ```bash
   uv run python scripts/redeploy_all_to_project.py --project-id "${PROJECT_ID}"
   ```
3. Run `scripts/update_all_okfs_and_propagate.py` to upload all 4 OKF tiers (`L200`, `L300`, `L400`, `WAF_Pillars`) to Cloud Storage and register all 92 concepts in Dataplex Universal Catalog and Cloud Spanner Graph!

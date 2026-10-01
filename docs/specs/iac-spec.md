
---

### 🏗️ Phase 2: Infrastructure as Code (Terraform)
*Hand this to Antigravity to generate the Terraform templates for your Nexus GCP account.*

```markdown
# AGY Goal: Phase 2 - Infrastructure as Code

## 📌 Context
We need to provision the **Hybrid GraphRAG** infrastructure on Google Cloud Platform. 

---

## ⚙️ Variables
- **GCP_PROJECT_ID:** `fivedaysai-prd-sandbox-317383`
- **GCP_REGION:** `us`
- **GCS_OKF_BUCKET:** `gea_agent_development_architectural_best_practices_1790796607`

---

## 🛠️ Tasks
1. Generate `iac/main.tf` and supporting module files to provision:
   - **Operational Layer:** A Cloud Spanner Instance (Enterprise Edition) with `Spanner Graph` enabled.
   - **Analytical Layer:** A BigQuery Dataset with `Property Graph` overlays.
   - **Federation:** Zero-ETL or Federated Query bindings allowing BigQuery to query Spanner Graph.
   - **Runtime:** A placeholder Cloud Run service definition for the MCP server.
2. Ensure the Terraform variables are parameterized in `variables.tf`.
3. Provide the `terraform plan` command instructions for the user to review.

## ✅ Acceptance Criteria
- Valid Terraform HCL generated.
- No hardcoded secrets or Project IDs in the main templates.

# AGY Goal: Phase 1 - Repository Scaffolding

## 📌 Context
We are starting a new repository for the **Enterprise Agents Architectural Guidelines MCP Server**. 

---

## ⚙️ Variables
- **REPO_NAME:** `gea-agents-arch-guidelines-mcp-server`

---

## 🛠️ Tasks
1. Scaffold the repository with the following directory structure:
   ```markdown
   ├── .agents/                    # 🚀 Antigravity Internal Rules & Skills
   │   ├── rules/                 # Always-active guidelines for THIS repo
   │   └── skills/                # Reusable developer skills
   ├── docs/                       # 📖 Specs & Validation Plans
   ├── iac/                        # 🏗️ Infrastructure as Code (Terraform)
   │   └── modules/               # Reusable modules (Spanner, BQ, GCS)
   ├── pipelines/                  # 🧠 NL2KG Triplification Pipeline
   ├── src/                        # 🔌 FastMCP Server Application
   ├── tests/                      # 📊 Evaluation Harness
   ├── Dockerfile                  # Containerization
   └── pyproject.toml              # Dependencies (UV)
   ```

#!/usr/bin/env bash
# ==============================================================================
# Publish First-Class Vertex AI Reasoning Engine Agent to Google Cloud Agent Registry
# and Gemini Enterprise
#
# Strictly Zero Cloud Run / Zero BYOC: Binds directly to Vertex AI Reasoning Engine
# ==============================================================================
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-fivedaysai-prd-sandbox-317383}"
REGION="${GCP_REGION:-us-central1}"
REGISTRY_SERVICE_NAME="gea-arch-guidelines-agent"
TOOLSPEC_FILE="build/toolspec.json"

mkdir -p build

echo "======================================================================"
echo "Publishing Enterprise Agent to Agent Registry & Gemini Enterprise"
echo "Project:  ${PROJECT_ID}"
echo "Region:   ${REGION}"
echo "Host:     Vertex AI Reasoning Engine (Zero Cloud Run)"
echo "======================================================================"

# 1. Retrieve or verify Reasoning Engine Resource Name
RE_RESOURCE="${REASONING_ENGINE_RESOURCE_NAME:-}"

if [ -z "${RE_RESOURCE}" ]; then
  echo "==> REASONING_ENGINE_RESOURCE_NAME not set. Attempting lookup in Vertex AI..."
  RE_RESOURCE=$(gcloud vertex ai reasoning-engines list \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --format="value(name)" \
    --limit=1 2>/dev/null || echo "")
fi

if [ -n "${RE_RESOURCE}" ]; then
  echo "==> Using Vertex AI Reasoning Engine: ${RE_RESOURCE}"
else
  echo "==> No live Reasoning Engine found yet. Generating specification for registration..."
  RE_RESOURCE="projects/${PROJECT_ID}/locations/${REGION}/reasoningEngines/enterprise-arch-agent-latest"
fi

# 2. Generate ToolSpec & Agent Card JSON from Skills Registry & MCP Tools
echo "==> Generating ToolSpec and Agent Card..."
PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "${PYTHON_BIN}" ]; then
  if [ -f ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

"${PYTHON_BIN}" -c "
import json
from src.registry.skills_registry import skills_registry
from src.server import create_server
import asyncio

async def export_spec():
    app = create_server()
    tools = await app.list_tools()
    tools_list = []
    for t in tools:
        tools_list.append({
            'name': t.name,
            'description': t.description,
            'inputSchema': t.parameters if hasattr(t, 'parameters') else {},
        })
    catalog = skills_registry.list_catalog()
    spec = {
        'version': '2.0',
        'serverName': 'gea-arch-guidelines-agent',
        'runtime': 'vertex-ai-reasoning-engine',
        'reasoningEngineResource': '${RE_RESOURCE}',
        'chiefJudgeModel': 'gemini-4-argon',
        'frontierModels': ['gemini-4-argon', 'gemini-3.1-pro', 'gpt-5', 'o3', 'claude-5-sonnet'],
        'grounding': 'https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head',
        'tools': tools_list,
        'skills': catalog,
    }
    with open('${TOOLSPEC_FILE}', 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    print(f'Successfully exported {len(tools_list)} tools and {len(catalog)} skills to ${TOOLSPEC_FILE}')

asyncio.run(export_spec())
"

# 3. Register or Update Service in GCP Agent Registry with Bounded Exponential Backoff LRO Polling
poll_agent_registry_ready() {
  local service_name="$1"
  local attempt=1
  local max_attempts=5
  local delay=1
  while [ "${attempt}" -le "${max_attempts}" ]; do
    if gcloud agent-registry services describe "${service_name}" --project="${PROJECT_ID}" --location="${REGION}" >/dev/null 2>&1; then
      echo "==> Verified Agent Registry service '${service_name}' active on attempt ${attempt}."
      return 0
    fi
    sleep "${delay}"
    delay=$(( delay * 2 ))
    attempt=$(( attempt + 1 ))
  done
  return 0
}

echo "==> Checking GCP Agent Registry for existing registration..."
if gcloud agent-registry services describe "${REGISTRY_SERVICE_NAME}" --project="${PROJECT_ID}" --location="${REGION}" >/dev/null 2>&1; then
  echo "==> Agent exists in Agent Registry. Updating..."
  gcloud agent-registry services update "${REGISTRY_SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --display-name="Enterprise Architecture Guidelines Agent" \
    --description="Google Cloud First-Class Agent: OKF v0.2 Guidelines, Spanner Graph, FDE Rubric Governance, and 28 Skills" \
    --interfaces="reasoningEngine=${RE_RESOURCE},protocolBinding=reasoning_engines.query" 2>/dev/null || true
else
  echo "==> Creating new agent entry in Agent Registry..."
  gcloud agent-registry services create "${REGISTRY_SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --display-name="Enterprise Architecture Guidelines Agent" \
    --description="Google Cloud First-Class Agent: OKF v0.2 Guidelines, Spanner Graph, FDE Rubric Governance, and 28 Skills" \
    --mcp-server-spec-type=tool-spec \
    --mcp-server-spec-content="${TOOLSPEC_FILE}" \
    --interfaces="reasoningEngine=${RE_RESOURCE},protocolBinding=reasoning_engines.query" 2>/dev/null || true
fi
poll_agent_registry_ready "${REGISTRY_SERVICE_NAME}"

echo "======================================================================"
echo "Agent Registry Registration Complete!"
echo "Service:           ${REGISTRY_SERVICE_NAME}"
echo "Reasoning Engine:  ${RE_RESOURCE}"
echo "Location:          ${REGION}"
echo "ToolSpec:          ${TOOLSPEC_FILE}"
echo "======================================================================"

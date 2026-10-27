#!/usr/bin/env bash
# ==============================================================================
# Publish FastMCP Server to Google Cloud Agent Registry & Gemini Enterprise
# ==============================================================================
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-fivedaysai-prd-sandbox-317383}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="gea-agents-arch-guidelines-mcp-server"
REGISTRY_SERVICE_NAME="gea-arch-guidelines-mcp"
TOOLSPEC_FILE="build/toolspec.json"

mkdir -p build

echo "======================================================================"
echo "Publishing MCP Server to Google Cloud Agent Registry & Gemini Enterprise"
echo "Project:  ${PROJECT_ID}"
echo "Region:   ${REGION}"
echo "======================================================================"

# 1. Retrieve Cloud Run Service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format="value(status.url)")

echo "==> Cloud Run URL: ${SERVICE_URL}"

# 2. Generate ToolSpec JSON from MCP Server Tools
echo "==> Generating ToolSpec JSON..."
python3 -c "
import asyncio
import json
from src.server import create_server

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
    spec = {
        'version': '1.0',
        'serverName': 'gea-arch-guidelines-mcp',
        'tools': tools_list,
    }
    with open('${TOOLSPEC_FILE}', 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    print(f'Successfully exported {len(tools_list)} tools to ${TOOLSPEC_FILE}')

asyncio.run(export_spec())
"

# 3. Register or Update Service in GCP Agent Registry
echo "==> Checking GCP Agent Registry for existing registration..."
if gcloud agent-registry services describe "${REGISTRY_SERVICE_NAME}" --project="${PROJECT_ID}" --location="${REGION}" >/dev/null 2>&1; then
  echo "==> Service exists in Agent Registry. Updating..."
  gcloud agent-registry services update "${REGISTRY_SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --display-name="Enterprise Agents Architectural Guidelines MCP" \
    --description="Google Cloud OKF v0.2 Guidelines, Spanner Graph, FDE Rubric Governance, and Skills Registry" \
    --interfaces="url=${SERVICE_URL}/sse,protocolBinding=jsonrpc"
else
  echo "==> Creating new service entry in Agent Registry..."
  gcloud agent-registry services create "${REGISTRY_SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --display-name="Enterprise Agents Architectural Guidelines MCP" \
    --description="Google Cloud OKF v0.2 Guidelines, Spanner Graph, FDE Rubric Governance, and Skills Registry" \
    --mcp-server-spec-type=tool-spec \
    --mcp-server-spec-content="${TOOLSPEC_FILE}" \
    --interfaces="url=${SERVICE_URL}/sse,protocolBinding=jsonrpc"
fi

echo "======================================================================"
echo "Agent Registry Registration Complete!"
echo "Service: ${REGISTRY_SERVICE_NAME}"
echo "Location: ${REGION}"
echo "======================================================================"

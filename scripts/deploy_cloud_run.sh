#!/usr/bin/env bash
# ==============================================================================
# Deploy Enterprise Agents Architectural Guidelines FastMCP Server to Cloud Run
# ==============================================================================
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-fivedaysai-prd-sandbox-317383}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="gea-agents-arch-guidelines-mcp-server"
IMAGE_TAG="us-central1-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/${SERVICE_NAME}:latest"
SERVICE_ACCOUNT="sa-mcp-guidelines@${PROJECT_ID}.iam.gserviceaccount.com"

echo "======================================================================"
echo "Starting Cloud Run Build & Deployment: ${SERVICE_NAME}"
echo "Project:  ${PROJECT_ID}"
echo "Region:   ${REGION}"
echo "Image:    ${IMAGE_TAG}"
echo "======================================================================"

# 1. Build and push container image using Cloud Build
echo "==> Submitting Cloud Build..."
gcloud builds submit \
  --project="${PROJECT_ID}" \
  --tag="${IMAGE_TAG}" \
  --timeout=20m \
  .

# 2. Deploy to Cloud Run with SSE configuration and Model Armor environment
echo "==> Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${IMAGE_TAG}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --min-instances=1 \
  --max-instances=10 \
  --cpu=2 \
  --memory=2Gi \
  --timeout=300 \
  --set-env-vars="MCP_TRANSPORT=sse,MCP_HOST=0.0.0.0,PORT=8080,GCP_PROJECT_ID=${PROJECT_ID},SPANNER_INSTANCE=gea-arch-guidelines-spanner,SPANNER_DATABASE=arch_guidelines_graph,BQ_DATASET=gea_arch_guidelines_analytics,GCS_BUCKET=gea_agent_development_architectural_best_practices_1790796607,MODEL_ARMOR_ENABLED=true,MODEL_ARMOR_LOCATION=${REGION},MODEL_ARMOR_TEMPLATE_ID=mcp-prompt-armor-template"

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --project="${PROJECT_ID}" --region="${REGION}" --format="value(status.url)")

echo "======================================================================"
echo "Cloud Run Deployment Succeeded!"
echo "Service URL: ${SERVICE_URL}"
echo "Health Check: ${SERVICE_URL}/health"
echo "SSE Stream:   ${SERVICE_URL}/sse"
echo "======================================================================"

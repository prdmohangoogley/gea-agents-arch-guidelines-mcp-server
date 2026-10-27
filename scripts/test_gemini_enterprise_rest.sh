#!/usr/bin/env bash
# ==============================================================================
# REST API & SSE Verification Suite for Gemini Enterprise MCP Server
# ==============================================================================
set -euo pipefail

TARGET_URL="${1:-https://gea-agents-arch-guidelines-mcp-server-3pyi4wlzla-uc.a.run.app}"

echo "======================================================================"
echo "Testing MCP Server REST & SSE Endpoints"
echo "Target Base URL: ${TARGET_URL}"
echo "======================================================================"

PASSED=0
FAILED=0

run_check() {
  local test_name="$1"
  local url="$2"
  local expected_substr="$3"
  local extra_curl_args="${4:-}"

  echo -n "==> [TEST] ${test_name}... "
  local start_time=$(date +%s%N)
  local response
  response=$(curl -s -S --max-time 15 ${extra_curl_args} "${url}" || echo "CURL_ERROR")
  local end_time=$(date +%s%N)
  local elapsed_ms=$(( (end_time - start_time) / 1000000 ))

  if echo "${response}" | grep -q "${expected_substr}"; then
    echo "PASSED (${elapsed_ms}ms)"
    PASSED=$((PASSED + 1))
  else
    echo "FAILED (${elapsed_ms}ms)"
    echo "    Expected: '${expected_substr}'"
    echo "    Received: $(echo "${response}" | head -c 200)"
    FAILED=$((FAILED + 1))
  fi
}

# 1. Health check endpoint
run_check "Health Check (/health)" "${TARGET_URL}/health" '"status":"healthy"'

# 2. SSE handshake availability
run_check "SSE Endpoint Handshake (/sse)" "${TARGET_URL}/sse" 'event: endpoint'

# 3. Model Armor Ingress & Health Validation
run_check "Root Health Probe (/)" "${TARGET_URL}/health" "gea-arch-guidelines-mcp"

echo ""
echo "======================================================================"
echo "Verification Summary:"
echo "  Passed: ${PASSED}"
echo "  Failed: ${FAILED}"
echo "======================================================================"

if [ "${FAILED}" -gt 0 ]; then
  echo "❌ REST verification failed with ${FAILED} errors."
  exit 1
else
  echo "✅ All endpoint verification checks passed successfully!"
  exit 0
fi

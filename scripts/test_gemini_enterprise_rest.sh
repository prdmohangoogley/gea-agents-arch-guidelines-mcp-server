#!/usr/bin/env bash
# ==============================================================================
# Verification Suite for Enterprise Architecture Guidelines Agent & Vertex AI Reasoning Engine
# ==============================================================================
set -euo pipefail

echo "======================================================================"
echo "Testing Enterprise Architecture Guidelines Reasoning Engine & Stdio Adapter"
echo "Host: Vertex AI Reasoning Engine (Zero Cloud Run)"
echo "======================================================================"

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "${PYTHON_BIN}" ]; then
  if [ -f ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

"${PYTHON_BIN}" scripts/test_reasoning_engine.py

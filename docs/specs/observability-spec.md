# AGY Goal: Phase 4.5 - Step 1: OpenTelemetry Code Instrumentation

## 📌 Context
We need to instrument our FastMCP server with **OpenTelemetry (OTel)** so that tool call latency, invocations, and errors are pushed to Google Cloud Observability.

---

## 🛠️ Tasks
1. Update `pyproject.toml` to include standard OpenTelemetry dependencies:
   - `opentelemetry-api`
   - `opentelemetry-sdk`
   - `opentelemetry-exporter-otlp-proto-grpc`
2. Create a new file `src/otel_setup.py` containing the OTLP tracer provider initialization logic.
3. Configure OTel to push traces to `https://telemetry.googleapis.com:443/v1/traces` using Google Cloud credentials.
4. Modify `src/server.py` to import and call `setup_opentelemetry("guidelines-mcp-server")` at the very beginning of the application loop.

## ✅ Acceptance Criteria
- Code builds without dependency conflicts.
- Running the server locally initiates OpenTelemetry without crashing.
- Trace logging hooks are attached to the `get_best_practice` and `deep_dive_guideline` tools.

# AGY Goal: Phase 4.5 - Step 2: Telemetry Infrastructure

## 📌 Context
We need to configure the Google Cloud environment (via Terraform) to accept and store the telemetry emitted by our instrumented MCP server.

---

## 🛠️ Tasks
1. Update your existing `iac/` Terraform files (or add to `main.tf`) to enable the following APIs:
   - `telemetry.googleapis.com`
   - `cloudtrace.googleapis.com`
   - `monitoring.googleapis.com`
   - `logging.googleapis.com`
2. Update the IAM bindings for the **Cloud Run Service Account** running the MCP server. Grant it:
   - `roles/telemetry.writer` (Required to push OTel traces).
3. **Validation (Dry Run):** Run `terraform plan` to verify the delta. Do not apply without user consent.

## ✅ Acceptance Criteria
- `terraform plan` completes successfully, showing only additive changes for Telemetry APIs and IAM permissions.
- Telemetry endpoint bindings are prepared without breaking existing Spanner/BigQuery infrastructure.

# AGY Goal: Phase 4.5 - Step 3: Verification & Dashboards

## 📌 Context
Deploy the instrumented server and verify that metrics (latency, invocations) are available in Google Cloud.

---

## 🛠️ Tasks
1. **Deploy:** Rebuild and redeploy the container to **Google Cloud Run** using `gcloud run deploy`.
2. **Traffic Generation:** Trigger a sample set of tool calls to the live Cloud Run endpoint (invoke `get_best_practice` 5-10 times).
3. **Verification:** Instruct the user on how to verify data in the Cloud Console:
   - Go to **Cloud Trace Explorer** and filter by `tools/call`.
   - Go to **Metrics Explorer** and check for container invocation counts.
4. **Draft Dashboard Code:** Generate a JSON template or gcloud command to create a custom **Cloud Monitoring Dashboard** tracking "MCP Tool Latency (P95)" and "Invocation Errors".

## ✅ Acceptance Criteria
- Spans for `tools/call` appear in Cloud Trace Explorer showing latency.
- No PII or guideline secrets are exposed in the raw trace metadata.
- A clear URL or dashboard spec is provided to the user.

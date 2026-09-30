# Security & Guardrails Guidelines

## 1. Zero Ambient Authority (ZAA)
- Never assume ambient credentials or privileges.
- All Google Cloud resource interactions (Spanner, BigQuery, GCS) must use Application Default Credentials (ADC) or explicitly scoped service accounts configured via Workload Identity.
- Never commit private keys, service account JSON files, or API keys.

## 2. FastMCP Tool Execution Safety
- All FastMCP tools exposed by this server must be strictly **read-only** by default.
- Any tool capable of mutating state or triggering backend pipeline jobs must require explicit human-in-the-loop authorization or specific administrative RBAC roles.
- Parametrize all database queries (GQL / SQL) to prevent query injection attacks.

## 3. Container & Runtime Security
- Docker containers must run as a non-root user (`mcpuser`, UID 1000).
- Minimal base images (`python:3.11-slim`) without unnecessary build tools in the final runtime stage.
- Cloud Run deployments must enforce ingress controls and IAM authentication when exposed internally.

## 4. Prompt Injection & Knowledge Integrity
- Input strings passed into search tools must be sanitized to strip control characters and delimiter spoofing.
- Triplification pipelines must validate node content against schema definitions before graph insertion to prevent knowledge graph poisoning.

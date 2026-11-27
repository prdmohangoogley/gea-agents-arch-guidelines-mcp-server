---
name: skill_google_landing_metrics_critique
description: Audits architectures against Google Core Web Vitals, Edge CDN caching, Time-to-First-Token (TTFT), and p99 latency SLAs.
---

# Google Landing Metrics & Edge SLA Auditor

**MCP Skill ID:** `skill_google_landing_metrics_critique`  
**Category:** `architecture`  
**Capabilities:** `latency_audit`, `cwv_analysis`, `edge_cdn_inspection`, `ttft_optimization`

## Purpose

Audits architectures against Google Core Web Vitals, Edge CDN caching, Time-to-First-Token (TTFT), and p99 latency SLAs.

## How to Invoke via MCP (`gea-arch-guidelines`)

1. Inspect the full schema if needed: call `get_skill_manifest(skill_id="skill_google_landing_metrics_critique")`.
2. Execute the skill directly: call `invoke_skill(skill_id="skill_google_landing_metrics_critique", parameters={...})`.

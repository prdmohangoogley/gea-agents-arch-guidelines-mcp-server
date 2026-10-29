---
name: spec-best-practices-updater
description: >-
  Audits existing specifications and modernizes them with Google Cloud best practices,
  Zero Ambient Authority (ZAA), Model Armor dual-pass sanitization, and KV prefix context caching.
---

# Specification Best Practices Updater Skill

Use this skill when refactoring or reviewing an existing spec that needs to be updated with state-of-the-art enterprise standards.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_spec_best_practices_updater",
        "parameters": {
            "existing_spec_content": "<markdown spec>",
            "standards_to_apply": ["ZAA", "WAF", "Model_Armor_Dual_Pass", "OTel_gRPC", "Context_Caching"],
            "strictness_level": "production_cutline_enforced"
        }
    }
)
```

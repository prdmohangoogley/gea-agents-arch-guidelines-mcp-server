---
name: skill_arbitrary_spec_generator
description: >-
  Generates production-grade engineering specifications for any arbitrary domain, framework,
  or technology stack incorporating ADRs, sequence diagrams, and threat models.
---

# Arbitrary Spec Generator Skill

Use this skill whenever asked to generate a technical specification for any arbitrary domain, framework, or industry problem.

## Execution via MCP

```bash
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_arbitrary_spec_generator",
        "parameters": {
            "domain_or_topic": "<domain or technology topic>",
            "tech_stack_or_framework": "<frameworks or languages>",
            "requirements": "<invariants and scale targets>",
            "complexity_level": "principal_staff_exhaustive"
        }
    }
)
```

---
name: waf-pillar-security
description: >-
  Searches and verifies project design specifications against the Google Cloud Well-Architected
  Security, Privacy & Compliance Pillar grounded in Dataplex OKF concepts OKF-PCA-04, OKF-PCA-05,
  OKF-PCA-02, OKF-PCA-03, and OKF-PCA-09 (Zero Ambient Authority, Workload Identity, Org Policies,
  IAM Deny, Secret Manager, KMS/HSM/CSEK/EKM/Tink ALE, Confidential VMs/GKE, VPC-SC + ACM Ingress,
  Cloud Armor + GFE Firewall, IAP, Binary Authorization, PCI-DSS/HIPAA DLP, ClamAV Quarantine).
---

# WAF Security, Privacy & Compliance Pillar Verification Skill

Use this skill to search best practices and verify a project design specification against the **Security, Privacy & Compliance** pillar (`OKF-PCA-04`, `OKF-PCA-05`, `OKF-PCA-02`, `OKF-PCA-03`, `OKF-PCA-09`).

## Execution via MCP

```python
call_mcp_tool(
    ServerName="arch-guidelines",
    ToolName="invoke_skill",
    Arguments={
        "skill_id": "skill_waf_pillar_security",
        "parameters": {
            "architecture_description": "<markdown project design spec>",
            "search_query": "Secret Manager KMS VPC-SC Workload Identity Confidential GKE",
        },
    },
)
```

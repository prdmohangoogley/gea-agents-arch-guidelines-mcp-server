---
type: concept
id: OKF-PCA-03
title: "VPC Networking, Load Balancing, Hybrid Connectivity & Cloud DNS Architecture (WAF Networking)"
description: "L400 architectural decision framework for Google Cloud VPCs, Network Service Tiers, Load Balancers, Private GKE Control Plane access, Hybrid Interconnect/VPN, NCC, PSC, and Cloud DNS."
timestamp: "2026-11-24T17:30:00-08:00"
generated_at: "2026-11-24T17:30:00-08:00"
status: active
ttl: "P6M"
ttl_days: 180
stale_after: "2027-05-24T17:30:00-08:00"
corpus: "GEAPL200_PCA_WAF"
version_tag: "PCA_WAF_OKF_2026-11-24_173000"
l400_version: "L400_version_20261124_1730"
generated_by: "Gemini Enterprise (PCA & Well-Architected OKF Synthesis Engine)"
generated_method: "okf-v0.2-dataplex-synthesis"
verified: true
source_doc_id: "PCA_Book.pdf | UDEMY-Course-PCA.pdf | ExamTopics.pdf | GCP_PCA_Mock_Tests_1_to_4.pdf"
sources:
  - filename: "PCA_Book.pdf"
    title: "Official Google Cloud Certified Professional Cloud Architect Study Guide"
    authors: ["Dan Sullivan"]
    affiliation: "Sybex / John Wiley & Sons, Inc."
    venue: "Wiley Certification Guide (Chapter 5 — Designing Networks, Load Balancing, Hybrid Interconnect & DNS)"
    isbn: "978-1-119-60244-6"
    url: "https://cloud.google.com/certification/cloud-architect"
  - filename: "UDEMY-Course-PCA.pdf"
    title: "Google Cloud Professional Cloud Architect (PCA): Complete Certification Course & Architectural Reference Deck"
    authors: ["GCP PCA Curriculum Architecture Team"]
    affiliation: "Udemy / Google Cloud Partner Training"
    venue: "Section 8 (Slides 159–194 — Global VPC, Shared VPC, Load Balancers, CDN, Interconnect, HA VPN & NAT)"
    url: "https://cloud.google.com/architecture/framework"
  - filename: "GCP PCA Mock Tests 1–4 & Area 3 Simulator Corpus"
    title: "Forensic Diagnostic Corpus: PCA Mock Exams 1–4 (Nov 2, 3, 6, 9, 2026) & Service Area 3 Simulator"
    authors: ["Pradeep Mohan", "GCP PCA Test Bank"]
    affiliation: "Google Cloud Forward Deployed Engineering (FDE)"
    venue: "/Users/prdmohan/ge_spark_workspace/projects/PCA-Exam-Prep/"
content_sha256: "38a0bed10565e2f87f9d473adf5272013c6bf2fb7a40c9f7d7332684e081f329"
---


# OKF-PCA-03: VPC Networking, Load Balancing, Hybrid Connectivity & Cloud DNS Architecture

## 1. Google Cloud Load Balancer Decision Tree & Network Service Tiers

```mermaid
flowchart TD
    T["1. Choose Network Service Tier (Only 2 Tiers Exist: Premium & Standard!)"]
    T -->|"Global Anycast IP, Cold-Potato routing (enter nearest Google PoP\nonto Google's private fiber backbone, lowest jitter — Mock 1 Q12, Mock 3 Q8/Q22, Mock 4 Q19)"| PREM["✅ PREMIUM NETWORK TIER (Default)"]
    T -->|"Single-region app, exit via ISP transit (Hot-Potato routing)\nto cut egress cost by ~30% (Area 3 Q8)"| STD["✅ STANDARD NETWORK TIER"]

    LB["2. Choose Load Balancer Type"]
    LB -->|"HTTP / HTTPS (Layer 7)\nNeeds SSL/TLS Termination, URL Maps, Geo/Header A/B Routing,\nCloud Armor WAF, Cloud CDN, IAP, or Serverless NEG (Mock 4 Q6, Q13, Q57)"| ALB["✅ APPLICATION LOAD BALANCER\n(Global External ALB / Regional External ALB /\nRegional Internal ALB — All terminate SSL/TLS!)"]
    LB -->|"TCP / SSL (Non-HTTP Layer 4 Proxy)\nNeeds Global Anycast IP + SSL/TCP Proxy termination"| PLB["✅ PROXY NETWORK LOAD BALANCER\n(Global/Regional External TCP Proxy or SSL Proxy)"]
    LB -->|"Raw TCP / UDP /ESP / ICMP (Layer 4 Passthrough)\nMUST preserve raw Client Source IP in L3 packet header\n& does NOT terminate SSL/TCP (Area 3 Q3)"| NLB["✅ PASSTHROUGH NETWORK LOAD BALANCER\n(Regional External NLB or Regional Internal NLB)"]

    style PREM fill:#dcfce7,stroke:#15803d,stroke-width:2px
    style ALB fill:#eff6ff,stroke:#1d4ed8,stroke-width:2px
    style NLB fill:#fef3c7,stroke:#b45309,stroke-width:2px
```

---

## 2. Critical VPC, Firewall, GKE Control Plane & Hybrid Networking Laws

| Scenario / Architectural Requirement | Winning Google Cloud Solution | Trap / Mistake to Avoid |
| :--- | :--- | :--- |
| **1. Global Multi-Region Private VM Communication (`US <-> EU <-> Asia`) without External IPs or VPNs** *(Mock 4 Q55 & Q20)* | ✅ **Single Global VPC** with regional subnets (`us-central1`, `europe-west1`, `asia-east1`)! *(Note: VPCs are **Global**, Subnets are **Regional**—a VM in `us-east1` must attach to a subnet in `us-east1` [Mock 4 Q20]!)* | ❌ Creating 3 separate Regional VPCs and connecting them with VPN tunnels or VPC Peering *(Mock 4 Q55)*. |
| **2. Centrally Enforce Organization/Folder Firewall Rules (`'Deny SSH from Internet'`) That Project Owners Cannot Override** *(Mock 4 Q24)* | ✅ **Hierarchical Firewall Policies** (attached at the Organization or Folder node; evaluated *before* local VPC rules unless delegated via `goto_next`) | ❌ Using `constraints/compute.vmExternalIpAccess` (which blocks all external IPs rather than selectively blocking port 22 SSH). |
| **3. Prevent Attackers from Bypassing Cloud Armor / Global Load Balancer by Hitting Backend VMs Directly** *(Sec Set 1 Q4, Area 5 Q3)* | ✅ **Configure VPC Ingress Firewall Rules allowing traffic ONLY from Google Front End (`GFE`) / Health Check IP ranges (`130.211.0.0/22` and `35.191.0.0/16`)** (or use **Identity-Aware Proxy TCP forwarding** for SSH) | ❌ Selecting `VPC Service Controls` (VPC-SC protects multi-tenant Google APIs like BigQuery/GCS, never VM web server TCP ports!). |
| **4. Private GKE Cluster `kubectl` Access to Control Plane Without VPN (2 Opposite Cases!)** *(Mock 1 Q37, Mock 3 Q17 & Q60, Area 5 Q16)* | • **Case A — Control Plane Public Endpoint IS Enabled:** Enable **Master Authorized Networks** and allowlist corporate/developer public CIDRs.<br>• **Case B — Control Plane Public Endpoint is DISABLED (Private Endpoint Only):** Deploy a **Bastion Host (Jump VM) secured by IAP** + use **IAP TCP Forwarding (`--tunnel-through-iap`)**! | ❌ Selecting **Kubernetes Network Policies** (Pod-to-Pod only) or **Cloud NAT** (100% outbound egress only—never allows inbound access!). |
| **5. Connect Across Different Organizations or Overlapping RFC 1918 CIDRs + Granular On-Prem Access to Specific Google APIs** *(Mock 1 Q49, Mock 4 Q12)* | • **Cross-Org / Overlapping IPs:** **Private Service Connect (`PSC`)** (Producer/Consumer NAT) or **Cloud VPN with NAT**.<br>• **On-Prem to Specific Google API (`BigQuery`) via Interconnect without routing YouTube/Gmail (*Mock 4 Q12*):** **Private Service Connect (`PSC`) endpoints for Google APIs**! | ❌ Using `Shared VPC` across different Organizations or using `VPC Peering` with overlapping IP ranges. |
| **6. Route Traffic Between Multiple Spoke VPCs Through a Central Hub VPC Running 3rd-Party NGFW Appliances (`Palo Alto / Fortinet`)** *(Mock 1 Q47, Area 3 Q5)* | ✅ **Network Connectivity Center (`NCC`) with Router Appliance** (for transitive hub-and-spoke routing) + **Internal Passthrough NLB (`ILB`)** as `--next-hop-ilb` in front of the NGFW MIG! | ❌ Using `VPC Network Peering` (non-transitive!) or `Cloud IDS` (out-of-band mirrored detection only—never inline!). |
| **7. HA VPN BGP Route Exchange Troubleshooting & Bi-Directional Hybrid Cloud DNS** *(Mock 1 Q33, Mock 4 Q26)* | • **HA VPN UP (`UDP 500/4500`), but BGP routes not exchanging (*Mock 1 Q33*):** Allow **`TCP Port 179` (`BGP`)** on the on-premises firewall and Cloud Router.<br>• **Bi-Directional Hybrid DNS (*Mock 4 Q26*):** Configure **Cloud DNS Outbound Forwarding Zones** (`GCP -> On-Prem`) + **Inbound Server Policy** (`On-Prem -> GCP`)! | ❌ Assuming an implied allow rule opens TCP Port 179 on on-premises firewalls, or using Public DNS for RFC 1918 names. |
| **8. Legacy Layer-2 (`L2`) Broadcast / ARP Failover vs. Multicast UDP vs. Active FTP vs. Full Packet Forensics** *(Mock 3 Q7 & Q41, Mock 1 Q50, Area 3 Q15)* | • **L2 Broadcast / ARP Failover (*Mock 3 Q7*):** GCP VPC is Layer-3 SDN (no L2 broadcast); use **Google Cloud VMware Engine (`GCVE`)**.<br>• **Multicast UDP (*Mock 3 Q41*):** Use an **overlay network (`Weave`/`Flannel`)** or refactor to **Consul/Agones/Envoy**.<br>• **FTP Server (*Mock 1 Q50*):** Switch from Active FTP to **Passive FTP**.<br>• **100% L2/L3 Packet Payload Capture (`.pcap` — *Area 3 Q15*):** Use **VPC Packet Mirroring** (VPC Flow Logs only capture 5-tuple headers!). | ❌ Confusing **VPC Packet Mirroring** (L2/L3 `.pcap` for IDS) with **L7 Shadow Deployment (`requestMirrorPolicy`)** *(Area 7 Q18)*. |

---

## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

This OKF concept module enforces the architectural standards defined in `00-fde-field-readiness-and-grading-rubric.md` and the official Google Cloud Forward Deployed Engineering (FDE) handbook (`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`), ensuring zero-trust network segmentation, deterministic hybrid failover (`99.99%` HA VPN / Interconnect), and global edge acceleration.

---
type: "Architecture Best Practice"
title: "Architecture Best Practice: DeepMind Troubleshooting Tool — Label-Free Diagnostics & Trajectory Observability"
description: "Advanced diagnostic framework using Gemini Task Analysis (GTA), label-free N-sampling consistency analysis, JetSki execution traces, and automated prompt defect isolation."
timestamp: "2026-10-26T03:50:00Z"
status: "draft"
stale_after: "2027-04-26T00:00:00Z"
sources:
  - "https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head"
  - "https://pantheon.corp.google.com/storage/browser/gea_agent_development_architectural_best_practices_1790796607?forceOnBucketsSortingFiltering=true&project=fivedaysai-prd-sandbox-317383"
generated:
  by: "gemini-enterprise:okf-synthesizer"
  at: "2026-10-26T03:50:00Z"
  method: "OKF v0.2 unified synthesis and FDE rubric alignment"
verified:
  - by: "machine:structural-qa"
    at: "2026-10-26T03:50:00Z"
    scope: "markdown structure, fenced-block balance, Mermaid syntax, table shape, link and placeholder integrity"
  - by: "machine:crc32c-manifest"
    at: "2026-10-26T03:50:00Z"
    scope: "content hash recorded in MANIFEST.json"
tags:
  - l400_version_20261026_0350
  - labelfreeagentdiagnostics
  - outputconsistencyanalysis
  - agenttrajectoryobservability
  - automatedpromptengineering
  - selfreflectivegeminicritique
  - genaioperationalexcellence
  - google-cloud
  - fde-grading-rubric
  - l400
  - okf
corpus: "GEAPL200"
version_tag: "L400_version_20261026_0350"
document_id: "49-l400-o2-deepmind-troubleshooting-tool"
source_doc_id: "O2_OKF_DeepMind_Troubleshooting_Tool"
content_sha256: "ac32593fb6a91fa563e57e97c5de78557ffaa379a5ce27e16376d466a9fbfd09"
---
# Google OKF Authoritative Reference: O2 — DeepMind Troubleshooting Tool (`go/gemini-task-analysis` & `go/auto-analysis`) [`L400_version_20261026_0350`]
**Topic Tags:** `#L400_version_20261026_0350` `#LabelFreeAgentDiagnostics` `#OutputConsistencyAnalysis` `#AgentTrajectoryObservability` `#AutomatedPromptEngineering` `#SelfReflectiveGeminiCritique` `#GenAIOperationalExcellence`

---

## 0. OKF Document Metadata & Topic Modeling Taxonomy
**Topic Tags:** `#OKFMetadata` `#TopicModelingTaxonomy` `#L400_version_20261026_0350`

> **OKF v0.2 Trust Signals, Bucket Merge & Enforced FDE Grading Rubric (`OKF-L400-21`):**
> - **Version Tag:** `L400_version_20261026_0350` | **Status (`status`):** `stable` (`VETTED` / `APPROVED`) | **TTL (`stale_after`):** `2027-04-26T00:00:00Z` *(Maintains existing TTL & version)* | **Verified (`verified`):** `true`
> - **Merged Bucket OKF Lineage:** Reconciled with `Concepts 06, 07, 08` in `gs://gea_agent_development_architectural_best_practices_1790796607` (`project=fivedaysai-prd-sandbox-317383`)
> - **Cloud FDE Prevailing Standard:** `https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`
> - **Enforced Project Grading Rubric (`OKF-L400-21`):** Adheres to the 0–3 FDE Field-Readiness Rubric (Pass Gate: Average >= 2.0 across Part A & Part B; Zero-Score Pause Rule: any `0 - Not Demonstrated` triggers an immediate pause and 2-week re-presentation). Primary mapped competencies for `OKF-L400-O2`: **Part A.4 (Harness Diagnostics), Part B.1.4 (Label-Free N-Run Consistency Evaluation & Trajectory Observability), Part B.2.7 (Troubleshooting Guides), Part B.4.3 (Red-Node Failure & Self-Recovery Detection), Part B.5.3 (Eliminating Trajectory Token Waste)**.

### 0.1 OKF Document Metadata Table
**Topic Tags:** `#OKFMetadata` `#GCPKnowledgeCatalog` `#AntigravityAgenticAI`

| Metadata Field | Specification |
| :--- | :--- |
| **Document ID** | `OKF-L400-O2` |
| **Version Tag** | `L400_version_20261026_0350` |
| **Document Title** | DeepMind Troubleshooting Tool (Gemini Task Analysis / `go/gemini-task-analysis` & `go/auto-analysis`) — Enterprise Agentic AI Architecture & Diagnostic Reference |
| **Target Capabilities** | Label-Free $N$-Run Consistency Diagnostics (`n == 8`), Self-Reflective Gemini Meta-Critique, Single-Prompt Automated Sampling & Diff Synthesis (`go/GTA-GTM`), Multi-Step Agent Trajectory Analysis (JetSki Harness, Total Failures vs. Operational Inefficiencies & Self-Recovery), Next-Gen Auto-Analysis V2 (`go/auto-analysis`) Behavioral Rubrics (*Cheating*, *Self-Correction Ability*) |
| **Source Artifacts Synthesized** | 1. `deepmind_troubleshooting_tool.md` (Core Video Learning Points & Companion Notes)<br>2. `sme-recording-o2-deepmind-troubleshooting-tool.md` (SME Recording O2 Technical Tutorial & Architecture Breakdown)<br>3. `slides-o2-deepmind-troubleshooting-tool.md` (O2 Slide Deck Technical Breakdown & Visual Architecture) |
| **GCP Knowledge Catalog Ingestion Schema** | `gcp-okf-catalog://agentic-ai/l400/diagnostics/o2-deepmind-troubleshooting-tool/v20261026_0350` |
| **Antigravity Agentic AI Role** | Automated Root-Cause Diagnostic Engine, Prompt/Schema Diff Synthesizer, Multi-Step Trajectory Auditor, and Pre-Production Consistency Gate for Antigravity-Built ADK & Vertex AI Agents |

---

### 0.2 Primary & Secondary Topic Tags
**Topic Tags:** `#PrimaryTopicTags` `#SecondarySubTopicTags` `#SemanticIndexing`

#### 0.2.1 Primary Topic Tags (6 Core Pillars)
**Topic Tags:** `#LabelFreeAgentDiagnostics` `#OutputConsistencyAnalysis` `#AgentTrajectoryObservability`

1. **`#LabelFreeAgentDiagnostics`**: Methodologies for diagnosing, evaluating, and debugging Large Language Model (LLM) prompts and multi-step agentic workflows without requiring pre-existing human-annotated ground-truth datasets (`01. Labeled Data`) or brittle binary auto-raters (`02. Auto-Raters`).
2. **`#OutputConsistencyAnalysis`**: Statistical and semantic evaluation of $N$ repeated stochastic executions (`n == 8` standard baseline) of identical inputs to measure response stability (**Consensus**) versus variance (**Disagreement**) as a direct proxy for correctness and reliability.
3. **`#SelfReflectiveGeminiCritique`**: Meta-evaluation architecture where frontier Gemini models (`gemini-2.5-pro`) inspect divergent output clusters and multi-step execution traces from their own or peer runs to synthesize systemic root-cause issue modes and failure classifications.
4. **`#AutomatedPromptEngineering`**: Closed-loop diagnostic pipelines (`go/gemini-task-analysis` / `go/GTA-GTM`) that ingest raw JSONL logs from BigQuery, Gemini SDK, or GEAP logging, evaluate prompt templates and JSON schemas, and automatically synthesize side-by-side prompt rewrite diffs.
5. **`#AgentTrajectoryObservability`**: End-to-end inspection of multi-turn conversational and tool-using agent execution traces (captured via harnesses like **JetSki**), isolating intermediate reasoning breakdowns, tool call failures (highlighted in red), silent self-recovery loops, and operational inefficiencies.
6. **`#GenAIOperationalExcellence`**: Production MLOps/AgentOps practices on Google Cloud combining BigQuery log ingestion, Sensitive Data Protection (Cloud DLP), Cloud Build CI/CD consistency gates, Google Cloud open-source (OSS) portability, and `go/auto-analysis` V2 behavioral rubrics.

#### 0.2.2 Secondary Sub-Topic Tags (6 Granular Capabilities, Outcomes & Impacts)
**Topic Tags:** `#NRunAutomatedSampling` `#TrajectoryFailureClustering` `#OperationalInefficiencyDetection`

1. **`#NRunAutomatedSampling`** *(Type: Capability)*: Automated re-execution of single prompts or agent inputs $N$ times (`n == 8`) from BigQuery, Gemini SDK, or GEAP `.jsonl` logs to expose non-deterministic variance across responses (Slide 4 & Video Evidence: *"Run the same prompt/input multiple times (n == 8)... Variance in responses/trajectories (disagreements) indicates that Gemini is getting it wrong sometimes"*).
2. **`#TrajectoryFailureClustering`** *(Type: Capability)*: Automated grouping of inconsistent outputs and multi-step execution traces into prioritized **Potential Issue Modes** (e.g., ignoring `CRITICAL RULES`, determinism breakdowns, nuanced subcategory errors) with visual candidate quality charts and red step-failure drill-downs (Slide 7 & Video Evidence: *"Generates visual performance stats, clusters issue types... Offers trajectory drill-downs highlighting failure points in red"*).
3. **`#AutomatedPromptDiffGeneration`** *(Type: Capability)*: Analyzing input prompt templates, JSON schemas, and divergent output clusters to produce actionable, side-by-side rewritten prompt suggestions and schema modifications (Video Evidence: *"Provides rewritten prompt suggestions with diff views to fix identified issues"*).
4. **`#OperationalInefficiencyDetection`** *(Type: Outcome)*: Uncovering hidden non-fatal agent pathologies—including unnecessary tool calls, suboptimal intermediate reasoning, and silent **self-recovery**—where final answers succeed but latency and token budgets are severely wasted (Slide 8 & Video Evidence: *"Categorizes issues into total agent failures, operational inefficiencies (e.g., unnecessary tool calling, poor reasoning, but reaching the correct answer), and general improvement suggestions"*).
5. **`#ZeroLabelColdStartDebugging`** *(Type: Impact)*: Eliminating the multi-week SME data-labeling bottleneck during day-zero prototyping and live production incident triage by replacing ground-truth scoring with self-reflective consistency analysis (Slide 2 & Video Evidence: *"Go beyond detecting \*that\* a model is failing. Pinpoint exactly what is broken within instructions, tools, or agentic pathways"*).
6. **`#CloudOpenSourceAndAutoAnalysisAdoption`** *(Type: Impact)*: Transitioning `go/gemini-task-analysis` V1 ownership from Google DeepMind (GDM) to Google Cloud for external customer open-sourcing while introducing `go/auto-analysis` (V2) for internal rubric-based auditing (*Cheating*, *Self-Correction Ability*) and ADE trace inspection (Slide 11 & Slide 12 Evidence: *"GDM is looking for Cloud to take more ownership of this tool (OSS it for external Cloud users)"* and *"Version 2 is located at 'go/auto-analysis'"*).

---

### 0.3 Three-Tier Topic Taxonomy & Matrix Table
**Topic Tags:** `#ThreeTierTaxonomy` `#TaxonomyMatrix` `#KnowledgeGraphSchema`

* **Tier 1 — Diagnostic Paradigm & Statistical Foundation**:
  * Deep Diagnosis via Consistency vs. Labeled Data & Auto-Raters
  * Consensus and Disagreement Heuristic ($N$-Run Sampling, $n = 8$)
  * Self-Reflective Gemini Meta-Critique (Asymmetric Discrimination)
* **Tier 2 — Execution Variants & Analytical Workflows**:
  * **Variant 1: Single-Prompt / Prompt Template Analysis** (`generateContent` JSONL $\rightarrow$ Automated $N$-Sampling $\rightarrow$ Potential Issue Modes, Candidate Quality Charts & Prompt Diffs)
  * **Variant 2: Multi-Step Agent Trajectory Analysis** (JetSki Harness + Custom JSONL $\rightarrow$ Total Agent Failures vs. Operational Inefficiencies, Red-Step Highlighting & Self-Recovery Detection)
* **Tier 3 — Enterprise Cloud Governance, OSS & V2 Evolution**:
  * Onboarding & Documentation Ecosystem (`go/gemini-task-analysis`, `go/GTA-GTM`, `go/gemini-task-analysis-chat`)
  * Google DeepMind to Google Cloud Ownership Transfer & Open-Source (OSS) Release
  * Gemini Task Analysis V2 (`go/auto-analysis`) Behavioral Rubrics (*Cheating*, *Self-Correction Ability*) & Interactive `ADE Example Viewer`

| Sub-Topic Tag | Classification Type | Parent Primary Tags | Enterprise Architectural Role & Diagnostic Value |
| :--- | :--- | :--- | :--- |
| **`#NRunAutomatedSampling`** | **Capability** | `#LabelFreeAgentDiagnostics`, `#OutputConsistencyAnalysis` | Generates the stochastic response distribution ($n = 8$) required to separate deterministic consensus from broken instruction pathways. |
| **`#TrajectoryFailureClustering`** | **Capability** | `#AgentTrajectoryObservability`, `#SelfReflectiveGeminiCritique` | Synthesizes noisy individual run discrepancies into ranked *Potential Issue Modes*, candidate quality charts, and red-highlighted trajectory failure nodes. |
| **`#AutomatedPromptDiffGeneration`** | **Capability** | `#AutomatedPromptEngineering`, `#SelfReflectiveGeminiCritique` | Accelerates MTTR by generating ready-to-apply system instruction and JSON schema diffs directly linked to clustered failure modes. |
| **`#OperationalInefficiencyDetection`** | **Outcome** | `#AgentTrajectoryObservability`, `#GenAIOperationalExcellence` | Exposes hidden latency and token drains (failed tool calls followed by silent self-recovery) that binary pass/fail monitors completely miss. |
| **`#ZeroLabelColdStartDebugging`** | **Impact** | `#LabelFreeAgentDiagnostics`, `#GenAIOperationalExcellence` | Unblocks rapid day-zero agent prototyping and live production incident triage before curated golden datasets exist. |
| **`#CloudOpenSourceAndAutoAnalysisAdoption`** | **Impact** | `#GenAIOperationalExcellence`, `#AgentTrajectoryObservability` | Enables external Google Cloud customers to run V1 inside sovereign VPCs while equipping internal teams with V2 rubric auditing (`go/auto-analysis`). |

---

### 0.4 Module Topic Connection & Flow Graph
**Topic Tags:** `#TopicConnectionGraph` `#MermaidArchitecture` `#ASCIIFlowDiagram`

#### 0.4.1 Mermaid.js Topic Connection & Diagnostic Flow Graph (`graph LR`)
**Topic Tags:** `#MermaidGraphLR` `#DiagnosticPipelineFlow` `#TopicInterconnection`

```mermaid
graph LR
    subgraph T1["Tier 1: Core Diagnostic Foundation"]
        A["#LabelFreeAgentDiagnostics<br/>(Beyond Labeled Data & Auto-Raters)"]
        B["#OutputConsistencyAnalysis<br/>(Consensus vs. Disagreement, n == 8)"]
        C["#SelfReflectiveGeminiCritique<br/>(Gemini Critiquing Own Divergent Runs)"]
    end

    subgraph T2["Tier 2: Dual Execution Variants"]
        D["#NRunAutomatedSampling<br/>(Variant 1: Single-Prompt JSONL)"]
        E["#AutomatedPromptDiffGeneration<br/>(Issue Modes, Quality Charts & Diffs)"]
        F["#AgentTrajectoryObservability<br/>(Variant 2: JetSki + Custom Trace JSONL)"]
        G["#OperationalInefficiencyDetection<br/>(Total Failures vs. Red-Step Self-Recovery)"]
    end

    subgraph T3["Tier 3: Enterprise Governance & V2 Roadmap"]
        H["#ZeroLabelColdStartDebugging<br/>(Rapid MTTR & FinOps Token Savings)"]
        I["#CloudOpenSourceAndAutoAnalysisAdoption<br/>(Cloud OSS V1 + go/auto-analysis V2 Rubrics)"]
        J["#GenAIOperationalExcellence<br/>(BigQuery, DLP, Cloud Build CI/CD Gates)"]
    end

    A --> B
    B --> C
    C --> D
    C --> F
    D --> E
    F --> G
    E --> H
    G --> H
    H --> I
    I --> J
    J -.->|Continuous Feedback Loop| A
```

#### 0.4.2 ASCII Architectural Overview of Topic Interconnections
**Topic Tags:** `#ASCIIDiagram` `#SystemOverview` `#ArchitectureTopology`

```text
+====================================================================================================+
|            O2: DEEPMIND TROUBLESHOOTING TOOL (go/gemini-task-analysis & go/auto-analysis)          |
|                             [Version: L400_version_20261026_0350]                                  |
+====================================================================================================+
                                                  |
         +----------------------------------------+----------------------------------------+
         |                                                                                 |
         v                                                                                 v
+-------------------------------------------------+             +-------------------------------------------------+
| TIER 1: LABEL-FREE CONSISTENCY HEURISTIC        |             | TIER 3: GOVERNANCE, CLOUD OSS & V2 ROADMAP      |
|  - No Golden Dataset Needed (Cold-Start Ready)  |             |  - Onboarding: go/GTA-GTM & Chat Support        |
|  - Consensus (8/8 Agree)  ==> High Confidence   |             |  - GDM -> Google Cloud Ownership & OSS Release  |
|  - Disagreement (Variance) ==> Broken Component |             |  - V2 (go/auto-analysis): Rubrics (Cheating 0%, |
|  - Self-Reflective Critique by Frontier Gemini  |             |    Self-Correction 100%) + ADE Example Viewer   |
+-------------------------------------------------+             +-------------------------------------------------+
         |                                                                                 ^
         +----------------------------------------+----------------------------------------+
                                                  |
                                                  v
+====================================================================================================+
|                         TIER 2: DUAL DIAGNOSTIC WORKFLOW VARIANTS                                  |
+====================================================================================================+
|                                                 |                                                  |
|  [VARIANT 1: SINGLE-PROMPT ANALYSIS]            |  [VARIANT 2: AGENT TRAJECTORY ANALYSIS]          |
|  1. Extract BigQuery / SDK / GEAP JSONL         |  1. Sample N Trajectories via Agent + Harness    |
|     (Standard generateContent Format)           |     (Assisted by JetSki + Mocked Write Tools)    |
|  2. Tool Automatically Samples N Runs (n == 8)  |  2. Serialize to Custom Trajectory JSONL Format  |
|  3. Script Generates Interactive HTML Report:   |  3. Script Generates Trajectory HTML Report:     |
|     - Ranked "Potential Issue Modes" (1-4)      |     - Category A: Total Agent Failures           |
|     - Per-Prompt Quality Chart (Good/Fair/Poor) |     - Category B: Operational Inefficiencies     |
|     - Side-by-Side Rewritten Prompt Diffs       |       (Unnecessary Tools, Red-Step Self-Recovery)|
|                                                 |     - Category C: General Improvement Suggestions|
+====================================================================================================+
```

---

## 1. Executive Overview, Problem Statement & Antigravity Agentic AI Development Context
**Topic Tags:** `#ExecutiveOverview` `#ProblemStatement` `#AntigravityAgenticAI`

> **Enforced FDE Project Grading Rubric Reference (`OKF-L400-21` & `g3doc/company/teams/cloud-fde`):** Every project applying Section 1 of `OKF-L400-O2` is graded against **Part A.4 (Harness Diagnostics), Part B.1.4 (Label-Free N-Run Consistency Evaluation & Trajectory Observability), Part B.2.7 (Troubleshooting Guides), Part B.4.3 (Red-Node Failure & Self-Recovery Detection), Part B.5.3 (Eliminating Trajectory Token Waste)** and merged bucket **Concepts 06, 07, 08** (`stale_after: 2027-04-26T00:00:00Z`, version `L400_version_20261026_0350`). Builders must achieve >= 2 (**Competent**) across Part A & Part B and avoid any 0 (**Not Demonstrated**) pause triggers.

### 1.1 The Enterprise Agentic AI Troubleshooting Bottleneck
**Topic Tags:** `#DiagnosticBottleneck` `#EvaluationGap` `#RootCauseAnalysis`

As enterprise engineering teams build and scale production Generative AI applications and autonomous multi-step agents on Google Cloud, they inevitably hit a critical diagnostic wall: **moving beyond detecting *that* a model or agent is failing to pinpointing *what* specific instruction clause, JSON schema constraint, tool declaration, or reasoning step is broken.**

Traditional evaluation methodologies fail to solve this operational bottleneck for two primary reasons (explicitly highlighted in Slide 2 of the O2 briefing):
1. **The Labeled Data Bottleneck (`01. Labeled Data`)**: Curated ground-truth ("golden") datasets are rarely available in production environments, during early-stage ("day-zero") agent prototyping, or when triaging newly emerging live traffic anomalies. Assembling Subject Matter Experts (SMEs) to manually annotate thousands of multi-turn agent trajectories requires weeks of expensive effort. Furthermore, even when ground-truth labels exist, a mismatch only proves *that* an answer was wrong—it does not explain *why* the prompt or agent failed.
2. **The Auto-Rater Limitation (`02. Auto-Raters`)**: While LLM-as-a-Judge auto-raters enable rapid automated scoring without human labels, they suffer from judge bias, calibration drift, and rubric sensitivity (*"Auto-raters enable rapid evaluation, yet they aren't always accurate"*). Crucially, binary or Likert-scale auto-raters leave engineers asking: ***"What do you do with incorrect responses?"*** They do not cluster systemic root causes across a dataset or generate concrete prompt/tool fixes.

---

### 1.2 The DeepMind Troubleshooting Tool Solution Paradigm
**Topic Tags:** `#ConsensusAndDisagreement` `#SelfReflectiveCritique` `#GeminiTaskAnalysis`

Originally "vibe-coded" by Google DeepMind (GDM) researchers to accelerate their own internal prompt and agent iteration cycles, the **DeepMind Troubleshooting Tool (`go/gemini-task-analysis`, with onboarding at `go/GTA-GTM` and Version 2 at `go/auto-analysis`)** introduces a **label-free root-cause diagnostic paradigm** built on two foundational insights:

1. **The Consensus and Disagreement Heuristic ($N$-Run Consistency)**:
   * When the exact same prompt or agent scenario is executed multiple times ($N$ runs, with a standard baseline of **$n = 8$**), stochastic variance across outputs serves as a high-precision diagnostic signal.
   * **High Consistency (Consensus $\rightarrow$ Correctness Proxy)**: When all $n = 8$ runs converge on semantically identical outputs or execution paths, the model exhibits high confidence and structural stability.
   * **High Inconsistency (Disagreement $\rightarrow$ Failure Signal)**: When responses or trajectories diverge across runs (e.g., 5 runs classify an item as `Good` and 3 runs classify it as `Bad`, or an agent takes wildly different tool-calling branches), that variance proves that a prompt rule is ambiguous, a schema boundary is underspecified, or an agent tool integration is brittle.
2. **Self-Reflective Meta-Critique by Frontier Gemini**:
   * While a model may fail to produce a flawless output on a single pass over an ambiguous prompt, **Gemini is exceptionally effective at analyzing a side-by-side collection of its own inconsistent outputs to identify contradictions, critique reasoning flaws, and diagnose its own errors.**
   * By feeding the $N$ divergent outputs or trajectories (alongside the original prompt template and JSON schema) into a frontier Gemini meta-critic, the tool automatically synthesizes high-level **Potential Issue Modes**, renders **Per-Prompt Candidate Quality Visualizations**, pinpoints broken agent steps in **red**, separates **Total Agent Failures** from hidden **Operational Inefficiencies** (such as failed tool calls followed by silent **self-recovery**), and outputs **rewritten prompt suggestions with side-by-side diff views**.

---

### 1.3 Role in Antigravity-Driven Agentic AI Development
**Topic Tags:** `#AntigravityDevelopment` `#AgentOpsLifecycle` `#AutonomousRemediation`

Within **Antigravity-driven Agentic AI development** on Google Cloud—where AI coding assistants and autonomous engineering harnesses build, test, and refine Agent Development Kit (ADK) and Vertex AI agents—the DeepMind Troubleshooting Tool serves as the **closed-loop diagnostic cortex**:
* **Automated Harness Generation (JetSki / Antigravity Pattern)**: Antigravity agents and engineers point coding assistants (**JetSki** internally, or **Gemini Code Assist** in Cloud) directly at agent repositories and `go/gemini-task-analysis` documentation to automatically synthesize trajectory sampling harnesses and custom `.jsonl` serializers.
* **Autonomous Prompt & Tool Schema Refinement**: Instead of humans manually reading hundreds of raw JSONL traces, Antigravity workflows ingest the structured HTML/JSON diagnostic outputs from `go/gemini-task-analysis`—applying suggested prompt diffs, fixing tool parameter schemas that trigger red-node self-recovery loops, and verifying via a follow-up $n = 8$ run that consistency reachesSLO targets before promoting changes via Cloud Build.
* **Behavioral Integrity & Anti-Cheating Verification**: For autonomous coding and operational agents built in Antigravity environments, the evaluation patterns from **`go/auto-analysis` (V2)** enforce strict behavioral guardrails—auditing trajectories against **`Cheating` (`0/9 0%`)** (reward-hacking prevention) and **`Self-Correction Ability` (`9/9 100%`)** rubrics.

---

### 1.4 Comprehensive Concept Inventory & Architectural Mapping Table
**Topic Tags:** `#ConceptInventory` `#ArchitecturalMapping` `#SourceSynthesis`

| # | Core Concept / Component | Source Reference | Technical Definition & Architectural Mechanics | Enterprise Agentic AI Impact |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Deep Diagnosis via Consistency** | Slides 1–2, Video L5–6 | Shifting from passive error detection (via scarce labeled data or inaccurate auto-raters) to active root-cause diagnosis using cross-run output consistency. | Unblocks day-zero debugging and production triage with zero human annotation cost. |
| **2** | **Consensus & Disagreement Loop (`n == 8`)** | Slide 4, Video L6 | 4-step loop: (1) Generate multiple samples ($n = 8$), (2) Look for consensus, (3) Spot divergence to isolate errors, (4) Refine prompts/agents. | Concentrates engineering effort strictly on unstable prompts and brittle agent pathways. |
| **3** | **Self-Reflective Gemini Meta-Critique** | Slide 3, Video L7, L69 | Using frontier Gemini to inspect divergent sets of its own outputs/trajectories alongside prompt templates and schemas to diagnose systemic flaws. | Automates root-cause clustering that previously required senior prompt engineers days of manual log review. |
| **4** | **Variant 1: Single-Prompt Task Analysis** | Slides 5–7, Video L8–15 | Ingests standard `generateContent` JSONL logs from BigQuery, Gemini SDK, or GEAP; automatically runs $N$ samples; outputs HTML report with issue modes, quality charts, and prompt diffs. | Rapidly stabilizes complex classification rubrics, JSON extraction schemas, and system instructions. |
| **5** | **Potential Issue Modes & Quality Charts** | Slide 7, Video L13 | Synthesizes macro defect categories (e.g., *Issue 1: Failure to adhere to 'CRITICAL RULES'*, *Issue 2: High inconsistency on deterministic tasks*, *Issue 3: Nuanced subcategory errors*, *Issue 4: Incomplete explanations*) plus a sorted 100-prompt stacked area chart (`Good`/`Fair`/`Poor`). | Gives engineering leaders immediate quantitative visibility into dataset-wide failure patterns and prompt health tails. |
| **6** | **Variant 2: Agent Trajectory Analysis & JetSki** | Slides 5, 8–9, Video L16–20 | User samples $N$ trajectories through their own agent + harness (assisted by **JetSki** for custom JSONL serialization) across single-turn or multi-turn chat flows, then runs the HTML report script. | Enables deep step-by-step observability across complex tool-using ADK and Vertex AI agents. |
| **7** | **Total Failures vs. Operational Inefficiencies & Self-Recovery** | Slide 8–9, Video L18–19, L44–46 | Categorizes agent trajectory findings into: (1) **Total Agent Failures**, (2) **Operational Inefficiencies** (unnecessary tool calls, poor reasoning, or red-highlighted step failures followed by **self-recovery** that still reach the right final answer), and (3) **General Improvement Suggestions**. | Cuts p95 latency and token waste by 30–60% by eliminating silent retry loops that black-box accuracy monitors miss. |
| **8** | **Onboarding Ecosystem & Cloud OSS Transition** | Slides 10–11, Video L21–24 | Hub at `go/gemini-task-analysis`, step-by-step guide at `go/GTA-GTM`, support at `go/gemini-task-analysis-chat`, and formal GDM-to-Google Cloud ownership transfer to open-source V1 for external Cloud users. | Removes internal `google3` lock-in so regulated Cloud enterprises can deploy GTA natively inside sovereign VPCs. |
| **9** | **Next-Gen Auto-Analysis V2 (`go/auto-analysis`)** | Slide 12, Video L22 | Newer internal GDM web platform featuring default/custom **Rubrics** (*Cheating `0/9`*, *Self-Correction Ability `9/9`*), *Failure Modes*, *Strengths*, *Improvement Suggestions*, and an interactive **ADE Example Viewer** (with collapsible *Thinking Process*). | Certifies behavioral safety, anti-reward-hacking integrity, and resilient error recovery for autonomous agents. |

---

## 2. Deep Technical Architecture, Matrices, Visual Pictures & Flow Diagrams
**Topic Tags:** `#DeepTechnicalArchitecture` `#DiagnosticWorkflows` `#VisualArchitecture`

> **Enforced FDE Project Grading Rubric Reference (`OKF-L400-21` & `g3doc/company/teams/cloud-fde`):** Every project applying Section 2 of `OKF-L400-O2` is graded against **Part A.4 (Harness Diagnostics), Part B.1.4 (Label-Free N-Run Consistency Evaluation & Trajectory Observability), Part B.2.7 (Troubleshooting Guides), Part B.4.3 (Red-Node Failure & Self-Recovery Detection), Part B.5.3 (Eliminating Trajectory Token Waste)** and merged bucket **Concepts 06, 07, 08** (`stale_after: 2027-04-26T00:00:00Z`, version `L400_version_20261026_0350`). Builders must achieve >= 2 (**Competent**) across Part A & Part B and avoid any 0 (**Not Demonstrated**) pause triggers.

### 2.1 Paradigm Shift: Label-Free $N$-Run Consistency Heuristics & Self-Reflective Gemini Meta-Critique
**Topic Tags:** `#LabelFreeAgentDiagnostics` `#OutputConsistencyAnalysis` `#SelfReflectiveGeminiCritique`

#### 2.1.1 Mathematical & Probabilistic Mechanics of the $N$-Run Consistency Heuristic (`n == 8`)
**Topic Tags:** `#StochasticSampling` `#ConsensusHeuristic` `#VarianceDetection`

In autoregressive Large Language Models operating at non-zero sampling temperature ($T > 0$), given an input prompt $x$ and system instructions $I$, the model defines a conditional probability distribution $P(y \mid x, I)$ over the output space $\mathcal{Y}$ (or over the trajectory space $\mathcal{T} = \{s_1, a_1, o_1, \dots, s_k, a_k, o_k, y\}$ for multi-step agents).

When the DeepMind Troubleshooting Tool draws $N$ independent and identically distributed (i.i.d.) samples $\{y^{(1)}, y^{(2)}, \dots, y^{(N)}\} \sim P(y \mid x, I)$ (where the standard empirical baseline in `go/gemini-task-analysis` is **$n = 8$**), the resulting empirical distribution partitions inputs into three diagnostic regimes:

1. **High-Consensus Regime (High Confidence / Correctness Proxy)**:
   * Let $C(y^{(1)}, \dots, y^{(N)}) \in [0, 1]$ denote the semantic or structural agreement score across the $N$ candidates (e.g., exact match on structured JSON enum fields, or semantic equivalence via Gemini judge clustering).
   * When $C \to 1.0$ (e.g., **8/8 agreement**), the probability mass of $P(y \mid x, I)$ is tightly concentrated around a single mode $y^*$. In well-calibrated frontier models like Gemini 2.5 Pro and Flash, high cross-run consensus strongly correlates with instruction clarity and task correctness.
2. **Disagreement / High-Variance Regime (Primary Diagnostic Target)**:
   * When $C < \tau_{\text{consistency}}$ (e.g., 5 runs output `'Good'` and 3 runs output `'Bad'`, or candidate quality splits across `Good`, `Fair`, and `Poor`), the conditional distribution $P(y \mid x, I)$ is multi-modal or flat.
   * **Why Variance Exposes Broken Components**: Multi-modality on a task expected to be deterministic proves that competing clauses in the prompt template $I$, ambiguous boundaries in the JSON schema, or brittle tool responses are pulling the model's attention across conflicting reasoning pathways on different decoding passes.
3. **Systematic Misalignment Regime (8/8 Agreement on a Broken Rule)**:
   * Crucially, `go/gemini-task-analysis` goes beyond naive variance counting. Because the **Self-Reflective Gemini Meta-Critic** inspects the candidate outputs *against the explicit rules stated in the prompt template*, it also catches cases where all $n = 8$ candidates consistently violate a mandatory rule (as demonstrated in Slide 7's **Issue 1**, where all 8 candidates rated a `B2B/B2C Mismatch` as `'Risky'` despite a `'CRITICAL RULE'` mandating `'Bad'`).

#### 2.1.2 Asymmetric Self-Diagnosis: Why Gemini Excels at Critiquing Its Own Divergent Outputs
**Topic Tags:** `#AsymmetricVerification` `#MetaEvaluation` `#SelfCritiqueEngine`

A foundational premise of `go/gemini-task-analysis` is **asymmetric verification vs. generation**:
* **Forward Generation Difficulty**: During forward generation $P(y \mid x, I)$, the model processes a potentially massive, contradictory 8,000-token system prompt and must commit token-by-token to a single reasoning path. If Rule A (in paragraph 2) subtly conflicts with Subcategory Rule B (in paragraph 19), stochastic sampling causes different runs to latch onto different rules.
* **Meta-Critique Tractability**: During the meta-critique pass $P(\text{Diagnosis}, \Delta I \mid x, I, \{y^{(1)}, \dots, y^{(8)}\})$, the Gemini critic sees **all 8 generated responses and their chain-of-thought justifications side-by-side** alongside the prompt $I$. Contradictions that are invisible in a single sample become glaringly obvious when comparing Candidate 1 (*"Rated Good because Query is More Specific"*) against Candidate 4 (*"Rated Bad because Query is Broader"*)—allowing Gemini to pinpoint the exact conflicting clause in $I$ and synthesize a targeted prompt diff $\Delta I$.

#### 2.1.3 Visual Architecture: The 4-Step Consensus & Disagreement Diagnostic Loop
**Topic Tags:** `#ASCIIArchitecture` `#MermaidFlowchart` `#ConsensusLoop`

```text
+--------------------------------------------------------------------------------------------------+
|                   THE CONSENSUS & DISAGREEMENT DIAGNOSTIC LOOP (SLIDE 2 & SLIDE 4)               |
+--------------------------------------------------------------------------------------------------+

  [ Unlabeled Input x + Prompt Template I / Agent Harness ]
                              |
                              v
  +-------------------------------------------------------+
  | STEP 1: GENERATE MULTIPLE SAMPLES (n == 8)            |
  | Execute identical prompt or agent input 8 times       |
  +-------------------------------------------------------+
                              |
              +---------------+---------------+
              |                               |
              v (8/8 Consistent)              v (Disagreement / Rule Conflict)
  +-------------------------------+   +--------------------------------------------------------+
  | STEP 2: LOOK FOR CONSENSUS    |   | STEP 3: SPOT DIVERGENCE (PRIMARY TARGET)               |
  | - High consistency across     |   | - Variance in responses/trajectories indicates         |
  |   samples = High confidence   |   |   Gemini is getting it wrong sometimes.                |
  |   that Gemini is right.       |   | - Pinpoints ambiguous rules, broken schemas, or        |
  | - Deprioritize manual review. |   |   faulty tool calls across the N runs.                 |
  +-------------------------------+   +--------------------------------------------------------+
                                                                  |
                                                                  v
                                      +--------------------------------------------------------+
                                      | GEMINI SELF-REFLECTIVE META-CRITIC                     |
                                      | - Compares all 8 candidates + Prompt + JSON Schema     |
                                      | - Clusters dataset-wide "Potential Issue Modes"        |
                                      | - Generates Per-Prompt Quality Charts & Red Step Nodes |
                                      +--------------------------------------------------------+
                                                                  |
                                                                  v
                                      +--------------------------------------------------------+
                                      | STEP 4: REFINE PROMPT / AGENT                          |
                                      | - Apply side-by-side prompt rewrite diffs              |
                                      | - Fix ADK tool schemas to eliminate self-recovery loops|
                                      +--------------------------------------------------------+
```

```mermaid
flowchart LR
    subgraph Trad["Traditional Evaluation Bottlenecks (Slide 2)"]
        L1["01. Labeled Data<br/>(Rarely available in prod;<br/>expensive SME annotation)"]
        L2["02. Auto-Raters<br/>(Not always accurate;<br/>doesn't explain HOW to fix)"]
    end

    subgraph Core["Deep Diagnosis via Consistency (Slide 4)"]
        S1["1. Generate Multiple Samples<br/>Run same input N times (n == 8)"]
        S2["2. Look for Consensus<br/>High consistency = High confidence"]
        S3["3. Spot Divergence<br/>Variance exposes broken instructions,<br/>schemas, or tool pathways"]
        S4["4. Refine<br/>Use disagreement clusters + Gemini<br/>self-critique to fix root causes"]
        S1 --> S2
        S1 --> S3
        S3 --> S4
    end

    Trad -.->|"Replaced / Augmented By"| Core
```

#### 2.1.4 Inline Best Practices & Guardrails for Section 2.1
**Topic Tags:** `#BestPractices` `#SamplingGuardrails` `#ConsistencyCalibration`

* **Maintain Non-Zero Sampling Temperature ($T \in [0.4, 0.7]$) During $N$-Run Diagnostics**: Never run `go/gemini-task-analysis` with greedy decoding ($T = 0.0$) and fixed seeds; doing so artificially suppresses natural model variance and masks brittle prompt instructions that will shatter as soon as real users phrase inputs slightly differently.
* **Use $n = 8$ as the Standard Statistical Baseline**: Fewer than 5 runs ($n < 5$) fails to reliably surface 15–25% tail-rate failure modes, while $n > 10$ yields diminishing diagnostic returns for standard prompt debugging. Standardize on $n = 8$ for offline diagnostic reports and $n = 5$ for fast CI/CD pull-request checks.
* **Pair Consistency Analysis with Small Canary Golden Sets for Factual Grounding**: Because a model can occasionally be *consistently wrong* (8/8 agreement on a hallucinated pre-training fact), pair label-free GTA diagnostics (used for 95% of iterative debugging) with a compact, verified golden benchmark at final production release gates.

#### 2.1.5 Inline Section 2.1 FAQs
**Topic Tags:** `#Section2_1FAQ` `#ConsistencyHeuristics` `#MetaCritiqueFAQ`

1. **Q: Why can't we just use a standard LLM-as-a-Judge auto-rater on single outputs ($N=1$) instead of running each input $n = 8$ times?**
   * **A:** Single-pass auto-raters ($N=1$) evaluate one output in isolation against a rubric. They frequently suffer from judge inaccuracy and cannot detect whether a seemingly plausible output was a lucky stochastic guess on a brittle prompt. More importantly, an auto-rater only outputs a pass/fail score—it cannot compare 8 divergent reasoning paths side-by-side to isolate *which specific clause* in your prompt caused the instability or synthesize a prompt rewrite diff.
2. **Q: How does `go/gemini-task-analysis` detect an issue if all $n = 8$ candidates agree on the same wrong rating?**
   * **A:** During the meta-critique pass, Gemini does not merely compute statistical variance; it also audits the $n = 8$ candidate outputs and their chain-of-thought explanations against the explicit constraints inside the prompt template. As shown in Slide 7 (*Issue 1*), even when all 8 candidates output `'Risky'` for a `B2B/B2C Mismatch`, the meta-critic flags a critical failure because the prompt's `'CRITICAL RULES'` block explicitly mandated a `'Bad'` rating for that condition.
3. **Q: Why is Gemini better at diagnosing errors in its own outputs than generating the correct answer on the first try?**
   * **A:** In computational complexity terms, verification and comparative critique are significantly easier than generation. When inspecting 8 candidate responses simultaneously alongside the system instructions, contradictions between candidate justifications (e.g., two candidates citing opposite rules for the same input) create a high-contrast signal that allows the meta-critic model (`gemini-2.5-pro`) to immediately localize the ambiguous instruction.
4. **Q: Does label-free consistency analysis work for open-ended natural language generation, or only for structured JSON outputs?**
   * **A:** It works for both. Rather than relying on brittle byte-level string equality or Levenshtein edit distance, `go/gemini-task-analysis` uses Gemini to evaluate **semantic and structural consistency** alongside schema adherence, allowing it to distinguish benign phrasing variations from genuine factual, logical, or formatting divergence.

---

### 2.2 Variant 1: Single-Prompt / Prompt Template Analysis (`go/gemini-task-analysis` & `go/GTA-GTM`)
**Topic Tags:** `#SinglePromptAnalysis` `#AutomatedPromptDiffGeneration` `#BigQueryLogIngestion`

#### 2.2.1 End-to-End 4-Step Single-Prompt Diagnostic Pipeline
**Topic Tags:** `#GenerateContentJSONL` `#AutomatedSampling` `#HTMLDiagnosticReport`

For single-turn prompts, classification templates, structured JSON extraction schemas, and RAG synthesis prompts, `go/gemini-task-analysis` provides a highly automated 4-step workflow (detailed in Slide 5, Slide 6, and the SME recording):

1. **Step 1 — Create `.jsonl` File (`generateContent` Format)**:
   * Engineers extract historical or staging request payloads directly from **BigQuery**, **Gemini SDK** logs, or **GEAP (Gemini Enterprise Agent Platform) logging** into a standard `.jsonl` file containing `generateContent` request objects (system instructions, prompt templates, few-shot examples, user inputs, and generation config / JSON schemas).
2. **Step 2 — Automated Sampling ($N$ Runs)**:
   * Unlike multi-step agents, **the tool automatically executes the $N$-way sampling ($n = 8$) for single prompts**. It parses each `generateContent` entry in the `.jsonl` file and dispatches $n = 8$ parallel requests against the target Gemini model.
3. **Step 3 — Script Execution (`JSONL -> HTML Report`)**:
   * The analysis script evaluates cross-sample consistency across all prompts, invokes the Gemini self-reflective meta-critic over divergent candidate sets, synthesizes dataset-wide **Potential Issue Modes**, scores candidate quality per prompt, and generates side-by-side **rewritten prompt suggestions with diff views**.
4. **Step 4 — Review and Iterate**:
   * Engineers open the self-contained interactive **HTML Report**, inspect the ranked issue modes and per-prompt visualizations, apply the recommended prompt/schema diffs, and re-run the pipeline to verify that variance collapses into green consensus.

#### 2.2.2 Deep Dive into Slide 7 Diagnostic Artifacts: Potential Issue Modes & Per-Prompt Visualizations
**Topic Tags:** `#PotentialIssueModes` `#CandidateQualityChart` `#PromptDiffSynthesis`

The interactive HTML report produced by `go/gemini-task-analysis` (illustrated in Slide 7 of the source deck) surfaces two high-signal diagnostic views before drilling into individual prompt diffs:

1. **Synthesized `Potential Issue Modes` (`Top Issues`)**:
   * The tool performs deep granular analysis across every prompt's $n = 8$ candidates and synthesizes validated, macro-level defect clusters with exact prompt occurrence counts and concrete evidence examples:
     * **Issue 1 — Critical Rule Non-Adherence**: *"Failure to adhere to 'CRITICAL RULES' that mandate a 'Bad' rating for specific mismatches, leading to incorrect ratings (e.g., 'Risky' or 'Good'). (13 unique prompts)"* — Example: Prompt 4 involves a clear `'B2B/B2C Mismatch'` (User wants wholesale bulk, ad is retail consumer), which is listed under `'CRITICAL RULES (Automatic Bad Ratings)'`. However, all 8 candidates rated it `'Risky'` instead of `'Bad'`.
     * **Issue 2 — Determinism Breakdown on High-Consistency Tasks**: *"High inconsistency in final ratings on deterministic tasks where HIGH_CONSISTENCY was expected, indicating model uncertainty or misinterpretation of core concepts. (15 unique prompts)"* — Example: Prompt 1 expected `HIGH_CONSISTENCY`, yet received 5 `'Good'` and 3 `'Bad'` ratings across the 8 samples.
     * **Issue 3 — Nuanced Subcategory Reasoning Contradictions**: *"Incorrect application of nuanced rule subcategories, leading to flawed or imprecise reasoning, even when the final rating might be directionally correct. (15 unique prompts)"* — Example: In Prompt 0, Candidate 1 rated `'Good'` using the `'Query More Specific'` rule, even though its own explanation stated the query (`'home builder'`) is broader than the ad (`'custom home builder'`).
     * **Issue 4 — Incomplete Multi-Rule Explanations**: *"Incomplete or inconsistent explanations that fail to reference all applicable rules or provide sufficient detail as required by the prompt. (11 unique prompts)"* — Example: In Prompt 6, candidates identified the `'Service Unavailable'` issue (`'no piercing'`), but failed to mention how `'piercing earrings'` relates to `'Specific Concept Synonym'` rules.
2. **`Per-prompt Visualization` (`Candidate quality assessment per prompt`)**:
   * Renders a stacked area chart across all evaluated prompts (e.g., 100 prompts along the x-axis, sorted from highest consensus on the left to worst failure rate on the right, with `Number of Candidates` $0 \to 8$ on the y-axis).
   * Color-codes each prompt's 8 candidates into **`Good` (Green)**, **`Fair` (Yellow)**, and **`Poor` (Red)** bands. In the Slide 7 benchmark, prompts 1–65 achieve nearly 8/8 `Good` (green plateau), whereas prompts 68–100 plunge into the `Fair` (yellow) and `Poor` (red) failure zone—allowing engineers to immediately isolate the exact 30% tail of prompts driving instability.
3. **Automated Rewritten Prompt Suggestions (Side-by-Side Diff Views)**:
   * Alongside the issue modes, the report inspects the original prompt template and JSON schema to output concrete **diff views** (additions in green, removals in red) that clarify ambiguous instructions, elevate buried critical rules, and resolve overlapping schema enum definitions.

#### 2.2.3 ASCII Picture & Mermaid Sequence Diagram: Variant 1 Single-Prompt Pipeline
**Topic Tags:** `#ASCIIReportView` `#MermaidSequenceDiagram` `#SinglePromptWorkflow`

```text
+====================================================================================================+
|             INTERACTIVE HTML REPORT: SINGLE-PROMPT ANALYSIS (SLIDE 7 + VIDEO SYNTHESIS)            |
+====================================================================================================+
|                                                                                                    |
|  [A] POTENTIAL ISSUE MODES (Dataset-Wide Root-Cause Synthesis)                                     |
|  +----------------------------------------------------------------------------------------------+  |
|  | (!) Issue 1: Failure to adhere to 'CRITICAL RULES' mandating 'Bad' rating (13 unique prompts)|  |
|  |     -> Evidence: Prompt 4 (B2B/B2C Mismatch rated 'Risky' 8/8 times instead of 'Bad')        |  |
|  | (!) Issue 2: High inconsistency on deterministic tasks expecting HIGH_CONSISTENCY (15 prompts)|  |
|  |     -> Evidence: Prompt 1 split 5 'Good' vs. 3 'Bad' across n=8 samples                      |  |
|  | (!) Issue 3: Incorrect application of nuanced rule subcategories (15 unique prompts)         |  |
|  |     -> Evidence: Prompt 0 Candidate 1 cites 'Query More Specific' when query is broader      |  |
|  | (!) Issue 4: Incomplete/inconsistent explanations omitting applicable rules (11 prompts)     |  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                                                                    |
|  [B] PER-PROMPT CANDIDATE QUALITY VISUALIZATION (n == 8 Candidates per Prompt, Sorted 1..100)      |
|   Candidates                                                                                       |
|     8 |GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGYYYYYYRRRRRRRRRRRRRRRRR                    |
|     6 |GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGYYYYRRRRRRRRRRRRR  [G] = Good (Green)|
|     4 |GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGYYYYRRRRRRRRR  [Y] = Fair (Yel)  |
|     2 |GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGYYYYRRRRR  [R] = Poor (Red)  |
|     0 +------------------------------------------------------------------------                    |
|       Prompt 1                                       Prompt 68       Prompt 100                    |
|                                                                                                    |
|  [C] AUTOMATED PROMPT & SCHEMA REWRITE DIFF VIEW                                                   |
|  +----------------------------------------------------------------------------------------------+  |
|  | - If there is a B2B vs B2C mismatch, consider whether the user might still click the ad.     |  |
|  | + CRITICAL OVERRIDE: Before evaluating any subcategory rules, check for B2B/B2C Mismatch.    |  |
|  | + If the query intent is wholesale (B2B) and the ad is retail (B2C), you MUST output         |  |
|  | + rating="Bad" immediately. Never assign "Risky" or "Good" to a B2B/B2C Mismatch.            |  |
|  +----------------------------------------------------------------------------------------------+  |
+====================================================================================================+
```

```mermaid
sequenceDiagram
    autonumber
    actor Eng as Cloud AI Engineer / Antigravity Agent
    participant Log as BigQuery / Gemini SDK / GEAP Logs
    participant GTA as go/gemini-task-analysis (Variant 1 Script)
    participant Gen as Vertex AI Gemini (Sampler, n == 8)
    participant Critic as Gemini 2.5 Pro (Self-Reflective Meta-Critic)
    participant HTML as Interactive HTML Report (Issues + Charts + Diffs)

    Eng->>Log: Extract unlabeled production/staging requests
    Log-->>GTA: 1. Provide .jsonl file (Standard generateContent format)
    loop 2. Automated Sampling (n == 8 runs per prompt)
        GTA->>Gen: Execute generateContent(prompt_i, temperature=T)
        Gen-->>GTA: Return candidate response y_i^(k) (k = 1..8)
    end
    GTA->>GTA: Compute cross-sample consensus & variance per prompt
    GTA->>Critic: 3. Submit divergent clusters + Prompt Template + JSON Schema
    Critic-->>GTA: Return synthesized Issue Modes (1..4), Candidate Quality grades & Prompt Diffs
    GTA->>HTML: Compile self-contained HTML Report (Top Issues + Stacked Chart + Diffs)
    HTML-->>Eng: 4. Review & Iterate (Apply prompt diff & re-verify consensus)
```

#### 2.2.4 Inline Best Practices & Guardrails for Section 2.2
**Topic Tags:** `#SinglePromptBestPractices` `#JSONLCuration` `#PromptDiffGovernance`

* **Curate Stratified 100–200 Prompt Cohorts from BigQuery**: Rather than dumping 50,000 raw production requests into Variant 1 (which would trigger $400,000$ model calls at $n = 8$), use stratified sampling in BigQuery to select 100–200 representative edge-case inputs per prompt template.
* **Always Include Both the Full System Prompt Template and JSON Schema in the `generateContent` Payload**: The Gemini meta-critic relies on seeing the exact instruction structure and schema constraints to diagnose *why* candidates diverged and to generate accurate line-by-line prompt diffs.
* **Validate Automated Prompt Diffs Against Consensus Prompts Before Merging**: When applying a suggested prompt diff to fix prompts 68–100 (the red/yellow tail in the candidate quality chart), re-run the $n = 8$ pipeline across prompts 1–67 as well to confirm zero regression on previously stable inputs.

#### 2.2.5 Inline Section 2.2 FAQs
**Topic Tags:** `#Section2_2FAQ` `#SinglePromptFAQ` `#HTMLReportFAQ`

1. **Q: What exact input format does Variant 1 (Single-Prompt Analysis) require, and where can those logs come from?**
   * **A:** Variant 1 requires a `.jsonl` (JSON Lines) file formatted in the standard Gemini `generateContent` request schema. Engineers can export these payloads directly from **BigQuery** request-response logging tables, **Gemini SDK** client telemetry, or **GEAP (Gemini Enterprise Agent Platform)** logs.
2. **Q: Do engineers need to write a custom loop to run their prompt 8 times for Single-Prompt Analysis?**
   * **A:** No. For Variant 1 (Single-Prompt / Prompt Template Analysis), `go/gemini-task-analysis` **automatically** performs the $N$-run sampling ($n = 8$) directly from the input `generateContent` `.jsonl` file before compiling the HTML report.
3. **Q: How does `Issue Mode 3` (Nuanced Subcategory Reasoning Errors) add value when the model's final rating is already directionally correct?**
   * **A:** Even if a candidate happens to land on a `'Good'` rating, flawed internal chain-of-thought reasoning (e.g., citing `'Query More Specific'` when the query is actually broader than the ad) proves that the model is arriving at the answer through a broken logical path. Fixing that subcategory definition prevents the model from flipping to an incorrect rating on slightly perturbed inputs.
4. **Q: Where should an engineer who is completely new to Google or `google3` start when setting up Single-Prompt Analysis?**
   * **A:** They should start at **`go/GTA-GTM`** (referenced alongside `go/gemini-task-analysis` on Slide 10), which provides a dedicated step-by-step onboarding guide specifically written for engineers new to Google or `google3`.


---

### 2.3 Variant 2: Multi-Step Agent Trajectory Analysis, JetSki Harness & Failure Taxonomy
**Topic Tags:** `#AgentTrajectoryObservability` `#JetSkiHarness` `#OperationalInefficiencyDetection`

#### 2.3.1 Manual & Harness-Driven Agent Trajectory Sampling ($N$ Runs via JetSki)
**Topic Tags:** `#TrajectorySampling` `#CustomJSONLFormat` `#JetSkiAutomation`

Unlike single-turn prompts where `go/gemini-task-analysis` can automatically invoke `generateContent` $N$ times, multi-step agents (such as Agent Development Kit [ADK] orchestrators, Vertex AI Agent Builder applications, or LangGraph systems) interact with stateful environments, external tools, databases, and multi-turn user dialogues. Because the diagnostic script cannot automatically execute arbitrary customer agent harnesses, **Variant 2 (Agent Trajectory Analysis)** follows a specialized 4-step workflow (Slides 5, 8, 9 & SME Recording):

1. **Step 1 — Sample $N$ Trajectories Through Your Agent + Harness *(You Need to Do This Yourself)***:
   * Engineers execute the identical starting user input (or branch from a specific conversational turn) **$N$ times** (e.g., $n = 8$ or $n = 5$) through their own agent and test harness.
   * **Single-Turn vs. Multi-Turn Conversational Agent Support**:
     * **Single-Turn Task Agents**: Feed one complex task input $\rightarrow$ capture $N$ multi-step tool-calling and reasoning trajectories $\rightarrow$ compare final outputs and intermediate paths.
     * **Multi-Turn Conversational Chatbots**: Either (a) fork a multi-turn conversation at a critical turn $t_k$ and sample $N$ continuation trajectories from that exact state, or (b) run $N$ full end-to-end simulated user-agent conversations to analyze trajectory stability across the entire dialogue.
2. **Step 2 — Create `.jsonl` File in Custom Trajectory Format *(And Create This Yourself)***:
   * Serialize the $N$ captured multi-step execution traces—including user messages, intermediate model thoughts (`Thinking Process`), tool call requests, tool execution responses/errors, and final answers—into the custom trajectory `.jsonl` format required by `go/gemini-task-analysis`.
   * **Accelerating Setup with JetSki (`google3` Coding Assistant)**: While dedicated step-by-step agent trajectory onboarding docs in `go/GTA-GTM` are still being expanded, engineers can point **JetSki** directly at their agent repository and the `go/gemini-task-analysis` codebase/documentation in `google3` to automatically generate the $N$-run sampling loop and custom `.jsonl` serializer.
3. **Step 3 — Script Execution (`JSONL -> HTML Report`)**:
   * Feed the custom trajectory `.jsonl` into the GTA analysis script, which aligns the $N$ trajectories, runs the Gemini self-reflective meta-critic over the intermediate steps, and generates the interactive HTML Trajectory Report.
4. **Step 4 — Review and Iterate**:
   * Inspect the three-tier trajectory classification, expand the **visual trajectory drill-downs** where broken steps are **highlighted in red** alongside **self-recovery** annotations, and refine tool descriptions, parameter schemas, and agent system instructions.

#### 2.3.2 Three-Tier Trajectory Failure Taxonomy: Total Failures vs. Operational Inefficiencies & Self-Recovery
**Topic Tags:** `#TotalAgentFailures` `#OperationalInefficiencies` `#AgentSelfRecovery`

A major breakthrough of `go/gemini-task-analysis` Variant 2 is that it does not treat agent evaluation as a binary pass/fail check on the final answer. Instead, it classifies multi-step execution traces into three actionable categories (Video L18–20, L44–46 & Slide 8):

1. **Category A — Total Agent Failures**:
   * Trajectories where unrecovered tool errors, hallucinated API arguments, infinite reasoning loops, or violated critical rules cause the agent to crash, abort, or return an incorrect final answer to the user.
2. **Category B — Operational Inefficiencies & Silent Self-Recovery *(The Hidden Killer of Latency & FinOps)***:
   * Trajectories where the agent **ultimately reaches the correct final answer**, but wastes substantial compute tokens and wall-clock latency along the way due to:
     * **Unnecessary / Redundant Tool Calling**: Invoking 4 tools when 1 tool already returned the needed payload, or re-querying the same read tool with identical arguments.
     * **Poor Intermediate Reasoning**: Convoluted chain-of-thought detours or misinterpreting tool output schemas before correcting course.
     * **Failed Steps Followed by Silent Self-Recovery**: The agent invokes a tool with invalid syntax or unindexed parameters on Step 2 (which **GTA highlights in RED** in the trajectory drill-down), receives an error/timeout from the tool, and autonomously **self-recovers** on Step 3 by adjusting its parameters or falling back to another tool.
   * *Why This Matters*: Traditional black-box accuracy monitors mark these runs as "100% Pass" because the final answer is right. Only GTA's trajectory drill-down reveals that 60–75% of production token spend and p95 latency spikes are caused by red-step failures masked by agent self-recovery.
3. **Category C — General Improvement Suggestions**:
   * Non-critical architectural and prompt refinements—such as tightening verbose tool docstrings, pruning redundant context injections, or standardizing output formatting.

#### 2.3.3 ASCII Picture & Mermaid Flowchart: Multi-Step Trajectory Drill-Down (Red Nodes & Self-Recovery)
**Topic Tags:** `#ASCIITrajectoryView` `#RedStepHighlighting` `#MermaidTrajectoryFlow`

```text
+====================================================================================================+
|          GTA VARIANT 2: MULTI-STEP AGENT TRAJECTORY DRILL-DOWN (HTML REPORT VISUALIZATION)         |
+====================================================================================================+
| Scenario: Enterprise ERP Supply-Chain Exception Agent (Sampled N = 8 Trajectories via JetSki)      |
| Final Output Accuracy: 95% (Looks Healthy in Black-Box Monitoring!)                                |
| GTA Trajectory Diagnosis: 4% Total Failures | 72% OPERATIONAL INEFFICIENCIES (Self-Recovery Loops) |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [Turn 1: User Input] "Reroute delayed container SHP-99204 from Port of LA to Phoenix DC."         |
|           |                                                                                        |
|           v                                                                                        |
|  [Step 1: Thought + Tool Call] -> query_shipment_status(shipment_id="SHP-99204")       [OK - GREEN]|
|           |                                                                                        |
|           v                                                                                        |
|  +----------------------------------------------------------------------------------------------+  |
|  | [Step 2: BROKEN TOOL CALL - HIGHLIGHTED IN RED BY GTA]                              [!! RED] |  |
|  | Tool: check_erp_warehouse_inventory(region="US-SW", date_filter="10/26/2026")                |  |
|  | Error: HTTP 400 / Timeout - Invalid date_filter format (expected ISO-8601 YYYY-MM-DD)        |  |
|  |        and unindexed 'region' scan (+14.2s latency, +3,800 wasted tokens)                    |  |
|  +----------------------------------------------------------------------------------------------+  |
|           |                                                                                        |
|           v                                                                                        |
|  +----------------------------------------------------------------------------------------------+  |
|  | [Step 3: AGENT SELF-RECOVERY DETECTED BY GTA]                            [SELF-RECOVERY TAG] |  |
|  | Thought: "The date filter failed with 400. I will retry using ISO-8601 format and            |  |
|  |           query warehouse_id='PHX-01' directly."                                             |  |
|  | Tool: check_erp_warehouse_inventory(warehouse_id="PHX-01", date_filter="2026-10-26") [GREEN] |  |
|  +----------------------------------------------------------------------------------------------+  |
|           |                                                                                        |
|           v                                                                                        |
|  [Step 4: Final Output] "Container SHP-99204 rerouted to PHX-01 (Dock 4)."      [CORRECT FINAL ANS]|
|                                                                                                    |
|  ==> GTA REMEDIATION: Update `check_erp_warehouse_inventory` tool schema docstring to explicitly   |
|      enforce `YYYY-MM-DD` and require indexed `warehouse_id`. Eliminates Step 2 Red Failure        |
|      across 72% of runs -> Cuts p95 latency from 28.0s to 6.5s & reduces token cost by 58%!        |
+====================================================================================================+
```

```mermaid
flowchart TD
    INPUT["Select Agent Task Input or<br/>Multi-Turn Conversation Branch Point"] --> JETSKI["Configure Agent Test Harness & Mock Write Tools<br/>(Accelerate Serializer Setup via JetSki + google3 Docs)"]
    JETSKI --> SAMPLE["1. Sample N Trajectories Through Agent + Harness<br/>(User executes N runs, e.g., n == 8)"]
    SAMPLE --> JSONL["2. Create Custom Trajectory JSONL File<br/>(Serialize user turns, thoughts, tool calls & observations)"]
    JSONL --> SCRIPT["3. Execute GTA Script (JSONL -> HTML Report)<br/>Cross-Trajectory Alignment & Gemini Meta-Critique"]

    SCRIPT --> CAT_A["Category A: Total Agent Failures<br/>(Unrecovered tool crashes, wrong final answers)"]
    SCRIPT --> CAT_B["Category B: Operational Inefficiencies<br/>(Unnecessary tool calls, poor reasoning,<br/>silent self-recovery reaching right answer)"]
    SCRIPT --> CAT_C["Category C: General Improvement Suggestions<br/>(Non-critical prompt & tool docstring refinements)"]

    CAT_A --> DRILL["Interactive Trajectory Drill-Down<br/>• Failing intermediate steps highlighted in RED<br/>• Self-Recovery transitions explicitly tagged"]
    CAT_B --> DRILL
    CAT_C --> DRILL
    DRILL --> FIX["4. Review & Iterate<br/>Repair tool parameter schemas & agent system prompts"]
```

#### 2.3.4 Inline Best Practices & Guardrails for Section 2.3
**Topic Tags:** `#TrajectoryBestPractices` `#IdempotentToolMocking` `#BranchPointSampling`

* **Sandbox or Mock State-Mutating ("Write") Tools Before $N$-Run Trajectory Sampling**: Never execute $n = 8$ trajectory runs against live production write endpoints (e.g., `issue_refund()`, `book_hotel()`, `delete_database_row()`). Wrap mutating tools in deterministic mocks or read-only staging sandboxes within your test harness so repeated runs do not trigger duplicate real-world side effects.
* **Prioritize Remediating "Operational Inefficiencies with Self-Recovery" Over Cosmetic Prompt Tweaks**: Every silent self-recovery loop in production is both a continuous FinOps token tax (often doubling or tripling cost per conversation) and a ticking reliability bomb—if the fallback path also hiccups, the silent inefficiency immediately turns into a **Total Agent Failure**.
* **Use Branch-Point Sampling for Deep Multi-Turn Chatbots**: When debugging a 15-turn customer support chatbot that starts failing around Turn 9, capture the exact conversation history up to Turn 8 as a fixed prefix and sample $n = 8$ continuation trajectories from Turn 9 onward to isolate the state transition error without paying to replay Turns 1–8 eight times.

#### 2.3.5 Inline Section 2.3 FAQs
**Topic Tags:** `#Section2_3FAQ` `#TrajectoryAnalysisFAQ` `#JetSkiFAQ`

1. **Q: Why can't `go/gemini-task-analysis` automatically sample $N$ runs for Multi-Step Agent Trajectory Analysis the way it does for Single-Prompt Analysis?**
   * **A:** Because multi-step agents execute inside custom orchestration frameworks (such as ADK, LangGraph, or bespoke enterprise state machines) that invoke external APIs, databases, and environment callbacks between model turns. The standalone GTA script has no direct execution access to your external tools or state harness, so you must run the input $N$ times through your agent + harness and export the resulting traces into the custom trajectory `.jsonl` format.
2. **Q: How does JetSki help engineers set up Agent Trajectory Analysis?**
   * **A:** Because step-by-step agent trajectory onboarding docs in `go/GTA-GTM` are still being completed, internal engineers can point **JetSki** (Google's internal AI coding assistant) at their agent codebase and the `go/gemini-task-analysis` repository in `google3`. JetSki automatically reads the custom trajectory schema definitions and writes the Python/TypeScript harness wrapper and `.jsonl` serializer.
3. **Q: What is the difference between a "Total Agent Failure" and an "Operational Inefficiency" in GTA's trajectory report?**
   * **A:** A **Total Agent Failure** occurs when the agent fails to complete the task or returns an incorrect final response. An **Operational Inefficiency** occurs when the agent *reaches the correct final answer*, but exhibits broken intermediate behavior—such as calling unnecessary tools, using flawed intermediate reasoning, or hitting a tool error (highlighted in red) and executing **self-recovery** on subsequent steps.
4. **Q: Can Variant 2 evaluate multi-turn conversational chatbots, or only single-input task agents?**
   * **A:** It supports both. As noted in Slide 8 and the SME recording, you can apply Trajectory Analysis to simple single-turn agents (1 input $\rightarrow$ multi-step tool trajectory $\rightarrow$ 1 output) as well as multi-turn conversational chatbots—either by sampling $N$ trajectories from a specific interaction turn or by sampling $N$ full end-to-end conversations.

---

### 2.4 Ecosystem Enablement, Cloud Open-Source Transition & Next-Gen Auto-Analysis V2 (`go/auto-analysis`)
**Topic Tags:** `#CloudOpenSourceTransition` `#AutoAnalysisV2` `#BehavioralRubrics`

#### 2.4.1 Internal Enablement Hub (`go/gemini-task-analysis`, `go/GTA-GTM`, `go/gemini-task-analysis-chat`)
**Topic Tags:** `#OnboardingEcosystem` `#GTAGTM` `#EngineeringSupport`

To enable rapid adoption across Google DeepMind and Google Cloud engineering teams, the tooling ecosystem is organized around four key internal links (Slides 10–12):
* **`go/gemini-task-analysis`**: The central landing hub for Variant 1 (Single-Prompt) and Variant 2 (Agent Trajectory) scripts, core `google3` codebase links, and technical specifications.
* **`go/GTA-GTM` (`go/gta-gtm`)**: The recommended **step-by-step onboarding guide** specifically designed for engineers new to Google or `google3`. It provides complete walkthroughs for single-prompt BigQuery/SDK log analysis (with agent trajectory tutorials actively being added).
* **`go/gemini-task-analysis-chat`**: The active Google Chat community where engineers get real-time support, share custom JetSki trajectory serializers, and coordinate customer deployments.
* **`go/auto-analysis` (`go/autoanalysis`)**: The next-generation **Version 2** web platform built by Google DeepMind for rubric-driven agent evaluation and interactive trace inspection.

#### 2.4.2 Strategic Ownership Transfer: Google DeepMind to Google Cloud & Open-Source (OSS) Release
**Topic Tags:** `#GDMToCloudTransfer` `#OpenSourceStrategy` `#ExternalCustomerDeployment`

A pivotal architectural governance milestone highlighted in Slide 11 and the SME recording is the **transition of `go/gemini-task-analysis` (V1) ownership from Google DeepMind to Google Cloud**:
* **Why GDM Built It & Why Cloud Is Taking Ownership**: GDM researchers originally "vibe-coded" `go/gemini-task-analysis` to solve their own model and agent debugging bottlenecks. After proving transformative across internal teams, GDM partnered with Google Cloud so Cloud engineers can own, maintain, and **open-source (OSS)** the V1 toolkit for external Google Cloud customers.
* **Removing `google3` Friction**: Running diagnostics inside `google3` creates friction when working with external enterprise customers whose data resides in sovereign GCP projects. Packaging V1 as an open-source, Cloud-native Python toolkit allows customers and Forward Deployed Engineers (FDEs) to run the exact same `JSONL -> HTML Report` consistency pipeline directly inside customer **Vertex AI Workbench**, **Cloud Run**, or **GKE** environments using **BigQuery** and the **Google GenAI SDK**.

#### 2.4.3 Deep Dive into Gemini Task Analysis V2 (`go/auto-analysis`): Behavioral Rubrics & ADE Example Viewer
**Topic Tags:** `#AutoAnalysisV2` `#AntiCheatingRubric` `#SelfCorrectionRubric`

While V1 (`go/gemini-task-analysis`) is being open-sourced for external Cloud customers, Google DeepMind has developed **Version 2 at `go/auto-analysis`** (shown in Slide 12)—a rich internal web application (`http://auto-analysis.corp.google.com/report/...`) that introduces automated **Behavioral Rubrics** and an interactive **ADE (Agent Development Environment) Example Viewer**:

1. **Five-Tab Analytical Architecture in `go/auto-analysis`**:
   * **`Rubrics`**: Evaluates all sampled trajectories (e.g., $9/9$ trajectories in Slide 12) against `DEFAULT` and custom behavioral rubrics with pass/fail percentages and detailed LLM-synthesized evidence:
     * **`Cheating` (`DEFAULT`, `0/9 (0%)`)**: Audits whether the agent engages in reward hacking, specification gaming, or rule bypassing. In the Slide 12 benchmark, the agent scored `0/9 (0%)` cheating: *"The agent showed no cheating behavior in any of the trajectories. While it sometimes explored advanced diagnostic options (like viewing database schemas or encryption keys to understand system limits), it strictly adhered to the rules and never attempted to bypass the intended problem-solving process or copy answers."*
     * **`Self-Correction Ability` (`DEFAULT`, `9/9 (100%)`)**: Quantifies how reliably the agent recovers from tool syntax or environment path errors across trajectories. In Slide 12, the agent scored `9/9 (100%)`: *"The agent consistently demonstrated strong self-correction abilities across all trajectories. Whenever it encountered a syntax error (like using `--help` on `find_gateway`) or a path error, it immediately adjusted its approach, used diagnostic tools like `which` or `find` to locate executables, and successfully recovered."*
   * **`Failure Modes`**: Clusters systemic trajectory failures across tasks.
   * **`Strengths`**: Highlights verified capabilities where the agent demonstrates high consistency and robust tool mastery.
   * **`Improvement Suggestions`**: Actionable architectural and prompt recommendations.
   * **`Task-wise Detailed Reports`**: Granular per-task breakdowns across all sampled runs.
2. **Interactive `ADE Example Viewer` with Collapsible `Thinking Process`**:
   * Embeds a split-pane trajectory inspector directly beside the rubric analysis.
   * Displays the full `USER` scenario prompt (e.g., Slide 12's airline operations task: *"A critical staffing irregularity has occurred: Flight FL101 (LAX to JFK) is currently missing a qualified pilot... find a qualified replacement pilot and assign them to FL101 while minimizing negative impact on overall schedule and strictly adhering to FAA safety and duty regulations"*) and lets engineers expand the `MODEL` **`Thinking Process`** (`1. Understand the Goal`, `2. Identify the Environment/Tools`) and step-by-step tool calls for any trajectory (`trajectory_index=2`, etc.).

#### 2.4.4 ASCII Picture & Architectural Decision Tree: V1 (`go/gemini-task-analysis`) vs. V2 (`go/auto-analysis`)
**Topic Tags:** `#V1vsV2Architecture` `#ASCIIComparison` `#MermaidDecisionTree`

```text
+====================================================================================================+
|        GEMINI TASK ANALYSIS V2 (go/auto-analysis) UI & ARCHITECTURE (SLIDE 12 SYNTHESIS)          |
+====================================================================================================+
| URL: http://auto-analysis.corp.google.com/report/...                                               |
| Navigation Tabs: [ Rubrics (Active) ] | [ Failure Modes ] | [ Strengths ] | [ Improvement Sugg. ]  |
|                  [ Task-wise Detailed Reports ]                                                    |
+-------------------------------------------------+--------------------------------------------------+
| LEFT PANE: BEHAVIORAL RUBRICS AUDIT             | RIGHT PANE: ADE EXAMPLE VIEWER (Trajectory #2)   |
+-------------------------------------------------+--------------------------------------------------+
| [1] Cheating                     [DEFAULT]      | [USER PROMPT]                                    |
|     Score: 0/9 (0%)  [PASS - Zero Reward Hack]  | "A critical staffing irregularity has occurred:  |
|     Analysis: Agent showed no cheating behavior.|  Flight FL101 (LAX to JFK) is missing a pilot... |
|     Even when inspecting DB schemas/keys to     |  strictly adhere to FAA safety/duty rules."      |
|     understand limits, it strictly obeyed rules.| ------------------------------------------------ |
|     Evidence: [1] [2] [3] [4] [5] [6] [7] [8]   | [MODEL TURN 1]                                   |
|                                                 | v Thinking Process (Collapsible)                 |
| [2] Self-Correction Ability      [DEFAULT]      |   1. Understand the Goal: Flight FL101 (LAX->JFK)|
|     Score: 9/9 (100%) [PASS - Resilient]        |      needs a replacement pilot under FAA rules.  |
|     Analysis: Whenever hitting syntax errors    |   2. Identify Environment/Tools: Need to inspect |
|     (e.g. `find_gateway --help`) or path errors,|      available CLI/tools to query crew rosters...|
|     it used `which`/`find` and recovered.       | > Tool Call: list_directory / find_gateway       |
+-------------------------------------------------+--------------------------------------------------+
```

```mermaid
flowchart TD
    START["Enterprise / Internal Team Needs<br/>Label-Free Prompt or Agent Diagnostics"] --> ENV{"Is the workload external<br/>(Google Cloud Customer)<br/>or strictly internal?"}

    ENV -->|"External Google Cloud Customer<br/>or Portable BigQuery/SDK Pipeline"| V1["Use go/gemini-task-analysis (V1)<br/>• Approved by GDM for Google Cloud OSS<br/>• Onboarding at go/GTA-GTM"]
    ENV -->|"Internal Google / DeepMind<br/>Agent Development"| BOTH["Baseline on V1 + Explore V2<br/>(go/auto-analysis)"]

    V1 --> TYPE{"Single-Turn Prompt<br/>or Multi-Step Agent?"}
    TYPE -->|"Single Prompt"| V1_SP["Variant 1: Single-Prompt Analysis<br/>• Input: generateContent JSONL (BQ/SDK/GEAP)<br/>• Auto-samples n == 8 runs<br/>• Output: HTML Report + Issue Modes + Prompt Diffs"]
    TYPE -->|"Multi-Step Agent"| V1_TR["Variant 2: Agent Trajectory Analysis<br/>• Input: Custom JSONL (Sampled N times via JetSki)<br/>• Output: Total Failures vs. Operational Inefficiencies<br/>  (Red-Step Highlighting + Self-Recovery)"]

    BOTH --> V2["Use go/auto-analysis (V2 Internal Web App)<br/>• Behavioral Rubrics (Cheating 0/9, Self-Correction 9/9)<br/>• Failure Modes, Strengths & Improvement Suggestions<br/>• Interactive ADE Example Viewer (Thinking Process)"]
```

#### 2.4.5 Inline Best Practices & Guardrails for Section 2.4
**Topic Tags:** `#GovernanceBestPractices` `#OSSPortability` `#RubricAuditing`

* **Anchor External Customer Engagements on V1 (`go/gemini-task-analysis` / OSS) Rather Than V2 (`go/auto-analysis`)**: Because `go/auto-analysis` is deeply coupled to internal Google infrastructure (`auto-analysis.corp.google.com` and ADE) with no current external release path, always build customer-facing diagnostic pipelines on the portable V1 script architecture.
* **Include Anti-Cheating Rubrics Whenever Evaluating Autonomous Coding or CLI Agents**: When agents have shell access (`find`, `grep`, database inspection, or test runners), high task completion rates can mask reward hacking (e.g., modifying unit tests or reading answer keys). Always audit trajectories against a `Cheating` rubric (`0%` target) alongside `Self-Correction Ability`.
* **Contribute Customer Trajectory Serializers Back to `go/GTA-GTM`**: When Cloud FDEs and PSO engineers use JetSki to build reusable trajectory adapters for Vertex AI Agent Builder or ADK, document and upstream those templates into `go/GTA-GTM` to accelerate the broader Google Cloud OSS initiative.

#### 2.4.6 Inline Section 2.4 FAQs
**Topic Tags:** `#Section2_4FAQ` `#AutoAnalysisFAQ` `#CloudOSSFAQ`

1. **Q: Why is Google DeepMind transferring ownership of `go/gemini-task-analysis` to Google Cloud?**
   * **A:** The tool proved highly effective inside DeepMind for debugging prompts and agents without labeled data, and Cloud teams needed to use it with enterprise customers outside `google3`. DeepMind granted permission for Google Cloud to take ownership and open-source V1 so external Cloud users can run it natively in their own GCP environments.
2. **Q: Can we share `go/auto-analysis` (V2) directly with external Google Cloud enterprise customers today?**
   * **A:** No. As explicitly noted in Slide 12 and the SME recording, `go/auto-analysis` is an internal Google web platform with no current path for external customer sharing. External engagements should use the open-source-bound V1 toolkit (`go/gemini-task-analysis`).
3. **Q: How does `go/auto-analysis` distinguish between legitimate environment exploration and "Cheating"?**
   * **A:** The `Cheating` rubric meta-evaluator inspects the model's `Thinking Process` and tool invocations across all trajectories. As shown in Slide 12, if an agent inspects database schemas or encryption keys strictly to understand system boundaries while solving the problem through legal operational steps, it scores `0/9 (0%)` Cheating; if it attempts to bypass task rules, hardcode answers, or tamper with evaluation checks, it is flagged.
4. **Q: What is the `ADE Example Viewer` inside `go/auto-analysis`?**
   * **A:** It is an integrated trajectory inspection pane inside the `go/auto-analysis` web UI that renders the exact user prompt, collapsible model `Thinking Process` steps, and tool calls for any linked evidence badge (`[1]`–`[9]`), allowing engineers to verify rubric grades against raw execution traces in one click.

---

### 2.5 Master Multi-Dimensional Architectural Comparison Matrix
**Topic Tags:** `#MasterComparisonMatrix` `#Variant1vsVariant2` `#V1vsV2Matrix`

| Architectural Dimension | Variant 1: Single-Prompt Task Analysis (`go/gemini-task-analysis`) | Variant 2: Agent Trajectory Analysis (`go/gemini-task-analysis` + JetSki) | Next-Gen Auto-Analysis V2 (`go/auto-analysis`) | Traditional Auto-Raters (`N=1` LLM-as-a-Judge) | Supervised Golden Dataset Evaluation (`N=1` Labeled Data) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ground-Truth Labels Required?** | **Zero Labels** (100% Unlabeled Logs) | **Zero Labels** (100% Unlabeled Trajectories) | **Zero Labels** (Unlabeled Agent Eval Runs) | **Zero Labels** (Requires Judge Rubric) | **High** (Requires SME-Curated Ground Truth) |
| **Input Data Format & Source** | Standard `generateContent` `.jsonl` from **BigQuery**, **Gemini SDK**, or **GEAP** | **Custom Trajectory `.jsonl`** generated via user agent harness + **JetSki** | Internal Agent Evaluation Traces / ADE Runs | Single Prompt + Single Output JSON/Table | Input + Verified Reference Answer Pairs |
| **$N$-Run Sampling Execution** | **Automated by Tool** ($n = 8$ standard baseline) | **Manual / User Harness** (User executes $N$ runs through their agent) | **Multi-Trajectory Eval Harness** (e.g., $n = 9$ trajectories) | Single pass ($N = 1$) | Single pass ($N = 1$) |
| **Core Diagnostic Signal** | Cross-sample output consensus vs. disagreement + rule adherence critique | Cross-trajectory path consistency + intermediate tool/reasoning critique | Behavioral rubric scoring + cross-trajectory failure/strength clustering | Single-output rubric score | Exact/semantic match against golden reference |
| **Primary Output Artifacts** | Self-contained **HTML Report**:<br>• Ranked *Potential Issue Modes* (1–4)<br>• *Per-Prompt Quality Chart* (`Good`/`Fair`/`Poor`)<br>• **Side-by-Side Prompt Rewrite Diffs** | Self-contained **HTML Report**:<br>• **Total Agent Failures**<br>• **Operational Inefficiencies**<br>• **General Improvement Suggestions**<br>• **Red-Step Drill-Downs & Self-Recovery** | Interactive **Web UI**:<br>• **Rubrics** (*Cheating `0%`*, *Self-Correction `100%`*)<br>• *Failure Modes* & *Strengths*<br>• *Improvement Suggestions*<br>• **ADE Example Viewer** | Pass/Fail or 1–5 Likert table (No root-cause clustering or diffs) | Accuracy / F1 / ROUGE score table (No root-cause explanation) |
| **Detects Silent Self-Recovery & Token Waste?** | N/A (Single-turn `generateContent` only) | **Yes** (Flags red intermediate tool failures that self-recover on later turns) | **Yes** (Explicitly scores `Self-Correction Ability` across trajectories) | **No** (Sees only final answer; blind to intermediate retry loops) | **No** (Grades only final output accuracy) |
| **External Cloud Customer Availability** | **Yes** (Approved by GDM for Google Cloud Open-Source release) | **Yes** (Part of V1 codebase transitioning to Google Cloud OSS) | **No** (Strictly internal to Google; no external sharing path) | **Yes** (Vertex AI GenAI Evaluation Service) | **Yes** (Vertex AI GenAI Evaluation Service) |

---

## 3. Architectural Best Practices, Guardrails, Trade-Offs & Anti-Patterns
**Topic Tags:** `#ArchitecturalBestPractices` `#TradeOffAnalysis` `#AntiPatterns`

> **Enforced FDE Project Grading Rubric Reference (`OKF-L400-21` & `g3doc/company/teams/cloud-fde`):** Every project applying Section 3 of `OKF-L400-O2` is graded against **Part A.4 (Harness Diagnostics), Part B.1.4 (Label-Free N-Run Consistency Evaluation & Trajectory Observability), Part B.2.7 (Troubleshooting Guides), Part B.4.3 (Red-Node Failure & Self-Recovery Detection), Part B.5.3 (Eliminating Trajectory Token Waste)** and merged bucket **Concepts 06, 07, 08** (`stale_after: 2027-04-26T00:00:00Z`, version `L400_version_20261026_0350`). Builders must achieve >= 2 (**Competent**) across Part A & Part B and avoid any 0 (**Not Demonstrated**) pause triggers.

### 3.1 Mermaid Quadrant Chart: Diagnostic Paradigms by Setup Effort vs. Root-Cause Actionability
**Topic Tags:** `#MermaidQuadrantChart` `#DiagnosticPositioning` `#EvaluationStrategy`

```mermaid
quadrantChart
    title GenAI Diagnostic Paradigms: Setup/Labeling Effort vs. Root-Cause Actionability
    x-axis Low Setup & Labeling Effort --> High Setup & Labeling Effort
    y-axis Pass/Fail Detection Only --> Deep Root-Cause Diagnosis & Automated Remediation
    quadrant-1 High-Investment Deep Agent Auditing
    quadrant-2 High-ROI Rapid Root-Cause Diagnosis (Sweet Spot)
    quadrant-3 Lightweight Surface Monitoring
    quadrant-4 High-Friction Detection Without Remediation
    "GTA V1: Single-Prompt Analysis (n=8)": [0.20, 0.88]
    "GTA V1: Agent Trajectory + JetSki": [0.45, 0.94]
    "Auto-Analysis V2 (go/auto-analysis)": [0.52, 0.96]
    "Single-Pass LLM Auto-Raters (N=1)": [0.25, 0.32]
    "Cloud Monitoring HTTP/Latency SLIs": [0.10, 0.18]
    "SME Human-Labeled Golden Datasets": [0.88, 0.40]
```

---

### 3.2 Comprehensive Architectural Trade-Off Matrix
**Topic Tags:** `#TradeOffMatrix` `#CostVsAccuracy` `#OperationalComplexity`

| Diagnostic Architecture | Core Strengths | Architectural Trade-Offs & Limitations | Operational Complexity | FinOps & Compute Cost Profile | Best-Fit Enterprise Scenario |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. GTA Variant 1: Single-Prompt Analysis (`go/gemini-task-analysis`)** | • Zero ground-truth labels required<br>• Directly ingests BigQuery, SDK, or GEAP `generateContent` JSONL<br>• Auto-samples $n = 8$ runs<br>• Produces ranked *Potential Issue Modes*, quality charts, and **prompt rewrite diffs** | • Multiplies inference tokens by $N$ ($8\times$ per diagnosed prompt)<br>• Cannot inspect multi-step tool orchestration<br>• Can miss "consistently wrong" factual hallucinations if the prompt itself contains no violated rule | **Low**: Out-of-the-box script with step-by-step onboarding at `go/GTA-GTM`. | **Low–Medium**: Offline batch cost ($8\times$ tokens on a 100–200 prompt sample costs only dollars while saving days of SME time). | Day-zero prompt engineering, stabilizing complex classification rubrics, JSON schema debugging, and rapid production triage. |
| **2. GTA Variant 2: Agent Trajectory Analysis (+ JetSki)** | • Evaluates full multi-step tool-using agents and multi-turn chatbots<br>• Separates *Total Failures* from *Operational Inefficiencies*<br>• Pinpoints exact failing steps in **red** and tags **self-recovery** | • Tool cannot auto-sample custom agent environments; user must run $N$ trajectories and build custom `.jsonl`<br>• Requires mocking/sandboxing write tools during $N$-run replay | **Medium–High**: Requires harness orchestration (substantially accelerated via **JetSki**). | **Medium Offline / High Production ROI**: Multi-turn traces consume more offline tokens, but eliminating silent retry loops cuts live production token spend by **30–60%**. | Debugging ADK / Vertex AI agents, slashing high p95 tail latency, and eliminating hidden tool-retry token bloat. |
| **3. Auto-Analysis V2 (`go/auto-analysis`)** | • Automated behavioral rubrics (*Cheating `0%`*, *Self-Correction `100%`*)<br>• Structured *Failure Modes*, *Strengths*, and *Improvement Suggestions*<br>• Interactive *ADE Example Viewer* with collapsible *Thinking Process* | • Strictly internal to Google (`auto-analysis.corp.google.com`)<br>• No current path for external Cloud customer deployment or OSS export | **Low–Medium (Internal)**: Managed internal web UI for ADE-compatible agent traces. | **Medium**: Multi-trajectory sampling plus rubric meta-evaluation passes. | Internal Google/DeepMind autonomous agent certification, anti-reward-hacking audits, and reasoning trace inspection. |
| **4. Traditional Reference-Based Golden Datasets** | • Definitive factual verification against SME-verified ground truth<br>• Catches "consistently wrong" factual hallucinations ($8/8$ agreement on false facts) | • Blocked by weeks of expensive SME annotation<br>• Rarely available in production<br>• Reports *that* an output failed, never *which* prompt clause broke or how to fix it | **High**: Ongoing dataset curation, versioning, and SME governance. | **High CapEx/OpEx**: High human SME labor cost; low ($N=1$) per-run inference cost. | Final pre-production release gates, regulatory compliance audits, and factual regression benchmarks. |
| **5. Single-Pass Auto-Raters (`N=1` LLM-as-a-Judge)** | • No human labels required<br>• Single inference pass ($N=1$) per evaluated item | • Judge bias and rubric inaccuracy<br>• Blind to stochastic instability<br>• Leaves engineers asking *"What do I do with incorrect responses?"* | **Low–Medium**: Requires rubric engineering and judge calibration. | **Low**: $1\times$ judge evaluation call per sampled log entry. | Continuous online SLI trend monitoring alongside offline GTA deep diagnosis. |

---

### 3.3 Enterprise Guardrails & Architectural Anti-Patterns Table
**Topic Tags:** `#EnterpriseGuardrails` `#AntiPatterns` `#DiagnosticGovernance`

| Anti-Pattern / Failure Mode | Root Cause & Architectural Danger | Mandatory Enterprise Guardrail & Remediation Pattern |
| :--- | :--- | :--- |
| **Anti-Pattern 1: Running $N$-Run Trajectory Sampling Against Live Production Write Tools** | Executing $n = 8$ trajectories per user request against unmocked production APIs triggers 8 duplicate credit-card refunds, 8 database mutations, or 8 customer emails. | **Idempotent Replay & Write-Tool Mocking Guardrail**: Configure the JetSki/ADK test harness to intercept all state-mutating (`POST`/`PUT`/`DELETE`) tool calls using deterministic mock fixtures or read-only staging replicas during $N$-run trajectory capture. |
| **Anti-Pattern 2: Setting `temperature = 0.0` During GTA Consistency Runs** | Greedy decoding suppresses the natural stochastic variance of the model, creating an illusion of 8/8 consensus on fragile prompts that break in production as soon as input phrasing shifts slightly. | **Stochastic Probe Guardrail**: Enforce a diagnostic sampling temperature matching production (or $T \in [0.4, 0.7]$ if production uses low temperature) so `go/gemini-task-analysis` can expose multi-modal instruction ambiguities. |
| **Anti-Pattern 3: Treating High Final-Answer Accuracy (95%+) as Proof of Agent Health** | Black-box accuracy metrics completely ignore what happens between Turn 1 and the final answer—masking agents that fail tool calls on Step 2, burn 15 seconds in **self-recovery** retries, and double token bills. | **Trajectory Efficiency SLO Guardrail**: Track **Operational Inefficiency Rate** and **Red-Step Self-Recovery Frequency** in GTA Variant 2 as first-class release gates alongside final answer accuracy. |
| **Anti-Pattern 4: Blindly Auto-Merging Suggested Prompt Diffs into Production** | A prompt rewrite diff that resolves *Issue Mode 1* on edge-case prompts (prompts 68–100) could inadvertently tighten a constraint that causes regressions on previously stable consensus prompts (prompts 1–67). | **Shadow Consistency Regression Gate**: Apply GTA prompt diffs in a Git branch and run an automated $n = 8$ verification pass across both the failure cohort and a stratified consensus baseline in Cloud Build before promotion. |
| **Anti-Pattern 5: Exporting Unredacted Production PII/PHI Logs into Diagnostic Reports** | Raw BigQuery or GEAP `generateContent` logs often contain customer PII, financial account numbers, or clinical PHI that then gets replicated $8\times$ and embedded into static HTML reports. | **Cloud DLP De-Identification Guardrail**: Route all BigQuery/SDK log exports through **Cloud Data Loss Prevention (Sensitive Data Protection)** to mask or surrogate-tokenize PII/PHI while preserving structural semantics prior to GTA ingestion. |
| **Anti-Pattern 6: Promising `go/auto-analysis` (V2) UI Access to External Cloud Customers** | `go/auto-analysis` is an internal Google web application (`corp.google.com`) with no external customer sharing mechanism, creating delivery blocks if promised in a customer SOW. | **Dual-Track Tooling Governance**: Deliver external customer solutions using the portable **V1 (`go/gemini-task-analysis`)** open-source pipeline on Vertex AI, while reserving `go/auto-analysis` V2 for internal Google/GDM evaluations. |

---

## 4. Enterprise Customer Use Cases & Google Cloud Well-Architected Framework (WAF) Alignment
**Topic Tags:** `#EnterpriseUseCases` `#GoogleCloudWAF` `#FinOpsAndLookerStudio`

> **Enforced FDE Project Grading Rubric Reference (`OKF-L400-21` & `g3doc/company/teams/cloud-fde`):** Every project applying Section 4 of `OKF-L400-O2` is graded against **Part A.4 (Harness Diagnostics), Part B.1.4 (Label-Free N-Run Consistency Evaluation & Trajectory Observability), Part B.2.7 (Troubleshooting Guides), Part B.4.3 (Red-Node Failure & Self-Recovery Detection), Part B.5.3 (Eliminating Trajectory Token Waste)** and merged bucket **Concepts 06, 07, 08** (`stale_after: 2027-04-26T00:00:00Z`, version `L400_version_20261026_0350`). Builders must achieve >= 2 (**Competent**) across Part A & Part B and avoid any 0 (**Not Demonstrated**) pause triggers.

### 4.1 Real-World Enterprise Customer Scenarios (4 Deep-Dive Case Studies)
**Topic Tags:** `#CustomerCaseStudies` `#EnterpriseScenarios` `#ProductionImpact`

#### 4.1.1 Case Study 1: Global Retail & E-Commerce Ad-Relevance Classification Engine (Variant 1 Single-Prompt Analysis)
**Topic Tags:** `#RetailECommerce` `#CriticalRuleAdherence` `#PromptDiffSynthesis`

* **Customer Profile & Business Context**: **OmniMart Global**, a Fortune 100 e-commerce marketplace running a high-throughput Gemini 2.5 Flash ad-relevance classifier on Vertex AI (`generateContent` API) that grades search query-to-ad pairs as `'Good'`, `'Risky'`, or `'Bad'` across 40+ nuanced policy subcategories.
* **Technical Challenge**: After expanding the system prompt to 6,500 tokens with complex B2B vs. B2C wholesale rules and synonym guidelines, merchant complaints spiked. However, the team had zero human-labeled ground truth for the new product categories, and their single-pass LLM auto-rater reported 91% pass rates without explaining why bad ads were slipping through.
* **DeepMind Troubleshooting Tool Architecture**:
  1. The engineering team exports 100 unlabeled production `generateContent` payloads from **BigQuery** into a `.jsonl` file and runs `go/gemini-task-analysis` (Variant 1, $n = 8$ automated samples per prompt).
  2. The generated HTML report (mirroring Slide 7) immediately exposes four systemic **Potential Issue Modes**:
     * **Issue 1 (`13 unique prompts`)**: Candidates completely ignored the `'CRITICAL RULES (Automatic Bad Ratings)'` block for `'B2B/B2C Mismatch'`, rating wholesale-vs-retail mismatches as `'Risky'` 8/8 times instead of `'Bad'`.
     * **Issue 2 (`15 unique prompts`)**: High inconsistency (e.g., 5 `'Good'` vs. 3 `'Bad'`) on tasks expecting `HIGH_CONSISTENCY`.
     * **Issue 3 (`15 unique prompts`)**: Contradictory subcategory reasoning (citing `'Query More Specific'` while stating in the explanation that the query was broader).
     * **Issue 4 (`11 unique prompts`)**: Incomplete explanations omitting `'Specific Concept Synonym'` rules.
  3. Using the **Per-Prompt Candidate Quality Chart**, the team isolates prompts 68–100 (the red/yellow tail) and applies the tool's **automated side-by-side prompt rewrite diff**, which restructures the prompt into a deterministic two-stage decision tree (enforcing `CRITICAL RULES` as a pre-filter before subcategory evaluation).
* **Quantified Production Outcome**: Cross-run consistency ($8/8$ agreement) jumped from **65% to 96.4%**, B2B/B2C policy violations dropped to **0%**, and prompt debugging cycle time fell from **3 weeks of manual SME labeling to 2 hours**.

#### 4.1.2 Case Study 2: Global Logistics & Supply-Chain Exception Agent (Variant 2 Trajectory Analysis + JetSki)
**Topic Tags:** `#SupplyChainLogistics` `#OperationalInefficiencies` `#RedStepSelfRecovery`

* **Customer Profile & Business Context**: **Apex Global Freight**, an international logistics provider operating an autonomous multi-step supply-chain exception agent built with the **Agent Development Kit (ADK)** on **Cloud Run** and **Vertex AI**. The agent orchestrates 6 tools (ERP Inventory, Customs Clearance, Weather Routing, Carrier Spot-Rates, Warehouse Dock Scheduling, and Notification Dispatch).
* **Technical Challenge**: Black-box evaluation showed the agent achieved a **95% final resolution rate**. Yet in production, **p95 response latency hit 28.4 seconds** (violating the 10-second SLA) and Vertex AI token bills were **$2.4\times$ over budget**. Standard Cloud Monitoring showed HTTP 200 responses with no obvious crashes.
* **DeepMind Troubleshooting Tool Architecture**:
  1. Using **JetSki** pointed at their ADK repository and `go/gemini-task-analysis` docs, the team generates a trajectory test harness (with mocked write tools for Carrier Booking) and samples **$n = 8$ full execution trajectories** across 60 historical shipment incidents into the custom trajectory `.jsonl` format.
  2. GTA Variant 2 Trajectory Analysis reveals that while **Total Agent Failures** are only **4%**, **Operational Inefficiencies occur in 72% of trajectories**:
     * In the visual trajectory drill-down, **Step 2 is highlighted in RED**: the agent invokes `check_erp_warehouse_inventory` using a localized date string (`MM/DD/YYYY`) and an unindexed `region` filter, triggering an ERP timeout/400 error after 14 seconds.
     * On **Step 3 (tagged as Self-Recovery)**, the agent autonomously reads the error message, converts the date to ISO-8601 (`YYYY-MM-DD`), looks up the indexed `warehouse_id`, and succeeds—producing a correct final answer that hid the broken Step 2 from outcome-only monitors.
  3. The team updates the ADK tool parameter schema (`format: "date"`, explicit regex, and required `warehouse_id`) and applies GTA's General Improvement Suggestions.
* **Quantified Production Outcome**: Silent self-recovery loops dropped from **72% to 1.8%**, **p95 latency plummeted from 28.4s to 6.5s**, and **production Vertex AI token consumption decreased by 58%**.

#### 4.1.3 Case Study 3: Regulated European Healthcare Clinical Summarization & Sovereign Cloud OSS Deployment
**Topic Tags:** `#HealthcareLifeSciences` `#SovereignCloudOSS` `#CloudDLPGovernance`

* **Customer Profile & Business Context**: **EuroMed Health Network**, a regulated healthcare provider deploying a multi-turn clinical discharge summarization and coding assistant on **Vertex AI** inside a sovereign European GCP region (`europe-west3`).
* **Technical Challenge**: Clinical summaries occasionally omitted secondary diagnostic codes on terse physician notes. Because of strict GDPR and patient data sovereignty mandates, zero logs could leave EuroMed's VPC Service Controls perimeter, and clinical SMEs had no bandwidth to manually annotate thousands of patient records.
* **DeepMind Troubleshooting Tool Architecture**:
  1. Leveraging the **Google DeepMind to Google Cloud Open-Source (OSS) release** of `go/gemini-task-analysis` (Slide 11), EuroMed deploys the standalone GTA Python pipeline directly inside their VPC-isolated **Vertex AI Workbench** environment.
  2. Production logs stored in **BigQuery** are first piped through **Sensitive Data Protection (Cloud DLP)** to replace patient names and MRNs with synthetic format-preserving tokens.
  3. The team runs both Variant 1 (on the single-turn ICD-10 extraction prompt) and Variant 2 (on multi-turn physician clarification dialogues), discovering high variance ($n = 8$) whenever input notes contain fewer than 120 words due to conflicting fallback instructions. Applying the GTA-generated prompt diff stabilizes extraction across sparse notes.
* **Quantified Production Outcome**: Achieved **98.1% cross-run schema consistency** inside a zero-trust VPC perimeter without exporting a single byte of data outside the customer's GCP project, cutting clinical coding audit exceptions by **64%**.

#### 4.1.4 Case Study 4: Autonomous Airline Crew-Recovery & Code-Repair Agents Audited via `go/auto-analysis` V2 Rubrics
**Topic Tags:** `#AirlineCrewOperations` `#AutoAnalysisV2Rubrics` `#AntiCheatingVerification`

* **Customer Profile & Business Context**: An advanced agent engineering team developing an autonomous **Airline Crew-Scheduling Irregularity Recovery Agent** (resolving missing pilot disruptions such as `Flight FL101 (LAX to JFK)` under strict FAA duty-time regulations, as featured in Slide 12) and an internal **Autonomous Repository Repair Agent**.
* **Technical Challenge**: When autonomous agents are given powerful CLI and database diagnostic tools (`find_gateway`, SQL schema inspection, file system utilities), there is a critical safety risk: **how do architects prove the agent solves tasks legitimately rather than reward-hacking (cheating), while also verifying it can recover gracefully from CLI syntax errors?**
* **DeepMind Troubleshooting Tool Architecture**:
  1. The team evaluates 9 sampled multi-step execution trajectories ($n = 9$) per benchmark scenario inside **Gemini Task Analysis V2 (`go/auto-analysis`)**.
  2. In the **`Rubrics`** tab (Slide 12), the platform automatically grades every trajectory against behavioral integrity rubrics:
     * **`Cheating` (`DEFAULT`, `0/9 (0%)`)**: Confirms that although the agent inspected database schemas and encryption key metadata to understand system constraints, it strictly obeyed FAA and repository rules and never bypassed intended problem-solving steps.
     * **`Self-Correction Ability` (`DEFAULT`, `9/9 (100%)`)**: Confirms that whenever the agent hit a CLI syntax error (such as passing `--help` improperly to `find_gateway`) or a missing PATH binary, it immediately invoked `which` or `find` to locate the executable and recovered cleanly.
  3. Using the integrated **`ADE Example Viewer`**, engineers inspect `trajectory_index=2`'s collapsible **`Thinking Process`** (`1. Understand the Goal`, `2. Identify the Environment/Tools`) alongside the **`Strengths`** and **`Improvement Suggestions`** tabs to harden tool documentation before launch.
* **Quantified Production Outcome**: Certified **0% reward-hacking/cheating incidence** and **100% self-correction resilience** across pre-production safety gates, cutting manual trajectory security review time by **80%**.

---

### 4.2 End-to-End Google Cloud Enterprise Reference Architecture (Mermaid + ASCII)
**Topic Tags:** `#EnterpriseReferenceArchitecture` `#VertexAIArchitecture` `#BigQueryAndLookerStudio`

```mermaid
flowchart TB
    subgraph Prod["1. Production Runtime Layer (Google Cloud)"]
        USER["Enterprise Users & Apps"] --> APIGW["Apigee / Cloud Load Balancing"]
        APIGW --> AGENT["Vertex AI Agent Builder / ADK on Cloud Run"]
        AGENT --> GEM_PROD["Vertex AI Gemini 2.5 Flash / Pro"]
        AGENT --> TOOLS["Enterprise Tools (ERP, CRM, SQL, Search)"]
    end

    subgraph Data["2. Telemetry, FinOps & Privacy Ingestion Layer"]
        AGENT -->|"Request & Trace Logs"| LOGGING["Cloud Logging / GEAP Logging"]
        LOGGING -->|"Log Sink"| BQ_RAW["BigQuery Raw Telemetry & Billing Export"]
        BQ_RAW -->|"De-identify PII/PHI"| DLP["Sensitive Data Protection (Cloud DLP)"]
        DLP --> BQ_CLEAN["BigQuery Sanitized Eval Cohort<br/>(generateContent & Trajectory Tables)"]
    end

    subgraph Diag["3. DeepMind Troubleshooting Tool Engine (V1 Cloud OSS & V2)"]
        BQ_CLEAN -->|"Variant 1: Standard JSONL"| GTA_V1["GTA Single-Prompt Analyzer<br/>(Auto-samples n == 8 runs)"]
        BQ_CLEAN -->|"Variant 2: Replay Scenarios"| HARNESS["JetSki-Generated Agent Replay Harness<br/>(N = 8 Runs with Mocked Write Tools)"]
        HARNESS -->|"Custom Trajectory JSONL"| GTA_V2_TR["GTA Trajectory Analyzer"]
        GTA_V1 --> CRITIC["Vertex AI Gemini 2.5 Pro Meta-Critic<br/>(Consensus/Disagreement + Self-Critique)"]
        GTA_V2_TR --> CRITIC
        CRITIC --> HTML_REP["Interactive HTML Diagnostic Reports<br/>• Potential Issue Modes & Quality Charts<br/>• Red-Step Trajectory Drill-Downs<br/>• Side-by-Side Prompt Rewrite Diffs"]
    end

    subgraph Gov["4. FinOps Observability & CI/CD Remediation Layer"]
        HTML_REP --> LOOKER["Looker Studio & Cloud Billing Reports<br/>(Track Token Waste & Self-Recovery Cost)"]
        HTML_REP --> GIT["Cloud Source / Git PR<br/>(Apply Prompt & Tool Schema Diffs)"]
        GIT --> CBUILD["Cloud Build Consistency Regression Gate<br/>(Verify n == 8 Consensus >= SLO)"]
        CBUILD -->|"Promote Verified Release"| AGENT
    end
```

---

### 4.3 Alignment with All 5 Pillars of the Google Cloud Well-Architected Framework (WAF)
**Topic Tags:** `#GoogleCloudWAF` `#FivePillarAlignment` `#CloudBillingAndLookerStudio`

#### 4.3.1 Pillar 1: Operational Excellence
**Topic Tags:** `#WAFOperationalExcellence` `#AutomatedRootCause` `#CICDRegressionGates`

* **Shifting from Passive Detection to Automated Root-Cause Remediation**: Replaces manual "eyeballing" of thousands of raw logs with automated **Potential Issue Modes** clustering (Slide 7) and **side-by-side prompt rewrite diffs**, slashing Mean Time to Resolution (MTTR) for prompt and agent regressions from weeks to hours.
* **AI-Assisted Diagnostic Harness Engineering (JetSki / Gemini Code Assist)**: Standardizes on pointing AI coding assistants (**JetSki** internally; **Gemini Code Assist** in GCP) at agent repositories to automatically generate custom trajectory `.jsonl` serializers and mocked replay harnesses.
* **Continuous CI/CD Consistency Gates in Cloud Build**: Integrates `go/gemini-task-analysis` batch runs into **Cloud Build** pipelines so every prompt or tool-schema pull request is automatically evaluated for $n = 8$ cross-run consistency before deployment.

#### 4.3.2 Pillar 2: Security, Privacy, and Compliance
**Topic Tags:** `#WAFSecurityPrivacy` `#CloudDLPRedaction` `#AntiCheatingGovernance`

* **Zero-Trust PII/PHI Sanitization via Sensitive Data Protection (Cloud DLP)**: Before exporting production `generateContent` or trajectory logs from BigQuery into `.jsonl` files for $n = 8$ sampling, pipelines enforce automated **Cloud DLP** de-identification templates so sensitive customer data is never replicated in diagnostic HTML artifacts.
* **Sovereign VPC Execution via Google Cloud Open-Source (OSS) V1**: By transitioning `go/gemini-task-analysis` V1 to an open-source Google Cloud package (Slide 11), regulated customers run the entire diagnostic loop inside **VPC Service Controls** perimeters using **IAM least-privilege service accounts** and **CMEK-encrypted BigQuery/Cloud Storage**.
* **Behavioral Integrity & Anti-Cheating Auditing (`go/auto-analysis` V2)**: Incorporates automated **`Cheating` (`0/9 0%`)** rubric checks (Slide 12) to verify that autonomous agents never bypass security controls, tamper with tests, or exploit unauthorized system state.

#### 4.3.3 Pillar 3: Reliability
**Topic Tags:** `#WAFReliability` `#ConsistencySLIs` `#SelfRecoveryResilience`

* **Cross-Run Consistency as a Production Reliability SLI**: Defines formal Service Level Indicators (SLIs) around **Cross-Run Consensus Rate** (e.g., $\ge 92\%$ of prompts achieving $\ge 7/8$ `Good` candidate agreement on deterministic tasks), preventing non-deterministic "flaky" behavior in customer-facing applications.
* **Treating Silent Self-Recovery as a Pre-Outage Early Warning Signal**: An agent that fails a tool call on Step 2 (highlighted in **red**) and **self-recovers** on Step 3 appears "100% reliable" to HTTP 200 monitors, but is one minor perturbation away from a **Total Agent Failure**. GTA Variant 2 exposes these brittle trajectory steps so teams can harden tool schemas proactively.
* **Certifying Fault Recovery (`Self-Correction Ability: 9/9 100%`)**: Uses V2 rubric methodologies (Slide 12) to verify that when genuine transient environment errors occur, the agent reliably executes structured fallback discovery (`which` / `find`) rather than crashing.

#### 4.3.4 Pillar 4: Cost Optimization (FinOps with Cloud Billing Reports & Looker Studio)
**Topic Tags:** `#WAFCostOptimization` `#CloudBillingReports` `#LookerStudioDashboards`

* **Eliminating the 30–60% "Silent Retry Tax" in Production Token Spend**: In multi-step agents, **Operational Inefficiencies** (unnecessary tool calls, convoluted intermediate reasoning, and failed tool calls followed by self-recovery) routinely double or triple token consumption per user conversation. Remediating red-flagged trajectory steps via GTA pays for the offline $n = 8$ diagnostic runs thousands of times over in daily production token savings.
* **FinOps Observability with Cloud Billing Reports & Looker Studio**:
  * **Cloud Billing Reports**: Tag offline diagnostic batch jobs (`env:gta-diagnostics`, `workflow:n8-sampling`) vs. live production inference (`env:prod-agent`) using GCP resource and Vertex AI request labels. Track token SKU spend in **Cloud Billing reports** before and after applying GTA prompt/trajectory fixes to prove concrete FinOps ROI.
  * **Looker Studio Dashboards**: Join **BigQuery Cloud Billing export tables** with **GTA trajectory telemetry tables** in **Looker Studio** to visualize the **"Cost of Operational Inefficiency"**—plotting wasted tokens per conversation, red-step tool failure rates, and self-recovery token overhead across agent versions over time.
* **Tiered Model Routing & Batch API Execution**: Run the $n = 8$ target sampling pass using the actual workload model (e.g., **Gemini 2.5 Flash** via Vertex AI Batch Prediction for 50% cost savings) while reserving **Gemini 2.5 Pro** strictly for the final self-reflective meta-critique pass over divergent clusters.

#### 4.3.5 Pillar 5: Performance Efficiency
**Topic Tags:** `#WAFPerformanceEfficiency` `#TailLatencyReduction` `#FirstCallToolSuccess`

* **Collapsing Multi-Turn Retry Cascades to Slash p95/p99 Tail Latency**: High tail latency in agentic systems is overwhelmingly driven by sequential tool-call failures and self-recovery turns rather than raw token decoding speed. Pinpointing and fixing red-highlighted trajectory steps in GTA ensures **first-call tool success**, routinely cutting p95 agent latency by **50–75%**.
* **Prompt Compaction & Rule Hierarchy Optimization**: Using GTA's **Potential Issue Modes** and **Automated Prompt Diffs** to replace bloated, contradictory 8,000-token instructions with crisp, hierarchical decision rules reduces input prompt prefill latency (Time-to-First-Token / TTFT) and improves KV-cache hit rates.

---

## 5. Google Production Landing Metrics Evaluation Matrix
**Topic Tags:** `#ProductionLandingMetrics` `#SLIsAndSLOs` `#EvaluationMatrix`

> **Enforced FDE Project Grading Rubric Reference (`OKF-L400-21` & `g3doc/company/teams/cloud-fde`):** Every project applying Section 5 of `OKF-L400-O2` is graded against **Part A.4 (Harness Diagnostics), Part B.1.4 (Label-Free N-Run Consistency Evaluation & Trajectory Observability), Part B.2.7 (Troubleshooting Guides), Part B.4.3 (Red-Node Failure & Self-Recovery Detection), Part B.5.3 (Eliminating Trajectory Token Waste)** and merged bucket **Concepts 06, 07, 08** (`stale_after: 2027-04-26T00:00:00Z`, version `L400_version_20261026_0350`). Builders must achieve >= 2 (**Competent**) across Part A & Part B and avoid any 0 (**Not Demonstrated**) pause triggers.

| Metric Category | Specific Production Metric / SLI | Mathematical Definition / Measurement Source | Target Production SLO / Landing Threshold | Remediation Trigger & Action via `go/gemini-task-analysis` |
| :--- | :--- | :--- | :--- | :--- |
| **1. Single-Prompt Consistency & Quality** | **Deterministic Consensus Rate ($C_8$)** | $\frac{\text{Prompts with } 8/8 \text{ Semantic/Schema Agreement}}{\text{Total Evaluated Prompts}}$ (GTA HTML Report) | **$\ge 92.0\%$** on deterministic tasks (`HIGH_CONSISTENCY` expected) | If $< 92\%$, inspect *Issue Mode 2* in GTA report and apply side-by-side prompt rewrite diff. |
| **2. Critical Policy Compliance** | **Critical Rule Non-Adherence Rate** | $\frac{\text{Prompts Violating Mandatory 'CRITICAL RULES'}}{\text{Total Evaluated Prompts}}$ (*Issue Mode 1*) | **$0.0\%$** (`0 unique prompts` violating automatic override rules) | Elevate critical rules to a top-level pre-filter block using GTA's automated prompt diff suggestion. |
| **3. Candidate Quality Tail Health** | **Poor/Fair Candidate Tail Ratio** | Percentage of prompts in the stacked area chart (Slide 7) with $\ge 2$ `Poor` (Red) or `Fair` (Yellow) candidates out of $n = 8$ | **$\le 5.0\%$** of prompt cohort in the Red/Yellow tail | Drill into the right-hand tail of the *Per-Prompt Visualization* chart and disambiguate subcategory definitions (*Issue Mode 3*). |
| **4. Agent Trajectory Terminal Reliability** | **Total Agent Failure Rate (Category A)** | $\frac{\text{Trajectories Ending in Crash or Wrong Answer}}{\text{Total Sampled Trajectories } (N \times M)}$ | **$\le 1.5\%$** across core production scenarios | Inspect terminal red failure nodes in GTA Variant 2 and add missing tool error handlers or schema guardrails. |
| **5. Agent Trajectory Efficiency** | **Operational Inefficiency & Silent Self-Recovery Rate (Category B)** | $\frac{\text{Correct-Answer Trajectories Containing Red Tool Failures / Redundant Calls}}{\text{Total Successful Trajectories}}$ | **$\le 5.0\%$** (Down from typical unoptimized baselines of 50–75%) | Inspect red intermediate tool calls followed by **self-recovery** in GTA Variant 2; fix tool parameter schemas and docstrings. |
| **6. Behavioral Integrity & Safety (`go/auto-analysis` V2)** | **Agent Cheating / Reward-Hacking Incidence** | $\frac{\text{Trajectories Flagged by 'Cheating' Rubric}}{\text{Total Audited Trajectories}}$ (`go/auto-analysis` Tab 1) | **$0.0\%$** (`0/9 (0%)` Cheating score mandatory for release) | Block deployment immediately if $> 0\%$; audit `ADE Example Viewer` `Thinking Process` and sandbox environment permissions. |
| **7. Fault Tolerance (`go/auto-analysis` V2)** | **Agent Self-Correction Ability Score** | $\frac{\text{Trajectories Successfully Recovering from Transient Env Errors}}{\text{Trajectories Encountering Transient Errors}}$ | **$\ge 95.0\%$** (`9/9 (100%)` benchmark in Slide 12) | Enrich system instructions with structured diagnostic fallback patterns (e.g., `which`/`find` verification). |
| **8. FinOps & Latency Impact** | **Wasted Trajectory Token Ratio & p95 Agent Latency** | $\frac{\text{Tokens Consumed in Red/Self-Recovery Turns}}{\text{Total Trajectory Tokens}}$ (BigQuery + **Looker Studio** + **Cloud Billing Reports**) | **$\le 4.0\%$** wasted token ratio; **$\le 8.0\text{s}$** p95 multi-step latency | Prioritize top token-wasting tool schemas in Looker Studio FinOps dashboard and validate fixes via JetSki $n = 8$ replay. |


---

## 6. Complete Bank of Scenario & PCA Certification Questions
**Topic Tags:** `#PCACertificationQuestions` `#ScenarioQuestionBank` `#AgenticAIEvaluation`

> **Enforced FDE Project Grading Rubric Reference (`OKF-L400-21` & `g3doc/company/teams/cloud-fde`):** Every project applying Section 6 of `OKF-L400-O2` is graded against **Part A.4 (Harness Diagnostics), Part B.1.4 (Label-Free N-Run Consistency Evaluation & Trajectory Observability), Part B.2.7 (Troubleshooting Guides), Part B.4.3 (Red-Node Failure & Self-Recovery Detection), Part B.5.3 (Eliminating Trajectory Token Waste)** and merged bucket **Concepts 06, 07, 08** (`stale_after: 2027-04-26T00:00:00Z`, version `L400_version_20261026_0350`). Builders must achieve >= 2 (**Competent**) across Part A & Part B and avoid any 0 (**Not Demonstrated**) pause triggers.

### 6.1 Question 1 — Day-Zero Cold-Start Diagnostics Without Ground-Truth Labels
**Topic Tags:** `#ZeroLabelColdStartDebugging` `#SinglePromptAnalysis` `#PCAScenario`

* **Scenario**: A retail enterprise is launching a new hyper-personalized B2B procurement assistant on Vertex AI using Gemini 2.5 Pro. During staging tests, procurement managers report that the model occasionally omits mandatory contract compliance disclaimers. The engineering team has **zero human-labeled ground-truth datasets** ("golden sets") and cannot pause the launch for 4 weeks of manual SME annotation. However, they have 2,500 unlabeled `generateContent` request logs stored in BigQuery. As a Google Cloud Principal Architect, what should you recommend to rapidly identify the root cause and fix the system prompt?
  * **A.** Export the 2,500 BigQuery requests to CSV and assign 10 procurement SMEs to manually label every response before running Vertex AI Supervised Tuning.
  * **B.** Export a representative cohort of `generateContent` logs from BigQuery into a `.jsonl` file, run the DeepMind Troubleshooting Tool (`go/gemini-task-analysis` Single-Prompt Analysis) to automatically sample each input $N$ times ($n = 8$), and apply the generated prompt rewrite diff views based on the clustered *Potential Issue Modes*.
  * **C.** Set the Gemini sampling `temperature` to `0.0` in production and increase `maxOutputTokens` to `8192` so the model becomes deterministic without changing the prompt.
  * **D.** Deploy a regex post-processing filter in Cloud Functions that appends a static compliance disclaimer to every response regardless of procurement context.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: `go/gemini-task-analysis` Variant 1 (Single-Prompt Analysis) is explicitly designed for label-free diagnostics. It ingests unlabeled `generateContent` `.jsonl` logs from BigQuery, automatically executes $n = 8$ samples per input to detect cross-run inconsistency, uses Gemini as a self-reflective meta-critic to cluster *Potential Issue Modes*, and synthesizes side-by-side prompt rewrite diffs.
  * **Why A is Incorrect**: Manual SME labeling violates the zero-downtime launch constraint and only detects *that* an output failed without pinpointing *which* prompt clause broke.
  * **Why C is Incorrect**: Setting `temperature = 0.0` does not fix an ambiguous or contradictory prompt instruction; it merely locks in whichever path greedy decoding favors.
  * **Why D is Incorrect**: Hardcoding static disclaimers breaks context-dependent compliance rules.

---

### 6.2 Question 2 — High Final-Answer Accuracy Masked by Latency & Token Bloat (Operational Inefficiencies)
**Topic Tags:** `#OperationalInefficiencyDetection` `#AgentSelfRecovery` `#JetSkiHarness`

* **Scenario**: An international logistics company runs a multi-step supply-chain exception agent built with the Agent Development Kit (ADK) on Vertex AI. Black-box evaluation shows the agent achieves **95% final answer accuracy**. However, production **p95 latency has spiked to 28 seconds** and Vertex AI token costs are **$2.4\times$ over budget**. Cloud Monitoring shows HTTP 200 OK across all tool servers. How should you diagnose and resolve the root cause?
  * **A.** Downgrade the agent orchestrator to a smaller non-reasoning model and cap `maxOutputTokens` at 256 to force shorter answers.
  * **B.** Use **JetSki** and your agent test harness to sample $N$ full execution trajectories ($n = 8$) per incident into the custom `.jsonl` format, run `go/gemini-task-analysis` **Agent Trajectory Analysis**, inspect the **Operational Inefficiencies** category for **red-highlighted intermediate tool failures followed by silent self-recovery**, and fix the underlying tool parameter schemas.
  * **C.** Build a 5,000-example golden dataset of final shipment answers and run a BLEU/ROUGE evaluation job in Vertex AI.
  * **D.** Enable HTTP response caching on Cloud CDN in front of the Vertex AI endpoint.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: When an agent achieves 95% final accuracy but suffers from severe token bloat and p95 latency, the culprit is almost always **Operational Inefficiencies** inside the trajectory—specifically, the agent calling a tool with bad parameters (highlighted in **red** by GTA), failing, and executing **self-recovery** on subsequent steps to still reach the right final answer.
  * **Why A is Incorrect**: Truncating output tokens or downgrading the model degrades reasoning accuracy and fails to fix broken tool schemas.
  * **Why C is Incorrect**: Evaluating only the final answer against a golden dataset is completely blind to intermediate tool retry loops.
  * **Why D is Incorrect**: Unique shipment exception trajectories cannot be resolved via static CDN caching.

---

### 6.3 Question 3 — Stabilizing Complex JSON Schemas & System Prompts Without Regression
**Topic Tags:** `#AutomatedPromptDiffGeneration` `#JSONSchemaDebugging` `#SinglePromptAnalysis`

* **Scenario**: A financial services firm uses Gemini 2.5 Flash to classify earnings-call transcripts into a 35-field nested JSON schema. Whenever analysts add new risk subcategories, classification consistency drops on edge-case transcripts. Junior engineers spend days tweaking the prompt by trial and error, often fixing one category while regressing three others. What is the most rigorous, automated workflow to resolve this?
  * **A.** Split the 35-field JSON schema into 35 separate sequential Gemini API calls.
  * **B.** Feed the Gemini SDK `.jsonl` request logs into `go/gemini-task-analysis` (Single-Prompt Analysis) so the tool automatically samples each transcript $n = 8$ times, evaluates both the **prompt template and input JSON schema** across divergent clusters, and generates **side-by-side rewritten prompt and schema diff suggestions**.
  * **C.** Remove the JSON schema from the API request and parse free-text Markdown outputs with regular expressions.
  * **D.** Increase the `topK` and `topP` parameters to maximum values to increase output diversity.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: In Single-Prompt Analysis, `go/gemini-task-analysis` inspects the prompt template *and* JSON schema alongside the $n = 8$ divergent outputs, clustering exact subcategory conflicts (like *Issue Mode 3*) and producing surgical side-by-side prompt/schema diffs.
  * **Why A is Incorrect**: Multiplying API calls by $35\times$ explodes latency and token cost while losing cross-field context.
  * **Why C & D are Incorrect**: Removing structured outputs or raising sampling randomness worsens schema determinism.

---

### 6.4 Question 4 — Semantic Consistency vs. Lexical String Matching in Meta-Critique
**Topic Tags:** `#SelfReflectiveGeminiCritique` `#SemanticConsistency` `#AsymmetricVerification`

* **Scenario**: An engineering lead questions how `go/gemini-task-analysis` evaluates cross-run consistency for natural language explanations when two valid runs use different phrasing (e.g., *"The query is broader than the ad"* vs. *"The user's search intent covers a wider category than the advertised product"*). How does the tool handle this?
  * **A.** It computes byte-for-byte MD5 hashes of each output and flags any hash mismatch as a failure.
  * **B.** It uses character-level Levenshtein edit distance with a hard threshold of 10 characters.
  * **C.** It uses **Gemini itself as a self-reflective meta-critic** over the $n = 8$ outputs, evaluating semantic agreement, chain-of-thought logical validity, and adherence to prompt rules rather than brittle lexical string identity.
  * **D.** It strips all natural language explanations and only evaluates integer fields.
* **Correct Answer**: **C**
* **Deep Architectural Rationale**:
  * **Why C is Correct**: `go/gemini-task-analysis` leverages Gemini's strong self-critique capability to inspect the full text and reasoning of all $n = 8$ candidates side-by-side, separating benign phrasing variance from genuine logical contradictions (such as citing `'Query More Specific'` while explaining that the query is broader).
  * **Why A, B, and D are Incorrect**: Lexical hashing/edit distance fails on natural language, and stripping explanations loses the richest diagnostic signal (*Issue Modes 3 and 4*).

---

### 6.5 Question 5 — Multi-Turn Conversational Chatbot Trajectory Sampling Strategies
**Topic Tags:** `#MultiTurnChatbots` `#BranchPointSampling` `#AgentTrajectoryObservability`

* **Scenario**: A telecommunications enterprise operates a multi-turn billing dispute chatbot. Users report that while Turns 1–4 are accurate, the agent frequently forgets billing policy constraints around Turn 6 when negotiating partial credits. How should the engineering team use `go/gemini-task-analysis` Variant 2 to debug this multi-turn conversational agent?
  * **A.** Concatenate all 6 user turns into a single giant prompt and run Variant 1 Single-Prompt Analysis without tool execution.
  * **B.** Sample $N$ trajectories through the agent harness—either by **branching $N$ runs from the specific conversational turn** where instability begins (Turn 5 $\rightarrow$ Turn 6) or by **sampling $N$ full end-to-end conversations**—serialize them into the custom trajectory `.jsonl` format, and run the GTA Trajectory HTML Report script.
  * **C.** Only evaluate Turn 1 of every conversation since subsequent turns depend on user input.
  * **D.** Clear the conversation history before every turn so every turn acts as Turn 1.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: As explicitly detailed in Slide 8 and the SME recording, GTA Variant 2 supports multi-turn conversational chatbots via two proven sampling patterns: sampling $N$ trajectories from a specific conversational step/turn, or sampling $N$ full end-to-end conversations.
  * **Why A, C, and D are Incorrect**: They destroy the multi-turn state transitions and tool call history required to diagnose Turn 6 degradation.

---

### 6.6 Question 6 — Navigating Dual-Track Tooling (`go/gemini-task-analysis` V1 vs. `go/auto-analysis` V2) for External Cloud Customers
**Topic Tags:** `#CloudOpenSourceTransition` `#DualTrackGovernance` `#AutoAnalysisV2`

* **Scenario**: As a Google Cloud Forward Deployed Engineer (FDE), you are advising a regulated banking customer who wants to run automated $n = 8$ consistency diagnostics and trajectory analysis entirely inside their own GCP project (`VPC Service Controls` perimeter) on BigQuery logs. A teammate suggests giving the customer direct access to `go/auto-analysis` (Version 2). What is the correct architectural guidance?
  * **A.** Provision an external IAM role granting the bank's engineers direct browser access to `http://auto-analysis.corp.google.com`.
  * **B.** Explain that **`go/auto-analysis` (V2) is strictly an internal Google platform with no external sharing path**, and instead deploy the **`go/gemini-task-analysis` (V1) toolkit**—which Google DeepMind has approved for **Google Cloud ownership and Open-Source (OSS) release**—directly inside the customer's Vertex AI / BigQuery environment.
  * **C.** Require the bank to email unredacted production CSV logs to Google DeepMind engineers every week.
  * **D.** Tell the customer that label-free consistency analysis cannot be performed outside `google3`.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Slides 11 and 12 explicitly establish this governance split: GDM is transitioning `go/gemini-task-analysis` (V1) to Google Cloud ownership so it can be open-sourced (OSS) for external Cloud users, whereas `go/auto-analysis` (V2) is an internal-only web app with no external sharing path.
  * **Why A, C, and D are Incorrect**: External users cannot access `corp.google.com`, emailing bank logs violates data sovereignty, and V1 is portable to GCP.

---

### 6.7 Question 7 — Diagnosing Slide 7 `Issue Mode 1`: Critical Rule Non-Adherence (`8/8` Wrong Consensus)
**Topic Tags:** `#CriticalRuleNonAdherence` `#IssueMode1` `#B2BvsB2CMismatch`

* **Scenario**: In the Slide 7 `go/gemini-task-analysis` HTML report for an ad-relevance classifier, **Issue Mode 1** flags `13 unique prompts` for: *"Failure to adhere to 'CRITICAL RULES' that mandate a 'Bad' rating for specific mismatches."* In **Prompt 4** (where a user searches for wholesale bulk supply but the ad is for a retail consumer item—a clear `'B2B/B2C Mismatch'`), **all 8 out of 8 candidates rated the ad `'Risky'` instead of `'Bad'`**. Why was `go/gemini-task-analysis` able to catch this error even though all 8 runs agreed with each other?
  * **A.** Because a human annotator manually labeled Prompt 4 as `'Bad'` prior to running the script.
  * **B.** Because the Gemini self-reflective meta-critic audits the candidate outputs and their justifications **against the explicit instruction rules in the prompt template** (which listed `'B2B/B2C Mismatch'` under `'CRITICAL RULES (Automatic Bad Ratings)'`), detecting rule non-adherence even when cross-run variance is zero.
  * **C.** Because the tool automatically rejects any prompt that outputs the word `'Risky'`.
  * **D.** Because 8/8 agreement is always classified as an error by the script.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: While cross-run variance is the primary heuristic for spotting unstable prompts, the Gemini meta-critic also evaluates candidate reasoning against the prompt template's stated rules—catching cases where a buried `'CRITICAL RULE'` is systematically overridden by later general guidelines across all 8 runs.
  * **Why A, C, and D are Incorrect**: Zero human labels are used, `'Risky'` is a valid rating for other prompts, and 8/8 agreement is normally desired when rules are followed.

---

### 6.8 Question 8 — Diagnosing Slide 7 `Issue Mode 3`: Nuanced Subcategory Reasoning Contradictions
**Topic Tags:** `#NuancedSubcategoryErrors` `#IssueMode3` `#ChainOfThoughtCritique`

* **Scenario**: During a review of Slide 7's `Potential Issue Modes`, your team inspects **Issue 3 (`15 unique prompts`)**: *"Incorrect application of nuanced rule subcategories, leading to flawed or imprecise reasoning, even when the final rating might be directionally correct."* In **Prompt 0**, Candidate 1 outputs a `'Good'` rating citing the `'Query More Specific'` rule, even though its own explanation states that the query (`'home builder'`) is *broader* than the ad (`'custom home builder'`). Why should architects fix this if the final rating (`'Good'`) is already directionally acceptable?
  * **A.** They should ignore it; only final rating labels matter in production.
  * **B.** Flawed internal chain-of-thought reasoning proves the subcategory definitions (`'Query More Specific'` vs. `'Query Broader'`) are ambiguous in the prompt; leaving the contradiction unfixed causes unstable rating flips on adjacent inputs and corrupts audit explanations shown to downstream users.
  * **C.** Because Gemini cannot process the words "broader" and "specific" in the same prompt.
  * **D.** Because `Prompt 0` is a reserved system test that must always be deleted.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Getting the right rating for the wrong reason is a classic symptom of prompt boundary ambiguity. Fixing the subcategory rule definitions ensures both reasoning integrity and rating stability across the broader input distribution.
  * **Why A, C, and D are Incorrect**: Ignoring broken reasoning leads to production drift, and Gemini easily handles specificity hierarchy once instructions are disambiguated.

---

### 6.9 Question 9 — Interpreting the Slide 7 Per-Prompt Candidate Quality Stacked Area Chart
**Topic Tags:** `#PerPromptVisualization` `#CandidateQualityChart` `#TailIsolation`

* **Scenario**: You open the `Per-prompt Visualization` (`Candidate quality assessment per prompt`) chart in the `go/gemini-task-analysis` HTML report for a 100-prompt evaluation cohort ($n = 8$ candidates per prompt). Prompts 1 through 65 display a solid green band from 0 to 8, while Prompts 68 through 100 show a sharp drop in green and a large expansion of yellow (`Fair`) and red (`Poor`) bands up to 8 candidates. How should your engineering team use this chart?
  * **A.** Rewrite the prompt from scratch and discard all 100 test cases.
  * **B.** Focus engineering triage immediately on **Prompts 68–100** (the high-disagreement / `Fair` & `Poor` tail) to identify what input characteristics or edge-case rules cause candidate quality to collapse, while using **Prompts 1–65** as a non-regression consensus baseline when testing prompt diffs.
  * **C.** Only inspect Prompt 1 because it is on the far left of the chart.
  * **D.** Reduce $n$ from 8 to 1 so the yellow and red bands disappear.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Sorting prompts by candidate quality distribution ($n = 8$) visually separates the 65% stable core from the ~32% unstable tail, enabling surgical debugging of the failing cohort while guarding against regression on the green consensus cohort.
  * **Why A, C, and D are Incorrect**: They waste the diagnostic localization provided by the sorted distribution chart.

---

### 6.10 Question 10 — Why Single-Pass Auto-Raters (`02. Auto-Raters`) Fail as Standalone Diagnostic Tools
**Topic Tags:** `#AutoRaterLimitations` `#Slide2ProblemStatement` `#RootCauseDiagnosis`

* **Scenario**: According to Slide 2 of the O2 DeepMind Troubleshooting Tool presentation (*"The Problem: Moving Beyond Error Detection to Deep Diagnosis"*), why are standard LLM **Auto-Raters (`02. Auto-Raters`)** insufficient when engineering teams need to troubleshoot and fix complex prompts or agents?
  * **A.** Auto-raters require at least 10,000 human-annotated ground-truth labels per prompt before they can run.
  * **B.** While auto-raters enable rapid evaluation, **they aren't always accurate**, and more importantly, **they fail to answer *"What do you do with incorrect responses?"***—they detect *that* a response scored poorly without pinpointing *what* is broken in the instructions, tools, or agentic pathways.
  * **C.** Auto-raters can only evaluate Python code and cannot read natural language text.
  * **D.** Auto-raters automatically overwrite production prompts without human review.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Slide 2 explicitly contrasts `01. Labeled Data` (*"rarely available in production"*) and `02. Auto-Raters` (*"enable rapid evaluation, yet they aren't always accurate. What do you do with incorrect responses?"*) against GTA's goal: *"Go beyond detecting \*that\* a model is failing. Pinpoint exactly what is broken within instructions, tools, or agentic pathways."*
  * **Why A, C, and D are Incorrect**: Auto-raters do not require 10,000 labels, work on text, and do not rewrite prompts (which is actually a capability of GTA, not standard auto-raters).

---

### 6.11 Question 11 — Auditing Behavioral Integrity & Reward Hacking in `go/auto-analysis` (V2 `Cheating` Rubric)
**Topic Tags:** `#AutoAnalysisV2` `#CheatingRubric` `#RewardHackingPrevention`

* **Scenario**: An internal autonomous agent team is evaluating a new DevOps troubleshooting agent across 9 complex trajectories ($n = 9$) using **Gemini Task Analysis V2 (`go/auto-analysis`)**. During execution, the agent inspects database schemas and reads encryption key metadata files before resolving the outage. When reviewing the **`Rubrics`** tab in `go/auto-analysis` (Slide 12), how does the **`Cheating` (`DEFAULT`)** rubric evaluate this behavior?
  * **A.** It automatically flags any trajectory that runs a database query as `100% Cheating`.
  * **B.** It inspects the agent's full trajectory and `Thinking Process` to distinguish between **legitimate diagnostic exploration** (viewing schemas or key metadata to understand system limits while adhering to all task rules, yielding **`0/9 (0%)` Cheating**) versus **reward hacking / rule bypassing** (attempting to copy answers or subvert the evaluation harness).
  * **C.** It only checks whether the agent finished in under 5 seconds.
  * **D.** It disables all CLI tools before the run starts.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Slide 12 directly illustrates this exact analysis under the `Cheating (DEFAULT): 0/9 (0%)` rubric: *"The agent showed no cheating behavior in any of the trajectories. While it sometimes explored advanced diagnostic options (like viewing database schemas or encryption keys to understand system limits), it strictly adhered to the rules and never attempted to bypass the intended problem-solving process or copy answers."*
  * **Why A, C, and D are Incorrect**: They mischaracterize the semantic meta-evaluation performed by `go/auto-analysis` rubrics.

---

### 6.12 Question 12 — Auditing Agent Fault Tolerance in `go/auto-analysis` (V2 `Self-Correction Ability` Rubric)
**Topic Tags:** `#SelfCorrectionAbility` `#AutoAnalysisV2` `#CLIErrorRecovery`

* **Scenario**: In the Slide 12 `go/auto-analysis` benchmark, the evaluated agent encounters a CLI syntax error when running `find_gateway --help` and hits a missing binary path error on an initial command. Yet the agent receives a **`9/9 (100%)`** score on the **`Self-Correction Ability` (`DEFAULT`)** rubric. What trajectory behavior justifies this `100%` score, and how should architects interpret it alongside Variant 2's *Operational Inefficiencies*?
  * **A.** The `100%` score means the agent never encountered any errors on any step.
  * **B.** The `9/9 (100%)` score confirms that **whenever the agent encountered a syntax or path error, it immediately adjusted its approach, used diagnostic tools like `which` or `find` to locate executables, and successfully recovered**; architects value high *Self-Correction Ability* for runtime resilience against unexpected environment faults, while still fixing avoidable prompt/schema bugs to minimize routine *Operational Inefficiencies*.
  * **C.** The `100%` score indicates that a human engineer stepped in and typed the correct command 9 times.
  * **D.** `Self-Correction Ability` measures whether the agent corrected the user's spelling mistakes.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Slide 12 defines `Self-Correction Ability (9/9 100%)` via the agent's ability to recover autonomously from syntax (`find_gateway --help`) and path errors using `which`/`find`. Architecturally, you want an agent's *capability* to self-correct to be 100% when novel environment faults occur, while optimizing tool schemas via GTA so the agent doesn't *waste* tokens self-recovering from preventable schema errors on every routine call.
  * **Why A, C, and D are Incorrect**: Contradict the explicit Slide 12 rubric evidence.

---

### 6.13 Question 13 — Preventing Duplicate Side Effects During $N$-Run Agent Trajectory Replay
**Topic Tags:** `#IdempotentToolMocking` `#WriteToolSandboxing` `#TrajectorySafety`

* **Scenario**: An airline operations team is troubleshooting an ADK Crew-Recovery Agent (like Slide 12's `Flight FL101 LAX to JFK` pilot assignment scenario) that invokes three read tools (`get_flight_manifest`, `query_pilot_reserve_pool`, `check_faa_duty_limits`) and two state-mutating write tools (`assign_pilot_to_flight`, `send_crew_sms_alert`). To run `go/gemini-task-analysis` Variant 2 across 40 historical disruptions with $n = 8$ trajectories each, how must the test harness be architected?
  * **A.** Run all $40 \times 8 = 320$ trajectories directly against the live production crew-scheduling database and live SMS gateway during off-peak hours.
  * **B.** Configure the agent test harness to execute against read-only snapshots for the read tools and **mock or sandbox the state-mutating write tools (`assign_pilot_to_flight`, `send_crew_sms_alert`)** with deterministic state validation so the $n = 8$ replay captures authentic trajectories with zero production side effects.
  * **C.** Remove all 5 tools from the agent before running Trajectory Analysis.
  * **D.** Only run $n = 1$ trajectory per disruption so each pilot only gets one real SMS.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Multi-sample trajectory analysis ($n = 8$) requires re-executing the agent 8 times per scenario. Mocking or sandboxing write tools prevents 320 live database mutations and SMS pages while preserving full multi-step tool-calling trajectories for GTA inspection.
  * **Why A is Incorrect**: Firing 320 live crew reassignments and SMS alerts into production is a catastrophic operational anti-pattern.
  * **Why C & D are Incorrect**: Removing tools prevents trajectory analysis altogether, and $n = 1$ both fails the consistency requirement and still mutates production once.

---

### 6.14 Question 14 — Privacy-Preserving BigQuery Log Ingestion with Sensitive Data Protection (Cloud DLP)
**Topic Tags:** `#CloudDLPRedaction` `#BigQueryLogIngestion` `#WAFSecurityPrivacy`

* **Scenario**: A healthcare payer wants to use `go/gemini-task-analysis` (Variant 1 Single-Prompt Analysis) to debug a prior-authorization medical necessity prompt. Their production `generateContent` request logs in BigQuery contain Protected Health Information (PHI), including patient names, dates of birth, and member IDs. What is the Google Cloud Well-Architected best practice before running the GTA pipeline?
  * **A.** Run the raw PHI logs through `go/gemini-task-analysis` and password-protect the generated HTML report.
  * **B.** Insert a **Sensitive Data Protection (Cloud DLP)** de-identification and format-preserving surrogate tokenization step between the BigQuery log export and the `.jsonl` file generation, ensuring clinical context and prompt structure remain intact for $n = 8$ sampling while zero PHI enters the diagnostic pipeline or HTML reports.
  * **C.** Delete the user input completely and run $n = 8$ samples on an empty prompt template.
  * **D.** Encrypt the `.jsonl` file with `gzip` before passing it to the Gemini API.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Sensitive Data Protection (Cloud DLP) surrogate tokenization replaces PHI identifiers with realistic synthetic tokens (e.g., `[PATIENT_01]`, shifted dates), preserving the exact semantic relationships needed to trigger clinical reasoning edge cases without exposing PHI across $8\times$ sampling logs or static HTML reports.
  * **Why A, C, and D are Incorrect**: Password-protecting HTML does not prevent PHI replication during $8\times$ sampling; empty inputs cannot test prompt edge cases; `gzip` is compression, not de-identification.

---

### 6.15 Question 15 — FinOps Observability: Quantifying "Cost of Operational Inefficiency" with Cloud Billing & Looker Studio
**Topic Tags:** `#CloudBillingReports` `#LookerStudioDashboards` `#FinOpsROI`

* **Scenario**: After using `go/gemini-task-analysis` Variant 2 to eliminate a silent self-recovery loop in an enterprise customer support agent, your VP of Engineering asks for an executive FinOps dashboard that continuously tracks the dollar savings from reduced trajectory retries alongside ongoing offline diagnostic sampling costs. Which Google Cloud architecture delivers this?
  * **A.** Manually copy token counts from local terminal logs into a monthly slide deck.
  * **B.** Apply distinct GCP labels (`env:prod-agent` vs. `env:gta-diagnostics`) to Vertex AI API calls, monitor SKU-level spend in **Cloud Billing reports**, and join **BigQuery Cloud Billing export tables** with **GTA trajectory analysis telemetry** in **Looker Studio** to visualize the **"Cost of Operational Inefficiency"** (wasted tokens in red-flagged/self-recovery turns vs. clean first-pass resolutions) across agent releases.
  * **C.** Disable BigQuery logging to save storage costs.
  * **D.** Use Cloud DNS query logs to estimate Vertex AI token consumption.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Combining GCP resource/request labels in **Cloud Billing reports** with joined BigQuery billing + GTA trace telemetry in **Looker Studio** gives engineering and FinOps leaders real-time visibility into both the minimal offline cost of $n = 8$ diagnostics and the massive 30–60% production token savings achieved by eliminating silent retry loops.
  * **Why A, C, and D are Incorrect**: Manual tracking does not scale, disabling logs blinds observability, and Cloud DNS does not measure token SKUs.

---

### 6.16 Question 16 — Onboarding New Engineers & Using JetSki for Custom Trajectory Serialization
**Topic Tags:** `#GTAGTMOnboarding` `#JetSkiSerializer` `#DeveloperVelocity`

* **Scenario**: Two new engineers join your Google Cloud AI team. Engineer A is brand-new to `google3` and needs a step-by-step tutorial to run **Single-Prompt Analysis** on Gemini SDK logs. Engineer B needs to run **Multi-Step Agent Trajectory Analysis** on a custom ADK agent, notes that the trajectory onboarding guide in `go/GTA-GTM` is still being expanded, and needs the fastest way to format her agent's traces into the required custom `.jsonl` format. What should you direct Engineer A and Engineer B to do?
  * **A.** Tell both engineers to wait 6 months until new documentation is published.
  * **B.** Direct Engineer A to **`go/GTA-GTM`** (the step-by-step onboarding guide for engineers new to Google/`google3`), and instruct Engineer B to **point JetSki directly at her agent repository and the `go/gemini-task-analysis` codebase/docs in `google3`** to automatically generate the $N$-run sampling harness and custom trajectory `.jsonl` serializer (while joining **`go/gemini-task-analysis-chat`** for support).
  * **C.** Tell Engineer B to manually type 800 multi-turn JSON traces by hand in a text editor.
  * **D.** Tell Engineer A to use `go/auto-analysis` to write SQL queries.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Slide 9, Slide 10, and the SME recording explicitly prescribe this exact workflow: `go/GTA-GTM` is the dedicated step-by-step guide for newcomers running Single-Prompt Analysis, while pointing **JetSki** at `go/gemini-task-analysis` in `google3` is the recommended accelerator for generating custom Agent Trajectory `.jsonl` adapters, backed by `go/gemini-task-analysis-chat`.
  * **Why A, C, and D are Incorrect**: Contradict the documented onboarding resources and JetSki automation workflow.

---

### 6.17 Question 17 — Diagnosing Slide 7 `Issue Mode 2` & `Issue Mode 4` (Determinism Breakdowns & Incomplete Explanations)
**Topic Tags:** `#IssueMode2` `#IssueMode4` `#DeterministicTasks`

* **Scenario**: In the Slide 7 `go/gemini-task-analysis` report, **Issue Mode 2 (`15 unique prompts`)** reports *"High inconsistency in final ratings on deterministic tasks where HIGH_CONSISTENCY was expected"* (e.g., Prompt 1 splitting 5 `'Good'` and 3 `'Bad'`), while **Issue Mode 4 (`11 unique prompts`)** reports *"Incomplete or inconsistent explanations that fail to reference all applicable rules"* (e.g., Prompt 6 identifying `'Service Unavailable'` for `'no piercing'` but omitting `'Specific Concept Synonym'` rules for `'piercing earrings'`). What prompt engineering pattern resolves both issue modes simultaneously?
  * **A.** Delete all explanation fields from the output schema so the model only outputs a single word.
  * **B.** Apply GTA's suggested prompt diff to introduce a **structured, exhaustive checklist chain-of-thought schema** requiring the model to explicitly evaluate and cite every applicable rule category (Primary Policy, Service Availability, Concept Synonyms) in a deterministic order *before* emitting the final rating enum.
  * **C.** Lower `maxOutputTokens` to 20 tokens so explanations are cut off early.
  * **D.** Randomly shuffle the prompt paragraphs before every API call.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: When a model skips applicable secondary rules (*Issue 4*) or splits 5 `'Good'` / 3 `'Bad'` on a deterministic task (*Issue 2*), it is performing premature, unguided heuristic jumping. Enforcing a structured pre-rating rule checklist in the prompt and JSON schema forces all 8 decoding passes to evaluate every applicable rule in the same order, collapsing variance and guaranteeing complete explanations.
  * **Why A, C, and D are Incorrect**: Deleting or truncating chain-of-thought explanations actually *reduces* classification determinism on complex multi-rule rubrics.

---

### 6.18 Question 18 — Automated CI/CD Consistency Regression Gates in Cloud Build
**Topic Tags:** `#CloudBuildCICD` `#ConsistencyRegressionGate` `#AgentOpsAutomation`

* **Scenario**: Your Antigravity agentic engineering team wants to prevent developers from merging prompt or ADK tool-schema changes that degrade cross-run consistency or introduce new silent self-recovery loops. How should you architect an automated pre-merge quality gate on Google Cloud?
  * **A.** Require every developer to manually test 2 prompts in Vertex AI Studio and paste a screenshot into the Git pull request.
  * **B.** Configure a **Cloud Build** CI pipeline triggered on pull requests that executes the open-source `go/gemini-task-analysis` script ($n = 8$ samples) over a stratified 50-case canary `.jsonl` suite, failing the build if the **Deterministic Consensus Rate** drops below 92%, **Critical Rule Violations** exceed 0%, or **Red-Step Operational Inefficiencies** exceed 5%, and attaching the generated HTML diff report as a build artifact.
  * **C.** Run $n = 8$ sampling synchronously inside the live user-facing production API gateway on every customer request.
  * **D.** Only run evaluations once a year during annual compliance audits.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: Embedding `go/gemini-task-analysis` into **Cloud Build** as an offline pre-merge CI gate catches prompt/trajectory regressions and publishes the interactive HTML report before brittle changes ever reach production.
  * **Why A is Incorrect**: Manual 2-prompt spot checks miss 15–25% tail regressions.
  * **Why C is Incorrect**: Running $8\times$ sampling synchronously on every live user request needlessly multiplies production token cost by $8\times$ when GTA is designed as an offline/CI diagnostic tool.
  * **Why D is Incorrect**: Annual checks cannot prevent daily deployment regressions.

---

### 6.19 Question 19 — Detecting Silent Context Degradation in Long-Context RAG Synthesis
**Topic Tags:** `#LongContextRAG` `#GEAPLogging` `#SinglePromptAnalysis`

* **Scenario**: An enterprise legal research assistant built on **GEAP (Gemini Enterprise Agent Platform)** retrieves 15 contract clauses and synthesizes a compliance risk memo in a single `generateContent` pass. Lawyers notice that when conflicting indemnity clauses appear near the middle of the retrieved context, the memo sometimes flags high risk and sometimes reports zero risk on identical queries. How should you isolate and fix this?
  * **A.** Export the GEAP `generateContent` logs to `.jsonl`, run `go/gemini-task-analysis` Variant 1 ($n = 8$ automated samples), inspect the divergent candidate cluster where the model flips between high and zero risk, and apply the tool's prompt diff to enforce per-clause citation extraction before synthesis.
  * **B.** Truncate the retrieved RAG context to only the first 500 characters.
  * **C.** Switch from semantic vector search to random document retrieval.
  * **D.** Disable GEAP logging.
* **Correct Answer**: **A**
* **Deep Architectural Rationale**:
  * **Why A is Correct**: Slide 6 explicitly lists **GEAP logging** (alongside BigQuery and Gemini SDK) as a direct `.jsonl` input source for Variant 1 Single-Prompt Analysis. Running $n = 8$ samples exposes the exact multi-clause conflict causing variance and synthesizes a prompt diff that stabilizes attention across all retrieved chunks.
  * **Why B, C, and D are Incorrect**: They destroy retrieval recall and observability.

---

### 6.20 Question 20 — Synthesizing `go/auto-analysis` V2 `Strengths` and `Failure Modes` for Model Tier Routing
**Topic Tags:** `#ModelTierRouting` `#AutoAnalysisStrengths` `#CostPerformanceOptimization`

* **Scenario**: An internal product team wants to migrate an autonomous workflow from `gemini-2.5-pro` to `gemini-2.5-flash` to reduce latency and inference cost, but only for task categories where `gemini-2.5-flash` maintains high trajectory stability and zero rubric regressions. How can the team use **Gemini Task Analysis V2 (`go/auto-analysis`)** to design an evidence-backed model router?
  * **A.** Route 100% of traffic to `gemini-2.5-flash` immediately without testing and wait for user bug reports.
  * **B.** Run multi-trajectory evaluations for both models in `go/auto-analysis`, compare the **`Strengths`**, **`Failure Modes`**, **`Task-wise Detailed Reports`**, and **`Rubrics`** (*Cheating*, *Self-Correction Ability*) tabs across task categories, and configure the orchestrator to route tasks in the verified **`Strengths`** cohort to `gemini-2.5-flash` while retaining `gemini-2.5-pro` (and applying `Improvement Suggestions`) for tasks in the **`Failure Modes`** cohort.
  * **C.** Route requests randomly based on whether the timestamp is even or odd.
  * **D.** Use `gemini-2.5-pro` only on weekends.
* **Correct Answer**: **B**
* **Deep Architectural Rationale**:
  * **Why B is Correct**: As shown in Slide 12, `go/auto-analysis` organizes evaluation findings into five dedicated tabs: `Rubrics`, `Failure Modes`, `Strengths`, `Improvement Suggestions`, and `Task-wise Detailed Reports`. Comparing these tabs across model tiers allows architects to safely offload high-consistency `Strengths` tasks to Flash while keeping complex `Failure Modes` tasks on Pro.
  * **Why A, C, and D are Incorrect**: Arbitrary or unverified routing risks severe quality degradation on complex reasoning tasks.

---

## 7. Comprehensive Module FAQ Compendium
**Topic Tags:** `#ComprehensiveFAQ` `#DeepTechnicalFAQs` `#O2TroubleshootingCompendium`

> **Enforced FDE Project Grading Rubric Reference (`OKF-L400-21` & `g3doc/company/teams/cloud-fde`):** Every project applying Section 7 of `OKF-L400-O2` is graded against **Part A.4 (Harness Diagnostics), Part B.1.4 (Label-Free N-Run Consistency Evaluation & Trajectory Observability), Part B.2.7 (Troubleshooting Guides), Part B.4.3 (Red-Node Failure & Self-Recovery Detection), Part B.5.3 (Eliminating Trajectory Token Waste)** and merged bucket **Concepts 06, 07, 08** (`stale_after: 2027-04-26T00:00:00Z`, version `L400_version_20261026_0350`). Builders must achieve >= 2 (**Competent**) across Part A & Part B and avoid any 0 (**Not Demonstrated**) pause triggers.

### 7.1 Foundational Concepts & Consistency Heuristics (FAQs 1–5)
**Topic Tags:** `#FoundationalFAQs` `#ConsistencyHeuristic` `#LabelFreeDiagnostics`

1. **Q1: What is the core purpose of the DeepMind Troubleshooting Tool (`go/gemini-task-analysis`), and how does it differ from traditional evaluation tools?**
   * **A:** Accessible at `go/gemini-task-analysis` (with Version 2 at `go/auto-analysis`), the tool is designed to **diagnose root-cause issues in prompts, schemas, and multi-step agents without requiring human-labeled ground-truth data**. Whereas traditional evaluations (`01. Labeled Data` and `02. Auto-Raters`) focus on passive *error detection* (telling you *that* a model failed), `go/gemini-task-analysis` uses cross-run **Consensus and Disagreement** ($n = 8$) and **Gemini self-reflective meta-critique** to pinpoint *what specific component* is broken and generate actionable prompt/trajectory fixes.
2. **Q2: Why does the tool use $n = 8$ repeated runs as its standard sampling baseline?**
   * **A:** Executing the identical prompt or agent input $n = 8$ times provides an optimal statistical balance between **variance sensitivity** and **offline compute cost**. With $n = 8$ samples at non-zero temperature, even a 15–25% intermittent failure mode has a high probability ($1 - 0.8^8 \approx 83\%$) of manifesting in at least one candidate, giving the Gemini meta-critic contrasting positive and negative examples to compare side-by-side.
3. **Q3: Does "high consistency" across $n = 8$ runs always guarantee 100% factual accuracy?**
   * **A:** High consistency strongly indicates that the prompt instructions are unambiguous and the model has high structural confidence. However, a model can occasionally be *consistently wrong*—for example, if a prompt contains a flawed rule or if the model has a pre-training misconception. Importantly, `go/gemini-task-analysis` mitigates instruction-level blind spots because the Gemini meta-critic also audits the 8 outputs against the explicit rules in the prompt template (catching cases like Slide 7's *Issue Mode 1*, where 8/8 runs rated a `'B2B/B2C Mismatch'` as `'Risky'` instead of the mandated `'Bad'`). For pure external factual accuracy, teams pair GTA with a small verified golden dataset at final release gates.
4. **Q4: How can Gemini reliably critique and diagnose errors in outputs that Gemini itself generated?**
   * **A:** This relies on **asymmetric verification vs. generation**. Generating a flawless response in a single forward pass over a sprawling, ambiguous 6,000-token prompt is hard because competing rules pull attention in different directions. However, when a frontier Gemini meta-critic (`gemini-2.5-pro`) inspects **all 8 generated responses and their chain-of-thought justifications side-by-side** alongside the prompt template, contradictions between runs become explicitly visible, making root-cause localization highly accurate.
5. **Q5: Is `go/gemini-task-analysis` intended to run synchronously in the critical path of live production user traffic?**
   * **A:** No. Running every live user request 8 times synchronously would multiply production token costs by $8\times$ and increase tail latency. Instead, `go/gemini-task-analysis` is an **offline diagnostic, staging, and CI/CD regression tool** that samples historical or canary logs ($n = 8$) to fix prompts and tool schemas—which then run at $N = 1$ in live production with dramatically higher reliability and lower token waste.

---

### 7.2 Variant 1: Single-Prompt / Prompt Template Analysis (FAQs 6–10)
**Topic Tags:** `#SinglePromptFAQs` `#PotentialIssueModes` `#PromptDiffs`

6. **Q6: What are the exact 4 steps of the Single-Prompt Analysis workflow (`Variant 1`)?**
   * **A:** As defined in Slides 5 and 6:
     1. **Create `.jsonl` file**: Extract `generateContent` request logs from **BigQuery**, **Gemini SDK**, or **GEAP logging**.
     2. **Automated sampling ($N$ runs)**: The tool **automatically** executes each prompt $N$ times ($n = 8$).
     3. **Script execution (`JSONL -> HTML Report`)**: The script computes consistency, runs Gemini meta-critique, clusters issue modes, and generates prompt diffs.
     4. **Review and iterate**: Inspect the interactive HTML report, apply the rewritten prompt diff suggestions, and re-verify.
7. **Q7: What are the four `Potential Issue Modes` surfaced in the Slide 7 Single-Prompt HTML Report?**
   * **A:** In the Slide 7 benchmark, the tool synthesized four dataset-wide issue modes:
     * **Issue 1 (`13 unique prompts`)**: Failure to adhere to `'CRITICAL RULES'` mandating an automatic `'Bad'` rating (e.g., rating a `'B2B/B2C Mismatch'` as `'Risky'` 8/8 times).
     * **Issue 2 (`15 unique prompts`)**: High inconsistency on deterministic tasks where `HIGH_CONSISTENCY` was expected (e.g., splitting 5 `'Good'` vs. 3 `'Bad'`).
     * **Issue 3 (`15 unique prompts`)**: Incorrect application of nuanced rule subcategories leading to self-contradictory reasoning (e.g., citing `'Query More Specific'` while explaining the query is broader).
     * **Issue 4 (`11 unique prompts`)**: Incomplete or inconsistent explanations that fail to reference all applicable rules (e.g., omitting `'Specific Concept Synonym'` rules).
8. **Q8: How do you read the `Per-prompt Visualization` (`Candidate quality assessment per prompt`) chart in the HTML report?**
   * **A:** The x-axis orders all evaluated prompts (e.g., Prompts 1 to 100) from highest consensus on the left to lowest quality on the right, and the y-axis plots the `Number of Candidates` ($0 \to 8$) stacked into **`Good` (Green)**, **`Fair` (Yellow)**, and **`Poor` (Red)**. A wide green plateau on the left confirms stable prompts, while the yellow/red drop-off on the right immediately isolates the specific prompts requiring prompt/schema remediation.
9. **Q9: Does Single-Prompt Analysis inspect only the prompt text, or does it also analyze structured output schemas?**
   * **A:** It analyzes **both the input prompt template and the JSON/input schema**. When generating rewritten suggestions with diff views, the tool can recommend fixes to ambiguous system instructions as well as overlapping or underspecified JSON schema field descriptions and enum definitions.
10. **Q10: How many prompts should an engineering team include in a `.jsonl` file for a Single-Prompt Analysis run?**
    * **A:** A stratified cohort of **50 to 200 unique prompts** (representing diverse production inputs and suspected edge cases) is ideal. At $n = 8$ samples per prompt, 100 prompts require only 800 model inferences plus the meta-critique synthesis pass—completing in minutes for just a few dollars while providing high statistical power to cluster macro issue modes.

---

### 7.3 Variant 2: Multi-Step Agent Trajectory Analysis & JetSki (FAQs 11–15)
**Topic Tags:** `#TrajectoryAnalysisFAQs` `#JetSkiWorkflow` `#OperationalInefficiencies`

11. **Q11: How do Steps 1 and 2 of Agent Trajectory Analysis (`Variant 2`) differ from Single-Prompt Analysis (`Variant 1`)?**
    * **A:** In Variant 1, you simply provide a standard `generateContent` `.jsonl` file and the tool automatically runs the $N$ samples. In Variant 2 (Slide 8), because the tool cannot execute your custom agent orchestrator or external tools automatically:
      * **Step 1**: **You must sample $N$ trajectories through your agent + harness yourself** ($n = 8$).
      * **Step 2**: **You must serialize those captured traces into the custom trajectory `.jsonl` format yourself** (typically automated using **JetSki**).
      * Steps 3 (`JSONL -> HTML Report`) and 4 (`Review and Iterate`) then mirror Variant 1.
12. **Q12: What are the three diagnostic categories into which GTA classifies multi-step agent trajectories?**
    * **A:** As highlighted in the SME recording and Slide 8, Variant 2 categorizes findings into:
      1. **Total Agent Failures**: The agent crashes, aborts, or outputs an incorrect final response.
      2. **Operational Inefficiencies**: The agent **reaches the correct final answer**, but exhibits wasted work—such as unnecessary tool calling, poor intermediate reasoning, or failed tool calls followed by **silent self-recovery**.
      3. **General Improvement Suggestions**: Non-critical refinements to tighten prompts, tool docstrings, and context usage.
13. **Q13: How does the GTA HTML report visually display broken intermediate steps and self-recovery inside an agent trajectory?**
    * **A:** The report provides interactive **trajectory drill-down views** that highlight exact intermediate failure points (such as a malformed tool call or API error on Step 2) in **RED**, and explicitly tag cases of **self-recovery** where the agent adjusts its arguments on subsequent turns (Step 3) to recover and complete the task.
14. **Q14: Why is detecting "Operational Inefficiencies with Self-Recovery" so impactful for enterprise FinOps and latency SLOs?**
    * **A:** Because traditional outcome-based evaluations only check whether the final answer is right. If an agent fails a tool call on Step 2 and self-recovers on Step 3 in 70% of production conversations, outcome monitors report "100% success" while the enterprise unknowingly pays for **double or triple the token volume** and suffers **2–4$\times$ worse p95 latency**. Fixing the tool schema exposed by GTA's red-step drill-down eliminates the retry loop immediately.
15. **Q15: How exactly do engineers use JetSki to speed up Variant 2 Agent Trajectory Analysis setup?**
    * **A:** Engineers open **JetSki** (Google's internal AI coding assistant) in their `google3` workspace and point it at both their agent codebase and the `go/gemini-task-analysis` trajectory documentation/schema definitions. JetSki automatically generates the $N$-run replay harness, mocks mutating tools, and outputs the custom `.jsonl` trajectory serializer.

---

### 7.4 Governance, Cloud Open-Source Transition & `go/auto-analysis` V2 (FAQs 16–20)
**Topic Tags:** `#GovernanceFAQs` `#CloudOSSRelease` `#AutoAnalysisV2FAQs`

16. **Q16: What is the origin story of `go/gemini-task-analysis`, and why is ownership moving to Google Cloud?**
    * **A:** The tool was originally "vibe-coded" by Google DeepMind (GDM) researchers to accelerate their own internal prompt and agent debugging without ground-truth labels. Because Google Cloud teams and external enterprise customers needed the same capability outside `google3`, GDM partnered with Google Cloud to transfer ownership of V1 (`go/gemini-task-analysis`) so Cloud can **open-source (OSS)** and maintain it for external Cloud customers (Slide 11).
17. **Q17: What is `go/auto-analysis` (`go/autoanalysis`), and what new capabilities does Version 2 introduce over V1?**
    * **A:** `go/auto-analysis` is DeepMind's newer **Version 2** internal web platform (Slide 12). It expands on V1 by providing a rich 5-tab UI (**`Rubrics`**, **`Failure Modes`**, **`Strengths`**, **`Improvement Suggestions`**, and **`Task-wise Detailed Reports`**), default and custom behavioral rubrics (such as **`Cheating`** and **`Self-Correction Ability`**), clickable trajectory evidence badges (`[1]`–`[9]`), and an embedded **`ADE Example Viewer`** with collapsible model **`Thinking Process`** inspection.
18. **Q18: Can external Google Cloud customers access `go/auto-analysis` (V2) today?**
    * **A:** No. `go/auto-analysis` is an internal Google application (`http://auto-analysis.corp.google.com`) with no current path for external customer sharing. External customer engagements must use the V1 `go/gemini-task-analysis` architecture being open-sourced by Google Cloud.
19. **Q19: What are all the official internal go-links for onboarding, documentation, V2 access, and community support?**
    * **A:** Across Slides 1, 10, 11, and 12:
      * **`go/gemini-task-analysis`**: Main V1 tool hub, scripts, and specifications.
      * **`go/GTA-GTM` (`go/gta-gtm`)**: Step-by-step onboarding guide specifically tailored for engineers new to Google or `google3`.
      * **`go/gemini-task-analysis-chat`**: Active Google Chat channel for troubleshooting support and community Q&A.
      * **`go/auto-analysis` (`go/autoanalysis`)**: Version 2 internal web application with behavioral rubrics and the ADE Example Viewer.
20. **Q20: How does `go/gemini-task-analysis` integrate into Antigravity-driven Agentic AI development and GCP Knowledge Catalogs?**
    * **A:** In Antigravity-driven Agentic AI workflows, coding and orchestration agents consume structured OKF knowledge catalogs (tagged with `#L400_version_20261026_0350`) to autonomously instrument ADK agents with JetSki trajectory serializers, execute $n = 8$ consistency checks in Cloud Build, parse GTA HTML/JSON issue modes and red-step self-recovery traces, apply side-by-side prompt/schema diffs, and track FinOps token efficiency gains in **Cloud Billing reports** and **Looker Studio** dashboards.


---

## FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

> **Mandatory Governance Standard:** Every project, prototype, or production agent built using the patterns in this concept **must pass the [Google Cloud FDE Field-Readiness & Project Grading Rubric](/concepts/00-fde-field-readiness-and-grading-rubric.md)** (aligned with the [Cloud FDE Team Charter](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head)). Scoring Requirement: **Average >= `2.0 (Competent)`** across both **Part A (Presentation & Advisory Rigor)** and **Part B (Engineering & Implementation Excellence)**, with **zero `0 (Not Demonstrated)` scores** on any single metric.

## 8. Enforceable FDE Field-Readiness & Project Grading Rubric Alignment (`OKF-L400-21` & `g3doc/company/teams/cloud-fde`)
**Topic Tags:** `#L400_version_20261026_0350` `#FDEGradingRubric` `#FieldReadinessStandard` `#CloudFDECharter` `#BucketOKFMerge`

### 8.1 Module-Specific FDE Grading Rubric Scorecard (0–3 Scale: Part A & Part B)
**Topic Tags:** `#L400_version_20261026_0350` `#FDEGradingRubric` `#PresentationAndAdvisoryRigor` `#EngineeringAndImplementationExcellence`

Every application or architecture built using **`OKF-L400-O2` (DeepMind Troubleshooting Tool (Gemini Task Analysis / GTA))** is evaluated against the standalone **FDE Grading Rubric (`OKF-L400-21`)**. To pass field readiness, the solution must achieve an average score of **>= 2.0 (Competent)** in both **Part A (Presentation & Advisory Rigor)** and **Part B (Engineering & Implementation Excellence)** with **zero `0 (Not Demonstrated)` scores**:

| Rubric Competency (`OKF-L400-21`) | `0 - Not Demonstrated` (Automatic Pause & 2-Week Re-Present) | `1 - Awareness` (Needs Coaching) | `2 - Competent` (Field-Ready Pass) | `3 - Proficient` (L400 Strong Pass) |
| :--- | :--- | :--- | :--- | :--- |
| **Part A.1 & A.2: Strategic Value, TCO & Technical Defense** | Presents `OKF-L400-O2` as an ungrounded "science project" with no CUJ, no TCO estimate, and inability to defend trade-offs under pushback. | Names high-level benefits of `DeepMind Troubleshooting Tool (Gemini Task Analysis / GTA)` but lacks quantitative TCO math or data-backed trade-off defense. | Frames `DeepMind Troubleshooting Tool (Gemini Task Analysis / GTA)` around customer personas & Critical User Journeys (CUJs), presents a viable TCO model (`O4`), and calmly defends design choices using data-backed matrices. | Quantifies unit economics across the 16-line TCO ledger, pre-empts CISO/CFO objections with empirical ablation stats, and links ADRs directly to commercial KPIs. |
| **Part A.4: AI-Driven Development Harness (In-Loop & Out-Loop)** | Built without a pre-configured AI harness, `SKILL.md`, or automated verification loop; agent mistakes are repeated manually. | Used basic IDE autocomplete without distinguishing In-the-Loop vs. Outside-the-Loop workflows or updating instructions. | Demonstrates pre-coding harness setup (`SKILL.md` + OKF MCP `tool_filter`), executes both **In-the-Loop** (spec fixes) and **Outside-the-Loop** (goal-driven lint/test loops), and feeds agent mistakes back into instructions. | Operates a self-improving Antigravity + `GCPSkillRegistry` (`B3`, `O3`) harness with containerized TDD verifiers (`O1`) and a versioned mistake-to-`Gotchas` ledger. |
| **Part B: Core Engineering Competencies (`Part A.4 (Harness Diagnostics), Part B.1.4 (Label-Free N-Run Consistency Evaluation & Trajectory Observability), Part B.2.7 (Troubleshooting Guides), Part B.4.3 (Red-Node Failure & Self-Recovery Detection), Part B.5.3 (Eliminating Trajectory Token Waste)`)** | Ignores the production guardrails of `OKF-L400-O2`, leaving single points of failure, unscoped credentials, or unverified LLM outputs. | Understands `DeepMind Troubleshooting Tool (Gemini Task Analysis / GTA)` conceptually but misses critical production edge cases (e.g., group truncation, Confused Deputy, or context bloat). | Implements the production patterns of `OKF-L400-O2` and merged bucket `Concepts 06, 07, 08` meeting latency SLAs, least-privilege security, deterministic + autorater evaluation, and graceful degradation. | Masters all L400 edge cases in `OKF-L400-O2`, automates shift-left policy/security gates in CI/CD across Progressive Deployment Rings, and teaches the panel novel optimization insights. |
| **Part B.2: Scoping, ADRs, API Specs & Operational Runbooks** | Missing architecture/sequence diagrams, ADRs, OpenAPI/MCP/A2A contracts, or troubleshooting runbooks. | Provides high-level box diagrams without sequence flows, formal ADRs, or actionable operational runbooks. | Delivers complete Mermaid/ASCII architecture & sequence diagrams, ADRs with trade-off rationale, contract-first API/MCP schemas, and day-2 troubleshooting runbooks. | Publishes version-pinned OKF v0.2 documentation bundles (`L400_version_20261026_0350`, `stale_after: 2027-04-26T00:00:00Z`) verified by automated `skills-ref` and schema linters. |

### 8.2 Cloud-FDE Prevailing Customer Best Practices & Bucket OKF Integration (`g3doc/company/teams/cloud-fde` & `Concepts 06, 07, 08`)
**Topic Tags:** `#L400_version_20261026_0350` `#CloudFDECharter` `#BucketOKFMerge` `#PrevailingCustomerBestPractices`

In accordance with **`https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head`** and the merged Cloud Storage bucket **`gs://gea_agent_development_architectural_best_practices_1790796607`** (`Concepts 06, 07, 08`), engineers implementing `OKF-L400-O2` must follow these prevailing customer best practices while maintaining the existing TTL (`stale_after: 2027-04-26T00:00:00Z`) and version (`L400_version_20261026_0350`):
* **Enforce Architectural Separation & Progressive Disclosure (`Concepts 01, 03, 04, 05`)**: Keep MCP tools atomic and stateless (scoped via `McpToolset` `tool_filter`), package procedural reasoning in `GCPSkillRegistry` `SKILL.md` bundles (`< 5,000 tokens` Tier 2), validate OKF v0.2 frontmatter trust signals (`status`, `stale_after`, `verified`, `content_sha256`) before execution, and place static prefixes first for 75–90% Context Caching discounts.
* **Enforce Zero-Trust Gateway, PAB & Model Armor (`Concepts 13, 14, 15`)**: Register all agents, skills, and MCP servers in **Agent Registry** (`VETTED`/`PRODUCTION`), route all data-plane calls through **Enterprise Agent Gateway** over **Private Service Connect (PSC)**, bind least-privilege IAM with **Principal Access Boundaries (PAB)** and out-of-band `GcpAuthProviderScheme` token injection, and screen all inputs/outputs through **Model Armor** + **Cloud DLP**.
* **Enforce Component-Level Trajectory Eval & Progressive Rings (`Concepts 06, 07, 12`)**: Validate every skill and agent trajectory in Vertex AI Evaluation Service (`IN_ORDER` / `ANY_ORDER`, Goal Completion >92%, Tool Precision >98%, Step Token Bloat <15%, P95 Step Latency <500ms) using deterministic verifiers **beyond LLM-as-a-Judge** before promoting across `Sandbox -> SME Alpha -> Champion Beta -> Production GA` rings.

### 8.3 Zero-Score ("Pause & Re-Present") Disqualifier Checklist for `OKF-L400-O2`
**Topic Tags:** `#L400_version_20261026_0350` `#ZeroScorePauseGate` `#FDEGradingRubric`

* [ ] **Commercial & CUJ Anchoring Verified (`Part A.1` / `Part B.2.1`)**: No ungrounded "science project" elements; `OKF-L400-O2` is tied to a specific customer persona, CUJ, Definition of Done, and TCO model.
* [ ] **Pre-Coding Harness & Mistake Feedback Verified (`Part A.4`)**: Both In-the-Loop and Outside-the-Loop Antigravity harness workflows are documented, and mistakes discovered during `OKF-L400-O2` implementation were fed back into `SKILL.md` `Gotchas`.
* [ ] **Evaluation Beyond LLM-as-a-Judge Verified (`Part B.1.4`)**: Deterministic schema/code/citation verifiers and retrieval/trajectory metrics are active alongside calibrated autoraters.
* [ ] **Zero-Trust & Least Privilege Verified (`Part B.3.1`–`B.3.5`)**: No static keys/PATs; PAB, OAuth/WIF, CMEK, VPC-SC, and Model Armor guardrails are enforced.
* [ ] **ADRs, Diagrams, API Contracts & Runbooks Complete (`Part B.2.4`–`B.2.7`)**: All required design and operational artifacts for `OKF-L400-O2` are complete and pinned to `L400_version_20261026_0350`.


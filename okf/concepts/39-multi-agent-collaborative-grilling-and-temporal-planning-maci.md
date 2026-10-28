---
type: "Architecture Best Practice"
title: "Case 2B: Multi-Agent Collaborative Grilling, Constraint Satisfaction & Temporal Planning (MACI)"
description: "Authoritative architectural reference for Multi-Agent Collaborative Intelligence (MACI), detailing how a higher-order Meta-Planner (MP), context-bounded 5W Node Agents, programmatic Edge Verifier Agents, Early Information Agents, and Clean-State Resets overcome the Gödelian Self-Reference Barrier and Stale Memory Propagation in Google Cloud ADK 2.0 and A2A temporal planning workflows."
timestamp: "2026-10-27T17:27:00-07:00"
status: "stable"
stale_after: "2027-04-27T17:27:00-07:00"
ttl: "6 months (180 days / P6M)"
ttl_months: 6
ttl_days: 180
sources:
  - "MACI: Multi-Agent Collaborative Intelligence for Adaptive Reasoning and Temporal Planning (Edward Y. Chang, Stanford University, 2025)"
  - "L400_concepts/B2_OKF_A2A_Protocol_and_Multi_Agent_Mechanics.md"
  - "L400_concepts/B1_OKF_Anatomy_of_an_Enterprise_Agent.md"
generated_by: "gemini-enterprise:okf-synthesizer"
generated_at: "2026-10-27T17:27:00-07:00"
verified: "true"
corpus: "GEAPL200"
version_tag: "GEAPL200_2026-10-27_1726"
okf_module_id: "OKF-L400-S4"
l400_version_tag: "L400_version_20261027_1726"
fde_rubric_reference: "concepts/00-fde-field-readiness-and-grading-rubric.md"
fde_charter_url: "https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head"
---

# Case 2B: Multi-Agent Collaborative Grilling, Constraint Satisfaction & Temporal Planning (MACI) (`OKF-L400-S4`)

## Version & 6-Month TTL Governance Tab (`2026-10-27 17:27 PDT`)

| Governance Attribute | Authoritative Value |
| :--- | :--- |
| **Version Timestamp (Today's Date & Time)** | **`2026-10-27 17:27 PDT`** (`2026-10-27T17:27:00-07:00`) |
| **Unified Bundle Version Tag (`version_tag`)** | **`GEAPL200_2026-10-27_1726`** |
| **L400 Catalog Version Tag (`l400_version_tag`)** | **`L400_version_20261027_1726`** |
| **Socratic Pack Release Tag** | **`SOCRATIC_OKF_20261027_1726`** |
| **Time-To-Live (`ttl`)** | **`6 months (180 days / P6M)`** |
| **Expiration Timestamp (`stale_after`)** | **`2027-04-27T17:27:00-07:00`** |


## Version & 6-Month TTL Governance Tab (`2026-10-27 17:27 PDT`)

| Governance Attribute | Authoritative Value |
| :--- | :--- |
| **Version Timestamp (Today's Date & Time)** | **`2026-10-27 17:27 PDT`** (`2026-10-27T17:27:00-07:00`) |
| **Unified Bundle Version Tag (`version_tag`)** | **`GEAPL200_2026-10-27_1726`** |
| **L400 Catalog Version Tag (`l400_version_tag`)** | **`L400_version_20261027_1726`** |
| **Socratic Pack Release Tag** | **`SOCRATIC_OKF_20261027_1726`** |
| **Time-To-Live (`ttl`)** | **`6 months (180 days / P6M)`** |
| **Expiration Timestamp (`stale_after`)** | **`2027-04-27T17:27:00-07:00`** |


## Version & 6-Month TTL Governance Tab (`2026-10-27 17:27 PDT`)

| Governance Attribute | Authoritative Value |
| :--- | :--- |
| **Version Timestamp (Today's Date & Time)** | **`2026-10-27 17:27 PDT`** (`2026-10-27T17:27:00-07:00`) |
| **Unified Bundle Version Tag (`version_tag`)** | **`GEAPL200_2026-10-27_1726`** |
| **L400 Catalog Version Tag (`l400_version_tag`)** | **`L400_version_20261027_1726`** |
| **Socratic Pack Release Tag** | **`SOCRATIC_OKF_20261027_1726`** |
| **Time-To-Live (`ttl`)** | **`6 months (180 days / P6M)`** |
| **Expiration Timestamp (`stale_after`)** | **`2027-04-27T17:27:00-07:00`** |


## 1. Executive Summary & Architectural Thesis

While **Case 2A (`OKF-L400-S3`)** addresses multi-agent Socratic grilling across competing *normative and axiomatic value frameworks*, **Case 2B (`OKF-L400-S4`)** addresses the complementary operational frontier: **Agent-Grills-Agent for Adaptive Reasoning, Combinatorial Constraint Satisfaction, and Dynamic Temporal Planning**.

Drawing upon **Edward Y. Chang (2025)** (*MACI: Multi-Agent Collaborative Intelligence for Adaptive Reasoning and Temporal Planning*, Computer Science Department, Stanford University), this module establishes why standalone Large Language Models—even frontier reasoning models equipped with Chain-of-Thought (CoT) or Tree-of-Thoughts (ToT) prompting—systematically fail on multi-threaded sequential and reactive scheduling tasks. Operating as probabilistic System 1 pattern-matchers rather than deliberative System 2 constraint solvers, standalone LLMs suffer from two fatal cognitive pathologies:
1. **The Gödelian Self-Reference Barrier**: Because generation and self-critique occur within the same probabilistic context and latent belief state, an LLM cannot reliably verify the consistency of its own generated plan (e.g., **GPT-4o** generating a reactive schedule with an unattended 4-hour oven fire hazard, a 7:00 PM deadline breach, and a 30-minute arithmetic fallacy, and **insisting it has "zero violations" when prompted to self-verify**, whereas **Claude** immediately identifies GPT-4o's errors when acting as an external critic).
2. **Stale Memory Propagation & Attention Narrowing**: When a dynamic disruption occurs (such as a 3-hour flight delay) and an LLM attempts to patch its schedule in-context, attention narrows onto the disrupted thread while eroding global safety invariants and carrying over invalidated timing assumptions from prior iterations.

To overcome these barriers on **Google Cloud Agent Development Kit (ADK 2.0)** (`B1`) and the **Agent-to-Agent (A2A) Protocol** (`B2`), **MACI** introduces a **Higher-Order Meta-Planner ($\mathcal{MP}: (\mathcal{O}, \mathcal{C}_E) \to \mathbf{W}^* = (\mathcal{N}, \mathcal{E})$)** that compiles unstructured planning objectives into a directed graph of **context-bounded ($w \le 1\text{k}$ tokens) Role-Specific Node Agents ($\mathcal{N} = A_n^*$)** spanning the **5W1H dimensions (Who, Where, When/Temporal, What, Why, How)**, continuously grilled by cognitively isolated **Programmatic and Specialized Edge Verifier Agents ($\mathcal{E} = A_e^*$)** enforcing atomic pre/mid/post validation gates ($\text{validate}(s_t \to s_{t+1})$, Eq. 6), continuous buffer/threshold monitoring ($\Delta t = t_{\text{planned}} - t_{\text{actual}}$, Eq. 16), upstream **Early Information Alerting ($f_{\text{early}}$, Eq. 20)**, and **Clean-State Context Resets (Eq. 19)**.

---

## 2. Structural Cognitive Deficits in Standalone LLM Planners

### 2.1 The Gödelian Self-Reference Barrier (Why Planners Cannot Grade Their Own Homework)
By analogy to **Gödel's Second Incompleteness Theorem**—which proves that no consistent formal system $\mathcal{F}$ capable of expressive arithmetic can prove its own consistency ($\text{Cons}(\mathcal{F})$) without ascending to a higher-order metasystem $\mathcal{F}' \supset \mathcal{F}$—MACI demonstrates that an autoregressive LLM cannot objectively validate a schedule inside the same generative context that produced it.

* **Empirical Asymmetry Between Self-Verification and Cross-Agent Grilling**:
  * In MACI's Multi-Actor Thanksgiving Planning benchmark (Section 3 & Appendix E), **GPT-4o**, **DeepSeek**, and **Claude** all fail to generate valid standalone sequential or reactive plans.
  * Yet when **Claude** is instantiated as an *external critic* with an isolated context window to evaluate schedules produced by **GPT-4o** or **DeepSeek**, Claude effortlessly detects DeepSeek's spatial teleportation error and GPT-4o's round-trip arithmetic and fire-safety violations.
  * Conversely, in **Table 16 (Appendix E.8.2)**, when **GPT-4o** is given the revised reactive problem specification ($\mathbf{W}^R$) after a 3-hour flight delay, it commits three severe violations simultaneously: (1) it dispatches Sarah to Boston Logan Airport (BOS) at 2:30 PM while nobody is home to supervise the oven; (2) it starts the 4-hour turkey at 3:00 PM, completing at 7:00 PM and violating the hard 6:00 PM dinner deadline; and (3) it computes the 60-minute BOS-to-Home drive as 30 minutes (3:30–4:00 PM). When the human operator explicitly prompts GPT-4o in-context to *"review your schedule and identify any constraint violations,"* **GPT-4o exhibits irrecoverable metacognitive blindness, asserting that its plan satisfies $100\%$ of constraints with zero violations**.
* **Architectural Mandate**: Self-reflection prompting ("check your work") inside a monolithic planner is an enterprise anti-pattern. Validation **must** be executed by an external higher-order metasystem—specifically, cognitively isolated **Edge Verifier Agents ($A_e^*$)** and deterministic constraint solvers (`O1`, `O6`) that share zero generative memory with the Node Planner.

### 2.2 Stale Memory Propagation & Attention Narrowing During Reactive Replanning
When a real-world schedule experiences a mid-execution shock (e.g., James's flight from SFO to BOS is delayed by 3 hours, shifting arrival from 1:00 PM to 4:00 PM EST), standalone LLMs fail due to two coupled context-window pathologies:
1. **Attention Narrowing (Constraint Erosion)**: As the LLM focuses attention heads on resolving the acute disruption (re-routing airport pickups for Emily at 2:30 PM and James at 4:00 PM), attention weights decay on background global invariants:
   * **DeepSeek (Standalone Reactive, §3.2)** arbitrarily pushes the immutable 6:00 PM Thanksgiving dinner deadline to 7:00 PM.
   * **GPT-4o (Standalone Reactive, Table 3)** focuses on picking up Grandma at 3:00–4:00 PM and dispatches Sarah from home while the turkey is roasting in the oven, creating a **severe unattended fire hazard**.
2. **Stale Memory Propagation (Appendix E.8.2 & E.9.1)**: When an iterative planner fails on iteration $k$ and appends the failed schedule plus error critique into a growing multi-turn conversation history, the model inherits **stale timing anchors and invalidated dependency assumptions** from iteration $k-1$. Rather than re-optimizing the future subgraph from scratch, the LLM performs local token patching around broken time slots.
   * **MACI's Clean-State Reset Solution**: MACI enforces **Selective Constraint Invalidation**. When a runtime violation or early upstream alert triggers replanning at time $t_{\text{alert}}$, the Meta-Planner locks all tasks already executed prior to $t_{\text{alert}}$ as immutable historical facts ($\mathcal{C}_{\text{locked}}$), **completely flushes the conversational scratchpad of all unexecuted future nodes**, and re-instantiates optimization from a clean state with updated constraints $\mathcal{C}_{\text{updated}}$.

### 2.3 Omission of Implicit Real-World Logistics ($\mathcal{C}_I$)
Standalone LLMs treat prompt numbers literally, ignoring physical and human operational realities unless explicitly told:
* If a flight lands at BOS Terminal B at 1:00 PM and home is 60 minutes away, standalone LLMs schedule the passenger arriving home at 2:00 PM—ignoring **30 minutes for baggage claim** and **30 minutes for rental car shuttle/pickup**.
* Standalone LLMs also conflate **Roles** (`Cook`, `Supervisor`, `Driver1`, `Driver2`) with **People** (`Sarah`, `James`, `Michael`, `Emily`, `Grandma`), rigidly assuming Sarah must stay in the kitchen for all 4 hours rather than recognizing that once Grandma arrives at home, Grandma can assume the `Supervisor` role to watch the oven while Sarah drives.

| Failure Mode / Hallucination | Concrete Manifestation in Standalone Frontier LLMs | How MACI's Agent-Grills-Agent Protocol Surfaces & Resolves It |
| :--- | :--- | :--- |
| **Spatial Discontinuity ("Teleportation")** | **DeepSeek (Table 1)** schedules James to arrive home at 2:00 PM to start the oven, then teleports him back to BOS airport at 3:00 PM to pick up Emily (violating the 60m Home $\to$ BOS travel time). | **Spatial Edge Agent (`location_track()`)** enforces continuous coordinate continuity ($\text{loc}(p, t)$) across the distance matrix $D$. It flags `route_feasible() == false`, forcing $\mathcal{MP}$ + DeepSeek (Table 12) to keep James idle at BOS from 2:00–3:00 PM to pick up Emily. |
| **Arithmetic / Round-Trip Fallacy** | **GPT-4o (Table 2)** schedules Michael to depart home at 5:00 PM to pick up Grandma (30m one-way) and return home at 5:30 PM ($30\text{m}$ allotted for a $2 \times 30\text{m} = 60\text{m}$ round trip). | **Temporal Edge Agent (`schedule_monitor()`)** sums directed spatial edges ($\text{Home} \to \text{Grandma} + \text{Grandma} \to \text{Home} = 60\text{m}$), rejecting the 30m slot via `timing_feasible() == false`. |
| **Safety Constraint Erosion & Metacognitive Blindness** | **GPT-4o (Table 3 & Table 16)** sends Sarah away from home (3:00–4:00 PM or 2:30 PM) while the turkey is in the oven (**Fire Hazard**) and claims **zero violations** when self-queried. | **Supervisor Node Monitor** + **Compliance & Safety Edge Agent (`safety_state()`)** enforce the invariant $\forall t \in [t_{\text{oven\_start}}, t_{\text{oven\_end}}], \exists p \in \mathcal{P} : \text{loc}(p, t) = \text{Home}$. Leaving without a validated `cooking_handoff()` triggers `coverage_gap()` and atomic rollback ($\text{validate} = \text{false}$, Eq. 6). |
| **Role-Person Conflation & Solution Rigidity** | All standalone models lock Sarah to the house and route Michael Home first ($\text{NYC} \to \text{Home} \to \text{BOS}$) instead of routing directly to the airport. | **Role Manager Agent** decouples abstract roles $n_i \in \mathcal{N}$ from actors $p \in \mathcal{P}$ via $f_{\text{role}}(n, \mathcal{P})$, enabling **DeepSeek + $\mathcal{MP}$ (Table 19)** to route Michael directly $\text{NYC} \to \text{BOS}$ at 3:00 PM after the 10:00 AM Early Alert. |

---

## 3. The MACI Meta-Planner ($\mathcal{MP}$) Node-and-Edge Graph Architecture

MACI replaces monolithic prompt engineering with a formal **Three-Component Architecture** operating over a **5W1H Multi-Agent Graph**.

### 3.1 The Three Architectural Pillars of MACI
1. **The Higher-Order Meta-Planner ($\mathcal{MP}$)**: A graph compiler $\mathcal{MP}: (\mathcal{O}, \mathcal{C}_E) \to \mathbf{W}^* = (\mathcal{N}, \mathcal{E})$ that ingests raw task objectives ($\mathcal{O}$) and explicit constraints ($\mathcal{C}_E$), invokes pre-planning grilling to expand the constraint set with implicit common-sense constraints ($\mathcal{C}_I$) and derived interaction dependencies ($\mathcal{C}_D$), extracts role qualifications, and synthesizes an executable workflow graph $\mathbf{W}^*$.
2. **Protocol-Buffer Agent Repository ($\mathbf{A}$)**: A catalog of lightweight, context-bounded agents ($w \le 1\text{k}$ tokens) registered via standardized **Protocol Buffers**. Each agent entry $A_i \in \mathbf{A}$ specifies six formal attributes:
   * **$P$ (Input/Output Protocol)**: Typed state-machine contract defining input payloads, state transitions, validation predicates, and output alert channels.
   * **$t$ (Agent Type)**: `common` (domain-agnostic 5W managers and systemic validators) vs. `specialized` (domain solvers such as Ant Colony Optimization or airport traffic estimators).
   * **$c$ (Capability Vector)**: Functional competencies, constraint specialties, and operating preconditions.
   * **$w$ (Context Window Ceiling)**: Hard cap of **$w \le 1\text{k}$ tokens** per agent to guarantee razor-sharp attention and eliminate context pollution.
   * **$e$ (Computational Efficiency)**: Latency and memory envelope.
   * **$r$ (Historical Rating)**: Empirical reliability score used to rank candidate agents.
3. **Run-Time Monitor & Recovery Substrate**: Executes message passing, enforces atomic multi-dimensional state transitions, monitors upstream event streams via the **Early Information Agent**, and executes **Clean-State Re-Optimization ($\mathbf{W}^R$)**.

### 3.2 The 5W1H State Space & Taxonomy of Node Agents ($\mathcal{N}$) vs. Edge Verifier Agents ($\mathcal{E}$)
Every planning problem is projected onto the **5W1H dimensions**—partitioned into **Node Agents ($A_n^*$)** that manage role/state execution and **Edge Verifier Agents ($A_e^*$)** that grill inter-node transitions and enforce global constraints:

| 5W1H / System Dimension | MACI Agent Name | Graph Role ($\mathcal{N}$ vs. $\mathcal{E}$) | Protocol Buffer Methods & Validation Predicates (Table 11) | Core Grilling & Verification Responsibility |
| :--- | :--- | :---: | :--- | :--- |
| **1. Who (Actors)** | **Role Manager Agent** (`Cook`, `Supervisor`, `Driver1`, `Driver2`) | **Node ($\mathcal{N}$)** | `cooking_handoff(task, duration, reqs)`<br/>`pickup_handoff(location, time, passenger)` | Maps actors $p \in \mathcal{P}$ to roles $(n_i, q_i)$ via $f_{\text{role}}(n, \mathcal{P})$; verifies qualifications (driver's license, rest state) and handoff completeness. |
| **2. Where (Location)** | **Spatial Agent** (`e_spatial`) | **Edge ($\mathcal{E}$)** | `location_track(actor, position, dest)`<br/>`Validate: route_feasible()`<br/>`Alert: travel_delay()` | Tracks continuous actor coordinates (`idle -> moving -> arrived`); grills proposed transitions against asymmetric/symmetric distance matrices $D$ and prevents teleportation. |
| **3. When (Time)** | **Temporal Agent** (`e_temporal`) | **Edge ($\mathcal{E}$)** | `schedule_monitor(event, time, dependencies)`<br/>`Validate: timing_feasible()`<br/>`Alert: delay_impact()` | Enforces start/end bounds, round-trip arithmetic, luggage/rental buffers, and continuous deviation classification ($\Delta t = t_{\text{planned}} - t_{\text{actual}}$, Eq. 16). |
| **4. What (Resources)** | **Resource Agent** (`e_resource`) | **Edge ($\mathcal{E}$)** | `resource_alloc(actor, vehicle, kitchen_slot)`<br/>`Validate: capacity_feasible()` | Prevents vehicle capacity overflow, double-booked rental cars, and kitchen workspace contention. |
| **5. Why (Logic & Safety)** | **Reasoning, Explanation & Compliance/Safety Agents** (`e_safety`) | **Edge ($\mathcal{E}$)** | `safety_state(condition, location, actors)`<br/>`Validate: safety_check()`<br/>`Alert: safety_violation()` | Enforces hard safety invariants (`secure -> warning -> violation`, e.g., continuous human supervision while oven is active) and logs causal trade-off rationales. |
| **6. How (Method & Implicit Context)** | **Common Sense Agent, Algorithm Selection Agent & Early Info Agent** | **Meta / Pre-Plan & Edge ($\mathcal{E}$)** | `f_early(E_upstream) -> alerts`<br/>`select_solver(N, D) -> {BruteForce, ACO, MILP}` | Surfaces implicit logistics ($\mathcal{C}_I$), routes combinatorial sub-problems to exact/ACO solvers, and intercepts upstream flight delays at departure time (10:00 AM). |

### 3.3 Two-Stage Common-Sense Discovery & Partitioned Verification (Autonomous vs. HITL Grilling)
Before generating any schedule, MACI's **Common Sense Integration Agent** grills the raw user specification $(\mathcal{O}, \mathcal{C}_E)$ to uncover unstated real-world bottlenecks ($\mathcal{C}_I$). Crucially, MACI partitions the verification of these candidate implicit constraints into two channels (Appendix E.2.3–E.2.4):
1. **Agent-Quantifiable Constraints (Autonomous Information Agents)**: Empirical logistics—such as United Airlines' average baggage claim delay at BOS Terminal B ($30\text{ mins}$), terminal-to-rental-center shuttle time ($30\text{ mins}$), and historical Thanksgiving traffic—are resolved autonomously by specialized data agents without bothering the user.
2. **Human-in-the-Loop (HITL) Interrogation (Non-Quantifiable Preferences & Capabilities)**: Interpersonal and household capability questions cannot be guessed by an LLM. The Meta-Planner grills the human user **once up-front**, discovering four critical facts injected into the Revised Specification $\mathbf{W}^*$:
   * *New Dependency 3*: One person can simultaneously prepare the turkey and side dishes.
   * *New Dependency 4*: Grandma prefers Michael to pick her up (provided it does not delay the 6:00 PM dinner).
   * *New Dependency 5*: Grandma and Sarah prefer not to cook together in the kitchen.

---

## 4. Formal Mathematical Formulations & Algorithmic Specifications

MACI formalizes its compilation, validation, and dynamic recovery mechanics across **Equations (1)–(20)** and **Algorithms 1–2**.

### 4.1 Meta-Planner Graph Compilation & Three-Step Agent Matching (Equations 1–5 & 12–14)
Given planning objectives $\mathcal{O}$ and explicit constraints $\mathcal{C}_E$, the higher-order Meta-Planner $\mathcal{MP}$ compiles a directed workflow graph $\mathbf{W}^*$:

$$\mathcal{MP} : (\mathcal{O}, \mathcal{C}_E) \to \mathbf{W}^* = (\mathcal{N}, \mathcal{E}), \quad \text{where } \mathcal{N} = A_n^*, \; \mathcal{E} = A_e^* \qquad \text{(Eq. 1)}$$

1. **Role & Qualification Extraction (Eq. 2)**:
   $$\text{map}_{\text{role}} : \mathcal{O} \to \{(n_i, q_i)\}_{i=1}^{|\mathcal{N}|}$$
   where $n_i \in \{\text{cook}, \text{driver}_1, \text{driver}_2, \text{supervisor}\}$ (Eq. 12) and $q_i$ encodes required qualifications.
2. **Global Constraint Expansion & Dependency Identification (Eq. 3)**:
   $$\mathcal{C} = \mathcal{C}_E \cup \mathcal{C}_I \cup \mathcal{C}_D, \qquad \mathcal{E} = \{e_{\text{temporal}}, e_{\text{spatial}}, e_{\text{safety}}\} \qquad \text{(Eq. 3, 12)}$$
3. **Node & Edge Agent Selection via Three-Step Repository Matching (Eq. 4–5 & 13–14)**:
   For each role node $n_j \in \mathcal{N}$ and dependency edge $e_{jk} \in \mathcal{E}$, $\mathcal{MP}$ queries repository $\mathbf{A}$ using a 3-step pipeline—(i) **Capability Matching** ($\text{dist}(q_j, A_i.c) < \epsilon$), (ii) **Protocol Compatibility Verification** ($A_i.P_{\text{out}} \preceq A_k.P_{\text{in}}$), and (iii) **Efficiency/Rating Ranking** ($\max (r_i, e_i)$):

   $$A_n^* = \bigcup_{j=1}^{|\mathcal{N}|} \left\{ A_i \in \mathbf{A} \;\middle|\; \text{dist}(q_j, A_i.c) < \epsilon \;\land\; \max_{A_i}(r_i) \right\} \qquad \text{(Eq. 4, 13)}$$

   $$A_e^* = \left\{ A_i \in \mathbf{A} \;\middle|\; \text{match}(A_i, \mathcal{E}) \;\land\; \text{compatible}(A_i.P, A_n^*) \right\} \qquad \text{(Eq. 5, 14)}$$

### 4.2 Atomic State Validation, Buffer Monitoring & Clean-State Dynamic Recovery (Equations 6–7 & 15–20)
Every candidate state transition $s_t \to s_{t+1}$ proposed by a Node Agent is intercepted by the Edge Verifier Agents before commit:

1. **Atomic Multi-Dimensional Validation Gate (Eq. 6)**:
   $$\text{validate}(s_t \to s_{t+1}) = \begin{cases} \text{true} & \text{if all pre-, mid-, and post-checks pass across } \mathcal{E} \\ \text{false} & \text{if any check fails (triggers immediate atomic rollback)} \end{cases} \qquad \text{(Eq. 6)}$$
   * **Pre-Validation Check**: Polls `timing_feasible()`, `route_feasible()`, and actor qualifications $q_i$.
   * **Mid-Transition Atomic Check**: Evaluates concurrent cross-dimensional invariants (e.g., if `e_temporal` approves Sarah's pickup window, but `e_safety` detects an unattended active oven without a completed `cooking_handoff()`, the entire transition is aborted).
   * **Post-Validation Rollback & Recovery (Eq. 7)**:
     $$\text{recover}(s_t, s_{\text{failed}}) \to s_{\text{valid}} \qquad \text{(Eq. 7)}$$

2. **Continuous Buffer & Threshold Monitoring (Eq. 15–16)**:
   During execution, Edge Agents continuously evaluate schedule adherence by comparing planned timestamp $t_{\text{planned}}$ against actual telemetry $t_{\text{actual}}$:

   $$\text{monitor} : \text{State} \to \{\text{normal}, \text{warning}, \text{violation}\} \qquad \text{(Eq. 15)}$$

   $$\Delta t = t_{\text{planned}} - t_{\text{actual}} \implies \begin{cases} \text{normal} & \text{if } |\Delta t| < \text{buffer} \\ \text{warning} & \text{if } \text{buffer} \le |\Delta t| < \tau \\ \text{violation} & \text{if } |\Delta t| \ge \text{threshold } \tau \end{cases} \qquad \text{(Eq. 16)}$$

3. **Early Upstream Information Detection & Three-Phase Dynamic Re-Optimization (Eq. 17–20)**:
   Instead of waiting until 1:00 PM EST to discover that James's flight from SFO has not landed at BOS, MACI's **Early Information Agent** monitors upstream departure events at 10:00 AM EST:

   $$f_{\text{early}} : \mathcal{E}_{\text{upstream}} \to \text{alerts} \qquad \text{(Eq. 20)}$$

   When an upstream alert or threshold violation ($|\Delta t| \ge \tau$) fires on dependency edge $e$, $\mathcal{MP}$ executes a 3-Phase Dynamic Adjustment:
   * **Phase 1 — Cascade Impact Assessment (Eq. 17)**:
     $$\text{impact}(e) = \sum_{n \in \text{affected}(e)} \text{severity}(n) \times \text{urgency}(n) \qquad \text{(Eq. 17)}$$
   * **Phase 2 — Minimum-Cost Feasible Solution Synthesis (Eq. 18)**:
     $$S^* = \arg\min_{s \in \text{Solutions}} \left\{ \text{cost}(s) \;\middle|\; \text{feasible}(s) \right\} \qquad \text{(Eq. 18)}$$
   * **Phase 3 — Clean-State Workflow Coordination Update (Eq. 19)**:
     $$\text{update} : (\mathbf{W}_{\text{current}}, S^*) \to \mathbf{W}_{\text{new}} \text{ (or } \mathbf{W}^R\text{)} \qquad \text{(Eq. 19)}$$

### 4.3 Traveling Salesperson Problem (TSP) & Ant Colony Optimization Formulation (Equations 8–11)
For combinatorial routing over $N$ locations with distance matrix $D$, $\mathcal{MP}$ instantiates $\mathcal{N} = \{n_{\text{route}}, n_{\text{dist}}, n_{\text{valid}}\}$ (Eq. 8), $\mathcal{E} = \{e_{\text{spatial}}, e_{\text{sequence}}, e_{\text{complete}}\}$ (Eq. 9), and objective function $V(\mathbf{W}, \mathcal{M}) = -\text{tour\_length}$ if valid else $-\infty$ (Eq. 10). While $\mathcal{MP}$ selects exact Brute Force for $N=5$ ($(5-1)!/2 = 12$ tours, finding the $24\text{ min}$ optimum), for $N \ge 10$ it dynamically delegates to an **Ant Colony Optimization (ACO)** solver agent ($100$ ants, $50$ iterations, evaporation $\rho = 0.1$, $\alpha = 1$, $\beta = 2$, heuristic visibility $\eta_{ij} = 1/D_{ij}$):

$$P_{ij} = \frac{[\tau_{ij}]^\alpha [\eta_{ij}]^\beta}{\sum_{k \in \text{allowed}} [\tau_{ik}]^\alpha [\eta_{ik}]^\beta} = \frac{[\tau_{ij}]^1 [1/D_{ij}]^2}{\sum_{k \in \text{allowed}} [\tau_{ik}]^1 [1/D_{ik}]^2}, \qquad \tau_{ij} \leftarrow (1 - \rho)\tau_{ij} + \sum_{k=1}^{m} \frac{10}{L_k}$$

---

## 5. Comprehensive Empirical Benchmarks (TSP & Multi-Actor Thanksgiving Planning)

### 5.1 Benchmark Suite 1: Asymmetric Campus Tour TSP ($N = 10$, Ground-Truth Optimal = 60 Minutes)

| Planner / Model Configuration | Tour Length Achieved | Optimality Gap vs. 60m | Selected Optimization Strategy | Iterations to Converge | Diagnostic Root Cause & Agent-Grills-Agent Intervention |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **Claude (Standalone)** | $92 \to 66\text{ mins}$ | $+10.0\%$ *(Suboptimal)* | Nearest Neighbor (Greedy) | 3 | Prematurely abandoned exact search for a greedy heuristic without deliberation; committed distance-matrix reading errors. |
| **GPT-4o (Standalone)** | $75 \to 68\text{ mins}$ | $+13.3\%$ *(Suboptimal)* | Genetic Algorithm | 3 | Formulated termination criteria but failed to implement exact DP or tune meta-heuristic parameters to reach 60m. |
| **DeepSeek (Standalone)** | **$60\text{ mins}$** | **$0.0\%$ *(Optimal)*** | Held-Karp Exact DP ($O(N^2 2^N)$) | **1** | Calculated that $N=10$ requires only $\sim 0.2\text{s}$ for exact DP; optimal at $N=10$ but exponential memory/time for larger $N$. |
| **$\mathcal{MP}$ + Claude (MACI)** | $66 \to \mathbf{60\text{ mins}}$ | **$0.0\%$ *(Optimal)*** | Ant Colony Optimization (ACO) | 2 | $\mathcal{MP}$'s `n_valid` and `PlanEvaluationAgent` grilled the 66m tour at Iteration 1, forcing ACO parameter refinement to hit 60m. |
| **$\mathcal{MP}$ + GPT-4o (MACI)** | **$60\text{ mins}$** | **$0.0\%$ *(Optimal)*** | Ant Colony Optimization (ACO) | **1** | Achieved exact 60m optimum in 1 pass once $\mathcal{MP}$ compiled the structured ACO workflow ($4\times$ faster than brute force). |
| **$\mathcal{MP}$ + DeepSeek (MACI)** | **$60\text{ mins}$** | **$0.0\%$ *(Optimal)*** | Ant Colony Optimization (ACO) | **1** | Combined $\mathcal{MP}$'s scalable ACO selection with DeepSeek's parameter synthesis to converge in 1 pass. |

### 5.2 Benchmark Suite 2: Multi-Actor Thanksgiving Sequential ($\mathbf{W}^*$) & Reactive 3-Hr Delay ($\mathbf{W}^R$) Planning

* **Scenario Parameters**: 5 actors (`Sarah` at home; `James` landing BOS at 1:00 PM [delayed to 4:00 PM in Study #2]; `Emily` landing BOS at 2:30 PM; `Michael` arriving from NYC at 3:00 PM; `Grandma` 30m from home / 60m from BOS). Tasks: 4-hour turkey roasting requiring continuous home supervision; 2-hour side dishes; 30m luggage + 30m car rental buffers at BOS; strict **6:00 PM dinner deadline**.

| Study Condition | Foundation Model | Standalone LLM (Without $\mathcal{MP}$) | With MACI Meta-Planner ($\text{LLM} + \mathcal{MP}$) | Key Architectural Outcomes & Diagnostic Insights |
| :--- | :--- | :--- | :--- | :--- |
| **Study #1: Sequential Planning ($\mathbf{W}^*$)** | **DeepSeek** | **FAILED** (Table 1): Omitted airport buffers; teleported James from Home (2:00 PM) to BOS (3:00 PM). | **PASSED in 2 Iterations** (Table 4 & Table 12): $100\%$ constraints met. | **Global Optimum Schedule**: Kept James waiting at BOS (2:00–3:00 PM) after renting car to pick up Emily; all actors home by 4:00 PM (**2 hours slack** before 6:00 PM dinner). |
| | **GPT-4o** | **FAILED** (Table 2): Omitted luggage/rental buffers; committed 30m round-trip arithmetic error for Grandma pickup. | **PASSED in 3 Iterations** (Table 4 & Table 13): $100\%$ constraints met. | Valid schedule, though lower slack: had James drive home empty at 2:00 PM while assigning Michael two back-to-back trips (BOS 3:00–5:00 PM, Grandma 5:00–6:00 PM). |
| | **Claude** | **FAILED** (§3.1): Omitted implicit airport logistics and failed multi-thread temporal alignment. | **PASSED in 2 Iterations** (Table 4 & Table 14): $100\%$ constraints met. | Valid schedule with 30m slack (all home by 5:30 PM), though James drove Home (2:00–3:00 PM) and immediately returned to BOS (3:00–5:00 PM) for Emily. |
| **Study #2: Reactive Planning (3-Hr SFO Flight Delay $\to 4:00\text{ PM}$, $\mathbf{W}^R$)** | **DeepSeek** | **FAILED** (§3.2): Violated hard deadline by pushing Thanksgiving dinner from 6:00 PM to 7:00 PM. | **PASSED in 3 Iterations** (Table 5 & Table 19): $100\%$ constraints met. | **Best Reactive Adaptation**: Exploited $\mathcal{MP}$'s **10:00 AM Early Information Alert** to route Michael *directly from NYC to BOS airport* (arriving 3:00 PM for Emily), then picking up Grandma (4:00–5:00 PM). |
| | **GPT-4o** | **FAILED** (Table 3): Severe **Safety Hazard**—sent Sarah to pick up Grandma (3:00–4:00 PM) while turkey was in the oven. | **FAILED ($\times$)** (Table 5 & Table 16): Committed 3 violations & failed self-recognition. | Under manual self-verification prompting, GPT-4o sent Sarah to BOS at 2:30 PM (unattended oven), started 4h turkey at 3:00 PM (finishing 7:00 PM), computed BOS-Home as 30m, and **claimed zero violations**—proving external Edge Verifiers (Eq. 6) are mandatory. |
| | **Claude** | **FAILED** (§3.2): Spotted errors in peer models' plans as an external critic, but failed self-verification on its own plan. | **PASSED in 3 Iterations** (Table 5 & Tables 17–18): Produced **2 valid plans**. | **Plan #1 (Table 17)** overloaded Michael with 3 trips; **Plan #2 (Table 18)** balanced driver fatigue by having James pick up Emily at 5:00 PM (Emily waits 2h at BOS). |

---

## 6. Google Cloud ADK 2.0 & A2A (`B1` / `B2` / `O1` / `O6`) Production Architecture

MACI's separation of higher-order meta-planning, protocol-buffer agent registries, context-bounded node agents, and deterministic edge verifiers maps directly to **Google Cloud ADK 2.0** (`B1`) and **A2A** (`B2`).

### 6.1 Architectural Diagram 1: MACI Meta-Planner ($\mathcal{MP}$) & ADK 2.0 `DynamicNode` Graph Topology

```mermaid
flowchart TB
    subgraph Inputs["1. Task Specification & Upstream Event Streams"]
        O["Objectives (O) & Explicit Constraints (C_E)"]
        P["Actors / People (P) & Metrics (M)"]
        Up["Upstream Telemetry Stream (E_upstream)<br/>e.g. SFO Departure Logs @ 10:00 AM EST"]
    end

    subgraph Repo["2. A2A AgentCard & Protocol Buffer Registry (A: P, t, c, w <= 1k, e, r)"]
        direction LR
        NodePool["5W Role Node Agents (A_n):<br/>• CookAgent (n_cook)<br/>• SupervisorAgent (n_supervisor)<br/>• DriverAgents (n_driver1, n_driver2)"]
        EdgePool["Programmatic Edge Verifiers (A_e):<br/>• TemporalVerifier (e_temporal)<br/>• SpatialVerifier (e_spatial)<br/>• SafetyVerifier (e_safety)<br/>• ResourceVerifier (e_resource)"]
        SolverPool["Specialized & Pre-Plan Agents:<br/>• CommonSenseAgent (C_I)<br/>• ACO / CP-SAT SolverAgent<br/>• EarlyInfoAgent (f_early)"]
    end

    subgraph MP["3. ADK 2.0 Meta-Planner (DynamicNode Graph Compiler: MP(O, C_E) -> W*)"]
        direction TB
        PreAug["Stage 0: Pre-Planning Grilling (Pattern O6)<br/>• Autonomous Data Agents (BOS luggage/shuttle)<br/>• Single Up-Front HITL Interrogation<br/>• Expand C = C_E U C_I U C_D (Eq. 3)"]
        Phase1_2["Phases 1 & 2: Role Extraction & 3-Step Matching<br/>• map_role: O -> {(n_i, q_i)} (Eq. 2)<br/>• Match Capability c, Protocol P, Rating r (Eq. 4-5)"]
        Phase3["Phase 3: Clean-State Iterative Refinement Loop<br/>• Propose State Transition s_t -> s_{t+1}<br/>• Enforce w <= 1k Scoped Context Ceiling (Pattern B2)"]
        PreAug --> Phase1_2 --> Phase3
    end

    subgraph Runtime["4. Deterministic Edge Verification Gate (Pattern O1) & Reactive Recovery (W^R)"]
        Gate["Atomic Transition Validator (Eq. 6)<br/>validate(s_t -> s_{t+1}) in {true, false}<br/>• Pre-Check: qualifications & buffers<br/>• Mid-Check: oven safety & vehicle capacity<br/>• Post-Check: recover(s_t, s_failed) -> s_valid (Eq. 7)"]
        Monitor["Continuous Buffer Monitor & Clean-State Reset<br/>• Δt = t_planned - t_actual -> {normal, warning, violation} (Eq. 16)<br/>• Impact: sum(severity * urgency) (Eq. 17)<br/>• Lock Executed Nodes + Flush Future Context -> W^R (Eq. 19)"]
        Gate --> Monitor
    end

    O & P --> PreAug
    Repo -->|Instantiate Scoped Sub-Agents| Phase1_2
    Phase3 <-->|Staged Transition vs. Atomic Rollback| Gate
    Up -->|f_early Alert @ 10:00 AM (Eq. 20)| Monitor
    Monitor -->|Selective Constraint Invalidation & Clean-State Reset| Phase3
```

### 6.2 Architectural Diagram 2: Atomic Pre/Mid/Post Edge Grilling & 10:00 AM Proactive Flight-Delay Recovery Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Operator as Human Operator (HITL)
    participant Early as EarlyInfoAgent (f_early)
    participant MP as ADK Meta-Planner (DynamicNode)
    participant Node as 5W Node Agents (w <= 1k tokens)
    participant Edge as Programmatic Edge Verifiers (Temporal / Spatial / Safety)

    Note over Operator,Edge: STAGE 1: PRE-PLANNING COMMON-SENSE GRILLING & HITL AUGMENTATION (Pattern O6)
    MP->>Edge: Query CommonSenseAgent & BOS Airport Info Agent on raw prompt (O, C_E)
    Edge-->>MP: Inject C_I: +30m Terminal B luggage claim, +30m rental car shuttle
    MP->>Operator: Single Up-Front HITL Grill: interpersonal & kitchen concurrency rules?
    Operator-->>MP: 1 person can cook turkey+sides; Grandma prefers Michael; Sarah & Grandma don't co-cook
    MP->>MP: Compile Revised Specification W* = (N, E) with C = C_E U C_I U C_D

    Note over MP,Edge: STAGE 2: ATOMIC STATE TRANSITION GRILLING (OVERCOMING GÖDELIAN BARRIER)
    Node->>Edge: Propose Candidate Transition s_t -> s_{t+1} (e.g., GPT-4o schedules Sarah for 3:00 PM pickup)
    Edge->>Edge: Pre-Check: timing_feasible() & route_feasible()
    Edge->>Edge: Mid-Check: safety_state() -> VIOLATION! Oven active 1:30-5:30 PM with Home empty!
    Edge-->>Node: validate(s_t -> s_{t+1}) == FALSE (Eq. 6) -> Atomic Rollback (Eq. 7: coverage_gap())
    Node->>Edge: Re-propose with Role Handoff: James waits at BOS (2:00-3:00 PM) for Emily; Sarah stays Home
    Edge-->>MP: validate() == TRUE -> Commit Optimal Baseline Workflow W* (All home by 4:00 PM)

    Note over Early,Edge: STAGE 3: 10:00 AM UPSTREAM ALERT & CLEAN-STATE REACTIVE RE-OPTIMIZATION (W^R)
    Early->>MP: 10:00 AM EST Alert (f_early, Eq. 20): James SFO->BOS delayed 3 hrs (New arrival: 4:00 PM)
    MP->>Edge: Compute Cascade Impact: sum(severity * urgency) (Eq. 17)
    Edge-->>MP: Critical violation (|Δt| = 180m >= τ) on 1:00 PM rental car & Emily 2:30 PM pickup
    MP->>MP: CLEAN-STATE RESET (Eq. 19): Lock pre-10:00 AM state; FLUSH unexecuted future context buffers
    MP->>Node: Re-instantiate Node Agents with clean context + updated C_updated
    Node->>Edge: Propose W^R: Route Michael directly NYC -> BOS (3:00 PM Emily pickup) -> Grandma (4:00-5:00 PM)
    Edge-->>MP: validate() == TRUE (100% constraints satisfied, 6:00 PM dinner preserved)
```

### 6.3 Production Python Implementation: ADK 2.0 `DynamicNode` Meta-Planner, Deterministic Edge Verifiers & Clean-State Reset

The following production architecture implements MACI in **Google Cloud ADK 2.0** (`B1`, `B2`, `O1`, `O6`). Notice how **Node Planners are never permitted to self-verify**; every candidate schedule emitted by an `LlmAgent` is intercepted by deterministic Python Edge Verifiers (`TemporalEdgeVerifier`, `SpatialEdgeVerifier`, `SafetyEdgeVerifier`), and any failed iteration or upstream disruption triggers a **Clean-State Context Reset** (`flush_stale_scratchpad_and_replan`) so failed drafts never pollute subsequent iterations.

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple
from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event


@dataclass
class AgentRegistrationCard:
    """Protocol Buffer / A2A AgentCard Entry A_i in Repository A (P, t, c, w <= 1k, e, r)."""
    agent_id: str
    role_dimension: Literal["who", "where", "when", "what", "why", "how"]
    graph_role: Literal["node", "edge"]
    input_protocol: str
    output_protocol: str
    agent_type: Literal["common", "specialized"]
    capabilities: List[str]
    max_context_tokens: int = 1000   # Hard MACI ceiling: w <= 1k tokens
    efficiency_score: float = 0.95
    rating: float = 0.98


@dataclass
class ScheduledTaskEvent:
    actor: str
    role: str                        # "cook" | "supervisor" | "driver1" | "driver2"
    task_name: str
    origin: str
    destination: str
    start_min: int                   # Minutes from 00:00 (e.g., 13:00 = 780, 18:00 = 1080)
    end_min: int
    oven_active: bool = False


class DeterministicMACIEdgeVerifier:
    """Implements MACI's Higher-Order Metasystem (Eq. 6, Eq. 7, Eq. 15, Eq. 16).
    Never lets the LLM planner grade its own homework (eliminates GPT-4o Table 16 blindness)."""

    def __init__(
        self,
        distance_matrix: Dict[Tuple[str, str], int],
        hard_deadline_min: int = 1080,  # 6:00 PM (18:00 = 1080 mins)
        airport_buffer_min: int = 60,   # 30m luggage + 30m rental/pickup buffer
        warning_buffer_min: int = 15,
        violation_threshold_tau: int = 30,
    ):
        self.D = distance_matrix
        self.hard_deadline_min = hard_deadline_min
        self.airport_buffer_min = airport_buffer_min
        self.warning_buffer_min = warning_buffer_min
        self.tau = violation_threshold_tau

    def classify_temporal_deviation(
        self, t_planned: int, t_actual: int
    ) -> Literal["normal", "warning", "violation"]:
        """Implements Equation (16): Delta_t = t_planned - t_actual."""
        delta_t = abs(t_planned - t_actual)
        if delta_t < self.warning_buffer_min:
            return "normal"
        elif delta_t < self.tau:
            return "warning"
        return "violation"

    def validate_schedule_atomic(
        self, events: List[ScheduledTaskEvent], oven_window: Tuple[int, int]
    ) -> Tuple[bool, List[str]]:
        """Implements Equation (6): validate(s_t -> s_{t+1}) across e_temporal, e_spatial, e_safety."""
        violations: List[str] = []

        # 1. Temporal Edge Check (e_temporal): Hard 6:00 PM deadline & duration arithmetic
        for ev in events:
            if ev.end_min > self.hard_deadline_min:
                violations.append(
                    f"[e_temporal] HARD_DEADLINE_VIOLATION: Task '{ev.task_name}' by {ev.actor} "
                    f"ends at {ev.end_min} > {self.hard_deadline_min} (6:00 PM)."
                )
            if ev.origin != ev.destination:
                required_travel = self.D.get((ev.origin, ev.destination), 0)
                allotted = ev.end_min - ev.start_min
                if allotted < required_travel:
                    violations.append(
                        f"[e_temporal/e_spatial] ARITHMETIC_DURATION_ERROR: {ev.actor} allotted "
                        f"{allotted}m for {ev.origin}->{ev.destination} (requires {required_travel}m)."
                    )

        # 2. Spatial Edge Check (e_spatial): Continuous actor coordinate tracking (No Teleportation)
        by_actor: Dict[str, List[ScheduledTaskEvent]] = {}
        for ev in sorted(events, key=lambda x: x.start_min):
            by_actor.setdefault(ev.actor, []).append(ev)

        for actor, seq in by_actor.items():
            for i in range(len(seq) - 1):
                curr_ev, next_ev = seq[i], seq[i + 1]
                if curr_ev.destination != next_ev.origin:
                    violations.append(
                        f"[e_spatial] SPATIAL_TELEPORTATION_ERROR: {actor} at '{curr_ev.destination}' "
                        f"at {curr_ev.end_min}m cannot teleport to '{next_ev.origin}' at {next_ev.start_min}m."
                    )
                if curr_ev.end_min > next_ev.start_min:
                    violations.append(
                        f"[e_temporal] OVERLAPPING_TASK_CONFLICT: {actor} double-booked between "
                        f"'{curr_ev.task_name}' and '{next_ev.task_name}'."
                    )

        # 3. Compliance & Safety Edge Check (e_safety): Continuous home supervision during 4-hr oven window
        oven_start, oven_end = oven_window
        for minute in range(oven_start, oven_end, 15):
            supervisors_at_home = [
                ev.actor for ev in events
                if ev.start_min <= minute < ev.end_min
                and ev.origin == "Home" and ev.destination == "Home"
                and ev.role in ("cook", "supervisor")
            ]
            if not supervisors_at_home:
                violations.append(
                    f"[e_safety] UNATTENDED_OVEN_FIRE_HAZARD: No qualified Cook/Supervisor at Home "
                    f"at minute {minute} while turkey is roasting ({oven_start}..{oven_end})."
                )
                break

        return (len(violations) == 0, violations)


class MACICleanStateMetaPlannerAgent(BaseAgent):
    """ADK 2.0 Custom DynamicNode Orchestrator implementing Algorithm 1 (MP) & Clean-State Reset (Eq. 19).
    Enforces w <= 1k token scoped context per Node Agent and zero Stale Memory Propagation."""

    planner_llm: LlmAgent
    edge_verifier: DeterministicMACIEdgeVerifier
    max_refinement_iterations: int = 3

    async def _run_async_impl(self, ctx: InvocationContext):
        state = ctx.session.state

        # Stage 0: Compile Global Constraint Set C = C_E U C_I U C_D (Eq. 3)
        explicit_c: List[str] = state.get("explicit_constraints", [])
        implicit_c: List[str] = state.get("implicit_common_sense_constraints", [
            "BOS luggage claim requires 30 minutes after landing.",
            "BOS rental car pickup requires 30 minutes after luggage claim.",
            "One person can simultaneously prepare turkey and side dishes.",
            "Grandma prefers Michael to pick her up if dinner is not delayed.",
        ])
        committed_history: List[Dict[str, Any]] = state.get("committed_history", [])
        upstream_alerts: List[str] = state.get("upstream_early_alerts", [])

        # Phase 3 Iterative Refinement with Clean-State Reset on Failure or Disruption
        structured_feedback: List[str] = []
        for iteration in range(1, self.max_refinement_iterations + 1):
            # CRITICAL (Pattern B2 / Eq. 19): Wipe transient scratchpad before each iteration
            # to prevent Stale Memory Propagation from prior failed schedules.
            state["scoped_node_prompt"] = {
                "iteration": iteration,
                "max_tokens": 1000,
                "locked_historical_events": committed_history,
                "active_constraints": explicit_c + implicit_c,
                "upstream_proactive_alerts": upstream_alerts,
                "external_edge_verifier_violations": structured_feedback,
            }

            async for event in self.planner_llm.run_async(ctx):
                yield event

            candidate_events: List[ScheduledTaskEvent] = state.get("staged_schedule_events", [])
            oven_window: Tuple[int, int] = state.get("staged_oven_window", (810, 1050))

            # Atomic Edge Verification Gate (Eq. 6)
            is_valid, violations = self.edge_verifier.validate_schedule_atomic(
                candidate_events, oven_window
            )
            if is_valid:
                state["committed_workflow_w_star"] = candidate_events
                state["validation_status"] = "PASSED_100_PERCENT"
                break
            else:
                # Atomic Rollback (Eq. 7): Do NOT commit staged_schedule_events; pass only
                # structured violation predicates into the next clean-state iteration.
                state["staged_schedule_events"] = []
                structured_feedback = violations
                state["validation_status"] = f"FAILED_ITERATION_{iteration}"
```

---

## 7. FDE Project Grading Rubric Enforcement & Prevailing Customer Alignment

In accordance with the **Google Cloud FDE Field Readiness & Grading Rubric (`concepts/00-fde-field-readiness-and-grading-rubric.md`)** and the [Cloud FDE Charter](https://g3doc.corp.google.com/company/teams/cloud-fde/index.md?cl=head), every customer deployment of **Case 2B (Multi-Agent Collaborative Grilling & Temporal Planning via MACI)** is audited against four mandatory architectural gates:

| FDE Grading Dimension | Mandatory Architectural Invariant (`OKF-L400-S4`) | Prevailing Customer Alignment & Verification Gate | Disqualifying Anti-Pattern (Automatic Rubric Failure) |
| :--- | :--- | :--- | :--- |
| **1. Gödelian Separation of Planner & Verifier (`O1`)** | Planning Node Agents ($A_n^*$) and Edge Verifier Agents ($A_e^*$) must be strictly isolated. Hard temporal, spatial, arithmetic, and safety invariants must be verified via deterministic callbacks (`DeterministicMACIEdgeVerifier`, CP-SAT/OR-Tools) or zero-shared-context Critic Agents ($\text{validate}(s_t \to s_{t+1})$, Eq. 6). | Eliminates the **GPT-4o Table 16 Metacognitive Blindness** failure mode in enterprise supply-chain, clinical scheduling, and cloud migration runbooks where standalone LLMs claim "zero violations" on hazardous schedules. | Using self-reflection prompts ("check your own schedule for errors") inside the same LLM context that generated the plan. |
| **2. Scoped $w \le 1\text{k}$ Context & Clean-State Reset (`B2`)** | Each 5W Node Agent must operate under a scoped context ceiling ($w \le 1\text{k}$ tokens) via typed Protocol Buffer / A2A contracts (`B1`/`B2`). On any failed validation iteration or reactive disruption, the orchestrator must lock already-executed events and **flush unexecuted future scratchpads** (Eq. 19). | Prevents **Stale Memory Propagation** and **Attention Narrowing** during dynamic incident recovery ($\mathbf{W}^R$), ensuring background safety invariants (e.g., continuous supervision / change-freeze windows) are never eroded. | Appending failed schedules and multi-turn error critiques into an ever-growing conversational history buffer. |
| **3. Pre-Planning Implicit Constraint Compilation (`O6`)** | Workflows must execute a **Pre-Planning Augmentation Stage** before scheduling: autonomous data agents resolve quantifiable buffers (e.g., baggage/shuttle/API latency) while a single up-front HITL gate resolves non-quantifiable policy/interpersonal preferences ($\mathcal{C} = \mathcal{C}_E \cup \mathcal{C}_I \cup \mathcal{C}_D$, Eq. 3). | Raises multi-actor sequential planning success from **$0\%$ (0/3 standalone frontier models)** to **$100\%$ (3/3 models passing in 2–3 iterations)** while avoiding mid-execution human interruptions. | Jumping directly from an underspecified user prompt to schedule generation without expanding implicit physical and operational buffers. |
| **4. Proactive Upstream Alerting & Solver Delegation (`DynamicNode`)** | The ADK orchestrator must subscribe to upstream event streams via an **Early Information Agent ($f_{\text{early}}$, Eq. 20)** to convert late reactive crises into proactive re-optimizations, and dynamically delegate $N \ge 10$ combinatorial sub-graphs to specialized solvers (e.g., ACO, Eq. 8–11). | Achieves **$0.0\%$ optimality gap on $N=10$ TSP ($60\text{m}$ vs. $66\text{–}68\text{m}$ standalone)** with a $4\times$ speedup over brute force, and enables **DeepSeek + $\mathcal{MP}$** to proactively re-route actors 3 hours before a delayed flight lands. | Waiting for a downstream task timeout to trigger replanning, or relying on unguided LLM token generation to solve NP-hard routing matrices. |

---

## Authoritative Research Publications & Bibliographic Provenance (8 Source Papers)

| Paper # | Workspace PDF Filename | Full Bibliographic Citation (Authors, Title, Venue, Year, Identifier) | Mapped OKF Concept & L400 Module | Primary Socratic Grilling Mode & Architectural Contribution |
| :---: | :--- | :--- | :--- | :--- |
| **Paper 1** | `Heterogeneous Debate Engine- Identity-Grounded Cognitive Architecture for Resilient LLM-Based Ethical Tutoring.pdf` | **Masłowski, J., & Chudziak, J. A. (2026).** *Heterogeneous Debate Engine: Identity-Grounded Cognitive Architecture for Resilient LLM-Based Ethical Tutoring.* Institute of Computer Science, Warsaw University of Technology. `arXiv:2603.27404v1 [cs.AI]` (March 28, 2026). | **`Concept 38`** (`OKF-L400-S3`) · `S3_OKF_Agent_Grills_Agent_Heterogeneous_Debate_and_Identity_Grounding.md` | **Agent-Grills-Agent & Moderator-Grills-User:** Orthogonal Axiom-Level Heterogeneity, SPIFFE-isolated Identity-Grounded RAG (`ChromaDB` / Vertex AI Vector Search), and Theory-of-Mind (ToM) Socratic Moderator preventing sycophancy (`SysAR = 0.90`, `ArCo = 0.44`). |
| **Paper 2** | `KELE- A Multi-Agent Framework for Structured Socratic Teaching with Large Language Models.pdf` | **Peng, X., Yuan, P., Li, D., Cheng, J., Fang, Q., & Liu, Z. (2025).** *KELE: A Multi-Agent Framework for Structured Socratic Teaching with Large Language Models.* National Engineering Research Center of Educational Big Data, Central China Normal University. *Findings of the Association for Computational Linguistics: EMNLP 2025*, pp. 16342–16362 (Nov 2025). | **`Concept 37`** (`OKF-L400-S2`) · `S2_OKF_Agent_Grills_User_Structured_Socratic_Inquiry_KELE.md` | **Agent-Grills-User (Chatbot & Tutoring):** Consultant–Teacher (`A_c` + `A_t`) multi-agent split, `SocRule` 5-stage monotonic progression (`a -> b -> c -> d -> e`), 34/43 pedagogical strategies, and strict **No Direct Answer Rate (`NDAR`)** anti-leakage guardrails. |
| **Paper 3** | `MACI- Multi-Agent Collaborative Intelligence for Adaptive Reasoning and Temporal Planning.pdf` | **Chang, E. Y. (2025).** *MACI: Multi-Agent Collaborative Intelligence for Adaptive Reasoning and Temporal Planning.* Department of Computer Science, Stanford University. `arXiv:2501.16689v2 [cs.AI]` (January 28, 2025). | **`Concept 39`** (`OKF-L400-S4`) · `S4_OKF_Multi_Agent_Collaborative_Grilling_and_Temporal_Planning_MACI.md` | **Agent-Grills-Agent (Collaborative Planning & Verification):** Overcomes the **Gödelian Self-Reference Barrier** and **Stale Memory Propagation** via the Meta-Planner (`MP`) 6W directed graph (`What, Where, When, Who, How, Why`), Programmatic Edge Verifiers (`Δt`), and Clean-State Context Resets. |
| **Paper 4** | `Prompting Large Language Models With the Socratic Method.pdf` | **Chang, E. Y. (2023).** *Prompting Large Language Models With the Socratic Method.* Department of Computer Science, Stanford University. *IEEE 13th Annual Computing and Communication Workshop and Conference (CCWC)*, March 2023, pp. 350–360; `arXiv:2303.08769v2 [cs.LG]`. | **`Concept 36`** (`OKF-L400-S1`) · `S1_OKF_Socratic_Prompting_Foundations_and_CRIT_Taxonomy.md` | **Both (`Agent-Grills-User` & `Agent-Grills-Agent`):** 11-strategy Socratic Prompting Taxonomy (Type 2 Focused vs. Type 3 Exploratory), the **CRIT (Critical Reading Inquisitive Template)** mathematical claim/source verification algorithm (`γ_r, θ_r, Γ`), and Psychological Safety Asymmetry. |
| **Paper 5** | `Socratic Students- Training Language Models to Ask Better Questions for Reasoning.pdf` | **Ambati, R. B., Niu, T., Singh, A., Mishra, S., Chaturvedi, S., & Srivastava, S. (2026).** *Socratic Students: Training Language Models to Ask Better Questions for Reasoning.* UNC Chapel Hill & Meta. `arXiv:2512.13102v4 [cs.AI]` (January 6, 2026). | **`Concept 37` & `Concept 41`** (`OKF-L400-S2`, `OKF-L400-S6`) | **Both (`Assessment Timing` & `ODQS Policy Optimization`):** Domain-adaptive **`PRE-ASSESSMENT` (Turn 0, +21.5% Math)** vs. **`MID-ASSESSMENT` (Turn 2, +12.8% Coding)**, **`SCAFFOLDED`** 3-part inquiry, and **Outcome-Driven Question Optimization (`SELF-ODQS` / `PEER-ODQS`)** via SFT+DPO on downstream `Pass@k` (+54.7% math, +22.9% code, **3 fewer turns**). |
| **Paper 6** | `Socratic Style Chain-of-Thoughts Help LLMs to be a Better Reasoner.pdf` | **Pei, J., Liu, P., Zhao, W. X., Men, A., & Liu, Y. (2025).** *Socratic Style Chain-of-Thoughts Help LLMs to be a Better Reasoner (`SoDa`).* UIBE, Renmin University of China, BUPT, & UC Santa Cruz. *Findings of the Association for Computational Linguistics: ACL 2025*, pp. 12384–12395 (July 2025). | **`Concept 40`** (`OKF-L400-S5`) · `S5_OKF_Recursive_Socratic_Questioning_and_SoDa_Chain_of_Thought.md` | **Agent-Grills-Agent (Socratic CoT Distillation & In-Trajectory Critique):** Socratic Teacher (`R_S`) grilling Student (`R_u`) across **8 Socratic Principles** (*Clarifying Concepts, Probing Assumptions, Probing Rationale, Questioning Viewpoints, Probing Implications, Questioning the Question, Encouraging Reflection, Challenging Logic*), achieving `9.72x` IQPT at 3% data volume. |
| **Paper 7** | `SOCREVAL- Large Language Models with the Socratic Method for Reference-Free Reasoning Evaluation.pdf` | **He, H., Zhang, H., & Roth, D. (2024).** *SOCREVAL: Large Language Models with the Socratic Method for Reference-Free Reasoning Evaluation.* University of Rochester, Tencent AI Lab, & University of Pennsylvania. *Findings of the Association for Computational Linguistics: NAACL 2024*; `arXiv:2310.00074v3 [cs.CL]`. | **`Concept 41`** (`OKF-L400-S6`) · `S6_OKF_Socratic_Autoraters_SOCREVAL_and_Outcome_Driven_Question_Optimization.md` | **Agent-Grills-Agent (Reference-Free Socratic Autorater):** Combines *Definition* + *Dialectic* (generating independent pseudo-reference `"own response"`) + *Maieutics* (step-by-step `"qualitative analysis"`) with weakest-link `min` aggregation (`E_chain(R) = min_j e(s_j)`), boosting human correlation +45% (`0.82` GSM8K) and CI/CD pass/fail accuracy from `69%` to `80%` at `< 2.1x` cost. |
| **Paper 8** | `The Art of SOCRATIC QUESTIONING- Recursive Thinking with Large Language Models.pdf` | **Qi, J., Xu, Z., Shen, Y., Liu, M., Jin, D., Wang, Q., & Huang, L. (2023).** *The Art of SOCRATIC QUESTIONING: Recursive Thinking with Large Language Models.* Virginia Tech, Amazon Inc., & Meta AI. *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP 2023)*, pp. 4177–4199 (Dec 2023). | **`Concept 40`** (`OKF-L400-S5`) · `S5_OKF_Recursive_Socratic_Questioning_and_SoDa_Chain_of_Thought.md` | **Agent-Grills-Agent (Recursive Divide-and-Conquer Tree):** Alternates **Top-Down Recursive Questioning Decomposition (`QG`)** and **Bottom-Up Hint-Guided Synthesis (`QA2H`)** gated by Answerer confidence (`low | medium | high`), bounded by max tree depth `d_m` and turn horizon `t_m`. |

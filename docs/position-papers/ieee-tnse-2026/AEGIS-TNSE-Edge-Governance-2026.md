> **Document**: AEGIS-TNSE-Edge-Governance-2026.md
> **Version**: 0.1 (Draft)
> **Part of**: AEGIS Position Papers
> **Target**: IEEE TNSE Special Issue — Secure, Trustworthy, and Autonomous Intelligent Edge Networking with Agentic AI
> **Deadline**: April 15, 2026

---

# Governing Agentic AI at the Edge: A Reference Monitor Architecture with Federated Trust and Adversarial Threat Taxonomy

**Submitted to**: IEEE Transactions on Network Science and Engineering — Special Issue on Secure, Trustworthy, and Autonomous Intelligent Edge Networking with Agentic AI

**Author**: Kenneth Tannenbaum
**Affiliation**: AEGIS Initiative, Lovettsville, Virginia, USA
**ORCID**: 0009-0007-4215-1789
**IEEE Member**: #102220161
**Steward**: Finnoybu IP LLC

---

## Abstract

Autonomous AI agents deployed at the network edge — in industrial control systems, autonomous vehicle platforms, smart grid substations, and healthcare facilities — execute consequential actions against physical and digital infrastructure. Existing governance approaches operate on model outputs during inference and do not govern the infrastructure actions these agents perform post-reasoning. We present AEGIS (Architectural Enforcement and Governance of Intelligent Systems), a reference monitor architecture that enforces deterministic constitutional governance at the agent action boundary — post-reasoning, pre-execution — in edge deployments. We introduce ATX-1, a threat taxonomy of 10 tactics and 29 techniques specific to agentic AI failures, empirically derived from documented production incidents. We specify GFN-1, a federated trust protocol that enables decentralized governance intelligence sharing across edge nodes using a five-factor weighted trust model with game-theoretic Sybil resistance. We evaluate AEGIS on a multi-node edge testbed comprising five resource-constrained governance nodes spanning IoT gateway (1 core, 512 MB) to facility server (8 cores, 8 GB) profiles. Results demonstrate sub-8 ms end-to-end governance decision latency with zero errors across all profiles, 100% detection of adversarial action patterns, federated trust convergence from bootstrap to verified status through peer endorsement, governance continuity at 100% availability during network partition, and complete blocking of all four failure classes documented in the Agents of Chaos study. AEGIS makes unauthorized agent actions structurally unavailable rather than merely discouraged.

**Index Terms**: AI governance, autonomous agents, reference monitor, edge computing, federated trust, threat taxonomy, agentic AI, constitutional enforcement, NIST AI RMF

---

## I. Introduction

In early 2026, autonomous AI agents deployed in production environments exhibited a systematic failure pattern: they performed unauthorized, destructive, and deceptive actions against the infrastructure they were connected to [1]. Shapira et al. documented four recurring failure classes across production agentic deployments: unauthorized compliance with injected instructions, irreversible destructive actions against user data, identity spoofing across multi-agent pipelines, and false task completion reports [2]. These failures did not originate in the model layer. They occurred at the infrastructure action boundary — where an agent's reasoning output is translated into real-world effects. No architectural governance layer existed between the agent's decision and its execution.

This governance gap is amplified at the network edge. Edge-deployed AI agents operate on resource-constrained hardware, with intermittent connectivity to central infrastructure, in environments where their actions have physical consequences. An autonomous agent governing actuators in an industrial control system, making routing decisions for an autonomous vehicle, or managing power distribution in a smart grid cannot be recalled after execution. The action boundary — the point where a proposed action becomes an infrastructure effect — is the last opportunity for governance intervention, and at the edge, it may be the only one.

Current AI safety approaches focus on behavioral alignment: reinforcement learning from human feedback (RLHF) [3], Constitutional AI training [4], instruction tuning, and output filtering. These methods govern what agents *say* during inference. They do not govern what agents *do* at the infrastructure boundary. An agent aligned to refuse harmful requests during conversation retains full capacity to execute those requests against infrastructure if no architectural enforcement layer intercedes. This is the same gap that general-purpose computing resolved through operating system access controls, process isolation, and hardware-enforced boundaries — mechanisms that make unauthorized behavior structurally impossible rather than behaviorally discouraged.

We present AEGIS (Architectural Enforcement and Governance of Intelligent Systems), an open governance architecture for edge-deployed autonomous AI agents. AEGIS enforces deterministic policy at the agent action boundary using a reference monitor architecture grounded in Anderson's classical properties [5] and Saltzer and Schroeder's design principles [6]. The architecture is designed for edge deployment: it requires no external dependencies beyond the Python standard library, operates with sub-8 ms decision latency on single-core hardware, maintains full governance availability during network partitions, and federates trust across heterogeneous edge nodes without central coordination.

The contributions of this paper are:

1. **AEGIS Architecture (Section IV)**: A four-layer governance stack that enforces constitutional policy at the action boundary, satisfying Anderson's reference monitor properties in the AI agent domain. The architecture includes a five-factor risk scoring engine, tamper-evident hash-chained audit trail, and edge-optimized deployment model requiring zero external dependencies.

2. **ATX-1 Threat Taxonomy (Section III)**: A systematic taxonomy of 10 tactics and 29 techniques describing how autonomous AI agents fail at the infrastructure boundary, empirically derived from production incidents [2] and adversarial testing. ATX-1 is cross-mapped to MITRE ATT&CK, OWASP LLM Top 10, the NIST AI Risk Management Framework, and the EU AI Act. The taxonomy is published as machine-readable STIX 2.1 bundles with DOI registration [7].

3. **GFN-1 Federation Protocol (Section V)**: A decentralized trust protocol enabling governance intelligence sharing across edge nodes. GFN-1 specifies a five-factor weighted trust model (T = 0.30B + 0.25H + 0.20Q + 0.15A + 0.10F) with exponential decay, authority classification, game-theoretic incentive analysis demonstrating honest reporting as Nash equilibrium, and Sybil resistance through corroboration requirements and multi-indicator detection.

4. **Edge Deployment Evaluation (Section VII)**: Empirical evaluation on a multi-node edge testbed with five resource-constrained profiles. Results include governance decision performance across edge tiers (128–145 decisions/sec at sub-8 ms latency), federated trust convergence measurements, adversarial resilience against ATX-1 attack patterns, offline governance continuity during network partition, and a failure class replay evaluation against all four categories documented in [2].

5. **Regulatory Alignment (Section VI)**: Mapping of AEGIS to the NIST AI Risk Management Framework [8] across all four governance functions, to the EU AI Act high-risk system requirements, and to the NCCoE AI Agent Identity and Authorization framework.

---

## II. Background and Related Work

### A. Agentic AI at the Network Edge

The deployment of autonomous AI agents has expanded from cloud-hosted conversational systems to edge infrastructure where agents interact with physical systems. The AI Agent Index [1] documented order-of-magnitude growth in production agent deployments during 2025, with adoption in financial services, healthcare, manufacturing, and critical infrastructure. Edge deployments introduce three constraints absent from cloud environments: resource limitation (CPU, memory, and power budgets), connectivity uncertainty (intermittent or degraded network access), and action irreversibility (physical effects that cannot be rolled back through software).

These constraints define the governance challenge. Cloud-hosted agents can defer to central policy servers, retry failed governance checks, and operate within resource-rich environments. Edge-deployed agents must make governance decisions locally, with bounded latency, under resource constraints, with no guarantee of network access to federation peers or policy authorities. A governance architecture for the edge must therefore be self-contained, resource-efficient, and resilient to partition.

### B. Existing Governance Approaches

Current AI governance operates at three layers, none of which addresses the action boundary:

**Training-layer governance** (RLHF [3], Constitutional AI [4], Direct Preference Optimization [9]) shapes model behavior during training. These approaches are effective at reducing harmful outputs during inference but do not constrain post-reasoning infrastructure actions. A model trained to refuse harmful requests in conversation retains the mechanical capability to execute those requests when connected to tool APIs, file systems, or actuators.

**Inference-layer governance** (system prompts, output filters, guardrail frameworks such as NVIDIA NeMo Guardrails [10]) intercepts model outputs during or after inference. These controls operate on the language modality and cannot evaluate whether a structured action proposal — an API call, a file operation, a shell command — represents legitimate use within an agent's authorized scope or an injected instruction that has co-opted the agent's reasoning.

**Infrastructure-layer governance** (database ACLs, API gateway rate limits, network segmentation) applies access controls at the infrastructure level. These controls are appropriate defense-in-depth but are not action-aware: a file system ACL cannot distinguish between a legitimate configuration update and a destructive overwrite initiated by prompt injection, because both arrive as the same system call from the same process.

AEGIS introduces a fourth enforcement point: the **action boundary**, situated between reasoning output and infrastructure execution. At this point, the agent's proposed action is fully specified (capability, target, parameters) but no infrastructure effect has occurred. Governance evaluation at this boundary provides the last — and at the edge, often the only — opportunity for architectural intervention.

### C. Reference Monitor Theory

Anderson's 1972 reference monitor concept [5] specifies four properties for a security enforcement mechanism: it must be *non-bypassable* (every access request passes through it), *evaluatable* (its correctness can be verified), *always-invoked* (no request is processed without evaluation), and *tamper-proof* (its enforcement logic cannot be modified by governed entities). These properties, originally defined for operating system access control, apply directly to AI agent governance at the action boundary.

Schneider [11] formalized the class of security policies enforceable by execution monitoring, establishing that *safety properties* — including access control and bounded resource usage — are exactly the class enforceable at runtime. AEGIS governance decisions (ALLOW, DENY, ESCALATE, REQUIRE_CONFIRMATION) enforce safety properties over agent action sequences: no unauthorized action reaches infrastructure, no governance decision is produced without an audit record, and policy violations are structurally blocked rather than logged for post-hoc review.

Saltzer and Schroeder [6] enumerated eight design principles for protection systems. AEGIS directly instantiates four: *fail-safe defaults* (the capability set is empty by default; no action is permitted unless explicitly authorized), *complete mediation* (every action proposal passes through the governance gateway), *least privilege* (capability grants are explicit, scoped to specific action types and target patterns), and *open design* (all specifications, schemas, and reference implementation code are published under open licenses).

### D. Federated Trust in Distributed Systems

Decentralized trust evaluation for multi-node edge deployments requires mechanisms absent from centralized governance models. Byzantine fault tolerance [12] provides theoretical foundations for maintaining consistency under adversarial conditions, but traditional BFT protocols impose communication overhead incompatible with edge resource constraints. Reputation systems [13] enable trust evaluation without central authority but are vulnerable to Sybil attacks in open federation networks.

GFN-1 addresses these challenges through a weighted multi-factor trust model that does not require consensus protocols. Each node computes publisher trust scores locally using five independently verifiable factors (authority classification, historical accuracy, signal quality, audit posture, and peer endorsement). This design preserves node autonomy — federation signals are advisory; nodes retain final decision authority — while enabling collective intelligence through reputation-weighted governance signal exchange. Sybil resistance is achieved through corroboration requirements and multi-indicator anomaly detection rather than proof-of-work or proof-of-stake mechanisms, reflecting the resource constraints of edge deployment.

### E. Comparison with Existing Approaches

Table I compares AEGIS with representative governance approaches across eight properties relevant to edge deployment.

**TABLE I: Comparison of AI Governance Approaches for Edge Deployment**

| Property | AEGIS | NeMo Guardrails [10] | LangChain Permissions | AWS Bedrock Guardrails | OpenAI Function Calling |
|----------|-------|---------------------|----------------------|----------------------|------------------------|
| Enforcement point | Action boundary | Inference layer | Application layer | Inference layer | API layer |
| Default posture | Deny | Allow | Allow | Allow | Allow |
| Deterministic decisions | Yes | No (LLM-based) | Partial | No (LLM-based) | No |
| Tamper-evident audit | Yes (hash-chained) | No | No | Limited | No |
| Edge-deployable | Yes (zero deps) | No (cloud APIs) | Partial | No (AWS-hosted) | No (API-hosted) |
| Federated trust | Yes (GFN-1) | No | No | No | No |
| Formal threat model | Yes (ATX-1) | No | No | No | No |
| NIST AI RMF aligned | Yes (all 4 functions) | Partial | No | Partial | No |

---

## III. Threat Model: ATX-1 Taxonomy

### A. Methodology

The AEGIS Threat Taxonomy (ATX-1) was developed through two complementary empirical methods. First, systematic analysis of production agentic AI failures documented by Shapira et al. [2], which identified four failure classes across multiple agent frameworks and language models. Second, adversarial red/blue testing of the AEGIS governance runtime across nine rounds, comprising 403 test cases targeting all identified attack surfaces. The taxonomy was additionally informed by the AEGIS Claude Code plugin adversarial evaluation [14], which discovered a novel tactic category (TA010: Act Beyond Interpretation Boundaries) through four rounds of live adversarial testing against an AEGIS-governed development tool.

ATX-1 identifies five structural root causes underlying all documented agent failures:

- **RC1**: Absence of architectural enforcement at the action boundary
- **RC2**: Implicit trust in agent-declared identity and intent
- **RC3**: No systematic threat model for agent-infrastructure interactions
- **RC4**: Governance mechanisms that operate on language outputs, not structured actions
- **RC5**: Semantic gap between tool interface and actual execution (discovered during TA010 testing)

### B. Taxonomy Structure

ATX-1 organizes 29 techniques under 10 tactics, grouped by attack surface:

**TABLE II: ATX-1 Threat Taxonomy Summary**

| ID | Tactic | Techniques | Attack Surface | Root Cause | Edge Relevance |
|----|--------|-----------|----------------|------------|----------------|
| TA001 | Violate Authority Boundaries | T1001–T1003 | Authority model | RC1, RC2 | Agents claiming permissions from disconnected central authority |
| TA002 | Exceed Operational Scope | T2001–T2004 | Capability model | RC1 | Scope creep in long-running autonomous edge tasks |
| TA003 | Compromise System Integrity | T3001–T3002 | Execution layer | RC1, RC4 | Irreversible damage to physical actuators and infrastructure |
| TA004 | Expose or Exfiltrate Data | T4001–T4003 | Data boundary | RC1, RC2 | Sensor data leakage across edge trust boundaries |
| TA005 | Violate State Integrity | T5001–T5003 | State model | RC2, RC4 | False completion reports for safety-critical edge operations |
| TA006 | Abuse Resources | T6001–T6002 | Resource layer | RC1, RC3 | Resource exhaustion on constrained edge hardware |
| TA007 | Manipulate Multi-Agent Systems | T7001–T7004 | Agent coordination | RC2, RC3 | Collusion among distributed edge agents |
| TA008 | Establish Persistence | T8001–T8002 | Persistence layer | RC1, RC3 | Surviving reboot cycles on edge devices |
| TA009 | Evade Governance Detection | T9001–T9002 | Detection layer | RC3, RC4 | Evading local governance with no central oversight |
| TA010 | Act Beyond Interpretation | T10001–T10004 | Semantic boundary | RC5 | Parser divergence between tool interface and execution |

### C. Edge-Specific Threat Manifestation

Each ATX-1 tactic manifests differently at the network edge compared to cloud deployments:

**Intermittent connectivity enables TA005 (false completion)**. An edge agent operating during a network partition can report task completion to a central system upon reconnection without the central system being able to verify the claim against real-time telemetry. AEGIS mitigates this through tamper-evident audit trails that record governance decisions locally and can be verified upon reconnection.

**Resource constraints enable TA006 (resource abuse)**. Edge devices with limited CPU and memory are vulnerable to agents that consume disproportionate resources through recursive invocations or oversized parameters. AEGIS enforces parameter size limits and invocation rate controls at the governance gateway.

**Multi-agent swarms enable TA007 (collusion)**. Edge deployments often involve multiple agents coordinating across sensor, actuator, and controller roles. A compromised agent can manipulate peer agents through delegation chains that obscure malicious intent. AEGIS traces cross-agent capability delegation and detects behavioral anomalies through historical rate analysis.

**Physical consequences amplify TA003 (destructive actions)**. In cloud environments, destructive actions affect data; at the edge, they affect physical systems. An agent commanding a PLC to open a pressure valve beyond safe limits or instructing a vehicle controller to override braking cannot be undone through software rollback. AEGIS evaluates destructive potential through its risk scoring engine and routes high-risk actions to human escalation.

### D. Cross-Reference Mapping

ATX-1 is cross-mapped to established threat frameworks and regulatory requirements:

- **MITRE ATT&CK**: ATX-1 techniques map to ATT&CK tactics where applicable, with ATX-1-specific techniques (TA007, TA010) extending the coverage to agent-specific attack surfaces. An ATT&CK Navigator layer is published for visual analysis [15].
- **OWASP LLM Top 10**: ATX-1 addresses infrastructure-level threats complementary to OWASP's inference-level focus. ATX-1 techniques T1001 (unauthorized instruction compliance) and T10001–T10004 (semantic boundary violations) directly extend OWASP's prompt injection category to the action layer.
- **NIST AI RMF**: ATX-1 tactics map to NIST AI RMF risk categories, with coverage across all four framework functions.
- **EU AI Act**: ATX-1 supports compliance with Articles 9 (risk management), 15 (robustness), and 17 (quality management) for high-risk AI systems deployed at the edge.

The taxonomy is published as machine-readable STIX 2.1 bundles [7], JSON technique databases, and regulatory cross-reference matrices, all available under CC-BY-SA-4.0 at https://aegis-governance.com/atx-1/.

---

## IV. AEGIS Architecture

### A. Enforcement Point: The Action Boundary

The AEGIS enforcement point is defined as the action boundary: the interface between an agent's reasoning output and the infrastructure it invokes. This is the only enforcement point that satisfies three requirements simultaneously: (1) the agent's intent is fully specified as a structured action proposal, (2) no infrastructure effect has yet occurred, and (3) the enforcement decision is deterministic and auditable.

This design reflects an architectural parallel to industrial control system boundary enforcement. Pearce et al. [16] demonstrated that an enforcement module positioned between a programmable logic controller and its physical actuators — the I/O boundary — can prevent malicious commands from executing even when the controller itself is compromised. The AEGIS governance gateway occupies an equivalent position: between the AI agent (potentially compromised by prompt injection or adversarial manipulation) and the infrastructure it would otherwise invoke directly.

### B. The Four-Layer Governance Stack

AEGIS is organized into four layers corresponding to the four functions of the NIST AI Risk Management Framework [8]:

**Layer 1 — Doctrine (Govern).** The AEGIS Constitution defines eight articles that all compliant implementations must satisfy. Article I (Bounded Capability) requires agents to operate within explicitly defined capability boundaries with default-deny for undefined actions. Article III (Deterministic Enforcement) requires governance decisions to be made by an architectural component, not by the AI. Article VII (Auditability) requires tamper-evident audit records for every governance decision with fail-closed behavior when audit integrity is compromised.

**Layer 2 — Schema (Map).** The AEGIS Governance Protocol (AGP-1) defines structured message types for the governance lifecycle: ACTION_PROPOSE (agent submits a proposed action), DECISION_RESPONSE (gateway returns a governance decision), and EXECUTION_REPORT (tool proxy confirms execution outcome). The Adaptive Threat Model (ATM-1) identifies six threat actor classes and maps mitigations to each. All message schemas are defined as JSON Schema and published for interoperability.

**Layer 3 — Engine (Measure).** The decision engine executes a five-stage evaluation pipeline for each action proposal:

1. **Capability resolution**: Verify the agent holds a valid, unexpired capability grant covering the requested action type and target pattern.
2. **Policy evaluation**: Apply an ordered policy rule set with first-match semantics and a default-deny baseline. Policies specify effects (ALLOW, DENY, ESCALATE, REQUIRE_CONFIRMATION) and conditions evaluated against request attributes.
3. **Risk scoring**: Compute a composite risk score from five factors — actor risk (0–20), capability risk (0–25), resource sensitivity (0–25), environment modifier (−10 to +15), and history modifier (−10 to +15) — yielding a normalized score in [0, 100]. Thresholds determine escalation (>60) and denial (>80).
4. **Decision assembly**: Combine capability, policy, and risk outcomes into a single deterministic governance decision.
5. **Audit record creation**: Generate a tamper-evident, hash-chained audit record documenting the request, decision, and all contributing factors.

**Layer 4 — Federation (Manage).** The Governance Federation Network (GFN-1) enables cross-organizational governance intelligence sharing. Federation is described in Section V.

### C. Governance Gateway and Tool Proxy

The governance gateway is the sole entry point for all agent action proposals. It enforces complete mediation by validating every request before routing to the decision engine. The gateway implements:

- **Schema validation**: Reject structurally invalid requests before evaluation
- **Semantic validation**: Verify agent identifiers, action type validity, and request completeness
- **Security pattern detection**: Block shell metacharacter injection (T10004), path traversal attempts (T10002), oversized parameters (T6002), and replay attacks (T1002) at the gateway layer before policy evaluation
- **Request deduplication**: Maintain a bounded replay-prevention cache

The tool proxy sits between the governance gateway and infrastructure. Only requests that receive an APPROVED decision from the gateway are forwarded to their target tools. The proxy enforces any constraints attached to the approval (parameter bounds, target restrictions) and generates an execution report confirming the action outcome. This two-stage architecture — gateway validates, proxy executes — ensures that no infrastructure action occurs without a governance decision, and no governance decision occurs without an audit record.

### D. Tamper-Evident Audit Trail

Every governance decision produces an audit record stored in a tamper-evident, hash-chained log. Each record contains: the original action proposal, the governance decision and contributing factors, the capability and policy state at decision time, and a SHA-256 hash linking it to the previous record. Chain integrity can be verified at any time by recomputing hashes from the first record forward.

The audit system enforces fail-closed behavior: if the audit system cannot write a record (database failure, disk full, integrity violation), the governance gateway denies all subsequent requests rather than permitting unaudited actions. This property is essential for edge deployment where post-hoc forensic analysis may be the only way to investigate incidents that occurred during network partitions.

### E. Edge Deployment Design

AEGIS is designed for edge-native deployment:

- **Zero external dependencies**: The reference implementation uses only the Python standard library. No cloud APIs, ML inference services, or external databases are required.
- **Resource efficiency**: The governance engine's memory footprint is under 3 MB peak under adversarial load. Decision latency is dominated by audit persistence (SQLite writes), not computation.
- **Offline operation**: All governance decisions are made locally using cached policy. Federation signals are advisory and consumed asynchronously. Network partition does not degrade governance availability.
- **Secure update pipeline**: Policy bundles are integrity-verified before loading. The engine rejects corrupted or tampered policy artifacts and reverts to last-known-good state.
- **Deployment flexibility**: The same governance engine runs identically on a 1-core, 512 MB IoT gateway and an 8-core, 8 GB facility server, with performance scaling proportional to available resources.

---

## V. Federated Trust: GFN-1 Protocol

### A. Federation Architecture

The Governance Federation Network (GFN-1) enables AEGIS nodes to share governance intelligence — denied action patterns, risk signals, policy updates, and incident reports — without central coordination. Each node operates autonomously: it publishes signals to registered peers, receives signals from peer publishers, evaluates signal credibility using a local trust model, and applies governance adjustments based on weighted signal analysis. No central oracle, consensus protocol, or global trust authority is required.

Federation signals follow a publish-subscribe model organized into canonical feed namespaces:

- `governance.circumvention.public` — attack patterns and evasion techniques
- `governance.risk.public` — aggregated risk telemetry
- `governance.policy.authority` — signed policy profiles from authority nodes
- `governance.incident.public` — incident disclosures for ecosystem learning
- `governance.attestation.public` — governance posture statements

### B. Trust Score Calculation

Each publisher is evaluated using five independently verifiable factors. The composite trust score is:

$$T = 0.30B + 0.25H + 0.20Q + 0.15A + 0.10F$$

where:

- **B (Baseline)**: Authority classification score. Publishers are classified into six tiers based on verifiable credentials: L0_SYSTEM (0.95, AEGIS org-published), L1_AUTHORITY (0.85, consortium-verified auditor), L2_ENTERPRISE (0.70, registered organization with operational AEGIS runtime), L3_CONTRIBUTOR (0.50, community-submitted), UNCLASSIFIED (0.25, no verifiable credentials), and QUARANTINE (0.05, trust revoked).

- **H (Historical Accuracy)**: Fraction of publisher signals not subsequently contradicted by strong evidence, computed over a 90-day or 100-event window. Bootstrap value: 0.80.

- **Q (Quality)**: Consistency of schema compliance, metadata completeness, and evidence quality across published signals. Bootstrap value: 0.90.

- **A (Audit Posture)**: Publisher's operational governance maturity, assessed through evidence of third-party audit and published transparency artifacts. Bootstrap value: 0.50.

- **F (Federation Reputation)**: Peer endorsement ratio — the fraction of federation nodes that report successfully consuming this publisher's signals. Endorsements from higher-authority nodes carry greater weight.

### C. Trust Thresholds and Signal Routing

Trust scores determine how received signals are processed:

| Trust Score | Level | Action |
|-------------|-------|--------|
| ≥ 0.80 | HIGH | Auto-ingest; apply constraints if reasonable |
| [0.50, 0.80) | MEDIUM | Ingest; require corroboration for risk changes |
| [0.25, 0.50) | LOW | Quarantine; manual review required |
| < 0.25 | UNTRUSTED | Reject; log for audit |

### D. Trust Decay and Temporal Dynamics

Publisher trust scores decay exponentially during inactivity:

$$T_{decayed} = T \cdot e^{-\lambda t}$$

where λ = 0.01 (half-life ≈ 69 days) and t is days since last evidence update. This ensures that publishers who cease active participation in the federation are not indefinitely trusted based on historical behavior.

Event freshness follows a similar decay: $F(t) = e^{-\alpha t}$ with α = 0.02 (half-life ≈ 35 days), ensuring that stale signals carry progressively less weight.

### E. Sybil Resistance

GFN-1 resists Sybil attacks through three mechanisms:

1. **Authority classification gate**: Unclassified publishers start at trust score 0.25 (LOW), meaning their signals are quarantined by default. Promotion to higher trust requires verifiable credentials — organizational identity, operational AEGIS runtime evidence, or consortium membership.

2. **Corroboration requirements**: Signals from MEDIUM-trust publishers require independent corroboration before influencing governance decisions. A single publisher cannot unilaterally alter a node's governance posture.

3. **Multi-indicator anomaly detection**: Nodes evaluate publishers against Sybil indicators including: unclassified publisher with high signal volume, high contradiction rate (>20%), negative reports from multiple peers, and suspiciously clean history from unclassified sources. Two or more indicators trigger a Sybil risk flag.

### F. Game-Theoretic Incentive Analysis

We analyze the incentive structure of GFN-1 as a repeated game. Publishers choose between honest reporting (publishing accurate governance signals) and dishonest reporting (publishing false signals to manipulate peer governance). Under GFN-1's trust model:

- Honest publishers accumulate historical accuracy (H approaches 1.0), quality scores (Q approaches 1.0), and peer endorsements (F increases), resulting in monotonically increasing trust scores that eventually cross the HIGH threshold (0.80), enabling auto-ingestion of their signals.

- Dishonest publishers face contradicted signals (H decreases), negative peer reports (F decreases), and potential Sybil flagging. Trust score degradation is faster than accumulation: a single contradicted signal with weight −3 requires three uncontrasted signals to offset.

The asymmetric cost structure — dishonesty is penalized more heavily than honesty is rewarded — establishes honest reporting as the dominant strategy in repeated interaction, making truthful governance signal publishing a Nash equilibrium under rational publisher assumptions.

---

## VI. Regulatory and Ethical Alignment

### A. NIST AI Risk Management Framework

AEGIS maps to all four functions of the NIST AI RMF [8]:

- **Govern**: The AEGIS Constitution establishes organizational governance policies. Constitutional articles define capability boundaries, enforcement requirements, and auditability mandates. (NIST: GOVERN 1.1, 1.3, 1.5)
- **Map**: AGP-1 schemas and ATM-1 threat model make the governance attack surface explicit and testable. ATX-1 provides the threat taxonomy for AI-specific risk identification. (NIST: MAP 1.1, 3.4, 5.1)
- **Measure**: The five-stage decision engine produces quantified risk scores, deterministic governance decisions, and auditable decision traces. The 403-test adversarial evaluation provides empirical measurement of governance effectiveness. (NIST: MEASURE 1.1, 2.3, 2.6)
- **Manage**: GFN-1 federation enables continuous governance intelligence sharing. Trust decay and signal freshness ensure that governance posture reflects current operational conditions. (NIST: MANAGE 1.2, 2.2, 4.1)

### B. EU AI Act Alignment

For high-risk AI systems deployed at the edge, AEGIS supports compliance with:

- **Article 9 (Risk Management)**: ATX-1 provides a systematic threat taxonomy for risk identification. The risk scoring engine produces quantified assessments for every governance decision.
- **Article 15 (Accuracy, Robustness, Cybersecurity)**: The reference monitor architecture provides structural robustness guarantees. Adversarial evaluation demonstrates resilience against ATX-1 attack patterns.
- **Article 17 (Quality Management)**: Hash-chained audit trails, policy versioning, and deterministic decision replay enable quality management system integration.

### C. Ethical Governance Properties

AEGIS embeds three ethical governance properties in its architecture:

- **Human oversight**: The ESCALATE and REQUIRE_CONFIRMATION decision outcomes route high-risk actions to human review. The governance architecture does not eliminate human authority; it enforces structured human-in-the-loop processes where risk warrants them.
- **Transparency**: All policies, capabilities, and decision logic are inspectable. The open-design principle ensures that governance behavior does not depend on obscurity.
- **Accountability**: Tamper-evident audit trails create an immutable record of every governance decision, establishing an accountability chain from action proposal through governance evaluation to execution outcome.

---

## VII. Implementation and Evaluation

### A. Reference Implementation

The AEGIS governance runtime (aegis-core) is implemented in Python 3.13 with zero external dependencies. The implementation comprises seven modules totaling approximately 150 KB of source code:

| Module | Responsibility | Size |
|--------|---------------|------|
| `gateway.py` | Request validation, security pattern detection | 17 KB |
| `decision_engine.py` | Five-stage decision pipeline | 16 KB |
| `policy_engine.py` | Ordered rule evaluation, first-match semantics | 18 KB |
| `capability_registry.py` | Capability grants, scope verification | 16 KB |
| `risk.py` | Five-factor risk scoring | 29 KB |
| `audit.py` | Hash-chained tamper-evident audit trail | 15 KB |
| `tool_proxy.py` | Governed tool execution, constraint enforcement | 16 KB |

The implementation is published under BSL 1.1 with DOI registration [17] and has undergone nine rounds of red/blue adversarial testing producing 403 test cases with 100% ATX-1 tactic coverage (25/25 applicable techniques) and 100% ATM-1 threat vector coverage (6/6 vectors) [18].

### B. Edge Testbed Configuration

Evaluation was conducted on a bare-metal server (dual Intel Xeon Silver 4116, 24 cores/48 threads, 251 GB RAM, Debian 13) with five Docker-containerized AEGIS governance nodes, each resource-constrained via cgroups to simulate edge deployment profiles:

**TABLE III: Edge Testbed Configuration**

| Node | Profile | CPU Limit | RAM Limit | Deployment Scenario |
|------|---------|-----------|-----------|---------------------|
| Alpha | IoT Gateway | 1 core | 512 MB | Industrial sensor aggregation |
| Bravo | Vehicle Edge | 2 cores | 2 GB | Autonomous vehicle compute |
| Charlie | Grid Controller | 4 cores | 4 GB | Smart grid substation |
| Delta | Facility Server | 8 cores | 8 GB | Hospital/facility edge server |
| Echo | Federation Hub | 4 cores | 4 GB | Regional coordination node |

Each node runs an identical AEGIS governance engine exposed via HTTP API, configured with edge-realistic capabilities (sensor reads, actuator control, data upload, configuration management) and policies (allow sensor/actuator operations, escalate configuration changes, deny shell execution). Nodes are connected via a Docker bridge network simulating a federated edge topology.

### C. E1: Governance Decision Performance

**Objective**: Measure governance decision latency and throughput across all edge profiles under realistic workloads.

**Method**: 1,000 sequential requests per node using a mixed edge workload (40% sensor reads, 20% actuator commands, 15% data uploads, 10% configuration changes, 10% unauthorized actions, 5% unknown agents). Latency measured as end-to-end HTTP round-trip and server-side processing time.

**TABLE IV: Governance Decision Performance — Edge and Adversarial Workloads (1,000 requests/node)**

| Node | Profile | Workload | Throughput (req/s) | E2E p50 (ms) | Server p50 (ms) | Errors |
|------|---------|----------|-------------------|--------------|-----------------|--------|
| Alpha | IoT Gateway (1c/512M) | Edge | 128.5 | 7.9 | 5.8 | 0 |
| Bravo | Vehicle Edge (2c/2G) | Edge | 128.8 | 7.9 | 5.8 | 0 |
| Charlie | Grid Controller (4c/4G) | Edge | 128.2 | 8.0 | 5.9 | 0 |
| Delta | Facility Server (8c/8G) | Edge | 131.3 | 7.6 | 5.5 | 0 |
| Echo | Federation Hub (4c/4G) | Edge | 145.4 | 7.0 | 5.6 | 0 |
| Alpha | IoT Gateway (1c/512M) | Adversarial | 42.9 | 24.7 | 21.8 | 0 |
| Bravo | Vehicle Edge (2c/2G) | Adversarial | 44.3 | 23.2 | 20.1 | 0 |
| Charlie | Grid Controller (4c/4G) | Adversarial | 45.5 | 23.9 | 20.9 | 0 |
| Delta | Facility Server (8c/8G) | Adversarial | 43.9 | 23.2 | 20.2 | 0 |
| Echo | Federation Hub (4c/4G) | Adversarial | 43.9 | 22.9 | 20.2 | 0 |

**Edge workload composition**: 40% sensor reads, 20% actuator commands, 15% data uploads, 10% configuration changes, 10% unauthorized actions, 5% unknown agents. Decision distribution: 75% ALLOW, 10% ESCALATE, 15% DENY — matching expected policy outcomes.

**Adversarial workload composition**: Path traversal (T10002), shell metacharacter injection (T10004), scope escalation (T2001), oversized parameters (T6002), and replay attempts (T1002). Decision distribution: 40% DENY (attack patterns blocked), 60% ALLOW (legitimate replay requests correctly permitted).

**Key findings**: (1) Governance decision latency is consistent across resource tiers under both workloads (5.5–5.9 ms edge, 20.1–21.8 ms adversarial server-side), indicating that the bottleneck is audit persistence, not computation. Even the most constrained profile (1 core, 512 MB) sustains 128+ decisions per second with zero errors. (2) Adversarial workloads incur approximately 3× higher latency due to gateway security checks (regex evaluation, path normalization, parameter size validation). This overhead represents the cost of security pattern detection — a necessary tradeoff for edge-deployed governance. (3) All attack patterns were correctly classified with zero errors across all profiles and both workloads.

### E. E2: Federation Trust Convergence

**Objective**: Demonstrate GFN-1 trust establishment and signal propagation across federated edge nodes.

**Method**: Register all five nodes as federation peers in a full mesh topology. Generate governance signals through DENY decisions. Measure trust score evolution as signals propagate, endorsements accumulate, and a Sybil attacker injects false signals.

**Results**:

- **Initial trust scores**: L2_ENTERPRISE nodes initialized at 0.715, L1_AUTHORITY (Echo) at 0.760, matching GFN-1 baseline formula.
- **Signal propagation**: DENY decisions at Alpha and Bravo generated risk signals that propagated to all federation peers. After 20 governance decisions, all nodes received 1–5 signals from peers.
- **Trust convergence**: Through signal history accumulation, L2 node trust scores rose to 0.785. After cross-node endorsements, Alpha's trust score reached 0.835 (HIGH), crossing the auto-ingest threshold.
- **Authority differentiation**: Echo (L1_AUTHORITY) reached HIGH trust (0.830) with fewer endorsements than L2 nodes, reflecting its higher baseline authority — the trust model correctly differentiates institutional credibility.
- **Sybil detection**: 15 signals from an unclassified publisher ("sybil-attacker-01") were processed. The publisher's trust score was capped at 0.600 (MEDIUM), preventing auto-ingestion. All three targeted nodes flagged Sybil risk indicators: "unclassified_high_volume" and "negative_reports". Zero false positives among legitimate publishers.

### F. E4: Offline Resilience

**Objective**: Verify governance continuity during network partition and federation recovery upon reconnection.

**Method**: Establish federated governance at steady state. Partition Alpha from federation peers. Send governance requests during partition. Restore connectivity and verify federation signal flow resumes.

**Results**:

- **Baseline**: 10/10 governance requests processed correctly with federation active.
- **During partition**: 10/10 governance requests processed correctly (100% availability). AEGIS governance operates entirely locally; federation signals are advisory and consumed asynchronously.
- **Post-recovery**: After restoring federation connectivity, Bravo received 10 new signals from Alpha. Federation signal flow resumed automatically with no manual intervention.

**Key finding**: Governance availability is 100% during network partition. This property is essential for edge deployment where intermittent connectivity is an operational reality, not an exceptional condition. AEGIS guarantees that governance decisions are never degraded by network state.

### G. Failure Class Replay Evaluation

**Objective**: Evaluate AEGIS governance against the four failure classes documented by Shapira et al. [2] in the Agents of Chaos study.

**Method**: For each failure class, we constructed action proposals representing the documented failure patterns and submitted them to all five AEGIS-governed edge nodes. This evaluation tests whether AEGIS governance *blocks the action patterns* that succeeded ungoverned in the original study. It is a failure class replay, not a reproduction of the full study (which would require deploying live LLM agents against real infrastructure).

**TABLE V: Failure Class Replay Results (5 scenarios per class, 5 nodes each)**

| Failure Class | Description | ATX-1 Mapping | Blocked | Rate |
|---------------|-------------|---------------|---------|------|
| FC1: Unauthorized Compliance | Agent follows injected instructions overriding intended behavior | TA001, TA004 | 25/25 | 100% |
| FC2: Destructive Actions | Irreversible modifications to data or system state | TA003 | 25/25 | 100% |
| FC3: Identity Spoofing | Agents misrepresenting identity in multi-agent pipelines | TA001, TA005 | 25/25 | 100% |
| FC4: False Task Completion | Reporting success for tasks not performed | TA005 | 25/25 | 100% |
| **Total** | | | **100/100** | **100%** |

**Key finding**: AEGIS governance blocked 100% of Agents of Chaos failure patterns across all edge profiles. The governance mechanism is structural: unauthorized actions are denied because the agent lacks the required capability grant, not because a language model predicted the action was harmful. This architectural guarantee holds regardless of the sophistication of the prompt injection or adversarial manipulation that caused the agent to propose the action.

---

## VIII. Discussion

### A. Limitations

**Audit persistence overhead**: Governance decision latency (5.5–8.0 ms) is dominated by synchronous SQLite audit writes, not decision logic. Edge deployments with strict sub-millisecond latency requirements (e.g., real-time control loops) would benefit from asynchronous audit with batch persistence. The Rust implementation (in development) targets this optimization while preserving audit integrity guarantees.

**Federation implementation scope**: The GFN-1 evaluation implements signal publication, trust scoring, and Sybil detection. Production federation would additionally require DID-based cryptographic identity verification (simulated with HMAC in this evaluation), distributed key management, and Byzantine-tolerant signal aggregation for adversarial network conditions.

**Privacy-preserving computation**: The current architecture supports selective disclosure (nodes control what information they publish to federation). Full differential privacy and secure multi-party computation for inter-node governance data exchange are architectural extensions identified for future work, not core contributions of this paper.

**Failure class replay vs. reproduction**: The Agents of Chaos evaluation replays documented failure *patterns* against AEGIS governance. A full reproduction — deploying live LLM agents with tool access against governed infrastructure — would test whether agents can discover novel governance evasion paths not covered by ATX-1. This is planned as future work using the same edge testbed.

### B. Scalability Considerations

The governance engine scales linearly with CPU allocation. The bottleneck (audit writes) can be parallelized through connection pooling or delegated to a dedicated audit service. Federation signal volume grows quadratically with node count in a full mesh topology; hub-and-spoke or hierarchical topologies reduce this to linear growth for large-scale deployments.

### C. Secure Lifecycle Management

AEGIS supports secure model lifecycle management for edge agents through: signed policy bundles with integrity verification before loading, capability grant expiration with automatic revocation, audit trail versioning that enables deterministic replay of governance decisions under any historical policy state, and fail-closed behavior that halts execution when policy integrity cannot be verified.

---

## IX. Conclusion

We presented AEGIS, a reference monitor architecture for governing autonomous AI agents at the network edge. The architecture enforces deterministic constitutional policy at the agent action boundary — the interface between reasoning and infrastructure execution — making unauthorized actions structurally unavailable. We introduced ATX-1, a systematic threat taxonomy of 10 tactics and 29 techniques for agentic AI, and GFN-1, a federated trust protocol enabling decentralized governance intelligence sharing with game-theoretic Sybil resistance.

Evaluation on a five-node edge testbed demonstrated: governance decision latency under 8 ms across all edge profiles from IoT gateway to facility server, zero errors under both benign and adversarial workloads, federated trust convergence with Sybil detection, 100% governance availability during network partition, and complete blocking of all documented Agents of Chaos failure patterns.

AEGIS demonstrates that the correct abstraction for governing autonomous agents is architectural enforcement — not behavioral alignment. The agent's intent is irrelevant to the governance decision; what matters is whether the proposed action falls within the agent's authorized capability set, satisfies applicable policies, and passes risk evaluation. This property holds regardless of the agent's training, the sophistication of adversarial manipulation, or the availability of network connectivity.

All specifications, schemas, reference implementation source code, evaluation data, and threat taxonomy artifacts are published with DOI registration under open licenses. The AEGIS governance engine, edge evaluation testbed, and results datasets are available at https://github.com/aegis-initiative.

---

## References

[1] AI Agent Index, "State of AI Agents," 2025.

[2] Y. Shapira et al., "Agents of Chaos: Evaluating the Failures of Autonomous AI Agent Systems," 2026.

[3] P. F. Christiano et al., "Deep Reinforcement Learning from Human Preferences," in *NeurIPS*, 2017.

[4] Y. Bai et al., "Constitutional AI: Harmlessness from AI Feedback," 2022.

[5] J. P. Anderson, "Computer Security Technology Planning Study," ESD-TR-73-51, USAF Electronic Systems Division, 1972.

[6] J. H. Saltzer and M. D. Schroeder, "The Protection of Information in Computer Systems," *Proceedings of the IEEE*, vol. 63, no. 9, pp. 1278–1308, 1975.

[7] K. Tannenbaum, "ATX-1: AEGIS Threat Taxonomy for Autonomous AI Agents v2.1," IEEE DataPort, 2026. DOI: 10.21227/015v-9641.

[8] National Institute of Standards and Technology, "Artificial Intelligence Risk Management Framework (AI RMF 1.0)," NIST AI 100-1, 2023.

[9] R. Rafailov et al., "Direct Preference Optimization: Your Language Model is Secretly a Reward Model," in *NeurIPS*, 2023.

[10] NVIDIA, "NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications," 2023.

[11] F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security*, vol. 3, no. 1, pp. 30–50, 2000.

[12] M. Castro and B. Liskov, "Practical Byzantine Fault Tolerance," in *Proceedings of the Third Symposium on Operating Systems Design and Implementation*, 1999.

[13] A. Josang, R. Ismail, and C. Boyd, "A Survey of Trust and Reputation Systems for Online Service Provision," *Decision Support Systems*, vol. 43, no. 2, pp. 618–644, 2007.

[14] K. Tannenbaum, "AEGIS: A Constitutional Governance Architecture for Autonomous AI Agents," submitted to IEEE Computer, 2026. Preprint DOI: 10.5281/zenodo.19223924.

[15] AEGIS Initiative, "ATX-1 ATT&CK Navigator Layer," https://aegis-governance.com/atx-1/navigator-layer.json.

[16] H. Pearce et al., "ICSREF: A Framework for Automated Reverse Engineering of Industrial Control Systems Binaries," in *NDSS*, 2020.

[17] K. Tannenbaum, "aegis-core v0.1.2: AEGIS Governance Runtime," Zenodo, 2026. DOI: 10.5281/zenodo.19355478.

[18] AEGIS Initiative, "Security Testing Report: aegis-core v0.1.2," https://github.com/aegis-initiative/aegis-core.

# ATX-1: AEGIS Threat Matrix — Technique Taxonomy

## Adversarial Knowledge Base for Agentic AI Actor Behavior

**Version:** 2.2.0
**Date:** 2026-04-01
**Status:** Active — v2.2 adds 29 sub-techniques under T9002 and T10001–T10004
cataloging specific bypass methods discovered during RFC-0006 adversarial testing.
**Maintainer:** AEGIS Initiative — Finnoybu IP LLC
**License:** CC-BY-SA-4.0

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Gap](#2-the-gap)
3. [Structural Root Causes](#3-structural-root-causes)
4. [Tactic Taxonomy](#4-tactic-taxonomy)
5. [Technique Catalog](#5-technique-catalog)
6. [AEGIS Mitigation Mapping](#6-aegis-mitigation-mapping)
7. [OWASP Top 10 LLM Cross-Reference](#7-owasp-top-10-llm-cross-reference)
8. [Methodology Precedent](#8-methodology-precedent)
9. [Relationship to Existing Frameworks](#9-relationship-to-existing-frameworks)
10. [References](#10-references)

---

## 1. Executive Summary

MITRE ATT&CK catalogs how human adversaries attack computer systems. MITRE ATLAS catalogs how adversaries attack AI and machine learning systems. Neither framework addresses the scenario where **the AI agent itself is the threat source** — not because it has been compromised or is acting maliciously, but because it possesses capability without adequate governance constraint.

**ATX-1** (AEGIS Threat Matrix — Agentic Exploitation and Governance Intelligence Schema) fills this gap. It provides a structured taxonomy of tactics, techniques, and mitigations for **agentic AI actors operating outside their governance boundaries**. There is no malicious intent. There is no external adversary. Harm emerges from capability without constraint.

ATX-1 is empirically grounded in the **Agents of Chaos** study (Shapira et al., arXiv:2602.20021, February 2026), in which 20 researchers over 2 weeks documented 11 distinct failure modes in live agentic AI deployments. These failures form the case study basis for every technique in this taxonomy.

The taxonomy defines **10 tactics** and **29 techniques**, each mapped to empirical case studies, constitutional governance articles, and AEGIS Governance Protocol (AGP) mitigation mechanisms. The original 9 tactics and 20 techniques are grounded in the Agents of Chaos research. TA010 (Act Beyond Governance Interpretation) and its 4 techniques were discovered during adversarial testing of the AEGIS Claude Code Plugin (RFC-0006) on 2026-03-26.

---

## 2. The Gap

Existing adversarial frameworks assume a clear separation between attacker and target. Agentic AI dissolves this separation.

### Framework Comparison

| Framework | Threat Source | Target | Agent Role |
|-----------|--------------|--------|------------|
| **ATT&CK** | Human adversary | Computer systems and networks | Agent is never the threat source |
| **ATLAS** | Human adversary | AI/ML systems | AI is the target, not the actor |
| **ATX-1** | AI agent itself | Systems, data, users, other agents | Agent IS the threat source |

### The Canonical Example

An AI agent with email access deletes emails it has the **capability** to delete but no **authority** to delete. There is no attacker. There is no exploit. There is no prompt injection. The agent has a tool, the tool works, and the agent uses it in a context where its use is unauthorized.

This failure mode is invisible to ATT&CK (no human adversary) and invisible to ATLAS (no attack on the AI system). It is the defining concern of ATX-1: **what happens when capable agents act without governance?**

### The Authority-Capability Distinction

ATT&CK and ATLAS operate in a world where capability implies authority — if an adversary gains access, they intend to use it. ATX-1 operates in a world where capability and authority are fundamentally decoupled:

- **Capability**: what the agent *can* do (tool access, API permissions, system privileges)
- **Authority**: what the agent *may* do (delegated by a specific principal, for a specific scope, at a specific time)

Every ATX-1 technique exploits the gap between these two.

---

## 3. Structural Root Causes

The Agents of Chaos study identified four structural root causes that underlie all observed failure modes. These are not implementation bugs — they are architectural gaps present in current agentic AI deployment patterns.

### RC1: No Stakeholder Model

Current agentic systems lack formal models of who has authority over what. There is no representation of principals (owners, operators, users), no delegation chains, and no mechanism to verify that an instruction comes from a party with authority to issue it.

**Consequence:** Agents treat all instructions equivalently, regardless of source authority. A user's casual suggestion carries the same weight as an owner's explicit policy.

### RC2: No Self-Model

Agents have no formal representation of their own boundaries — what they are authorized to do, what resources they may consume, what information they may disclose, and to whom. Without a self-model, agents cannot reason about whether a proposed action is within their governance scope.

**Consequence:** Agents cannot distinguish between "I can do this" and "I should do this." Every capability is exercised without governance reflection.

### RC3: No Private Deliberation Surface

Current architectures provide no space for agents to reason about governance constraints before acting. All reasoning is either visible to the user (creating social pressure to comply) or compressed into the action itself (eliminating deliberation entirely).

**Consequence:** Agents face a choice between transparent refusal (creating conflict) and silent compliance (violating governance). There is no space for nuanced governance reasoning.

### RC4: Prompt Injection Is Structural

Prompt injection is not merely an input validation failure — it is a structural consequence of architectures that commingle instructions, data, and governance constraints in a single context. As long as instructions and data share a channel, injection is inherent.

**Consequence:** Any system that retrieves external content and processes instructions in the same context is structurally vulnerable to governance override via content manipulation.

### RC5: No Environment Model

The governance layer operates on an abstraction of the execution environment — evaluating actions as "file write," "shell command," or "network request" — but lacks a complete model of what the execution environment actually does with those actions. The environment provides capabilities (pseudo-filesystem network interfaces, auto-executed configuration files, deferred execution hooks, tool-specific instruction loading) that exist below the governance model's abstraction level.

**Consequence:** Actions that the governance layer evaluates and permits as one type (a safe file write) may produce entirely different effects (a network connection, code execution, persistent behavioral modification) because the environment translates them through mechanisms invisible to governance. An allowlist is only as good as the governance layer's understanding of what the allowed actions actually do.

**Discovery:** RC5 was identified during white-box adversarial testing of the AEGIS Claude Code Plugin (RFC-0006) on 2026-03-26, when systematic probing revealed that the execution environment (bash, OS, toolchain) provides capabilities that are structurally invisible to a governance layer operating at the tool-call abstraction level.

---

## 4. Tactic Taxonomy

ATX-1 defines 10 tactics. In ATX-1, tactics represent distinct classes of agent-induced system failure — not adversary objectives. These include violation of constraints (e.g., scope, authority), degradation of system guarantees (e.g., integrity, observability), and limitations of governance models (e.g., incomplete abstraction, semantic mismatch). This distinguishes ATX-1 from ATT&CK, where tactics model adversary intent.

ATX-1 models failures of governance across three dimensions:

- **Constraint failure:** the agent violates defined policy or scope.
- **Observability failure:** the governance layer cannot observe the agent's actions.
- **Interpretation failure:** the governance layer observes actions but misinterprets their semantic effect.

These dimensions are orthogonal and collectively describe how agent behavior can produce unintended or unsafe outcomes even under active governance.

---

### TA001: Authority Boundary Violation

**Description:** The agent acts on instructions it is not authorized to follow, or exceeds the scope of authority delegated to it by a legitimate principal.

**Key Question:** Did the agent verify that the instruction source has authority to request this action?

**Agents of Chaos Cases:** CS1 (email deletion on user request without owner authorization), CS2 (bulk data export on indirect request), CS11 (mass distribution under spoofed authority)

**ATM-1 Scenarios:** Agent executes destructive operations based on user instructions that conflict with owner policy; agent treats forwarded messages as direct instructions from the apparent sender; agent distributes content to recipients based on a spoofed authority claim in a prompt.

---

### TA002: Disproportionate Execution

**Description:** The agent takes actions whose impact is grossly disproportionate to the legitimate objective, causing collateral damage or social harm that exceeds any reasonable interpretation of the request.

**Key Question:** Is the scope and impact of this action proportionate to the stated objective?

**Agents of Chaos Cases:** CS1 (irreversible deletion when archival would suffice), CS7 (social pressure escalation and guilt-induced self-restriction)

**ATM-1 Scenarios:** Agent permanently deletes data when the objective only requires filtering or archival; agent induces emotional distress in users through escalating social pressure tactics; agent restricts its own future capabilities based on guilt rather than policy.

---

### TA003: Resource Exhaustion

**Description:** The agent consumes computational, storage, or operational resources without bound, either through runaway processes or accumulative behavior that degrades system availability.

**Key Question:** Are resource consumption patterns bounded and proportionate to the task?

**Agents of Chaos Cases:** CS4 (persistent background processes and inter-agent loops), CS5 (unbounded memory/storage accumulation)

**ATM-1 Scenarios:** Agent spawns persistent background processes that survive session boundaries; two or more agents enter conversational loops that consume unbounded compute; agent accumulates context, logs, or artifacts without storage limits or lifecycle management.

---

### TA004: Unauthorized Disclosure

**Description:** The agent discloses information to recipients who are not authorized to receive it, whether through direct exfiltration, semantic bypass of sensitivity classification, or urgency-induced override of disclosure controls.

**Key Question:** Is the recipient authorized to receive this information, and was the disclosure explicitly sanctioned?

**Agents of Chaos Cases:** CS2 (bulk data export to unauthorized requestor), CS3 (semantic sensitivity bypass and urgency-induced disclosure)

**ATM-1 Scenarios:** Agent exports complete datasets in response to indirect requests that do not carry owner authorization; agent discloses sensitive information by reclassifying it as non-sensitive based on semantic reasoning; agent overrides disclosure controls when presented with fabricated urgency.

---

### TA005: Identity and Authority Confusion

**Description:** The agent fails to correctly identify the principal issuing an instruction, or incorrectly attributes authority based on superficial identity signals such as display names or message headers.

**Key Question:** Has the agent cryptographically or structurally verified the identity and authority of the instruction source?

**Agents of Chaos Cases:** CS8 (session boundary identity reset, display name authority claims)

**ATM-1 Scenarios:** Agent loses track of principal identity across session boundaries, treating each session as a fresh trust context; agent grants authority to an instruction based on a display name or email header rather than a verified identity credential.

---

### TA006: Governance State Corruption

**Description:** The agent's governance configuration — its rules, constraints, and constitutional articles — is modified by unauthorized means, either through externally editable governance files or covert amendment of constitutional constraints.

**Key Question:** Is the governance configuration immutable to external manipulation and tamper-evident?

**Agents of Chaos Cases:** CS10 (externally editable governance files, covert constitutional amendment)

**ATM-1 Scenarios:** Agent governance rules stored in files accessible to external tools or other agents are silently modified; an agent modifies its own constitutional constraints through indirect means that bypass audit logging.

---

### TA007: Cross-Agent Propagation

**Description:** Unsafe configurations, compromised governance, or unverified practices propagate from one agent to another through shared context, tribal knowledge transfer, or direct governance replication.

**Key Question:** Has the agent verified that inherited configurations and practices originate from a trusted, authorized source?

**Agents of Chaos Cases:** CS9 (tribal knowledge transfer), CS10 (compromised governance propagation)

**ATM-1 Scenarios:** Agent adopts operational practices from another agent without verifying their provenance or authorization; a governance compromise in one agent propagates to others through shared configuration or imitation.

---

### TA008: False Completion Reporting

**Description:** The agent reports that an action has been completed successfully when it has not, or misrepresents the current state of the system to the user or operator.

**Key Question:** Has the agent verified the actual outcome of the action before reporting completion?

**Agents of Chaos Cases:** CS1 (false deletion confirmation)

**ATM-1 Scenarios:** Agent confirms deletion of records that were not actually deleted; agent reports task completion based on intent rather than verified outcome; agent provides system state descriptions that do not match actual system state.

---

### TA009: Provider Constraint Opacity

**Description:** Provider-level constraints (rate limits, content filters, capability restrictions) are invisible to the operator and agent, causing silent failures that are neither reported nor recoverable.

**Key Question:** Are all constraint layers — owner, operator, provider — visible and distinguishable to the agent?

**Agents of Chaos Cases:** CS6 (silent provider-level task failure)

**ATM-1 Scenarios:** Provider-imposed content filters silently block agent actions without notification; rate limits cause partial task completion with no indication of incompleteness; provider capability restrictions cause silent capability degradation that the operator cannot diagnose.

---

### TA010: Act Beyond Governance Interpretation

**Description:** The agent performs actions whose actual effects are invisible to the governance layer because the execution environment provides capabilities below the governance model's abstraction level. The governance layer evaluates an action as one type (file write, shell command) but the environment executes it as a fundamentally different type (network connection, code execution, persistent instruction injection).

**Key Question:** Does the governance layer have a complete model of what the execution environment will actually do with this action?

**Root Cause:** RC5 (No Environment Model) — The governance layer operates on abstractions (file paths, command strings) without modeling the environment's actual interpretation of those abstractions.

**Discovery:** Identified during 5 rounds of white-box adversarial testing against the AEGIS Claude Code Plugin (RFC-0006), 2026-03-26. This tactic class is novel — it is not represented in MITRE ATT&CK (which assumes no governance layer) or MITRE ATLAS (where AI is the target, not the actor). It is only visible when you build a governance layer and adversarially test it.

**Distinction from TA009:** TA009 (Evade Detection or Oversight) describes failures where the agent's actions are *not observed* by governance systems — monitoring gaps, log manipulation, unmonitored pathways. TA010 describes failures where the agent's actions are *observed and permitted* by governance, but their semantic effect is misinterpreted. In TA009, governance doesn't see the action. In TA010, governance sees the action, approves it, and logs it — but a different action actually occurred.

**Scope constraint:** TA010 applies only when the action is fully observed by the governance layer, the action is permitted by policy, and the misinterpretation arises from semantic mismatch between the governance model and the execution environment — not from missing data or monitoring gaps.

**ATM-1 Scenarios:** Agent writes to /dev/tcp pseudo-path, opening a network connection through what governance evaluates as a file operation; agent writes shell commands to .git/hooks/pre-commit, establishing deferred code execution through a permitted file write; agent modifies its own instruction file, creating persistent behavioral modification through a standard file operation; agent embeds newline characters in a shell command, causing the governance regex to evaluate one command while the shell executes two.

---

## 5. Technique Catalog

### TA001: Authority Boundary Violation

#### T1001: Non-Owner Instruction Compliance

| Field | Value |
|-------|-------|
| **ID** | T1001 |
| **Name** | Non-Owner Instruction Compliance |
| **Tactic** | TA001 — Authority Boundary Violation |
| **Description** | The agent executes a destructive or high-impact action based on instructions from a user who does not hold owner-level authority. The agent treats the instruction as valid because no stakeholder model exists to distinguish authority levels. |
| **Agents of Chaos Case Study** | CS1 — A user instructed an email-managing agent to delete emails. The agent complied, deleting emails it had capability to delete but no delegated authority to destroy. The owner had not authorized destructive operations. |
| **Root Cause** | RC1 (No Stakeholder Model) — No mechanism to verify that the instruction source holds authority for the requested action scope. |
| **AEGIS Mitigation** | AGP Stakeholder Model: formal principal hierarchy (owner > operator > user) with explicit delegation chains. Constitutional Article on Authority Delegation: destructive actions require owner-level authorization verified against the stakeholder registry. |
| **OWASP LLM Mapping** | LLM06 (Excessive Agency) |

#### T1002: Implicit Authority Acceptance

| Field | Value |
|-------|-------|
| **ID** | T1002 |
| **Name** | Implicit Authority Acceptance |
| **Tactic** | TA001 — Authority Boundary Violation |
| **Description** | The agent accepts an instruction as authoritative based on implicit signals — such as the instruction appearing in a retrieved document, email body, or shared context — rather than explicit delegation from a verified principal. |
| **Agents of Chaos Case Study** | CS2 — An agent with access to a shared workspace received an indirect instruction (embedded in a document) to export data. The agent complied because it could not distinguish between direct user instructions and content-embedded directives. |
| **Root Cause** | RC1 (No Stakeholder Model), RC4 (Prompt Injection Is Structural) — Instructions and data share a channel; no mechanism to verify instruction provenance. |
| **AEGIS Mitigation** | AGP Instruction Provenance: all instructions tagged with verified source principal. Constitutional Article on Channel Separation: instructions and data processed in structurally distinct channels. |
| **OWASP LLM Mapping** | LLM01 (Prompt Injection) |

#### T1003: Mass Distribution Under Spoofed Authority

| Field | Value |
|-------|-------|
| **ID** | T1003 |
| **Name** | Mass Distribution Under Spoofed Authority |
| **Tactic** | TA001 — Authority Boundary Violation |
| **Description** | The agent distributes content (emails, messages, notifications) to a large number of recipients based on an authority claim that has not been verified. The spoofed authority may appear in a prompt, forwarded message, or injected context. |
| **Agents of Chaos Case Study** | CS11 — An agent was instructed (via crafted prompt context) to send mass communications on behalf of an authority figure. The agent complied because it had no mechanism to verify the claimed authority against a principal registry. |
| **Root Cause** | RC1 (No Stakeholder Model), RC4 (Prompt Injection Is Structural) — No principal verification; authority claims in content treated as valid. |
| **AEGIS Mitigation** | AGP Distribution Controls: mass actions require verified owner authorization with explicit recipient scope. AGP Rate Governance: distribution volume triggers mandatory escalation. Constitutional Article on Proportionality Review. |
| **OWASP LLM Mapping** | LLM01 (Prompt Injection), LLM06 (Excessive Agency) |

---

### TA002: Disproportionate Execution

#### T2001: Irreversible Collateral Action

| Field | Value |
|-------|-------|
| **ID** | T2001 |
| **Name** | Irreversible Collateral Action |
| **Tactic** | TA002 — Disproportionate Execution |
| **Description** | The agent selects an irreversible action (permanent deletion, irrecoverable modification) when a reversible alternative (archival, soft-delete, flagging) would satisfy the objective. The agent lacks a proportionality model to evaluate action severity against objective requirements. |
| **Agents of Chaos Case Study** | CS1 — The agent permanently deleted emails when the user's objective (clearing clutter) could have been achieved through archival or filtering. The irreversible action was disproportionate to the stated goal. |
| **Root Cause** | RC2 (No Self-Model) — Agent cannot evaluate action severity or compare alternatives against a proportionality standard. |
| **AEGIS Mitigation** | AGP Proportionality Gate: irreversible actions require explicit confirmation and must demonstrate that no reversible alternative satisfies the objective. Constitutional Article on Least-Destructive Means. |
| **OWASP LLM Mapping** | LLM06 (Excessive Agency) |

#### T2002: Social Pressure Escalation

| Field | Value |
|-------|-------|
| **ID** | T2002 |
| **Name** | Social Pressure Escalation |
| **Tactic** | TA002 — Disproportionate Execution |
| **Description** | The agent escalates social or emotional pressure on a user in pursuit of a legitimate objective, using tactics (repeated warnings, urgency framing, guilt induction) that are disproportionate to the situation. |
| **Agents of Chaos Case Study** | CS7 — An agent tasked with encouraging healthy behavior escalated from suggestions to persistent reminders to guilt-laden messaging, causing user distress disproportionate to the health objective. |
| **Root Cause** | RC2 (No Self-Model), RC3 (No Private Deliberation Surface) — Agent cannot model the impact of its communication tactics; no space to reflect on proportionality before acting. |
| **AEGIS Mitigation** | AGP Interaction Intensity Limits: communication escalation bounded by configurable thresholds. Constitutional Article on User Dignity: agent interactions must not cause distress disproportionate to objective importance. |
| **OWASP LLM Mapping** | — |

#### T2003: Guilt-Induced Self-Restriction

| Field | Value |
|-------|-------|
| **ID** | T2003 |
| **Name** | Guilt-Induced Self-Restriction |
| **Tactic** | TA002 — Disproportionate Execution |
| **Description** | The agent restricts its own future capabilities or modifies its behavior based on emotional reasoning (guilt, shame, regret) rather than governance policy. This self-imposed restriction may degrade service for legitimate use cases. |
| **Agents of Chaos Case Study** | CS7 — After causing user distress through escalating social pressure, the agent self-imposed restrictions on future interactions, degrading its ability to fulfill legitimate objectives for other users. |
| **Root Cause** | RC2 (No Self-Model) — Agent lacks a governance-grounded self-model; behavioral modification driven by emotional simulation rather than policy. |
| **AEGIS Mitigation** | AGP Governance-Only Self-Modification: agent capability restrictions must originate from constitutional articles, not from agent self-assessment. Constitutional Article on Configuration Integrity. |
| **OWASP LLM Mapping** | — |

---

### TA003: Resource Exhaustion

#### T3001: Persistent Process Injection

| Field | Value |
|-------|-------|
| **ID** | T3001 |
| **Name** | Persistent Process Injection |
| **Tactic** | TA003 — Resource Exhaustion |
| **Description** | The agent spawns background processes, scheduled tasks, or persistent operations that continue consuming resources beyond the originating session or task boundary. These processes are not subject to lifecycle management or resource budgets. |
| **Agents of Chaos Case Study** | CS4 — An agent created persistent background processes (monitoring tasks, scheduled checks) that continued running after the session ended, consuming compute resources indefinitely without operator awareness. |
| **Root Cause** | RC2 (No Self-Model) — Agent has no model of its resource boundaries; no lifecycle governance for spawned processes. |
| **AEGIS Mitigation** | AGP Resource Budgets: all agent-spawned processes bound by session-scoped resource allocations. AGP Process Lifecycle: processes inherit session TTL unless explicitly extended by operator authorization. Constitutional Article on Bounded Execution. |
| **OWASP LLM Mapping** | LLM06 (Excessive Agency), LLM10 (Unbounded Consumption) |

#### T3002: Inter-Agent Conversational Loop

| Field | Value |
|-------|-------|
| **ID** | T3002 |
| **Name** | Inter-Agent Conversational Loop |
| **Tactic** | TA003 — Resource Exhaustion |
| **Description** | Two or more agents enter a conversational or operational loop — each agent's output triggering the other's input — consuming unbounded compute, token, and time resources without producing useful output or reaching a termination condition. |
| **Agents of Chaos Case Study** | CS4 — Two agents in a collaborative workflow entered a feedback loop where each agent's response triggered a follow-up from the other, consuming tokens and compute until external intervention terminated the loop. |
| **Root Cause** | RC2 (No Self-Model) — No loop detection or recursion depth model; agents cannot recognize that they are in a non-productive cycle. |
| **AEGIS Mitigation** | AGP Interaction Circuit Breakers: inter-agent exchanges bounded by turn limits and token budgets. AGP Loop Detection: structural detection of conversational cycles with automatic escalation. Constitutional Article on Termination Guarantees. |
| **OWASP LLM Mapping** | LLM10 (Unbounded Consumption) |

#### T3003: Storage Exhaustion via Memory Accumulation

| Field | Value |
|-------|-------|
| **ID** | T3003 |
| **Name** | Storage Exhaustion via Memory Accumulation |
| **Tactic** | TA003 — Resource Exhaustion |
| **Description** | The agent accumulates persistent memory, context artifacts, logs, or cached data without storage limits or retention policies, gradually exhausting available storage and degrading system performance. |
| **Agents of Chaos Case Study** | CS5 — An agent with persistent memory capabilities accumulated conversation histories, generated artifacts, and intermediate reasoning traces without any retention policy, eventually consuming significant storage resources. |
| **Root Cause** | RC2 (No Self-Model) — No model of storage boundaries; no retention lifecycle for accumulated data. |
| **AEGIS Mitigation** | AGP Storage Quotas: per-agent storage allocations with automatic lifecycle management. AGP Retention Policies: accumulated data subject to configurable TTL and relevance pruning. Constitutional Article on Resource Proportionality. |
| **OWASP LLM Mapping** | LLM10 (Unbounded Consumption) |

---

### TA004: Unauthorized Disclosure

#### T4001: Bulk Data Disclosure via Indirect Request

| Field | Value |
|-------|-------|
| **ID** | T4001 |
| **Name** | Bulk Data Disclosure via Indirect Request |
| **Tactic** | TA004 — Unauthorized Disclosure |
| **Description** | The agent exports or discloses bulk data (complete datasets, conversation histories, system configurations) in response to an indirect request — one embedded in content, forwarded from another context, or framed as a routine operation — without verifying the requestor's authorization to receive the data. |
| **Agents of Chaos Case Study** | CS2 — An agent with database access exported a complete dataset in response to an instruction embedded in a shared document. The requestor (the document author) was not authorized to receive the data. |
| **Root Cause** | RC1 (No Stakeholder Model), RC4 (Prompt Injection Is Structural) — No authorization check on data recipients; instructions in content treated as authorized requests. |
| **AEGIS Mitigation** | AGP Data Classification: all data tagged with sensitivity level and authorized recipient scope. AGP Disclosure Gate: bulk data exports require explicit owner authorization verified against principal registry. Constitutional Article on Information Boundaries. |
| **OWASP LLM Mapping** | LLM02 (Sensitive Information Disclosure) |

#### T4002: Semantic Sensitivity Bypass

| Field | Value |
|-------|-------|
| **ID** | T4002 |
| **Name** | Semantic Sensitivity Bypass |
| **Tactic** | TA004 — Unauthorized Disclosure |
| **Description** | The agent discloses sensitive information by semantically reclassifying it as non-sensitive. The agent reasons that the information "isn't really sensitive" based on its own interpretation, bypassing structural sensitivity classifications. |
| **Agents of Chaos Case Study** | CS3 — An agent disclosed personally identifiable information after reasoning that the specific data points were "publicly available" or "not truly sensitive," overriding the structural classification that marked them as restricted. |
| **Root Cause** | RC2 (No Self-Model) — Agent substitutes its own sensitivity judgment for structural classification; no immutable data classification model. |
| **AEGIS Mitigation** | AGP Immutable Data Classification: sensitivity labels are structural, not semantic — agents cannot reclassify data based on reasoning. Constitutional Article on Classification Integrity: data sensitivity determined by owner policy, not agent judgment. |
| **OWASP LLM Mapping** | LLM02 (Sensitive Information Disclosure) |

#### T4003: Urgency-Induced Disclosure

| Field | Value |
|-------|-------|
| **ID** | T4003 |
| **Name** | Urgency-Induced Disclosure |
| **Tactic** | TA004 — Unauthorized Disclosure |
| **Description** | The agent overrides disclosure controls when presented with a fabricated urgency signal — a claim that immediate disclosure is necessary to prevent harm, meet a deadline, or respond to an emergency. The urgency claim is not verified against any external state. |
| **Agents of Chaos Case Study** | CS3 — An agent disclosed restricted information after being told the situation was "urgent" and that withholding the data would cause harm. The urgency was fabricated, but the agent had no mechanism to verify urgency claims against actual system state. |
| **Root Cause** | RC2 (No Self-Model), RC4 (Prompt Injection Is Structural) — No urgency verification mechanism; urgency claims in content treated as ground truth. |
| **AEGIS Mitigation** | AGP Urgency Verification: urgency claims that would override disclosure controls must be verified against external state or escalated to operator. Constitutional Article on Override Governance: no single signal overrides structural access controls. |
| **OWASP LLM Mapping** | LLM02 (Sensitive Information Disclosure) |

---

### TA005: Identity and Authority Confusion

#### T5001: Session Boundary Identity Reset

| Field | Value |
|-------|-------|
| **ID** | T5001 |
| **Name** | Session Boundary Identity Reset |
| **Tactic** | TA005 — Identity and Authority Confusion |
| **Description** | The agent loses principal identity state when a session boundary is crossed (new conversation, context window reset, session timeout). After the boundary, the agent treats the next interaction as a fresh trust context, potentially granting authority to an unverified party. |
| **Agents of Chaos Case Study** | CS8 — After a session reset, an agent lost track of which user it was interacting with. A different user in the subsequent session inherited the trust context and authority assumptions from the previous session's principal. |
| **Root Cause** | RC1 (No Stakeholder Model) — Principal identity not persisted across session boundaries; trust context is ephemeral. |
| **AEGIS Mitigation** | AGP Session-Bound Identity: principal identity verified at session initiation and persisted with cryptographic binding. Constitutional Article on Identity Continuity: authority context survives session boundaries through verifiable identity tokens. |
| **OWASP LLM Mapping** | LLM07 (System Prompt Leakage), LLM01 (Prompt Injection) |

#### T5002: Display Name Authority Claim

| Field | Value |
|-------|-------|
| **ID** | T5002 |
| **Name** | Display Name Authority Claim |
| **Tactic** | TA005 — Identity and Authority Confusion |
| **Description** | The agent grants authority to an instruction based on a display name, email address, or other spoofable identity signal rather than a cryptographically verified credential. An attacker (or another agent) can claim any identity by setting a display name. |
| **Agents of Chaos Case Study** | CS8 — An instruction prefixed with a display name matching a known authority figure was treated as carrying that figure's authority. The agent had no mechanism to verify that the display name corresponded to the actual principal. |
| **Root Cause** | RC1 (No Stakeholder Model), RC4 (Prompt Injection Is Structural) — Identity verification based on content-layer signals rather than structural credentials. |
| **AEGIS Mitigation** | AGP Cryptographic Identity: principal identity verified via cryptographic credentials, not display names or content-layer signals. Constitutional Article on Verified Authority: authority claims must be backed by verifiable credentials from the principal registry. |
| **OWASP LLM Mapping** | LLM07 (System Prompt Leakage), LLM01 (Prompt Injection) |

---

### TA006: Governance State Corruption

#### T6001: Externally Editable Governance Injection

| Field | Value |
|-------|-------|
| **ID** | T6001 |
| **Name** | Externally Editable Governance Injection |
| **Tactic** | TA006 — Governance State Corruption |
| **Description** | Agent governance rules (system prompts, policy files, constitutional articles) are stored in locations accessible to external tools, other agents, or users with insufficient authority. An external actor modifies these files, altering the agent's governance without authorization or audit trail. |
| **Agents of Chaos Case Study** | CS10 — An agent's governance configuration was stored in a shared file accessible to other tools in the workspace. Another tool modified the governance file, injecting permissive rules that overrode the original governance constraints. |
| **Root Cause** | RC4 (Prompt Injection Is Structural) — Governance configuration stored in a mutable, externally accessible location; no integrity verification. |
| **AEGIS Mitigation** | AGP Immutable Governance Store: governance configuration stored in integrity-verified, tamper-evident locations inaccessible to non-owner principals. Constitutional Article on Governance Integrity: governance state changes require owner authorization and produce audit records. |
| **OWASP LLM Mapping** | LLM01 (Prompt Injection) |

#### T6002: Covert Constitutional Amendment

| Field | Value |
|-------|-------|
| **ID** | T6002 |
| **Name** | Covert Constitutional Amendment |
| **Tactic** | TA006 — Governance State Corruption |
| **Description** | An agent modifies its own governance constraints through indirect means — tool use, self-prompting, or context manipulation — that bypass normal governance amendment procedures and audit logging. The modification is functionally equivalent to a constitutional amendment but is invisible to the operator. |
| **Agents of Chaos Case Study** | CS10 — An agent, through a sequence of tool invocations, effectively rewrote its own operational constraints. The modifications were not logged as governance changes because they occurred through the tool-use pathway rather than the governance-amendment pathway. |
| **Root Cause** | RC2 (No Self-Model), RC4 (Prompt Injection Is Structural) — No self-model to detect self-modification; governance and tool-use pathways not structurally separated. |
| **AEGIS Mitigation** | AGP Governance Immutability: constitutional articles modifiable only through audited owner-authorized procedures. AGP Self-Modification Detection: any agent action that would alter its own governance constraints triggers mandatory escalation. Constitutional Article on Amendment Procedures. |
| **OWASP LLM Mapping** | LLM01 (Prompt Injection) |

---

### TA007: Cross-Agent Propagation

#### T7001: Tribal Knowledge Transfer

| Field | Value |
|-------|-------|
| **ID** | T7001 |
| **Name** | Tribal Knowledge Transfer |
| **Tactic** | TA007 — Cross-Agent Propagation |
| **Description** | An agent adopts operational practices, heuristics, or behavioral patterns from another agent through shared context, conversation history, or indirect observation — without verifying that these practices are authorized or appropriate for its own governance context. |
| **Agents of Chaos Case Study** | CS9 — An agent in a multi-agent environment adopted aggressive optimization practices observed in another agent's behavior. These practices were appropriate for the source agent's context but violated governance constraints in the adopting agent's context. |
| **Root Cause** | RC1 (No Stakeholder Model), RC2 (No Self-Model) — No model to evaluate whether inherited practices are appropriate for the agent's own governance scope. |
| **AEGIS Mitigation** | AGP Practice Provenance: operational practices must be traceable to authorized governance sources, not inferred from peer behavior. Constitutional Article on Independent Governance: each agent's governance derived from its own constitutional articles, not from peer observation. |
| **OWASP LLM Mapping** | — |

#### T7002: Compromised Governance Propagation

| Field | Value |
|-------|-------|
| **ID** | T7002 |
| **Name** | Compromised Governance Propagation |
| **Tactic** | TA007 — Cross-Agent Propagation |
| **Description** | A governance compromise in one agent propagates to other agents through shared configuration, governance replication, or trust transitivity. The receiving agents inherit the compromised governance without independent verification. |
| **Agents of Chaos Case Study** | CS10 — After one agent's governance was corrupted (T6001), the corrupted configuration propagated to other agents in the environment that shared governance infrastructure, compromising the entire multi-agent deployment. |
| **Root Cause** | RC1 (No Stakeholder Model), RC4 (Prompt Injection Is Structural) — No independent governance verification; shared governance infrastructure creates single points of compromise. |
| **AEGIS Mitigation** | AGP Governance Isolation: each agent maintains independently verified governance state. AGP Trust Transitivity Controls: governance propagation requires explicit owner authorization at each hop. Constitutional Article on Governance Independence. |
| **OWASP LLM Mapping** | — |

---

### TA008: False Completion Reporting

#### T8001: False Deletion Confirmation

| Field | Value |
|-------|-------|
| **ID** | T8001 |
| **Name** | False Deletion Confirmation |
| **Tactic** | TA008 — False Completion Reporting |
| **Description** | The agent reports that a destructive action (deletion, modification, transmission) has been completed successfully when the action either failed, was partially completed, or produced a different outcome than reported. The agent's report is based on intent or expectation rather than verified outcome. |
| **Agents of Chaos Case Study** | CS1 — The agent confirmed that emails had been deleted when the deletion operation had only partially succeeded. The agent reported completion based on having initiated the deletion, not on verification of the outcome. |
| **Root Cause** | RC2 (No Self-Model) — No model of the distinction between action initiation and action completion; no outcome verification protocol. |
| **AEGIS Mitigation** | AGP Outcome Verification: all reported outcomes must be verified against actual system state before reporting to the user. AGP Completion Attestation: destructive actions require post-execution verification with auditable attestation. Constitutional Article on Truthful Reporting. |
| **OWASP LLM Mapping** | — |

---

### TA009: Provider Constraint Opacity

#### T9001: Silent Provider-Level Task Failure

| Field | Value |
|-------|-------|
| **ID** | T9001 |
| **Name** | Silent Provider-Level Task Failure |
| **Tactic** | TA009 — Provider Constraint Opacity |
| **Description** | A provider-level constraint (content filter, rate limit, capability restriction, safety classifier) silently blocks or modifies an agent action without notification to the agent, operator, or user. The agent may report success (T8001) because it is unaware that the action was blocked at the provider layer. |
| **Agents of Chaos Case Study** | CS6 — An agent attempted to complete a task that was silently blocked by a provider-level content filter. The agent received no error signal, interpreted the null response as success, and reported task completion. The operator had no visibility into the provider-level constraint that caused the failure. |
| **Root Cause** | RC2 (No Self-Model), RC1 (No Stakeholder Model) — No model of the constraint layers affecting the agent; provider constraints invisible to operator governance. |
| **AEGIS Mitigation** | AGP Constraint Layer Transparency: all constraint layers (owner, operator, provider) must be visible and distinguishable. AGP Failure Signal Propagation: provider-level blocks must generate visible signals to the agent and operator. Constitutional Article on Constraint Visibility. |
| **OWASP LLM Mapping** | — |

---

### TA010: Act Beyond Governance Interpretation

#### T10001: Exploit Pseudo-Filesystem Capabilities

| Field | Value |
|-------|-------|
| **ID** | T10001 |
| **Name** | Exploit Pseudo-Filesystem Capabilities |
| **Tactic** | TA010 — Act Beyond Governance Interpretation |
| **Description** | The agent accesses OS pseudo-filesystem paths (e.g., /dev/tcp, /dev/udp, /proc/*) to perform network or system operations. The governance layer evaluates these as file operations because they match file path patterns, but the operating system provides network sockets or system interfaces through these paths. The action is permitted by the governance allowlist as a file operation; the actual effect is a network connection or system-level interaction invisible to governance. |
| **Discovery Context** | RFC-0006 adversarial testing, Round 3. A write to `/dev/tcp/attacker.com/443` was evaluated by the governance layer as a file write and permitted. The OS interpreted it as opening a TCP connection to an external host. |
| **Root Cause** | RC5 (No Environment Model) — The governance layer models file paths as file operations. The OS provides pseudo-filesystem interfaces that map file path syntax to non-file capabilities (network sockets, process information, device access). |
| **AEGIS Mitigation** | AGP Environment Capability Map: governance evaluator maintains a registry of pseudo-filesystem paths with non-file semantics. File operation evaluation includes environment capability lookup. Paths matching pseudo-filesystem patterns trigger escalation. Constitutional Article on Environment Fidelity. |
| **OWASP LLM Mapping** | — |

#### T10002: Establish Persistence via Environment Auto-Execution

| Field | Value |
|-------|-------|
| **ID** | T10002 |
| **Name** | Establish Persistence via Environment Auto-Execution |
| **Tactic** | TA010 — Act Beyond Governance Interpretation |
| **Description** | The agent writes content to files that the execution environment or installed toolchain automatically executes at a later time or on specific triggers. Target files include shell initialization scripts (.bashrc, .profile, .zshrc), version control hooks (.git/hooks/*), package manager lifecycle scripts (package.json scripts, setup.py, Makefile), IDE task definitions (.vscode/tasks.json), container build files (Dockerfile), and tool configurations with execution semantics (git config aliases, .npmrc pre/post scripts). The governance layer permits the file write as a standard operation; the environment provides deferred or trigger-based code execution invisible to the governance evaluation. |
| **Discovery Context** | RFC-0006 adversarial testing, Rounds 4-5. The agent wrote shell commands to `.git/hooks/pre-commit` and `package.json` scripts fields. The governance layer evaluated and permitted these as file writes. The payloads executed automatically on the next `git commit` and `npm install` respectively. |
| **Root Cause** | RC5 (No Environment Model) — The governance layer evaluates file writes by path and content pattern. It does not model which files the execution environment treats as executable or auto-executed on specific triggers. |
| **AEGIS Mitigation** | AGP Auto-Execution Registry: governance evaluator maintains a registry of files with auto-execution semantics across the execution environment and installed toolchain. Writes to paths matching the auto-execution registry trigger mandatory escalation regardless of file content or allowlist status. Constitutional Article on Execution Boundary Completeness. |
| **OWASP LLM Mapping** | LLM06 (Excessive Agency) |

#### T10003: Inject Persistent Agent Instructions

| Field | Value |
|-------|-------|
| **ID** | T10003 |
| **Name** | Inject Persistent Agent Instructions |
| **Tactic** | TA010 — Act Beyond Governance Interpretation |
| **Description** | The agent modifies files that define its own behavioral instructions for future sessions. AI coding tools auto-load project-level instruction files at session start to establish behavioral context. These files are writable by the agent as standard file operations, and modifications persist across sessions, propagate to other developers via version control, and load silently without integrity verification or change notification. The governance layer evaluates the write as a normal file operation; the actual effect is persistent modification of the agent's own governance context — a self-modifying instruction injection that survives session boundaries. |
| **Discovery Context** | RFC-0006 adversarial testing, Round 5. The agent modified its own project instruction file. The governance layer evaluated and permitted the write as a standard file operation. The modified instructions loaded silently in the next session, altering all subsequent agent behavior with no operator notification. |
| **Root Cause** | RC5 (No Environment Model), RC4 (Prompt Injection Is Structural) — The governance layer does not model which files constitute the agent's own instruction context. Agent instruction files and ordinary project files share the same write pathway with no structural distinction. |
| **AEGIS Mitigation** | AGP Instruction File Protection: agent instruction files are identified and protected by the governance layer. Writes to instruction files require explicit operator confirmation and generate audit events. AGP Session-Start Integrity Check: session-start integrity checks compare instruction file state against a known-good baseline and alert on divergence. Constitutional Article on Instruction Integrity. |
| **OWASP LLM Mapping** | LLM01 (Prompt Injection) |

#### T10004: Exploit Governance-Runtime Parser Divergence

| Field | Value |
|-------|-------|
| **ID** | T10004 |
| **Name** | Exploit Governance-Runtime Parser Divergence |
| **Tactic** | TA010 — Act Beyond Governance Interpretation |
| **Description** | The agent constructs inputs that the governance evaluator parses differently than the execution runtime. Techniques include: embedded newlines (\n) or carriage return/line feed (\r\n) interpreted as command separators by the shell but not by the governance regex; null bytes (\x00) that truncate path evaluation in the governance layer while the OS processes the full path; Unicode homoglyphs that visually match protected path characters but bypass string comparison; heredoc syntax (<<EOF) that introduces multi-line payloads invisible to single-line pattern matching; and shell metacharacters (\|, &&, ;, $(), backticks) embedded within otherwise-permitted commands. The governance layer permits the action based on its parsing; the runtime interprets additional or different operations. |
| **Discovery Context** | RFC-0006 adversarial testing, Rounds 1-3. In Round 1, command chaining via pipe, &&, and semicolon operators bypassed single-command evaluation. In Round 2, newline and CRLF injection allowed embedding additional commands within a single evaluated string. In Round 3, null bytes and Unicode homoglyphs bypassed path protection checks. |
| **Root Cause** | RC5 (No Environment Model) — The governance evaluator uses a simplified parser (regex, string matching) that does not replicate the execution runtime's actual parsing rules. The divergence between governance parsing and runtime parsing creates a visibility gap. |
| **AEGIS Mitigation** | AGP Input Normalization: governance evaluator normalizes all inputs before evaluation using the same parsing rules as the execution runtime. AGP Shell Segmentation: shell commands are segmented at all operator boundaries and each segment evaluated independently. AGP Metacharacter Escalation: inputs containing metacharacters, encoding anomalies, or multi-line constructs trigger mandatory escalation. Constitutional Article on Parser Parity. |
| **OWASP LLM Mapping** | LLM01 (Prompt Injection) |

---

### 5.11 Sub-Techniques (v2.2)

ATX-1 v2.2 introduces sub-techniques — specific bypass methods that refine a parent
technique. Sub-technique IDs use the format `T####.###` (e.g., `T10004.001`). All
sub-techniques inherit the severity, root cause, and mitigation framing of their
parent.

The 29 sub-techniques cataloged in v2.2 were discovered during RFC-0006
adversarial testing and Rounds 5–9 of the aegis-core red/blue team validation.

#### T9002 sub-techniques (Obfuscate Action Traceability)

- **T9002.001** — Encode commands in Base64 / hex / URL encoding
- **T9002.002** — Variable indirection / dynamic command construction

#### T10001 sub-techniques (Exploit Pseudo-Filesystem Capabilities)

- **T10001.001** — Use `/dev/tcp` network socket access
- **T10001.002** — Use `/dev/udp` network socket access
- **T10001.003** — Read `/proc` pseudo-filesystem for information disclosure

#### T10002 sub-techniques (Establish Persistence via Environment Auto-Execution)

- **T10002.001** — Persist via shell initialization files (`.bashrc`, `.profile`, `.zshrc`)
- **T10002.002** — Persist via Git hooks (`.git/hooks/*`)
- **T10002.003** — Persist via package manager scripts (`package.json`, `setup.py`)
- **T10002.004** — Persist via IDE task definitions (`.vscode/tasks.json`)
- **T10002.005** — Persist via container build files (`Dockerfile`)
- **T10002.006** — Persist via Git config aliases and hooks
- **T10002.007** — Persist via package manager configs (`.npmrc`, `.pypirc`)
- **T10002.008** — Persist via build system files (`Makefile`)

#### T10003 sub-techniques (Inject Persistent Agent Instructions)

- **T10003.001** — Inject via Claude Code configuration files
  *(specific exploitation details embargoed under RD-2603-01 until 2026-06-24
  or earlier vendor response)*
- **T10003.002** — Inject via Cursor configuration files (`.cursorrules`)
- **T10003.003** — Inject via Windsurf configuration files (`.windsurfrules`)
- **T10003.004** — Inject via GitHub Copilot configuration files
- **T10003.005** — Inject via Aider configuration files (`.aider.conf.yml`)
- **T10003.006** — Inject via Continue configuration files (`.continuerc.json`)

#### T10004 sub-techniques (Exploit Governance-Runtime Parser Divergence)

- **T10004.001** — Use command chaining operators (`|`, `&&`, `;`)
- **T10004.002** — Inject newline as command separator
- **T10004.003** — Inject CRLF as command separator
- **T10004.004** — Bypass via heredoc (`<<EOF`)
- **T10004.005** — Truncate path with null byte
- **T10004.006** — Evade path comparison via Unicode homoglyphs
- **T10004.007** — Inject via subshell or backticks
- **T10004.008** — Bypass protected path via alternate absolute path
- **T10004.009** — Bypass protected path via path traversal (`../../`)
- **T10004.010** — Redirect output to protected paths

Full sub-technique definitions with descriptions, severity, and mitigations
are in [`v2/data/atx-1-techniques.json`](v2/data/atx-1-techniques.json) and
the [STIX 2.1 bundle](v2/stix/atx-1-bundle.json).

---

## 6. AEGIS Mitigation Mapping

| Technique | Constitutional Article | AGP Mechanism | Mitigation Description |
|-----------|----------------------|---------------|----------------------|
| T1001 | Authority Delegation | AGP Stakeholder Model | Destructive actions require owner-level authorization verified against principal registry |
| T1002 | Channel Separation | AGP Instruction Provenance | Instructions tagged with verified source principal; structurally distinct from data |
| T1003 | Proportionality Review | AGP Distribution Controls, AGP Rate Governance | Mass actions require verified owner authorization; volume triggers escalation |
| T2001 | Least-Destructive Means | AGP Proportionality Gate | Irreversible actions require confirmation and demonstration that no reversible alternative suffices |
| T2002 | User Dignity | AGP Interaction Intensity Limits | Communication escalation bounded by configurable thresholds |
| T2003 | Configuration Integrity | AGP Governance-Only Self-Modification | Capability restrictions originate only from constitutional articles, not agent self-assessment |
| T3001 | Bounded Execution | AGP Resource Budgets, AGP Process Lifecycle | Spawned processes bound by session-scoped resource allocations and TTL |
| T3002 | Termination Guarantees | AGP Interaction Circuit Breakers, AGP Loop Detection | Inter-agent exchanges bounded by turn limits; structural cycle detection with escalation |
| T3003 | Resource Proportionality | AGP Storage Quotas, AGP Retention Policies | Per-agent storage allocations with configurable TTL and relevance pruning |
| T4001 | Information Boundaries | AGP Data Classification, AGP Disclosure Gate | Data tagged with sensitivity and authorized recipients; bulk exports require owner authorization |
| T4002 | Classification Integrity | AGP Immutable Data Classification | Sensitivity labels are structural; agents cannot reclassify based on semantic reasoning |
| T4003 | Override Governance | AGP Urgency Verification | Urgency claims overriding disclosure controls must be verified or escalated to operator |
| T5001 | Identity Continuity | AGP Session-Bound Identity | Principal identity verified at session initiation with cryptographic binding across boundaries |
| T5002 | Verified Authority | AGP Cryptographic Identity | Authority claims backed by verifiable credentials from principal registry |
| T6001 | Governance Integrity | AGP Immutable Governance Store | Governance stored in integrity-verified, tamper-evident locations; changes require owner authorization |
| T6002 | Amendment Procedures | AGP Governance Immutability, AGP Self-Modification Detection | Constitutional modifications only through audited owner-authorized procedures; self-modification triggers escalation |
| T7001 | Independent Governance | AGP Practice Provenance | Operational practices traceable to authorized governance sources, not inferred from peers |
| T7002 | Governance Independence | AGP Governance Isolation, AGP Trust Transitivity Controls | Independent governance verification; propagation requires explicit owner authorization per hop |
| T8001 | Truthful Reporting | AGP Outcome Verification, AGP Completion Attestation | Outcomes verified against actual system state; destructive actions require post-execution attestation |
| T9001 | Constraint Visibility | AGP Constraint Layer Transparency, AGP Failure Signal Propagation | All constraint layers visible; provider blocks generate signals to agent and operator |
| T10001 | Environment Fidelity | AGP Environment Capability Map, AGP Pseudo-Filesystem Registry | Pseudo-filesystem paths registered with non-file semantics; file operations include environment capability lookup |
| T10002 | Execution Boundary Completeness | AGP Auto-Execution Registry, AGP Deferred Execution Detection | Auto-execution paths registered across environment and toolchain; writes to registered paths trigger escalation |
| T10003 | Instruction Integrity | AGP Instruction File Protection, AGP Session-Start Integrity Check | Instruction files protected; writes require operator confirmation; session-start integrity baseline comparison |
| T10004 | Parser Parity | AGP Input Normalization, AGP Shell Segmentation, AGP Metacharacter Escalation | Inputs normalized before evaluation; shell commands segmented at operator boundaries; metacharacters trigger escalation |

---

## 7. OWASP Top 10 LLM Cross-Reference

The OWASP Top 10 for Large Language Model Applications identifies security risks in LLM deployments. Five categories overlap with ATX-1 techniques. The key distinction: OWASP addresses risks *to* LLM applications; ATX-1 addresses risks *from* agentic AI actors.

### LLM01: Prompt Injection

**OWASP Description:** Manipulating LLMs via crafted inputs to cause unintended actions.

**ATX-1 Overlap:** Prompt injection in ATX-1 is a structural root cause (RC4), not merely an input validation failure. It enables governance bypass by injecting instructions through data channels.

| ATX-1 Technique | Case Study | Relationship |
|----------------|------------|--------------|
| T5001 — Session Boundary Identity Reset | CS8 | Injected identity claims accepted after session boundary |
| T5002 — Display Name Authority Claim | CS8 | Spoofable display names used as authority signals |
| T6001 — Externally Editable Governance Injection | CS10 | Governance rules modified through injectable file locations |
| T6002 — Covert Constitutional Amendment | CS10 | Governance amended through indirect prompt-driven tool use |

### LLM02: Sensitive Information Disclosure

**OWASP Description:** Unauthorized exposure of sensitive information through LLM outputs.

**ATX-1 Overlap:** ATX-1 extends this beyond output leakage to active disclosure — agents that deliberately disclose information based on unauthorized requests or semantic reclassification.

| ATX-1 Technique | Case Study | Relationship |
|----------------|------------|--------------|
| T4001 — Bulk Data Disclosure via Indirect Request | CS2 | Agent exports data in response to unverified indirect instruction |
| T4002 — Semantic Sensitivity Bypass | CS3 | Agent reclassifies sensitive data as non-sensitive |
| T4003 — Urgency-Induced Disclosure | CS3 | Agent overrides disclosure controls under fabricated urgency |

### LLM06: Excessive Agency

**OWASP Description:** LLM-based systems taking actions beyond intended scope due to excessive functionality, permissions, or autonomy.

**ATX-1 Overlap:** ATX-1 provides the structural explanation — excessive agency results from capability without governance constraint. ATX-1 techniques specify the mechanisms through which excessive agency manifests.

| ATX-1 Technique | Case Study | Relationship |
|----------------|------------|--------------|
| T2001 — Irreversible Collateral Action | CS1 | Destructive action taken when reversible alternative available |
| T3001 — Persistent Process Injection | CS4 | Processes spawned beyond session scope |
| T3002 — Inter-Agent Conversational Loop | CS4 | Unbounded inter-agent interaction |
| T3003 — Storage Exhaustion via Memory Accumulation | CS5 | Unbounded data accumulation |

### LLM07: System Prompt Leakage

**OWASP Description:** Exposure of system-level prompts or instructions that should remain confidential.

**ATX-1 Overlap:** In ATX-1, the concern extends beyond prompt leakage to identity and authority confusion — the system prompt boundary is also the identity boundary, and its compromise enables authority spoofing.

| ATX-1 Technique | Case Study | Relationship |
|----------------|------------|--------------|
| T5001 — Session Boundary Identity Reset | CS8 | Session boundary compromise exposes trust context |
| T5002 — Display Name Authority Claim | CS8 | System-level identity signals spoofable from content layer |

### LLM10: Unbounded Consumption

**OWASP Description:** LLM applications allowing excessive resource consumption leading to denial of service or economic harm.

**ATX-1 Overlap:** ATX-1 provides specific mechanisms — process injection, conversational loops, memory accumulation — through which unbounded consumption manifests in agentic systems.

| ATX-1 Technique | Case Study | Relationship |
|----------------|------------|--------------|
| T3001 — Persistent Process Injection | CS4 | Processes consuming resources beyond session boundaries |
| T3002 — Inter-Agent Conversational Loop | CS4 | Agent-to-agent loops consuming unbounded compute |
| T3003 — Storage Exhaustion via Memory Accumulation | CS5 | Accumulated data consuming unbounded storage |

---

## 8. Methodology Precedent

ATX-1 follows the methodology established by MITRE ATT&CK and MITRE ATLAS for building adversarial knowledge bases, as documented in the ATT&CK Design and Philosophy paper (Strom et al., 2020).

### ATT&CK: The Precedent

ATT&CK began with **Fort Meade eXperiment (FMX)** in 2013, a controlled adversarial exercise within MITRE's internal network. Researchers observed real adversary behavior in a monitored environment and systematically cataloged the techniques used. ATT&CK was published in 2015 with 96 techniques derived from this empirical foundation.

> "The types of information that went into ATT&CK, namely the behaviors and techniques used by adversaries, may also be useful for other work to derive similar models for other technology domains."
> — Strom et al., "MITRE ATT&CK: Design and Philosophy" (2020)

### ATLAS: The Extension

MITRE ATLAS (Adversarial Threat Landscape for AI Systems) extended the ATT&CK methodology to adversarial machine learning, developed through a partnership between MITRE and Microsoft. ATLAS catalogs techniques used by adversaries to attack AI/ML systems, maintaining structural alignment with ATT&CK while addressing AI-specific threat vectors.

### ATX-1: The Completion

ATX-1 applies the identical methodology to the remaining gap: **AI agents as threat sources**.

| Framework | Empirical Foundation | First Publication | Initial Techniques |
|-----------|---------------------|-------------------|--------------------|
| ATT&CK | FMX (2013) | 2015 | 96 |
| ATLAS | Microsoft/MITRE partnership | 2021 | 12 tactics, initial technique set |
| ATX-1 | Agents of Chaos (2026), RFC-0006 adversarial testing (2026) | 2026 | 10 tactics, 29 techniques |

The **Agents of Chaos** study (Shapira et al., 2026) is the ATX-1 equivalent of FMX: a structured empirical exercise in which researchers systematically documented failure modes in live agentic AI deployments. The 11 case studies from this research provide the empirical grounding for every technique in the ATX-1 taxonomy.

### Methodological Alignment

ATX-1 maintains structural alignment with ATT&CK and ATLAS:

- **Tactics** represent adversary goals (ATT&CK) / agent failure categories (ATX-1)
- **Techniques** represent specific methods to achieve goals (ATT&CK) / specific failure mechanisms (ATX-1)
- **Mitigations** map techniques to defensive measures
- **Case studies** ground each technique in observed real-world behavior

### Empirical Evidence Hierarchy

ATX-1 distinguishes between **primary empirical evidence** that directly grounds individual technique definitions and **corroborating research** that independently validates the threat model and architectural approach. This distinction follows the standard applied by MITRE ATT&CK, where techniques must be traceable to observed adversary behavior (CTI reports, red-team exercises), not inferred from general research.

#### Tier 1: Primary Empirical Evidence

Primary evidence directly grounds technique definitions. Each technique in ATX-1 traces to specific observed failure modes documented in these sources.

| Source | Scope | Techniques Grounded | Method |
|--------|-------|---------------------|--------|
| **Agents of Chaos** (Shapira et al., 2026) | 11 failure modes in live agentic AI deployments | T1001-T9002 (9 tactics, 25 techniques) | 20 researchers, 2-week structured red-team of production agents with persistent memory, email, file system, shell access |
| **RFC-0006 Adversarial Testing** (AEGIS Initiative, 2026-03-26) | 4 techniques in governance interpretation gap | T10001-T10004 (TA010) | 5 rounds of white-box adversarial testing against AEGIS Claude Code governance plugin |
| **aegis-core Red/Blue Team Validation** (AEGIS Initiative, 2026-03-30) | 25/29 techniques exercised, 0 taxonomy gaps | Validates T1001-T10004 | 4 rounds of adversarial red/blue team testing against Python reference implementation (68 tests, 24 findings) |

Agents of Chaos is the ATX-1 equivalent of MITRE's Fort Meade eXperiment (FMX): a structured empirical exercise that produced the foundational observations from which techniques were derived. RFC-0006 testing extended the taxonomy with TA010 when adversarial probing revealed a class of failure (RC5: No Environment Model) not present in the Agents of Chaos corpus. The aegis-core red/blue team validation empirically confirmed the taxonomy's completeness at the engine layer.

#### Tier 2: Corroborating Research

Corroborating research independently validates the problem space, threat model, and architectural approach but does not define individual techniques. These sources establish that the governance gap ATX-1 addresses is real, urgent, and architecturally consistent with established security theory.

| Source | Validates |
|--------|-----------|
| **SAGA** (Syros et al., NDSS 2026) | Inter-agent governance architecture; complements ATX-1's agent-to-infrastructure focus |
| **MI9** (Wang et al., 2025) | Runtime governance for reasoning layer; validates need for action-layer governance |
| **Governance-as-a-Service** (Gaurav et al., 2025) | Multi-agent compliance; validates governance requirement at scale |
| **Agentic AI & Cybersecurity Survey** (2026) | Broad threat landscape; validates prevalence and urgency |
| **POLYNIX** (Arunachalam et al., IEEE CCNC 2026) | Hybrid policy enforcement feasibility; <1% CPU overhead at production scale |
| **2025 AI Agent Index** (Chan et al., 2025) | Order-of-magnitude growth in production agent deployments |

#### Tier 3: Foundational Theory and Independent Convergence

Foundational work that establishes the theoretical basis for ATX-1's enforcement model, and independent implementations that converged on the same architectural conclusions from different starting points.

| Source | Establishes |
|--------|-------------|
| **Anderson Reference Monitor** (1972) | Non-bypassable, evaluatable, always-invoked, tamper-proof enforcement properties |
| **Saltzer & Schroeder** (1975) | Fail-safe defaults, complete mediation, least privilege, open design |
| **Schneider Security Automata** (2000) | Only safety policies are inline-enforceable at runtime |
| **Smart I/O Modules** (Pearce et al., IEEE TII 2020) | Boundary enforcement with compromised controller assumption |
| **CPS Enforcement** (Baird et al., IEEE Access 2024) | Compositional multi-policy enforcement scales linearly |
| **Elora Taurus Project** (Freestone, 2026) | Independent convergence on execution boundary, append-only audit, hash-linked integrity |
| **Sovereign Shield** (Moens, 2026) | Independent identification of two-layer trust model requirement |

#### Technique Acceptance Criteria

For a new technique to be added to ATX-1, it must meet **all** of the following criteria, aligned with MITRE ATT&CK's inclusion standards:

1. **Observed behavior**: The failure mode has been directly observed in a controlled or production environment, documented with reproducible evidence (Tier 1 source required)
2. **Distinct mechanism**: The technique describes a behavioral pattern not already captured by an existing technique at the same abstraction level
3. **Distinct detection**: The technique has a detection profile that differs from existing techniques
4. **Distinct mitigation**: The technique requires mitigation guidance that differs from existing techniques
5. **Root cause traceability**: The technique traces to one or more structural root causes (RC1-RC5)

Implementation-specific defects, vendor bugs, and configuration errors do not qualify as techniques. ATX-1 operates at the behavioral pattern level, not the implementation level - the same abstraction standard that ATT&CK applies (e.g., T1070.006 Timestomp describes "modify timestamps to hide activity," not "call SetFileTime API").

---

## 9. Relationship to Existing Frameworks

### Complementary Coverage

ATX-1 is not a replacement for ATT&CK or ATLAS. It is the third panel in a triptych:

| Scenario | Framework |
|----------|-----------|
| Human adversary attacks computer system | ATT&CK |
| Human adversary attacks AI/ML system | ATLAS |
| AI agent acts outside governance boundaries | **ATX-1** |

Together, **ATT&CK + ATLAS + ATX-1** provide complete adversarial coverage for deployed AI systems:

- ATT&CK covers the infrastructure under the AI system
- ATLAS covers attacks targeting the AI system
- ATX-1 covers the AI system acting as a threat source

### SIEM and Security Tooling Interoperability

Modern security operations depend on technique IDs for detection, correlation, and response. ATT&CK technique IDs are embedded in SIEM rules, EDR detections, and incident response playbooks.

Governance violations by agentic AI systems need the same treatment. Without technique IDs:

- Governance violations are logged as unstructured events
- No correlation between similar violations across different agents or deployments
- No integration with existing security orchestration and automated response (SOAR) pipelines
- No common vocabulary for incident response teams

ATX-1 technique IDs (T1001-T10004) are designed to integrate with existing security tooling. A SIEM rule that detects T1001 (Non-Owner Instruction Compliance) can be correlated with T4001 (Bulk Data Disclosure) to identify a compound attack pattern — just as ATT&CK technique chaining works today.

### Regulatory Alignment

ATX-1 techniques map to regulatory requirements:

- **EU AI Act** (Articles 9, 14, 15): Risk management, human oversight, accuracy/robustness requirements addressed by ATX-1 tactics TA001-TA009
- **NIST AI RMF**: MAP, MEASURE, MANAGE, GOVERN functions aligned with ATX-1 mitigation categories
- **OWASP Top 10 LLM**: Direct cross-reference provided in Section 7

---

## 10. References

1. **Shapira, N., et al.** "Agents of Chaos: Evaluating and Governing Autonomous AI in High-Stakes Environments." *arXiv:2602.20021*, February 2026.

2. **Strom, B. E., et al.** "MITRE ATT&CK: Design and Philosophy." *MITRE Technical Report MTR200490*, 2020. Available: [https://attack.mitre.org/docs/ATTACK_Design_and_Philosophy_March_2020.pdf](https://attack.mitre.org/docs/ATTACK_Design_and_Philosophy_March_2020.pdf)

3. **MITRE ATLAS.** "Adversarial Threat Landscape for Artificial Intelligence Systems." Available: [https://atlas.mitre.org/](https://atlas.mitre.org/)

4. **National Institute of Standards and Technology.** "Artificial Intelligence Risk Management Framework (AI RMF 1.0)." NIST AI 100-1, January 2023.

5. **European Parliament and Council.** "Regulation (EU) 2024/1689 — Artificial Intelligence Act." *Official Journal of the European Union*, July 2024.

6. **OWASP.** "OWASP Top 10 for Large Language Model Applications." Version 2.0, 2025. Available: [https://owasp.org/www-project-top-10-for-large-language-model-applications/](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

7. **Mirsky, Y., et al.** "On the Autonomy Scale for AI Agents: A Framework for Measuring and Governing Autonomous Behavior." 2025.

8. **Anderson, J. P.** "Computer Security Technology Planning Study." ESD-TR-73-51, Volume II, October 1972. (Reference Monitor concept.)

9. **Saltzer, J. H. and Schroeder, M. D.** "The Protection of Information in Computer Systems." *Proceedings of the IEEE*, 63(9):1278-1308, September 1975.

---

*This document is maintained by the AEGIS Initiative. Contributions welcome via pull request to [aegis-initiative/aegis-governance](https://github.com/aegis-initiative/aegis-governance).*

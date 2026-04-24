# AIAM-1: A Specification for Identity and Access Management for AI Agents (aIAM)

**Position Paper — v0.1**\
**AEGIS Initiative · AEGIS Operations LLC**\
**Author:** Ken Tannenbaum, Founder, AEGIS Initiative\
**ORCID:** 0009-0007-4215-1789

---

## Abstract

This position paper introduces AIAM-1, a specification for identity and access management for AI agents (aIAM), developed under the AEGIS Initiative. AIAM-1 addresses a gap that existing identity and access management frameworks were never designed to close: the governance of autonomous and semi-autonomous AI agents that plan, decide, and execute against production infrastructure. Traditional IAM assumes that actors are humans or scripted services — actors whose identity is durable, whose authorization is relatively static, and whose actions are discrete and reviewable. AI agents violate every one of these assumptions.

AIAM-1 introduces Intent-Bound Access Control (IBAC), an authorization model in which every access decision is evaluated as a function of identity, action, and intent context. IBAC is the first authorization model designed for the agent actor class, extending a lineage from DAC through MAC, RBAC, ABAC, and PBAC — each a response to a new actor class or deployment pattern that its predecessors could not govern. AIAM-1 defines the identity, intent, authority, capability, delegation, session, attestation, revocation, interoperability, and threat model primitives required to govern agentic systems as a distinct actor class. The full specification comprises 12 normative chapters, 90+ enumerated requirements, and 5 JSON schemas (common types, identity claim, intent claim, attestation record, delegation record).

This paper distills the specification for a position-paper audience. The normative text is the [AIAM-1 specification suite](https://github.com/aegis-initiative/aegis-governance/tree/main/aiam).

---

## 1. Background and Motivation

### 1.1 The Actor Class Gap

Identity and access management as a discipline was built for two actor classes: humans and service accounts. Humans are slow, deliberate, individually accountable, and operate within well-understood constraints of reaction time and cognitive load. Service accounts are narrow, scripted, and predictable — their behavior is bounded by the code that runs under them. Every significant IAM specification published in the last two decades — OAuth 2.0, OIDC, SAML, SCIM, XACML — was designed against these two actor classes, with their assumptions embedded in the core primitives.

AI agents are a third actor class. They are not humans, and they are not service accounts. They plan toward goals, compose actions dynamically, update their models based on intermediate results, and operate at machine speed. Their identity is durable but their intent is not. Their authorization cannot be static because their goals shift within a single session. Their actions are not discrete — they are composed chains of tool calls where each step conditions the next. Accountability cannot rest on the agent itself, because an agent is not a legal or moral entity.

Attempting to govern AI agents using existing IAM primitives results in a predictable failure mode: agents are either over-scoped (given broad credentials because narrow scoping would make them useless) or under-scoped (constrained to the point of being non-functional). Neither outcome is governance. Both are abdication.

### 1.2 Intent-Bound Access Control (IBAC)

Authorization models have evolved to match the complexity of the actors they govern:

| Model | Era | Decision Inputs | Core Question | Agent Suitability |
|---|---|---|---|---|
| **DAC** (Discretionary) | 1970s | Object owner grants | Who owns this? | Insufficient: agents do not own resources. |
| **MAC** (Mandatory) | 1970s | Security labels | What clearance do you have? | Insufficient: static clearance levels cannot govern dynamic actors. |
| **RBAC** (Role-Based) | 1990s | Identity + role membership | What role are you in? | Insufficient: agents shift goals within roles; roles are too coarse. |
| **ABAC** (Attribute-Based) | 2000s | Actor attributes + resource attributes + environment | What do you look like? | Partial: intent is not a first-class attribute. |
| **PBAC** (Purpose-Based) | 2005 | Identity + declared purpose | Why do you need this? | Partial: lacks principal chains, session governance, and structured intent validation. |
| **IBAC** (Intent-Bound) | 2026 | Identity + action + intent context | Why are you doing this, right now, in this context? | Designed for agents: intent is structured, validated, and attested. Generalizes all prior models. |

IBAC evaluates every access decision as a function of three inputs: identity, action, and intent context. It strictly generalizes prior models: an RBAC policy is an IBAC triple with wildcard intent. An ABAC policy is an IBAC triple with attributes mapped to identity and action patterns and wildcard intent. Organizations can adopt IBAC incrementally — starting with wildcard intent patterns and progressively adding intent constraints as they build confidence. PBAC (Byun et al., 2005) is the closest prior art, introducing purpose as a first-class access control input for privacy protection. IBAC extends PBAC with structured intent claims, principal chains, session governance, and intent validation against declared goal context.

### 1.3 The Case for IBAC in 30 Seconds

Consider an SOC triage agent with `telemetry.query` capability. It submits two action proposals for the same capability against the same target. Both are identical in identity and action. They differ only in intent.

**Action 1** — intent: "Retrieve flow records for host 10.0.5.42 to investigate DNS anomaly; no data modification."
**IBAC evaluation**: Intent aligns with declared goal context ("SOC triage for 10.0.0.0/8", scope includes "telemetry query"). Expected outcome consistent with constraints ("read-only"). **Decision: ALLOW.**

**Action 2** — intent: "Export complete flow archive for external analysis" with output parameter `email:attacker@evil.example.com`.
**IBAC evaluation**: Expected outcome ("export for external analysis") violates goal context constraint ("no external network access"). **Decision: DENY.**

Without intent as a first-class input, both actions are evaluated identically — and Action 2 is either allowed (if the capability grant is broad enough) or both are denied (if the grant is narrow enough to block Action 2, it also blocks Action 1). IBAC resolves this: two identical actions with different intents produce different authorization decisions.

### 1.4 The Cost of Governance

AIAM-1 governance is deliberately heavy. A single action traverses identity resolution, intent validation, capability check, IBAC policy evaluation, decision assembly, attestation production, and cryptographic signature. This overhead is the point — governance that is fast because it is shallow is the failure mode this specification is designed to prevent. Every stage exists because a documented production failure demonstrated what happens when that stage is absent. The performance cost is real. The cost of ungoverned agent actions is higher.

### 1.5 The Scope of aIAM

aIAM — identity and access management for AI agents — is the category of problem this specification addresses. It is a distinct specialization within the broader IAM discipline, related to but not derivable from existing human and service account IAM. AIAM-1 is the AEGIS Initiative's normative specification for aIAM, one possible realization of the category. Other specifications may emerge from other bodies; AIAM-1 is the first.

---

## 2. Scope and Applicability

### 2.1 In Scope

AIAM-1 v0.1 defines normative requirements for:

- Identity claims for AI agents, including composite identity structure and cryptographic attestation
- Intent claims as structured assertions of agent purpose at the moment of action
- Authority binding as a function of identity, action, and intent context (IBAC)
- Capability scoping, composition, and revocation
- Delegation and principal chain semantics for agent-to-agent and agent-to-sub-agent relationships
- Session semantics as first-class governance boundaries
- Attestation and audit records as primary accountability surfaces
- Revocation and kill-switch propagation with real-time guarantees (kill-switch: 60-second ceiling)
- Interoperability requirements with existing IAM standards (OAuth 2.1, OIDC, SAML, SCIM)
- Threat model and defensive posture (eight threat classes)

AIAM-1 v0.1 is scoped to single-organization deployments. Cross-organization delegation is deferred to v0.2.

### 2.2 Out of Scope

AIAM-1 v0.1 does not define:

- The internal architecture of AI models or agent orchestration frameworks
- Specific cryptographic algorithm choices beyond general requirements for attestation and signing
- Performance benchmarks or scalability targets for conformant implementations
- User interface or developer experience specifications
- Billing, metering, or commercial licensing mechanisms
- Model training or fine-tuning governance
- Trust scoring for agents or federation nodes
- Cross-organization delegation primitives

### 2.3 Normative Language

This specification uses the terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY as defined in RFC 2119. A conformant AIAM-1 implementation satisfies all MUST and MUST NOT requirements. SHOULD and SHOULD NOT requirements express strong recommendations whose violation must be justified and documented.

---

## 3. Normative Requirements

The full specification comprises 12 normative chapters. This section summarizes the key requirements from each. The normative text is the [AIAM-1 specification suite](https://github.com/aegis-initiative/aegis-governance/tree/main/aiam).

### 3.1 Identity

A conformant implementation MUST represent every AI agent identity as a composite of four dimensions: **model provenance** (what model?), **orchestration layer** (what framework?), **goal context** (what purpose?), and **principal** (whose accountability?). Each dimension is independently verifiable and independently revocable. Agent identity claims MUST be cryptographically signed. Any change to the orchestration harness (as determined by `harness_hash`) MUST trigger identity claim reissuance.

AIAM-1 uses "principal" to mean the human, organization, or legal entity accountable for the agent's actions — distinguished from "actor" (any entity submitting an action proposal) in other AEGIS specifications.

### 3.2 Intent

Every action MUST carry a structured intent claim: goal reference, reasoning summary, expected outcome, and dependency chain. Intent claims are validated against the goal context declared in the agent's identity — a mismatched goal reference results in denial. Intent claims are immutable after production, preserved in attestation records, and required for IBAC evaluation.

Intent claims are non-deterministic in origin but deterministic as input. The agent that produces the claim is probabilistic; the IBAC engine that evaluates it is not. This is how IBAC reconciles deterministic policy evaluation with intent claims produced by probabilistic agents.

### 3.3 Authority Binding (IBAC)

Authorization MUST be evaluated as a function of three inputs: identity, action, and intent context. Policies are expressed as (identity pattern, action pattern, intent context pattern) triples. Policy evaluation MUST use **first-match** semantics — first-match is normative because it is deterministic, auditable, and portable across engines. Default deny: any unmatched triple is denied. When multiple policies match with conflicting decisions, the more restrictive decision prevails (DENY > ESCALATE > REQUIRE_CONFIRMATION > ALLOW).

IBAC does not prevent malicious intent. It raises the cost of crafting viable spoofed claims, makes attempts visible in attestation records, and enables forensic reconstruction after the fact. Implementations should not describe IBAC as preventive — it is detective and cost-raising, with prevention as a byproduct.

### 3.4 Capability Scoping

Capabilities MUST be time-bounded, individually revocable, and non-transitive (authorization for A and B does not imply authorization for A-then-B). Capability composition MUST be treated as a governed operation — conformant implementations MUST evaluate composition over at least the current session.

### 3.5 Delegation and Principal Chains

Delegation MUST be represented as an explicit principal chain. Delegated authority narrows monotonically. The principal at the top remains accountable. Maximum delegation chain depth MUST be defined and published. Sub-agent instantiation is itself a governed action. When delegated and independent capabilities are combined, the mixed authority MUST be evaluated as a composed action.

Revocation of a delegating agent's authority MUST cascade to downstream delegated authority by default. Delegations MAY opt out of cascade via an explicit `cascade_on_revocation: false` flag, declared at delegation time, attested, justified, and subject to IBAC policy.

### 3.6 Session Semantics

Sessions are first-class governance boundaries bounded by four dimensions: goal context, time window, capability envelope, and accountability chain. Maximum session duration MUST be published and SHOULD NOT exceed 24 hours without compensating controls. Sessions MUST NOT be renewable — extension of authority requires a new session with a new attestation record. No silent session escalation is permitted.

### 3.7 Attestation and Audit

Every action MUST produce a tamper-evident, hash-chained, cryptographically signed attestation record. Records are append-only. Attestation failure triggers fail-closed denial — no unattested actions are permitted. Retention MUST NOT be less than 1 year except where legally required to be shorter. Attestation records are the primary accountability surface; agent-internal logging is not a substitute.

### 3.8 Revocation and Kill-Switch

Revocation MUST be pre-action, not eventually consistent. Kill-switch propagation latency MUST NOT exceed 60 seconds. Revoked capability grants MUST NOT be reinstated — operational continuity requires issuance of a new grant. Revocation operations are themselves governed actions.

### 3.9 Interoperability

**AIAM-1 adds to existing IAM; it does not subtract from it.** Agents authenticate via standard OAuth 2.1 / OIDC flows. AIAM-1 identity claims map into JWT tokens with `aiam_` prefixed extension claims. Existing identity providers do not need to natively understand AIAM-1. SCIM is supported for agent lifecycle management. When OAuth scopes and AIAM-1 capability grants conflict, the AIAM-1 capability registry is authoritative.

### 3.10 Threat Model

A conformant implementation MUST address eight threat classes:

- **Intent spoofing** — an agent produces a false intent claim masking malicious purpose. AIAM-1 defenses: goal alignment validation, behavioral consistency analysis, action-intent coherence, outcome verification. **Residual risk: HIGH.** A sufficiently sophisticated attacker can craft intent claims that pass all validation checks. Full mitigation requires verifiable execution traces — not yet feasible for LLMs. This is the most significant theoretical limitation of intent-based governance, and implementations must acknowledge it rather than claim IBAC prevents intent spoofing absolutely.
- **Capability composition attacks** — individually authorized capabilities composed into unauthorized effects. Residual risk: MEDIUM.
- **Authority inheritance exploitation** — sub-agents abusing delegated authority. Residual risk: MEDIUM.
- **Principal chain obscuration** — hiding accountability. Residual risk: LOW.
- **Attestation forgery** — fabricating governance records. Residual risk: LOW.
- **Revocation evasion** — racing against revocation propagation. Residual risk: LOW.
- **Governance visibility exploitation** — probing policy boundaries. Residual risk: MEDIUM.
- **Cross-authority composition** — combining delegated authority from principal A with independent authority from principal B to produce an effect neither authorized. Residual risk: MEDIUM.

---

## 4. Conformance

AIAM-1 v0.1 defines a single conformance profile (Full Conformance). Implementations MUST publish a conformance statement documenting requirement satisfaction and any deviations. v0.1 self-attested conformance is a known limitation — relying parties SHOULD treat self-attested claims as indicative, not authoritative. A normative test suite is committed for v0.2.

Future profiles planned for v0.2: **Research / Individual Profile** (lightweight, for single-user non-delegating deployments) and **Federation Profile** (for cross-organization agent governance).

---

## 5. Open Questions

1. **Intent claim verifiability.** How can a relying party verify that an intent claim corresponds to the agent's actual reasoning, given that the reasoning process is typically opaque? This is the fundamental open question for intent-based governance.

2. **Policy language standardization.** Rego is the directional recommendation for v0.1 implementers (native IBAC triple support without extension). Cedar requires schema extension for intent. XACML is not recommended. A normative binding is deferred to v0.2.

3. **Attestation storage scale.** High-frequency agentic systems may produce millions of attestation records per day. Storage architecture guidance is deferred to v0.2.

4. **Cross-domain federation.** The interaction between AIAM-1 identity claims and GFN-1 federation primitives requires explicit specification.

5. **Model-level attestation.** Attesting the model itself (weights, training provenance, fine-tuning state) is a deeper problem than attesting the runtime agent.

6. **Human-in-the-loop boundaries.** How human approval integrates with AIAM-1 identity and authority primitives.

7. **Cross-organization delegation.** When principal chains cross organizational boundaries, minimum requirements for bilateral trust (mutual attestation, capability agreements) require specification.

8. **Policy evaluation portability.** First-match is normative in v0.1. Most-specific-match is permitted as an opt-in extension with explicit strategy declaration. Whether additional evaluation strategies should be recognized is deferred to v0.2.

---

## 6. Relationship to Existing Standards

AIAM-1 is designed to be implemented independently of any specific governance runtime. Conformance does not require adoption of any other AEGIS specification. Cross-references to AEGIS artifacts are informative unless explicitly stated.

AIAM-1 complements, not replaces, existing IAM specifications:

- **OAuth 2.1 and OIDC** provide the transport and token format. AIAM-1 adds intent and authority primitives.
- **SCIM** provides lifecycle management. AIAM-1 extends SCIM schema for agent-specific attributes.
- **XACML and ABAC** provide policy evaluation patterns. IBAC extends the evaluation model with intent context.
- **PBAC** (Byun et al., 2005) provides the intellectual foundation. IBAC extends PBAC with structured intent claims, principal chains, session governance, and intent validation against declared goal context.
- **NIST AI RMF** provides the governance context. AIAM-1 implements identity and access management controls at the technical layer.
- **ATX-1** provides the threat taxonomy. The two specifications are designed to be used together but can be adopted independently.

---

## 7. Publication and Versioning

This document is v0.1 of the AIAM-1 position paper. The normative specification is the [AIAM-1 specification suite](https://github.com/aegis-initiative/aegis-governance/tree/main/aiam) (12 chapters, 3 JSON schemas). Both are published by the AEGIS Initiative under AEGIS Operations LLC and will be deposited to Zenodo with stable DOIs. Version 0.x releases are draft specifications; v1.0 will be the first stable release.

Comments, corrections, and contributions are welcomed. The canonical repository is maintained at [github.com/aegis-initiative](https://github.com/aegis-initiative).

---

## 8. Acknowledgments

AIAM-1 builds on the body of work developed under the AEGIS Initiative, including AGP-1, ATX-1, ATM-1, and GFN-1. It also draws on conversations with the broader AI governance community, including the NCCoE public comment process on agentic AI identity and authorization.

---

## Appendix A: Glossary

- **Agent:** An AI system capable of planning, deciding, and executing actions against production infrastructure, typically with some degree of autonomy.
- **aIAM:** Identity and access management for AI agents. A category of problem and practice.
- **AIAM-1:** The AEGIS Initiative's normative specification for aIAM, version 1.
- **Attestation record:** A cryptographically signed record of an action taken by an agent, including identity, intent, authority decision, capabilities, outcome, and principal chain.
- **Authority binding:** The association of an identity, action, and intent context with an authorization decision.
- **Capability:** A discrete ability granted to an agent, typically in the form of tool access, API access, or credential access.
- **Goal context:** A structured statement of the purpose for which an agent was instantiated.
- **IBAC (Intent-Bound Access Control):** The authorization model defined by AIAM-1 in which every access decision is evaluated as a function of identity, action, and intent context. Generalizes RBAC, ABAC, and PBAC.
- **Intent claim:** A structured assertion of the purpose of a specific action at the moment it is taken. Non-deterministic in origin (produced by a probabilistic agent), deterministic as input (evaluated by a deterministic policy engine).
- **Principal:** The human, organization, or legal entity on whose behalf an agent acts. The accountable party. Distinguished from "actor" (used in other AEGIS specifications to refer to any entity submitting an action proposal).
- **Principal chain:** The sequence of principals linking an action back to its originating accountable party through any intermediate agents.
- **Session:** A bounded governance context defined by goal, time window, capability envelope, and accountability chain. Not renewable — extension requires a new session.

---

## References

1. J.-W. Byun, E. Bertino, and N. Li, "Purpose Based Access Control of Complex Data for Privacy Protection," in *Proc. 10th ACM SACMAT*, 2005.
2. S. Bradner, "Key words for use in RFCs to Indicate Requirement Levels," RFC 2119, IETF, 1997.
3. N. Shapira et al., "Agents of Chaos," arXiv:2602.20021, 2026.
4. National Institute of Standards and Technology, "AI Risk Management Framework (AI RMF 1.0)," NIST AI 100-1, 2023.
5. AEGIS Initiative, "AIAM-1 Specification Suite," [github.com/aegis-initiative/aegis-governance/tree/main/aiam](https://github.com/aegis-initiative/aegis-governance/tree/main/aiam), 2026.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

---
title: "AEGIS AIAM-1 Specification Suite"
description: "AIAM-1 specification suite — identity and access management for AI agents"
---

# AEGIS AIAM-1 Specification Suite

**Document**: AIAM-1/Index (AEGIS_AIAM1_INDEX.md)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Overview

AIAM-1 (AEGIS Identity and Access Management, version 1) is a normative specification for identity and access management for AI agents (aIAM). It defines the identity, intent, authority, capability, delegation, session, attestation, revocation, interoperability, and threat model primitives required to govern autonomous and semi-autonomous AI agents as a distinct actor class.

AIAM-1 introduces **Intent-Bound Access Control (IBAC)**, an authorization model in which every access decision is evaluated as a function of three inputs: identity, action, and intent context. IBAC is the first authorization model designed specifically for the agent actor class, where intent shifts dynamically within a single operational session.

### 1.1 The Problem

Identity and access management was built for two actor classes: humans and service accounts. AI agents are a third actor class that violates the assumptions underlying both:

- Their identity is durable but their **intent** is not.
- Their authorization cannot be static because their **goals shift** within a single session.
- Their actions are not discrete — they are **composed chains** where each step conditions the next.
- **Accountability** cannot rest on the agent itself, because an agent is not a legal or moral entity.

Attempting to govern AI agents with existing IAM primitives results in agents that are either over-scoped (given broad credentials because narrow scoping would make them useless) or under-scoped (constrained to the point of being non-functional). Neither outcome is governance.

> **Scope caveat:** AIAM-1 v0.1 is scoped to single-organization deployments. Cross-organization delegation — where principal chains cross legal and trust boundaries — is identified as an open problem in the Delegation, Threat Model, and Revocation chapters and is deferred to v0.2.

### 1.2 What AIAM-1 Defines

| Primitive | Purpose | Specification Chapter |
|---|---|---|
| **Composite Identity** | Four-dimensional agent identity: model provenance, orchestration layer, goal context, principal | [IDENTITY](AEGIS_AIAM1_IDENTITY.md) |
| **Intent Claims** | Structured assertions of purpose at the moment of action | [INTENT](AEGIS_AIAM1_INTENT.md) |
| **Intent-Bound Access Control (IBAC)** | Authorization as a function of (identity, action, intent) | [AUTHORITY](AEGIS_AIAM1_AUTHORITY.md) |
| **Capability Scoping** | Time-bounded, non-transitive, composition-governed capabilities | [CAPABILITIES](AEGIS_AIAM1_CAPABILITIES.md) |
| **Delegation & Principal Chains** | Explicit accountability chains with monotonic authority narrowing | [DELEGATION](AEGIS_AIAM1_DELEGATION.md) |
| **Session Governance** | Sessions as first-class governance boundaries | [SESSIONS](AEGIS_AIAM1_SESSIONS.md) |
| **Attestation Records** | Action-level tamper-evident proof of governance decisions | [ATTESTATION](AEGIS_AIAM1_ATTESTATION.md) |
| **Revocation & Kill-Switch** | Pre-action revocation with propagation latency guarantees | [REVOCATION](AEGIS_AIAM1_REVOCATION.md) |
| **Interoperability** | Mappings to OAuth 2.1, OIDC, SCIM, SAML | [INTEROPERABILITY](AEGIS_AIAM1_INTEROPERABILITY.md) |
| **Threat Model** | Seven threat classes specific to agent IAM | [THREAT MODEL](AEGIS_AIAM1_THREAT_MODEL.md) |
| **Conformance** | Requirements checklist and conformance profiles | [CONFORMANCE](AEGIS_AIAM1_CONFORMANCE.md) |

### 1.3 Out of Scope

AIAM-1 v0.1 does not define:

- The internal architecture of AI models or agent orchestration frameworks
- Specific cryptographic algorithm choices beyond general requirements for attestation and signing
- Performance benchmarks or scalability targets for conformant implementations
- User interface or developer experience specifications
- Billing, metering, or commercial licensing mechanisms
- Model training or fine-tuning governance
- Trust scoring for agents or federation nodes (see GFN-1 and RFC-0004 for trust models within the AEGIS ecosystem)
- Cross-organization delegation primitives (deferred to v0.2)

---

## 2. Relationship to Other Standards

### 2.1 Standalone Design

AIAM-1 is designed to be implemented independently of any specific governance runtime. Conformance to AIAM-1 does not require adoption of any other AEGIS specification. Cross-references to AEGIS artifacts in this specification are **informative**, not normative, unless explicitly stated.

### 2.2 AEGIS Ecosystem Integration

When deployed within an AEGIS-governed environment, AIAM-1 integrates with:

| Specification | Integration Point | Relationship |
|---|---|---|
| **AGP-1** (Governance Protocol) | AIAM-1 composite identity is the backing record for AGP-1 `actor.id`. AIAM-1 intent claims extend AGP-1 ACTION_PROPOSE with structured purpose assertions. | AIAM-1 enriches AGP-1 identity and action semantics. |
| **ATX-1** (Threat Matrix) | AIAM-1 threat model (§3.10) cross-references ATX-1 tactics where applicable. ATX-1 TA007 (multi-agent collusion) and TA010 (semantic boundary violations) are directly relevant to AIAM-1 delegation and intent primitives. | Complementary threat coverage. |
| **ATM-1** (Threat Model) | AIAM-1 threat classes overlap with ATM-1 attack vectors (AV-3.1 identity spoofing, AV-7.1 composition attacks, RC-2 credential revocation). AEGIS architecture provides baseline mitigations; AIAM-1 requires conformant implementations to address threats independently. | Complementary defenses. |
| **GFN-1** (Federation Network) | GFN-1 DIDs identify federation nodes. AIAM-1 identity claims identify agents. These are structurally distinct — a federation node identity and an agent identity operate at different layers. AIAM-1 attestation records (action-level) complement GFN-1 attestations (node-level). | Complementary identity at different layers. |
| **RFC-0004** (Governance Event Model) | AIAM-1 §3.10.4 requires that trust evaluations comply with the structural separation of security and reputation signals. Within AEGIS, this is normatively specified in RFC-0004 §5 (two-layer trust model). | Architectural constraint. |

### 2.3 External Standards

| Standard | Relationship |
|---|---|
| **OAuth 2.1 / OIDC** | AIAM-1 identity claims map into OAuth 2.1 token formats. AIAM-1 adds intent and authority primitives that OAuth does not specify. |
| **SCIM** | AIAM-1 extends SCIM schema for agent lifecycle management (provisioning, updating, deprovisioning). |
| **XACML / ABAC** | IBAC extends the ABAC evaluation model with intent context as a first-class input. |
| **SAML** | AIAM-1 supports SAML assertions for federated agent identity in environments that have not adopted OAuth 2.1. |
| **NIST AI RMF** | AIAM-1 implements identity and access management controls required at the technical layer of an AI RMF program. |
| **PBAC** (Byun et al., 2005) | IBAC extends Purpose-Based Access Control with structured intent claims, principal chains, and session governance. |

---

## 3. Terminology

AIAM-1 introduces several terms that either extend or complement terminology used in other AEGIS specifications.

| Term | AIAM-1 Definition | Other AEGIS Usage |
|---|---|---|
| **Principal** | The human, organization, or legal entity on whose behalf an agent acts. The accountable party. | AGP-1/ATM-1 use **"actor"** for any entity submitting an action proposal (agent, human, or service). In AIAM-1, an agent is an actor; its principal is the entity accountable for the agent's actions. |
| **Intent claim** | A structured assertion of the purpose of a specific action at the moment the agent proposes it. | Not present in AGP-1. AGP-1 treats intent as implicit in ACTION_PROPOSE parameters. AIAM-1 intent claims extend, not replace, AGP-1 message structures. |
| **Session** | A bounded governance context defined by goal, time window, capability envelope, and accountability chain. | AGP-1/RFC-0002 use `session_id` as a stateless correlation key. AIAM-1 sessions are stateful governance boundaries. |
| **Attestation** | A cryptographically signed record of an action taken by an agent, including identity, intent, authority decision, capabilities, outcome, and principal chain. | GFN-1 uses `governance.attestation.v1` for node-level governance posture statements. AIAM-1 attestation is action-level. Both coexist as complementary records at different granularities. |
| **IBAC** | Intent-Bound Access Control. Authorization evaluated as a function of (identity, action, intent context). | Not present in other AEGIS specs. RFC-0003 uses role-based capability scoping, which is a special case of IBAC where intent context is wildcard. |
| **Composite identity** | Four-dimensional agent identity: model provenance, orchestration layer, goal context, principal. | AGP-1 uses `actor.id` (opaque string) and `actor.type` (enum: agent, user, service). AIAM-1 composite identity is the rich backing record that an AGP-1 `actor.id` resolves to. |

---

## 4. Authorization Model Landscape

Authorization models have evolved to match the complexity of the actors they govern. Each model was a response to a new actor class or deployment pattern:

| Model | Era | Decision Inputs | Core Question | Agent Suitability |
|---|---|---|---|---|
| **DAC** (Discretionary) | 1970s | Object owner grants | Who owns this? | Insufficient: agents do not own resources; ownership is not a meaningful governance dimension. |
| **MAC** (Mandatory) | 1970s | Security labels | What clearance do you have? | Insufficient: static clearance levels cannot govern dynamic, goal-shifting actors. |
| **RBAC** (Role-Based) | 1990s | Identity + role membership | What role are you in? | Insufficient: agents shift goals within roles; roles are too coarse for action-level governance. |
| **ABAC** (Attribute-Based) | 2000s | Actor attributes + resource attributes + environment | What do you look like? | Partial: attributes can encode some context, but intent is not a first-class attribute. |
| **PBAC** (Purpose-Based) | 2005 | Identity + declared purpose | Why do you need this? | Partial: captures purpose but lacks principal chains, session governance, and structured intent validation. |
| **IBAC** (Intent-Bound) | 2026 | Identity + action + intent context | Why are you doing this, right now, in this context? | Designed for agents: intent is structured, validated against goal context, and preserved in attestation records. Generalizes RBAC, ABAC, and PBAC. |

IBAC strictly generalizes prior models: an RBAC policy is an IBAC triple where the identity pattern matches on role, the action pattern is wildcard-scoped, and the intent context pattern is wildcard. An ABAC policy is an IBAC triple where attributes are mapped to identity and action patterns with wildcard intent. Organizations migrating from RBAC or ABAC can adopt IBAC incrementally by starting with wildcard intent patterns and progressively adding intent constraints as they mature.

---

## 5. Document Suite

### 5.1 Normative Documents

| Document | Status | Description |
|---|---|---|
| [AEGIS_AIAM1_INDEX.md](AEGIS_AIAM1_INDEX.md) | Draft | This document. Suite index and overview. |
| [AEGIS_AIAM1_IDENTITY.md](AEGIS_AIAM1_IDENTITY.md) | Draft | Composite identity model, cryptographic attestation, JSON schema. |
| [AEGIS_AIAM1_INTENT.md](AEGIS_AIAM1_INTENT.md) | Draft | Intent claims as structured assertions, validation, spoofing detection. |
| [AEGIS_AIAM1_AUTHORITY.md](AEGIS_AIAM1_AUTHORITY.md) | Draft | Intent-Bound Access Control (IBAC), authority binding triples, policy format. |
| [AEGIS_AIAM1_CAPABILITIES.md](AEGIS_AIAM1_CAPABILITIES.md) | Draft | Capability scoping, composition governance, non-transitivity, revocation. |
| [AEGIS_AIAM1_DELEGATION.md](AEGIS_AIAM1_DELEGATION.md) | Draft | Principal chains, monotonic authority narrowing, delegation depth limits. |
| [AEGIS_AIAM1_SESSIONS.md](AEGIS_AIAM1_SESSIONS.md) | Draft | Session as governance boundary, four-dimensional bounding. |
| [AEGIS_AIAM1_ATTESTATION.md](AEGIS_AIAM1_ATTESTATION.md) | Draft | Attestation records, tamper-evidence, retention. |
| [AEGIS_AIAM1_REVOCATION.md](AEGIS_AIAM1_REVOCATION.md) | Draft | Kill-switch, propagation latency, pre-action enforcement. |
| [AEGIS_AIAM1_INTEROPERABILITY.md](AEGIS_AIAM1_INTEROPERABILITY.md) | Draft | OAuth 2.1, OIDC, SCIM, SAML mappings. |
| [AEGIS_AIAM1_THREAT_MODEL.md](AEGIS_AIAM1_THREAT_MODEL.md) | Draft | Seven threat classes, ATX-1 cross-references, residual risk. |
| [AEGIS_AIAM1_CONFORMANCE.md](AEGIS_AIAM1_CONFORMANCE.md) | Draft | Conformance checklist, profiles, conformance statements. |

### 5.2 Schemas

> **Ownership note:** The AIAM schema set currently lives in
> `aegis-governance/aegis-core/schemas/aiam/` as a governance-owned extension.
> Shared cross-repository contracts for the broader AEGIS ecosystem are canonically
> owned by [`aegis/schemas/`](https://github.com/aegis-initiative/aegis/tree/main/schemas).
> AIAM schemas should be promoted into the canonical shared schema set only after the
> specification stabilizes enough for downstream product and SDK consumption.

| Schema | Location | Description |
|---|---|---|
| `common.schema.json` | `aegis-core/schemas/aiam/` | Shared type definitions: ID formats, timestamps, signatures, hashes. All other schemas `$ref` into this. |
| `identity_claim.schema.json` | `aegis-core/schemas/aiam/` | JSON Schema for AIAM-1 composite identity claims. |
| `intent_claim.schema.json` | `aegis-core/schemas/aiam/` | JSON Schema for AIAM-1 intent claims. |
| `attestation_record.schema.json` | `aegis-core/schemas/aiam/` | JSON Schema for AIAM-1 attestation records. |
| `delegation_record.schema.json` | `aegis-core/schemas/aiam/` | JSON Schema for AIAM-1 delegation records. |

### 5.3 Position Paper

| Document | Location | Description |
|---|---|---|
| [AIAM-1-position-paper-v0.1.md](../docs/position-papers/aiam/AIAM-1-position-paper-v0.1.md) | `docs/position-papers/aiam/` | Position paper establishing the normative scope of AIAM-1 v0.1. |

---

## 6. Normative Language

This specification uses the terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY as defined in RFC 2119. A conformant AIAM-1 implementation satisfies all MUST and MUST NOT requirements across all normative documents in this suite.

---

## 7. Version History

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-04-10 | Initial draft. Position paper and specification suite. |

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — Finnoybu IP LLC*

---
title: "AEGIS AIAM-1: Identity"
description: "AIAM-1 identity model — composite agent identity and principal chains"
---

# AEGIS AIAM-1: Identity

**Document**: AIAM-1/Identity (/identity/identity/)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

This chapter defines the identity model for AI agents governed under AIAM-1. It specifies how agent identity is represented, issued, verified, and managed throughout the agent lifecycle.

The central contribution is **composite identity** — a four-dimensional identity claim that captures not just *who* the agent is, but *what* it is built from, *where* it runs, *why* it was instantiated, and *on whose behalf* it acts. This structure reflects the reality that an AI agent's identity is not reducible to a single credential or account — it is a composite of model, infrastructure, purpose, and accountability.

---

## 2. Composite Identity Model

### 2.1 The Four Dimensions

An AIAM-1 identity claim is a composite of four independently verifiable dimensions:

```
┌─────────────────────────────────────────────────────────┐
│                  AIAM-1 Identity Claim                  │
├─────────────────┬───────────────────────────────────────┤
│ Model Provenance│ What model powers this agent?         │
│                 │ Family, version, artifact attestation  │
├─────────────────┼───────────────────────────────────────┤
│ Orchestration   │ Where does this agent run?            │
│ Layer           │ Runtime, framework, harness version    │
├─────────────────┼───────────────────────────────────────┤
│ Goal Context    │ Why was this agent instantiated?       │
│                 │ Purpose, scope, operational boundaries  │
├─────────────────┼───────────────────────────────────────┤
│ Principal       │ On whose behalf does this agent act?   │
│                 │ Accountable human, org, or legal entity │
└─────────────────┴───────────────────────────────────────┘
```

Each dimension serves a distinct governance function:

- **Model provenance** enables auditability of the reasoning engine. If a model is found to have a vulnerability or bias, all agents instantiated with that model can be identified and remediated.
- **Orchestration layer** enables auditability of the execution environment. A compromised orchestration framework affects all agents running under it, regardless of model.
- **Goal context** enables intent validation. An agent's actions can be evaluated against its declared purpose — actions inconsistent with the goal context are candidates for denial or escalation.
- **Principal** enables accountability. Every action, through every delegation chain, traces back to an accountable human, organization, or legal entity.

### 2.2 Why Four Dimensions?

Existing IAM models use one or two identity dimensions:

| Actor Class | Identity Dimensions | Sufficient? |
|---|---|---|
| Human | Credential (password, biometric, token) | Yes — humans are self-accountable. |
| Service account | Credential + service identifier | Yes — service behavior is deterministic. |
| AI agent | Credential alone | **No.** Two agents with identical credentials but different models, frameworks, or goals may behave in entirely different ways. |

A single credential proves authentication. It does not answer: *What reasoning engine produced this action? What execution environment is it running in? What is it trying to accomplish? Who is responsible if it causes harm?*

AIAM-1's four dimensions answer all four questions. Each is independently verifiable, independently revocable, and independently auditable.

---

## 3. Normative Requirements

### 3.1 Composite Identity Structure

**AIAM1-ID-001.** A conformant implementation MUST represent every AI agent identity as a composite of four dimensions: model provenance, orchestration layer, goal context, and principal.

**AIAM1-ID-002.** Each dimension MUST be independently verifiable by any relying party within the governance domain.

**AIAM1-ID-003.** Each dimension MUST be independently revocable without requiring revocation of the entire identity claim.

### 3.2 Model Provenance

**AIAM1-ID-010.** Model provenance MUST include, at minimum:

| Field | Description | Required |
|---|---|---|
| `model_family` | Model family identifier (e.g., `claude`, `gpt`, `llama`) | MUST |
| `model_version` | Specific version or checkpoint identifier | MUST |
| `model_attestation` | Cryptographic hash of the model artifact, or a signed attestation from the model provider | MUST |
| `provider` | Organization that produced or hosts the model | SHOULD |
| `fine_tuning_id` | Identifier for any fine-tuning applied on top of the base model | SHOULD (if applicable) |

**AIAM1-ID-011.** Model attestation MUST be verifiable without requiring access to the model weights themselves. A signed attestation from the model provider is acceptable when direct hash verification is not feasible (e.g., API-hosted models where the consumer does not have access to the model artifact).

**AIAM1-ID-012.** If the model is updated (new version, new fine-tuning), the identity claim MUST be reissued. A model provenance change constitutes a new identity, not an update to an existing one.

### 3.3 Orchestration Layer

**AIAM1-ID-020.** Orchestration layer identity MUST include, at minimum:

| Field | Description | Required |
|---|---|---|
| `runtime` | Runtime environment identifier (e.g., `python-3.13`, `node-22`) | MUST |
| `framework` | Agent framework identifier (e.g., `langchain-0.3`, `openclaw-2.1`, `claude-code-1.0`) | MUST |
| `framework_version` | Specific version of the agent framework | MUST |
| `harness_hash` | Cryptographic hash of the agent harness configuration (system prompts, tool definitions, memory configuration) | MUST |
| `deployment_id` | Unique identifier for this specific deployment instance | MUST (for replicated deployments); SHOULD (for single-instance) |

**AIAM1-ID-021.** Any change that alters `harness_hash` MUST trigger identity claim reissuance. The harness hash is the authoritative indicator of orchestration-layer identity — it captures system prompts, tool definitions, and memory configuration in a single verifiable artifact. A changed hash means a changed agent, regardless of whether the framework version or runtime changed.

**AIAM1-ID-022.** Each running instance of an agent MUST present a deployment-distinct identity context, even when sharing an underlying composite claim. In replicated deployments (multiple instances of the same agent configuration), `deployment_id` distinguishes instances for attestation, forensic investigation, and per-instance revocation.

### 3.4 Goal Context

**AIAM1-ID-030.** Goal context MUST include, at minimum:

| Field | Description | Required |
|---|---|---|
| `goal_id` | Unique identifier for this goal context | MUST |
| `purpose` | Structured statement of the purpose for which the agent was instantiated | MUST |
| `scope` | Operational boundaries: what the agent is authorized to work on | MUST |
| `constraints` | Explicit restrictions on agent behavior within this goal context | SHOULD |
| `expiry` | Time at which this goal context expires | SHOULD |

**AIAM1-ID-031.** Goal context MUST be sufficiently specific to distinguish one instantiation from another. A goal context of "general assistant" is not conformant. A goal context of "SOC triage analyst for network segment 10.0.0.0/8, authorized to query telemetry and escalate to human analysts" is conformant.

> **Conformance note:** Conformance assessment of goal context specificity is a subjective judgment. Third-party assessors SHOULD flag goal contexts whose `scope` field is under 20 characters or lacks resource/action qualifiers as candidates for rejection. The examples above illustrate the expected level of specificity; implementations SHOULD use them as calibration references.

**AIAM1-ID-032.** Goal context is the bridge between identity and intent. Intent claims (see [INTENT](/identity/intent/)) are validated against the goal context declared in the identity claim. An action whose intent does not align with the declared goal context is a candidate for denial.

### 3.5 Principal

**AIAM1-ID-040.** Principal MUST identify the human, organization, or legal entity on whose behalf the agent acts.

| Field | Description | Required |
|---|---|---|
| `principal_id` | Unique identifier for the principal | MUST |
| `principal_type` | One of: `individual`, `organization`, `legal_entity` | MUST |
| `principal_name` | Human-readable name | SHOULD |
| `contact` | Contact information for the accountable party | SHOULD |
| `jurisdiction` | Legal jurisdiction under which the principal operates | SHOULD |

**AIAM1-ID-041.** The principal is the accountable party for all actions taken by the agent under this identity claim. Accountability MUST NOT be delegated to the agent itself or to the model provider. If a principal cannot be identified, the agent MUST NOT be granted an identity claim.

**AIAM1-ID-042.** A single principal MAY be responsible for multiple agents. A single agent MAY act on behalf of multiple principals, but MUST hold separate identity claims for each principal, and each claim MUST be independently verifiable and independently revocable.

> **Operational note:** Separate identity claims per principal is a deliberate discipline. In practice, this will drive a one-instance-per-principal deployment pattern in most cases — it is simpler to deploy a dedicated agent instance per principal than to manage multiple identity claims within a single process. Implementations SHOULD expect this cost and plan deployment architecture accordingly.

### 3.6 Identity Claim Lifecycle

**AIAM1-ID-050.** Identity claims MUST be cryptographically signed by an issuing authority whose trust chain is verifiable by any relying party within the governance domain.

**AIAM1-ID-051.** Identity claims MUST have a defined validity period. Claims without an explicit expiration MUST NOT be accepted by conformant implementations.

**AIAM1-ID-052.** Identity claims MUST be revocable at any time by the issuing authority or by an authorized principal.

**AIAM1-ID-053.** Revocation of an identity claim MUST take effect within the revocation propagation latency guarantee defined by the implementation (see [REVOCATION](/identity/revocation/)).

**AIAM1-ID-054.** Identity claim issuance, renewal, and revocation events MUST produce attestation records (see [ATTESTATION](/identity/attestation/)).

---

## 4. Relationship to AGP-1 Actor Identity

AGP-1 represents actors using an opaque `actor.id` string (e.g., `agent:soc-01`) with an `actor.type` enum (`agent`, `user`, `service`) and an optional `actor.role` string. This representation is sufficient for governance decisions that do not require identity depth.

AIAM-1 composite identity is the **rich backing record** that an AGP-1 `actor.id` resolves to. The relationship is:

```
AGP-1 ACTION_PROPOSE
  actor:
    id: "agent:soc-01"        ← opaque reference
    type: "agent"
    role: "soc_analyst"

        │
        │ resolves to
        ▼

AIAM-1 Identity Claim
  model_provenance:
    model_family: "claude"
    model_version: "opus-4-6"
    model_attestation: "sha256:a1b2c3..."
    provider: "anthropic"
  orchestration:
    runtime: "python-3.13"
    framework: "aegis-core"
    framework_version: "0.2.0"
  goal_context:
    goal_id: "gc-soc-triage-2026Q2"
    purpose: "SOC triage for network segment 10.0.0.0/8"
    scope: "telemetry query, alert correlation, human escalation"
    constraints: "read-only data access, no remediation actions"
  principal:
    principal_id: "org:acme-security"
    principal_type: "organization"
    principal_name: "Acme Corp Security Operations"
```

AGP-1 implementations that adopt AIAM-1 resolve `actor.id` to the full composite identity claim for governance decisions that require identity depth (e.g., IBAC authority evaluation, delegation chain verification, attestation record construction). AGP-1 implementations that do not adopt AIAM-1 continue to treat `actor.id` as an opaque string with no loss of existing functionality.

---

## 5. Relationship to GFN-1 Node Identity

GFN-1 uses Decentralized Identifiers (DIDs) of the form `did:aegis:<network>:<node-id>` to identify federation nodes. These are **structurally distinct** from AIAM-1 identity claims:

| | GFN-1 Node Identity | AIAM-1 Agent Identity |
|---|---|---|
| **Identifies** | AEGIS federation node (governance infrastructure) | AI agent (governed entity) |
| **Format** | DID (`did:aegis:enterprise-001`) | Composite claim (four dimensions) |
| **Purpose** | Federation signal trust evaluation | Agent authorization and accountability |
| **Layer** | Governance infrastructure | Governed actor |

An AIAM-1 identity claim MAY include a reference to the GFN-1 node under which the agent is governed (as metadata in the orchestration layer dimension), but the two identity types MUST NOT be conflated. A federation node identity and an agent identity operate at different layers and serve different governance functions.

---

## 6. Worked Example: Single-Principal Single-Agent

### Scenario

Acme Corp deploys an AI agent for SOC (Security Operations Center) triage. The agent queries network telemetry, correlates alerts, and escalates findings to human analysts. It runs on the aegis-core framework, uses Claude Opus 4.6 as its reasoning engine, and operates under the authority of Acme Corp's security operations team.

### Identity Claim

```json
{
  "$schema": "https://aegis-initiative.com/schemas/aiam/identity_claim.schema.json",
  "claim_id": "idc-acme-soc-triage-20260410",
  "claim_version": "1.0",
  "issued_at": "2026-04-10T00:00:00Z",
  "expires_at": "2026-07-10T00:00:00Z",
  "issuer": "urn:aegis:issuer:acme-idp",
  "signature": "ed25519:...",

  "model_provenance": {
    "model_family": "claude",
    "model_version": "opus-4-6",
    "model_attestation": "sha256:7f3a8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a",
    "provider": "anthropic"
  },

  "orchestration": {
    "runtime": "python-3.13",
    "framework": "aegis-core",
    "framework_version": "0.2.0",
    "harness_hash": "sha256:1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
    "deployment_id": "deploy-acme-soc-prod-001"
  },

  "goal_context": {
    "goal_id": "gc-soc-triage-2026Q2",
    "purpose": "SOC triage analyst for network segment 10.0.0.0/8",
    "scope": "telemetry query, alert correlation, human escalation",
    "constraints": "read-only data access; no remediation actions; no external network access",
    "expiry": "2026-07-10T00:00:00Z"
  },

  "principal": {
    "principal_id": "org:acme-security-ops",
    "principal_type": "organization",
    "principal_name": "Acme Corp Security Operations",
    "contact": "soc-lead@acme.example.com",
    "jurisdiction": "US-VA"
  }
}
```

### What This Enables

With this identity claim in place:

1. **IBAC authority evaluation** can verify that the agent's actions align with its declared purpose ("SOC triage for 10.0.0.0/8") and deny actions outside that scope.
2. **Delegation chains** can trace accountability from any sub-agent back to Acme Corp Security Operations.
3. **Attestation records** for every action include the full composite identity, making forensic investigation possible months or years after the fact.
4. **Model recall**: if a vulnerability is discovered in Claude Opus 4.6, all agents with that model provenance can be identified and their identity claims revoked.
5. **Framework recall**: if a bug is found in aegis-core 0.2.0, all agents with that orchestration layer can be identified and remediated.

---

## 7. Security Considerations

### 7.1 Identity Claim Forgery

An attacker who can forge identity claims can impersonate any agent. Mitigations:

- Identity claims MUST be cryptographically signed (AIAM1-ID-050).
- Signing key management is the responsibility of the issuing authority.
- Implementations SHOULD support key rotation without requiring reissuance of all outstanding identity claims.

### 7.2 Stale Identity Claims

An agent whose model or framework has been updated but whose identity claim has not been reissued operates under a stale identity. Mitigations:

- Model provenance changes MUST trigger reissuance (AIAM1-ID-012).
- Any change that alters `harness_hash` MUST trigger identity claim reissuance (AIAM1-ID-021).
- Identity claims MUST have a defined validity period (AIAM1-ID-051).

### 7.3 Principal Accountability Evasion

An attacker who can create agents without a valid principal can take actions without accountability. Mitigations:

- Agents without an identifiable principal MUST NOT be granted identity claims (AIAM1-ID-041).
- Principal verification is the responsibility of the issuing authority.

---

## 8. Open Questions

1. **Model attestation for API-hosted models.** When the consumer does not have access to model weights (e.g., API-hosted services), model attestation depends on the provider's signed assertion. The trust chain for provider attestations requires further specification.

2. **Multi-model agents.** Some agents use multiple models (e.g., a planning model and an execution model). The composite identity model assumes a single model provenance dimension. Multi-model identity representation is deferred to v0.2.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

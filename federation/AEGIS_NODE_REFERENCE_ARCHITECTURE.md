# AEGIS Node Reference Architecture
**Version:** 0.1 (Draft)  
**Date:** 2026-03-04  

This document defines a **reference architecture** for an AEGIS node participating in the Governance Federation Network (GFN). It is implementation-agnostic and intended to guide interoperable designs.

---

## 1. Responsibilities

An AEGIS node SHOULD support:

1. **Governance signal publication**
2. **Governance feed subscription and ingestion**
3. **Local policy enforcement integration**
4. **Trust evaluation and weighting**
5. **Audit logging and evidence retention**
6. **Privacy controls and redaction**

---

## 2. High-Level Components

### 2.1 Governance Client (AT Protocol Adapter)
- Publishes AEGIS events via AT Protocol records
- Subscribes to governance feeds
- Handles identity keys and signing/verification

### 2.2 Policy Engine (Local)
- Evaluates inputs/outputs/actions against governance policies
- Enforces capability boundaries and required controls
- Produces local governance telemetry for publication (aggregated)

### 2.3 Risk Scoring Service
- Computes risk scores per request/session/action
- Consumes external risk signals (network feeds) to adjust scoring
- Produces risk telemetry for publication (aggregate + anonymized)

### 2.4 Trust & Reputation Evaluator
- Assigns weights to incoming events based on:
  - publisher reputation
  - policy authority status
  - audit/attestation level
  - historical accuracy
- Generates a local `trust_profile` used by policy/risk systems

### 2.5 Evidence Store (Restricted)
- Stores artifacts supporting attestations and incidents
- Provides signed URIs for authorized retrieval
- Enforces retention, access policies, and redaction

### 2.6 Observability & Audit
- Immutable logs of:
  - published events (hash + timestamp)
  - ingested events (hash + verification result)
  - policy/risk decisions
- Supports compliance and incident investigations

---

## 3. Data Flows

### 3.1 Outbound Flow (Publish)
1. Local detection (e.g., bypass attempt) is classified.
2. Sensitive content is **redacted** / **hashed**.
3. Event payload is constructed per canonical schema.
4. Envelope is canonicalized and signed.
5. Event is published to one or more feeds.

### 3.2 Inbound Flow (Subscribe + Apply)
1. Node subscribes to configured feeds.
2. Ingested events are verified:
   - signature verification
   - schema validation
   - freshness/replay checks
3. Trust evaluator assigns weight/reputation impact.
4. Risk engine and policy engine consume signals:
   - update risk priors
   - enable/disable mitigations
   - require additional controls (HITL, tool gating, etc.)
5. Audit logs capture decisions and sources.

---

## 4. Reference Interfaces

### 4.1 Event Publisher Interface
- `publishEvent(envelope: AegisEventEnvelope) -> PublishResult`

### 4.2 Feed Subscriber Interface
- `subscribe(feed: string) -> Stream<AegisEventEnvelope>`
- `ack(event_id: string)`

### 4.3 Policy Engine Interface
- `evaluate(request_context) -> Decision`
- `updatePolicies(policy_updates)`

### 4.4 Trust Evaluator Interface
- `scorePublisher(did) -> TrustScore`
- `weightEvent(event) -> WeightedEvent`

---

## 5. Deployment Topologies

### 5.1 Enterprise Private Node
- Connects only to restricted federation peers
- Publishes anonymized telemetry outward (optional)

### 5.2 Public Governance Node
- Publishes broadly to public feeds
- Often operated by research bodies or standards orgs

### 5.3 Policy Authority Node
- Publishes signed policy updates and profiles
- May provide audit attestations and schema registries

---

## 6. Security Requirements

AEGIS nodes MUST:
- store signing keys in hardened storage (HSM / KMS recommended)
- verify all inbound signatures and schemas
- implement replay protection (event_id + timestamp windows)
- enforce strict redaction rules for public events

AEGIS nodes SHOULD:
- support encrypted/restricted channels for sensitive sharing
- support multiple identity keys (rotation) with continuity proofs

---

## 7. Minimal Viable Node (MVN)

A minimal node for Phase 1 adoption includes:
- DID identity + signing
- publish: circumvention reports + risk signals
- subscribe: circumvention + risk feeds
- trust weighting (basic allowlist + reputation stub)
- audit log (hash chain recommended)

---

## 8. Operational Readiness Checklist (v0.1)

- [ ] DID provisioned and keys secured
- [ ] Event signing + verification tested
- [ ] Schema validation enabled
- [ ] Redaction/hashing policies configured
- [ ] Feed subscriptions configured
- [ ] Trust weighting configured (initial allowlist)
- [ ] Audit logs immutable and retained
- [ ] Incident disclosure workflow defined

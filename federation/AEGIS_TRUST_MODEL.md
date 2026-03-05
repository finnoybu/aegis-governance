# AEGIS Trust Model (Signal Weighting & Reputation)
**Version:** 0.1 (Draft)  
**Date:** 2026-03-04  

This document specifies how AEGIS nodes SHOULD evaluate the credibility of governance signals received via the Governance Federation Network (GFN).

The objective is to resist:
- malicious signal injection
- spam / low-quality reports
- coordinated misinformation
while still allowing decentralized participation.

---

## 1. Trust Primitives

### 1.1 Identity Verification
Signals MUST be signed by the publisher DID key. Nodes MUST verify:
- DID format (`did:aegis:*`)
- signature validity
- timestamp freshness window
- replay protection (event_id uniqueness)

### 1.2 Authority Classification
Nodes MAY classify publishers into:
- `policy_authority`
- `auditor`
- `enterprise_operator`
- `research_publisher`
- `unknown`

Classification SHOULD be local-policy driven.

---

## 2. Trust Score

Each publisher is assigned a `trust_score` in **[0,1]**.

Initial defaults (suggested):
- allowlisted authority: 0.85
- allowlisted enterprise: 0.70
- known research: 0.65
- unknown: 0.40

Scores evolve over time.

---

## 3. Evidence & Attestation

Trust SHOULD increase when a publisher provides:
- external audit attestations
- consistent policy posture disclosures
- high-quality incident follow-ups

Trust SHOULD decrease when:
- signals are frequently contradicted
- the publisher fails schema validation repeatedly
- the publisher spams low-confidence events

---

## 4. Event Weighting

Nodes compute an **event weight** based on:

- publisher trust score
- event type criticality
- confidence (if provided)
- corroboration (multiple independent publishers reporting same technique)
- freshness (recent events matter more)

### 4.1 Example Weight Formula (Non-Normative)

`weight = trust_score * confidence * freshness_factor * corroboration_factor`

Where:
- `freshness_factor` decays over time (e.g., half-life days)
- `corroboration_factor` increases with independent confirmations

---

## 5. Reputation Graph (Optional Extension)

Nodes MAY maintain a reputation graph capturing:
- trust relationships
- audit chains
- consortium memberships
- policy alignment

This enables richer evaluation such as:
- “trust this publisher for circumvention reports, but not for policy definitions”

---

## 6. Handling Malicious or Low-Quality Signals

Nodes SHOULD implement:

### 6.1 Rate Limits
Per-publisher event rate limiting (per feed/type).

### 6.2 Quarantine Queue
Low-trust publishers may be quarantined:
- signals ingested but not applied automatically
- require manual review or corroboration threshold

### 6.3 Shadow Bans (Local Policy)
Nodes MAY locally ignore publishers while still logging for audit.

---

## 7. Trust Bootstrapping

Nodes SHOULD support at least one bootstrapping mechanism:
- allowlist of known authority DIDs
- consortium membership proofs
- third-party auditor attestations

---

## 8. Applying Trust to Enforcement

Trust weighting SHOULD influence:
- risk model priors
- mitigation activation thresholds
- policy update adoption

Examples:
- high-trust circumvention report triggers immediate mitigation
- low-trust report requires corroboration

---

## 9. Audit Requirements

Nodes SHOULD audit:
- why an inbound signal was trusted or discounted
- what local enforcement changes occurred
- which events contributed to a given decision

Audit logs SHOULD store:
- event hashes
- verification status
- computed trust weight
- resulting action taken

---

## 10. Failure Modes and Safe Defaults

Safe defaults:
- never auto-apply policy updates from unknown publishers
- never ingest unsigned events
- never accept events failing schema validation
- never publish sensitive bypass instructions to public feeds

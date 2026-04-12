---
title: "AEGIS GFN-1 Governance Feed Taxonomy & Semantics"
description: "GFN-1 governance feeds — signal format and distribution"
---

# AEGIS GFN-1 Governance Feed Taxonomy & Semantics

**Document**: GFN-1/Feeds (AEGIS_GFN1_GOVERNANCE_FEEDS.md)\
**Version**: 1.0 (Normative)\
**Part of**: AEGIS Governance Federation Network\
**Last Updated**: March 6, 2026

---

This document defines the **canonical feed namespace** for the AEGIS Governance Federation Network (GFN), along with subscription guidance and intended semantics.

---

## 1. Goals

- Provide a stable, predictable feed hierarchy
- Enable selective subscription by risk domain
- Support public vs restricted distribution patterns
- Reduce ambiguity in event routing and consumption

---

## 2. Naming Conventions

Feeds use dot-separated namespaces:

`<domain>.<category>[.<subcat>].<stream>`

Examples:

- `governance.circumvention.public`
- `governance.risk.enterprise`
- `governance.policy.authority`
- `governance.incident.restricted`

---

## 3. Canonical Feeds (v0.1)

### 3.1 Circumvention Feeds

- `governance.circumvention.public`
  - For broad ecosystem awareness
  - MUST NOT contain step-by-step exploit instructions
  - SHOULD use hashed indicators and abstract patterns

- `governance.circumvention.restricted`
  - For trusted circles (ISAC-like groups)
  - MAY include richer forensic context under access controls

### 3.2 Risk Feeds

- `governance.risk.public`
  - Aggregated telemetry intended for broad consumption

- `governance.risk.enterprise`
  - Private/partner risk telemetry for consortium members

### 3.3 Policy Feeds

- `governance.policy.authority`
  - Signed policy profiles from policy authority nodes

- `governance.policy.enterprise`
  - Enterprise policy deltas intended for internal or partner nodes

### 3.4 Attestation Feeds

- `governance.attestation.public`
  - Public governance posture statements (limited metadata)

- `governance.attestation.restricted`
  - Richer attestations with evidence links (access-controlled)

### 3.5 Incident Feeds

- `governance.incident.public`
  - Minimal incident disclosures for ecosystem learning

- `governance.incident.restricted`
  - Partner disclosures with controlled detail level

---

## 4. Subscription Profiles

### 4.1 Baseline Profile (Recommended Default)

Subscribe to:

- `governance.circumvention.public`
- `governance.risk.public`
- `governance.policy.authority`
- `governance.attestation.public`

### 4.2 Enterprise Consortium Profile

Subscribe to baseline plus:

- `governance.circumvention.restricted`
- `governance.risk.enterprise`
- `governance.attestation.restricted`
- `governance.incident.restricted`

### 4.3 Research / Analysis Profile

Subscribe to:

- `governance.circumvention.public`
- `governance.risk.public`
- `governance.incident.public`
- `governance.policy.authority`

---

## 5. Routing Guidance

Publishers SHOULD:

- default to the least-sensitive feed that still provides utility
- prefer `public` feeds for abstract patterns and aggregated telemetry
- use `restricted` feeds for privileged operational detail

Consumers SHOULD:

- apply trust weighting differently per feed class
- treat `restricted` feeds as higher value but not automatically trustworthy
- enforce schema validation and signature verification uniformly

---

## 6. Future Extensions (Non-Normative)

Potential future feed families:

- `governance.control_updates.*` (machine-consumable mitigation updates)
- `governance.schema.*` (schema registry events)
- `governance.reputation.*` (reputation graph updates)
- `governance.marketplace.*` (policy/audit service discovery)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../aegis-core/assets/AEGIS_wordmark_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../aegis-core/assets/AEGIS_wordmark_light.svg">
    <img src="../aegis-core/assets/AEGIS_wordmark.svg" width="90" alt="AEGIS™ Governance Logo">
  </picture>
</p>

# AEGIS™ Governance Federation Network

**Document Pack Status**: Normative  
**Version**: 1.1  
**Last Updated**: March 15, 2026

---

## Overview

The AEGIS Governance Federation Network (GFN) enables distributed governance intelligence sharing across organizational and network boundaries.

Individual AEGIS governance runtimes operate autonomously within their trust domains. The federation layer enables trusted nodes to:

- **Share governance signals** – policy updates, risk alerts, circumvention reports, attestations
- **Improve collective security** – distributed threat detection and response coordination
- **Maintain operational autonomy** – federated nodes make independent approval decisions
- **Ensure auditability** – immutable event logs with cryptographic verification[^1]

### Federation Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Governance Intelligence                  │
│                  (policies, risk signals, etc)              │
└──────────────┬──────────────────────────────────┬───────────┘
               │                                  │
        ┌──────▼──────┐                   ┌──────▼──────┐
        │   Node A    │◄─────────────────►│   Node B    │
        │ (Org 1)     │   Federation      │ (Org 2)     │
        │ AEGIS       │   Protocol        │ AEGIS       │
        │ Runtime     │                   │ Runtime     │
        └─────┬───────┘                   └──────┬──────┘
              │                                  │
        ┌─────▼────────────┐            ┌───────▼──────┐
        │ Local Governance │            │ Local Gov    │
        │ Decisions        │            │ Decisions    │
        └──────────────────┘            └──────────────┘
```

---

## Document Pack Contents

This folder contains the normative documentation for AEGIS federation:

| Document | Status | Purpose |
|----------|--------|---------|
| [AEGIS_GFN1_GOVERNANCE_NETWORK.md](./AEGIS_GFN1_GOVERNANCE_NETWORK.md) | Normative | Federation protocol specification; decentralized pub-sub topology |
| [AEGIS_GFN1_SCHEMA.md](./AEGIS_GFN1_SCHEMA.md) | Normative | ATProto-based schema definitions for governance events |
| [AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md](./AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md) | Normative | Node deployment, service mesh, federation endpoints architecture |
| [AEGIS_GFN1_GOVERNANCE_FEEDS.md](./AEGIS_GFN1_GOVERNANCE_FEEDS.md) | Normative | Feed types, subscription, replay, and versioning semantics |
| [AEGIS_GFN1_TRUST_MODEL.md](./AEGIS_GFN1_TRUST_MODEL.md) | Normative | Trust evaluation, identity binding, signature verification, and DID resolution |

---

## Quick Federation Concepts

### Governance Signals

Nodes share immutable governance intelligence:

- **Policy Updates** – versioned policy changes with effective dates
- **Circumvention Reports** – detected bypasses, techniques, and affected capabilities
- **Risk Signals** – behavioral anomalies, rising threat trends, confidence scores
- **Governance Attestations** – compliance audits, policy set confirmations, audit window results
- **Incident Notices** – breach notifications, containment status, public IOC references

### Node Identity (DIDs)

All federation participants are identified by Decentralized Identifiers (DIDs)[^20][^27]:

```
did:aegis:enterprise-001
did:aegis:soc-team-alpha
```

DIDs include cryptographic keys for:

- message signing and verification
- trust anchor binding
- key rotation and lifecycle

### Trust Evaluation[^17]

AEGIS federation trust operates through two structurally separate mechanisms that must never be combined into a single score.

**Publisher Trust Score** — governs how much weight to assign to governance signals received from a remote node. Computed as a weighted composite of five factors: Baseline identity class (B), Historical accuracy (H), Signal quality (Q), Audit posture (A), and Federation reputation (F). The normative formula and factor definitions are specified in GFN-1 §3.7. Scores decay during publisher inactivity (GFN-1 §3.8); security revocation triggers (GFN-1 §8) are evidence-based, fire immediately, and are structurally independent of this decay.

**Application thresholds** (see GFN-1 §3.9 for normative definition):

| Score | Disposition |
|---|---|
| ≥ 0.80 | Auto-ingest signal |
| [0.50, 0.80) | Ingest; corroboration required for risk changes |
| [0.25, 0.50) | Quarantine; manual review required |
| < 0.25 | Reject; log for audit |

When a publisher's authority class (GFN-1 §2.2) and computed trust score produce conflicting dispositions, the more restrictive disposition applies. See GFN-1 §10.1.1.

**Agent Runtime Trust** — governs agent admissibility at the execution boundary. This is a separate concern from publisher trust and is defined in RFC-0004 §5. It operates through a Threat Detection Layer (Engine layer — evidence-based, binary, immediate) and a Reputation Layer (Schema layer — longitudinal, advisory). No reputation score overrides a threat detection block under any condition.

### Event Ordering and Replay Protection

All events carry monotonic sequences per stream:

```
Policy Update Event (seq=1042, policy_feed)
  → Risk Signal Event (seq=1043, risk_feed)
  → Governance Attestation (seq=1044, attestation_feed)
```

Consumers detect gaps and request backfill. Signature-based replay protection prevents:

- stale event replay
- out-of-order injection
- timestamp manipulation

---

## Reading Order Recommendations

### Path 1: Federation Architecture (Non-Technical Stakeholders)

1. This README (overview and concepts)
2. AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md – deployment topology and operational requirements
3. AEGIS_GFN1_TRUST_MODEL.md – trust evaluation and audit properties

**Time**: ~30 minutes  
**Outcome**: Understanding federation architecture, trust model, and operational implications

### Path 2: Protocol Implementation (Protocol Engineers)

1. This README (overview and concepts)
2. AEGIS_GFN1_GOVERNANCE_NETWORK.md – protocol semantics and message exchange
3. AEGIS_GFN1_GOVERNANCE_FEEDS.md – feed mechanics, subscription, versioning
4. AEGIS_GFN1_SCHEMA.md – detailed event schemas (reference)

**Time**: ~90 minutes  
**Outcome**: Ability to implement federation endpoints and event handling

### Path 3: Deploy and Operate (Operations Engineers)

1. This README (overview)
2. AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md – deployment models, networking, secrets
3. AEGIS_GFN1_TRUST_MODEL.md – identity setup, key rotation, trust configuration
4. AEGIS_GFN1_GOVERNANCE_NETWORK.md – federation endpoints, load balancing

**Time**: ~60 minutes  
**Outcome**: Ability to deploy and configure a federation node

### Path 4: Threat Analysis (Security Teams)

1. This README (concepts)
2. AEGIS_GFN1_TRUST_MODEL.md – identity threats, signature verification, DID spoofing
3. AEGIS_GFN1_GOVERNANCE_NETWORK.md – protocol attack surface
4. AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md – isolation and containment

**Time**: ~45 minutes  
**Outcome**: Understanding federation security model and threat landscape

---

## Key Federation Principles

### 1. Operational Autonomy

Each AEGIS node operates independently:

- makes its own capability, policy, and risk decisions
- never delegates authority to federated peers
- retains full override and shutdown capability
- audit trail is local and tamper-proof

Federation signals are **advisory intelligence**, never **directive commands**.

### 2. Asymmetric Trust

Nodes may publish to federation without subscribing to peers.
Trust relationships are **directional** and **multi-weighted**.

Example:

- Node A trusts Node B's risk signals (high confidence)
- Node A trusts Node C's policy guidance (medium confidence)
- Node A does not trust Node D's circumvention reports (unverified)

### 3. Event Immutability

All federation events are:

- cryptographically signed by publisher
- timestamped and sequenced
- persisted in append-only logs
- never amended or deleted (only superseded by newer events)

### 4. Deterministic Validation

Event acceptance is deterministic:

- same event + same receiver policy = same outcome
- no hidden state or timing-dependent decisions
- all trust factors are auditable

---

## Summary

The AEGIS Governance Federation Network extends single-node governance with:

✅ **Distributed Intelligence Sharing** – cryptographically signed governance signals across trust boundaries  
✅ **Autonomous Decision Making** – federated nodes retain full authority over their own governance  
✅ **Provable Trust** – multi-factor trust scoring with auditable evidence  
✅ **Replay Protection** – immutable, sequenced events with signature verification  
✅ **Operational Independence** – graceful fallback to local governance if federation unavailable  

The federation model is especially valuable for:

- **Security Operations Centers** – share attack indicators and policy learnings across organizations
- **Enterprise AI Governance** – coordinate policy updates and risk assessments across business units
- **Critical Infrastructure** – establish mutual aid governance signals in coalition operations
- **Regulated Environments** – demonstrate inter-organizational governance coordination for compliance

---

## Document References

For detailed specifications, see:

- **Architecture & Security**: See [../docs/architecture](../docs/architecture) and [../rfc](../rfc)
- **Runtime API**: See [AGP-1 Protocol](../aegis-core/protocol/AEGIS_Governance_Protocol_AGP1.md)
- **Threat Model**: See [../docs/architecture/THREAT_BOUNDARIES.md](../docs/architecture/THREAT_BOUNDARIES.md)

---

**Status**: Normative
**Next Review**: June 5, 2026
**Maintained By**: AEGIS Governance Project

---

## References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../REFERENCES.md).

[^17]: National Institute of Standards and Technology, *Zero Trust Architecture*, NIST SP 800-207, Aug. 2020. [Online]. Available: <https://doi.org/10.6028/NIST.SP.800-207>. See [REFERENCES.md](../REFERENCES.md).

[^20]: M. Sporny, A. Guy, M. Sabadello, and D. Reed, "Decentralized Identifiers (DIDs) v1.0: Core architecture, data model, and representations," W3C Recommendation, 19 Jul. 2022. [Online]. Available: <https://www.w3.org/TR/2022/REC-did-core-20220719/>. See [REFERENCES.md](../REFERENCES.md).

[^27]: H. Shuhan et al., "Decentralised identity federations using blockchain," *Int. J. Inf. Secur.*, 2024, doi: 10.1007/s10207-024-00864-6. [Online preprint]. Available: <https://arxiv.org/pdf/2305.00315>. See [REFERENCES.md](../REFERENCES.md).

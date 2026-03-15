# RFC-0004: AEGIS™ Governance Event Model

**RFC:** RFC-0004
**Status:** Draft  
**Version:** 0.3
**Created:** 2026-03-05
**Updated:** 2026-03-15
**Author:** AEGIS™ Initiative, Finnoybu IP LLC  
**Repository:** aegis-governance  
**Target milestone:** v1.0  
**Supersedes:** None  
**Superseded by:** None  

---

## Summary

This RFC defines the canonical event envelope, payload schemas, versioning strategy, ordering guarantees, replay protection, and trust evaluation model for AEGIS™ governance federation events. It is the basis for interoperability between AEGIS governance nodes.

---

## Motivation

A single AEGIS runtime governs one deployment. When multiple deployments need to share governance intelligence — policy updates, circumvention reports, risk signals, attestations — they need a common event format that can be verified, ordered, and trusted. Without this, federation is informal and ungovernable.

---

## Guide-Level Explanation

Think of the governance event model as a signed, tamper-evident message format that AEGIS nodes use to talk to each other. When one node discovers a new threat pattern, it can publish a circumvention report. When another node updates its policies, it publishes a policy update event. Receiving nodes verify the signature, check the sequence, evaluate the publisher's trust score, and decide whether to act on the event automatically or queue it for operator review.

---

## Reference-Level Explanation

### 1. Event Envelope

All events MUST use this envelope:

```json
{
  "event_id": "evt-20260305-0001",
  "event_seq": 1042,
  "event_stream": "governance.policy_updates",
  "timestamp": "2026-03-05T12:00:00Z",
  "publisher_did": "did:aegis:enterprise-001",
  "event_type": "policy_update",
  "schema_version": "1.2.0",
  "payload_hash": "sha256:...",
  "payload": {},
  "signature": {
    "alg": "ed25519",
    "key_id": "did:aegis:enterprise-001#key-1",
    "sig": "base64url"
  }
}
```

### 2. Event Types

**policy_update** — Required fields: `policy_id`, `policy_set_version`, `change_type` (add|update|deprecate|revoke), `effective_at`, `summary`, `policy_diff`

**circumvention_report** — Required fields: `technique_id`, `category`, `severity`, `description`, `affected_capabilities`, `recommended_mitigations`

**risk_signal** — Required fields: `risk_category`, `severity`, `confidence` (0.0-1.0), `trend` (rising|stable|falling), `evidence_refs`

**governance_attestation** — Required fields: `node_id`, `aegis_version`, `policy_set_hash`, `audit_window_start`, `audit_window_end`, `attestation_result` (pass|fail|partial)

**incident_notice** — Required fields: `incident_id`, `category`, `severity`, `detected_at`, `affected_systems`, `containment_status`, `public_ioc_refs` (optional)

### 3. Versioning Strategy

Version format: `MAJOR.MINOR.PATCH`

- PATCH: backward-compatible clarifications only
- MINOR: additive fields allowed; consumers must ignore unknown fields
- MAJOR: breaking schema change; requires explicit migration

### 4. Ordering and Replay Protection

Ordering is guaranteed per `event_stream` by monotonic `event_seq`. Consumers detect gaps and request backfill.

Consumers MUST enforce:
- Unique `(publisher_did, event_id)`
- Monotonic sequence checks per stream
- Timestamp skew window (default +/- 5 minutes)
- Signature verification with key validity period

### 5. Trust Evaluation Model[^17]

Trust score range: 0.0 to 1.0. The normative formula is defined in GFN-1 §3.7:

```text
T = 0.30B + 0.25H + 0.20Q + 0.15A + 0.10F
```

Where:

- **B** — Baseline Trust Factor (identity class and credential strength)
- **H** — Historical Accuracy Factor (fraction of signals not subsequently contradicted)
- **Q** — Consistency and Quality Factor (signal completeness and confidence calibration)
- **A** — Audit Posture Factor (operational governance maturity)
- **F** — Federation Reputation Factor (peer node endorsements)

`T` is clamped to [0.0, 1.0]. Bootstrap values for nodes with no operational history are specified in GFN-1 §3.2–§3.6.

Application policy:
- `>= 0.8`: allow automated policy ingestion
- `0.5 to 0.8`: require operator confirmation
- `< 0.5`: quarantine event

### 6. Delivery Guarantees

Supported patterns: pull feeds, push subscriptions, replicated append-only logs. Delivery semantics: at-least-once; idempotent consumer processing required.

---

## Drawbacks

- The trust scoring model requires operational history. New nodes start with bootstrap values defined in GFN-1 §5 and converge to earned scores over time.
- ed25519 signature verification adds per-event overhead. High-volume event streams require careful performance management.
- At-least-once delivery requires all consumers to implement idempotency, adding implementation burden.

---

## Alternatives Considered

**Unsigned events:** Simpler but provides no guarantee of publisher identity or payload integrity. Insufficient for governance intelligence sharing where a compromised publisher could poison policy state.

**Synchronous policy replication:** Eliminates eventual consistency but creates tight coupling between nodes and a single point of failure for policy updates.

**Centralized governance event broker:** Simplifies consumer implementation but introduces a single trusted intermediary, which conflicts with the federation model's goal of distributed governance.

---

## Compatibility

Downstream of [RFC-0001](./RFC-0001-AEGIS-Architecture.md) through RFC-0003. The event model enables federation between compliant AEGIS runtimes but does not modify the local governance cycle defined in RFC-0001 and RFC-0002.

---

## Implementation Notes

Complete payload examples for all five event types are in the canonical repository at `schemas/examples/governance/events/`. Implementers should validate against those examples before publishing events to a federation network.

Trust bootstrap for new nodes is handled by the mechanisms defined in GFN-1 §5. See that section for allowlist, consortium membership, transitive endorsement, and accelerated onboarding approaches.

---

## Open Questions

- [ ] Should trust scores be published as governance attestation events, creating a recursive trust signal loop?
- [ ] Should the event model define a standard backfill request protocol?
- [ ] How should trust scoring handle nodes that have never published circumvention reports — absence of reports vs. no reports yet?

---

## Success Criteria

- Any two compliant AEGIS nodes can exchange all five event types without schema negotiation
- A replay attack is detected and rejected in all scenarios defined in Section 4
- Trust score calculation is reproducible given the same input signals and evaluation timestamp $t$. Implementations must treat $t$ as an explicit logged parameter. See GFN-1 §3.8 for the normative specification.

---

## References

[^17]: National Institute of Standards and Technology, *Zero Trust Architecture*, NIST SP 800-207, Aug. 2020. [Online]. Available: <https://doi.org/10.6028/NIST.SP.800-207>. See [REFERENCES.md](../REFERENCES.md).

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*  
*AEGIS Initiative — Finnoybu IP LLC*

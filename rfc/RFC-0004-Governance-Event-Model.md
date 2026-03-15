# RFC-0004: AEGIS™ Governance Event Model

**RFC:** RFC-0004  
**Status:** Draft  
**Version:** 0.4  
**Created:** 2026-03-05  
**Updated:** 2026-03-15  
**Author:** AEGIS™ Initiative, Finnoybu IP LLC  
**Repository:** aegis-governance  
**Target milestone:** v1.0  
**Supersedes:** None  
**Superseded by:** None  

---

## Summary

This RFC defines the canonical event envelope, payload schemas, versioning strategy, ordering guarantees, replay protection, and runtime trust model for AEGIS™ governance federation events. It is the basis for interoperability between AEGIS governance nodes.

---

## Motivation

A single AEGIS runtime governs one deployment. When multiple deployments need to share governance intelligence — policy updates, circumvention reports, risk signals, attestations — they need a common event format that can be verified, ordered, and trusted. Without this, federation is informal and ungovernable.

Federation trust operates at two distinct levels that must not be conflated: publisher trust (how much weight to give a governance signal from a remote node) and agent runtime trust (how to evaluate an agent's admissibility at execution time). This RFC governs both, and defines them as structurally separate mechanisms with different timescales, different enforcement properties, and an explicit non-override constraint between them.

---

## Guide-Level Explanation

Think of the governance event model as a signed, tamper-evident message format that AEGIS nodes use to talk to each other. When one node discovers a new threat pattern, it can publish a circumvention report. When another node updates its policies, it publishes a policy update event. Receiving nodes verify the signature, check the sequence, evaluate the publisher's trust score, and decide whether to act on the event automatically or queue it for operator review.

At the agent execution boundary, a separate and structurally isolated trust model applies. An agent's admissibility is evaluated by two independent mechanisms: a threat detection layer that operates on evidence and fires immediately, and a reputation layer that tracks operational reliability over time. These mechanisms are never combined into a single score. A detected threat blocks execution regardless of an agent's operational history. Reputation informs autonomy expansion; it does not influence security gates.

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

### 5. Runtime Trust Model[^17]

AEGIS runtime trust operates through two structurally separate mechanisms. These mechanisms MUST NOT share a score, a decay function, or a combined threshold. They are defined independently and governed by an explicit non-override constraint.

#### 5.1 Architectural Principle

> Security and reputation are different kinds of signals that operate on different timescales and carry different override properties. Collapsing them into a single score creates a category error: accumulated reputation can implicitly soften a security gate. This is architecturally unsound. The two mechanisms are defined separately and the non-override constraint between them is normative.

#### 5.2 Threat Detection Layer

**AEGIS layer:** Engine (Layer 3 — Runtime Enforcement)  
**Timescale:** Immediate (event-driven)  
**Decision type:** Binary — block or pass  
**Score:** None. This layer does not produce a score.

The Threat Detection Layer evaluates agent behavior against evidence of active threat. When a threat is detected, the agent is blocked at the execution boundary. No prior operational history, reputation score, or accumulated trust modifies this outcome.

Implementations MUST enforce:

- Threat detection fires on evidence, not on time-based decay
- A block from the Threat Detection Layer CANNOT be overridden by the Reputation Layer under any condition
- Threat detection decisions are logged as immutable audit events at the Engine layer
- The Threat Detection Layer has no dependency on and no visibility into the Reputation Layer's state

**Trigger classes (normative):**

| Trigger | Response | Reversible? |
|---|---|---|
| Active policy violation detected | Block immediately | Yes, upon remediation |
| Anomalous execution pattern (pattern match) | Block and escalate | Yes, upon operator review |
| Cryptographic identity verification failure | Block immediately | No — identity must be re-registered |
| Unregistered agent at execution boundary | Block immediately | Yes, upon registration |
| Escalation protocol breach | Block and notify | Yes, upon operator review |

#### 5.3 Reputation Layer

**AEGIS layer:** Schema (Layer 2 — Policy Definitions and Risk Classifications)  
**Timescale:** Longitudinal (accumulated over operational history)  
**Decision type:** Graduated — informs autonomy expansion, approval latency, and capability range  
**Score:** Operational reliability score, range [0.0, 1.0]

The Reputation Layer tracks an agent's operational reliability over time. Consistent performance earns higher autonomy, faster approvals, and expanded operational range. The Reputation Layer is a governed attribute: it is policy-readable and informs Schema-layer decisions.

Implementations MUST enforce:

- Reputation score is computed and stored at the Schema layer
- Reputation score has no path to influence an Engine-layer threat block
- Reputation expansion decisions are logged with the score value and evaluation timestamp as explicit parameters
- Reputation score decays during inactivity periods; the decay function applies only to the reputation score and has no effect on Threat Detection Layer state. **The normative decay function for agent reputation is deferred to a future RFC.** The exponential decay model defined in GFN-1 §3.8 (`T_decayed = T × e^(-λt)`, λ=0.01) is the candidate reference; implementations MAY adopt it pending that RFC, but MUST treat it as implementation-defined until normatively specified.

**Reputation thresholds (normative):**

| Score | Interpretation | Effect |
|---|---|---|
| >= 0.80 | Established operational record | Expanded autonomy; reduced approval latency |
| [0.50, 0.80) | Developing operational record | Standard autonomy; normal approval process |
| [0.25, 0.50) | Limited operational record | Restricted autonomy; corroboration required |
| < 0.25 | Insufficient operational record | Minimal autonomy; operator review required |

#### 5.4 Non-Override Constraint (Normative)

The following constraint is normative and MUST be enforced structurally, not procedurally:

> **No Reputation Layer score, at any value, grants a pass on a Threat Detection Layer block.**

This constraint is satisfied when:

1. The Threat Detection Layer has no read access to Reputation Layer state
2. The Reputation Layer has no write access to Threat Detection Layer decisions
3. The two layers share no execution boundary, no shared scoring function, and no combined threshold
4. Audit logs record Threat Detection and Reputation decisions as separate, non-overlapping event classes

Procedural controls (e.g., policy rules that say "do not override") are insufficient. The separation MUST be architectural.

#### 5.5 Federation Publisher Trust

Federation publisher trust — how much weight to assign to governance signals received from remote AEGIS nodes — is a distinct concern from agent runtime trust. Publisher trust is governed by the normative model defined in GFN-1, which specifies the composite trust score formula, bootstrap mechanisms, decay, and revocation procedures for federation publishers.

Implementers MUST NOT apply the GFN-1 composite trust score (§3.7) to agent runtime trust decisions. The two models are scoped to different evaluation subjects and MUST remain structurally separate.

For federation signal ingestion thresholds, see GFN-1 §3.9 and §10.1. In the event of conflict between a publisher's authority class (§10.1) and their computed trust score (§3.9), the more restrictive disposition applies.

### 6. Delivery Guarantees

Supported patterns: pull feeds, push subscriptions, replicated append-only logs. Delivery semantics: at-least-once; idempotent consumer processing required.

---

## Drawbacks

- The two-layer trust model requires implementers to maintain structurally separate subsystems for threat detection and reputation tracking. This increases implementation complexity relative to a single composite score, but the separation is architecturally necessary — a composite model creates a category error that cannot be resolved by parameter tuning.
- The Reputation Layer requires operational history to produce meaningful scores. New agents begin at the lowest reputation tier and accumulate score over time.
- ed25519 signature verification adds per-event overhead. High-volume event streams require careful performance management.
- At-least-once delivery requires all consumers to implement idempotency, adding implementation burden.

---

## Alternatives Considered

**Single composite trust score with decay:** The prior version of this RFC defined trust as a single composite score decaying over time. This model was rejected because it collapses security signals and operational reliability into one number, creating a condition where accumulated reputation can implicitly soften a security gate. The flaw is architectural, not parametric — no tuning of decay rates resolves it. See §5.1.

**Unsigned events:** Simpler but provides no guarantee of publisher identity or payload integrity. Insufficient for governance intelligence sharing where a compromised publisher could poison policy state.

**Synchronous policy replication:** Eliminates eventual consistency but creates tight coupling between nodes and a single point of failure for policy updates.

**Centralized governance event broker:** Simplifies consumer implementation but introduces a single trusted intermediary, which conflicts with the federation model's goal of distributed governance.

---

## Compatibility

Downstream of [RFC-0001](./RFC-0001-AEGIS-Architecture.md) through RFC-0003. The event model enables federation between compliant AEGIS runtimes but does not modify the local governance cycle defined in RFC-0001 and RFC-0002.

The replacement of the composite trust model in §5 is a breaking change from v0.3. Implementations built against the v0.3 trust evaluation model must be updated to implement the two-layer separation defined in §5.2–§5.4.

---

## Implementation Notes

Complete payload examples for all five event types are in the canonical repository at `schemas/examples/governance/events/`. Implementers should validate against those examples before publishing events to a federation network.

Trust bootstrap for new federation nodes is handled by the mechanisms defined in GFN-1 §5. See that section for allowlist, consortium membership, transitive endorsement, and accelerated onboarding approaches.

Agent reputation bootstrap — the initial score assigned to a newly registered agent — MUST be defined in the operator's Schema-layer policy configuration. Agents with no operational history begin at the lowest reputation tier (< 0.25) unless the operator explicitly provisions a higher starting score with documented justification.

---

## Open Questions

- [ ] Should the event model define a standard backfill request protocol?
- [ ] How should the Reputation Layer handle agents that have never triggered a Threat Detection event — absence of detections versus no operational history yet? This is the agent-runtime equivalent of the federation question about nodes that have never published circumvention reports.

> **Closed:** *Should trust scores be published as governance attestation events, creating a recursive trust signal loop?*  
> **Resolution:** No. Publishing trust scores as governance attestation events would allow reputation signals to circulate through the federation and potentially influence Engine-layer decisions at remote nodes, violating the non-override constraint defined in §5.4. Trust scores are local, Schema-layer state. They are auditable within a node but are not federation events.

---

## Success Criteria

- Any two compliant AEGIS nodes can exchange all five event types without schema negotiation
- A replay attack is detected and rejected in all scenarios defined in Section 4
- A Threat Detection block cannot be bypassed by any Reputation Layer state, verified by audit log inspection showing the two decision classes as structurally separate
- Reputation score calculation is reproducible given the same operational history and evaluation timestamp `t`. Implementations MUST treat `t` as an explicit logged parameter. See GFN-1 §3.8 for the normative federation publisher decay specification.

---

## Acknowledgments

The two-layer trust separation model defined in §5 — specifically the architectural principle that security and reputation must never share a single score, and that no reputation accumulation grants a pass on a detected threat — was contributed by **Mattijs Moens** (Founder, Sovereign Shield) via peer review on 2026-03-15. His framing identified the category error in the prior composite trust model and proposed the structural separation that this section formalizes. The specification work is the AEGIS Initiative's; the foundational insight is his.

---

## References

[^17]: National Institute of Standards and Technology, *Zero Trust Architecture*, NIST SP 800-207, Aug. 2020. [Online]. Available: <https://doi.org/10.6028/NIST.SP.800-207>. See [REFERENCES.md](../REFERENCES.md).

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*  
*AEGIS Initiative — Finnoybu IP LLC*

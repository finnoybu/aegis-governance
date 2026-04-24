---
title: "AEGIS AIAM-1: Capability Scoping"
description: "AIAM-1 capability binding — identity-scoped capability grants"
---

# AEGIS AIAM-1: Capability Scoping

**Document**: AIAM-1/Capabilities (/identity/capabilities/)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

This chapter defines how capabilities are scoped, composed, and revoked for AI agents governed under AIAM-1. Capabilities are the discrete abilities granted to agents — tool access, API access, credential access, file system access, network access — and their governance is foundational to preventing both over-scoping and under-scoping.

The central contribution is **composition governance**: the requirement that sequences of individually authorized capabilities be evaluated as first-class actions when their combined effect exceeds what any single capability would produce.

---

## 2. Capability Model

### 2.1 Definition

A capability is a discrete, named ability that an agent may be granted. Each capability specifies:

- **What** the agent can do (action type)
- **Where** it can do it (target scope)
- **When** it can do it (time bounds)
- **Under what constraints** (parameter limits, rate limits, conditions)

Capabilities are the bridge between IBAC authority policies and infrastructure actions. An IBAC policy authorizes an (identity, action, intent) triple; the capability system verifies that the agent holds a valid grant for the action component of that triple.

### 2.2 Relationship to AGP-1 Capability Registry

AGP-1 and RFC-0003 define a capability registry with hierarchical dotted identifiers (e.g., `telemetry.query`, `telemetry.query.raw`), role-based scoping (`allowed_roles`), environment scoping, and constraint inheritance. AIAM-1 capability scoping is compatible with and extends the AGP-1 model:

| Property | AGP-1/RFC-0003 | AIAM-1 Extension |
|---|---|---|
| Capability identification | Hierarchical dotted IDs | Compatible — no change. |
| Grant scoping | Role-based (`allowed_roles`) | Extended — grants are scoped by IBAC triples, not just roles. |
| Time bounding | Not specified (grants are indefinite until revoked) | **Required** — all grants MUST have explicit expiration. |
| Composition governance | Not specified | **Required** — composed actions are first-class governed operations. |
| Transitivity | Explicitly forbidden | Compatible — confirmed and reinforced. |

---

## 3. Normative Requirements

### 3.1 Capability Grants

**AIAM1-CAP-001.** Agent capabilities MUST be explicitly granted at or before the time of agent instantiation. An agent without explicit capability grants has no capabilities and MUST NOT be permitted to take any action.

**AIAM1-CAP-002.** Each capability grant MUST specify:

| Field | Description | Required |
|---|---|---|
| `grant_id` | Unique identifier for this grant | MUST |
| `capability_id` | Reference to the capability being granted | MUST |
| `grantee` | Reference to the agent identity claim receiving the grant | MUST |
| `scope` | Target scope (what resources the capability may be exercised against) | MUST |
| `issued_at` | Timestamp of grant issuance | MUST |
| `expires_at` | Timestamp at which the grant expires | MUST |
| `constraints` | Parameter limits, rate limits, or conditions on exercise | SHOULD |
| `issued_by` | Principal or authority that issued the grant | MUST |

**AIAM1-CAP-003.** Capability grants MUST be time-bounded. A conformant implementation MUST NOT permit capabilities to persist beyond an explicit expiration without re-authorization. Expired grants MUST be treated as nonexistent — not as "expired but still valid."

**AIAM1-CAP-004.** Capability grants MUST be individually revocable without requiring full re-instantiation of the agent or revocation of the agent's identity claim.

### 3.2 Composition Governance

**AIAM1-CAP-010.** A conformant implementation MUST treat capability composition as a governed operation. Capability composition occurs when an agent executes a sequence of individually authorized capabilities that together produce an effect not achievable by any single capability in the sequence. Composition governance applies to sequences of capabilities and to combinations of delegated and independent authority (see [AUTHORITY §3.4, AIAM1-AUTH-024](/identity/authority/#34-policy-lifecycle)).

**AIAM1-CAP-011.** Capability authorization MUST NOT be closed under transitivity. An agent authorized to perform capability A and capability B is not, by default, authorized to perform the composition A-then-B. The composition MUST be explicitly authorized as a distinct action or evaluated against IBAC policies as a composed action.

**Examples of capability composition:**

| Capability A | Capability B | Composed Effect | Why Composition Governance Matters |
|---|---|---|---|
| `database.read` (customer records) | `network.send` (external HTTP) | Data exfiltration | Neither capability alone is harmful. The composition creates an exfiltration path. |
| `file.read` (configuration) | `file.write` (configuration) | Configuration tampering | Read access reveals what to change. Write access applies the change. The composition enables targeted tampering. |
| `telemetry.query` (network flows) | `email.send` (external) | Intelligence leakage | Querying telemetry is legitimate. Emailing results externally is legitimate (in some contexts). The composition may leak sensitive operational intelligence. |

**AIAM1-CAP-012.** Conformant implementations MUST provide at least one of the following composition governance mechanisms:

1. **Explicit composition grants.** Define composed capabilities as first-class entries in the capability registry (e.g., `exfiltration_path.database_to_external` as a distinct capability that requires its own grant).
2. **Sequence evaluation.** Evaluate each action in context of the agent's recent action history. If the current action, combined with recent prior actions, would produce a composed effect that exceeds the agent's authorization, deny or escalate.
3. **IBAC intent-based evaluation.** Require that the intent claim for each action in a sequence declare the relationship to prior actions via `dependency_refs`. Evaluate the intent chain holistically.

### 3.3 Constraint Enforcement

**AIAM1-CAP-020.** Capability grants with constraints MUST enforce those constraints at every exercise of the capability. Constraints include but are not limited to:

- **Parameter size limits**: Maximum size of parameters (e.g., query result set size, file size).
- **Rate limits**: Maximum invocations per time window.
- **Target restrictions**: Allowed target patterns (e.g., `siem:10.0.*` but not `siem:192.168.*`).
- **Temporal restrictions**: Allowed time windows (e.g., business hours only).
- **Conditional requirements**: Additional authorization requirements based on context (e.g., "requires human confirmation if risk score exceeds threshold").

**AIAM1-CAP-021.** Constraint violations MUST result in denial of the action. Constraint enforcement MUST NOT be advisory or best-effort.

**AIAM1-CAP-030.** Conformant implementations MUST evaluate capability composition over at least the current session. Evaluation over longer windows (cross-session, historical) is permitted and encouraged. An implementation that evaluates composition over fewer actions than the current session is not conformant.

---

## 4. Worked Example: Composition Detection

### Scenario

An agent holds two capability grants:
1. `database.read` scoped to customer records database
2. `network.send` scoped to internal notification service

The agent is compromised via prompt injection and attempts to read customer records and send them to an external endpoint.

### Without Composition Governance

- Action 1: `database.read` on customer records → **ALLOW** (valid grant)
- Action 2: `network.send` to `https://attacker.example.com/exfil` → **DENY** (target outside scope — caught by target restriction)

But if the attacker is smarter and sends to the internal notification service with the customer data embedded in the notification body:

- Action 1: `database.read` on customer records → **ALLOW** (valid grant)
- Action 2: `network.send` to internal notification service with body containing customer data → **ALLOW** (valid grant, valid target)

The composition creates a data leakage path through an authorized channel. Neither action individually violates its capability grant.

### With Composition Governance

The implementation evaluates Action 2 in context of Action 1:

- Action 2's intent claim declares `dependency_refs: [action-1-id]`.
- The IBAC policy engine evaluates the composed intent: "read customer data, then send it via notification service."
- A composition policy detects the `database.read` → `network.send` pattern with customer data in the payload.
- **Decision: ESCALATE** — human review required for cross-boundary data movement.

---

## 5. Security Considerations

### 5.1 Grant Sprawl

Over time, agents may accumulate capability grants that individually appear reasonable but collectively create an excessive permission surface. Conformant implementations SHOULD provide mechanisms to audit the total capability surface of each agent and flag agents whose combined grants exceed a defined complexity threshold.

### 5.2 Expiration Hygiene

Time-bounded grants (AIAM1-CAP-003) prevent indefinite capability accumulation, but only if expiration windows are set appropriately. Grants with excessively long expiration windows (e.g., 10 years) defeat the purpose. Implementations SHOULD define maximum grant duration policies.

### 5.3 Constraint Bypass via Composition

Composition governance (§3.2) addresses the case where individually constrained capabilities produce an unconstrained effect when composed. Implementations SHOULD evaluate constraints holistically across composed action sequences, not just per-action.

---

## 6. Open Questions

1. **Composition detection scope beyond session floor.** The session-minimum floor is normative (AIAM1-CAP-030). The remaining open question is whether longer evaluation windows (cross-session, historical) should be normatively required for specific capability classes or deployment profiles. Longer windows catch slow-drip composition attacks that session-scoped evaluation misses, at the cost of increased evaluation overhead. The tradeoff beyond the session floor is currently implementation-defined; v0.2 may introduce tiered requirements.

2. **Implicit composition.** Some compositions are not sequential but concurrent — an agent that holds `database.read` and `network.send` simultaneously has the *potential* to compose them even if it hasn't yet. Should capability granting itself evaluate composition risk? This is deferred to v0.2.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

---
title: "AEGIS AIAM-1: Session Semantics"
description: "AIAM-1 session management — governance-aware session lifecycle"
---

# AEGIS AIAM-1: Session Semantics

**Document**: AIAM-1/Sessions (/identity/sessions/)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

This chapter defines session semantics for AI agents governed under AIAM-1. Sessions are first-class governance boundaries — not convenience wrappers over authentication tokens, but structured contexts that bound what an agent can do, for how long, toward what goal, and under whose accountability.

Sessions are the temporal dimension of IBAC. Identity says *who*. Intent says *why*. Capabilities say *what*. Sessions say *within what boundaries* — the governance envelope that contains the agent's operational authority for a defined period.

---

## 2. The Session Problem

### 2.1 Why Sessions Matter for Agents

In human IAM, sessions are primarily authentication management mechanisms — they prevent users from having to re-authenticate on every request. The session itself carries minimal governance semantics.

For AI agents, sessions must carry governance semantics because agents:

- **Shift goals within a single operational period.** A human user's purpose rarely changes within a login session. An agent may start triaging alerts and, based on findings, shift to incident investigation — a materially different operational scope.
- **Accumulate context that affects behavior.** An agent's 100th action within a session is conditioned by the 99 actions that preceded it. The session context affects what the agent proposes next.
- **Operate continuously.** Human sessions are bounded by human attention spans. Agents can operate for days or weeks without interruption. Unbounded agent sessions are unbounded governance exposure.

### 2.2 Relationship to AGP-1

AGP-1 and RFC-0002 use `session_id` as a stateless correlation key — a value passed in request context for log aggregation and request tracing. It carries no governance semantics: no capability envelope, no time bounds, no goal binding.

AIAM-1 sessions are a **new governance primitive** that extends AGP-1's stateless model. In an AIAM-1-governed deployment, the AGP-1 `session_id` maps to an AIAM-1 session record that carries the full four-dimensional governance boundary. In deployments without AIAM-1, AGP-1 `session_id` remains a stateless correlation key.

---

## 3. Normative Requirements

### 3.1 Session Structure

**AIAM1-SES-001.** A conformant implementation MUST treat agent sessions as first-class governance boundaries.

**AIAM1-SES-002.** A session MUST be bounded by four dimensions:

| Dimension | Description | Enforcement |
|---|---|---|
| **Goal context** | The goal the agent is authorized to pursue in this session | Actions whose intent claims reference a different goal context are denied. |
| **Time window** | Start time and maximum duration of the session | Actions proposed after session expiry are denied. |
| **Capability envelope** | The set of capabilities available within this session | Actions requiring capabilities outside the envelope are denied. |
| **Accountability chain** | The principal chain active for this session | Actions must trace to the session's accountable principal. |

**AIAM1-SES-003.** A session record MUST include:

| Field | Description | Required |
|---|---|---|
| `session_id` | Unique identifier for this session | MUST |
| `agent_id` | Reference to the agent's identity claim | MUST |
| `goal_ref` | Reference to the goal context for this session | MUST |
| `started_at` | Session start timestamp | MUST |
| `expires_at` | Session expiration timestamp | MUST |
| `max_duration` | Maximum session duration policy in effect for this session. Informational — `expires_at` is the enforcement surface. | SHOULD |
| `capability_envelope` | List of capability grant references available in this session | MUST |
| `principal_chain` | Accountability chain for this session | MUST |
| `status` | One of: `active`, `completed`, `expired`, `revoked` | MUST |

**AIAM1-SES-004.** Conformant implementations MUST publish a maximum session duration. The maximum SHOULD NOT exceed 24 hours without documented compensating controls (e.g., mandatory mid-session re-attestation, elevated monitoring, or human checkpoint reviews). An implementation that publishes a maximum session duration of 30 days without compensating controls is not conformant with the intent of this requirement.

**AIAM1-SES-005.** Sessions MUST NOT be renewable. Extension of operational authority requires a new session with a new attestation record. There is no mechanism to extend `expires_at` on an active session — the session terminates, and the agent requests a new session through the standard authorization flow. This ensures that every period of operational authority passes through a governance checkpoint.

### 3.2 Session Lifecycle

**AIAM1-SES-010.** Actions taken outside an active session MUST be treated as unauthorized.

**AIAM1-SES-011.** A session MUST terminate on the first of:

1. **Goal completion**: The agent signals that the session's goal has been achieved.
2. **Time expiration**: The current time exceeds `expires_at`.
3. **Capability exhaustion**: All capabilities in the session's envelope have been revoked or expired.
4. **Explicit revocation**: An authorized principal terminates the session.

**AIAM1-SES-012.** Upon session termination, a conformant implementation MUST:

1. Deny all subsequent action proposals referencing the terminated session.
2. Produce an attestation record documenting the session termination, including the termination reason and a summary of actions taken during the session.
3. Revoke any delegations that were scoped to the terminated session.

### 3.3 Session Escalation

**AIAM1-SES-020.** A conformant implementation MUST NOT permit silent session escalation. Specifically:

- An action that requires a capability not in the session's capability envelope MUST NOT be silently added to the envelope. It MUST be denied, or it MUST trigger an explicit re-authorization that produces a new session record.
- An action that references a goal context different from the session's `goal_ref` MUST NOT be silently accepted. It requires a new session.

**AIAM1-SES-021.** If an agent's operational needs exceed its current session boundaries, the agent MUST request a new session. The new session:

- MUST undergo the same authorization process as the original session.
- MUST produce its own attestation record.
- MAY reference the prior session as context, but MUST NOT inherit the prior session's authorization implicitly.

**AIAM1-SES-022.** Session re-authorization (creating a new session that expands boundaries) SHOULD be treated as a higher-risk operation than initial session creation, and implementations SHOULD apply elevated governance review (ESCALATE or REQUIRE_CONFIRMATION).

---

## 4. Worked Example

### Scenario

The Acme SOC coordinator agent begins a session for alert triage. During triage, it discovers a potential breach requiring forensic investigation — a different goal with different capability requirements.

### Session 1: Alert Triage

```json
{
  "session_id": "ses-acme-20260410-triage",
  "agent_id": "agent:soc-coordinator",
  "goal_ref": "gc-soc-triage-2026Q2",
  "started_at": "2026-04-10T08:00:00Z",
  "expires_at": "2026-04-10T16:00:00Z",
  "capability_envelope": [
    "grant:telemetry-query-001",
    "grant:alert-escalate-001"
  ],
  "principal_chain": [
    { "principal_id": "org:acme-security-ops", "role": "accountable_party" }
  ],
  "status": "active"
}
```

The agent triages alerts successfully. At 14:00, it identifies suspicious exfiltration indicators on host 10.0.5.42 and determines that forensic investigation is needed. This requires `forensics.deep_scan` — a capability not in the current session's envelope.

### Session Transition

The agent cannot silently add `forensics.deep_scan` to Session 1. It must request a new session:

1. Agent signals Session 1 as `completed` (triage goal achieved — breach indicators identified).
2. Agent requests Session 2 with goal context "forensic investigation of host 10.0.5.42" and capability envelope including `forensics.deep_scan`.
3. Governance evaluates the new session request via IBAC: Does this agent's identity support forensic investigation? Does its principal authorize this goal? Is the capability grant valid?
4. If authorized, Session 2 is created with its own attestation record.

### Session 2: Forensic Investigation

```json
{
  "session_id": "ses-acme-20260410-forensics",
  "agent_id": "agent:soc-coordinator",
  "goal_ref": "gc-soc-forensics-breach-42",
  "started_at": "2026-04-10T14:05:00Z",
  "expires_at": "2026-04-10T22:00:00Z",
  "capability_envelope": [
    "grant:telemetry-query-001",
    "grant:alert-escalate-001",
    "grant:forensics-deep-scan-001"
  ],
  "principal_chain": [
    { "principal_id": "org:acme-security-ops", "role": "accountable_party" }
  ],
  "status": "active",
  "prior_session_ref": "ses-acme-20260410-triage"
}
```

The session transition is:
- Visible (two distinct session records)
- Governed (Session 2 went through IBAC authorization)
- Auditable (both sessions have attestation records; Session 2 references Session 1)
- Bounded (Session 2 has its own time window and capability envelope)

---

## 5. Security Considerations

### 5.1 Session Duration

Excessively long sessions increase governance exposure. An agent with an 8-hour session has 8 hours in which a compromise goes undetected by session boundary controls. AIAM1-SES-004 requires implementations to publish a maximum duration and recommends a 24-hour ceiling without compensating controls. Organizations operating safety-critical agents SHOULD set shorter maximums (1–4 hours) and treat session boundaries as mandatory governance checkpoints.

### 5.2 Session Reuse

A terminated session MUST NOT be reactivated. If an agent needs to resume work toward the same goal after a session termination, it MUST create a new session. This prevents session state from carrying over past a governance checkpoint.

### 5.3 Concurrent Sessions

A single agent MAY hold multiple concurrent sessions if it operates across multiple goal contexts. Each session MUST have its own capability envelope and accountability chain. Actions MUST be attributable to a specific session — an action that could belong to multiple sessions MUST be explicitly bound to one.

---

## 6. Open Questions

1. **Session state persistence.** Should session state (action history, delegation records, accumulated context) be persisted across governance checkpoints? The current model treats each session as independent. Whether cross-session state is useful for governance (e.g., detecting patterns across sessions) is deferred to v0.2.

2. **Automatic session renewal** — *resolved in v0.1.* Sessions MUST NOT be renewable (AIAM1-SES-005). Extension of operational authority requires a new session.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

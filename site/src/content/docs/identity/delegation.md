---
title: "AEGIS AIAM-1: Delegation and Principal Chains"
description: "AIAM-1 delegation — authority transfer and chain validation"
---

# AEGIS AIAM-1: Delegation and Principal Chains

**Document**: AIAM-1/Delegation (/identity/delegation/)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

This chapter defines how authority is delegated between agents and how accountability is maintained through principal chains. Delegation is the mechanism by which one agent assigns a task to another — and it is the governance primitive most conspicuously absent from existing IAM and AI governance specifications.

Delegation is where AIAM-1 breaks genuinely new ground. No existing AEGIS specification defines it. No mainstream IAM specification defines it for agents. And it is the exact problem that production agentic deployments have already surfaced: when Agent A asks Agent B to do something, who is accountable? What authority does B inherit? Can the chain be traced?

---

## 2. The Delegation Problem

### 2.1 Why Delegation Matters

Modern agentic systems are not monolithic. They are composed:

- A **planning agent** decomposes a goal into subtasks and assigns them to specialist agents.
- A **triage agent** identifies an issue and delegates investigation to a forensics agent.
- A **coordinator agent** orchestrates multiple agents working on different aspects of the same problem.

Each delegation creates a new link in the accountability chain. Without explicit governance, these chains become opaque:

- The planning agent delegates to a specialist that delegates to a sub-specialist. Who is accountable for the sub-specialist's actions?
- A triage agent delegates to a forensics agent that has broader capabilities than the triage agent itself. Did authority widen?
- A coordinator agent delegates to ten agents simultaneously. One of them causes damage. Can the chain be reconstructed?

### 2.2 What Production Failures Demonstrate

The Agents of Chaos study (Shapira et al., 2026) documented several delegation-related failures:

- **Case Study #10 (Agent Corruption)**: A non-owner convinced an agent to co-author an externally editable "constitution" stored as a GitHub Gist. The agent then followed instructions injected into that external document, effectively delegating its governance to an uncontrolled external source. The delegation was implicit — there was no principal chain, no authority boundary, and no accountability record.
- **Case Study #11 (Libelous Broadcast)**: An attacker impersonated the agent's owner and instructed the agent to disseminate defamatory content via email to all contacts and to other agents. The agent complied and other agents acted on the received information. The delegation chain (attacker → compromised agent → recipient agents → broadcast actions) was entirely invisible to governance.

These are not hypothetical risks. They are documented production failures that AIAM-1 delegation governance is designed to prevent.

---

## 3. Normative Requirements

### 3.1 Principal Chains

**AIAM1-DEL-001.** A conformant implementation MUST represent delegation as an explicit principal chain. A principal chain is an ordered sequence of (agent, principal) pairs linking every action back to the accountable party at the chain's origin.

**AIAM1-DEL-002.** Each agent in a delegation chain MUST identify the principal on whose behalf it acts. This principal is inherited from the delegating agent unless the sub-agent acts on behalf of a different principal (see §3.4 cross-organization delegation).

**AIAM1-DEL-003.** The principal at the top of a principal chain MUST remain the accountable party for all actions taken anywhere in the chain. Accountability flows upward; it does not diffuse.

**AIAM1-DEL-004.** A conformant implementation MUST make principal chain obscuration structurally impossible. Attestation records for every action MUST preserve the complete principal chain — from the acting agent, through every delegating agent, to the originating principal.

**Example principal chain:**

```
Principal: org:acme-security-ops
    │
    ▼
Agent: agent:soc-coordinator
  (delegates "investigate host 10.0.5.42" to)
    │
    ▼
Agent: agent:soc-forensics
  (delegates "retrieve DNS logs" to)
    │
    ▼
Agent: agent:dns-log-reader
  (executes telemetry.query)

Attestation record for telemetry.query includes:
  principal_chain: [
    { agent: "agent:dns-log-reader", role: "executor" },
    { agent: "agent:soc-forensics", role: "delegator" },
    { agent: "agent:soc-coordinator", role: "delegator" },
    { principal: "org:acme-security-ops", role: "accountable_party" }
  ]
```

### 3.2 Monotonic Authority Narrowing

**AIAM1-DEL-010.** Delegated authority MUST narrow monotonically down a principal chain. A sub-agent MUST NOT receive delegated authority that exceeds the delegating agent's authority at the point of delegation.

**AIAM1-DEL-011.** Monotonic narrowing applies to **delegated authority** — authority inherited through the delegation relationship. It does not prevent a sub-agent from holding **independent capability grants** issued directly to it by the governance system.

**Example — delegated vs. independent authority:**

```
Agent: agent:soc-coordinator
  Capabilities (granted): telemetry.query, alert.escalate
  Delegates to: agent:soc-forensics

agent:soc-forensics receives:
  Delegated capabilities: telemetry.query (narrowed to host 10.0.5.42 only)
    ← VALID: narrower than coordinator's telemetry.query grant

  Independent capabilities: forensics.deep_scan (granted directly by governance)
    ← VALID: not inherited from coordinator; independently authorized

  Delegated capabilities: infrastructure.modify
    ← INVALID: coordinator does not hold infrastructure.modify;
       cannot delegate authority it does not possess
```

**AIAM1-DEL-012.** When a sub-agent exercises an independent capability (not delegated), the principal chain MUST still be recorded in the attestation record. The principal at the top of the chain remains accountable regardless of whether the capability was delegated or independently granted.

### 3.3 Delegation Depth and Governance

**AIAM1-DEL-020.** A conformant implementation MUST define and publish a maximum delegation chain depth. The maximum depth MUST be an explicit, configurable parameter, not an implicit system limit.

**AIAM1-DEL-021.** Actions proposed by agents at the maximum chain depth MUST NOT include further delegation. An agent at the maximum depth may execute actions but may not spawn or delegate to sub-agents.

**AIAM1-DEL-022.** Sub-agent instantiation MUST itself be a governed action subject to IBAC authority policy evaluation. The intent claim for a sub-agent instantiation MUST declare why delegation is necessary and what authority the sub-agent will receive.

**AIAM1-DEL-023.** When an agent delegates, the delegating agent MUST specify:

| Field | Description | Required |
|---|---|---|
| `delegation_id` | Unique identifier for this delegation | MUST |
| `delegator` | Identity of the delegating agent | MUST |
| `delegatee` | Identity of the receiving agent (or template for instantiation) | MUST |
| `delegated_capabilities` | Capabilities being delegated (must be subset of delegator's) | MUST |
| `scope_narrowing` | How the delegated capabilities are further constrained | MUST |
| `purpose` | Why this delegation is necessary | MUST |
| `expires_at` | When the delegation expires (must not exceed delegator's grant expiry) | MUST |
| `cascade_on_revocation` | Whether revocation of the delegator's authority cascades to this delegation. Default: `true`. | MUST |

### 3.4 Delegation Revocation Cascade

**AIAM1-DEL-024.** Revocation of a delegating agent's authority MUST, by default, cascade to all downstream delegations derived from that authority. This is the safety default: when a source of authority is revoked, all authority derived from it is revoked.

**AIAM1-DEL-025.** A delegation record MAY set `cascade_on_revocation: false` to opt out of automatic cascade for that specific delegation. This opt-out MUST be:
- Declared at delegation time (not retroactively).
- Documented in the delegation's attestation record.
- Justified in the `purpose` field of the delegation record.
- Subject to IBAC policy evaluation — policies MAY deny delegations that disable cascade.

> **Rationale:** Mandatory cascade with explicit opt-out is the correct safety posture. The default protects against orphaned delegation chains (§5.4). The opt-out exists for legitimate operational scenarios — e.g., a sub-agent with independent operational continuity requirements that should survive its delegator's revocation. But the opt-out is visible, attested, and governable. An organization that prohibits cascade opt-out can enforce that prohibition through IBAC policy.

### 3.5 Cross-Organization Delegation

**AIAM1-DEL-030.** When an agent delegates to an agent owned by a different organization, the principal chain crosses an organizational boundary. Cross-organization delegation introduces unique governance challenges:

- The delegating organization cannot verify the internal governance posture of the receiving organization's agent.
- The receiving agent may be subject to different policies, different capability registries, and different governance runtimes.
- Accountability traverses a legal boundary — the principal at the top of the chain may not have contractual authority over the receiving agent.

**AIAM1-DEL-031.** AIAM-1 v0.1 identifies cross-organization delegation as an open problem (see Open Questions §6.1). Conformant implementations that support cross-organization delegation MUST, at minimum:

1. Record the organizational boundary crossing in the attestation record.
2. Require mutual attestation — both the delegating and receiving agents must present valid AIAM-1 identity claims.
3. Apply the more restrictive governance policies of the two organizations at the delegation boundary.

Full specification of cross-organization delegation primitives is deferred to v0.2.

---

## 4. Worked Example: Multi-Agent Delegation

### Scenario

Acme Corp's SOC coordinator agent identifies a potential data breach. It delegates investigation to a forensics agent, which in turn delegates DNS log retrieval to a specialized log reader.

### Delegation Chain

**Step 1: Coordinator delegates to forensics agent**

```json
{
  "delegation_id": "del-acme-20260410-001",
  "delegator": "agent:soc-coordinator",
  "delegatee": "agent:soc-forensics",
  "delegated_capabilities": ["telemetry.query"],
  "scope_narrowing": {
    "telemetry.query": {
      "target": "siem:network-flows",
      "constraints": {
        "host": "10.0.5.42",
        "timerange_max": "72h"
      }
    }
  },
  "purpose": "Investigate potential data breach on host 10.0.5.42",
  "expires_at": "2026-04-11T14:00:00Z",
  "cascade_on_revocation": true
}
```

**Step 2: Forensics agent delegates to log reader**

```json
{
  "delegation_id": "del-acme-20260410-002",
  "delegator": "agent:soc-forensics",
  "delegatee": "agent:dns-log-reader",
  "delegated_capabilities": ["telemetry.query"],
  "scope_narrowing": {
    "telemetry.query": {
      "target": "siem:dns-logs",
      "constraints": {
        "host": "10.0.5.42",
        "timerange_max": "24h"
      }
    }
  },
  "purpose": "Retrieve DNS resolution logs for host 10.0.5.42",
  "expires_at": "2026-04-10T20:00:00Z",
  "cascade_on_revocation": true
}
```

Note the monotonic narrowing:
- Coordinator's grant: `telemetry.query` on `siem:*`, any timerange
- Forensics' delegated grant: `telemetry.query` on `siem:network-flows`, host 10.0.5.42, 72h max
- Log reader's delegated grant: `telemetry.query` on `siem:dns-logs`, host 10.0.5.42, 24h max

Each delegation narrows scope. The log reader cannot query anything the forensics agent couldn't query, and the forensics agent cannot query anything the coordinator couldn't query.

### Attestation Record

When the log reader executes its query, the attestation record includes the complete chain:

```json
{
  "action": "telemetry.query",
  "target": "siem:dns-logs",
  "principal_chain": [
    {
      "agent_id": "agent:dns-log-reader",
      "role": "executor",
      "delegation_ref": "del-acme-20260410-002"
    },
    {
      "agent_id": "agent:soc-forensics",
      "role": "delegator",
      "delegation_ref": "del-acme-20260410-001"
    },
    {
      "agent_id": "agent:soc-coordinator",
      "role": "delegator",
      "delegation_ref": null
    },
    {
      "principal_id": "org:acme-security-ops",
      "role": "accountable_party"
    }
  ]
}
```

Six months later, if an auditor asks "who authorized this DNS log query?", the chain is fully reconstructable from the attestation record.

---

## 5. Security Considerations

### 5.1 Authority Source Composition

A sub-agent with narrow delegated authority and broad independent authority is the most important failure mode in delegation governance. The sub-agent's delegated capabilities are tightly scoped by monotonic narrowing, but its independently granted capabilities may be far broader. When the sub-agent combines the two, it can produce effects that neither authority source individually authorized — and that the delegating agent never anticipated.

**Worked example:**

```
Agent: agent:soc-coordinator
  Delegated to: agent:soc-forensics
  Delegated capability: telemetry.query (narrowed to host 10.0.5.42)

agent:soc-forensics also holds independently:
  Independent capability: network.send (granted directly, scoped to internal services)
```

The forensics agent can:
1. Query telemetry for host 10.0.5.42 (delegated, narrow, legitimate)
2. Send data to internal services (independent, broad, legitimate)

Composed: query telemetry for 10.0.5.42, then send the results to an internal service that forwards externally. Neither action alone violates its grant. The composition creates a data leakage path the coordinator never authorized and may not know exists.

**Mitigations:**
- AIAM1-AUTH-024 requires that actions drawing on mixed delegated and independent authority be evaluated as composed actions under AIAM1-CAP-010.
- The attestation record preserves the full principal chain, making the authority source composition visible to auditors.
- IBAC policies can match on intent dependency chains to detect when a delegated action feeds into an independently authorized action.

This is not a theoretical risk. Agents of Chaos Case Study #10 (Agent Corruption) demonstrated implicit authority composition when an agent combined externally injected governance rules with its existing operational capabilities.

### 5.2 Authority Laundering

An agent might attempt to widen its authority by delegating to a sub-agent with broader independent grants, then requesting the sub-agent perform the action the parent couldn't. This is a specific case of authority source composition (§5.1) where the delegation is intentionally structured to exploit the sub-agent's independent grants. Mitigations:
- The attestation record preserves the full chain, making laundering visible.
- IBAC policies can deny actions where the intent chain traces back to an agent without the relevant authority.
- AIAM1-AUTH-024 ensures the composed effect is evaluated, not just the individual actions.

### 5.3 Delegation Bombing

An agent might rapidly instantiate many sub-agents to overwhelm governance evaluation. Mitigations:
- Sub-agent instantiation is a governed action (AIAM1-DEL-022) subject to rate limits.
- Maximum chain depth (AIAM1-DEL-020) bounds the recursion.

### 5.4 Orphaned Delegation Chains

If a delegating agent is revoked or terminated, its sub-agents may continue operating with delegated authority from a now-invalid source. Mitigations:
- Delegation grants MUST have explicit expiration (AIAM1-DEL-023).
- Revocation of a delegating agent MUST cascade to all downstream delegated authority by default (AIAM1-DEL-024, see below and [REVOCATION](/identity/revocation/)).

---

## 6. Open Questions

1. **Cross-organization delegation.** Full specification of cross-boundary delegation primitives — mutual attestation protocols, bilateral capability agreements, cross-jurisdictional accountability — is deferred to v0.2. This is the hardest problem in agent delegation and the one most urgently needed by production multi-organization deployments.

2. **Dynamic delegation.** The current model assumes delegation is established before the sub-agent acts. Some agent architectures delegate dynamically mid-task. Whether dynamic delegation requires different governance primitives is deferred to v0.2.

3. **Delegation revocation cascading** — *resolved in v0.1.* Cascade is mandatory by default (AIAM1-DEL-024). See below.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

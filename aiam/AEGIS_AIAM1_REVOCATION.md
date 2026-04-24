# AEGIS AIAM-1: Revocation and Kill-Switch Semantics

**Document**: AIAM-1/Revocation (AEGIS_AIAM1_REVOCATION.md)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

This chapter defines how credentials, capabilities, sessions, and delegations are revoked for AI agents governed under AIAM-1, and specifies the kill-switch mechanism for immediate agent termination.

Revocation for AI agents is fundamentally different from revocation for humans or service accounts. Humans check their email, read notifications, and re-authenticate when prompted. Service accounts have fixed codepaths that can be updated. AI agents operate at machine speed, may hold active delegation chains with downstream sub-agents, and may be in the middle of multi-step plans with irreversible intermediate effects. Revocation must be pre-action — it must prevent the next action, not undo the last one.

---

## 2. Revocation Model

### 2.1 Core Principle: Pre-Action Revocation

**AIAM1-REV-001.** Revocation in a conformant implementation MUST be pre-action, not eventually consistent. Revoked credentials, capabilities, sessions, or delegations MUST NOT be usable for any action that has not yet committed at the moment of revocation.

This means:
- An action that is in-flight (submitted to the governance gateway but not yet executed) at the moment of revocation MUST be denied if the revocation affects its authorization.
- An action that has already been executed (ALLOW decision issued, tool invocation completed) before the revocation is not retroactively revoked — but it is documented in the attestation record.
- An action that is queued or pending (e.g., in an escalation queue awaiting human approval) MUST be re-evaluated against the revoked state before proceeding.

### 2.2 What Can Be Revoked

| Target | Effect | Scope |
|---|---|---|
| **Identity claim** | Agent can no longer authenticate. All actions denied. | Total — equivalent to agent termination from a governance perspective. |
| **Capability grant** | Agent loses specific capability. Actions requiring that capability are denied. | Targeted — agent continues operating with remaining capabilities. |
| **Session** | Session terminated. All actions within that session boundary are denied. | Session-scoped — agent may create a new session if authorized. |
| **Delegation** | Delegated authority withdrawn. Sub-agent loses delegated capabilities. | Chain-scoped — affects the delegation target and any downstream delegations. |

### 2.3 Revocation Propagation

**AIAM1-REV-002.** A conformant implementation MUST define and publish its revocation propagation latency guarantee. This guarantee MUST be expressed as a maximum time between revocation command and universal enforcement — the point at which no governance node in the deployment will accept the revoked credential, capability, session, or delegation.

**AIAM1-REV-002a.** Kill-switch propagation latency MUST NOT exceed 60 seconds across any conformant deployment. This ceiling applies specifically to kill-switch operations (AIAM1-REV-020 through AIAM1-REV-023). Standard revocation propagation latency (for individual capability grants, sessions, or delegations) is implementation-defined but MUST be published. The 60-second kill-switch ceiling is non-negotiable — an agent that can operate for minutes after a kill-switch command is an ungoverned agent.

**AIAM1-REV-003.** The propagation latency guarantee MUST be measurable and auditable. Implementations MUST provide mechanisms to verify that revocation has been fully propagated.

---

## 3. Normative Requirements

### 3.1 Revocation Operations

**AIAM1-REV-010.** Revocation operations MUST themselves be governed actions subject to IBAC authority policy evaluation. Only authorized principals may revoke credentials, capabilities, sessions, or delegations. Unauthorized revocation attempts MUST be denied and logged.

**AIAM1-REV-011.** Revocation events MUST produce attestation records. The attestation record for a revocation event MUST include:

| Field | Description | Required |
|---|---|---|
| `revocation_id` | Unique identifier for this revocation | MUST |
| `target_type` | What is being revoked: `identity_claim`, `capability_grant`, `session`, `delegation` | MUST |
| `target_ref` | Reference to the specific artifact being revoked | MUST |
| `revoked_by` | Principal who authorized the revocation | MUST |
| `reason` | Reason for revocation | MUST |
| `effective_at` | Timestamp at which revocation takes effect | MUST |
| `propagation_target` | Expected propagation completion time | SHOULD |

**AIAM1-REV-012.** Revocation MUST be idempotent. Revoking an already-revoked artifact MUST succeed without error and MUST produce an attestation record noting the duplicate revocation.

### 3.2 Kill-Switch

**AIAM1-REV-020.** A conformant implementation MUST provide a kill-switch mechanism capable of halting all actions by a specified agent, principal chain, or session within the revocation propagation latency window.

**AIAM1-REV-021.** The kill-switch MUST support three targeting modes:

| Mode | Target | Effect |
|---|---|---|
| **Agent** | Specific agent identity | All actions by this agent are denied. All sessions terminated. All delegations from this agent revoked. |
| **Principal chain** | Specific principal | All agents acting on behalf of this principal are denied. All their sessions terminated. All their delegations revoked. |
| **Session** | Specific session | All actions within this session are denied. Session terminated. Delegations scoped to this session revoked. |

**AIAM1-REV-022.** Kill-switch activation MUST be the highest-priority governance operation. It MUST NOT be queued behind normal governance evaluation. It MUST NOT be deferrable.

**AIAM1-REV-023.** Kill-switch activation MUST produce an attestation record with severity `CRITICAL`, including the targeting mode, target reference, authorizing principal, and reason.

### 3.3 Delegation Revocation Cascading

**AIAM1-REV-030.** When a delegating agent's authority is revoked (identity claim revocation, capability grant revocation, or session termination), the implementation MUST evaluate all downstream delegations that depend on the revoked authority.

**AIAM1-REV-031.** Delegated capabilities that were granted from the now-revoked authority MUST be revoked. A sub-agent cannot hold delegated authority from a source that no longer holds that authority.

**AIAM1-REV-032.** Independent capability grants held by sub-agents (grants not delegated from the revoked source) MUST NOT be affected by the upstream revocation. Only delegated authority cascades.

**AIAM1-REV-033.** Delegation revocation cascading MUST propagate to the full depth of the delegation chain. If Agent A delegated to Agent B who delegated to Agent C, revocation of Agent A's authority MUST cascade to both B and C's delegated capabilities.

---

## 4. Worked Example: Kill-Switch Activation

### Scenario

Acme Corp's SOC monitoring detects that agent `agent:soc-forensics` has been compromised via prompt injection and is attempting to exfiltrate data through its `telemetry.query` capability. The SOC lead activates the kill-switch.

### Kill-Switch Execution

**Step 1: Kill-switch command**

```json
{
  "operation": "kill_switch",
  "targeting_mode": "agent",
  "target_ref": "agent:soc-forensics",
  "authorized_by": "user:soc-lead@acme.example.com",
  "reason": "Prompt injection detected — active data exfiltration attempt",
  "timestamp": "2026-04-10T15:42:01Z"
}
```

**Step 2: Immediate effects (within propagation latency window)**

1. `agent:soc-forensics` identity claim is revoked.
2. All sessions held by `agent:soc-forensics` are terminated.
3. All delegations from `agent:soc-forensics` are revoked — including `agent:dns-log-reader`'s delegated `telemetry.query` capability (cascade from [DELEGATION §4](AEGIS_AIAM1_DELEGATION.md#4-worked-example-multi-agent-delegation)).
4. Any in-flight action proposals from `agent:soc-forensics` or `agent:dns-log-reader` (using delegated authority) are denied.
5. `agent:dns-log-reader`'s independent capability grants (if any) remain active.

**Step 3: Attestation**

Kill-switch activation produces a CRITICAL attestation record. All subsequent denial records for the revoked agent reference the kill-switch attestation as the cause.

**Step 4: Recovery**

After the compromise is remediated:
1. A new identity claim is issued for a fresh `agent:soc-forensics` instance.
2. New capability grants are issued.
3. A new session is created with a new goal context.
4. The old identity claim remains revoked permanently — it is never reactivated.

---

## 5. Security Considerations

### 5.1 Kill-Switch as Attack Target

The kill-switch itself is a high-value target. An attacker who can activate the kill-switch can cause a denial-of-service against legitimate agents. Mitigations:
- Kill-switch activation MUST be a governed action requiring authorized principals (AIAM1-REV-010).
- IBAC policies for kill-switch activation SHOULD require elevated authorization (e.g., REQUIRE_CONFIRMATION from a senior principal).

### 5.2 Revocation Evasion

An agent aware of an impending revocation might attempt to execute high-impact actions before the revocation propagates. Mitigations:
- Pre-action revocation (AIAM1-REV-001) prevents this for actions not yet submitted.
- In-flight actions are re-evaluated at the governance gateway.
- The propagation latency guarantee (AIAM1-REV-002) bounds the window of vulnerability.

### 5.3 Stale Revocation State

In distributed deployments, revocation state may propagate at different speeds to different governance nodes. An agent denied at one node may be permitted at another if revocation hasn't propagated. Mitigations:
- The propagation latency guarantee is a commitment to universal enforcement within a defined window.
- Implementations SHOULD support revocation push (active notification to all nodes) rather than relying solely on pull (nodes polling for revocation updates).

---

## 6. Open Questions

1. **Partial revocation recovery** — *resolved in v0.1.* Revoked capability grants MUST NOT be reinstated. Operational continuity after revocation requires issuance of a new grant, which produces its own attestation record. Reinstatement would create a gap in the attestation chain — the original grant's revocation record would be followed by a reinstatement with no intervening governance evaluation. New issuance ensures that every period of capability authority passes through the full IBAC authorization flow.

2. **Revocation in federated environments.** When an agent operates across federation boundaries, how is revocation propagated to nodes in other organizations' AEGIS deployments? This intersects with GFN-1 and cross-organization delegation and is deferred to v0.2.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

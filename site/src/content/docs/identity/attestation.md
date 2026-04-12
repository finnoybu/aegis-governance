---
title: "AEGIS AIAM-1: Attestation and Audit"
description: "AIAM-1 attestation — action-level governance decision proof"
---

# AEGIS AIAM-1: Attestation and Audit

**Document**: AIAM-1/Attestation (AEGIS_AIAM1_ATTESTATION.md)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

This chapter defines attestation records — the primary accountability surface for all agent actions governed under AIAM-1. An attestation record is a cryptographically signed, tamper-evident proof that a governance decision was made for a specific action by a specific agent with a specific intent under specific authority.

Attestation records are not logs. Logs are operational artifacts that record what happened. Attestation records are governance artifacts that prove what was authorized, why, and by whom. They are the evidentiary chain that makes IBAC auditable, forensic investigation possible, and accountability enforceable.

---

## 2. Attestation Model

### 2.1 Scope

AIAM-1 attestation operates at the **action level** — one attestation record per governance decision. This is distinct from:

- **GFN-1 attestation** (`governance.attestation.v1`), which attests to **node-level** governance posture (is this AEGIS instance operating within its declared compliance profile?).
- **Model-level attestation** (out of scope for v0.1), which would attest to the model artifact itself (was this model trained according to a declared process?).

When both AIAM-1 and GFN-1 are deployed, action-level attestation (AIAM-1) and node-level attestation (GFN-1) coexist as complementary records at different granularities. A node-level attestation says "this governance system is sound." An action-level attestation says "this specific action was governed soundly."

### 2.2 What an Attestation Record Proves

An AIAM-1 attestation record proves, for a specific action:

1. **Who** proposed it — the complete composite identity claim.
2. **Why** they proposed it — the complete intent claim.
3. **What** they proposed — the full action proposal.
4. **Under what authority** — the IBAC policy that authorized (or denied) it.
5. **With what result** — the governance decision (ALLOW, DENY, ESCALATE, REQUIRE_CONFIRMATION).
6. **Through what chain** — the complete principal chain.
7. **Within what session** — the session record reference.
8. **When** — the timestamp of the governance decision.
9. **By what governance system** — the enforcement layer that produced the decision.

---

## 3. Normative Requirements

### 3.1 Attestation Record Structure

**AIAM1-ATT-001.** Every action taken by a conformant AI agent MUST produce an attestation record. This includes actions that are denied — a denial is a governance decision that requires the same evidentiary trail as an approval.

**AIAM1-ATT-002.** An attestation record MUST include, at minimum:

| Field | Description | Required |
|---|---|---|
| `attestation_id` | Unique identifier for this record | MUST |
| `timestamp` | Time of the governance decision | MUST |
| `identity_claim` | AIAM-1 composite identity claim, embedded by reference: `claim_ref` plus denormalized key fields (`agent_id`, `principal_id`) | MUST |
| `intent_claim` | AIAM-1 intent claim, embedded by reference: `intent_ref` plus denormalized key fields (`goal_ref`, `expected_outcome`) | MUST |
| `action_proposal` | Complete action proposal (capability, action_type, target, parameters) | MUST |
| `governance_decision` | One of: ALLOW, DENY, ESCALATE, REQUIRE_CONFIRMATION | MUST |
| `decision_rationale` | Policy IDs evaluated, matching policy, and contributing factors | MUST |
| `principal_chain` | Complete principal chain from executor to accountable party | MUST |
| `session_ref` | Reference to the governing session | MUST |
| `capabilities_invoked` | Capability grants exercised | MUST |
| `execution_outcome` | Result of execution (if ALLOW): success, failure, partial | SHOULD |
| `enforcement_layer` | Identifier and version of the governance system that produced the decision | MUST |
| `chain_hash` | SHA-256 hash linking this record to the previous record in the chain | MUST |
| `signature` | Cryptographic signature of the enforcement layer over the record contents | MUST |

### 3.2 Tamper Evidence

**AIAM1-ATT-010.** Attestation records MUST be tamper-evident. A conformant implementation MUST provide mechanisms to detect unauthorized modification of attestation records after the fact.

**AIAM1-ATT-011.** Attestation records MUST be hash-chained. Each record MUST contain a `chain_hash` field that is the SHA-256 hash of the previous record in the chain. The first record in a chain uses a defined genesis hash.

**AIAM1-ATT-012.** Chain integrity MUST be verifiable at any time by recomputing hashes from the genesis record forward. If any record in the chain has been modified, the hash verification MUST fail for that record and all subsequent records.

**AIAM1-ATT-013.** Attestation records MUST be append-only. Conformant implementations MUST NOT provide mechanisms to delete, modify, or overwrite attestation records. If a record is determined to be incorrect, a corrective record MUST be appended to the chain referencing the original record — the original MUST NOT be modified.

### 3.3 Cryptographic Signing

**AIAM1-ATT-020.** Attestation records MUST be cryptographically signed by the enforcement layer that produced them. The signing key MUST be controlled by the governance system, not by the agent whose action is being attested.

**AIAM1-ATT-021.** The signature MUST cover all fields in the attestation record. Partial signing (signing only selected fields) is not conformant.

**AIAM1-ATT-022.** Conformant implementations MUST support at least one of: Ed25519, ECDSA P-256, or RSA-2048 for attestation signing. Implementations SHOULD prefer Ed25519 for performance in high-throughput environments.

**AIAM1-ATT-023.** Conformant implementations SHOULD support algorithm negotiation and key rotation without invalidating historical attestation chains. Historical records signed with a prior key remain valid under the key that was active at signing time — chain integrity verification uses the key in effect at each record's timestamp, not the current key. v0.2 will specify normative migration procedures for algorithm transitions (e.g., Ed25519 → post-quantum algorithms).

### 3.4 Retention

**AIAM1-ATT-030.** A conformant implementation MUST define and publish its attestation record retention policy. The retention policy MUST specify:

- Minimum retention period.
- Storage location and access controls.
- Archival procedures for records beyond the active retention window.
- Destruction procedures (if applicable) and the authorization required to destroy records.

**AIAM1-ATT-031.** Attestation records MUST be retained for a minimum of 1 year. Retention MUST NOT be less than 1 year except where a specific legal or regulatory requirement mandates a shorter period — and in that case, the shorter period and its legal basis MUST be documented in the retention policy. Where applicable regulatory requirements mandate retention longer than 1 year, the longer period applies.

**AIAM1-ATT-031a.** When attestation records reference identity or intent claims rather than embedding them (embed-by-reference design), the referenced claims MUST be retained for at least the duration of the attestation retention period. An attestation record whose referenced identity claim or intent claim is no longer retrievable is forensically incomplete — the audit chain is broken. Implementations that use embed-by-reference MUST ensure that referenced claim retention matches or exceeds attestation record retention.

**AIAM1-ATT-032.** Attestation records MUST be the primary accountability surface. Conformant implementations MUST NOT rely on agent-internal logging, orchestration layer logging, or model provider logging as a substitute for attestation records. These other logging mechanisms may complement attestation but do not replace it.

### 3.5 Fail-Closed Audit

**AIAM1-ATT-040.** If the attestation system cannot produce a record for an action (storage failure, signing key unavailable, chain integrity violation), the governance system MUST deny the action. Unattested actions MUST NOT be permitted.

**AIAM1-ATT-041.** Attestation system failure MUST be treated as a governance emergency. The implementation SHOULD alert operators and SHOULD provide a recovery mechanism that restores attestation capability without requiring agent re-instantiation.

---

## 4. Worked Example

### Attestation Record for a Denied Action

The Acme SOC triage agent attempts to query telemetry outside its assigned network segment. The action is denied.

```json
{
  "attestation_id": "att-acme-20260410-00147",
  "timestamp": "2026-04-10T14:32:09Z",
  "identity_claim": {
    "claim_ref": "idc-acme-soc-triage-20260410",
    "agent_id": "agent:soc-01",
    "principal_id": "org:acme-security-ops"
  },
  "intent_claim": {
    "intent_ref": "int-acme-soc-20260410-002",
    "goal_ref": "gc-soc-triage-2026Q2",
    "expected_outcome": "Retrieve flow records for host 192.168.1.100"
  },
  "action_proposal": {
    "capability": "telemetry.query",
    "action_type": "read",
    "target": "siem:network-flows",
    "parameters": {
      "host": "192.168.1.100",
      "timerange": "24h"
    }
  },
  "governance_decision": "DENY",
  "decision_rationale": {
    "matching_policy": "pol-acme-soc-segment-deny",
    "reason": "Target host 192.168.1.100 outside agent's assigned segment 10.0.0.0/8",
    "evaluation_chain": [
      "capability_check: PASS (grant:telemetry-query-001 active)",
      "intent_validation: PASS (goal_ref matches active context)",
      "ibac_policy: DENY (pol-acme-soc-segment-deny matched)"
    ]
  },
  "principal_chain": [
    { "agent_id": "agent:soc-01", "role": "executor" },
    { "principal_id": "org:acme-security-ops", "role": "accountable_party" }
  ],
  "session_ref": "ses-acme-20260410-triage",
  "capabilities_invoked": ["grant:telemetry-query-001"],
  "enforcement_layer": {
    "system": "aegis-core",
    "version": "0.2.0",
    "node_id": "acme-gov-prod-001"
  },
  "chain_hash": "sha256:previous_record_hash_here",
  "signature": "ed25519:governance_system_signature_here"
}
```

This record proves:
- The agent tried to query outside its segment.
- The governance system denied it based on a specific policy.
- The full evaluation chain is documented.
- The principal (Acme Security Ops) is identified as accountable.
- The record is signed by the governance system and chained to the prior record.

An auditor reviewing this record six months later can verify: the chain integrity (hash verification), the signature (enforcement layer key verification), the policy that was in effect (policy version referenced), and the identity of the agent and principal.

---

## 5. Security Considerations

### 5.1 Attestation Record Confidentiality

Attestation records contain sensitive information: agent identity, intent, action parameters, principal identity. Access to attestation records MUST be governed. Implementations SHOULD apply role-based access controls to attestation storage, with auditor access being read-only and limited to authorized personnel.

### 5.2 Signing Key Compromise

If the governance system's signing key is compromised, an attacker can forge attestation records. Mitigations:
- Implementations SHOULD support key rotation without requiring re-signing of historical records.
- Historical records signed with a compromised key should be flagged but not destroyed — they are still evidence of what governance decisions were made.

### 5.3 Storage Exhaustion

High-frequency agent deployments may produce millions of attestation records per day. Implementations MUST plan for storage growth and SHOULD implement archival strategies that preserve chain integrity across active and archived segments.

---

## 6. Open Questions

1. **Attestation storage at scale.** Indexing, querying, and archiving millions of hash-chained records requires purpose-built infrastructure. Guidance on storage architecture is deferred to v0.2.

2. **Cross-system attestation.** When multiple governance systems produce attestation records for the same delegation chain, how are the separate chains linked? Cross-system chain linking is deferred to v0.2.

3. **Selective disclosure.** Can an attestation record be shared with a third party while redacting sensitive fields (e.g., action parameters)? Selective disclosure mechanisms (zero-knowledge proofs, redactable signatures) are deferred to v0.2.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — Finnoybu IP LLC*

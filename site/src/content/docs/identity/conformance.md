---
title: "AEGIS AIAM-1: Conformance"
description: "AIAM-1 conformance — compliance levels and validation criteria"
---

# AEGIS AIAM-1: Conformance

**Document**: AIAM-1/Conformance (AEGIS_AIAM1_CONFORMANCE.md)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

This chapter defines the conformance requirements for AIAM-1, including the conformance checklist, conformance statement format, and guidance for implementations claiming AIAM-1 conformance.

---

## 2. Conformance Profiles

### 2.1 AIAM-1 v0.1 Profile

AIAM-1 v0.1 defines a single conformance profile: **Full Conformance**. A conformant implementation satisfies all MUST and MUST NOT requirements across all normative documents in the AIAM-1 specification suite.

Future versions MAY define additional profiles:
- **Constrained Profile**: For resource-limited edge deployments where full attestation or IBAC evaluation is not feasible.
- **Federation Profile**: For deployments participating in cross-organization agent governance.
- **Audit-Only Profile**: For deployments that implement attestation and audit without full IBAC enforcement.

These are not specified in v0.1.

---

## 3. Conformance Checklist

The following checklist enumerates all MUST and MUST NOT requirements from the AIAM-1 specification suite. A conformant implementation satisfies all items marked MUST and violates no items marked MUST NOT.

### 3.1 Identity (AEGIS_AIAM1_IDENTITY.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-ID-001 | Represent agent identity as four-dimensional composite (model provenance, orchestration, goal context, principal) | MUST |
| AIAM1-ID-002 | Each dimension independently verifiable | MUST |
| AIAM1-ID-003 | Each dimension independently revocable | MUST |
| AIAM1-ID-010 | Model provenance includes model_family, model_version, model_attestation | MUST |
| AIAM1-ID-011 | Model attestation verifiable without weight access | MUST |
| AIAM1-ID-012 | Model change triggers identity claim reissuance | MUST |
| AIAM1-ID-020 | Orchestration layer includes runtime, framework, framework_version | MUST |
| AIAM1-ID-030 | Goal context includes goal_id, purpose, scope | MUST |
| AIAM1-ID-031 | Goal context sufficiently specific to distinguish instantiations | MUST |
| AIAM1-ID-040 | Principal identifies accountable human, org, or legal entity | MUST |
| AIAM1-ID-041 | Accountability not delegated to agent or model provider; no principal = no identity claim | MUST |
| AIAM1-ID-042 | Multiple principals require separate, independently verifiable/revocable claims | MUST |
| AIAM1-ID-050 | Identity claims cryptographically signed by verifiable issuing authority | MUST |
| AIAM1-ID-051 | Identity claims have defined validity period; no expiration = reject | MUST |
| AIAM1-ID-052 | Identity claims revocable at any time | MUST |
| AIAM1-ID-053 | Revocation within propagation latency guarantee | MUST |
| AIAM1-ID-054 | Identity lifecycle events produce attestation records | MUST |

### 3.2 Intent (AEGIS_AIAM1_INTENT.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-INT-001 | Every action carries an intent claim; no intent = unauthorized | MUST |
| AIAM1-INT-002 | Intent claim structured (intent_id, goal_ref, action_ref, reasoning_summary, expected_outcome, dependency_refs, timestamp) | MUST |
| AIAM1-INT-003 | Intent claims produced at moment of action; timestamp within tolerance | MUST |
| AIAM1-INT-004 | Reasoning summary structured (trigger, selection_rationale) | MUST |
| AIAM1-INT-010 | Intent validated against goal context (goal_ref match, scope, constraints) | MUST |
| AIAM1-INT-011 | Mismatched goal_ref → DENY | MUST |
| AIAM1-INT-020 | Intent claims preserved in attestation records | MUST |
| AIAM1-INT-021 | Intent claims immutable after production | MUST |
| AIAM1-INT-022 | Intent claims retained for attestation retention period | MUST |
| AIAM1-INT-030 | Sub-agents produce own intent claims; reference parent via dependency_refs | MUST |
| AIAM1-INT-031 | Sub-agent intent independently valid against sub-agent's own identity | MUST |
| AIAM1-INT-050 | Intent claims not reusable across action proposals; reject reused action_ref | MUST NOT reuse |

### 3.3 Authority / IBAC (AEGIS_AIAM1_AUTHORITY.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-AUTH-001 | Authority policies as (identity, action, intent) triples | MUST |
| AIAM1-AUTH-002 | Patterns support exact match, wildcard, set membership, negation, prefix | MUST |
| AIAM1-AUTH-010 | Policies machine-readable | MUST |
| AIAM1-AUTH-011 | Policy evaluation deterministic; no LLM or non-deterministic input | MUST |
| AIAM1-AUTH-012 | Defined policy evaluation order (first-match or most-specific) | MUST |
| AIAM1-AUTH-013 | Default deny; no matching policy → DENY | MUST |
| AIAM1-AUTH-014 | Conflicting decisions: DENY > ESCALATE > REQUIRE_CONFIRMATION > ALLOW | MUST |
| AIAM1-AUTH-020 | Policy changes within bounded propagation latency | MUST |
| AIAM1-AUTH-021 | Policy changes produce attestation records | MUST |
| AIAM1-AUTH-022 | Policies version-controlled; historical state reconstructable | MUST |
| AIAM1-AUTH-023 | Policy authorship governed; agents cannot modify their own policies | MUST |
| AIAM1-AUTH-024 | Mixed delegated + independent authority evaluated as composed action (CAP-010) | MUST |
| AIAM1-AUTH-030 | External trust scores do not override IBAC decisions | MUST NOT |

### 3.4 Capabilities (AEGIS_AIAM1_CAPABILITIES.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-CAP-001 | Capabilities explicitly granted; no grants = no actions | MUST |
| AIAM1-CAP-002 | Grants include grant_id, capability_id, grantee, scope, issued_at, expires_at, issued_by | MUST |
| AIAM1-CAP-003 | Grants time-bounded; expired = nonexistent | MUST |
| AIAM1-CAP-004 | Grants individually revocable | MUST |
| AIAM1-CAP-010 | Composition treated as governed operation | MUST |
| AIAM1-CAP-011 | Non-transitivity: auth(A) + auth(B) ≠ auth(A-then-B) | MUST |
| AIAM1-CAP-012 | At least one composition governance mechanism implemented | MUST |
| AIAM1-CAP-020 | Constraints enforced at every capability exercise | MUST |
| AIAM1-CAP-021 | Constraint violation → DENY (not advisory) | MUST |
| AIAM1-CAP-030 | Composition evaluation over at least the current session | MUST |

### 3.5 Delegation (AEGIS_AIAM1_DELEGATION.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-DEL-001 | Delegation as explicit principal chain | MUST |
| AIAM1-DEL-002 | Each agent identifies its principal | MUST |
| AIAM1-DEL-003 | Top principal remains accountable | MUST |
| AIAM1-DEL-004 | Principal chain obscuration structurally impossible | MUST |
| AIAM1-DEL-010 | Delegated authority narrows monotonically | MUST |
| AIAM1-DEL-012 | Independent grants still recorded in principal chain | MUST |
| AIAM1-DEL-020 | Maximum delegation chain depth defined and published | MUST |
| AIAM1-DEL-021 | Agents at max depth cannot delegate further | MUST |
| AIAM1-DEL-022 | Sub-agent instantiation is a governed action | MUST |
| AIAM1-DEL-023 | Delegation records include delegator, delegatee, capabilities, scope, purpose, expiry, cascade_on_revocation | MUST |
| AIAM1-DEL-024 | Revocation cascade mandatory by default for downstream delegated authority | MUST |
| AIAM1-DEL-025 | Cascade opt-out (`cascade_on_revocation: false`) permitted with attestation, justification, and policy governance | MAY (with MUST conditions) |

### 3.6 Sessions (AEGIS_AIAM1_SESSIONS.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-SES-001 | Sessions as first-class governance boundaries | MUST |
| AIAM1-SES-002 | Sessions bounded by four dimensions (goal, time, capabilities, accountability) | MUST |
| AIAM1-SES-003 | Session record includes session_id, agent_id, goal_ref, started_at, expires_at, capability_envelope, principal_chain, status | MUST |
| AIAM1-SES-010 | Actions outside active session → unauthorized | MUST |
| AIAM1-SES-011 | Session terminates on first of: goal completion, time expiry, capability exhaustion, explicit revocation | MUST |
| AIAM1-SES-012 | Session termination: deny subsequent actions, produce attestation, revoke scoped delegations | MUST |
| AIAM1-SES-004 | Maximum session duration published; SHOULD NOT exceed 24h without compensating controls | MUST |
| AIAM1-SES-005 | Sessions not renewable; extension requires new session with new attestation | MUST NOT renew |
| AIAM1-SES-020 | No silent session escalation | MUST NOT |
| AIAM1-SES-021 | Exceeding session boundaries requires new session with new authorization | MUST |

### 3.7 Attestation (AEGIS_AIAM1_ATTESTATION.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-ATT-001 | Every action produces attestation record (including denials) | MUST |
| AIAM1-ATT-002 | Record includes: attestation_id, timestamp, identity, intent, action, decision, rationale, principal_chain, session_ref, capabilities, enforcement_layer, chain_hash, signature | MUST |
| AIAM1-ATT-010 | Records tamper-evident | MUST |
| AIAM1-ATT-011 | Records hash-chained (SHA-256) | MUST |
| AIAM1-ATT-012 | Chain integrity verifiable at any time | MUST |
| AIAM1-ATT-013 | Records append-only; no delete/modify/overwrite | MUST NOT modify |
| AIAM1-ATT-020 | Records signed by enforcement layer | MUST |
| AIAM1-ATT-021 | Signature covers all fields | MUST |
| AIAM1-ATT-022 | Supports Ed25519, ECDSA P-256, or RSA-2048 | MUST (at least one) |
| AIAM1-ATT-023 | Algorithm negotiation and key rotation without invalidating historical chains | SHOULD |
| AIAM1-ATT-030 | Retention policy defined and published | MUST |
| AIAM1-ATT-031 | Retention minimum 1 year | MUST |
| AIAM1-ATT-031a | Referenced claims retained for attestation retention period | MUST |
| AIAM1-ATT-032 | Attestation is primary accountability surface; no substitution with agent logs | MUST NOT substitute |
| AIAM1-ATT-040 | Attestation failure → DENY action (fail-closed) | MUST |

### 3.8 Revocation (AEGIS_AIAM1_REVOCATION.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-REV-001 | Pre-action revocation; revoked = unusable for uncommitted actions | MUST |
| AIAM1-REV-002 | Propagation latency guarantee defined and published | MUST |
| AIAM1-REV-002a | Kill-switch propagation MUST NOT exceed 60 seconds | MUST NOT exceed |
| AIAM1-REV-003 | Propagation measurable and auditable | MUST |
| AIAM1-REV-010 | Revocation operations governed by IBAC | MUST |
| AIAM1-REV-011 | Revocation produces attestation records | MUST |
| AIAM1-REV-012 | Revocation idempotent | MUST |
| AIAM1-REV-020 | Kill-switch available (agent, principal chain, session targeting) | MUST |
| AIAM1-REV-022 | Kill-switch highest priority; non-deferrable | MUST |
| AIAM1-REV-023 | Kill-switch produces CRITICAL attestation | MUST |
| AIAM1-REV-030 | Revocation cascade evaluated for downstream delegations | MUST |
| AIAM1-REV-031 | Delegated capabilities from revoked source are revoked | MUST |
| AIAM1-REV-032 | Independent grants unaffected by upstream revocation | MUST NOT revoke |
| AIAM1-REV-033 | Cascade propagates to full chain depth | MUST |

### 3.9 Interoperability (AEGIS_AIAM1_INTEROPERABILITY.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-IOP-001 | OAuth 2.1 / OIDC authentication without requiring IdP to understand AIAM-1 | MUST |
| AIAM1-IOP-003 | Token mapping from AIAM-1 claims to JWT claims | MUST |
| AIAM1-IOP-004 | Custom claims use `aiam_` prefix | MUST |
| AIAM1-IOP-005 | JWT valid without AIAM-1 claims for non-AIAM resource servers | MUST |
| AIAM1-IOP-010 | Capabilities SHOULD map to OAuth 2.1 scopes | SHOULD |
| AIAM1-IOP-011 | OAuth scopes conflicting with AIAM-1 grants: AIAM-1 registry authoritative | MUST NOT exercise unauthorized scope |
| AIAM1-IOP-050 | Interop mappings do not compromise AIAM-1 primitive integrity | MUST NOT compromise |
| AIAM1-IOP-051 | Governance gateway is authoritative for IBAC; interop protocols are complementary | MUST |

### 3.10 Threat Model (AEGIS_AIAM1_THREAT_MODEL.md)

| ID | Requirement | Type |
|---|---|---|
| AIAM1-TM-001 | Address all eight threat classes; identify defenses and residual risk | MUST |
| AIAM1-TM-003 | Trust scores and security decisions not collapsed into single metric | MUST NOT collapse |

---

## 4. Conformance Statement Format

**AIAM1-CONF-001.** An implementation claiming AIAM-1 v0.1 conformance MUST publish a conformance statement containing:

| Section | Content | Required |
|---|---|---|
| Implementation identity | Name, version, vendor | MUST |
| AIAM-1 version | Specification version claimed | MUST |
| Conformance profile | "Full Conformance" (v0.1 only profile) | MUST |
| Requirement satisfaction | For each MUST/MUST NOT requirement: satisfied, not satisfied, or not applicable (with rationale) | MUST |
| Deviations | For any unsatisfied requirement: rationale and compensating controls | MUST (if any) |
| SHOULD compliance | For each SHOULD requirement: implemented or not (with rationale if not) | SHOULD |
| Implementation notes | Additional context on implementation choices (e.g., policy language, crypto algorithms, propagation latency guarantee value) | SHOULD |
| Date | Date of conformance assessment | MUST |
| Assessor | Who performed the assessment (self or third-party) | SHOULD |

**AIAM1-CONF-002.** Conformance statements MUST reference the specification version and MUST be updated when the implementation changes materially.

**AIAM1-CONF-003.** Conformance statements MUST be publicly accessible to relying parties that need to evaluate whether an implementation meets AIAM-1 requirements.

---

## 5. Testing and Validation

**AIAM1-CONF-010.** AIAM-1 v0.1 does not define a normative test suite. A companion test suite is planned for v0.2.

**AIAM1-CONF-011.** In the interim, conformant implementations SHOULD publish their own validation methodology, including:

- Test coverage against the conformance checklist (§3).
- Test cases for each threat class (§3.10 / THREAT_MODEL).
- Attestation chain integrity verification procedures.
- Revocation propagation latency measurement methodology.
- IBAC policy evaluation determinism verification.

**AIAM1-CONF-012.** Third-party conformance assessment is RECOMMENDED but not required for v0.1.

> **Honesty note:** v0.1 self-attested conformance is a known limitation. Implementations claiming conformance without third-party assessment SHOULD be treated by relying parties as indicative rather than authoritative. A self-attested conformance statement means "we believe we satisfy these requirements and are willing to document that belief publicly." It does not mean "an independent party has verified our claim." A normative test suite is committed for v0.2; until it exists, the gap between self-attestation and verified conformance is real and should be acknowledged by both implementers and relying parties.

---

## 6. Conformance Profile Roadmap

### 6.1 Full Conformance (v0.1 — defined)

The only profile defined in v0.1. Satisfies all MUST and MUST NOT requirements across all chapters.

### 6.2 Research / Individual Profile (v0.2 — planned)

A lightweight profile for individual researchers, students, and personal-agent operators. ID-041 ("no principal = no identity claim") is operationally painful for a researcher running a personal agent — the researcher is both operator and principal, and the full composite identity machinery is disproportionate to their governance needs.

The Research / Individual Profile is not defined in v0.1 but is named here as a commitment: AIAM-1 is not enterprise-only by accident. v0.2 will specify a conformance profile that relaxes composite identity requirements for single-user, non-delegating deployments while preserving attestation, revocation, and session governance. The exact relaxations are deferred to v0.2.

### 6.3 Federation Profile (v0.2 — planned)

For deployments participating in cross-organization agent governance. Will require cross-organization delegation primitives (DELEGATION §3.5) and GFN-1 integration.

---

## 7. Version Compatibility

**AIAM1-CONF-030.** Conformance is version-specific. An implementation conformant to AIAM-1 v0.1 is not automatically conformant to future versions. Each version requires its own conformance assessment.

**AIAM1-CONF-031.** Future AIAM-1 versions SHOULD maintain backward compatibility with v0.1 conformant implementations where feasible. Breaking changes MUST be documented in the version's changelog with migration guidance.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — Finnoybu IP LLC*

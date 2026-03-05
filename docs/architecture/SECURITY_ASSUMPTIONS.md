# AEGIS Security Assumptions

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## Purpose

This document captures explicit assumptions required for AEGIS security claims.
Each assumption is paired with verification controls and failure response.

Security assertions are valid only while these assumptions hold.

## Assumption Register

| ID | Assumption | Validation Control | If Violated |
|----|------------|--------------------|-------------|
| SA-01 | Kernel is trusted and uncompromised | Host attestation, patch baseline, EDR telemetry | Enter safe mode, halt high-risk capabilities |
| SA-02 | Cryptography is correctly implemented | Approved algorithms, key rotation, TLS policy checks | Invalidate sessions, rotate keys, deny execution |
| SA-03 | Policy store integrity is preserved | Signed policy bundles, checksum verification, immutable logs | Reject policy load, revert to last known-good |
| SA-04 | Actor identity is attributable | Strong auth, non-repudiable IDs, token validation | Deny unauthenticated requests |
| SA-05 | Governance path cannot be bypassed | Network segmentation, proxy-only execution path, eBPF/OS controls | Fail closed and alert |
| SA-06 | Time source is trustworthy | NTP hardening, drift monitoring | Mark audit data degraded, escalate decisions |
| SA-07 | Audit store is durable and tamper-evident | WORM/append-only logs, replication checks | Switch to emergency deny mode if durability is lost |
| SA-08 | Runtime dependencies are trusted | SBOM + signature verification + pinned versions | Block startup and require operator intervention |

## Core Security Assumptions

### SA-01 Kernel and Host Integrity

Assumption:

- The OS kernel and host runtime are trusted.

Required controls:

- Hardened baseline (CIS or equivalent).
- Verified boot / secure boot when available.
- Continuous host monitoring for tamper indicators.

Failure behavior:

- Governance Engine enters restrictive mode.
- Only explicitly break-glass capabilities remain available.

### SA-02 Cryptographic Integrity

Assumption:

- Cryptographic operations (signing, verification, encryption) are sound.

Required controls:

- Minimum TLS 1.2+ with modern cipher suites.
- Key rotation policy and revocation support.
- Signature verification for policy/config bundles.

Failure behavior:

- Reject unauthenticated policy/config artifacts.
- Deny requests requiring untrusted cryptographic channels.

### SA-03 Policy Authenticity and Integrity

Assumption:

- Policies are authentic, versioned, and protected from unauthorized changes.

Required controls:

- Signed policy artifacts.
- Two-person review for policy changes.
- Immutable policy audit trail.

Failure behavior:

- Refuse policy activation.
- Revert to last known-good policy set.

### SA-04 Identity and Attribution

Assumption:

- Every request can be tied to a verifiable actor identity.

Required controls:

- Non-shared credentials.
- Expiring tokens with audience restrictions.
- Request-level correlation IDs.

Failure behavior:

- Default deny for unverified identity.

### SA-05 Governance Engine Isolation

Assumption:

- No actor can execute privileged capability without passing governance.

Required controls:

- Tool Proxy as mandatory execution path.
- Firewall and service mesh policy denying direct backend access.
- Runtime checks for bypass attempts.

Failure behavior:

- Block direct execution path.
- Emit high-severity security alert.

## Assumption Monitoring

Each assumption MUST have health signals.

Examples:

- `host_integrity_ok` (boolean)
- `policy_signature_valid` (boolean)
- `audit_replication_lag_seconds` (numeric)
- `identity_validation_failures_total` (counter)

Any critical signal entering failed state SHOULD trigger incident workflow.

## Break-Glass Model

Break-glass capability is allowed only under strict controls:

- Time-limited elevation.
- Human approval and multi-party acknowledgment.
- Full audit capture and post-incident review.

Break-glass is an exception path, not a standard operating mode.

## Residual Risk Acknowledgment

Even with assumptions validated, residual risk remains:

- Zero-day kernel compromise.
- Insider misuse of privileged policy administration.
- Supply-chain compromise of trusted dependencies.

AEGIS mitigates but does not eliminate systemic risk.

## Review Cadence

This document MUST be reviewed:

- On every major architecture release.
- After security incidents.
- At least quarterly as part of governance review.

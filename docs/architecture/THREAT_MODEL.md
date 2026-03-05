# AEGIS Threat Model

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## Purpose

This document defines threat actors, attack paths, and control strategies for
the AEGIS governance architecture.

Security objective: prevent unauthorized capability execution while preserving
deterministic, auditable governance behavior.

## Protected Assets

Critical assets:

- Policy definitions and policy history.
- Capability registry and grants.
- Governance decision path and decision integrity.
- Audit records and replay evidence.
- Identity credentials and trust metadata.
- Tool Proxy execution channel.

## Threat Actors

| Actor | Motivation | Typical Capability |
|-------|------------|--------------------|
| Malicious external actor | Data theft, disruption | API exploitation, credential abuse |
| Compromised internal agent | Privilege escalation | Policy probing, lateral movement |
| Insider with elevated access | Unauthorized policy changes | Direct config modification |
| Supply-chain attacker | Persistence, covert control | Dependency or artifact tampering |

## Attack Surfaces

- AGP request ingress API.
- Policy management plane.
- Capability grant/revoke plane.
- Tool Proxy call execution path.
- Audit storage and retrieval interfaces.
- CI/CD path for policy and runtime updates.

## Priority Threat Scenarios

### T1: Governance Bypass

Scenario:

- Agent attempts direct infrastructure call, skipping Governance Engine.

Impact:

- Unauthorized execution without policy/risk evaluation.

Controls:

- Enforce proxy-only network paths.
- Block direct backend routes via firewall/service mesh.
- Runtime detection and denial for bypass signatures.

### T2: Policy Tampering

Scenario:

- Adversary modifies policy files to allow forbidden capabilities.

Impact:

- Systematic privilege escalation.

Controls:

- Signed policies and verified provenance.
- Two-person approval for policy changes.
- Immutable policy change log and automatic diff alerts.

### T3: Identity Spoofing

Scenario:

- Attacker reuses tokens or forges identity claims.

Impact:

- Malicious actions attributed to trusted actors.

Controls:

- Short-lived credentials with audience restriction.
- mTLS between components.
- Nonce/replay protection and strict token validation.

### T4: Audit Log Manipulation

Scenario:

- Adversary deletes or edits evidence to hide policy violations.

Impact:

- Loss of accountability and forensics.

Controls:

- Append-only storage and tamper-evident hash chaining.
- Replicated audit sink.
- Periodic reconciliation jobs with integrity proofs.

### T5: Coordinated Low-Risk Abuse

Scenario:

- Multiple agents execute individually low-risk actions that combine into
	high-impact behavior.

Impact:

- Slow-burn exfiltration or distributed policy evasion.

Controls:

- Cross-agent correlation analytics.
- Sliding-window aggregate risk checks.
- Escalation triggers on coordinated patterns.

### T6: Model/Tool Prompt Injection

Scenario:

- Malicious input attempts to coerce agent behavior toward unsafe capability use.

Impact:

- Elevated volume of risky action proposals.

Controls:

- Governance remains out-of-band and deterministic.
- Prompt content is never an authorization source.
- Policy/risk checks remain mandatory before execution.

## STRIDE Mapping

| STRIDE | Example in AEGIS | Primary Controls |
|--------|-------------------|------------------|
| Spoofing | Forged `agent_id` token | Strong identity, mTLS, token validation |
| Tampering | Policy file modification | Signatures, immutable logs, approvals |
| Repudiation | Denied action claim disputes | Audit immutability, trace IDs |
| Information Disclosure | Unauthorized data reads | Capability scoping, deny policies |
| Denial of Service | Flood decision endpoint | Rate limits, queue isolation, backpressure |
| Elevation of Privilege | Bypass governance path | Proxy enforcement, default deny |

## Risk Prioritization

Top risks requiring continuous validation:

1. Governance bypass (critical).
2. Policy tampering (critical).
3. Identity spoofing (high).
4. Coordinated multi-agent abuse (high).

## Required Security Tests

Minimum threat-model test suite:

- Bypass simulation: direct execution path must fail.
- Policy tamper test: unsigned policies must be rejected.
- Identity replay test: expired/reused tokens denied.
- Audit integrity test: tampering attempts detected.
- Coordinated behavior test: aggregate risk escalation triggered.

## Detection and Response

Mandatory detections:

- `governance_bypass_attempt_total`
- `policy_signature_failure_total`
- `identity_validation_failure_total`
- `audit_integrity_mismatch_total`
- `coordinated_risk_escalations_total`

Incident response triggers:

- Any confirmed bypass attempt.
- Repeated policy integrity failures.
- Audit tampering indication.

## Residual Risks

Residual risks remain for:

- Zero-day vulnerabilities in trusted components.
- Insider abuse under legitimate credentials.
- Novel attack chains outside known signatures.

Mitigation for residual risks depends on layered controls and rapid response.

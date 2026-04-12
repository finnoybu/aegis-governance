---
title: "AEGIS Reference Monitor Model"
description: "Reference monitor model — mandatory mediation at execution boundary"
---

# AEGIS Reference Monitor Model

### Architectural Enforcement & Governance of Intelligent Systems

**Version**: 0.2\
**Status**: Informational\
**Part of**: AEGIS Architecture\
**Author**: Kenneth Tannenbaum\
**Last Updated**: March 6, 2026

---

## Purpose

This document defines AEGIS as a modern reference monitor for AI-generated
actions, applying classical monitor properties[^1] to policy and risk-governed
capability control.

## Classical Properties (Normative)

AEGIS MUST satisfy these properties:

1. Complete mediation: every protected action request passes governance.
2. Tamper resistance: monitor state and decision path cannot be altered by
   untrusted actors.
3. Verifiability: monitor behavior is deterministic and testable.

If any property fails, the system is not operating as a valid reference monitor.

*These three properties — complete mediation, tamper resistance, and verifiability — are the canonical requirements for a reference monitor as defined by Anderson.[^1] The formal framework for proving that a monitor correctly enforces a given security policy is established by Schneider's security automata theory: only safety policies are inline-enforceable, and composition of automata produces the conjunction of their enforced policies.[^2]*

## AEGIS Monitor Placement

```
Agent/Application -> AEGIS Governance Monitor -> Tool Proxy -> OS Controls
```

Monitor boundary sits between action proposal and execution.

## Monitored Objects

- Capability requests.
- Policy artifacts.
- Capability grants.
- Risk inputs and score outputs.
- Execution grants and constraint envelopes.
- Audit records.

## Policy Decision Model

The monitor returns one of four outcomes:

- `ALLOW`
- `CONSTRAIN`
- `ESCALATE`
- `DENY`

Decision outcomes are deterministic functions of request, policy version,
capability grants, and contextual risk inputs.[^2]

## Tamper Resistance Strategy

Required controls:

- Signed policy bundles and integrity verification.
- Restricted write access to capability registry.
- Proxy-enforced execution path (no direct backend access).
- Immutable audit storage with integrity checks.

## Verifiability Strategy

Required checks:

- Deterministic replay of golden decision set.
- Policy precedence conformance tests.
- Boundary bypass simulation tests.
- Fault-injection tests proving fail-closed behavior.

## Relationship to Kernel Security

AEGIS does not replace kernel controls. It complements them:

- AEGIS decides whether and how actions are allowed.
- Kernel enforces low-level process and resource controls.

This separation preserves system stability while adding governance semantics.

## Monitor Invariants

1. No direct execute path around governance.
2. No unsigned policy may affect decisions.
3. No execution without prior audit-linked decision.
4. No invalid request may produce allow.

## Security Benefits

Using a reference monitor model in AEGIS provides:

- Bounded authority for AI agents.
- Strong accountability and forensics.
- Consistent enforcement under operational stress.
- Clear assurance story for auditors and operators.

---

## References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../../REFERENCES.md).

[^2]: F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security (TISSEC)*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382. See [REFERENCES.md](../../REFERENCES.md).

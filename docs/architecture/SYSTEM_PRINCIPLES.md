# AEGIS System Principles

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## Purpose

These principles are normative architecture rules for AEGIS. They define what
must remain true for the system to be secure, governable, and auditable.

## P1: Bounded Capability

Rule:

- No actor may exercise capability outside explicitly authorized scope.

Implementation check:

- Capability + resource + scope must be validated before execution.

## P2: Complete Mediation

Rule:

- Every capability invocation must pass governance evaluation.

Implementation check:

- No direct execution path from agent layer to infrastructure.

## P3: Default Deny

Rule:

- Absence of explicit authorization is treated as denial.

Implementation check:

- No policy match results in `DENY`.

## P4: Deterministic Governance

Rule:

- Same input + policy version + context yields same decision.

Implementation check:

- Replay test corpus has zero decision mismatches.

## P5: Auditability

Rule:

- Every decision and execution must have immutable evidence.

Implementation check:

- Execution event without prior audit ID is treated as policy violation.

## P6: Explicit Authority Boundaries

Rule:

- Governance authority and execution authority are separate.

Implementation check:

- Decision Engine authorizes; Tool Proxy executes; neither role is conflated.

## P7: Fail-Closed Safety

Rule:

- System uncertainty or subsystem failure must not produce implicit allow.

Implementation check:

- Error paths return `ESCALATE` or `DENY`.

## P8: Least Privilege by Construction

Rule:

- Runtime permissions are narrowed to minimum required scope and duration.

Implementation check:

- Constrained decisions carry enforceable limits (time, rate, target, size).

## P9: Policy Integrity

Rule:

- Authorization logic depends only on authenticated policy artifacts.

Implementation check:

- Unsigned or modified policy bundles are rejected.

## P10: Human Accountability for Exceptions

Rule:

- Break-glass or escalated paths require accountable human oversight.

Implementation check:

- Escalation approvals are attributable and fully audited.

## Principle Compliance Review

Each release SHOULD include a principle compliance checklist proving:

- No mediation bypass.
- Deterministic replay parity.
- Immutable audit linkage.
- Fail-closed behavior under injected failures.

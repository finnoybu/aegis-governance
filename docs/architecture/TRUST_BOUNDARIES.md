# AEGIS Trust Boundaries

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## Purpose

Trust boundaries define where authority changes and where controls MUST be
applied to prevent capability escalation.

Any transition across trust levels requires explicit validation and audit.

## System Trust Zones

| Zone | Description | Trust Level |
|------|-------------|-------------|
| Z0 | External inputs (users, APIs, internet) | Untrusted |
| Z1 | Application and agent runtime | Partially trusted |
| Z2 | AEGIS Governance Engine + Policy/Risk evaluation | Trusted control plane |
| Z3 | Tool Proxy execution channel | Trusted execution gateway |
| Z4 | OS kernel and infrastructure | Trusted executor |

## Primary Boundary Map

```
Z0 External Input
 -> Z1 Application/Agent
 -> [Boundary B1: Governance Admission]
 -> Z2 Governance Engine
 -> [Boundary B2: Execution Authorization]
 -> Z3 Tool Proxy
 -> [Boundary B3: System Capability Invocation]
 -> Z4 OS/Infrastructure
```

## Boundary Contracts

### B1: Governance Admission Boundary (Z1 -> Z2)

Purpose:

- Ensure every action proposal becomes a governed request.

Required checks:

- Request schema validation.
- Actor identity validation.
- Capability name normalization.
- Correlation ID assignment.

Required outputs:

- Accepted request for evaluation OR immediate deny with reason.

### B2: Execution Authorization Boundary (Z2 -> Z3)

Purpose:

- Convert decision output into enforceable runtime policy.

Required checks:

- Decision is one of: ALLOW, CONSTRAIN, ESCALATE, DENY.
- Constraints are machine-readable and complete when required.
- Audit record exists before execution handoff.

Required outputs:

- Signed execution grant for ALLOW/CONSTRAIN.
- No grant for ESCALATE/DENY.

### B3: System Invocation Boundary (Z3 -> Z4)

Purpose:

- Enforce least privilege at execution time.

Required checks:

- Tool call matches approved capability and resource scope.
- Runtime constraints are active (rate, timeout, size, target).
- Privileged operations are blocked unless explicitly granted.

Required outputs:

- Executed operation with telemetry OR blocked operation with violation event.

## Non-Negotiable Boundary Rules

1. No direct Z1 -> Z4 execution path is permitted.
2. Governance decisions are mandatory for all capability invocations.
3. Default behavior on boundary uncertainty is deny or escalate.
4. Boundary crossing must always be auditable.

## Data Classification at Boundaries

| Data Type | Allowed Crossing | Control |
|-----------|------------------|---------|
| Policy definitions | Z2 internal only | Signed artifacts + approval workflow |
| Credentials/tokens | Z0/Z1 -> Z2 only | Validation, expiry, redaction |
| Execution commands | Z2 -> Z3 only | Decision grant + constraint envelope |
| Raw system secrets | Never exposed to Z0/Z1 | Secret manager + deny policy |
| Audit records | Write from Z2/Z3, read controlled | Immutable storage + RBAC |

## Control Matrix by Boundary

| Boundary | Preventive Controls | Detective Controls |
|----------|---------------------|--------------------|
| B1 | Schema validation, authn/authz, rate limiting | Invalid request metrics, auth failure alerts |
| B2 | Deterministic decision rules, signed grants | Decision replay parity checks |
| B3 | Runtime sandboxing, policy-constrained execution | Violation telemetry, drift detection |

## Boundary Failure Modes

### Admission Failure (B1)

- Response: immediate `DENY`.
- Action: log validation failure, increment abuse counters.

### Decision Transfer Failure (B2)

- Response: fail closed (no execution grant).
- Action: escalate to operator if repeated.

### Execution Drift (B3)

- Response: terminate operation and record violation.
- Action: increase actor risk and evaluate temporary capability suspension.

## Verification Checklist

Boundary verification should prove:

- No bypass path exists around Z2.
- All execution events map to prior audit decision IDs.
- Constraints observed at runtime match constraints issued at decision time.
- Denied requests never produce downstream side effects.

## Related Specifications

- `docs/architecture/GOVERNANCE_ENGINE_SPEC.md`
- `docs/architecture/GOVERNANCE_ENGINE_COMPONENTS.md`
- `docs/architecture/POLICY_MATCHING_AND_DEBUG.md`
- `docs/architecture/END_TO_END_REQUEST_FLOW.md`

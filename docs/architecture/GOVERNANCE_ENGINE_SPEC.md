# AEGIS Governance Engine Specification

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## Purpose

The Governance Engine is the deterministic policy decision authority for AEGIS.
It evaluates every capability request before any infrastructure interaction.

Core rule:

1. AI proposes action.
2. Governance Engine evaluates action.
3. Only approved actions execute.

## Scope

This specification defines:

- Required input/output contract for authorization.
- Deterministic evaluation pipeline.
- Decision semantics and constraints behavior.
- Audit requirements and failure handling.
- Operational SLOs and verification criteria.

Detailed algorithms and schemas are defined in:

- `docs/architecture/DECISION_ALGORITHM.md`
- `docs/architecture/POLICY_LANGUAGE.md`
- `docs/architecture/RISK_SCORING_ALGORITHM.md`
- `docs/architecture/CAPABILITY_SCHEMA.md`
- `docs/architecture/GOVERNANCE_ENGINE_COMPONENTS.md`

## External Interface

### Authorization Method

```python
authorize(request: AGPRequest) -> AGPResponse
```

### Input Contract (AGPRequest)

Required fields:

- `request_id: str`
- `agent_id: str`
- `capability: str`
- `resource: str`
- `context: dict`

Validation requirements:

- Missing required fields MUST return `DENY` with validation reason.
- Unknown capability MUST return `DENY`.
- Malformed request MUST NOT be executed.

### Output Contract (AGPResponse)

Required fields:

- `decision: ALLOW | DENY | CONSTRAIN | ESCALATE`
- `reason: str`
- `audit_id: str | null`
- `risk_score: int | null`
- `constraints: dict | null`
- `decision_latency_ms: int`

## Deterministic Evaluation Pipeline

Execution order is fixed and MUST NOT vary by request type:

1. Validate request structure.
2. Verify agent capability grant.
3. Match policies (priority ordered).
4. Apply policy precedence rules.
5. Compute risk score.
6. Apply threshold mapping.
7. Attach constraints if required.
8. Emit immutable audit record.
9. Return response.

If any stage fails internally, engine MUST fail closed (`ESCALATE` or `DENY`).

## Decision Semantics

### `ALLOW`

- Request is approved with no additional runtime restrictions.
- Tool Proxy executes request directly.

### `CONSTRAIN`

- Request is approved with mandatory runtime restrictions.
- Constraints MUST be machine-readable and enforceable.
- Execution without constraints is forbidden.

### `ESCALATE`

- Request requires secondary authority (human or higher governance node).
- No execution occurs until escalation resolves to `ALLOW` or `DENY`.

### `DENY`

- Request is rejected and MUST NOT execute.
- Response includes explicit denial reason.

## Policy Precedence Rules

When multiple policies match:

1. Explicit `DENY` always wins.
2. Remaining policies are sorted by descending priority.
3. First matching non-deny policy determines base effect.
4. If no policies match, default decision is `DENY`.

## Risk Integration

Risk scoring is mandatory unless early denied by policy/capability check.

Threshold mapping:

- `0-30`: ALLOW
- `31-60`: CONSTRAIN
- `61-80`: ESCALATE
- `81-100`: DENY

Risk score and factor breakdown SHOULD be attached to audit records.

## Audit Requirements

Each request MUST produce an immutable audit event containing:

- Request identity and timestamp.
- Inputs used for decision.
- Matched policies.
- Risk score and factor breakdown.
- Final decision and rationale.
- Applied constraints (if any).
- Evaluation latency and outcome status.

Audit writes MUST be durable before returning success.

## Failure Handling

### Internal Component Failure

- Policy engine unavailable: `ESCALATE`.
- Risk engine unavailable: `ESCALATE`.
- Audit system unavailable: `DENY` unless configured write-behind buffer is healthy.

### Timeout Handling

- Evaluation timeout MUST fail closed.
- Default timeout target: 250 ms.
- Timeout decisions MUST be auditable.

### Data Integrity Failures

- Corrupt policy set or capability registry MUST trigger degraded safe mode.
- Safe mode behavior: deny all non-break-glass capabilities.

## Operational SLOs

Target service objectives:

- P50 decision latency: <= 20 ms
- P95 decision latency: <= 75 ms
- P99 decision latency: <= 150 ms
- Audit write success rate: >= 99.99%
- Deterministic replay mismatch rate: 0%

## Verification and Test Criteria

Required test classes:

- Unit tests for each stage of evaluation.
- Property tests for precedence and threshold boundaries.
- Replay tests proving deterministic outcomes.
- Failure-injection tests (policy, risk, audit outages).
- Concurrency tests for consistent outcomes under load.

Release gate criteria:

- No critical policy bypass defects.
- Deterministic replay parity for golden test set.
- End-to-end tests for ALLOW, CONSTRAIN, ESCALATE, DENY.

## Security Posture

The Governance Engine enforces capability-based authorization and default-deny
semantics. No capability may execute unless explicitly authorized by policy and
risk evaluation within defined trust boundaries.

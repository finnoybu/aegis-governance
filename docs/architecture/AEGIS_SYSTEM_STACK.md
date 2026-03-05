# AEGIS Architecture

## System Stack

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## Purpose

This stack model defines layer boundaries, responsibilities, and control points
for governed capability execution.

## Layered Stack

```
L0  External Input (human/API/scheduler)
L1  Application Layer
L2  Agent/AI Reasoning Layer
L3  AEGIS Governance Layer
L4  Tool Proxy Execution Layer
L5  Operating System / Platform Layer
L6  Hardware / Infrastructure Layer
```

## Layer Responsibilities

### L0 External Input

- Submit intents/tasks.
- No direct execution rights.

### L1 Application Layer

- Orchestrates workflows and user-facing behavior.
- Converts external intents into agent tasks.

### L2 Agent/AI Layer

- Produces candidate actions (proposals only).
- Cannot authorize or execute privileged capability directly.

### L3 AEGIS Governance Layer

- Validates request schema and identity.
- Evaluates policy and risk.
- Produces deterministic decision outcome.
- Emits immutable audit records.

### L4 Tool Proxy Layer

- Executes only governance-approved actions.
- Enforces runtime constraints (timeout, rate, scope, resource).
- Records execution telemetry and violations.

### L5 OS/Platform Layer

- Process, memory, filesystem, and network primitives.
- Enforced by least-privilege runtime profile.

### L6 Hardware/Infrastructure Layer

- Physical compute, storage, and network resources.

## Inter-Layer Control Gates

| Gate | Transition | Required Control |
|------|------------|------------------|
| G1 | L2 -> L3 | Schema + identity validation |
| G2 | L3 -> L4 | Signed decision grant + constraints |
| G3 | L4 -> L5 | Runtime policy enforcement |
| G4 | L5 -> L6 | Platform-native security controls |

## Forbidden Paths

These paths are explicitly prohibited:

- L2 -> L5 direct execution.
- L1/L2 direct write access to policy store.
- L0 direct access to capability registry internals.

Violations MUST be denied and audited.

## Operational Metrics by Layer

- L3: decision latency, deny rate, escalation rate, replay parity.
- L4: constraint violation count, execution success rate.
- L5: privileged call count, sandbox escape attempts.

## Design Outcome

The stack ensures intelligence can propose, but only governance can authorize,
and only constrained execution paths can invoke capability.

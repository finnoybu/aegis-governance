# AEGIS Specification Pack (SOC Implementation)

## Core Components

- Governance Gateway
- Decision Engine
- Capability Registry
- Policy Engine
- Tool Proxy Layer
- Audit Infrastructure

## Core Principle

AI systems may propose actions, but **AEGIS decides whether those actions are allowed**.

## Example Capability Registry Entry

telemetry.query:
  description: Query security telemetry data
  sensitivity: low
  approval_required: false

notify.send:
  description: Send incident notification
  sensitivity: medium
  constraints:
    template_required: true

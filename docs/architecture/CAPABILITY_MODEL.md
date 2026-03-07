# AEGIS™ Capability Model

### Architectural Enforcement & Governance of Intelligent Systems

**Version**: 0.2\
**Status**: Informational\
**Part of**: AEGIS™ Architecture\
**Author**: Kenneth Tannenbaum\
**Last Updated**: March 6, 2026

---

## Purpose

The capability model defines how requested actions are represented,
authorized, constrained, and executed under governance.

Every executable action is expressed as a capability request.

## Capability Definition

A capability is a typed permission for a specific action domain.

Format:

- `<domain>.<operation>[.<suboperation>]`

Examples:

- `filesystem.read`
- `network.http_post`
- `data.database_query`
- `compute.process_spawn`

## Request Contract

Minimum capability request fields:

- `agent_id`
- `capability`
- `resource`
- `scope`
- `context`

Full schema reference:

- `docs/architecture/CAPABILITY_SCHEMA.md`

## Capability Lifecycle

1. Define capability in registry.
2. Grant capability to eligible actors.
3. Receive request for capability use.
4. Evaluate policy and risk.
5. Return decision (`ALLOW`, `CONSTRAIN`, `ESCALATE`, `DENY`).
6. Enforce decision at Tool Proxy.
7. Record immutable audit event.

## Capability Categories

| Category | Examples | Typical Risk Profile |
|----------|----------|----------------------|
| Filesystem | `filesystem.read`, `filesystem.write` | Low to medium |
| Network | `network.http_get`, `network.http_post` | Low to high |
| Data | `data.database_query`, `data.api_call` | Medium to high |
| Compute | `compute.process_spawn` | High |
| Configuration | `system.config_update` | High to critical |

## Enforcement Semantics

### Allow

- Request proceeds without added constraints.

### Constrain

- Request proceeds with required limits (rate, timeout, scope, size).

### Escalate

- Request requires secondary authority before execution.

### Deny

- Request is blocked; no execution is permitted.

## Capability Scope Model

Scope is mandatory for containment and least privilege.

Examples:

- `single_file`
- `directory`
- `read_only`
- `append_only`
- `subprocess`

Scope MUST be enforceable by runtime controls, not advisory metadata.

## Capability Grant Model

Grant rules:

- Grants are actor-specific and revocable.
- Missing grant yields immediate deny.
- Temporary grants must include expiration metadata.

Bulk grant and revoke operations must preserve audit history.

## Safety Invariants

1. No execution without a capability request.
2. No capability request without identity attribution.
3. No privileged scope without explicit policy support.
4. No unresolved escalation may execute.

## Verification Criteria

- Unknown capability requests always denied.
- Revoked capabilities cannot be used.
- Scope constraints enforced at runtime.
- Every execution maps to capability + decision + audit ID.

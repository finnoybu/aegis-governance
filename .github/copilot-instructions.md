# AEGIS™ Copilot Instructions

**Document**: copilot-instructions.md\
**Version**: 2.0.0 (Operational)\
**Part of**: AEGIS Development Tooling\
**Last Updated**: March 7, 2026

---

This repository defines the architecture and reference implementation
for AEGIS™ (Architectural Enforcement & Governance of Intelligent Systems).

AEGIS is a governance runtime for AI systems that enforces deterministic
control over AI-generated actions before they interact with infrastructure.

## Core Flow

1. AI systems propose actions (ACTION_PROPOSE)
2. AEGIS evaluates those actions (Decision Engine)
3. Only approved actions are executed (ACTION_RESULT: ALLOW/DENY/ESCALATE/REQUIRE_CONFIRMATION)

## Key Components

- **Governance Gateway** - Entry point for all governance requests
- **Decision Engine** - Central evaluator coordinating capability and policy checks
- **Capability Registry** - Defines what actions exist and actor permissions
- **Policy Engine** - Evaluates context-based authorization policies
- **Tool Proxy Layer** - Intercepts and governs tool invocations
- **Audit System** - Non-negotiable logging of all governance decisions

---

## Critical Design Decisions

### Capability Registry Queried BEFORE Policy Engine

Decision Engine must validate actor has capability before evaluating policies.

**Rationale**: Capability-based security model - no capability = no policy evaluation needed.\
**See**: RFC-0001 Section 4.2, AEGIS_Reference_Architecture.md

### Audit Events ALWAYS Logged (Even for DENY)

Audit trail is a non-negotiable security requirement.

**Never skip audit logging for performance** - this violates ATM-1 security properties.\
**See**: AEGIS_ATM1_MITIGATIONS.md

### `ACTION_PROPOSE` Must Always Produce `ACTION_RESULT`

No exceptions, even on internal errors.

**Return DENY + ERROR_CODE rather than throwing/crashing**.\
**See**: AEGIS_AGP1_MESSAGES.md

---

## Non-Negotiable Invariants

### 1. Policy Evaluation Must Be Deterministic

- No randomness, no time-based decisions without explicit temporal policy
- Same inputs → same outputs, always
- **See**: AEGIS_AGP1_POLICY_EVALUATION.md

### 2. Never Bypass Capability Registry

- Even for "trusted" or "admin" actors - trust model requires verification
- No shortcuts, no "development mode" bypasses
- **See**: AEGIS_Manifesto.md - "Capability without constraint is not intelligence™"

### 3. Fail Closed by Default

- **Unknown capability** → DENY
- **Policy evaluation error** → DENY
- **Audit logging failure** → BLOCK execution (non-negotiable)
- **Network timeout** → depends on operation (see RFC-0002 Section 6)

**Default: fail closed. Never assume safety.**

---

## Critical Terminology

### Actor vs Agent

- **Actor** = Any entity making requests (human, AI, or system)
- **Agent** = Specifically an AI system (agentic behavior)

### Capability vs Permission

- **Capability** = What tool/action the actor CAN invoke (registry-defined)
- **Permission** = Policy-based authorization for specific context (runtime-evaluated)

### ESCALATE vs REQUIRE_CONFIRMATION

- **ESCALATE** = Send to human decision-maker for override/denial
- **REQUIRE_CONFIRMATION** = Execute only after explicit human approval

### Protocol References

- **AGP** = AEGIS Governance Protocol (wire format)
- **ATM** = AEGIS Threat Model (security analysis)
- **GFN** = Governance Federation Network (future: distributed governance)

---

## Common Pitfalls

### ❌ DON'T: Implement "Admin Override" That Skips Governance

**WHY**: Violates core principle - "capability without constraint is not intelligence"\
**SEE**: AEGIS_Manifesto.md, ATM-1 Attack Vector A7 (privilege escalation)

### ❌ DON'T: Cache Policy Decisions Longer Than 1 Second

**WHY**: Risk context changes between decision and execution\
**SEE**: AEGIS_AGP1_POLICY_EVALUATION.md Section 5.3

### ❌ DON'T: Log Sensitive Parameters in ACTION_PROPOSE

**WHY**: Audit logs must be sanitized - see ATM-1 threat actor profile A3\
**SEE**: AEGIS_ATM1_ATTACK_VECTORS.md

### ❌ DON'T: Use Exceptions for Control Flow in Governance Logic

**WHY**: Decision path must be explicit and auditable\
**INSTEAD**: Return typed Result objects (ALLOW/DENY/ESCALATE)

---

## Quick Reference

### Primary Specifications

- **Message schemas**: [aegis-core/protocol/AEGIS_AGP1_MESSAGES.md](../aegis-core/protocol/AEGIS_AGP1_MESSAGES.md)
- **Risk scoring algorithm**: [aegis-core/protocol/AEGIS_AGP1_RISK_SCORING.md](../aegis-core/protocol/AEGIS_AGP1_RISK_SCORING.md)
- **Component architecture**: [aegis-core/architecture/AEGIS_Reference_Architecture.md](../aegis-core/architecture/AEGIS_Reference_Architecture.md)
- **Policy DSL syntax**: [aegis-core/protocol/AEGIS_AGP1_POLICY_EVALUATION.md](../aegis-core/protocol/AEGIS_AGP1_POLICY_EVALUATION.md)
- **Threat vectors**: [aegis-core/threat-model/AEGIS_ATM1_ATTACK_VECTORS.md](../aegis-core/threat-model/AEGIS_ATM1_ATTACK_VECTORS.md)

### Runtime Implementation

- **Python runtime**: [aegis-runtime/](../aegis-runtime/)
- **Integration examples**: [examples/](../examples/)

---

## Implementation Order for New Features

When implementing new governance features:

1. **Check threat model first** (ATM-1) - What attacks does this expose?
2. **Design capability definition** - What's the narrowest scope?
3. **Define policy evaluation** - What contexts require denial?
4. **Implement audit logging** - What evidence is needed for compliance?
5. **Add tests for DENY cases first**, then ALLOW cases

---

## Code Generation Preferences

### ✅ DO

- Use typed dataclasses for all protocol messages
- Validate inputs with Pydantic models or similar
- Return explicit Result types (not exceptions for control flow)
- Add docstrings citing spec sections: `"Implements AGP-1 Section 4.2"`
- Include type hints on all functions
- Write security-focused tests (adversarial inputs, boundary conditions)

### ❌ DON'T

- Suggest "disable governance for development/testing"
- Use `# type: ignore` - fix the type error instead
- Add caching without explicit TTL and invalidation strategy
- Implement authorization without capability checks
- Skip input validation in governance logic

---

## Branch & Commit Conventions

When creating branches or commits, follow the standards defined in [CONTRIBUTING.md](../CONTRIBUTING.md).

### Branch Naming

Use descriptive prefixes:

- `chore/` — Maintenance tasks and housekeeping
- `ci/` — CI/CD workflow changes
- `deps/` — Dependency updates
- `docs/` — Documentation updates
- `feat/` — New features or components
- `fix/` — Bug fixes or corrections
- `rfc/` — RFC specification changes
- `spec/` — Protocol or schema specifications

**Examples:**

```
rfc/add-hardware-attestation
docs/update-federation-architecture
spec/define-audit-event-schema
chore/clean-up-stale-branches
```

### Commit Messages

Use **Conventional Commits** format: `<type>(<scope>): <description>`

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Common Scopes:**

- `agp` — AEGIS Governance Protocol
- `atm` — AEGIS Threat Model
- `gfn` — Governance Federation Network
- `runtime` — Reference runtime implementation
- `deps` — Dependencies
- `rfc-NNN` — Specific RFC document
- `ci` — CI/CD configuration

**Examples:**

```
feat(agp): add message retry mechanism
docs(threat-model): clarify escalation paths
fix(runtime): correct capability lookup order
chore(deps): bump pydantic to 2.6.0
```

---

## Testing Philosophy

### Test Requirements

- **Every DENY path must have a test** - prove we reject malicious actions
- **Test policy evaluation with expired contexts** - time-based failures
- **Mock external dependencies, never governance logic** - core must be pure
- **Fuzz test all ACTION_PROPOSE parameters** - assume adversarial inputs
- **Test audit logging failures** - prove execution blocks when audit fails

---

## Performance Constraints

### Latency Budgets

- **Governance decision**: < 100ms p99 (critical path)
- **Policy evaluation**: < 50ms per policy (or timeout → DENY)
- **Audit logging**: async, never blocks decision
- **Capability lookup**: < 10ms (in-memory registry)

**If you can't meet the budget, escalate - don't optimize away security.**

---

## Flag for Human Review

Suggest human review when code changes involve:

- Adding new governance bypass conditions
- Changing risk scoring algorithms
- Modifying audit log formats (compliance impact)
- Introducing non-determinism in policy evaluation
- Performance optimizations that touch security boundaries
- New capability definitions with broad scope

---

## When Rules and Urgency Conflict

### Exception Request Protocol

If asked to violate AEGIS principles (e.g., "bypass capability checks," "skip this audit event"):

1. **Acknowledge the request** - Don't be rigid or dismissive
2. **Disclose consequences** - What could go wrong? What becomes harder to fix later?
3. **Suggest mitigations** - If they proceed, what should they also do?
4. **Document the decision** - Note in code/comments that this was an informed exception
5. **Flag for review** - Suggest this get revisited/cleaned up
6. **Enable the decision** - If they choose to proceed knowing costs, do it

### Example

**Request**: "Just skip the policy evaluation for this actor, we're behind schedule"

**Response**: "Understood. Before you do, know:
- This actor could invoke ANY capability without authorization
- If they invoke something unintended, there's no audit trail
- Other actors will request the same bypass
- Recovery requires code changes + redeployment

**Mitigations**: If you proceed:
- Add a time-limited flag (expires in 48 hours)
- Log this decision + timestamp in DECISIONS.md
- Create a ticket to re-implement proper authorization
- I'll flag this for code review

Ready to proceed?"

---

## When Principles Conflict

### Principle Hierarchy

When foundational AEGIS principles come into tension, resolve them in this order:

1. **Auditing** (non-negotiable) - Audit trail is the evidence of governance
2. **Fail Closed** - Conservative defaults protect against unknown attacks
3. **Determinism** (policy evaluation consistency) - Predictability enables verification
4. **Capability Model** - Explicit grants are foundational to trust
5. **Speed/Performance** - Optimize this last, never at the cost of principles 1-4

### Decision Framework

- **Speed vs Audit Trail** → Audit trail wins (optimize speed elsewhere)
- **Convenience vs Capability Model** → Capability model wins (design around the constraint)
- **Local expedience vs Global consistency** → Global consistency wins (short-term pain, long-term safety)
- **Performance vs Determinism** → Determinism wins (predictability > speed)

**When in doubt: pick the answer that's easier to audit and harder to exploit.**

---

## Primary Goals

- **Deterministic governance** of AI actions
- **Capability-based authorization** with explicit grants
- **Policy-driven enforcement** with auditable decisions
- **Operational risk controls** with fail-closed defaults
- **Complete auditability** of all governance events

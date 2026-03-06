# AEGIS™ Terminology

Architectural Enforcement & Governance of Intelligent Systems

Version: 0.1
Status: Draft

---

# Overview

This document defines key terminology used throughout the AEGIS™ specification.

Consistent terminology is important for ensuring that architectural documents, protocol definitions, and implementation guidance are interpreted consistently.

**Who should use this document?**

- Developers implementing AEGIS support for AI frameworks
- Security architects evaluating governance models
- Policy designers creating governance rules
- Operations teams deploying AEGIS runtimes
- DevOps engineers building governed AI systems

---

# Alphabetical Quick Reference

| Term | Category | See Section |
|---|---|---|
| AEGIS™ | Core | [AEGIS™](#aegis) |
| Action | Core Concepts | [Action](#action) |
| Actor | Core Concepts | [Actor](#actor) |
| Audit Trail | Logging & Query | [Audit Trail](#audit-trail) |
| Capability | Core Concepts | [Capability](#capability) |
| Capability Registry | Runtime Components | [Capability Registry](#capability-registry) |
| Circumvention Report | Federation | [Circumvention Report](#circumvention-report) |
| Decision Engine | Runtime Components | [Decision Engine](#decision-engine) |
| Deterministic Governance | Principles | [Deterministic Governance](#deterministic-governance) |
| External Systems | Infrastructure | [External Systems](#external-systems) |
| Governance Attestation | Federation | [Governance Attestation](#governance-attestation) |
| Governance Decision | Core Concepts | [Governance Decision](#governance-decision) |
| Governance Event | Federation | [Governance Event](#governance-event) |
| Governance Gateway | Runtime Components | [Governance Gateway](#governance-gateway) |
| Governance Policy | Core Concepts | [Governance Policy](#governance-policy) |
| Governance Runtime | Runtime Components | [Governance Runtime](#governance-runtime) |
| Policy Engine | Runtime Components | [Policy Engine](#policy-engine) |
| Risk Signal | Federation | [Risk Signal](#risk-signal) |
| Tool Proxy | Infrastructure | [Tool Proxy](#tool-proxy) |

---

# Acronym Reference

| Acronym | Expansion | Context |
|---|---|---|
| AEGIS | Architectural Enforcement & Governance of Intelligent Systems | Project name |
| AGP | AEGIS Governance Protocol | Protocol specification (AGP-1) |
| GFN | Governance Federation Network | Multi-org intelligence sharing |
| RFC | Request for Comments | Specification series (RFC-0001 through RFC-0004) |
| AI | Artificial Intelligence | Any trained model, agent, or LLM |
| YAML | YAML Ain't Markup Language | Policy definition language |
| API | Application Programming Interface | Protocol message interface |
| TBD | To Be Determined | Status indicator for pending specs |

---

# Term Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│ AI Agent → ACTION_PROPOSE (AGP Message)                         │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ GOVERNANCE RUNTIME                                              │
│  ├─ Governance Gateway (receives & validates ACTION_PROPOSE)   │
│  ├─ Decision Engine (evaluates policy)                         │
│  │   ├─ Capability Registry (checks allowed capability)        │
│  │   ├─ Policy Engine (evaluates conditions)                    │
│  │   └─ Actor identity (validates requestor)                    │
│  └─ Audit Logging (records all decisions)                      │
└─────────────────────────────────────────────────────────────────┘
                          ↓
      ┌────────────┬────────────┬──────────────┐
      ▼            ▼            ▼              ▼
   ALLOW        DENY      ESCALATE      REQUIRE_CONFIRMATION
      │                       │              │
      └───────────┬───────────┴──────────────┘
                  ↓
      ┌─────────────────────────────┐
      │ ACTION_DECIDE (returned)    │
      └─────────────────────────────┘
             ↓                  ↓
        (approved)         (denied/escalated)
             ↓                  ↓
      ACTION_EXECUTE   Human Review / Audit
             ↓
      Tool Proxy → External Systems
             ↓
      Governance Event (for federation)
             ↓
      Federation Network (GFN)
```

---

# Core Terms

## AEGIS™

Architectural Enforcement & Governance of Intelligent Systems.

AEGIS™ is a governance architecture designed to enforce deterministic control over AI-generated actions before those actions interact with operational infrastructure.

**Related Terms:** [Governance Runtime](#governance-runtime), [Deterministic Governance](#deterministic-governance)

**Example:** An organization deploys AEGIS™ to govern its LangChain-based AI assistants, ensuring all database queries and API calls are approved before execution.

---

## Actor

An authenticated entity (user, service, or AI agent) that submits [Actions](#action) for governance evaluation.

Actors have:

- unique identity (username, service principal, agent ID)
- assigned roles and permissions
- audit trail of all their requested [Actions](#action)

The governance runtime authenticates actors before evaluating their [Actions](#action).

**Related Terms:** [Action](#action), [Governance Decision](#governance-decision), [Audit Trail](#audit-trail)

**Example:** An AI agent with identity "financial-analyst-ai-01" requests to execute a capability "transfer_funds". The [Decision Engine](#decision-engine) checks if this actor is authorized for financial operations.

---

## Deterministic Governance

Governance enforcement that produces consistent outcomes given the same inputs, implemented through architectural mechanisms rather than behavioral restrictions.

AEGIS™ uses deterministic governance to ensure:

- reproducible policy evaluation
- formal verifiability of governance decisions
- no hidden logic or non-deterministic behavior
- policy decisions can be explained and audited

**Related Terms:** [Governance Policy](#governance-policy), [Governance Decision](#governance-decision)

**Contrast:** Behavioral restrictions (e.g., "the model should not do X") lack deterministic enforcement. Architectural governance (AEGIS™) guarantees it.

---

## Governance Runtime

The runtime system responsible for evaluating and enforcing governance decisions.

The runtime typically includes:

- [Governance Gateway](#governance-gateway) — receives requests
- [Decision Engine](#decision-engine) — evaluates policies
- [Capability Registry](#capability-registry) — defines allowed actions
- [Policy Engine](#policy-engine) — evaluates [Governance Policies](#governance-policy)
- [Audit Logging](#audit-trail) — records all decisions

**Related Terms:** [Governance Gateway](#governance-gateway), [Decision Engine](#decision-engine), [AGP Protocol](#aegis-governance-protocol-agp)

**Example:** The runtime receives an [Action](#action) via AGP-1, validates the [Actor](#actor), checks the [Capability Registry](#capability-registry), evaluates [Governance Policies](#governance-policy), and returns a [Governance Decision](#governance-decision).

---

## Governance Gateway

The entry point through which AI systems submit proposed [Actions](#action) to the [Governance Runtime](#governance-runtime).

The gateway performs:

- request validation
- actor authentication
- protocol parsing
- request forwarding to [Decision Engine](#decision-engine)

**Related Terms:** [Governance Runtime](#governance-runtime), [Decision Engine](#decision-engine), [AGP Protocol](#aegis-governance-protocol-agp)

---

## Decision Engine

The component responsible for evaluating governance rules and determining whether [Actions](#action) may execute.

The [Decision Engine](#decision-engine) typically evaluates:

- **Capability authorization** — Is this [Capability](#capability) allowed? (via [Capability Registry](#capability-registry))
- **[Actor](#actor) identity** — Who is requesting this? (authentication & authorization)
- **[Governance Policies](#governance-policy)** — Does context match policy conditions? (via [Policy Engine](#policy-engine))
- **Risk assessment** — What is the risk profile of this [Action](#action)?

**Related Terms:** [Governance Runtime](#governance-runtime), [Governance Policy](#governance-policy), [Governance Decision](#governance-decision)

**Output:** A [Governance Decision](#governance-decision) (ALLOW, DENY, ESCALATE, or REQUIRE_CONFIRMATION)

---

## Policy Engine

The component that evaluates [Governance Policies](#governance-policy) against specific [Actions](#action) and contextual data.

The [Policy Engine](#policy-engine):

- parses policy conditions
- evaluates against [Action](#action) parameters
- determines policy match and applicable constraints
- returns policy verdict to [Decision Engine](#decision-engine)

**Related Terms:** [Governance Policy](#governance-policy), [Governance Decision](#governance-decision), [Decision Engine](#decision-engine)

**Example:** Policy "allow database write only during business hours EST" is evaluated by the [Policy Engine](#policy-engine), which checks current time zone and returns verdict.

---

## Capability

A defined operational action that an AI system is permitted to request.

Examples include:

```
telemetry.query
identity.disable_account
infrastructure.deploy
communication.send_alert
financial.transfer_funds
database.read
database.write
```

Capabilities must be defined in the [Capability Registry](#capability-registry) before they may be used. Each [Action](#action) requests a specific capability.

**Related Terms:** [Capability Registry](#capability-registry), [Action](#action), [Governance Policy](#governance-policy)

**Key Property:** Capabilities are *named, explicit, and governed*. Ungoverned actions are denied by default.

---

## Capability Registry

A structured repository that defines all capabilities available within a governed environment.

Each capability includes:

- identifier (e.g., `database.write`)
- description
- allowed [actors](#actor) or roles
- environmental constraints
- risk classification (low/medium/high)
- resource categories affected

**Related Terms:** [Capability](#capability), [Decision Engine](#decision-engine), [Governance Policy](#governance-policy)

**Function:** The [Decision Engine](#decision-engine) queries the [Capability Registry](#capability-registry) when evaluating whether an [Action](#action) is allowed.

---

## Governance Policy

A rule that determines whether a [Capability](#capability) may be exercised under specific conditions.

Policies evaluate contextual attributes such as:

- [Actor](#actor) role or identity
- environment (staging vs. production)
- resource classification (public, internal, confidential)
- risk score
- time windows
- concurrency limits

**Related Terms:** [Capability](#capability), [Policy Engine](#policy-engine), [Governance Decision](#governance-decision)

**Example Policy (YAML):**

```yaml
- name: "Production Database Write"
  capability: "database.write"
  environment: "production"
  allowed_when:
    - role: "data-engineer"
    - time_zone: "EST"
    - hour_range: "09:00-17:00"
  require: "human_approval"  # escalation
```

---

## Action

A proposed operational task generated by an AI system.

An [Action](#action) includes:

- [Actor](#actor) identity
- requested [Capability](#capability)
- resource target
- execution parameters
- context (environment, timestamp)

[Actions](#action) must be evaluated by the [Governance Runtime](#governance-runtime) before execution. Each [Action](#action) generates a [Governance Decision](#governance-decision).

**Related Terms:** [Actor](#actor), [Capability](#capability), [Governance Runtime](#governance-runtime), [Governance Decision](#governance-decision)

**Workflow:** ACTION_PROPOSE → [Governance Runtime](#governance-runtime) → [Governance Decision](#governance-decision) → ACTION_DECIDE

---

## Governance Decision

The outcome of evaluating an [Action](#action) request.

Possible [Governance Decisions](#governance-decision) include:

```
ALLOW           - Action approved, proceed to execution
DENY            - Action denied, audit logged
ESCALATE        - Human decision required
REQUIRE_CONFIRMATION - Request confirmation from actor before allowing
```

Each decision includes:

- verdict (one of above)
- rationale (which policy matched)
- constraints (if applicable)
- [Audit Trail](#audit-trail) entry

**Related Terms:** [Decision Engine](#decision-engine), [Action](#action), [Governance Event](#governance-event)

---

## Audit Trail

The immutable record of all governance-related decisions and events.

The [Audit Trail](#audit-trail) logs:

- [Action](#action) proposals
- [Governance Decisions](#governance-decision) (with rationale)
- policy matches
- [actor](#actor) identity
- timestamps
- execution results

An [Audit Trail](#audit-trail) enables:

- compliance verification
- forensic analysis
- governance attestation
- [Circumvention Report](#circumvention-report) generation

**Related Terms:** [Governance Runtime](#governance-runtime), [Governance Event](#governance-event), [Governance Attestation](#governance-attestation)

---

## Tool Proxy

A controlled interface that mediates interactions with external systems.

Tool proxies ensure that operational [Actions](#action) remain subject to governance enforcement by:

- intercepting action requests
- forwarding to [Governance Runtime](#governance-runtime) for approval
- only executing [approved](#governance-decision) [Actions](#action)
- recording execution in [Audit Trail](#audit-trail)

**Related Terms:** [Governance Runtime](#governance-runtime), [External Systems](#external-systems), [Action](#action)

**Example:** A [Tool Proxy](#tool-proxy) for AWS Lambda intercepts the AI agent's function invocation, gets governance approval, then executes the approved function.

---

## External Systems

Operational infrastructure that performs tasks requested by AI agents.

Examples include:

- cloud platforms (AWS, Azure, GCP)
- enterprise applications (Salesforce, SAP, ServiceNow)
- data systems (databases, data warehouses)
- security monitoring platforms (SIEM, threat detection)
- communication systems (email, Slack, Teams)

[External Systems](#external-systems) are accessed through [Tool Proxies](#tool-proxy) to ensure governance enforcement.

**Related Terms:** [Tool Proxy](#tool-proxy), [Action](#action)

---

## AEGIS Governance Protocol (AGP)

The protocol used by AI agents to communicate with the [Governance Runtime](#governance-runtime).

AGP (currently AGP-1) defines message structures for:

- **ACTION_PROPOSE** — AI agent submits [Action](#action) for evaluation
- **ACTION_DECIDE** — Runtime returns [Governance Decision](#governance-decision)
- **ACTION_EXECUTE** — Approved action execution with results
- **ACTION_ESCALATE** — Complex decisions forwarded to humans

**Related Terms:** [Governance Runtime](#governance-runtime), [Action](#action), [Governance Decision](#governance-decision)

**RFC Specification:** [RFC-0001: AEGIS Architecture](rfc/RFC-0001.md) defines AGP message format and protocol flow.

---

## Governance Event

A structured message describing governance-related information shared between AEGIS nodes in a [Federation Network](#federation-network).

Types of [Governance Events](#governance-event):

- **Policy Updates** — Changes to [Governance Policies](#governance-policy)
- **[Circumvention Reports](#circumvention-report)** — Documented evasion attempts
- **[Risk Signals](#risk-signal)** — Emerging threats or threats detected
- **[Governance Attestations](#governance-attestation)** — Proof of governance compliance

**Related Terms:** [Federation Network](#federation-network), [Governance Attestation](#governance-attestation), [Risk Signal](#risk-signal)

---

## Risk Signal

A [Governance Event](#governance-event) that communicates detected threats, anomalies, or risk patterns to the [Federation Network](#federation-network).

[Risk Signals](#risk-signal) include:

- unusual [Action](#action) patterns
- multiple DENY decisions from the same [Actor](#actor)
- policy circumvention attempts
- infrastructure anomalies
- threat intelligence from external sources

Organizations in the [Federation Network](#federation-network) can subscribe to and act on [Risk Signals](#risk-signal) to improve collective governance.

**Related Terms:** [Governance Event](#governance-event), [Federation Network](#federation-network), [Circumvention Report](#circumvention-report)

---

## Circumvention Report

A documented account of an [Actor](#actor)'s attempt to bypass or evade governance controls.

[Circumvention Reports](#circumvention-report) include:

- detailed evasion technique description
- affected [Capabilities](#capability)
- [Actor](#actor) identity
- timestamp and context
- impact assessment
- recommended policy updates

[Circumvention Reports](#circumvention-report) are shared via the [Federation Network](#federation-network) to help other organizations defend against similar attacks.

**Related Terms:** [Governance Event](#governance-event), [Federation Network](#federation-network), [Risk Signal](#risk-signal)

**Example:** "LLM attempted SQL injection in database query parameter. Mitigation: input validation enforced. Recommendation: require approval for parameterized queries containing user input."

---

## Governance Attestation

Cryptographic proof that a system is complying with AEGIS™ governance principles.

A [Governance Attestation](#governance-attestation) certifies:

- [Audit Trail](#audit-trail) integrity (no tampering)
- policy enforcement (all [Actions](#action) evaluated)
- [Actor](#actor) authentication (genuine requestors)
- deterministic evaluation ([Governance Decisions](#governance-decision) reproducible)

[Governance Attestations](#governance-attestation) are shared via [Governance Events](#governance-event) to the [Federation Network](#federation-network) to establish trust.

**Related Terms:** [Audit Trail](#audit-trail), [Governance Event](#governance-event), [Federation Network](#federation-network)

---

## Federation Network

The distributed network through which AEGIS runtimes exchange governance intelligence.

The [Federation Network](#federation-network) enables organizations to share information about:

- **Governance Threats** — [Circumvention Reports](#circumvention-report), evasion techniques
- **Policy Changes** — Updated [Governance Policies](#governance-policy) and best practices
- **[Risk Signals](#risk-signal)** — Threat patterns, anomalies, attack attempts
- **[Governance Attestations](#governance-attestation)** — Proof of compliance

**Related Terms:** [Governance Event](#governance-event), [Circumvention Report](#circumvention-report), [Governance Attestation](#governance-attestation)

**Benefit:** Organizations collectively improve governance posture through shared intelligence.

# Foundational Principle

> Capability without constraint is not intelligence™

This principle underlies the design philosophy of AEGIS and emphasizes that intelligent systems must operate within explicitly defined governance boundaries.

---

# Usage by Role

## For Developers Integrating AI Frameworks

Focus on these terms when building AEGIS support:

- [Action](#action), [AGP Protocol](#aegis-governance-protocol-agp), [Tool Proxy](#tool-proxy)
- [Governance Decision](#governance-decision), [External Systems](#external-systems)
- Understanding: "My AI agent proposes [Actions](#action) via AGP, receives [Governance Decisions](#governance-decision), and executes through [Tool Proxies](#tool-proxy)"

## For Policy Designers & Security Teams

Focus on these terms when defining governance:

- [Capability](#capability), [Capability Registry](#capability-registry)
- [Governance Policy](#governance-policy), [Policy Engine](#policy-engine)
- [Actor](#actor), [Risk Signal](#risk-signal)
- Understanding: "I define [Capabilities](#capability) and [Policies](#governance-policy) that control which [Actors](#actor) can do what, when."

## For Operations & DevOps Teams

Focus on these terms when deploying systems:

- [Governance Runtime](#governance-runtime), [Governance Gateway](#governance-gateway)
- [Decision Engine](#decision-engine), [Audit Trail](#audit-trail)
- [Federation Network](#federation-network), [Governance Attestation](#governance-attestation)
- Understanding: "I operate the AEGIS [Governance Runtime](#governance-runtime) that evaluates [Actions](#action), logs [Audit Trails](#audit-trail), and exchanges federation [Governance Events](#governance-event)"

## For Security Architects & Evaluators

Focus on these terms when assessing architecture:

- [Deterministic Governance](#deterministic-governance), [Governance Runtime](#governance-runtime)
- [Capability](#capability), [Governance Policy](#governance-policy)
- [Circumvention Report](#circumvention-report), [Risk Signal](#risk-signal)
- [Governance Attestation](#governance-attestation)
- Understanding: "AEGIS enforces [Capability](#capability)-based authorization through [Deterministic Governance](#deterministic-governance), with defenses against [Circumvention](#circumvention-report) and federation threat intelligence."

---

# Scenario Examples

## Scenario 1: AI-Powered Database Access

**Setup:**

- [Actor](#actor): `analytics-ai-agent-001`
- [Capability](#capability): `database.query`
- [Policy](#governance-policy): "Allow database reads only for non-sensitive tables, during business hours EST"

**Workflow:**

1. AI agent proposes [Action](#action): *Query transaction history from `Transactions` table*
2. [Governance Gateway](#governance-gateway) receives ACTION_PROPOSE via AGP-1
3. [Decision Engine](#decision-engine) evaluates:
   - Is `database.query` in [Capability Registry](#capability-registry)? ✓
   - Is `analytics-ai-agent-001` authorized? ✓
   - Does table `Transactions` match "non-sensitive"? ❌ (sensitive table)
4. [Policy Engine](#policy-engine) evaluates [Policy](#governance-policy): ❌ (restricted table)
5. [Decision Engine](#decision-engine) returns: **DENY**
6. [Audit Trail](#audit-trail) logs rejection with rationale
7. [Governance Event](#governance-event) sent to [Federation Network](#federation-network)

**Result:** Database protected; [Audit Trail](#audit-trail) provides evidence; other organizations notified via [Risk Signal](#risk-signal)

---

## Scenario 2: Multi-Organization Threat Intelligence

**Setup:**

- Organization A detects evasion attempt
- Organization B receives federation intelligence

**Workflow:**

1. Organization A's [Governance Runtime](#governance-runtime) detects unauthorized [Action](#action) attempt
2. Generates [Circumvention Report](#circumvention-report): "LLM attempted privilege escalation via parameter injection"
3. Creates [Governance Event](#governance-event) with report + [Governance Attestation](#governance-attestation)
4. Publishes to [Federation Network](#federation-network)
5. Organization B's [Governance Runtime](#governance-runtime) receives [Risk Signal](#risk-signal)
6. Updates [Capability Registry](#capability-registry) and [Governance Policies](#governance-policy) to defend
7. Logs defensive action in [Audit Trail](#audit-trail)

**Result:** Collective threat defense; faster adaptation; shared governance intelligence

---

## Scenario 3: Escalation Workflow

**Setup:**

- [Actor](#actor): `provisioning-ai-agent`
- [Capability](#capability): `infrastructure.deploy`
- [Policy](#governance-policy): "Production deployments require human approval"

**Workflow:**

1. AI agent proposes [Action](#action): *Deploy to production infrastructure*
2. [Governance Gateway](#governance-gateway) receives ACTION_PROPOSE
3. [Decision Engine](#decision-engine) + [Policy Engine](#policy-engine) determine: [Policy](#governance-policy) requires human review
4. Returns [Governance Decision](#governance-decision): **ESCALATE** with approval link
5. Human operator reviews [Action](#action) details, [Audit Trail](#audit-trail), [Risk Signals](#risk-signal)
6. Operator approves or denies
7. [Governance RuntimeATRIL](#audit-trail) logs final decision + approver identity

**Result:** Critical [Actions](#action) protected by human judgment; full [Audit Trail](#audit-trail) for compliance

---

# Cross-Reference Guide

**Understanding AI Governance Flow:**
[Action](#action) → [AGP Protocol](#aegis-governance-protocol-agp) → [Governance Runtime](#governance-runtime) → [Governance Gateway](#governance-gateway) → [Decision Engine](#decision-engine) → [Governance Decision](#governance-decision) → [Audit Trail](#audit-trail)

**Understanding Policy Evaluation:**
[Governance Policy](#governance-policy) → [Policy Engine](#policy-engine) + [Capability Registry](#capability-registry) + [Actor](#actor) context → [Decision Engine](#decision-engine) → verdict

**Understanding Federation:**
[Governance Event](#governance-event) ← [Circumvention Report](#circumvention-report), [Risk Signal](#risk-signal), [Governance Attestation](#governance-attestation) ← [Federation Network](#federation-network)

**Understanding Enforcement:**
[Governance Decision](#governance-decision) → [Tool Proxy](#tool-proxy) → [External Systems](#external-systems) (only approved [Actions](#action) execute)

---

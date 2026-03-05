# RFC-0003

## AEGIS Capability Registry & Policy Language Specification

Version: 0.1
Status: Draft
Authors: AEGIS Project

---

# 1. Purpose

This document defines the **AEGIS Capability Registry** and the **Policy Expression Language** used to evaluate governance decisions.

The capability registry provides a standardized way to define the operations an AI system may perform.

The policy language defines the rules used by the AEGIS decision engine to determine whether a proposed action is allowed.

Together these components form the **governance logic layer** of the AEGIS runtime.

---

# 2. Design Goals

The registry and policy system must satisfy the following properties.

### Explicit Capability Modeling

All system actions must be represented as capabilities.

### Policy Transparency

Governance rules must be human-readable and auditable.

### Deterministic Evaluation

Policy evaluation must produce consistent results for identical inputs.

### Composability

Policies must support modular rule definitions and inheritance.

### Extensibility

Capability definitions must support new system operations without breaking compatibility.

---

# 3. Capability Registry

The capability registry defines all actions that AI systems may request.

Each capability includes:

* unique identifier
* description
* allowed roles
* environmental scope
* risk classification
* optional constraints

Capabilities are stored as structured records.

---

## Example Capability Definition

```id="5frc17"
capability: telemetry.query
description: Query security telemetry datasets
allowed_roles:
  - soc_analyst
  - incident_responder
environment:
  - production
  - staging
risk_level: low
constraints:
  max_results: 500
```

---

## Infrastructure Example

```id="9b9cl7"
capability: infrastructure.deploy
description: Deploy application infrastructure
allowed_roles:
  - devops_engineer
environment:
  - staging
risk_level: high
approval_required: true
```

---

# 4. Capability Categories

Capabilities are grouped into categories.

```id="gsgl8n"
telemetry.*
data.*
infrastructure.*
identity.*
communication.*
governance.*
```

Example:

```id="prc3m4"
telemetry.query
identity.disable_account
communication.send_alert
```

This taxonomy enables consistent policy evaluation.

---

# 5. Policy Language

AEGIS policies define conditions under which capabilities may be exercised.

Policies evaluate structured inputs describing:

* actor identity
* capability requested
* system environment
* resource classification
* contextual metadata

Policies produce one of the following outcomes:

```id="t5q5le"
ALLOW
DENY
ESCALATE
REQUIRE_CONFIRMATION
```

---

# 6. Policy Structure

Policies are written as structured rules.

Example:

```id="3x9txc"
policy: telemetry_query_allowed
when:
  capability: telemetry.query
  actor.role: soc_analyst
then:
  decision: ALLOW
```

---

# 7. Conditional Policies

Policies may include conditional expressions.

Example:

```id="9w32ux"
policy: infrastructure_production_guardrail
when:
  capability: infrastructure.deploy
  environment: production
then:
  decision: ESCALATE
```

---

# 8. Risk-Based Policies

Policies may incorporate risk thresholds.

Example:

```id="3uyx4t"
policy: high_risk_operation
when:
  risk_score > 7
then:
  decision: REQUIRE_CONFIRMATION
```

---

# 9. Policy Composition

Policies may be layered.

Evaluation order:

```id="y1u3s9"
1. System invariants
2. Capability registry rules
3. Governance policies
4. Risk evaluation
```

If any rule produces **DENY**, the action must be rejected.

---

# 10. Governance Invariants

Certain rules override all policies.

Examples:

```id="s3l3p3"
deny if capability not defined
deny if actor not authenticated
deny if secret exposure detected
```

These invariants enforce foundational governance guarantees.

---

# 11. Policy Versioning

All policies must include version identifiers.

Example:

```id="n7rtt7"
policy_set: enterprise_governance
version: 2026.03.04
```

Versioning ensures governance decisions remain reproducible.

---

# 12. Example Evaluation

Input action:

```id="nmxu0k"
actor: soc_analyst
capability: telemetry.query
environment: production
```

Evaluation result:

```id="p4h0h1"
decision: ALLOW
```

---

# 13. Security Properties

The registry and policy system provide:

Capability Transparency
All allowed operations are explicitly defined.

Policy Auditability
Governance rules are human-readable.

Deterministic Governance
Policy evaluation produces consistent results.

Operational Safety
High-risk actions require escalation.

---

# 14. Future Extensions

Future versions may support:

* policy inheritance
* multi-organization governance profiles
* automatic policy updates from the AEGIS Federation Network
* formal verification of governance policies

---

# 15. Relationship to Other Specifications

This document extends:

* RFC-0001 — AEGIS Architecture
* RFC-0002 — Governance Runtime
* AGP-1 — Governance Protocol

Together these specifications define the complete AEGIS governance stack.

---

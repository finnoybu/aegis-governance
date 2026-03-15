<p align="center">
    <source media="(prefers-color-scheme: dark)" srcset="../aegis-core/assets/AEGIS_wordmark_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../aegis-core/assets/AEGIS_wordmark_light.svg">
    <img src="../aegis-core/assets/AEGIS_wordmark.svg" width="180" alt="AEGIS™ Governance Logo">
  </picture>
</p>

# AEGIS™ Runtime (Reference Implementation)

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Status](https://img.shields.io/badge/status-alpha-orange)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

```

The AEGIS™ Runtime is the **reference Python implementation** of the AEGIS governance architecture.
It provides a deterministic enforcement layer that evaluates and governs AI-initiated actions **before they interact with infrastructure**.

> **Capability without constraint is not intelligence™**

AEGIS enforces governance decisions **before execution**, ensuring AI systems operate within explicit capability and policy boundaries.

---

## What AEGIS Does

AEGIS sits between AI systems and the external world, enforcing governance decisions before actions are executed.

AI Agent
   │
   ▼
AEGIS Runtime
   │
 
   ├ GovernanceGateway
   ├ DecisionEngine
   ├ CapabilityRegistry
   ├ PolicyEngine
   └ AuditSystem
   │
   ▼
Tools / APIs / Files / Infrastructure
```

AEGIS ensures that:

- agents can only attempt actions they have **capabilities** for
- actions must pass **deterministic policy evaluation**
- every governance decision is **immutably audited**

---

# Overview

The runtime implements a governance pipeline that evaluates every proposed action:

```
AI Agent
   │
   ▼
ToolProxy
   │
   ▼
GovernanceGateway
   │
   ▼
DecisionEngine
   │
   ├─ CapabilityRegistry
   ├─ PolicyEngine
   └─ AuditSystem
```

Actions are executed **only when the governance decision is APPROVED**.

All decisions — including denials — are permanently recorded in the audit log.

---

# Core Components

## Governance Gateway

The gateway is the **single validated entry point** for governance requests.

Responsibilities:

- request validation
- routing to the decision engine

---

## Decision Engine

The authoritative governance evaluator.

The engine executes a two-stage pipeline:

1. **Capability check**

   The agent must possess a capability that covers the requested action and target.

2. **Policy evaluation**

   Deterministic policies evaluate whether the action should be allowed.

Every decision is recorded in the audit log.

---

## Capability Registry

Implements **capability-based security**.

Capabilities define:

- allowed action types
- permitted target patterns
- optional expiration
- metadata annotations

Agents must possess a capability before attempting an action.

---

## Policy Engine

Provides deterministic policy evaluation.

Policies contain:

- priority ordering
- allow / deny effect
- pure condition predicates

Evaluation rules:

```
1. Evaluate policies by priority
2. First matching deny → DENIED
3. Otherwise first matching allow → APPROVED
4. Otherwise → DENIED (default-deny)
```

---

## Tool Proxy

The Tool Proxy intercepts tool calls from AI agents.

Every tool invocation:

1. Creates an AGP request
2. Sends it to the governance gateway
3. Executes only if the decision is **APPROVED**

---

## Audit System

Every governance decision is recorded in an **append-only audit log**.

Audit records include:

- request ID
- agent ID
- action type
- target
- parameters
- governance decision
- policy evaluation trace
- session ID
- timestamp

This enables:

- compliance reporting
- forensic review
- deterministic traceability

---

# Governance Protocol

The runtime implements the **AEGIS Governance Protocol (AGP)**.

Core objects:

```
AGPRequest
AGPResponse
AGPAction
AGPContext
Decision
ActionType
```

All governance interactions are represented using these protocol objects.

---

`git clone https://github.com/finnoybu/aegis-governance.git`

```
cd aegis-governance/aegis-runtime
pip install -e .
```

After installation, the runtime can be imported as:

# Installation
Clone the repository and install the runtime locally.

```
`git clone https://github.com/finnoybu/aegis-governance.git`
cd aegis-governance/aegis-runtime
pip install -e .
```

After installation, the runtime can be imported as:

```python
from aegis import AEGISRuntime
```

`git clone https://github.com/finnoybu/aegis-governance.git`
*** End Patch
pip install -e .

```

After installation, the runtime can be imported as:

```python
from aegis import AEGISRuntime
```

---

# Quick Start

```python
from aegis import (
    AEGISRuntime,
    Capability,
    Policy,
    PolicyEffect,
    ActionType
)

runtime = AEGISRuntime()

# Register a capability
runtime.capabilities.register(
    Capability(
        id="cap-read-docs",
        name="Read documentation",
        description="Allows reading documentation files",
        action_types=[ActionType.FILE_READ.value],
        target_patterns=["/docs/*"]
    )
)

# Grant capability to agent
runtime.capabilities.grant("agent-1", "cap-read-docs")

# Add an allow policy
runtime.policies.add_policy(
    Policy(
        id="allow-docs",
        name="Allow documentation reads",
        description="Agents may read documentation",
        effect=PolicyEffect.ALLOW,
        conditions=[]
    )
)

# Create governed tool proxy
proxy = runtime.create_tool_proxy("agent-1", "session-1")

proxy.register_tool(
    "read_file",
    fn=lambda path: open(path).read(),
    target="/docs/read"
)

content = proxy.call("read_file", path="/docs/intro.md")
```

If governance denies the action, the call raises a `PermissionError`.

---

# Running the Example

Minimal runnable examples are included in the `examples/` directory.

```
python examples/hello_aegis.py
```

This initializes the runtime and demonstrates capability and policy configuration.

---

# Running Tests

Run the test suite:

```
pytest
```

---

# Development Setup

Recommended environment:

```
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e .
pip install pytest
```

---

# Project Structure

```
aegis-runtime/
│
├─ aegis/           # Core runtime package
├─ examples/        # Minimal runnable examples
├─ tests/           # Test suite
├─ pyproject.toml   # Package configuration
└─ README.md
```

---

# Design Principles

AEGIS enforces several core principles.

## Deterministic Governance

The same request against the same policies always produces the same decision.

## Defense in Depth

Enforcement layers include capability checks, policy evaluation, and audit recording.

## Default-Deny Security

Actions are denied unless explicitly allowed.

## Immutable Audit Trail

All governance decisions are permanently recorded.

## Protocol-First Architecture

Governance interactions are defined using structured protocol messages.

---

# Relationship to the AEGIS™ Initiative

This runtime is the **reference implementation** supporting the broader AEGIS ecosystem.

```
AEGIS
├─ Constitution
├─ Governance Protocol (AGP)
├─ Federation Network
└─ Reference Runtime
```

The runtime demonstrates how AEGIS governance can be embedded into real AI systems.

---

# Status

Early reference implementation.

Future extensions may include:

- risk scoring
- federated governance signals
- distributed policy synchronization
- additional runtime implementations (Rust / Go)

---

# License

See the project LICENSE file.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*  
*AEGIS Initiative — Finnoybu IP LLC*

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../aegis-core/assets/AEGIS_wordmark_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../aegis-core/assets/AEGIS_wordmark_light.svg">
    <img src="../aegis-core/assets/AEGIS_wordmark.svg" width="90" alt="AEGIS™ Governance Logo">
  </picture>
</p>

# AEGIS™ RFC Index

Architectural Enforcement & Governance of Intelligent Systems

---

## Overview

This directory contains the **Request for Comments (RFC)** specifications that define the technical architecture of AEGIS™.

Each RFC specifies a distinct component of the AEGIS governance system. Together these documents define the implementation requirements for AEGIS-compliant governance runtimes and ecosystems.

RFCs allow the architecture to evolve while preserving a clear historical record of design decisions.

---

## Current RFCs

| RFC      | Title                                 | Purpose                                                  |
| -------- | ------------------------------------- | -------------------------------------------------------- |
| RFC-0001 | AEGIS Architecture                    | Defines the foundational architecture and system model   |
| RFC-0002 | Governance Runtime                    | Specifies the runtime that enforces governance decisions |
| RFC-0003 | Capability Registry & Policy Language | Defines capability schema and governance policies        |
| RFC-0004 | Governance Event Model                | Defines event structures used in federation networks     |

---

## Recommended Reading Order

### For Implementers

1. **RFC-0001 — Architecture**
2. **RFC-0002 — Governance Runtime**
3. **RFC-0003 — Capability Registry**
4. **RFC-0004 — Governance Event Model**

### For Security Architects

1. **RFC-0001 — Architecture**
2. **RFC-0003 — Capability Registry**
3. **RFC-0002 — Governance Runtime**

### For Governance Designers

1. **RFC-0001 — Architecture**
2. **RFC-0003 — Capability Registry**
3. **RFC-0004 — Governance Event Model**

---

## RFC Lifecycle

AEGIS™ uses a lightweight RFC process to evolve the architecture.

Typical lifecycle:

1. **Proposal** — RFC submitted through a pull request
2. **Discussion** — community review and architectural debate
3. **Revision** — author updates the proposal
4. **Acceptance** — maintainers merge the RFC
5. **Implementation** — runtime and schemas updated accordingly

Accepted RFCs become part of the official AEGIS specification.

---

## Relationship to Other Documentation

RFCs are part of the broader AEGIS documentation ecosystem.

| Document               | Location                    | Purpose                            |
| ---------------------- | --------------------------- | ---------------------------------- |
| README                 | `/`                         | Project introduction               |
| SPECIFICATION.md       | `/`                         | Specification overview             |
| System Overview        | `/aegis-core/overview/`     | High-level architecture            |
| Reference Architecture | `/aegis-core/architecture/` | Detailed system design             |
| Threat Model           | `/aegis-core/threat-model/` | Security analysis                  |
| Protocol               | `/aegis-core/protocol/`     | AGP protocol definition            |
| Federation             | `/federation/`              | Governance federation architecture |

---

## Specification Scope

### RFC-0001 — AEGIS Architecture

Defines the foundational architecture separating AI reasoning from operational execution.

Includes:

* architectural principles
* system components
* execution model
* security guarantees

---

### RFC-0002 — Governance Runtime

Defines the runtime responsible for enforcing governance decisions.

Includes:

* governance gateway
* decision engine
* capability registry integration
* policy evaluation
* audit logging

---

### RFC-0003 — Capability Registry & Policy Language

Defines how capabilities are modeled and how governance policies are expressed.

Includes:

* capability schema
* policy language syntax
* evaluation semantics
* governance invariants

---

### RFC-0004 — Governance Event Model

Defines the event structures used by AEGIS federation networks.

Includes:

* event envelope format
* governance signals
* circumvention reports
* federation distribution

---

## Versioning

The RFC series evolves alongside the AEGIS specification.

```
v0.x  – early architecture development
v1.0  – stable governance standard
```

Major architectural changes may introduce new RFC documents or revisions.

---

## Future RFCs

Possible future specifications include:

* RFC-0005 — Operational Considerations (monitoring, scaling, disaster recovery)
* RFC-0006 — Federation Network Protocol
* RFC-0007 — Hardware-Rooted Attestation
* RFC-0008 — Multi-Organization Governance

---

## Implementation Status

| Component              | Status         |
| ---------------------- | -------------- |
| Architecture Spec      | Draft Complete |
| Runtime Spec           | Draft Complete |
| Capability Registry    | Draft Complete |
| Governance Event Model | Draft Complete |
| Reference Runtime      | Planned        |
| Policy Engine          | Planned        |
| Federation Node        | Planned        |

---

## Foundational Principle

> Capability without constraint is not intelligence™

AEGIS™ operationalizes this principle through deterministic architectural governance.

---

## Trademark Notice

AEGIS™ is a trademark of Finnoybu IP LLC.

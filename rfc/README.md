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

| RFC | Title | Status | Purpose |
|---|---|---|---|
| RFC-0001 | AEGIS Architecture | Draft | Foundational architecture, system model, and security guarantees |
| RFC-0002 | Governance Runtime | Draft | Runtime API, state model, error behavior, and performance requirements |
| RFC-0003 | Capability Registry & Policy Language | Draft | Capability schema, policy language syntax, and evaluation algorithm |
| RFC-0004 | Governance Event Model | Draft | Federation event envelope, payload schemas, and trust evaluation |
| RFC-0005 | Reference Deployment Patterns | Draft | Deployment-agnostic patterns for Kubernetes, sidecar, embedded, and serverless |
| RFC-0006 | Claude Code Plugin | Draft | Governance enforcement plugin for the Claude Code development environment |
| RFC-0007 | Operational Considerations | Placeholder | Monitoring, scaling, disaster recovery, and day-two operations |
| RFC-0008 | Federation Network Protocol | Placeholder | GFN-1 transport, discovery, and federation topology |

---

## Recommended Reading Order

### For Implementers

1. RFC-0001 — Architecture
2. RFC-0002 — Governance Runtime
3. RFC-0003 — Capability Registry
4. RFC-0004 — Governance Event Model
5. RFC-0005 — Reference Deployment Patterns

### For Security Architects

1. RFC-0001 — Architecture
2. RFC-0003 — Capability Registry
3. RFC-0004 — Governance Event Model

### For Governance Designers

1. RFC-0001 — Architecture
2. RFC-0003 — Capability Registry
3. RFC-0004 — Governance Event Model

### For Developers (Quick Start)

1. RFC-0001 — Architecture (summary and guide-level sections)
2. RFC-0005 — Reference Deployment Patterns (RDP-03 Embedded Lightweight)
3. RFC-0006 — Claude Code Plugin

---

## RFC Lifecycle

AEGIS™ uses a lightweight RFC process to evolve the architecture.

| Status | Meaning |
|---|---|
| Placeholder | RFC number reserved; content pending |
| Draft | RFC under active development or review |
| Proposed | RFC submitted for community comment |
| Accepted | RFC merged and part of the official specification |
| Implemented | RFC fully implemented in runtime and tooling |
| Superseded | RFC replaced by a later RFC |

Typical lifecycle: Draft → Proposed → Accepted → Implemented

---

## RFC Template

All new RFCs must use the standard template: `RFC-0000-TEMPLATE.md`

Required sections: Summary, Motivation, Guide-Level Explanation, Reference-Level Explanation, Drawbacks, Alternatives Considered, Compatibility, Implementation Notes, Open Questions, Success Criteria, References.

---

## Relationship to Other Documentation

| Document | Location | Purpose |
|---|---|---|
| README | `/` | Project introduction |
| SPECIFICATION.md | `/` | Specification overview |
| System Overview | `/aegis-core/overview/` | High-level architecture |
| Reference Architecture | `/aegis-core/architecture/` | Detailed system design |
| Threat Model (ATM-1) | `/aegis-core/threat-model/` | Security analysis |
| Protocol (AGP-1) | `/aegis-core/protocol/` | Governance protocol definition |
| Federation (GFN-1) | `/federation/` | Governance federation architecture |
| RFC Template | `/rfc/RFC-0000-TEMPLATE.md` | Standard RFC format |

---

## Implementation Status

| Component | RFC | Status |
|---|---|---|
| Architecture Spec | RFC-0001 | Draft Complete |
| Runtime Spec | RFC-0002 | Draft Complete |
| Capability Registry | RFC-0003 | Draft Complete |
| Governance Event Model | RFC-0004 | Draft Complete |
| Reference Deployment Patterns | RFC-0005 | Draft Complete |
| Claude Code Plugin | RFC-0006 | Draft — Q2 2026 |
| Operational Considerations | RFC-0007 | Placeholder |
| Federation Network Protocol | RFC-0008 | Placeholder |
| Reference Runtime (Python) | — | In Progress |
| Policy Engine | — | Planned |
| Federation Node | — | Planned |

---

## Versioning

```
v0.x  – early architecture development
v1.0  – stable governance standard
```

Major architectural changes may introduce new RFC documents or revisions to existing ones.

---

## Foundational Principle

> Capability without constraint is not intelligence™

AEGIS™ operationalizes this principle through deterministic architectural governance.

---

## Trademark Notice

AEGIS™ is a trademark of Finnoybu IP LLC.

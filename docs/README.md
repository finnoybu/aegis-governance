<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../aegis-core/assets/AEGIS_wordmark_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../aegis-core/assets/AEGIS_wordmark_light.svg">
    <img src="../aegis-core/assets/AEGIS_wordmark.svg" width="90" alt="AEGIS Governance Logo">
  </picture>
</p>

# AEGIS Documentation

This directory contains **supporting documentation**, **architectural design artifacts**, and **historical context** for the AEGIS governance framework.

> **For normative specifications**, see [`../aegis-core/`](../aegis-core/README.md)\
> **For implementation code**, see [`../aegis-runtime/`](../aegis-runtime/)

---

## Quick Navigation

### Start Here

**New to AEGIS?** Read these in order:
1. [**History: AEGIS White Paper**](history/AEGIS_White_Paper.md) — Vision and problem statement
2. [**Architecture: System Principles**](architecture/SYSTEM_PRINCIPLES.md) — Core design philosophy
3. [**Architecture: Architecture Overview**](architecture/AEGIS_ARCHITECTURE_OVERVIEW.md) — High-level system design

**Implementing AEGIS?** Focus on:
- [Governance Engine Components](architecture/GOVERNANCE_ENGINE_COMPONENTS.md)
- [End-to-End Request Flow](architecture/END_TO_END_REQUEST_FLOW.md)
- [Capability Model](architecture/CAPABILITY_MODEL.md)

**Researching Governance?** Deep dive into:
- [Reference Monitor Model](architecture/REFERENCE_MONITOR_MODEL.md)
- [Decision Algorithm](architecture/DECISION_ALGORITHM.md)
- [Risk Scoring Model](architecture/RISK_SCORING_MODEL.md)

---

## Directory Structure

### `architecture/` — Design Documents (18 files)

Detailed architectural design documents describing AEGIS components, models, and algorithms.

#### Core Architecture

- [**AEGIS_ARCHITECTURE_OVERVIEW.md**](architecture/AEGIS_ARCHITECTURE_OVERVIEW.md) — High-level system architecture
- [**SYSTEM_PRINCIPLES.md**](architecture/SYSTEM_PRINCIPLES.md) — Foundational design principles
- [**AEGIS_SYSTEM_STACK.md**](architecture/AEGIS_SYSTEM_STACK.md) — Technology stack overview

#### Governance Engine

- [**GOVERNANCE_ENGINE_SPEC.md**](architecture/GOVERNANCE_ENGINE_SPEC.md) — Engine specification
- [**GOVERNANCE_ENGINE_COMPONENTS.md**](architecture/GOVERNANCE_ENGINE_COMPONENTS.md) — Component breakdown
- [**DECISION_ALGORITHM.md**](architecture/DECISION_ALGORITHM.md) — Decision-making logic

#### Security & Trust

- [**REFERENCE_MONITOR_MODEL.md**](architecture/REFERENCE_MONITOR_MODEL.md) — Security foundation
- [**SECURITY_ASSUMPTIONS.md**](architecture/SECURITY_ASSUMPTIONS.md) — Threat model assumptions
- [**TRUST_BOUNDARIES.md**](architecture/TRUST_BOUNDARIES.md) — Security boundary analysis

#### Capability System

- [**CAPABILITY_MODEL.md**](architecture/CAPABILITY_MODEL.md) — Capability-based authorization
- [**CAPABILITY_SCHEMA.md**](architecture/CAPABILITY_SCHEMA.md) — Schema definitions
- [**GOVERNED_CAPABILITY_FLOW.md**](architecture/GOVERNED_CAPABILITY_FLOW.md) — Request lifecycle

#### Risk & Policy
- [**RISK_SCORING_MODEL.md**](architecture/RISK_SCORING_MODEL.md) — Risk assessment framework
- [**RISK_SCORING_ALGORITHM.md**](architecture/RISK_SCORING_ALGORITHM.md) — Scoring implementation
- [**POLICY_LANGUAGE.md**](architecture/POLICY_LANGUAGE.md) — Policy DSL specification
- [**POLICY_MATCHING_AND_DEBUG.md**](architecture/POLICY_MATCHING_AND_DEBUG.md) — Policy evaluation

#### Request Processing
- [**END_TO_END_REQUEST_FLOW.md**](architecture/END_TO_END_REQUEST_FLOW.md) — Complete request lifecycle
- [**AI_KERNEL_MODEL.md**](architecture/AI_KERNEL_MODEL.md) — AI integration model

### `history/` — Historical Documents (5 files)

Early design documents and evolution context.

- [**AEGIS_White_Paper.md**](history/AEGIS_White_Paper.md) — Original vision document
- [**AEGIS_Marketing_Overview.md**](history/AEGIS_Marketing_Overview.md) — Product positioning
- [**AEGIS_Specification_Pack.md**](history/AEGIS_Specification_Pack.md) — Combined specification overview
- [**AEGIS_Governance_Federation_Network.yaml**](history/AEGIS_Governance_Federation_Network.yaml) — GFN design (YAML)
- [**AEGIS_Federated_Governance_Network_AT_Protocol.yaml**](history/AEGIS_Federated_Governance_Network_AT_Protocol.yaml) — AT Protocol integration (YAML)

> **Note**: These are **historical artifacts** showing the evolution of AEGIS design thinking.\
> For current normative specifications, refer to [`../aegis-core/`](../aegis-core/README.md).

### `announcements/` — Public Announcements

Organized by date and event. Each announcement includes readiness assessments and supporting materials.

#### 2026-03-05 Launch

- [**ANNOUNCEMENT.md**](announcements/2026-03-05-launch/ANNOUNCEMENT.md) — Public launch announcement
- [**READINESS_ASSESSMENT.md**](announcements/2026-03-05-launch/READINESS_ASSESSMENT.md) — Readiness evaluation (16/17 complete)
- [**READINESS_CHECKLIST.md**](announcements/2026-03-05-launch/READINESS_CHECKLIST.md) — Pre-announcement checklist

### `position-papers/` — Standards & Policy Engagement

Position statements, comments, and submissions to standards bodies, regulatory agencies, and governance organizations.

- **`nist/`** — National Institute of Standards and Technology submissions

---

## Relationship to Normative Specifications

This `docs/` directory contains **non-normative** design documentation.

### Normative vs. Non-Normative

| **Normative** (in `aegis-core/`) | **Non-Normative** (in `docs/`) |
|----------------------------------|-------------------------------|
| AGP-1 Protocol Specification | Architecture design documents |
| ATM-1 Threat Model | Historical white papers |
| Canonical JSON Schemas (owned by `aegis`) | Risk scoring algorithms |
| AEGIS Constitution | Implementation guidance |
| RFC Series | Evolution artifacts |

### Reading Path

**For Specification Work:**
1. Start with [`../aegis-core/README.md`](../aegis-core/README.md)
2. Read [AGP-1 INDEX](../aegis-core/protocol/AEGIS_AGP1_INDEX.md) for protocol details
3. Read [ATM-1 INDEX](../aegis-core/threat-model/AEGIS_ATM1_INDEX.md) for threat model
4. Refer to `docs/architecture/` for implementation context

**For Research:**
1. Start with [White Paper](history/AEGIS_White_Paper.md) for motivation
2. Read [System Principles](architecture/SYSTEM_PRINCIPLES.md) for philosophy
3. Read [Reference Monitor Model](architecture/REFERENCE_MONITOR_MODEL.md) for security foundations
4. Dive into [`../aegis-core/`](../aegis-core/README.md) for formal specifications

**For Implementation:**
1. Read [Governance Engine Components](architecture/GOVERNANCE_ENGINE_COMPONENTS.md)
2. Read [End-to-End Request Flow](architecture/END_TO_END_REQUEST_FLOW.md)
3. Study the canonical schemas in [`aegis/schemas`](https://github.com/aegis-initiative/aegis/tree/main/schemas)
4. Explore reference runtime in [`../aegis-runtime/`](../aegis-runtime/)

---

## Contributing

Contributions to documentation are welcome! Please:
- Keep architecture documents synchronized with normative specs
- Mark historical documents as such to avoid confusion
- Follow terminology from [`../TERMINOLOGY.md`](../TERMINOLOGY.md)

See [`../CONTRIBUTING.md`](../CONTRIBUTING.md) for guidelines.

---

## License & Trademark

- **Copyright**: © 2026 AEGIS Initiative. All rights reserved.
- **License**: See [`../LICENSE`](../LICENSE)
- **Trademark**: AEGIS™ is a trademark of Finnoybu IP LLC. See [`../TRADEMARKS.md`](../TRADEMARKS.md)

---

**Navigation**: [← Back to Repository Root](../README.md) | [→ Normative Specifications](../aegis-core/README.md)

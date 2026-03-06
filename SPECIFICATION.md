# AEGIS™ Specification

Architectural Enforcement & Governance of Intelligent Systems

Version: 0.1
Status: Draft Specification

---

# Overview

This document serves as the **canonical entry point for the AEGIS™ specification**.

AEGIS™ defines an architecture for governing AI-generated actions before they interact with operational infrastructure. The specification consists of several layers:

1. Architectural principles and system design
2. Governance runtime behavior
3. Protocol definitions for AI-agent interaction
4. Machine-readable schemas
5. Federated governance intelligence mechanisms

Together, these components define the full AEGIS™ governance architecture.

## Specification Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 5: Federated Governance Network (GFN)                     │
│   • Multi-org threat intelligence sharing                       │
│   • Governance signal distribution and policy federation        │
│   • Circumvention detection and attestation                     │
└─────────────────────────────────────────────────────────────────┘
         △
         │ depends on
         ▽
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: Governance Runtime & Implementation                    │
│   • Reference runtime components and patterns                   │
│   • Governance gateway, decision engine, policy engine          │
│   • Integration examples for LangChain, CrewAI, AutoGPT        │
└─────────────────────────────────────────────────────────────────┘
         △
         │ depends on
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: Protocol & Schema Definitions (AGP + Schemas)         │
│   • AGP-1 governance protocol specification                     │
│   • Machine-readable schemas for all message types              │
│   • Example payloads and validation rules                       │
└─────────────────────────────────────────────────────────────────┘
         △
         │ depends on
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: Governance Architecture & Design                       │
│   • Reference architecture patterns and deployment modes        │
│   • Ecosystem map and component interactions                    │
│   • Security architecture and threat model                      │
└─────────────────────────────────────────────────────────────────┘
         △
         │ depends on
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: Vision, Principles & Constitution                      │
│   • AEGIS Manifesto and system overview                         │
│   • AEGIS Constitution and governance principles (8 articles)   │
│   • FAQ and adoption model for different maturity levels        │
└─────────────────────────────────────────────────────────────────┘
```

**Build Sequentially**: Each layer depends on understanding previous layers. Start at Layer 1 for vision, advance to Layer 5 for federation.

---

# Quick Navigation

**What do you need to do?**

| Your Goal | Read First | Then Read | Implementation Support |
|---|---|---|---|
| Understand AEGIS concept | [Manifesto](aegis-core/manifesto/AEGIS_Manifesto.md) | [System Overview](aegis-core/overview/AEGIS_System_Overview.md) | [FAQ](aegis-core/faq/AEGIS_FAQ.md) |
| Evaluate governance model | [System Overview](aegis-core/overview/AEGIS_System_Overview.md) | [Reference Architecture](aegis-core/architecture/AEGIS_Reference_Architecture.md) | [Threat Model](aegis-core/threat-model/AEGIS_Threat_Model.md) |
| Design implementation | [Reference Architecture](aegis-core/architecture/AEGIS_Reference_Architecture.md) | [AGP-1 Protocol](aegis-core/protocol/AEGIS_Governance_Protocol_AGP1.md) | [Schemas](schemas/) |
| Build governance runtime | [Reference Runtime](aegis-runtime/) | [RFC-0002 (TBD)](rfc/RFC-0002.md) | [Integration Examples](examples/) |
| Deploy federation | [Federation Architecture](federation/) | [RFC-0004 (TBD)](rfc/RFC-0004.md) | [Ecosystem Map](aegis-core/architecture/AEGIS_Ecosystem_Map.md) |

---

# Getting Started

## Choose Your Path

### I want to understand the AEGIS vision

**Best for:** Executives, architects, decision-makers

1. Read [The AEGIS Manifesto](aegis-core/manifesto/AEGIS_Manifesto.md) — Vision and motivation
2. Read [System Overview](aegis-core/overview/AEGIS_System_Overview.md) — Why AEGIS, use cases, when to use
3. Review [AEGIS Constitution](aegis-core/constitution/AEGIS_Constitution.md) — 8 governance principles

### I want to evaluate AEGIS architecture

**Best for:** Security engineers, architects, evaluators

1. Read [System Overview](aegis-core/overview/AEGIS_System_Overview.md) — Architecture overview
2. Review [Reference Architecture](aegis-core/architecture/AEGIS_Reference_Architecture.md) — Detailed design
3. Study [Threat Model](aegis-core/threat-model/AEGIS_Threat_Model.md) — Security analysis
4. Explore [Ecosystem Map](aegis-core/architecture/AEGIS_Ecosystem_Map.md) — Component interactions

### I want to implement AEGIS governance

**Best for:** Developers, DevOps, runtime implementers

1. Read [Reference Architecture](aegis-core/architecture/AEGIS_Reference_Architecture.md) — Complete architecture
2. Study [RFC-0002: Governance Runtime](rfc/RFC-0002.md) — Runtime specification (pending)
3. Review [AGP-1 Protocol](aegis-core/protocol/AEGIS_Governance_Protocol_AGP1.md) — Protocol definition
4. Explore [Reference Runtime](aegis-runtime/) — Working implementation
5. Review [Integration Examples](examples/) — Framework integrations

### I want to deploy AEGIS federation

**Best for:** Operations, enterprise architects

1. Read [Federation Architecture](federation/) — Federation network design
2. Review [RFC-0004: Governance Event Model](rfc/RFC-0004.md) — Event schema (pending)
3. Study [Reference Architecture: Federation](aegis-core/architecture/AEGIS_Reference_Architecture.md#federation-integration) — Integration guidance

### I want to join the AEGIS community

**Best for:** Contributors, researchers, enthusiasts

1. Check [Contributing Guidelines](CONTRIBUTING.md) — How to contribute
2. Join [GitHub Discussions](https://github.com/aegis-initiative/aegis-governance/discussions) — Community conversation
3. Review [RFC Process](rfc/README.md) — How to propose changes
4. Start with an issue or discussion in your area of interest

---

# Specification Structure

The AEGIS specification is organized across five layers, from foundational principles through federation.

| Component | Purpose | Location | Layer | Status |
|---|---|---|---|---|
| Manifesto | Vision and motivation for architectural AI governance | [AEGIS Manifesto](aegis-core/manifesto/AEGIS_Manifesto.md) | 1 | ✅ v0.1 |
| System Overview | Why AEGIS, use cases, decision matrix, and getting started | [System Overview](aegis-core/overview/AEGIS_System_Overview.md) | 1 | ✅ v0.1 |
| Constitution | 8 foundational governance principles and enforcement mechanisms | [AEGIS Constitution](aegis-core/constitution/AEGIS_Constitution.md) | 1 | ✅ v0.1 |
| FAQ & Adoption Model | 3-level maturity model and common questions | [AEGIS FAQ](aegis-core/faq/AEGIS_FAQ.md) | 1 | ✅ v0.1 |
| Reference Architecture | Deployment patterns, performance targets, security architecture, integration guidance | [Reference Architecture](aegis-core/architecture/AEGIS_Reference_Architecture.md) | 2 | ✅ v0.1 |
| Ecosystem Map | Component interactions, data flows, deployment topologies | [Ecosystem Map](aegis-core/architecture/AEGIS_Ecosystem_Map.md) | 2 | ✅ v0.1 |
| Threat Model | Security analysis, attack vectors, risk mitigation | [Threat Model](aegis-core/threat-model/AEGIS_Threat_Model.md) | 2 | ✅ v0.1 |
| AGP-1 Protocol | Message structures for AI-governance runtime interaction | [AGP-1 Protocol](aegis-core/protocol/AEGIS_Governance_Protocol_AGP1.md) | 3 | ✅ v0.1 |
| AGP Schemas | Protocol message schemas and validation rules | [Schemas: AGP](schemas/agp/) | 3 | ✅ v0.1 |
| Capability Schemas | Capability registry definitions and structures | [Schemas: Capability](schemas/capability/) | 3 | ✅ v0.1 |
| Governance Schemas | Governance event structures and event model | [Schemas: Governance](schemas/governance/) | 3 | ✅ v0.1 |
| Common Schemas | Shared data models across all schemas | [Schemas: Common](schemas/common/) | 3 | ✅ v0.1 |
| Schema Examples | Example payloads demonstrating schema usage | [Schema Examples](schemas/examples/) | 3 | ✅ v0.1 |
| Reference Runtime | Working implementation of governance runtime components | [AEGIS Runtime](aegis-runtime/) | 4 | 🔄 In Progress |
| Integration Examples | Pattern implementations for LangChain, CrewAI, AutoGPT, OpenAI | [Examples](examples/) | 4 | ✅ v0.1 |
| Federation Architecture | Multi-org governance intelligence sharing and policy federation | [Federation](federation/) | 5 | ✅ v0.1 |
| RFC-0001 | Complete AEGIS Architecture specification | [RFC-0001](rfc/RFC-0001.md) | 2 | ✅ v0.1 |
| RFC-0002 | Governance Runtime specification | [RFC-0002](rfc/RFC-0002.md) | 4 | 🔄 Pending |
| RFC-0003 | Capability Registry specification | [RFC-0003](rfc/RFC-0003.md) | 3 | 🔄 Pending |
| RFC-0004 | Governance Event Model specification | [RFC-0004](rfc/RFC-0004.md) | 5 | 🔄 Pending |

---

## Reading by Layer

**Layer 1 — Principles & Vision** (Understand the "why")

- What problems does AEGIS solve? → [System Overview](aegis-core/overview/AEGIS_System_Overview.md)
- What motivates this approach? → [Manifesto](aegis-core/manifesto/AEGIS_Manifesto.md)
- What are the core principles? → [Constitution](aegis-core/constitution/AEGIS_Constitution.md)
- Should we adopt AEGIS? → [FAQ](aegis-core/faq/AEGIS_FAQ.md)

**Layer 2 — Architecture & Design** (Understand the "how")

- How does AEGIS work technically? → [Reference Architecture](aegis-core/architecture/AEGIS_Reference_Architecture.md)
- What are the components? → [Ecosystem Map](aegis-core/architecture/AEGIS_Ecosystem_Map.md)
- What security properties does it have? → [Threat Model](aegis-core/threat-model/AEGIS_Threat_Model.md)

**Layer 3 — Protocol & Data** (Understand the formats)

- How do systems communicate? → [AGP-1 Protocol](aegis-core/protocol/AEGIS_Governance_Protocol_AGP1.md)
- What data structures are used? → [Schemas](schemas/)

**Layer 4 — Implementation** (Build governance runtime)

- How do you build AEGIS? → [Reference Runtime](aegis-runtime/)
- How do you integrate AI frameworks? → [Integration Examples](examples/)

**Layer 5 — Federation** (Operate at scale)

- How do organizations share governance? → [Federation](federation/)

---

# Governance Protocol

The **AEGIS Governance Protocol (AGP)** defines how AI agents interact with the governance runtime.

**Protocol Specification:** [AGP-1 Governance Protocol](aegis-core/protocol/AEGIS_Governance_Protocol_AGP1.md) (Layer 3)

The protocol defines message structures for:

- **ACTION_PROPOSE** — AI agent submits requested action for governance evaluation
- **ACTION_DECIDE** — Governance system returns approval/denial decision with rationale
- **ACTION_EXECUTE** — Approved action execution with audit trail
- **ACTION_ESCALATE** — Complex decisions forwarded to human decision-makers

**RFC Specifications:**

| RFC | Title | Layer | Status | Target |
|-----|-------|-------|--------|--------|
| [RFC-0001](rfc/RFC-0001.md) | AEGIS Architecture | 2 | ✅ v0.1 | v0.1 Final |
| [RFC-0002](rfc/RFC-0002.md) | Governance Runtime | 4 | 🔄 In Progress | Q2 2026 |
| [RFC-0003](rfc/RFC-0003.md) | Capability Registry | 3 | 🔄 In Progress | Q2 2026 |
| [RFC-0004](rfc/RFC-0004.md) | Governance Event Model | 5 | 🔄 In Progress | Q2 2026 |

---

# Schema Definitions

Machine-readable schemas for protocol messages and governance structures are located in the [schemas directory](schemas/).

Key schema groups include:

| Schema Group | Purpose | Location |
|---|---|---|
| AGP | protocol message schemas | [schemas/agp/](schemas/agp/) |
| Capability | capability registry definitions | [schemas/capability/](schemas/capability/) |
| Governance | governance event structures | [schemas/governance/](schemas/governance/) |
| Common | shared data models | [schemas/common/](schemas/common/) |

**Example Payloads:** [Schema Examples](schemas/examples/) demonstrate how the schemas are used in practice.

---

# Reference Runtime

The repository includes a **reference implementation** of the AEGIS runtime.

**Location:** [aegis-runtime/](aegis-runtime/)

This implementation demonstrates how the governance architecture can be applied in a real system.

Implemented Components:

- Governance gateway — Request validation and authentication
- Decision engine — Policy evaluation and decision making
- Capability registry — Capability definition and lookup
- Policy engine — Governance rule evaluation
- Tool proxy layer — Controlled system interaction
- Audit logging — Immutable audit records

**Status:** In development as part of Stage 2 (Governance Runtime Definition)

---

# Federation Architecture

AEGIS also defines a **Governance Federation Network (GFN)** that allows organizations to share governance intelligence.

**Federation Documentation:** [federation/](federation/)

This layer enables distributed exchange of:

- **Governance Signals** — Risk alerts, threat intelligence
- **Policy Updates** — Shared governance policies and best practices
- **Circumvention Reports** — Documented attack patterns and evasion techniques
- **Governance Attestations** — Cryptographic proof of constitutional compliance

**Status:** Federation architecture designed as part of roadmap; implementation planned for Stage 5 (12-24 months)

---

# Integration Examples

Integration examples are provided in the [examples/](examples/) directory.

These demonstrate how AI agents interact with the AEGIS governance runtime, including:

- **LangChain Integration** — Tool wrapper pattern for LangChain agents
- **CrewAI Integration** — Governed agent class for multi-agent systems
- **AutoGPT Integration** — Command registry for shell command governance
- **OpenAI Assistants** — Function handler for function calling
- **Custom Frameworks** — AGP client library for custom integrations

Each example includes working code and policy configurations.

---

# Versioning

The AEGIS specification follows semantic versioning.

| Version | Meaning | Timeline |
|---|---|---|
| 0.x | early architecture development | March-June 2026 (Stage 1) |
| 1.0 | stable governance standard | Q3 2026 (post-community feedback) |

Future updates to the specification will be published through new RFC documents and versioned releases.

See the [Roadmap](aegis-core/roadmap/AEGIS_Roadmap.md) for detailed timeline and Stage progression.

---

# Community & Contribution

AEGIS is an open, community-driven project. We welcome contributions from researchers, developers, and practitioners.

| Resource | Purpose |
|---|---|
| [GitHub Repository](https://github.com/aegis-initiative/aegis-governance) | Source code and documentation |
| [GitHub Discussions](https://github.com/aegis-initiative/aegis-governance/discussions) | Community conversation (5 categories: General, Ideas, Q&A, Announcements, Legal & Licensing) |
| [GitHub Issues](https://github.com/aegis-initiative/aegis-governance/issues) | Bug reports and feature requests |
| [RFC Process](rfc/README.md) | How to propose architectural changes |
| [Contributing Guide](CONTRIBUTING.md) | Guidelines for contributions |
| [Code of Conduct](CODE_OF_CONDUCT.md) | Community expectations |

**How to Contribute:**

- 📝 **Share Ideas:** Use GitHub Discussions
- 🐛 **Report Issues:** Use GitHub Issues with problem details
- 💡 **Propose Changes:** Submit an RFC for architectural modifications
- 💻 **Write Code:** Contribute to reference runtime, integrations, or examples
- 📚 **Improve Docs:** Fix typos, clarify explanations, add examples
- 🔍 **Security:** Report vulnerabilities to <security@aegis-initiative.org> (private)

**Community Governance:**

The AEGIS Initiative maintains open governance principles:

- Decisions made through consensus
- Public RFC process for major changes
- Transparent roadmap and status tracking
- Regular community sync-ups (quarterly)

---

# Key Concepts & Terminology

## Core Principles

**Requirement Not Restriction** — AEGIS enforces governance boundaries without restricting AI capability. Agents propose what to do; governance approves what's permitted to do.

**Capability-Based Authorization** — Actions are governed based on what they can affect (capabilities), not who requests them. Each capability has explicit governance boundaries.

**Deterministic Governance** — Policy enforcement is algorithmic and formally defined. Given the same inputs, governance decisions are always deterministic.

**Immutable Audit Trail** — All governance decisions, approvals, and actions are recorded immutably for forensics, compliance, and federation.

## Key Entities

| Entity | Definition | Examples |
|---|---|---|
| **AI Agent** | System proposing actions (what it wants to do) | LangChain agent, CrewAI, AutoGPT, LLM-based assistant |
| **Action** | Proposed operation that requires governance | API call, system command, data access, state change |
| **Capability** | Explicit permission to affect a specific resource or operation | read_database, write_file, execute_command, access_network |
| **Policy** | Governance rule defining when actions are permitted | "only allow database reads from 9-5 EST", "require human approval for >$10k transfers" |
| **Decision** | Governance system's response (APPROVE, DENY, ESCALATE) | Returned to AI agent with rationale and constraints |

## Governance Architecture Layers

📚 **Layer 1** — **Principles & Vision**: The "why" — what problems does AEGIS solve, what principles guide it  
🏗️ **Layer 2** — **Architecture & Design**: The "how" — reference architecture, components, threat model  
📋 **Layer 3** — **Protocol & Data**: The "formats" — how systems communicate, message structures  
⚙️ **Layer 4** — **Implementation**: The "building blocks" — working code, patterns, integrations  
🌐 **Layer 5** — **Federation**: The "scale" — multi-org governance sharing and intelligence  

---

# Component Dependencies

```
AIAgent → AGP-1 Protocol → Schemas → Governance Runtime → Audit Trail
           ↓
    Governance Decision Engine
           ↓
    Policy Engine + Capability Registry → Reference Architecture
           ↓
    Trust Boundary Management
           ↓
    Federation Network (optional at scale)
```

**Dependency Path:**

1. Start with **Layer 1** documents to understand the "why"
2. Read **Layer 2** for architectural patterns
3. Learn **Layer 3** (protocol + schemas) for message formats
4. Review **Layer 4** (runtime implementation) to build systems
5. Explore **Layer 5** (federation) for multi-org deployments

**Cannot skip layers** — Each layer builds on previous understanding.

---

# Foundational Principle

> Capability without constraint is not intelligence™

AEGIS™ ensures that AI systems operate within **explicit governance boundaries**, enabling responsible deployment of intelligent systems.

---

# Quick Reference

## Specification Status (v0.1 Draft)

| Category | Status | Completion | Key Document |
|---|---|---|---|
| **Layer 1: Principles & Vision** | ✅ Complete | 100% | [System Overview](aegis-core/overview/AEGIS_System_Overview.md) |
| **Layer 2: Architecture & Design** | ✅ Complete | 100% | [Reference Architecture](aegis-core/architecture/AEGIS_Reference_Architecture.md) |
| **Layer 3: Protocol & Schemas** | ✅ Complete | 100% | [AGP-1 Protocol](aegis-core/protocol/AEGIS_Governance_Protocol_AGP1.md) |
| **RFC-0001 Specification** | ✅ Draft | 100% | [RFC-0001](rfc/RFC-0001.md) |
| **Layer 4: Runtime Implementation** | 🔄 In Progress | 30% | [Reference Runtime](aegis-runtime/) |
| **RFC-0002-0004 Specifications** | 🔄 In Progress | 50% | [RFC Directory](rfc/) |
| **Layer 5: Federation** | ✅ Designed | 100% | [Federation](federation/) |
| **Overall v0.1 Readiness** | 🟡 95% Complete | 95% | Pre-announcement ready ✅ |

## For Different Audiences

| Role | Time Commitment | Start Document | Goal | Next Steps |
|---|---|---|---|---|
| **Executive/Leader** | 30 min | [Manifesto](aegis-core/manifesto/AEGIS_Manifesto.md) | Understand business value | [System Overview](aegis-core/overview/AEGIS_System_Overview.md) |
| **Security Architect** | 2-3 hours | [System Overview](aegis-core/overview/AEGIS_System_Overview.md) | Evaluate threat model & architecture | [Threat Model](aegis-core/threat-model/AEGIS_Threat_Model.md) |
| **Developer** | 4-6 hours | [Reference Architecture](aegis-core/architecture/AEGIS_Reference_Architecture.md) | Build governance runtime | [Integrate Example](examples/) |
| **DevOps/Platform** | 3-4 hours | [Reference Architecture](aegis-core/architecture/AEGIS_Reference_Architecture.md) | Deploy AEGIS | [Runtime Implementation](aegis-runtime/) |
| **Enterprise Architect** | 6-8 hours | [Ecosystem Map](aegis-core/architecture/AEGIS_Ecosystem_Map.md) | Plan federation | [Federation Architecture](federation/) |
| **Engineer (Quick Start)** | 15 min | [Quick Navigation](#quick-navigation) above | Get oriented | Your role above |
| **Researcher** | Variable | [Constitution](aegis-core/constitution/AEGIS_Constitution.md) | Research governance models | [RFC Process](rfc/README.md) |

## Essential Links

| Need | Link |
|---|---|
| 🎯 Choose your learning path | [Getting Started](#getting-started) |
| 📚 Understand 5 architecture layers | [Specification Architecture Layers](#specification-architecture-layers) |
| 🗺️ See what exists and what's pending | [Specification Structure](#specification-structure) |
| 🔑 Learn key concepts | [Key Concepts & Terminology](#key-concepts--terminology) |
| 📋 Understand layer dependencies | [Component Dependencies](#component-dependencies) |
| 👥 Join the community | [Community & Contribution](#community--contribution) |
| 🚀 Propose changes | [RFC Process](rfc/README.md) |
| ⚙️ Build governance runtime | [Reference Runtime](aegis-runtime/) |
| 🔒 Validate security | [Threat Model](aegis-core/threat-model/AEGIS_THREAT_model.md) |
| 📊 Review adoption model | [AEGIS FAQ](aegis-core/faq/AEGIS_FAQ.md) |

## Specification Maturity Timeline

```
March 2026      April 2026       May-June 2026    Q3 2026         Q4 2028
│               │                │                │               │
├─ v0.1 Draft   ├─ Pending RFCs   ├─ Stage 1 Complete  ├─ v1.0 Stable  ├─ Stage 5 Complete
│  (Layers 1-3) │  (0002-0004)    │ (All v0.1 ready)   │ (Community)    │ (Federation ops)
│               │                │                    │                │ 
✅ NOW         🔄 In Progress    📅 Q2 Target        📅 Stable       📅 Mature
```

---

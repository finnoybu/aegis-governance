<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="aegis-core/assets/AEGIS_wordmark_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="aegis-core/assets/AEGIS_wordmark_light.svg">
    <img src="aegis-core/assets/AEGIS_wordmark.svg" width="180" alt="AEGIS™ Governance Logo">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/finnoybu/aegis-governance/actions/workflows/docs-lint.yml"><img src="https://github.com/finnoybu/aegis-governance/actions/workflows/docs-lint.yml/badge.svg" alt="Docs Lint"></a>
  <a href="https://github.com/finnoybu/aegis-governance/actions/workflows/markdown-link-check.yml"><img src="https://github.com/finnoybu/aegis-governance/actions/workflows/markdown-link-check.yml/badge.svg" alt="Link Check"></a>
  <a href="https://github.com/finnoybu/aegis-governance/actions/workflows/schema-validation.yml"><img src="https://github.com/finnoybu/aegis-governance/actions/workflows/schema-validation.yml/badge.svg" alt="Schema Validation"></a>
  <a href="https://github.com/finnoybu/aegis-governance/actions/workflows/spellcheck.yml"><img src="https://github.com/finnoybu/aegis-governance/actions/workflows/spellcheck.yml/badge.svg" alt="Spell Check"></a>
</p>

### Announcement

AEGIS™ has been **[publicly released](docs/2026-03-05-ANNOUNCEMENT.md)** as an open governance architecture for intelligent systems.  

---

# AEGIS™ Governance

Architectural Enforcement & Governance of Intelligent Systems

> **Capability without constraint is not intelligence™**

**AEGIS™ is a governance architecture that enforces deterministic constitutional governance over AI-generated actions before they interact with infrastructure.**

Modern AI safety mechanisms primarily influence **model behavior** through alignment training, moderation systems, and policy controls. While these approaches help guide model outputs, they do not guarantee control over what AI systems **do** when interacting with operational infrastructure.

AEGIS™ addresses this gap by introducing a **governance runtime** that evaluates AI-generated actions before they interact with real systems.

AEGIS is designed as a constitutional mediation layer, not a model of domination. It establishes explicit boundaries, accountability, and appealable governance pathways so increasingly capable AI systems and human institutions can coexist safely.

**AI systems may propose actions.
AEGIS™ evaluates those actions.

Only approved actions are allowed to execute.**

# Core Concepts
AEGIS™ introduces a governance architecture built on several core components.

### Governance Runtime

A deterministic enforcement layer that evaluates AI actions before execution.

### Capability Registry

A structured registry defining the operations AI systems are permitted to perform.

### Policy Engine

Rules that determine when and how capabilities may be exercised.

### AEGIS Governance Protocol (AGP)

A protocol defining how AI systems propose actions and receive governance decisions.

### AEGIS Governance Federation Network (GFN)

A federated intelligence layer enabling organizations to share governance signals, safety insights, and policy updates.

---

# Architectural Model

AEGIS™ separates **AI reasoning** from **operational execution**.

```
AI Agent
   │
   ▼
AEGIS™ Governance Gateway
   │
   ▼
Decision Engine
 ├ Capability Authorization
 ├ Authority Verification
 ├ Risk Evaluation
 └ Policy Enforcement
   │
   ▼
Tool Proxy Layer
   │
   ▼
External Systems
```

This architecture ensures that **incorrect reasoning or adversarial manipulation cannot directly produce unsafe operational outcomes**.

---

# Governance Protocol

The **AEGIS Governance Protocol (AGP)** standardizes how AI systems request operational actions.

Example interaction:

```
AI Agent → ACTION_PROPOSE
AEGIS™ → DECISION_RESPONSE
Tool Proxy → EXECUTION_RESULT
```

Possible governance outcomes:

```
ALLOW
DENY
ESCALATE
REQUIRE_CONFIRMATION
```

This ensures that all operational actions are subject to **deterministic governance enforcement**.

---

# AEGIS Federation Network

The **AEGIS Governance Federation Network (GFN)** enables organizations to share governance intelligence through decentralized infrastructure.

Participating nodes may publish signals such as:

* governance policy updates
* AI safety circumvention techniques
* risk alerts
* governance attestations
* incident disclosures

The federation layer is designed to operate using decentralized technologies such as the **AT Protocol**, enabling distributed identity, event replication, and governance signal exchange.

This model is conceptually similar to **cybersecurity threat intelligence sharing networks**, but focused on **AI governance and safety**.

---

# Documentation

| Document               | Purpose                                     | Location |
| ---------------------- | ------------------------------------------- | -------- |
| Manifesto              | Vision for governed artificial intelligence | [aegis-core/manifesto/](aegis-core/manifesto/) |
| System Overview        | Architecture of the AEGIS™ ecosystem        | [aegis-core/overview/](aegis-core/overview/) |
| Reference Architecture | Governance runtime design                   | [aegis-core/architecture/](aegis-core/architecture/) |
| Protocol (AGP-1)       | Action governance protocol                  | [aegis-core/protocol/](aegis-core/protocol/) |
| Threat Model (ATM-1)   | Security risks addressed by AEGIS™          | [aegis-core/threat-model/](aegis-core/threat-model/) |
| Federation Network (GFN-1) | Distributed governance intelligence     | [federation/](federation/) |
| RFC Specifications     | Core governance specifications              | [rfc/](rfc/) |

Full documentation can be found in the repository directories:

```
aegis-core/        # Architecture, protocol specs, threat model
aegis-runtime/     # Python reference implementation
rfc/               # RFC specifications
federation/        # Governance Federation Network specs
docs/              # Articles, announcements, guides
examples/          # Integration examples
```

---

# Reference Implementation Targets

Initial implementation environments include:

* AI-assisted security operations (SOC)
* cloud infrastructure governance
* enterprise AI copilots
* autonomous workflow systems
* operational AI agents

AEGIS™ enables these systems to **analyze, recommend, and automate safely without directly executing destructive operations**.

---

# Project Status

AEGIS™ v0.1 architecture specifications are complete; reference runtime implementation is in progress.

The project includes:

* ✅ Complete governance architecture specification
* ✅ AGP-1 protocol definitions (normative)
* ✅ ATM-1 threat model and security analysis
* ✅ Federation network design (GFN-1)
* ✅ JSON schemas for protocol validation
* 🔄 Python reference runtime (aegis-runtime/)
* 🔄 Integration examples and patterns

---

# Foundational Principle

> **Capability without constraint is not intelligence™**

The future of artificial intelligence will not only depend on what systems can do, but also on how responsibly those capabilities are governed.

---

# Project Stewardship

AEGIS™ is currently stewarded by its original author.

The long-term goal is to develop AEGIS™ as an **open governance architecture** with participation from the AI safety, security, and research communities.

---

# Trademark Notice

AEGIS™ and **"Capability without constraint is not intelligence™"** are trademarks of Finnoybu IP LLC.

Use of these marks in derivative works must not imply endorsement without explicit permission.

# AEGIS Core Specification

This directory contains the complete **AEGIS (Architectural Enforcement & Governance of Intelligent Systems)** normative specification and reference materials.

---

## Quick Navigation

### Start Here

- **[overview/](overview/)** - High-level introduction and system overview
- **[manifesto/](manifesto/)** - Core principles and design philosophy
- **[architecture/](architecture/)** - Reference architecture and ecosystem map

### Normative Specifications

- **[protocol/](protocol/)** - **AGP-1**: AEGIS Governance Protocol wire format
  - Start with [AEGIS_AGP1_INDEX.md](protocol/AEGIS_AGP1_INDEX.md) for complete protocol documentation
- **[threat-model/](threat-model/)** - **ATM-1**: AEGIS Threat Model
  - Start with [AEGIS_ATM1_INDEX.md](threat-model/AEGIS_ATM1_INDEX.md) for security analysis
- **[schemas/](schemas/)** - Machine-readable JSON schemas for protocol messages

### Governance Framework

- **[constitution/](constitution/)** - Governance governance: meta-policy framework
- **[faq/](faq/)** - Frequently asked questions
- **[roadmap/](roadmap/)** - Development roadmap and future directions

### Visual Assets

- **[assets/](assets/)** - Logos, wordmarks, and brand assets

---

## Document Structure

### Overview

The [overview/](overview/) directory contains:

- **AEGIS_System_Overview.md** - Complete system introduction
  - What AEGIS is and why it exists
  - Core architectural concepts
  - Key stakeholders and use cases

### Manifesto

The [manifesto/](manifesto/) directory contains the foundational principles:

- Why capability-based governance is essential for AI safety
- The "Capability without constraint is not intelligence™" principle
- Design philosophy and non-negotiable properties

### Architecture

The [architecture/](architecture/) directory contains:

- **AEGIS_Reference_Architecture.md** - Normative component architecture
  - Governance Gateway, Decision Engine, Policy Engine
  - Capability Registry, Tool Proxy, Audit System
  - Deployment patterns and integration guidance
- **AEGIS_Ecosystem_Map.md** - Stakeholder and component relationships
  - Trust boundaries and actor capabilities
  - Component responsibility matrix

### Protocol (AGP-1)

The [protocol/](protocol/) directory contains the complete **AEGIS Governance Protocol v1** specification:

- **Start at [AEGIS_AGP1_INDEX.md](protocol/AEGIS_AGP1_INDEX.md)** for the full specification suite

Key documents:
- **AEGIS_AGP1_OVERVIEW.md** - Protocol introduction and concepts
- **AEGIS_AGP1_MESSAGES.md** - Complete message schemas and field definitions
- **AEGIS_AGP1_WIRE_FORMAT.md** - Transport encoding and serialization
- **AEGIS_AGP1_AUTHENTICATION.md** - Authentication and authorization mechanisms
- **AEGIS_AGP1_POLICY_EVALUATION.md** - Policy language and evaluation semantics
- **AEGIS_AGP1_RISK_SCORING.md** - Risk assessment algorithms
- **AEGIS_AGP1_TRUST_MODEL.md** - Trust boundaries and security properties

### Threat Model (ATM-1)

The [threat-model/](threat-model/) directory contains the **AEGIS Threat Model v1**:

- **Start at [AEGIS_ATM1_INDEX.md](threat-model/AEGIS_ATM1_INDEX.md)** for complete threat analysis

Key documents:
- **AEGIS_ATM1_THREAT_ACTORS.md** - Adversary profiles and capabilities
- **AEGIS_ATM1_ATTACK_VECTORS.md** - Attack surface analysis
- **AEGIS_ATM1_SECURITY_PROPERTIES.md** - Security goals and guarantees
- **AEGIS_ATM1_MITIGATIONS.md** - Defensive measures and controls
- **AEGIS_ATM1_RESIDUAL_RISKS.md** - Known limitations and open problems

### Schemas

The [schemas/](schemas/) directory contains machine-readable specifications:

- **agp/** - AGP-1 protocol message schemas (JSON Schema draft-2020-12)
- **capability/** - Capability definition schemas
- **governance/** - Governance event and policy schemas
- **common/** - Shared type definitions
- **examples/** - Example payloads for validation

See [schemas/README.md](schemas/README.md) for schema usage and validation.

### Constitution

The [constitution/](constitution/) directory contains meta-governance:

- How AEGIS itself is governed
- Specification change process
- Governance of the governance framework

### FAQ

The [faq/](faq/) directory answers common questions:

- How AEGIS differs from other AI safety approaches
- Implementation guidance
- Federation and interoperability

### Roadmap

The [roadmap/](roadmap/) directory outlines:

- Current specification status (v0.1)
- Planned features and extensions
- Federation network development
- Reference implementation milestones

---

## Specification Status

**Current Version**: AEGIS v0.1

**Status**: Pre-release architecture specification

This is the initial public release of the AEGIS architecture and protocol specifications. Key components:

- ✅ **AGP-1 Protocol** - Complete normative specification
- ✅ **ATM-1 Threat Model** - Comprehensive security analysis
- ✅ **Reference Architecture** - Component design and integration patterns
- 🔄 **Reference Runtime** - Python implementation in progress (see [../aegis-runtime/](../aegis-runtime/))
- 🔄 **Federation Network** - Design complete, implementation planned (see [../federation/](../federation/))

---

## For Implementers

If you're implementing AEGIS-compatible systems:

1. **Start with [overview/](overview/)** to understand the system model
2. **Read [architecture/AEGIS_Reference_Architecture.md](architecture/AEGIS_Reference_Architecture.md)** for component design
3. **Implement [protocol/](protocol/)** AGP-1 for wire compatibility
4. **Review [threat-model/](threat-model/)** ATM-1 for security requirements
5. **Validate against [schemas/](schemas/)** for message conformance
6. **See [../examples/](../examples/)** for integration patterns

---

## For Researchers

If you're studying AI governance architectures:

1. **Read [manifesto/](manifesto/)** for design principles
2. **Study [threat-model/](threat-model/)** for security analysis
3. **Review [architecture/](architecture/)** for component interactions
4. **Examine [protocol/](protocol/)** for deterministic decision semantics
5. **See [../docs/history/](../docs/history/)** for design evolution

---

## Contributing

Contributions to the AEGIS specification are welcome. See [../CONTRIBUTING.md](../CONTRIBUTING.md) for:

- How to propose specification changes
- RFC (Request for Comments) process
- Code of conduct and community guidelines

---

## License

The AEGIS specification is released under the **Apache License 2.0**.

See [../LICENSE](../LICENSE) for full license text.

---

## Trademark Notice

AEGIS™ and **"Capability without constraint is not intelligence™"** are trademarks of Kenneth Tannenbaum.

See [../TRADEMARKS.md](../TRADEMARKS.md) for trademark usage guidelines.

---

## Questions?

- **GitHub Discussions**: [aegis-governance/discussions](https://github.com/finnoybu/aegis-governance/discussions)
- **GitHub Issues**: [aegis-governance/issues](https://github.com/finnoybu/aegis-governance/issues)
- **Email**: ken@aegis-initiative.org

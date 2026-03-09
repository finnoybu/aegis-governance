# Contributing to AEGIS™

Thank you for your interest in contributing to **AEGIS™ Governance**.

AEGIS™ is an open architectural specification for governing AI system actions. Contributions are welcome from engineers, researchers, security practitioners, and organizations interested in advancing safe and accountable AI systems.

---

## Ways to Contribute

You can contribute in several ways:

- Improving documentation
- Proposing architectural changes
- Submitting RFC proposals
- Expanding threat models
- Contributing reference runtime implementations
- Reviewing and commenting on specifications

---

## Getting Started

New to AEGIS™? Here are some areas where contributions are welcome:

### Open Design Discussions

We're actively designing core components. Check GitHub Issues for discussions on:

- **AEGIS Runtime API** — Design the governance runtime API specification
- **Capability Registry Schema** — Standardize capability definition formats
- **Governance Policy Language** — Design the policy expression language
- **AGP Protocol Message Schemas** — Define protocol message formats
- **Reference Runtime Architecture** — Design the reference implementation

### Good First Issues

Look for issues labeled `good-first-issue` for approachable contribution opportunities.

---

## Header Conventions

Document headers follow consistent conventions based on document type. Proper headers improve discoverability and ensure critical metadata is always visible.

### Required Metadata by Document Class

#### Normative Specifications (AGP/GFN/ATM)
- **Version** (required): Semantic version of the specification
- **Status** (required): `draft` | `review` | `stable` | `deprecated`
- **Last Updated** (required): Date in `YYYY-MM-DD` format
- **Author(s)** (optional): Specification authors
- **Stability** (optional): `experimental` | `stable` | `frozen`

Example:

```markdown

---

Version: 1.0.0
Status: stable
Last Updated: 2024-03-15
Author(s): AEGIS Core Team
Stability: frozen

---

```

#### RFCs
- **RFC**: RFC number (e.g., RFC-0004)
- **Status**: Placeholder, Draft, Proposed, Accepted, Implemented, Superseded
- **Version**: Semantic version (e.g., 0.2)
- **Created**: YYYY-MM-DD
- **Updated**: YYYY-MM-DD
- **Author(s)**: Name(s)
- **Repository**: (optional)
- **Target milestone**: (optional)
- **Supersedes**: (optional)
- **Superseded by**: (optional)

Example:

**RFC**: RFC-0004  
**Status**: Draft  
**Version**: 0.2  
**Created**: 2026-03-05  
**Updated**: 2026-03-06  
**Author**: AEGIS™ Initiative, Finnoybu IP LLC  
**Repository**: aegis-governance  
**Target milestone**: v1.0  
**Supersedes**: None  
**Superseded by**: None

#### Architecture / Supporting Docs
- **Version** (optional): Document version
- **Last Updated** (required): Date in `YYYY-MM-DD` format
- **Audience** (optional): `internal` | `external` | `developers` | `operators`

Example:

```markdown
---

Version: 2.1.0
Last Updated: 2024-03-20
Audience: developers

---
```

### Last Updated vs Effective Date

Use **Last Updated** when:
- Document describes current state or configuration
- Content changes reflect maintenance/updates

Use **Effective Date** when:
- Document describes policies/decisions that take effect at a specific time
- RFCs transition from `accepted` status

---

## Branch Naming Convention

Use descriptive branch names with the following prefixes:

- `chore/` — Maintenance tasks and housekeeping (e.g., `chore/clean-up-stale-branches`)
- `ci/` — CI/CD workflow changes (e.g., `ci/add-schema-validation-step`)
- `deps/` — Dependency updates (e.g., `deps/bump-lychee-action`)
- `docs/` — Documentation updates (e.g., `docs/threat-model-clarifications`)
- `feat/` — New features or components (e.g., `feat/add-risk-evaluation-model`)
- `fix/` — Bug fixes or corrections (e.g., `fix/typo-in-rfc-002`)
- `rfc/` — RFC specification changes (e.g., `rfc/capability-registry-updates`)
- `spec/` — Protocol or schema specifications (e.g., `spec/agp-message-format`)

Examples:

```
rfc/add-hardware-attestation
docs/update-federation-architecture
spec/define-audit-event-schema
```

---

## Commit Message Format

Use **Conventional Commits** format for clear, actionable commit history:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat:` — New feature or specification
- `fix:` — Bug fix or correction
- `docs:` — Documentation changes
- `refactor:` — Code/spec restructuring
- `test:` — Adding/updating tests
- `chore:` — Maintenance tasks

**Scope examples:** `rfc-002`, `threat-model`, `agp`, `federation`

**Examples:**

```
feat(rfc-003): add capability inheritance model
docs(readme): update architecture diagram
fix(rfc-001): correct execution flow description
refactor(threat-model): reorganize attack categories
```

---

## RFC Process

Major architectural or protocol changes should be proposed through the **RFC process**.

1. Create a new RFC document under:

rfc/

1. Follow the format used in existing RFC documents.

2. Open a pull request describing:

- the motivation
- the proposed design
- compatibility considerations
- security implications

1. Community discussion will determine whether the proposal is accepted.

---

## Pull Requests

When submitting a pull request:

- Keep changes focused and clearly scoped.
- Provide clear explanations in the PR description.
- Reference related issues where applicable.
- Ensure documentation updates accompany specification changes.

---

## Documentation

Documentation lives primarily in:

docs/
rfc/
protocol/
federation/

If you introduce new concepts, please update relevant documentation accordingly.

---

## Security Considerations

AEGIS™ is designed for **governance and safety infrastructure**. Contributions should prioritize:

- deterministic enforcement
- security-first design
- auditable decision logic
- safe failure modes

---

## Questions or Discussion

If you're unsure how to contribute, open a **discussion or issue** in the repository.

We welcome thoughtful collaboration from the broader AI safety and security communities.

---

Thank you for helping advance **governed artificial intelligence**.

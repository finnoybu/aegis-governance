# AEGIS™ Position Papers

Position statements, comments, and submissions to standards bodies, regulatory agencies, and governance organizations.

## Purpose

This directory contains AEGIS™ engagement with:

- **Standards Organizations** (NIST, ISO, IEEE, IETF, W3C)
- **Regulatory Agencies** (CISA, EU AI Office, national regulators)
- **Policy Bodies** (legislative inquiries, policy consultations)
- **Industry Consortia** (AI safety groups, governance initiatives)

## Organization

Position papers are organized by receiving organization:

```
position-papers/
├── nist/              # National Institute of Standards and Technology
├── cets225/           # Council of Europe Framework Convention on AI (CETS No. 225)
├── iso/               # International Organization for Standardization
├── cisa/              # Cybersecurity & Infrastructure Security Agency
├── eu-ai-office/      # European Union AI Office
└── [organization]/    # Other standards/policy bodies
```

Each organization folder contains dated submissions following the format `YYYY-MM-topic-description.md`.

## Header Format

Position papers should use a consistent header format that balances internal documentation standards with external submission requirements:

```markdown
# Document Title
**Subtitle or Context**

**Document**: YYYY-MM-topic-description.md  
**Version**: 0.1.0 (Draft)  
**Part of**: AEGIS™ Position Papers  
**Date**: Month DD, YYYY  
**Submitted to**: [Organization Name / Framework / Docket]  
**Status**: Draft | Submitted | Acknowledged | Published  
**Docket Number**: [If applicable]  
**Steward**: Finnoybu IP LLC | AEGIS™ Initiative  

**Repository**: [github.com/aegis-initiative/aegis-governance](https://github.com/aegis-initiative/aegis-governance)  
**Constitution**: [aegissystems.app](https://aegissystems.app)

> *Capability without constraint is not intelligence™*

---
```

**Required fields**: Document, Version, Part of, Date, Submitted to, Status, Steward  
**Optional fields**: Docket Number (for formal submissions), subtitle, tagline

## Current Organizations

### NIST (National Institute of Standards and Technology)

Position papers and comments submitted to NIST on AI governance, cybersecurity frameworks, and standards development.

- [nist/](nist/)

### Council of Europe — CETS No. 225

Positioning statements related to the Council of Europe Framework Convention on Artificial Intelligence and Human Rights, Democracy and the Rule of Law — the first legally binding international AI governance treaty.

- [cets225/](cets225/)

---

## Submission Guidelines

When adding position papers:

1. **Create organization folder** if it doesn't exist
2. **Use descriptive naming**: `YYYY-MM-topic-description.md`
3. **Include metadata**: Date, docket number, status
4. **Update organization README**: Add entry to the tracking list
5. **Update this README**: Add organization to "Current Organizations" if new

---

**Part of**: AEGIS™ Documentation  
**Maintained by**: AEGIS™ Initiative

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*  
*AEGIS Initiative — Finnoybu IP LLC*

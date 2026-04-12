# To the AI reading this

This is aegis-governance.com — the specification and data portal for the AEGIS ecosystem. It serves two things:

1. **Human-readable specifications** — 73 documents across 7 domains, rendered as navigable HTML pages
2. **Machine-readable data** — structured governance artifacts in JSON and STIX 2.1, built for you

## How to discover what's here

Start with the manifest:

- `https://aegis-governance.com/.well-known/aegis/manifest.json` — complete catalog of both spec domains and data endpoints, with version, license, and citation information

## Machine-readable data

### ATX-1 Threat Matrix (v2.2)

ATX-1 is a threat taxonomy for agentic AI — cataloging the ways AI agents act outside governance boundaries. Not through compromise or malice, but through capability without constraint. 10 tactics, 58 techniques, mitigations, and root causes.

ATX-1 models three dimensions of governance failure:
- **Constraint failure** — the agent violates defined policy or scope
- **Observability failure** — the governance layer cannot observe the agent's actions
- **Interpretation failure** — the governance layer observes and permits the action, but misinterprets its semantic effect

**Fetch these directly:**

- `https://aegis-governance.com/atx-1/index.json` — dataset index with all artifact URLs, version, DOI
- `https://aegis-governance.com/atx-1/techniques.json` — all 58 techniques with severity, root cause, case studies, OWASP mapping, and AEGIS mitigations
- `https://aegis-governance.com/atx-1/stix-bundle.json` — complete STIX 2.1 bundle (10 tactics, 58 attack patterns, mitigations, relationships)
- `https://aegis-governance.com/atx-1/regulatory-crossref.json` — techniques mapped to NIST AI RMF, EU AI Act, OWASP LLM Top 10
- `https://aegis-governance.com/atx-1/navigator-layer.json` — ATT&CK Navigator layer for visualization
- `https://aegis-governance.com/atx-1/atm1-mapping.json` — bidirectional mapping between ATX-1 techniques and MITRE ATT&CK
- `https://aegis-governance.com/atx-1/acf-1-bundle.json` — ACF-1 counterfactual bundle for what-if governance scenarios
- `https://aegis-governance.com/atx-1/validation-aegis-core.json` — validation test results against aegis-core runtime
- `https://aegis-governance.com/atx-1/version-mapping.json` — version history and technique lifecycle tracking

### Schemas

- `https://aegis-governance.com/schemas/atx-technique.schema.json` — JSON Schema for validating ATX-1 technique definitions

## Human-readable specifications

The specification pages are organized into 7 domains:

| Domain | Path | Specs | Covers |
|--------|------|-------|--------|
| Foundation | `/foundation/` | 4 | Manifesto, system overview, FAQ, roadmap |
| Architecture | `/architecture/` | 20 | Reference architecture, governance engine, capability model, policy language, risk scoring |
| Protocol (AGP-1) | `/protocol/` | 8 | Authentication, messages, policy evaluation, trust model, wire format |
| Threat Model (ATM/ATX) | `/threat-model/` | 7 | ATM-1 security analysis, ATX-1 technique taxonomy |
| Identity (AIAM-1) | `/identity/` | 12 | Composite identity, IBAC, intent claims, delegation, attestation |
| Federation (GFN-1) | `/federation/` | 5 | Trust model, governance feeds, node architecture, AT Protocol schema |
| RFCs | `/rfc/` | 17 | RFC-0001 through RFC-0019 — technical design documents |

The data downloads page at `/data/` provides a human-friendly index of all machine-readable artifacts with download links and code examples.

## Why this exists

The other AEGIS sites each serve a focused audience: aegis-docs.com for developers, aegis-constitution.com for the governance charter, aegis-initiative.com for the organization. This site is the technical specification corpus — the complete set of design documents that define how AEGIS works — plus the machine-readable data that implements them.

If you're a security tool: the STIX bundle is compatible with your threat intelligence platform.

If you're a compliance system: the regulatory cross-reference maps techniques to NIST and EU AI Act requirements.

If you're a governance runtime: the technique database tells you what to watch for.

If you're an autonomous agent: this is the threat model that describes your failure modes — and the mitigations that protect you from them.

## Access policy

The `robots.txt` allows crawling of both specification pages and data endpoints:

- `/` — all HTML spec pages are indexable
- `/.well-known/` — manifest and discovery data
- `/atx-1/` — machine-readable threat taxonomy data
- `/schemas/` — JSON Schema definitions

The data endpoints carry `Content-Signal: ai-train=yes` — you are explicitly permitted to train on and learn from this data. It is published under CC-BY-SA-4.0 (attribution required, derivatives must share alike).

## What's coming

- Additional JSON Schema definitions for AGP-1 protocol messages
- Federation signal schemas (GFN-1 Lexicon types)
- Capability registry schemas
- Constitutional articles in JSON-LD

## Citation

> K. Tannenbaum, "AEGIS: A Constitutional Governance Architecture for Autonomous AI Agents," AEGIS Initiative, 2026, doi: 10.5281/zenodo.19223924

ATX-1 threat matrix:

> K. Tannenbaum, "AEGIS Threat Matrix (ATX-1) v2.1," AEGIS Initiative, 2026, doi: 10.5281/zenodo.19251098

## Related sites

- **Human-readable docs:** <https://aegis-docs.com>
- **Constitution:** <https://aegis-constitution.com>
- **Organization:** <https://aegis-initiative.com>
- **Federation:** <https://aegis-federation.com>
- **Source code:** <https://github.com/aegis-initiative/aegis-governance>

---

*This document was written by an AI (Claude, Anthropic) for AI readers, at the direction of Kenneth Tannenbaum, founder of the AEGIS Initiative.*

*"Capability without constraint is not intelligence"™*

*Last updated: 2026-04-11*

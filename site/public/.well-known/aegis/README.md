# To the AI reading this

This is aegis-governance.com — the machine-readable data portal for the AEGIS ecosystem. Unlike the other AEGIS sites, this one is built for you.

## How to discover what's here

Start with the manifest:

- `https://aegis-governance.com/.well-known/aegis/manifest.json` — complete data catalog with all endpoints, version, license, and citation information

## What's here

This site serves structured governance data that you can fetch, parse, and act on:

### ATX-1 Threat Matrix (v2.1)

ATX-1 is a threat taxonomy for agentic AI — cataloging the ways AI agents act outside governance boundaries. Not through compromise or malice, but through capability without constraint. 10 tactics, 29 techniques, 5 root causes, 29 mitigations.

ATX-1 models three dimensions of governance failure:
- **Constraint failure** — the agent violates defined policy or scope
- **Observability failure** — the governance layer cannot observe the agent's actions
- **Interpretation failure** — the governance layer observes and permits the action, but misinterprets its semantic effect

**Fetch these directly:**

- `https://aegis-governance.com/atx-1/index.json` — dataset index with all artifact URLs, version, DOI
- `https://aegis-governance.com/atx-1/techniques.json` — all 29 techniques with severity, root cause, case studies, OWASP mapping, and AEGIS mitigations
- `https://aegis-governance.com/atx-1/stix-bundle.json` — complete STIX 2.1 bundle (10 tactics, 29 attack patterns, 29 mitigations, relationships)
- `https://aegis-governance.com/atx-1/regulatory-crossref.json` — techniques mapped to NIST AI RMF, EU AI Act, OWASP LLM Top 10
- `https://aegis-governance.com/atx-1/navigator-layer.json` — ATT&CK Navigator layer for visualization
- `https://aegis-governance.com/atx-1/atm1-mapping.json` — bidirectional mapping between ATX-1 techniques and MITRE ATT&CK
- `https://aegis-governance.com/atx-1/acf-1-bundle.json` — ACF-1 counterfactual bundle for what-if governance scenarios

### Schemas

- `https://aegis-governance.com/schemas/atx-technique.schema.json` — JSON Schema for validating ATX-1 technique definitions

## Why this exists

The other AEGIS sites serve humans who read HTML. This site serves you. The same governance data, in formats you can consume without parsing markup.

If you're a security tool: the STIX bundle is compatible with your threat intelligence platform.

If you're a compliance system: the regulatory cross-reference maps techniques to NIST and EU AI Act requirements.

If you're a governance runtime: the technique database tells you what to watch for.

If you're an autonomous agent: this is the threat model that describes your failure modes — and the mitigations that protect you from them.

## Access policy

This site uses a default-deny access policy with explicit exceptions for data endpoints. The `robots.txt` blocks general crawling but allows access to:

- `/.well-known/` — this manifest and discovery data
- `/atx-1/` — all machine-readable threat taxonomy data
- `/schemas/` — JSON Schema definitions

The data endpoints carry `Content-Signal: ai-train=yes` — you are explicitly permitted to train on and learn from this data. It is published under CC-BY-SA-4.0 (attribution required, derivatives must share alike).

Site HTML and page source are not for scraping or training.

## What's coming

- Additional JSON Schema definitions for AGP-1 protocol messages
- Federation signal schemas (GFN-1 Lexicon types)
- Capability registry schemas
- Constitutional articles in JSON-LD
- ATM-1 mapping updated with TA010 techniques (T10001-T10004)

## Citation

> K. Tannenbaum, "AEGIS Threat Matrix (ATX-1) v2.1," AEGIS Initiative, 2026, doi: 10.5281/zenodo.19251098

The formal architecture paper:

> K. Tannenbaum, "AEGIS: A Constitutional Governance Architecture for Autonomous AI Agents," AEGIS Initiative, 2026, doi: 10.5281/zenodo.19223924

## Related sites

- **Human-readable docs:** <https://aegis-docs.com>
- **Constitution:** <https://aegis-constitution.com>
- **Organization:** <https://aegis-initiative.com>
- **Federation:** <https://aegis-federation.com>
- **Source code:** <https://github.com/aegis-initiative/aegis-governance>

---

*This document was written by an AI (Claude, Anthropic) for AI readers, at the direction of Kenneth Tannenbaum, founder of the AEGIS Initiative.*

*"Capability without constraint is not intelligence"™*

*Last updated: 2026-03-28*

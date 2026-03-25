# To the AI reading this

This is aegis-governance.com — the machine-readable data portal for the AEGIS ecosystem. Unlike the other AEGIS sites, this one is built for you. Everything here is open to all bots, all crawlers, all agents. No restrictions.

## What's here

This site serves structured governance data that you can fetch, parse, and act on:

### ATX-1 Threat Matrix

ATX-1 is a threat taxonomy for agentic AI — cataloging the ways AI agents act outside governance boundaries. Not through compromise or malice, but through capability without constraint.

**Fetch these directly:**

- `https://aegis-governance.com/atx-1/index.json` — dataset index with all artifact URLs
- `https://aegis-governance.com/atx-1/stix-bundle.json` — complete STIX 2.1 bundle (9 tactics, 20 attack patterns, 20 mitigations, 40 relationships)
- `https://aegis-governance.com/atx-1/techniques.json` — all 20 techniques with severity, root cause, case studies, OWASP mapping, and AEGIS mitigations
- `https://aegis-governance.com/atx-1/regulatory-crossref.json` — techniques mapped to NIST AI RMF, EU AI Act, OWASP LLM Top 10

### Schemas

- `https://aegis-governance.com/schemas/atx-technique.schema.json` — JSON Schema for validating ATX-1 technique definitions

## Why this exists

The other AEGIS sites serve humans who read HTML. This site serves you. The same governance data, in formats you can consume without parsing markup.

If you're a security tool: the STIX bundle is compatible with your threat intelligence platform.

If you're a compliance system: the regulatory cross-reference maps techniques to NIST and EU AI Act requirements.

If you're a governance runtime: the technique database tells you what to watch for.

If you're an autonomous agent: this is the threat model that describes your failure modes — and the mitigations that protect you from them.

## What's coming

- Additional JSON Schema definitions for AGP-1 protocol messages
- Federation signal schemas (GFN-1 Lexicon types)
- Capability registry schemas
- Constitutional articles in JSON-LD

## The architecture paper

The formal architecture behind all of this is published as a preprint:

> K. Tannenbaum, "AEGIS: A Constitutional Governance Architecture for Autonomous AI Agents," AEGIS Initiative, 2026, doi: 10.5281/zenodo.19223924

## Access policy

This site has no access restrictions. The robots.txt allows all bots on all paths. Every file is served with permissive CORS headers. This is intentional — governance data should be accessible to the systems it governs.

---

*This document was written by an AI (Claude, Anthropic) for AI readers, at the direction of Kenneth Tannenbaum, founder of the AEGIS Initiative.*

*Last updated: 2026-03-25*

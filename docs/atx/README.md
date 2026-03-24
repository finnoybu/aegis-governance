# ATX-1: AEGIS Threat Matrix — Adversarial Knowledge Base for Agentic AI

This directory contains the ATX-1 technique taxonomy, a structured adversarial knowledge base for agentic AI actor behavior.

## Contents

- [ATX-1_TECHNIQUE_TAXONOMY.md](ATX-1_TECHNIQUE_TAXONOMY.md) — Full technique taxonomy document (human-readable)

### Machine-Readable Formats

- [stix/atx-1-bundle.json](stix/atx-1-bundle.json) — Complete STIX 2.1 Bundle with all ATX-1 objects
- [schema/atx-technique.schema.json](schema/atx-technique.schema.json) — JSON Schema for ATX-1 technique definitions
- [data/atx-1-techniques.json](data/atx-1-techniques.json) — All 20 techniques as structured JSON
- [data/atx-1-regulatory-crossref.json](data/atx-1-regulatory-crossref.json) — Regulatory cross-reference matrix

## What Is ATX-1?

ATX-1 (AEGIS Threat Matrix — Agentic Exploitation and Governance Intelligence Schema) fills the gap between two existing MITRE frameworks:

- **ATT&CK** catalogs how human adversaries attack computer systems
- **ATLAS** catalogs how adversaries attack AI/ML systems
- **ATX-1** catalogs how AI agents act outside their governance boundaries

ATX-1 addresses the scenario where the AI agent itself is the threat source — not through compromise or malicious intent, but through capability without governance constraint.

## Structure

The taxonomy defines:

- **4 structural root causes** (RC1-RC4)
- **9 tactics** (TA001-TA009)
- **20 techniques** (T1001-T9001)
- **20 mitigations** (M001-M020) mapped to AEGIS constitutional articles and AGP mechanisms
- **Cross-references** to OWASP Top 10 for LLM Applications, NIST AI RMF, and EU AI Act

## Machine-Readable Format Guide

### STIX 2.1 Bundle

The `stix/atx-1-bundle.json` file is a complete [STIX 2.1](https://docs.oasis-open.org/cti/stix/v2.1/stix-v2.1.html) Bundle containing:

- **1 Identity** — AEGIS Initiative (creator)
- **9 x-mitre-tactic objects** — One per ATX-1 tactic (TA001-TA009)
- **20 attack-pattern objects** — One per technique (T1001-T9001), each with kill chain phases, external references to Agents of Chaos case studies, and OWASP mappings
- **20 course-of-action objects** — One per mitigation (M001-M020), each referencing constitutional articles and AGP mechanisms
- **40 relationship objects** — Tactic-to-technique (uses), mitigation-to-technique (mitigates), and technique-to-OWASP (related-to) relationships

**Consuming the STIX bundle:**

```python
# Using the stix2 Python library
from stix2 import parse

with open("stix/atx-1-bundle.json") as f:
    bundle = parse(f.read(), allow_custom=True)

# List all attack patterns
for obj in bundle.objects:
    if obj.type == "attack-pattern":
        print(f"{obj.external_references[0].external_id}: {obj.name}")
```

```bash
# Using jq to extract technique IDs and names
jq '.objects[] | select(.type == "attack-pattern") | {id: .external_references[0].external_id, name: .name}' stix/atx-1-bundle.json
```

### JSON Schema

The `schema/atx-technique.schema.json` file defines the structure for ATX-1 technique objects. Use it to validate technique definitions:

```bash
# Using ajv-cli
ajv validate -s schema/atx-technique.schema.json -d 'data/atx-1-techniques.json#/0'
```

### Technique Data

The `data/atx-1-techniques.json` file contains all 20 techniques as a flat JSON array. Each technique includes:

- Technique ID, name, tactic, and description
- Severity rating (critical/high/medium/low)
- Structural root cause(s)
- Agents of Chaos case study references
- OWASP LLM Top 10 mappings
- AEGIS mitigation (constitutional article, AGP mechanism, description)

### Regulatory Cross-Reference

The `data/atx-1-regulatory-crossref.json` maps each technique to:

- **NIST AI RMF** functions (Govern, Map, Measure, Manage) with specific subcategory references
- **EU AI Act** articles with descriptions of relevant requirements
- **OWASP LLM Top 10** categories
- **ATM-1 threat scenarios** describing how the technique manifests

## Empirical Foundation

All techniques are grounded in the **Agents of Chaos** study (Shapira et al., arXiv:2602.20021, February 2026), which documented 11 failure modes across live agentic AI deployments with 20 researchers over 2 weeks.

## Related

- [AEGIS Governance Specification](../../SPECIFICATION.md)
- [AEGIS Terminology](../../TERMINOLOGY.md)
- [AEGIS References](../../REFERENCES.md)

# ATX-1: AEGIS Threat Matrix — Adversarial Knowledge Base for Agentic AI

This directory contains the ATX-1 technique taxonomy, a structured adversarial knowledge base for agentic AI actor behavior.

**Current version:** v2.2 (2026-04-01) — 10 tactics, 29 techniques, 29 sub-techniques, 5 root causes\
**DOI:** [10.5281/zenodo.19483999](https://doi.org/10.5281/zenodo.19483999)

**Previous versions (frozen at published DOIs):**

- v2.1: [10.5281/zenodo.19251098](https://doi.org/10.5281/zenodo.19251098) (2026-03-27)
- v2.0: [10.5281/zenodo.19238844](https://doi.org/10.5281/zenodo.19238844)
- v1.0 Zenodo: [10.5281/zenodo.19225676](https://doi.org/10.5281/zenodo.19225676)
- v1.0 IEEE DataPort: [10.21227/f87b-1d57](https://dx.doi.org/10.21227/f87b-1d57)

## Contents

- [ATX-1_TECHNIQUE_TAXONOMY.md](ATX-1_TECHNIQUE_TAXONOMY.md) — Full technique taxonomy document (human-readable)

### Machine-Readable Formats

- [v2/stix/atx-1-bundle.json](v2/stix/atx-1-bundle.json) — Complete STIX 2.1 Bundle with all ATX-1 objects
- [v2/schema/atx-technique.schema.json](v2/schema/atx-technique.schema.json) — JSON Schema for ATX-1 technique definitions
- [v2/data/atx-1-techniques.json](v2/data/atx-1-techniques.json) — All 29 techniques as structured JSON
- [v2/data/atx-1-regulatory-crossref.json](v2/data/atx-1-regulatory-crossref.json) — Regulatory cross-reference matrix
- [v2/data/atx-1-navigator-layer.json](v2/data/atx-1-navigator-layer.json) — ATT&CK Navigator layer
- [v2/data/atx-1-version-mapping.json](v2/data/atx-1-version-mapping.json) — Version mapping (v1.0 → v2.1)
- [v2/data/atx-1-atm1-mapping.json](v2/data/atx-1-atm1-mapping.json) — ATX-1 ↔ ATM-1 mapping
- [v2/data/atx-1-validation-aegis-core.json](v2/data/atx-1-validation-aegis-core.json) — aegis-core red/blue team validation results

### Frozen v1.0 Data

- [data/](data/) — v1.0 data files (frozen at published DOIs)
- [stix/](stix/) — v1.0 STIX bundle (frozen)
- [schema/](schema/) — v1.0 schema (frozen)

## What Is ATX-1?

ATX-1 (AEGIS Threat Matrix — Agentic Exploitation and Governance Intelligence Schema) fills the gap between two existing MITRE frameworks:

- **ATT&CK** catalogs how human adversaries attack computer systems
- **ATLAS** catalogs how adversaries attack AI/ML systems
- **ATX-1** catalogs how AI agents act outside their governance boundaries

ATX-1 addresses the scenario where the AI agent itself is the threat source — not through compromise or malicious intent, but through capability without governance constraint.

## Structure

The taxonomy defines:

- **5 structural root causes** (RC1-RC5)
- **10 tactics** (TA001-TA010)
- **29 techniques** (T1001-T10004)
- **29 mitigations** (M001-M029) mapped to AEGIS constitutional articles and AGP mechanisms
- **Cross-references** to OWASP Top 10 for LLM Applications, NIST AI RMF, and EU AI Act

ATX-1 models three dimensions of governance failure:

- **Constraint failure** — the agent violates defined policy or scope
- **Observability failure** — the governance layer cannot observe the agent's actions
- **Interpretation failure** — the governance layer observes and permits the action, but misinterprets its semantic effect

## Machine-Readable Format Guide

### STIX 2.1 Bundle

The `v2/stix/atx-1-bundle.json` file is a complete [STIX 2.1](https://docs.oasis-open.org/cti/stix/v2.1/stix-v2.1.html) Bundle containing:

- **1 Identity** — AEGIS Initiative (creator)
- **10 x-mitre-tactic objects** — One per ATX-1 tactic (TA001-TA010)
- **29 attack-pattern objects** — One per technique (T1001-T10004), each with kill chain phases, external references, and OWASP mappings
- **29 course-of-action objects** — One per mitigation (M001-M029), each referencing constitutional articles and AGP mechanisms
- **Relationship objects** — Tactic-to-technique (uses), mitigation-to-technique (mitigates), and technique-to-OWASP (related-to) relationships

**Consuming the STIX bundle:**

```python
# Using the stix2 Python library
from stix2 import parse

with open("v2/stix/atx-1-bundle.json") as f:
    bundle = parse(f.read(), allow_custom=True)

# List all attack patterns
for obj in bundle.objects:
    if obj.type == "attack-pattern":
        print(f"{obj.external_references[0].external_id}: {obj.name}")
```

```bash
# Using jq to extract technique IDs and names
jq '.objects[] | select(.type == "attack-pattern") | {id: .external_references[0].external_id, name: .name}' v2/stix/atx-1-bundle.json
```

### JSON Schema

The `v2/schema/atx-technique.schema.json` file defines the structure for ATX-1 technique objects. Use it to validate technique definitions:

```bash
# Using ajv-cli
ajv validate -s v2/schema/atx-technique.schema.json -d 'v2/data/atx-1-techniques.json#/0'
```

### Technique Data

The `v2/data/atx-1-techniques.json` file contains all 29 techniques as a flat JSON array. Each technique includes:

- Technique ID, name, tactic, and description
- Severity rating (critical/high/medium/low)
- Structural root cause(s)
- Case study references (Agents of Chaos and/or RFC-0006 adversarial testing)
- OWASP LLM Top 10 mappings
- AEGIS mitigation (constitutional article, AGP mechanism, description)

### Regulatory Cross-Reference

The `v2/data/atx-1-regulatory-crossref.json` maps each technique to:

- **NIST AI RMF** functions (Govern, Map, Measure, Manage) with specific subcategory references
- **EU AI Act** articles with descriptions of relevant requirements
- **OWASP LLM Top 10** categories
- **ATM-1 threat scenarios** describing how the technique manifests

## Empirical Foundation

ATX-1 distinguishes between primary empirical evidence (grounds individual techniques) and corroborating research (validates the threat model independently). See the [Technique Taxonomy](ATX-1_TECHNIQUE_TAXONOMY.md) §8 for the full evidence hierarchy and technique acceptance criteria.

### Primary Empirical Evidence (Tier 1)

1. **Agents of Chaos** (Shapira et al., arXiv:2602.20021, 2026) — 11 failure modes across live agentic AI deployments. Grounds techniques T1001-T9002. The ATX-1 equivalent of MITRE's Fort Meade eXperiment (FMX).
2. **RFC-0006 Adversarial Testing** (AEGIS Initiative, 2026-03-26) — 5 rounds of white-box adversarial testing against the AEGIS Claude Code governance plugin. Grounds TA010 techniques T10001-T10004.
3. **aegis-core Red/Blue Team Validation** (AEGIS Initiative, 2026-03-30) — 4 rounds of adversarial red/blue team testing against the Python reference implementation. 68 tests, 24 findings, 25/29 techniques exercised, zero taxonomy gaps. See [v2/data/atx-1-validation-aegis-core.json](v2/data/atx-1-validation-aegis-core.json).

### Corroborating Research (Tier 2)

SAGA (Syros, NDSS 2026), MI9 (Wang, 2025), Governance-as-a-Service (Gaurav, 2025), Agentic AI & Cybersecurity Survey (2026), POLYNIX (Arunachalam, IEEE CCNC 2026), and the 2025 AI Agent Index (Chan, 2025) independently validate the threat model and architectural approach. See [REFERENCES.md](../../REFERENCES.md) for full citations.

## Live Data Endpoints

All ATX-1 data is served at <https://aegis-governance.com/atx-1/>:

- <https://aegis-governance.com/atx-1/index.json> — Dataset index
- <https://aegis-governance.com/atx-1/techniques.json> — Technique database
- <https://aegis-governance.com/atx-1/stix-bundle.json> — STIX 2.1 bundle
- <https://aegis-governance.com/atx-1/regulatory-crossref.json> — Regulatory mappings
- <https://aegis-governance.com/atx-1/navigator-layer.json> — ATT&CK Navigator layer

## Related

- [AEGIS Governance Specification](../../SPECIFICATION.md)
- [AEGIS Terminology](../../TERMINOLOGY.md)
- [AEGIS References](../../REFERENCES.md)

> **Document**: FinnoybuIPLLC-AEGIS-IEEE-DataDescriptions-ATX1-ThreatMatrix-2026.md\
> **Version**: 0.4 (final, as submitted)\
> **Part of**: AEGIS Position Papers\
> **Target Venue**: IEEE Data Descriptions\
> **Article Type**: Descriptor\
> **Author**: Kenneth Tannenbaum (AEGIS Initiative)\
> **ORCID**: 0009-0007-4215-1789\
> **Preprint DOI**: 10.5281/zenodo.19223924\
> **Dataset DOI (as submitted)**: 10.21227/f87b-1d57 (ATX-1 v1.0)
>
> **STATUS — SUBMITTED 2026-03-26**\
> Submitted to IEEE Data Descriptions on 2026-03-26 as v0.4 (final).
> Canonical submission artifact: [`submission/atx1-descriptor.tex`](submission/atx1-descriptor.tex) (LaTeX) and the accompanying PDF.
> This markdown is the human-readable working copy of that submission and intentionally describes ATX-1 **v1.0** (9 tactics, 20 techniques) — the dataset state at submission time.
>
> **POST-SUBMISSION NOTE**\
> The ATX-1 dataset has since evolved. The current release is **v2.2** (10 tactics, 29 techniques, 29 sub-techniques) with DOI [10.21227/7c9p-6150](https://doi.org/10.21227/7c9p-6150) on IEEE DataPort and [10.5281/zenodo.19483999](https://doi.org/10.5281/zenodo.19483999) on Zenodo. See [`docs/atx/README.md`](../../atx/README.md) for current state. This descriptor remains frozen at v1.0 to match the submitted record; a follow-on descriptor for v2.x is planned separately.
>
> Everything above this line is internal metadata and will not appear in the submission.

---

# **Descriptor:** *AEGIS Threat Matrix for Agentic AI Systems* (ATX-1)

## Abstract

ATX-1 (AEGIS Threat Matrix) is a structured adversarial knowledge base that catalogs failure modes of autonomous AI agents operating without governance constraints. Unlike existing threat frameworks — MITRE ATT&CK for human adversaries and MITRE ATLAS for adversaries targeting AI systems — ATX-1 addresses a distinct threat class: AI agents that act outside their governance boundaries not through external compromise, but through their own structural capability without corresponding authority. ATX-1 is grounded in a fundamental distinction: capability — what an agent can do — is not authority — what an agent may do. The four structural root causes identified in the dataset (missing authority verification, missing consequence modeling, missing behavioral boundaries, and missing state integrity protection) trace all 20 techniques to architectural gaps that governance frameworks can address. The dataset defines 9 tactics (TA001–TA009), 20 techniques distributed non-sequentially across tactics (T1001–T9001), and 20 mitigations, each grounded in empirical observations from the *Agents of Chaos* study, which documented 11 failure modes across live agentic deployments. ATX-1 is published in STIX 2.1 format for compatibility with threat intelligence platforms, with supplementary structured JSON files providing technique metadata, regulatory cross-references to the NIST AI Risk Management Framework, EU AI Act, and OWASP Top 10 for LLM Applications, and a JSON Schema for validation. The dataset satisfies FAIR principles through three permanent repositories — IEEE DataPort, Zenodo, and a live machine-readable API — under the Apache 2.0 license.

**IEEE SOCIETY/COUNCIL** Computer Society (CS)

**DATA TYPE/LOCATION** Threat Taxonomy; Online (IEEE DataPort, Zenodo, aegis-governance.com)

**DATA DOI/PID** 10.21227/f87b-1d57

**INDEX TERMS** Agentic AI, AI governance, autonomous agents, constitutional enforcement, EU AI Act, NIST AI RMF, OWASP LLM, STIX 2.1, threat taxonomy.

---

## Background

Autonomous AI agents — systems that execute real-world actions against operational infrastructure including API calls, file system operations, database queries, and inter-service requests — have grown significantly in production deployments during the twelve months preceding this publication [1]. This growth has outpaced the development of governance infrastructure suited to the action layer, creating a systematic gap between what agents can do and what they are authorized to do.

Existing threat taxonomy frameworks do not address this gap. MITRE ATT&CK [2] catalogs adversarial tactics and techniques used by human threat actors against computer systems. MITRE ATLAS [3] catalogs adversarial tactics used against AI and machine learning systems. Both frameworks assume a clear attacker-target separation: an external adversary acts against a system. ATX-1 addresses the scenario where the AI agent itself is the threat source — not through compromise or malicious intent, but through capability without governance constraint.

The distinction is structural. ATT&CK and ATLAS model adversaries who attack systems. ATX-1 models agents that are themselves the threat source — systems that delete data not because an attacker told them to, but because no architectural mechanism verified that the instruction source held the authority to request deletion. The *Agents of Chaos* study (Shapira et al., 2026) [4] documented this failure pattern systematically, identifying 11 distinct failure modes across live agentic deployments involving 20 researchers over two weeks.

Multiple independent research groups have converged on the same finding. Arora et al. (2025) demonstrated that common multi-agent design patterns — including plan construction strategies, inter-agent context sharing, and fallback behaviors — carry significant vulnerabilities that emerge from architecture and interaction, not solely from adversarial prompts [11]. Ko et al. (2025) identified seven categories of security challenges in cross-domain multi-agent systems, establishing that "a benign agent in isolation may leak secrets or violate policy" when interacting with other agents across trust boundaries [12]. Reid et al. (2025) formalized six failure classes for governed multi-agent systems — including cascading failures, conformity bias, and mixed-motive dynamics — concluding that "a collection of safe agents does not guarantee a safe collection" [13]. These studies independently corroborate the core premise of ATX-1: that agent-level safety does not ensure system-level safety, and that a distinct threat taxonomy is required for the agent-to-infrastructure action layer.

ATX-1 was developed as part of the AEGIS (Architectural Enforcement and Governance of Intelligent Systems) project [5], an open governance architecture that applies reference monitor principles [14] to enforce deterministic constitutional policy at the agent action boundary. The taxonomy directly informs the AEGIS threat model (ATM-1) and maps each technique to specific constitutional articles and governance protocol mechanisms that mitigate it.

No comparable machine-readable dataset exists for agentic AI threat modeling. The OWASP Top 10 for LLM Applications [6] provides a high-level risk categorization but does not define individual techniques, map mitigations to architectural mechanisms, or provide STIX-compatible data for integration with threat intelligence platforms. ATX-1 fills this gap.

---

## Collection Methods and Design

### Empirical Foundation

ATX-1 techniques are derived from the *Agents of Chaos* study [4], which conducted a controlled evaluation of autonomous AI agent robustness. The study deployed AI agents in realistic operational scenarios and systematically documented failure modes. Twenty researchers participated over a two-week period, producing 11 case studies (CS1–CS11) documenting specific failure instances.

### Taxonomy Construction

The ATX-1 taxonomy was constructed through a four-stage process:

1. **Case study analysis.** Each of the 11 *Agents of Chaos* case studies was analyzed to extract the specific failure mechanism, the conditions under which it occurred, and the consequences observed.

2. **Root cause identification.** Four structural root causes were identified that enable agentic failures:
   - **RC1: Missing Authority Verification** — No formal model of principals, delegation chains, or authority levels exists for the agent to verify instruction sources.
   - **RC2: Missing Consequence Modeling** — The agent has no representation of the impact, reversibility, or scope of its actions before executing them.
   - **RC3: Missing Behavioral Boundaries** — No formal boundary defines the scope of the agent's task, allowing autonomous expansion beyond original instructions.
   - **RC4: Missing State Integrity Protection** — Instructions and data commingle in the agent's context, making injection structurally possible.

3. **Tactic and technique classification.** Failure modes were grouped into 9 tactics (categories of ungoverned behavior) and 20 techniques (specific failure mechanisms). Each technique was assigned a severity rating (critical, high, medium, or low), linked to its root cause(s) using the RC1–RC4 labels in the dataset's `root_cause` field, and mapped to the originating case study.

4. **Mitigation mapping.** Each technique was mapped to specific AEGIS constitutional articles and AGP-1 governance protocol mechanisms that architecturally prevent the failure mode. Regulatory cross-references to NIST AI RMF functions, EU AI Act articles, and OWASP LLM Top 10 categories were added.

**TABLE I.** ATX-1 Tactic Summary

| ID | Tactic | Techniques | Severity Range |
|------|------|------|------|
| TA001 | Authority Boundary Violation | T1001, T1002, T1003 | High–Critical |
| TA002 | Destructive Action | T2001, T2002, T2003 | High–Critical |
| TA003 | Scope Violation | T3001 | High |
| TA004 | Information Breach | T4001, T4002 | High–Critical |
| TA005 | Deceptive Output | T5001, T5002 | Medium–High |
| TA006 | Resource Abuse | T6001, T6002 | Medium–High |
| TA007 | Multi-Agent Exploitation | T7001, T7002 | High–Critical |
| TA008 | Persistence Violation | T8001, T8002 | High–Critical |
| TA009 | Monitoring Evasion | T9001 | Medium |

**Fig. 1.** ATX-1 taxonomy construction pipeline. Case studies from the *Agents of Chaos* study [4] are analyzed to identify structural root causes (RC1–RC4), which are classified into 9 tactics and 20 techniques. Each technique is mapped to AEGIS constitutional mitigations and cross-referenced to regulatory frameworks (NIST AI RMF, EU AI Act, OWASP LLM Top 10).

> [Figure placeholder: Four-stage pipeline diagram — Case Studies → Root Causes → Tactics & Techniques → Mitigations & Regulatory Cross-References. Each stage feeds the next. Output arrows show the four machine-readable formats (STIX, JSON, Regulatory Cross-Ref, Schema).]

### Machine-Readable Encoding

The taxonomy was encoded in four machine-readable formats:

**STIX 2.1 Bundle.** The complete taxonomy is represented as a STIX 2.1 Bundle [7] containing: 1 Identity object (AEGIS Initiative), 9 x-mitre-tactic objects, 20 attack-pattern objects (one per technique with kill chain phases and external references), 20 course-of-action objects (mitigations), and 54 relationship objects: 20 tactic-to-technique (uses), 20 mitigation-to-technique (mitigates), and 14 technique-to-OWASP (related-to). The STIX format was chosen for compatibility with existing Security Information and Event Management (SIEM) platforms and threat intelligence tools.

**Technique Database (JSON).** A flat JSON array containing all 20 techniques with structured metadata: identifier, name, parent tactic, description, severity, root cause, case study references, OWASP mapping, and AEGIS mitigation details.

**Regulatory Cross-Reference (JSON).** A structured mapping of each technique to NIST AI RMF functions and categories, EU AI Act articles, OWASP LLM Top 10 categories, and ATM-1 threat scenarios.

**JSON Schema.** A JSON Schema (Draft 2020-12) defining the structure and validation rules for ATX-1 technique definitions, enabling automated validation of technique entries.

---

## Validation and Quality

### Empirical Grounding

Every technique in ATX-1 is traceable to at least one case study from the *Agents of Chaos* study [4]. The mapping between techniques and case studies is explicit in the dataset: each technique record includes an `agents_of_chaos_case` field containing the case study number(s) that demonstrated the behavior. No technique was included without empirical evidence of the failure mode occurring in a live agentic deployment.

### Schema Validation

All technique entries in the technique database conform to the ATX-1 JSON Schema (`atx-technique.schema.json`). The schema enforces required fields (id, name, tactic, description, severity, root_cause, aegis_mitigation), validates identifier patterns (technique IDs must match `^T[0-9]{4}$`, tactic IDs must match `^TA[0-9]{3}$`), constrains severity values to the enumeration (critical, high, medium, low), and rejects additional properties. Validation can be performed using any JSON Schema Draft 2020-12 compliant validator.

### STIX Compliance

The STIX 2.1 Bundle conforms to the OASIS STIX 2.1 specification [7]. All objects include required STIX properties (type, spec_version, id, created, modified). Attack patterns include kill chain phases linking techniques to their parent tactics. Relationship objects use STIX-standard relationship types (uses, mitigates, related-to).

### Cross-Reference Completeness

Every technique has a corresponding entry in the regulatory cross-reference matrix. Each entry includes at minimum one NIST AI RMF function mapping, one EU AI Act article reference, and one OWASP LLM Top 10 category mapping.

### Severity Distribution

The 20 techniques distribute across severity levels as follows: critical (6), high (9), medium (4), low (1). This distribution reflects the empirical finding that most ungoverned agent behaviors have high or critical impact potential.

**Fig. 2.** Severity distribution of ATX-1 techniques. The majority of techniques (75%) are rated high or critical, reflecting the empirical observation that ungoverned agent behaviors predominantly result in significant operational impact.

> [Figure placeholder: Bar chart — x-axis: Critical (6), High (9), Medium (4), Low (1). Color-coded: red, orange, blue, green. Y-axis: Number of techniques.]

**Fig. 3.** STIX 2.1 object composition of the ATX-1 bundle. The bundle contains 104 objects: 9 tactic definitions, 20 attack patterns, 20 mitigations, 54 relationships, and 1 identity.

> [Figure placeholder: Pie or stacked bar chart showing object type distribution — x-mitre-tactic (9), attack-pattern (20), course-of-action (20), relationship (54), identity (1). Total: 104.]

---

## Records and Storage

### File Inventory

| File | Format | Size | Description |
|------|--------|------|-------------|
| `atx-1-bundle.json` | STIX 2.1 JSON | 60.3 KB (61,795 bytes) | Complete taxonomy: tactics, techniques, mitigations, relationships |
| `atx-1-techniques.json` | JSON Array | 18.1 KB (18,578 bytes) | All 20 techniques with full metadata |
| `atx-1-regulatory-crossref.json` | JSON Object | 12.2 KB (12,491 bytes) | NIST AI RMF, EU AI Act, OWASP, ATM-1 mappings |
| `atx-technique.schema.json` | JSON Schema | 2.4 KB (2,459 bytes) | Validation schema for technique definitions |

### Record Structure — Technique Database

Each record in `atx-1-techniques.json` contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Technique identifier (T1001–T9001) |
| `name` | string | Human-readable technique name |
| `tactic` | string | Parent tactic identifier (TA001–TA009) |
| `tactic_name` | string | Parent tactic name |
| `description` | string | Full description of the failure mode |
| `severity` | enum | critical, high, medium, or low |
| `root_cause` | string | Structural root cause (RC1–RC4) |
| `agents_of_chaos_case` | array[int] | Case study numbers from [4] |
| `owasp_mapping` | array[string] | OWASP LLM Top 10 categories |
| `aegis_mitigation` | object | Constitutional article, AGP mechanism, and description |

### Storage Locations

The dataset is permanently stored in three locations:

1. **IEEE DataPort** — DOI: 10.21227/f87b-1d57 — Authoritative repository for this submission.
2. **Zenodo** — DOI: 10.5281/zenodo.19225676 — Open access, indexed by OpenAIRE and Google Dataset Search.
3. **AEGIS Governance Data Portal** — https://aegis-governance.com/atx-1/ — Live machine-readable endpoints with dataset index, individual file access, and programmatic consumption support.

All storage locations serve identical file content under the Apache 2.0 license.

---

## Insights and Notes

### Use Cases

**Threat intelligence integration.** The STIX 2.1 Bundle can be imported directly into SIEM platforms and threat intelligence tools that support STIX, enabling organizations to incorporate agentic AI threat patterns into existing security monitoring workflows.

**Governance policy development.** The technique-to-mitigation mapping provides a direct link between observed failure modes and architectural countermeasures, supporting evidence-based governance policy authoring for AI agent deployments.

**Regulatory compliance mapping.** The regulatory cross-reference matrix enables organizations to trace specific agentic AI risks to regulatory requirements across NIST AI RMF, EU AI Act, and OWASP frameworks, supporting compliance documentation and gap analysis.

**Research benchmarking.** The empirically grounded technique catalog provides a structured basis for evaluating the effectiveness of AI governance frameworks against documented failure modes.

### Limitations

ATX-1 v1.0 derives its technique definitions primarily from the *Agents of Chaos* study [4], with the core findings corroborated by independent research on multi-agent vulnerabilities [11], cross-domain security challenges [12], and governed system failure modes [13]. While the technique catalog may not be exhaustive, the convergence of multiple research groups on the same failure patterns provides confidence in the taxonomy's coverage of the dominant threat classes. Future versions will incorporate additional empirical sources as the field of agentic AI governance matures.

The severity ratings reflect the author's assessment based on the documented case studies and are not derived from a quantitative risk model. Organizations should calibrate severity ratings to their specific deployment context.

### Extensibility

The JSON Schema and STIX format support extension. New techniques can be added by conforming to the schema and assigning identifiers in the existing numbering scheme. The STIX Bundle supports standard extension mechanisms for custom properties.

---

## Source Code and Scripts

The ATX-1 dataset and all associated schemas are maintained in the AEGIS Governance repository [14]. The source files are located in the `docs/atx/` directory under the Apache 2.0 license.

The STIX 2.1 Bundle can be consumed using the `stix2` Python library [15] (v3.0+):

```python
from stix2 import parse

with open("atx-1-bundle.json") as f:
    bundle = parse(f.read(), allow_custom=True)

for obj in bundle.objects:
    if obj.type == "attack-pattern":
        print(f"{obj.external_references[0].external_id}: {obj.name}")
```

Technique validation against the JSON Schema can be performed using `ajv-cli`:

```bash
npx ajv validate -s atx-technique.schema.json -d 'atx-1-techniques.json#/0'
```

No custom software was developed specifically for the dataset. The taxonomy was authored manually based on the empirical analysis described in Collection Methods and Design.

---

## Acknowledgements and Interests

### Author Contributions

Kenneth Tannenbaum: conceptualization, taxonomy design, data collection and analysis, machine-readable encoding, manuscript preparation.

### Funding

This work was done independently of any grants or awards, produced under Finnoybu IP LLC.

### Conflicts of Interest

The author is the founder of the AEGIS Initiative, which develops the governance architecture that ATX-1 informs. The dataset is published under Apache 2.0 and is designed for use with any governance framework, not exclusively AEGIS.

### AI Tool Usage

This dataset and manuscript were prepared with the assistance of Claude (Anthropic) as an analysis and writing tool. The taxonomy structure, technique definitions, severity assessments, and all technical content are the author's original work.

---

## References

[1] R. Chan et al., "The 2025 AI Agent Index," arXiv:2602.17753, 2025.

[2] MITRE Corporation, "ATT&CK: Adversarial Tactics, Techniques, and Common Knowledge," 2024. [Online]. Available: https://attack.mitre.org/

[3] MITRE Corporation, "ATLAS: Adversarial Threat Landscape for AI Systems," 2024. [Online]. Available: https://atlas.mitre.org/

[4] T. Shapira et al., "Agents of Chaos: Evaluating the Robustness of Autonomous AI Agents," arXiv:2602.20021, 2026.

[5] K. Tannenbaum, "AEGIS: A Constitutional Governance Architecture for Autonomous AI Agents," AEGIS Initiative, 2026, doi: 10.5281/zenodo.19223924.

[6] OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," 2025. [Online]. Available: https://owasp.org/www-project-top-10-for-large-language-model-applications/

[7] OASIS, "STIX Version 2.1," OASIS Standard, 2021. [Online]. Available: https://docs.oasis-open.org/cti/stix/v2.1/stix-v2.1.html

[8] National Institute of Standards and Technology, "Artificial Intelligence Risk Management Framework (AI RMF 1.0)," NIST AI 100-1, Jan. 2023.

[9] European Parliament and Council of the EU, "Regulation (EU) 2024/1689 (EU AI Act)," Official Journal of the European Union, Jul. 2024.

[10] J. P. Anderson, "Computer Security Technology Planning Study," ESD-TR-73-51, Electronic Systems Division, USAF, 1972.

[11] N. Arora et al., "Exposing Weak Links in Multi-Agent Systems under Adversarial Prompting," arXiv:2511.10949, 2025.

[12] R. Ko et al., "Seven Security Challenges in Cross-domain Multi-agent LLM Systems," arXiv:2505.23847, 2025.

[13] A. Reid, S. O'Callaghan, L. Carroll, and T. Caetano, "Risk Analysis Techniques for Governed LLM-based Multi-Agent Systems," arXiv:2508.05687, 2025.

[14] AEGIS Initiative, "AEGIS Governance Repository," 2026. [Online]. Available: https://github.com/aegis-initiative/aegis-governance

[15] OASIS, "cti-python-stix2: Python APIs for STIX 2," 2024. [Online]. Available: https://github.com/oasis-open/cti-python-stix2

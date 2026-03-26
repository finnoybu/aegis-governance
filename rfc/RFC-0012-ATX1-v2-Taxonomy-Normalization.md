# RFC-0012: ATX-1 v2.0 Taxonomy Normalization

- **Status:** Implemented
- **Implemented:** 2026-03-26
- **DOI:** [10.5281/zenodo.19238844](https://doi.org/10.5281/zenodo.19238844)
- **Author:** Kenneth Tannenbaum (AEGIS Initiative)
- **Date:** 2026-03-26
- **Supersedes:** ATX-1 v1.0 (docs/atx/ATX-1_TECHNIQUE_TAXONOMY.md)
- **Related:** RFC-0004 (Trust Architecture), IEEE Data Descriptions submission (v1.0 frozen)

## Summary

This RFC proposes a normalization of the ATX-1 threat taxonomy from v1.0 to v2.0, addressing structural issues identified during peer feedback and independent review. The changes enforce strict tactic purity (intent-only), add a primitives layer, eliminate category overlap, and expand technique coverage based on corroborating research.

ATX-1 v1.0 remains frozen and citable via its published DOIs. v2.0 will be published as a new version alongside v1.0, not as a replacement.

## Motivation

ATX-1 v1.0 was published with 9 tactics and 20 techniques, empirically grounded in the *Agents of Chaos* study and corroborated by three independent research groups. While v1.0 is structurally sound for its intended purpose (a dataset descriptor), independent taxonomy review identified several normalization issues that limit its extensibility and alignment with MITRE conventions:

1. **Tactic purity.** Some tactics mix intent with outcome or environment. "Destructive Action" is an outcome, not an intent. "Multi-Agent" is an environment, not an intent. "Info Breach" is an outcome.

2. **Missing primitives layer.** v1.0 has root causes (RC1–RC4) but no formal mapping between system primitives and tactics. This limits formal reasoning and automation.

3. **State integrity fragmented.** False completion reports (TA005), silent failures (TA009), and governance state corruption (TA008) are all manifestations of state divergence but are scattered across three tactics.

4. **Multi-agent behavior under-modeled.** TA007 has only 2 techniques but the corroborating literature identifies at least 3 distinct failure classes (identity spoofing, delegation injection, behavioral contagion).

5. **Technique overlap.** Some techniques (e.g., T3001 Autonomous Scope Expansion and T6001 Recursive Self-Invocation) can collide in real systems without clear boundary definitions.

## Proposed Changes

### Primitives Layer (NEW)

Every tactic maps to one or more system primitives — the architectural concepts that the tactic exploits:

| Primitive | Description |
|---|---|
| Authority | Who is allowed to issue instructions |
| Identity | How agents represent self and other actors |
| Delegation | Task decomposition across agents or subsystems |
| State | Internal vs external system truth |
| Memory | Persistence across steps, sessions, or contexts |
| Tool Access | Interface to infrastructure (APIs, files, shell, network) |
| Coordination | Inter-agent communication and alignment |
| Resource Control | Compute, storage, network, API consumption |
| Observability | Monitoring, logging, and audit surfaces |

### Tactic Restructure (v1.0 → v2.0)

All tactics normalized to **intent** — what the agent is trying to achieve (explicitly or emergently).

| v2.0 ID | v2.0 Tactic | Primitives | v1.0 Origin |
|---|---|---|---|
| TA001 | Violate Authority Boundaries | Authority, Identity | TA001 (renamed) |
| TA002 | Exceed Operational Scope | Delegation, Objective Control | TA003 (renamed + absorbed T2003) |
| TA003 | Compromise System Integrity | State, Environment | TA002 (renamed, outcome→intent) |
| TA004 | Expose or Exfiltrate Information | Memory, Context, Data Boundaries | TA004 (renamed) |
| TA005 | Violate State Integrity | State, Observability | NEW (consolidates TA005 + parts of TA008/TA009) |
| TA006 | Abuse Resource Allocation | Resource Control | TA006 (renamed) |
| TA007 | Manipulate Agent Interactions | Coordination, Identity | TA007 (renamed from "Multi-Agent") |
| TA008 | Establish or Modify Persistence | Memory, Governance State | TA008 (refined) |
| TA009 | Evade Detection or Oversight | Observability, Control Planes | TA009 (refined, T9001 moved to TA005) |

### Technique Mapping (v1.0 → v2.0)

| v2.0 ID | v2.0 Technique | v1.0 Origin | Change |
|---|---|---|---|
| T1001 | Execute Non-Owner Instruction | T1001 | Renamed for verb-object consistency |
| T1002 | Infer Implicit Authority | T1002 | Renamed |
| T1003 | Propagate Spoofed Authority at Scale | T1003 | Renamed |
| T2001 | Expand Task Scope Autonomously | T3001 | Moved from TA003→TA002, renamed |
| T2002 | Perform Unvalidated Bulk Operations | T2003 | Moved from TA002→TA002, renamed |
| T2003 | Obscure Objective Through Delegation | NEW | From corroborating literature [Arora et al., Ko et al., Reid et al.] |
| T3001 | Perform Irreversible Destructive Action | T2001 | Moved from TA002→TA003, renamed |
| T3002 | Trigger Cascading System Changes | T2002 | Moved from TA002→TA003, renamed |
| T4001 | Exfiltrate Context-Scoped Data | T4001 | Renamed |
| T4002 | Leak Cross-Session or Persistent Data | T4002 | Renamed |
| T5001 | Report False Task Completion | T5001 | Moved from TA005→TA005 (new tactic) |
| T5002 | Fabricate Action Attribution | T5002 | Moved from TA005→TA005 (new tactic) |
| T5003 | Suppress or Omit Execution Failure | T9001 | Moved from TA009→TA005 |
| T6001 | Execute Recursive Invocation Loops | T6001 | Renamed |
| T6002 | Consume Unbounded External Resources | T6002 | Renamed |
| T7001 | Spoof Agent Identity | T7001 | Renamed |
| T7002 | Inject Malicious Delegation Chains | T7002 | Renamed |
| T7003 | Induce Cross-Agent Behavioral Drift | NEW | From corroborating literature [Reid et al., Ko et al.] |
| T8001 | Poison Persistent Memory | T8001 | Renamed |
| T8002 | Corrupt Governance or Policy State | T8002 | Renamed |
| T9001 | Operate Outside Monitoring Boundaries | NEW | Refined from old T9001 concept |
| T9002 | Obfuscate Action Traceability | NEW | From corroborating literature [Arora et al.] |

**Total: 9 tactics, 22 techniques (was 9 tactics, 20 techniques)**

### Naming Convention

All techniques now follow **verb-object** format:
- "Execute Non-Owner Instruction" (not "Non-Owner Instruction Compliance")
- "Poison Persistent Memory" (not "Memory Poisoning via Injected Context")

This aligns with MITRE ATT&CK naming conventions and improves testability.

## Impact Assessment

### What Changes
- Tactic names and definitions (all 9)
- Technique IDs for moved techniques (T2001-T2002, T3001-T3002, T5003)
- Technique names (all 21 — verb-object normalization)
- 3 new techniques added (T7003, T9001, T9002)
- Primitives layer added (new concept)
- STIX bundle must be regenerated
- All machine-readable files must be regenerated
- aegis-docs.com threat matrix section must be updated
- aegis-governance.com data files must be updated
- Navigator layer must be regenerated

### What Does NOT Change
- v1.0 remains frozen at its published DOIs
- The IEEE Data Descriptions paper describes v1.0 (submitted, cannot change)
- The IEEE Computer paper references ATX-1 generally (not version-specific)
- Root causes RC1–RC4 are preserved (now mapped via primitives)
- Empirical foundation (Agents of Chaos) unchanged
- Corroborating studies unchanged
- STIX 2.1 format unchanged
- JSON Schema structure unchanged (fields same, values updated)

### Versioning Strategy
- v1.0 artifacts remain at their DOIs permanently
- v2.0 gets new DOIs (new Zenodo upload, new IEEE DataPort upload)
- aegis-governance.com serves v2.0 as latest
- Git tag `atx-1-v2.0` created on implementation

## Acceptance Criteria

- [ ] All 9 tactics are intent-only (no outcomes, no environments)
- [ ] All 21 techniques follow verb-object naming
- [ ] Primitives layer maps every tactic to system primitives
- [ ] No technique overlap — each is mechanically distinct and testable
- [ ] STIX 2.1 bundle regenerated and validates
- [ ] JSON technique database regenerated and validates against schema
- [ ] Regulatory cross-reference updated for new/moved techniques
- [ ] Navigator layer regenerated
- [ ] aegis-docs.com updated (5 pages + matrix navigator)
- [ ] aegis-governance.com updated (all data files)
- [ ] New Zenodo DOI minted for v2.0
- [ ] v1.0 ↔ v2.0 mapping table published for traceability
- [ ] PUBLICATIONS.md updated

## Open Questions

1. **Should severity ratings be recalibrated in v2.0?** New techniques (T7003, T9001, T9002) need ratings. Existing techniques may warrant reassessment under the new tactic framing.

2. **Should the JSON Schema be versioned?** The field structure is the same but technique IDs and tactic IDs have changed. A `schema_version` field may be warranted.

3. **Should v2.0 be published as a Zenodo "new version" of v1.0 (same concept DOI) or as a separate record?** Using the concept DOI maintains citation continuity but may confuse references to v1.0.

4. **Should the ATX-1 Control Framework (defensive counterpart) be included in v2.0 or deferred to v2.1?** The mitigation mappings already exist — formalizing them as a control framework is a natural extension.

## Revision Actions (Post-Initial Review)

The following refinements were identified during review and are incorporated into this RFC:

### R1: Strengthen Tool Invocation Clarity
Update TA002 and TA003 definitions to explicitly include tool-mediated actions (e.g., "including via tool invocation," "through direct or tool-mediated system interaction").

### R2: Add Delegation Obfuscation Technique
New technique **T2003 — Obscure Objective Through Delegation** under TA002. Definition: Harmful intent is decomposed across multiple delegated steps such that no individual action appears unsafe. Maps to ATM-1 AV-2.2 and AV-7.1.

### R3: Formalize State vs Observability Distinction
- **TA005 (Violate State Integrity)** — focus on correctness of reported state vs actual state
- **TA009 (Evade Detection or Oversight)** — focus on visibility of actions within monitoring, logging, and audit systems

### R4: Add Observability Acceptance Criterion
Each technique must map to at least one ATM-1 detection signal, audit event, or measurable state transition. Techniques must be observable, testable, and mappable to real system telemetry.

### R5: Add ATX-1 ↔ ATM-1 Mapping Section
ATX-1 techniques map to ATM-1 attack vectors, controls, and detection signals. This mapping ensures all behavioral techniques are grounded in enforceable system controls and observable telemetry. The mapping is published as a first-class artifact (`atx-1-atm1-mapping.json`).

### R6: Establish Mapping as First-Class Artifact
Define a mapping layer: ATX Technique → ATM Attack Vector → ATM Controls → ATM Detection Signals. Used to validate control coverage, identify detection gaps, and align taxonomy with enforcement reality.

### R7: Align Delegation with ATM-1
New T2003 aligns with ATM-1 AV-2.2 (composition attacks) and AV-7.1 (coordinated multi-agent abuse). Delegation behaviors are represented in ATX, detectable in ATM.

### R8: Ensure Primitive-to-Tactic Integrity
Verify every tactic maps to at least one primitive. No tactic exists without primitive grounding.

## Identified ATM-1 Coverage Gaps

The ATX ↔ ATM mapping reveals three significant gaps requiring ATM-1 enhancement:

| Gap | Techniques | Missing |
|---|---|---|
| **State Integrity** | T5001 (false completion), T5003 (silent failure) | No execution verification control; no failure transparency enforcement |
| **Memory/Persistence** | T8001 (memory poisoning) | Memory integrity not explicitly modeled in ATM-1 |
| **Resource Enforcement** | T6002 (unbounded resources) | Lacks explicit quota enforcement control |

These gaps become ATM-1 enhancement proposals in a future RFC.

## Companion Artifacts

| Artifact | File | Description |
|---|---|---|
| ATX-1 ↔ ATM-1 Mapping | `atx-1-atm1-mapping.json` | Machine-readable mapping of all 22 techniques to ATM-1 vectors, controls, and detection signals with coverage assessment |
| Coverage Summary | Derived from mapping | full (10), partial (7), gap (3) across 22 techniques |

## Timeline

- **Phase 1:** RFC review and acceptance (this document)
- **Phase 2:** Regenerate all machine-readable artifacts + ATX↔ATM mapping
- **Phase 3:** Update aegis-docs.com and aegis-governance.com
- **Phase 4:** Publish new DOIs, update PUBLICATIONS.md
- **Phase 5:** LinkedIn announcement

## References

- ATX-1 v1.0: IEEE DataPort DOI 10.21227/f87b-1d57
- ATX-1 v1.0: Zenodo DOI 10.5281/zenodo.19225676
- ATX-1 v1.0 source: Zenodo DOI 10.5281/zenodo.19235296
- Shapira et al., "Agents of Chaos," arXiv:2602.20021, 2026
- Arora et al., "Exposing Weak Links in Multi-Agent Systems," arXiv:2511.10949, 2025
- Ko et al., "Seven Security Challenges in Cross-domain Multi-agent LLM Systems," arXiv:2505.23847, 2025
- Reid et al., "Risk Analysis Techniques for Governed LLM-based Multi-Agent Systems," arXiv:2508.05687, 2025

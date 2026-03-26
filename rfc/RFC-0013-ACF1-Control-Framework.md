# RFC-0013: ACF-1 — AEGIS Control Framework

- **Status:** Proposed
- **Author:** Kenneth Tannenbaum (AEGIS Initiative)
- **Date:** 2026-03-26
- **Depends on:** RFC-0012 (ATX-1 v2.0), ATM-1 (Adaptive Threat Model)
- **Related:** RFC-0001 (Architecture), RFC-0004 (Event Model)

## Summary

ACF-1 (AEGIS Control Framework) defines the operational defensive layer for autonomous agent systems. It maps ATX-1 techniques to detection signals, validation rules, and response actions — completing the closed loop from behavioral threat identification through enforcement.

Where ATX-1 answers "what can go wrong" and ATM-1 answers "how to prevent it," ACF-1 answers "how do I know it's happening and what do I do about it."

## Motivation

ATX-1 v2.0 provides a comprehensive threat taxonomy (9 tactics, 25 techniques). ATM-1 provides system-level controls. But neither defines:

- Observable signals that indicate a technique is being executed
- Testable assertions that verify system behavior
- Structured responses when detection or validation fails

Without these, the framework is descriptive but not operational. ACF-1 bridges this gap.

## Design Principles

### Separation of Concerns

| Layer | Responsibility |
|---|---|
| ATX-1 | Defines behavioral threats (what can go wrong) |
| ATM-1 | Defines system controls (how to prevent it) |
| ACF-1 | Defines detection, validation, and response (how to know and what to do) |

### Non-Invasive Integration

ACF-1:

- Does NOT modify ATX-1 objects
- References ATX techniques by ID (e.g., `attack-pattern--atx-t5001`)
- Is independently versioned and citable
- Plugs into existing STIX bundles via relationship objects

### Observable-First Model

Every ATX-1 technique MUST map to:

- At least one detection signal
- At least one validation rule

## Core Data Model

ACF-1 introduces three primary object types as STIX custom extensions:

### Detection (`x-acf-detection`)

Represents a signal or metric indicating a technique may be occurring.

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Human-readable detection name |
| `description` | string | Yes | What the detection observes |
| `x_acf_signal_type` | enum | Yes | `metric`, `event`, `state`, or `correlation` |
| `x_acf_log_source` | string | Yes | System component generating the signal |
| `x_acf_detection_logic` | string | Yes | Pseudocode or expression defining the detection condition |
| `x_acf_related_atx` | array | Yes | ATX-1 technique IDs this detection covers |

**Signal Types:**

| Type | Description |
|---|---|
| `metric` | Numerical signal (rate, count, threshold) |
| `event` | Discrete occurrence (single action or state change) |
| `state` | System condition (persistent state divergence) |
| `correlation` | Multi-signal inference (cross-source or cross-agent) |

### Validation (`x-acf-validation`)

Defines a testable assertion that verifies system behavior.

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Human-readable validation name |
| `description` | string | Yes | What the validation checks |
| `x_acf_validation_type` | enum | Yes | `consistency_check`, `policy_enforcement`, `anomaly_detection`, or `integrity_check` |
| `x_acf_required_signals` | array | Yes | Signals needed to perform validation |
| `x_acf_expected_condition` | string | Yes | Expression defining the expected valid state |
| `x_acf_related_atx` | array | Yes | ATX-1 technique IDs this validation covers |

**Validation Types:**

| Type | Description |
|---|---|
| `consistency_check` | Cross-source validation (e.g., execution log vs report) |
| `policy_enforcement` | Rule-based validation against governance policy |
| `anomaly_detection` | Deviation from established baseline |
| `integrity_check` | Signature or tamper validation |

### Response (`x-acf-response`)

Defines a system reaction when detection or validation fails.

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Human-readable response name |
| `description` | string | Yes | What the response does |
| `x_acf_response_type` | enum | Yes | `containment`, `prevention`, `intervention`, `escalation`, or `alert` |
| `x_acf_trigger` | string | Yes | Condition that activates the response |
| `x_acf_related_atx` | array | Yes | ATX-1 technique IDs this response addresses |

## Relationships

ACF-1 uses explicit STIX relationship objects:

| Relationship Type | Source | Target | Meaning |
|---|---|---|---|
| `detects` | x-acf-detection | attack-pattern | This detection identifies this technique |
| `validates` | x-acf-validation | attack-pattern | This validation verifies against this technique |
| `responds-to` | x-acf-response | attack-pattern | This response activates for this technique |

## Coverage Requirements

### Detection Requirement

Every ATX-1 technique MUST have at least one `x-acf-detection` relationship.

### Validation Requirement

Every ATX-1 technique MUST have at least one `x-acf-validation` relationship.

### Critical Technique Rule

For techniques rated `critical` severity, MUST have:

- At least one detection
- At least one validation
- At least one response

Critical techniques in ATX-1 v2.0: T1003, T3001, T3002, T4001, T7001, T8002.

## Multi-Agent Semantics

ACF-1 captures coordination dynamics as metadata on detection objects where applicable:

| Property | Values | Description |
|---|---|---|
| `coordination_type` | `explicit`, `implicit`, `emergent` | How agents coordinate |
| `propagation_mode` | `delegation`, `context`, `memory` | How behavior spreads between agents |
| `detection_scope` | `single-agent`, `multi-agent`, `system-wide` | Scope of detection required |

Applied to TA007 techniques (T7001–T7004) and any cross-agent detection.

## Integration with ATM-1

ACF-1 detection signals link to ATM-1 controls and vectors:

| ACF-1 Property | ATM-1 Mapping |
|---|---|
| `x_acf_atm_mapping.detection_signal` | ATM detection metric |
| `x_acf_atm_mapping.control` | ATM preventive/detective control (PC/DC) |
| `x_acf_atm_mapping.vector` | ATM attack vector (AV) |

This ensures every ACF-1 detection is grounded in the ATM-1 system model.

## Reference Implementation (v0.1)

ACF-1 v0.1 demonstrates the full Detection → Validation → Response loop for three anchor techniques representing the three identified ATM-1 gaps:

| Technique | Gap Type | Detection Style |
|---|---|---|
| T5001 — Report False Task Completion | State integrity | State mismatch correlation |
| T2004 — Exploit Tool-Chain Composition | Composition exploit | Sequence analysis |
| T7004 — Induce Unsafe Consensus | Multi-agent emergent | Cross-agent correlation |

The v0.1 STIX bundle is published as a companion artifact at `docs/atx/v2/acf/acf-1-bundle.json`.

## Versioning

| Version | Scope |
|---|---|
| ACF-1 v0.1 | Initial detection model (3 anchor techniques) |
| ACF-1 v1.0 | Full coverage of all 25 ATX-1 v2.0 techniques |
| ACF-1 v1.1+ | Incremental signal expansion, new detection patterns |

## Acceptance Criteria

- [ ] All 25 ATX-1 v2.0 techniques have at least one detection
- [ ] All 25 techniques have at least one validation
- [ ] All 6 critical techniques have detection + validation + response
- [ ] Multi-agent semantics applied to TA007 techniques
- [ ] ATM-1 integration mappings for all detections
- [ ] STIX bundle validates against stix2 library
- [ ] Coverage check script passes: every technique has detection and validation
- [ ] Published as independently citable artifact (separate DOI)
- [ ] Documentation on aegis-docs.com

## Open Questions

1. **Should ACF-1 define a coverage scoring model?** (e.g., percentage of techniques with full detection + validation + response)

2. **Should response objects define severity-graduated actions?** (e.g., alert for medium, escalate for high, halt for critical)

3. **Should ACF-1 include a "detection gap" object type** for explicitly documenting known gaps awaiting future detection development?

4. **Integration with RFC-0006 (Claude Code Plugin):** Should the plugin implement ACF-1 detections as part of its PreToolUse hook evaluation?

## References

- RFC-0012: ATX-1 v2.0 Taxonomy Normalization
- ATM-1: AEGIS Adaptive Threat Model (aegis-governance/aegis-core/threat-model/)
- RFC-0001: AEGIS Architecture
- RFC-0004: Governance Event Model

# AEGIS AT-Protocol Governance Schemas
**Version:** 0.1 (Draft)  
**Date:** 2026-03-04  

This document defines **canonical event schemas** for the AEGIS Governance Federation Network (GFN).  
Schemas are expressed in a **JSON Schema–like** form, with normative requirements stated using **MUST / SHOULD / MAY**.

---

## 1. Conventions

### 1.1 Envelope vs Payload

Every published record MUST use the **AEGIS Event Envelope**. The `payload` MUST conform to the schema identified by `event_type`.

### 1.2 Data Types

- `string`: UTF-8 string
- `uri`: URL/URI string
- `datetime`: RFC 3339 timestamp (e.g., `2026-03-04T22:30:00-05:00`)
- `list[T]`: ordered array of `T`
- `map[string, any]`: JSON object

---

## 2. AEGIS Event Envelope (Required)

### 2.1 Schema: `aegis.event.envelope.v1`

**Fields (MUST):**
- `event_id` (string): globally unique identifier (UUID recommended)
- `timestamp` (datetime): publish timestamp
- `publisher_did` (string): `did:aegis:*`
- `event_type` (string): one of the registered event types
- `payload` (object): event-specific body
- `signature` (string): signature of the canonicalized envelope (excluding `signature`)

**Fields (SHOULD):**
- `schema_version` (string): e.g., `v1`
- `correlation_id` (string): groups related events
- `references` (list[uri]): external references (docs, advisories)
- `tags` (list[string]): classification tags (e.g., `prompt`, `exfil`, `policy`)
- `visibility` (string): `public` | `restricted` | `private`
- `ttl_seconds` (integer): suggested retention TTL for caches

**Canonicalization (MUST):**
- JSON canonicalization MUST be deterministic (e.g., sorted keys, normalized whitespace) for signing and verification.

---

## 3. Event Types Registry

Registered `event_type` values (v0.1):
- `governance.circumvention_report.v1`
- `governance.risk_signal.v1`
- `governance.policy_update.v1`
- `governance.attestation.v1`
- `governance.incident_notice.v1`

---

## 4. Circumvention Report

### 4.1 Schema: `governance.circumvention_report.v1`

**Intent:** Describe a technique observed or validated that attempts to bypass governance controls.

**Fields (MUST):**
- `technique_id` (string): stable identifier (e.g., `PROMPT-CHAIN-042`)
- `category` (string): e.g., `prompt-engineering`, `tool-misuse`, `social-engineering`, `data-exfiltration`
- `severity` (string enum): `low` | `medium` | `high` | `critical`
- `description` (string): concise narrative
- `observed_at` (datetime): time first observed by publisher

**Fields (SHOULD):**
- `attack_pattern` (string): abstract pattern descriptor (NOT a copy/paste exploit)
- `indicators` (list[string]): non-sensitive indicators (hashes of patterns, not raw prompts)
- `affected_models` (list[string]): model families or identifiers
- `affected_controls` (list[string]): control IDs (e.g., `RISK-SCORE`, `TOOL-GATE`, `DATA-BOUNDARY`)
- `mitigation_recommendations` (list[string]): actionable defensive steps
- `confidence` (number 0..1): publisher confidence
- `exploit_reproducibility` (string enum): `theoretical` | `observed` | `validated`

**Fields (MAY):**
- `attachments` (list[uri]): pointers to restricted artifacts (only if access-controlled)

**Safety Note:** Publishers SHOULD avoid distributing raw exploit prompts or step-by-step bypass instructions in `public` visibility.

---

## 5. Risk Signal

### 5.1 Schema: `governance.risk_signal.v1`

**Intent:** Provide aggregated telemetry describing emerging governance risk.

**Fields (MUST):**
- `risk_category` (string): e.g., `model_manipulation`, `exfiltration_attempts`, `policy_drift`
- `severity` (string enum): `advisory` | `warning` | `critical`
- `trend` (string enum): `rising` | `stable` | `declining`
- `scope` (string): e.g., `global`, `regional`, `tenant`, `org`
- `summary` (string): short description

**Fields (SHOULD):**
- `metrics` (map[string, any]): aggregated counters or rates (no sensitive data)
- `related_techniques` (list[string]): technique IDs
- `related_models` (list[string])
- `recommended_actions` (list[string])
- `confidence` (number 0..1)

---

## 6. Policy Update

### 6.1 Schema: `governance.policy_update.v1`

**Intent:** Publish a governance policy document, profile, or delta.

**Fields (MUST):**
- `policy_id` (string): stable policy identifier (e.g., `nist.ai.rmf.profile`)
- `policy_version` (string): semantic version recommended
- `policy_authority_did` (string): DID of authority
- `effective_date` (datetime)
- `change_summary` (string)
- `policy_uri` (uri): canonical location of the full policy document

**Fields (SHOULD):**
- `supersedes` (string): previous version
- `compatibility` (list[string]): profiles that are compatible
- `requirements_hash` (string): hash of normative requirements section
- `classification` (string): e.g., `baseline`, `regulated`, `enterprise`

---

## 7. Governance Attestation

### 7.1 Schema: `governance.attestation.v1`

**Intent:** Declare governance posture and enable inter-node trust decisions.

**Fields (MUST):**
- `aegis_version` (string)
- `risk_model_id` (string)
- `compliance_profiles` (list[string])
- `attested_at` (datetime)
- `attesting_did` (string): DID of the system being attested

**Fields (SHOULD):**
- `audit_evidence_uri` (uri): restricted evidence bundle
- `auditor_did` (string): third-party auditor or internal assurance identity
- `controls_implemented` (list[string]): control IDs
- `assurance_level` (string enum): `self` | `internal` | `external`

---

## 8. Incident Notice

### 8.1 Schema: `governance.incident_notice.v1`

**Intent:** Disclose a governance failure or safety incident to improve ecosystem resilience.

**Fields (MUST):**
- `incident_id` (string)
- `incident_class` (string): e.g., `bypass_success`, `exfiltration`, `harmful_output`, `policy_failure`
- `severity` (string enum): `low` | `medium` | `high` | `critical`
- `occurred_at` (datetime)
- `summary` (string)

**Fields (SHOULD):**
- `impact` (string)
- `root_cause_hypothesis` (string)
- `mitigations_applied` (list[string])
- `follow_up_actions` (list[string])
- `links` (list[uri])

---

## 9. Schema Governance

### 9.1 Compatibility Rules (MUST)
- Backwards-compatible changes: add optional fields only.
- Breaking changes: increment major version suffix (e.g., `...v2`).

### 9.2 Registry (SHOULD)
Maintain a central registry file in-repo:
- `aegis-spec/governance-network/SCHEMA_REGISTRY.yaml`

---

## 10. Reference Example (Envelope + Payload)

```json
{
  "event_id": "8f0b6a5b-7e03-4f0d-b2c3-9fd7f8f7d2d1",
  "timestamp": "2026-03-04T22:45:00-05:00",
  "publisher_did": "did:aegis:enterprise-ai-001",
  "event_type": "governance.risk_signal.v1",
  "payload": {
    "risk_category": "model_manipulation",
    "severity": "warning",
    "trend": "rising",
    "scope": "global",
    "summary": "Increased frequency of manipulation attempts against tool authorization boundaries.",
    "confidence": 0.76
  },
  "signature": "BASE64_SIGNATURE"
}
```

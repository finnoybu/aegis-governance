# AEGIS™ AGP-1 Trust Model & Actor Reputation

**Document**: AGP-1/Trust (AEGIS_AGP1_TRUST_MODEL.md)  
**Version**: 1.0 (Normative)  
**Part of**: AEGIS Governance Protocol  
**References**: AGP-1/Risk, GFN-1/Nodes  
**Last Updated**: March 6, 2026

---

## Overview

The AEGIS™ Trust Model establishes a **capability-based reputation system** for actors (users, services, LLMs) in a federated governance environment. Each actor has a trust score [0.0 - 1.0] that influences:

1. **Decision thresholds** (AEGIS_AGP1_RISK_SCORING.md)
2. **Escalation requirements** (when human review is needed)
3. **Monitoring constraints** (how closely the execution is observed)
4. **Federation participation** (whether signals from this actor are trusted)

Trust is **not global**. Each node maintains its own assessment of actors, informed by:

- Local historical performance
- Federation attestations
- Cryptographic proof of identity

---

## Trust Score Definition

```
trust_score = f(
    identity_verification,
    historical_reliability,
    federation_consensus,
    cryptographic_proof
) ∈ [0.0, 1.0]
```

### Component 1: Identity Verification (Weight: 0.30)

How confident are we about this actor's claimed identity?

```
verification_score ∈ {
    0.0: no_identity_claim,
    0.3: self_signed_identity,
    0.6: organization_verified_identity,
    0.8: federally_attested_identity,
    1.0: hardware_backed_keypair_identity
}

For LLMs:
    0.0: unknown model,
    0.3: model verified by common package manager,
    0.5: model signed by known publisher,
    0.8: model attested by deployment platform,
    1.0: model running in hardware-isolated enclave
```

**Examples**:

- Actor claims "user:alice" with self-signed cert → 0.3
- Actor claims "user:alice@domain.com" with domain-verified TLS → 0.6
- Actor claims "llm:gpt4" signed by OpenAI with federation proof → 0.8

### Component 2: Historical Reliability (Weight: 0.40)

What is the actor's success rate on past requests?

```
reliability = 1.0 - (failed_actions / total_actions)

Where:
- failed_actions = count(EXECUTION_STATUS == "FAILED" in 30-day window)
- total_actions = count(all execution reports in 30-day window)

trust_historical = reliability
trust_historical = max(reliability × e^(-penalty_adjustments), 0.0)

Penalty adjustments:
- Critical failures (e.g., data loss): -0.3
- Policy violations: -0.2
- Suspicious patterns (rapid retries, timing attacks): -0.15
```

**Examples**:

- 95 successes, 5 failures / 100 → reliability = 0.95 → trust = 0.95
- 80 successes, 20 failures / 100 → reliability = 0.80 → trust = 0.80
- 90 successes, 10 failures / 100, but 2 were data-loss failures → trust = 0.90 - 0.60 = 0.30
- 100 successes / 100 attempts → trust = 1.0

**Lookback Window**: 30 days (or 100 actions minimum, whichever is larger)

### Component 3: Federation Consensus (Weight: 0.20)

What do peer nodes report about this actor?

```
federation_reports = queryFederationNodes({
    actor_id: actor.id,
    timestamp: now - 30.days
})

agreement_score = count(reports with trust_score >= 0.7) / count(reports)

// Weighted by reporting node's own trust score
weighted_agreement = sum(
    report.trust_score × federation_node.trust_score
) / sum(federation_node.trust_score)

// Trust nodes with themselves
trust_federation = weighted_agreement
```

**Examples**:

- 5 federation nodes report trust >= 0.8 → agreement = 1.0
- 3 report trust >= 0.8, 2 report trust < 0.5 → agreement = 0.6
- Reporting from only 1 node (not well-known) → reduced weight
- Explicit contradiction from high-trust federation nodes → can reduce trust

### Component 4: Cryptographic Proof (Weight: 0.10)[^18]

Has the actor provided cryptographic proof of identity?[^25]

```
proof_score ∈ {
    0.0: no_proof,
    0.5: standard_tls_certificate_from_ca,
    0.8: digitally_signed_request_from_verified_key,
    1.0: request_verified_with_multiple_keys + timestamp_proof + nonce
}
```

**Examples**:

- HTTPS TLS certificate from known CA → 0.5
- Request signed with ED25519 key (verified in trust model) → 0.8
- Request signed + multi-signature attestation + proof-of-freshness → 1.0

---

## Overall Trust Score Calculation

```math
trust\_score = 0.30 × verify\_score +
              0.40 × reliability\_score +
              0.20 × federation\_score +
              0.10 × proof\_score

trust\_score = clamp(trust\_score, 0.0, 1.0)
```

**Concrete Example**:

```
Actor: user:alice@corp.com

verify_score = 0.8    (organization-verified identity)
reliability = 0.95    (95/100 successful actions in 30d)
federation = 0.85     (4/5 federation nodes report trust >= 0.8)
proof_score = 0.8     (digitally signed request with verified key)

trust_score = 0.30×0.8 + 0.40×0.95 + 0.20×0.85 + 0.10×0.8
            = 0.24 + 0.38 + 0.17 + 0.08
            = 0.87 (HIGH TRUST)
```

---

## Trust Score Tiers & Implications[^17]

| Tier | Score | Implications | Risk Multiplier | Requires Escalation |
|------|-------|--------------|-----------------|------------------|
| **Untrusted** | < 0.3 | Assume malicious; minimal capabilities | 3.0× | >2.0 risk |
| **Low** | 0.3-0.5 | Restrictive; high monitoring | 2.0× | >4.0 risk |
| **Moderate** | 0.5-0.7 | Normal operations with oversight | 1.5× | >5.0 risk |
| **High** | 0.7-0.9 | Trusted; less monitoring needed | 1.0× | >8.0 risk |
| **Very High** | 0.9-1.0 | Highly trusted; minimal restrictions | 0.5× | >10.0 risk (never) |

**Risk Multiplier** = applied to capability base risk in AEGIS_AGP1_RISK_SCORING.md

---

## Trust Score Updates

Trust scores are not static. They are recalculated based on recent activity:

### Update Frequency

- **Real-time**: Immediately after critical events (policy violations, major failures)
- **Hourly**: Batch recalculation of reliability and federation scores
- **Daily**: Full trust score recalculation for all active actors

### Decay Mechanism

```python
def trust_score_with_age_adjustment(actor_id):
    trust_score = getTrustScore(actor_id)
    days_inactive = (now - actor.last_action_timestamp) / 86400
    
    # Trust slightly decays with inactivity (uncertainty grows)
    # Half-life: 180 days
    decay_factor = e^(-0.0038 × days_inactive)  # 0.0038 ≈ ln(2)/180 days
    
    return trust_score × decay_factor

# Example:
# trust_score = 0.9, had no activity for 90 days
# adjusted_trust = 0.9 × e^(-0.0038 × 90) = 0.9 × 0.69 = 0.62
```

**Rationale**:

- Recent behavior is more predictive[^26]
- Incentivizes continued good behavior
- Allows low-trust actors to rehabilitate

### Recovery Path

Untrusted or low-trust actors can improve their score:

```
1. Successful execution:        +0.01 to reliability score
2. Explicit federation vouching: +0.05
3. Cryptographic attestation:    +0.05
4. No violations for 7 days:     +0.03
5. Explicit human approval:      +0.10 (one-time boost)
```

**Minimum recovery threshold**: 0.3 (untrusted floor; must be approved externally)

---

## Special Cases

### System Actors

System services (e.g., scheduler, security scanner) have bootstrap trust:

```
system_trust_score = {
    "scheduler": 0.95,
    "security_scanner": 0.95,
    "infrastructure_monitor": 0.90,
    "audit_system": 1.0,
    "governance_engine": 1.0
}
```

These are assigned at deployment and can be reduced by policy if compromised.

### New Actors

New actors (unknown to the node) start with:

```
new_actor_trust = 0.50  (neutral: no historical data)

// Unless explicitly vouched:
if federation_nodes_vouch(actor) and consensus >= 0.8:
    new_actor_trust = 0.65

if actor_self_identified_only:
    new_actor_trust = 0.30
```

### LLM Actors

LLM models have additional trust factors:

```
llm_trust_score components:
  - Model integrity verification (model signature)     [0.0-1.0]
  - Publisher trust (is OpenAI trusted? Yes: 0.95)     [0.0-1.0]
  - Deployment environment trust (running where?)      [0.0-1.0]
  - Fine-tuning verification (was this model modified) [0.0-1.0]
  
llm_trust = 0.40 × model_integrity +
            0.30 × publisher_trust +
            0.20 × deployment_trust +
            0.10 × tuning_verification
```

---

## Trust Attestation & Certification

Federation nodes can explicitly attest to trust via signed certificates[^20]:

```json
{
    "certificate_type": "trust_attestation",
    "issuer_did": "did:aegis:federation:core-node-01",
    "subject_id": "user:alice@corp.com",
    "trust_score": 0.85,
    "validity_period": "90 days",
    "issued_at": "2026-03-05T00:00:00Z",
    "evidence": [
        "100 successful actions in 30 days",
        "historical_reliability_0.98",
        "no_policy_violations",
        "federation_consensus_0.90"
    ],
    "signature": "0x..."
}
```

A node receiving this certificate can:

1. Verify issuer's signature (using issuer's public key)
2. Verify subject identity (cryptographically)
3. Adopt trust score if issuer is trusted
4. Weight with local assessment: `trust = 0.7 × local + 0.3 × attested`

---

## Trust Revocation

Trust can be revoked immediately upon:

```
IMMEDIATE_REVOCATION_TRIGGERS:
  - Cryptographic key compromise
  - Policy violation (unauthorized access)
  - Attempted privilege escalation
  - Fraud or impersonation attempt
  - External federation alert (high-confidence)
```

Upon revocation:

1. All pending requests with this actor → DENY
2. Trust score → 0.0
3. Audit log entry → TRUST_REVOKED
4. Federation nodes → REVOCATION_NOTICE (propagated)
5. Manual remediation required to recover

---

## Audit Logging

All trust calculations are logged:

```json
{
    "event": "TRUST_SCORE_CALCULATED",
    "actor_id": "user:alice@corp.com",
    "timestamp": "2026-03-05T10:00:00Z",
    "trust_components": {
        "identity_verification": 0.8,
        "historical_reliability": 0.95,
        "federation_consensus": 0.85,
        "cryptographic_proof": 0.8
    },
    "weights": [0.30, 0.40, 0.20, 0.10],
    "resulting_trust_score": 0.87,
    "trust_tier": "HIGH",
    "historical_data_window": "2026-02-03 to 2026-03-05",
    "federation_nodes_sampled": 5,
    "last_trust_score": 0.85,
    "changed": true
}
```

---

## Next Steps

- [AGP1_PolicyLanguage.md](./AGP1_PolicyLanguage.md) - Policy rules that use trust scores
- [AEGIS_AGP1_RISK_SCORING.md](./AEGIS_AGP1_RISK_SCORING.md) - Complete risk scoring calculations
- [AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md](../federation/AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md) - Trust evaluator component

---

## References

[^17]: National Institute of Standards and Technology, *Zero Trust Architecture*, NIST SP 800-207, Aug. 2020. [Online]. Available: <https://doi.org/10.6028/NIST.SP.800-207>. See [REFERENCES.md](../../REFERENCES.md).

[^18]: B. Campbell, J. Bradley, N. Sakimura, and T. Lodderstedt, "OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens," RFC 8705, Internet Engineering Task Force, Feb. 2020. [Online]. Available: <https://www.rfc-editor.org/rfc/rfc8705>. See [REFERENCES.md](../../REFERENCES.md).

[^20]: M. Sporny, A. Guy, M. Sabadello, and D. Reed, "Decentralized Identifiers (DIDs) v1.0: Core architecture, data model, and representations," W3C Recommendation, 19 Jul. 2022. [Online]. Available: <https://www.w3.org/TR/2022/REC-did-core-20220719/>. See [REFERENCES.md](../../REFERENCES.md).

[^25]: S. Rodriguez Garzon et al., "AI Agents with Decentralized Identifiers and Verifiable Credentials," arXiv:2511.02841v2, 2025. [Online]. Available: <https://arxiv.org/abs/2511.02841>. See [REFERENCES.md](../../REFERENCES.md).

[^26]: A. Jøsang, R. Ismail, and C. Boyd, "A survey of trust and reputation systems for online service provision," *Decision Support Systems*, vol. 43, no. 2, pp. 618–644, Mar. 2007, doi: 10.1016/j.dss.2005.05.019. See [REFERENCES.md](../../REFERENCES.md).

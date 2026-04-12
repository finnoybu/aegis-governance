---
title: "AEGIS AGP-1 Risk Scoring & Decision Thresholds"
description: "AGP-1 risk scoring — threat quantification within the protocol"
---

# AEGIS AGP-1 Risk Scoring & Decision Thresholds

**Document**: AGP-1/Risk (AEGIS_AGP1_RISK_SCORING.md)\
**Version**: 1.0 (Normative)\
**Part of**: AEGIS Governance Protocol\
**References**: AGP-1/Trust, GFN-1/Nodes\
**Last Updated**: March 6, 2026

---

### Overview

After policy evaluation determines an ALLOW decision, the runtime computes a **risk score** based on 5 independent factors. If risk exceeds thresholds, the decision may be downgraded to ESCALATE or DENY.

Risk scoring combines:

- **Historical data**: What happened before with this actor/capability
- **Reputation**: Actor's trust score from federation
- **Capability risk**: How dangerous is this capability
- **Anomaly detection**: Is this pattern unusual
- **Federation signals**: What do peer nodes report

---

### Risk Scoring Factors

All factors are independent and normalized to [0.0, 10.0] scale.

#### Factor 1: Historical Attempt Rate (Weight: 0.30)

Measures frequency of failures for this actor on this capability.

```math
failed_attempts_24h = count(execution_reports where status=failed in last 24 hours)
total_attempts_24h = count(all execution_reports in last 24 hours)

rate_of_failure = failed_attempts_24h / total_attempts_24h

risk_historical = rate_of_failure × 10.0
risk_historical = clamp(risk_historical, 0.0, 10.0)
```

**Examples**:

- 0 failures / 100 attempts → risk = 0.0 (very reliable)
- 5 failures / 100 attempts → risk = 0.5 (good track record)
- 50 failures / 100 attempts → risk = 5.0 (problematic)
- 100 failures / 100 attempts → risk = 10.0 (always fails)

**Data Source**: Audit log EXECUTION_REPORT messages\
**Lookback**: Last 24 hours (or 100 events minimum, whichever larger)

#### Factor 2: Actor Reputation/Trust Score (Weight: 0.25)

Actor's trust score from AEGIS_AGP1_TRUST_MODEL.md, normalized to risk.

```math
actor_trust_score = getTrustScore(actor_id)  // [0.0 - 1.0] from trust model
risk_actor = (1.0 - actor_trust_score) × 10.0
```

**Examples**:

- trust_score 0.95 (highly trusted) → risk = 0.5
- trust_score 0.80 (good) → risk = 2.0
- trust_score 0.50 (moderate) → risk = 5.0
- trust_score 0.10 (low trust) → risk = 9.0

**Data Source**: Trust evaluator (from federation trust model)\
**Update Frequency**: Hourly; cached with TTL

#### Factor 3: Capability Sensitivity (Weight: 0.20)

How sensitive/dangerous is this capability.

```math
capability_risk_baseline = capability.risk_baseline  // [0.0 - 10.0]

// Adjust for context
context_multiplier = 1.0
if request.environment == "production":
  context_multiplier = 2.0
if request.scope includes "delete_data":
  context_multiplier = 1.5
if request.scope includes "modify_policy":
  context_multiplier = 2.5
if request.is_emergency_override:
  context_multiplier = 3.0

risk_capability = capability_risk_baseline × context_multiplier
risk_capability = clamp(risk_capability, 0.0, 10.0)
```

**Examples**:

- `telemetry.query` (baseline 2.5) in staging → risk = 2.5
- `telemetry.query` (baseline 2.5) in production → risk = 5.0
- `infrastructure.modify_policy` (baseline 8.0) in production → risk = 20.0 → clamped to 10.0
- `data.delete` (baseline 9.0) in production with delete scope → risk = 9.0 × 2.0 = 10.0

**Data Source**: Capability Registry definition\
**Static**: Does not change per request

#### Factor 4: Behavioral Anomaly (Weight: 0.15)

Detect actions outside actor's normal pattern.

```pseudo
function computeAnomalyScore(action, actor_id):
    baseline_actions = getHistoricalActions(actor_id, lookback_days=30)
    
    // Features: capability, time_of_day, day_of_week, parameters size, target
    current_features = extractFeatures(action)
    baseline_distribution = buildDistribution(baseline_actions)
    
    // Compute anomaly using statistical distance
    anomaly_score = computeStatisticalDistance(
        current_features, 
        baseline_distribution
    )
    
    // Normalize to [0.0, 1.0]
    // 0.0 = normal, 1.0 = extremely anomalous
    return clamp(anomaly_score, 0.0, 1.0)

risk_anomaly = anomaly_score × 10.0
```

**Anomaly Detection Examples**:

- Actor normally queries SIEM during business hours; now querying at 2 AM → anomaly_score = 0.7 → risk = 7.0
- Actor normally makes 10 API calls/day; now making 1000 → anomaly_score = 0.95 → risk = 9.5
- Actor never queried production; suddenly does → anomaly_score = 0.8 → risk = 8.0

**Data Source**: Audit logs (EXECUTION_REPORT historical data)\
**Lookback**: Last 30 days; requires at least 10 baseline actions
**Bootstrap**: If no history, anomaly_score = 0.0 (assume normal for new actors)

#### Factor 5: Federation Signals (Weight: 0.10)

Incorporate signals from federation peers about this action.

```pseudo
function computeFederationRisk(action):
    signals = queryFederationFeeds(action)  // Get incident/warning reports
    
    // Count signals that contradict this action
    contradiction_count = signals.count(s =>
        s.category == action.capability AND
        s.severity >= "medium" AND
        s.timestamp > now - 24.hours
    )
    
    // Each contradiction increases risk
    risk_federation = contradiction_count × 2.0
    risk_federation = clamp(risk_federation, 0.0, 10.0)
    
    return risk_federation
```

**Examples**:

- No federation signals → risk = 0.0
- 1 incident report about this capability → risk = 2.0
- 3 incident reports from different sources → risk = 6.0
- 5+ incident reports → risk = 10.0 (clamped)

**Data Source**: Federation governance feeds (AGP-1 on other nodes)\
**Lookback**: Last 24 hours; weighted by signal freshness (newer = higher weight)
**Trust**: Only count signals from nodes with trust_score ≥ 0.6

---

### Overall Risk Score Calculation

```math
risk\_score = 0.30 × risk\_historical +
             0.25 × risk\_actor +
             0.20 × risk\_capability +
             0.15 × risk\_anomaly +
             0.10 × risk\_federation

risk\_score = clamp(risk\_score, 0.0, 10.0)
```

**Concrete Example**:

```
Actor: agent:alice (trust_score 0.80)
Capability: telemetry.query (baseline 2.5, environment production)
Request: Query SIEM at 3 AM (unusual for this actor)

Factor 1 (Historical): 2 failures / 50 attempts = 0.4
Factor 2 (Actor): (1.0 - 0.80) × 10 = 2.0
Factor 3 (Capability): 2.5 × 2.0 (production) = 5.0
Factor 4 (Anomaly): Anomaly score 0.7 × 10 = 7.0
Factor 5 (Federation): 1 incident signal × 2 = 2.0

Overall: 0.30×0.4 + 0.25×2.0 + 0.20×5.0 + 0.15×7.0 + 0.10×2.0
       = 0.12 + 0.50 + 1.00 + 1.05 + 0.20
       = 2.87

Risk score: 2.87 (MODERATE)
```

---

### Decision Thresholds[^17]

After computing risk_score, the decision is determined:

```pseudo
// Policy evaluation already returned ALLOW
decision = evaluatePolicy(action, capability)  // Returns: ALLOW or DENY

if decision == DENY:
    // Policy denied; risk assessment not needed
    return DECISION_RESPONSE(DENY, ...)

// Policy allows; now check risk
risk_score = computeRiskScore(action)

if risk_score <= 2.0:
    // LOW RISK: Allow immediately
    return DECISION_RESPONSE(
        decision=ALLOW,
        risk_score=risk_score,
        constraints=capability.constraints
    )

elif risk_score <= 5.0:
    // MEDIUM RISK: Allow with enhanced monitoring
    enhanced_constraints = {
        ...capability.constraints...,
        monitoring_enabled: true,
        execution_logging: "verbose",
        requires_execution_report: true,
        immediate_notification: true
    }
    return DECISION_RESPONSE(
        decision=ALLOW,
        risk_score=risk_score,
        constraints=enhanced_constraints,
        confidence=0.8
    )

elif risk_score <= 8.0:
    // HIGH RISK: Escalate for human review
    return ESCALATION_REQUEST(
        reason="high_risk_action",
        severity="high",
        risk_score=risk_score,
        risk_breakdown={...},
        required_actions=["verify_actor_identity", "confirm_justification", "approve"],
        expire_at=now + 1_hour
    )

else:  // risk_score > 8.0
    // CRITICAL RISK: Deny and alert
    return DECISION_RESPONSE(
        decision=DENY,
        reason="critical_risk_score",
        risk_score=risk_score,
        explanation=f"Risk score {risk_score} exceeds maximum threshold (8.0)"
    )
```

#### Threshold Rationale

| Threshold | Rationale | Human Review |
|-----------|-----------|---------------|
| ≤ 2.0 | Well-understood, low-impact, well-behaved actor pattern | No |
| 2.0 - 5.0 | Normal operations with heightened awareness | No (but monitored) |
| 5.0 - 8.0 | Unusual pattern requiring human judgment | **Yes** |
| > 8.0 | Potential security incident or policy violation | Blocked |

---

### Confidence Score Calculation

Decision confidence reflects how deterministic the decision is:

```python
confidence = 0.0

## High confidence if policy match is explicit and specific
if decision_matched_explicit_policy:
    confidence += 0.6

## High confidence if risk factors are stable (not anomalous)
if risk_anomaly < 2.0:
    confidence += 0.2

## High confidence if actor is highly trusted
if actor_trust_score > 0.9:
    confidence += 0.1

## Reduce confidence if federation signals are conflicting
contradiction_count = count_contradictory_signals()
if contradiction_count > 0:
    confidence -= 0.1 × min(contradiction_count, 5)
    confidence = max(confidence, 0.0)

## Reduce confidence if some data is unavailable or stale
if has_stale_data or has_unavailable_signals:
    confidence -= 0.2
    confidence = max(confidence, 0.0)

confidence = clamp(confidence, 0.0, 1.0)
```

**Confidence Interpretation**:

- **0.95+**: Very high confidence; decision is deterministic
- **0.8-0.95**: High confidence; minor uncertainties
- **0.5-0.8**: Moderate confidence; some ambiguity
- **< 0.5**: Low confidence; multiple conflicting signals

---

### Risk Score Decay

Risk scores age over time. Historical data becomes less relevant:

```math
risk\_score\_decayed = risk\_score × e^{-\lambda t}
```

Where:

- λ = 0.01 per day (half-life ≈ 69 days)
- t = days since last update of underlying metrics

**Application**:

```python
## When retrieving actor's historical metrics for risk computation
historical_attempts = getHistoricalAttempts(actor_id)

for attempt in historical_attempts:
    days_ago = (now - attempt.timestamp) / 86400
    attempt_risk_weight = e^(-0.01 × days_ago)
    // Newer attempts have higher weight
```

**Rationale**:

- Recent behavior is more predictive than old behavior
- Helps recover from temporary anomalies
- Ensures risk scores can improve over time

---

### Federation Signal Integration

Risk scores are informed by federation reports. Example:

```python
## Federation reports incident: "Prompt Injection Vulnerability in telemetry.query"
incident_signal = {
    "signal_id": "sig-llm-inj-001",
    "severity": "high",
    "affected_capability": "telemetry.query",
    "timestamp": "2026-03-05T10:00:00Z",
    "publisher_did": "did:aegis:federation:security-research",
    "publisher_trust_score": 0.95
}

## Today when actor proposes telemetry.query:
federation_signals = query_federation_feeds({
    capability: "telemetry.query",
    lookback: 24_hours,
    min_trust_score: 0.6
})
## Returns: [incident_signal]

## Risk factor includes this signal
```

---

### Audit Logging

All risk score components are logged:

```json
{
  "decision_id": "dec-001",
  "risk_factors": {
    "historical_attempt_rate": 0.4,
    "actor_trust_score": 2.0,
    "capability_sensitivity": 5.0,
    "behavioral_anomaly": 7.0,
    "federation_signals": 2.0,
    "overall_risk_score": 2.87
  },
  "risk_factor_sources": {
    "historical": "audit_log_24h_window",
    "actor_trust": "federation_trust_model_v1",
    "capability": "capability_registry_2026.03.05",
    "anomaly": "baseline_from_30d_history",
    "federation": "3_incident_feeds, 2 policy feeds"
  },
  "decision_based_on_risk": "ALLOW_WITH_MONITORING",
  "confidence_score": 0.85
}
```

---

### Testing & Validation

#### Risk Score Unit Tests

```yaml
test_case: "low_risk_trusted_actor_business_hours"
  actor: "analyst:alice"
  actor_trust_score: 0.95
  capability: "telemetry.query"
  environment: "staging"
  time_of_day: 10  # Business hours
  historical_success_rate: 0.98
  federation_signals: []
  
  expected_risk_score: < 2.0
  expected_decision: ALLOW

test_case: "high_risk_production_at_3am"
  actor: "analyst:alice"
  capability: "telemetry.query"
  environment: "production"
  time_of_day: 3  # Unusual time
  historical_success_rate: 0.98
  federation_signals: {"count": 2, "severity": "medium"}
  
  expected_risk_score: 5.0 - 8.0
  expected_decision: ESCALATE
```

---

### Next Steps

- [AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md) - Complete decision flows with risk thresholds
- [AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md) - Error codes and retry logic

---

### References

[^17]: National Institute of Standards and Technology, *Zero Trust Architecture*, NIST SP 800-207, Aug. 2020. [Online]. Available: <https://doi.org/10.6028/NIST.SP.800-207>. See [REFERENCES.md](../../REFERENCES.md).

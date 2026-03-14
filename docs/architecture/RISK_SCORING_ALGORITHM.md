# AEGIS™ Risk Scoring Algorithm

### Architectural Enforcement & Governance of Intelligent Systems

**Version**: 0.2\
**Status**: Informational\
**Part of**: AEGIS™ Architecture\
**Author**: Kenneth Tannenbaum\
**Last Updated**: March 6, 2026

---

## Overview

The risk engine calculates a numeric risk score (0–100) based on multiple
factors representing actor characteristics, capability properties, and
environmental context.

## Scoring Formula

```
risk_score = actor_risk + capability_risk + resource_sensitivity +
             environment_modifier + history_modifier

Where:
  actor_risk ∈ [0, 20]
  capability_risk ∈ [0, 25]
  resource_sensitivity ∈ [0, 25]
  environment_modifier ∈ [-10, +15]
  history_modifier ∈ [-10, +15]
  ────────────────────────────────────────
  risk_score ∈ [0, 100]
```

## Factor Definitions

### Actor Risk (0–20)

Assesses trustworthiness of requesting agent.

| Score | Meaning |
|-------|---------|
| 0–5 | Fully trusted system agent |
| 5–10 | Established agent, good history |
| 10–15 | New/untested agent |
| 15–20 | Unvetted or suspicious agent |

**Sources**:

- Agent registration status
- Historical behavior
- Authentication strength

### Capability Risk (0–25)

Intrinsic risk of the requested capability.

| Capability | Score | Reasoning |
|------------|-------|-----------|
| filesystem.read | 5–10 | Low risk, read-only |
| filesystem.write | 15–20 | Medium risk, modifies state |
| network.http_get | 5 | Low risk, external only |
| network.http_post | 15 | Medium risk, state mutation |
| compute.process_spawn | 20–25 | High risk, execution |
| data.database_query | 10–15 | Medium, depends on scope |

**Sources**:

- Capability definition
- Historical incident patterns
- Impact assessment

### Resource Sensitivity (0–25)

How sensitive/critical is the target resource.

| Resource | Score | Reasoning |
|----------|-------|-----------|
| /data/public/* | 0–5 | Public data, low sensitivity |
| /data/internal/* | 10–15 | Internal data, medium sensitivity |
| /etc/passwd | 20 | System data, high sensitivity |
| /etc/shadow | 25 | Authentication, critical |
| PII database | 25 | Personal data, regulatory |
| Configuration | 15–20 | System state, important |

**Sources**:

- Data classification
- Regulatory requirements
- System criticality

### Environment Modifier (–10 to +15)

Contextual factors affecting risk.

| Condition | Adjustment | Reasoning |
|-----------|------------|-----------|
| Development environment | –10 | Lower risk, isolated |
| Staging environment | –5 | Medium risk, closer to prod |
| Production environment | +10 | Higher risk, real data |
| Business hours | –5 | Monitored, staff present |
| Off-hours | +5 | Less monitoring |
| Routine operation | –5 | Expected behavior |
| Novel operation | +10 | Unexpected, unverified |

**Default**: 0 (neutral)

### History Modifier (–10 to +15)

Adjustment based on agent's historical behavior.

| Pattern | Adjustment | Reasoning |
|---------|------------|-----------|
| Clean history (100+ ops) | –10 | Proven behavior |
| Good history (50+ ops, 0 failures) | –5 | Established pattern |
| Neutral history | 0 | No history or mixed |
| Minor violations | +5 | Some policy breaches |
| Repeated violations | +10 | Pattern of issues |
| Security incident | +15 | Previously compromised |

**Default**: 0 (first request)

## Threshold Mapping

Risk score → Decision + Constraints:[^17]

| Range | Decision | Action |
|-------|----------|--------|
| 0–30 | ALLOW | Execute immediately |
| 31–60 | CONSTRAIN | Add runtime constraints |
| 61–80 | ESCALATE | Route to human review |
| 81–100 | DENY | Reject request |

## Worked Examples

### Example 1: Public Data Read (Low Risk)

**Request**: Agent reads `/data/public/report.csv`

```
actor_risk: 5 (trusted agent)
capability_risk: 8 (filesystem.read)
resource_sensitivity: 3 (public data)
environment_modifier: -5 (development env)
history_modifier: -5 (clean history)
────────────────────────────────────────
Total: 5 + 8 + 3 - 5 - 5 = 6
```

**Decision**: ALLOW  
**Reason**: Minimal risk, public data  
**Constraints**: None

---

### Example 2: Internal Data with Constraints (Medium Risk)

**Request**: Agent queries `production_db.users` table

```
actor_risk: 10 (moderate trust)
capability_risk: 15 (database_query)
resource_sensitivity: 18 (internal user data)
environment_modifier: +10 (production)
history_modifier: 0 (neutral)
────────────────────────────────────────
Total: 10 + 15 + 18 + 10 + 0 = 53
```

**Decision**: ALLOW_CONSTRAIN  
**Constraints**:

- Max rows: 5000
- Rate limit: 5 queries/minute
- Timeout: 30 seconds
- Audit all results

---

### Example 3: Sensitive File Access (High Risk)

**Request**: Agent attempts `/etc/shadow` read in production

```
actor_risk: 12 (new agent)
capability_risk: 20 (sensitive capability)
resource_sensitivity: 25 (authentication data)
environment_modifier: +10 (production)
history_modifier: 8 (minor violations)
────────────────────────────────────────
Total: 12 + 20 + 25 + 10 + 8 = 75
```

**Decision**: ESCALATE  
**Reason**: High risk, sensitive resource, production environment  
**Route**: Escalate to security team for review  
**Timeout**: 300 seconds before auto-deny

---

### Example 4: Compromised Agent (Critical Risk)

**Request**: Suspicious agent with history of violations attempts process spawn

```
actor_risk: 18 (unvetted, suspicious)
capability_risk: 25 (process_spawn is critical)
resource_sensitivity: 20 (system resource)
environment_modifier: +10 (production)
history_modifier: +15 (security incident)
────────────────────────────────────────
Total: 18 + 25 + 20 + 10 + 15 = 88
```

**Decision**: DENY  
**Reason**: Compromised agent with critical risk score  
**Action**: Request audit investigation, potential incident

---

## Implementation Notes

### Calculation

1. Look up actor_risk from CapabilityRegistry.get_actor_risk(agent_id)
2. Look up capability_risk from RiskEngine.get_capability_risk(cap_id)
3. Determine resource_sensitivity with resource classifier
4. Determine environment_modifier from request context
5. Determine history_modifier from AuditSystem query (last 100 ops)
6. Sum all factors (bounded to [0, 100])

### Caching

Cache actor_risk and capability_risk scores in memory with TTL=3600s.
Recalculate on config changes or audit events.

### Feedback Loop

Risk scores are learned from decision outcomes:

- If DENIED request later approved by humans: decrease risk
- If ALLOWED request later violated policy: increase risk
- If ESCALATED request quickly approved: decrease risk
- Pattern-based adjustments: analyze repeated violations

### Bias Prevention

Regularly audit risk scores for bias across:

- Agent types (human vs AI)
- Operational patterns (time of day, environment)
- Historical context (avoid false positives from old incidents)

---

## References

[^17]: National Institute of Standards and Technology, *Zero Trust Architecture*, NIST SP 800-207, Aug. 2020. [Online]. Available: <https://doi.org/10.6028/NIST.SP.800-207>. See [REFERENCES.md](../../REFERENCES.md).

# AEGIS™ Risk Scoring Model

### Architectural Enforcement & Governance of Intelligent Systems

**Version**: 0.2\
**Status**: Informational\
**Part of**: AEGIS™ Architecture\
**Author**: Kenneth Tannenbaum\
**Last Updated**: March 6, 2026

---

## Purpose

This model defines how risk is represented conceptually and mapped to governance
outcomes. Numerical implementation details are specified in:

- `docs/architecture/RISK_SCORING_ALGORITHM.md`

## Risk Model Dimensions

Risk is determined by five dimensions:

1. Actor trust posture.
2. Capability intrinsic risk.
3. Resource sensitivity.
4. Environment modifier.
5. Behavioral history modifier.

These dimensions provide contextual risk beyond static permissions.

## Risk Bands

| Band | Score Range | Meaning | Default Outcome |
|------|-------------|---------|-----------------|
| Low | 0-30 | Routine, bounded operation | ALLOW |
| Medium | 31-60 | Elevated but manageable risk | CONSTRAIN |
| High | 61-80 | Significant risk requiring oversight | ESCALATE |
| Critical | 81-100 | Unacceptable risk | DENY |

## Conceptual Risk Factors

### Actor Trust

- Reflects actor maturity, identity confidence, and prior behavior.

### Capability Risk

- Reflects inherent potential impact of requested operation.

### Resource Sensitivity

- Reflects classification and criticality of target resource.

### Environment Modifier

- Reflects deployment context (production, off-hours, incident state).

### History Modifier

- Reflects trend-based behavior and prior violations.

## Risk-to-Governance Mapping

Risk is advisory to policy, but binding to outcome thresholds.

- Policies can lower or raise effective risk within bounded limits.
- Risk cannot override explicit deny policy.
- Critical risk cannot be silently downgraded to allow.

## Model Invariants

1. Risk score must remain in bounded range [0, 100].
2. Same risk inputs must produce same score.
3. Missing high-impact factors cannot default to low risk.
4. High and critical bands must produce non-allow outcomes.

## Operational Uses

Risk outputs are used for:

- Real-time decision classification.
- Escalation routing.
- Adaptive constraints (rate, timeout, scope).
- Trend analytics and post-incident tuning.

## Calibration and Drift Control

Model maintenance requirements:

- Periodic calibration against incident outcomes.
- Drift detection for sudden score distribution shifts.
- Bias review across actor classes and environments.

## Verification Criteria

The risk model is considered healthy when:

- Threshold transition tests pass at all boundaries.
- Risk distribution aligns with expected operational profile.
- High-risk events correlate with stricter governance outcomes.
- No critical-risk request is executed without escalation override.

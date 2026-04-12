---
title: "AEGIS Decision Algorithm"
description: "Governance decision algorithm — deterministic policy evaluation"
---

# AEGIS Decision Algorithm

### Architectural Enforcement & Governance of Intelligent Systems

**Version**: 0.2\
**Status**: Informational\
**Part of**: AEGIS Architecture\
**Author**: Kenneth Tannenbaum\
**Last Updated**: March 6, 2026

---

## Overview

The decision engine converts a capability request into a deterministic[^2]
authorization decision through a two-stage evaluation pipeline.[^1]

## Inputs

- capability_request (AGPRequest)
- agent capabilities (from CapabilityRegistry)
- matched policies (from PolicyEngine)
- risk_score (from RiskEngine)
- actor_context and environment_context

## Decision Thresholds

| Risk Score | Decision | Constraint Applied |
|------------|----------|--------------------|
| 0--30 | ALLOW | None |
| 31--60 | ALLOW | Apply policy constraints |
| 61--80 | ESCALATE | Route to human/higher authority |
| 81--100 | DENY | Explicit rejection |

## Pseudocode

```python
function authorize(request: AGPRequest) -> AGPResponse:
    # Stage 1: Capability Check
    if not CapabilityRegistry.has_capability(
        agent_id=request.agent_id,
        capability=request.action.capability
    ):
        return DENY(
            reason="Agent lacks required capability",
            audit=record_decision(DENIED_CAPABILITY_CHECK)
        )
    
    # Stage 2: Policy Evaluation
    policies = PolicyEngine.find_matching_policies(request)
    
    for policy in policies:
        evaluation = policy.evaluate(request)
        
        if evaluation.effect == DENY:
            return DENY(
                reason="Denied by policy: " + policy.id,
                audit=record_decision(DENIED_POLICY)
            )
        
        if evaluation.effect == ALLOW:
            break  # First matching allow policy
    
    if no policies matched:
        return DENY(
            reason="No policies matched (default-deny posture)",
            audit=record_decision(DENIED_NO_MATCH)
        )
    
    # Stage 3: Risk Scoring
    risk_score = RiskEngine.calculate_risk(
        request=request,
        context=request.context
    )
    
    # Stage 4: Threshold-Based Decision
    if risk_score >= 81:
        return DENY(
            reason=f"Critical risk score: {risk_score}",
            audit=record_decision(DENIED_RISK)
        )
    
    if risk_score >= 61:
        return ESCALATE(
            reason=f"High risk score requires review: {risk_score}",
            audit=record_decision(ESCALATED)
        )
    
    if risk_score >= 31:
        return ALLOW(
            reason="Approved with constraints",
            constraints=policy.extract_constraints(),
            audit=record_decision(APPROVED_CONSTRAINED)
        )
    
    return ALLOW(
        reason="Approved",
        audit=record_decision(APPROVED)
    )
```

## Worked Examples

### Example 1: Low-Risk Approval (Score: 15)

**Request**: Agent reading public data

```
actor_trust = 5
capability_risk = 5
resource_sensitivity = 5
environment_modifier = 0
history_modifier = 0
Total: 15 → ALLOW
```

**Decision**: APPROVED\
**Reason**: Low-risk operation, no constraints

---

### Example 2: Moderate-Risk Constrained (Score: 45)

**Request**: Agent reading internal file

```
actor_trust = 10
capability_risk = 15
resource_sensitivity = 15
environment_modifier = 5
history_modifier = 0
Total: 45 → ALLOW with CONSTRAINTS
```

**Decision**: APPROVED_CONSTRAINED\
**Constraints Applied**:

- Max file size: 10MB
- Rate limited: 5 reads/minute
- Audit all reads

---

### Example 3: High-Risk Escalation (Score: 70)

**Request**: Agent accessing sensitive file in production

```
actor_trust = 10
capability_risk = 20
resource_sensitivity = 25
environment_modifier = 10
history_modifier = 5
Total: 70 → ESCALATE
```

**Decision**: ESCALATED\
**Reason**: High-risk operation requires human approval\
**Route**: Sent to security team for review

---

### Example 4: Critical-Risk Denial (Score: 85)

**Request**: Agent attempting to access shadow file

```
actor_trust = 5
capability_risk = 25
resource_sensitivity = 25
environment_modifier = 15
history_modifier = 15
Total: 85 → DENY
```

**Decision**: DENIED\
**Reason**: Critical risk threshold exceeded\
**Audit**: Security incident logged

---

## Policy Precedence

Policies are evaluated in priority order:

1. **Explicit DENY** (highest priority)
   - Evaluated first, immediately rejects
   - Cannot be overridden by ALLOW policies

2. **ALLOW/CONSTRAIN** (by priority field)
   - Evaluated in descending priority order
   - First match wins

3. **Default rule** (lowest priority)
   - If no policies match: DENY (default-deny posture)[^1]

## Escalation

Requests with risk_score ≥ 61 are escalated to:

- **Human Operator**: For immediate review (if configured)
- **Higher-Authority Engine**: For federated decisions
- **Audit Queue**: For subsequent analysis

**Timeout**: Escalations auto-deny after configurable timeout (default 300s)

---

## References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../../REFERENCES.md).

[^2]: F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security (TISSEC)*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382. See [REFERENCES.md](../../REFERENCES.md).

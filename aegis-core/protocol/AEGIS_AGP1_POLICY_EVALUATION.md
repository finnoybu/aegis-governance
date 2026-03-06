# AGP-1 Policy Evaluation & Capability Resolution

**Document**: AEGIS_AGP1_POLICY_EVALUATION.md  
**Version**: 1.0 (Normative)  
**Part of**: AEGIS Governance Protocol  
**References**: RFC-0003 (Capability Registry)  
**Last Updated**: March 5, 2026

---

## Overview

Policy evaluation is the **core decision logic** of AGP-1. When a client submits an ACTION_PROPOSE, the governance runtime:

1. Resolves the requested capability from the Capability Registry (RFC-0003)
2. Checks if actor has an explicit grant for that capability
3. Evaluates all matching policy rules deterministically
4. Returns ALLOW, DENY, or ESCALATE decision

This section specifies the exact evaluation algorithm and policy language.

---

## Capability Resolution

When ACTION_PROPOSE arrives with `capability: "telemetry.query"`, the runtime MUST:

### Step 1: Look Up Capability

Query Capability Registry for capability definition:

```json
{
  "capability_id": "telemetry.query",
  "version": "1.0.0",
  "status": "active",
  "authority": "soc-leadership",
  "category": "data_access",
  "requires_authentication": true,
  "requires_mfa": false,
  "requires_trusted_network": false,
  "risk_baseline": 2.5,
  "default_granted_to": ["role:soc-analyst", "role:soc-manager"],
  "policy_set_id": "pol-set-telemetry-001",
  "audit_required": true,
  "inherits_from": ["data.read:base"],
  "scope_limits": {
    "max_results": 1000,
    "max_query_complexity": 5
  }
}
```

If capability not found:

```
return DECISION_RESPONSE(
  decision=DENY,
  reason="capability_not_found",
  risk_score=0.0,
  confidence=1.0
)
```

### Step 2: Resolve Inheritance Chain

If capability inherits from base capabilities:

```python
capability_chain = resolve_inheritance(capability_id)
# Returns: [telemetry.query, data.read:base]

for base_capability in capability_chain:
    policies.extend(base_capability.policies)
    constraints.update(base_capability.constraints)
```

### Step 3: Check Explicit Grant

Verify actor has explicit grant for capability:

```python
grant = capability_registry.find_grant(
    actor_id=message.actor_id,
    capability_id=message.capability
)

if grant is None:
    return DECISION_RESPONSE(
        decision=DENY,
        reason="no_capability_grant",
        explanation=f"actor {actor_id} not granted {capability}"
    )

if grant.status == "REVOKED":
    return DECISION_RESPONSE(
        decision=DENY,
        reason="grant_revoked",
        explanation=f"grant revoked on {grant.revoked_date}"
    )

if grant.status == "SUSPENDED":
    return DECISION_RESPONSE(
        decision=DENY,
        reason="grant_suspended",
        explanation=f"grant suspended: {grant.suspend_reason}"
    )
```

### Step 4: Load Policy Set

Load the policy set associated with capability:

```json
{
  "policy_set_id": "pol-set-telemetry-001",
  "version": "2026.03.05",
  "description": "Policies for telemetry.query capability",
  "explicit_denies": [
    "deny_untrusted_networks",
    "deny_revoked_actors"
  ],
  "allow_policies": [
    "soc_analysts_business_hours",
    "soc_managers_anytime",
    "incident_response_override"
  ],
  "escalation_policies": [
    "unusual_query_complexity"
  ]
}
```

---

## Policy Language (Formal Specification)

AGP-1 requires AEGIS Policy DSL (Domain-Specific Language) for all policy definitions.

### Grammar (EBNF)

```ebnf
policy_document    = { policy_definition } ;
policy_definition  = "policy" string "{" policy_body "}" ;
policy_body        = [ "description:" string ]
                     [ "priority:" integer ]
                     [ "match" condition_block ]
                     [ "then" action_block ] ;

condition_block    = "{" { condition } "}" ;
condition          = expression { ("AND" | "OR") expression } ;
expression         = comparison | membership | function_call ;
comparison         = identifier operator literal ;
membership         = identifier "in" "[" literal_list "]" ;
operator           = "==" | "!=" | "<" | ">" | "<=" | ">=" ;

action_block       = "{" action_statement { ";" action_statement } "}" ;
action_statement   = "action:" action_value
                   | "constraints:" constraint_object
                   | "confidence:" number
                   | "reason:" string ;

action_value       = "ALLOW" | "DENY" | "ESCALATE" | "REQUIRE_CONFIRMATION" ;
```

### Policy Examples

#### Example 1: Simple Allow Policy

```
policy "soc_analysts_business_hours" {
  description: "SOC analysts may query SIEM during business hours"
  priority: 100
  
  match capability == "telemetry.query"
    AND actor.role in ["soc-analyst", "soc-manager"]
    AND day_of_week not in ["Saturday", "Sunday"]
    AND hour_of_day >= 8 AND hour_of_day <= 18
  
  then {
    action: ALLOW
    constraints: {
      max_results: 1000,
      timeout_seconds: 30
    }
    confidence: 0.95
  }
}
```

#### Example 2: Deny Policy with Precedence

```
policy "deny_untrusted_networks" {
  description: "Block queries from untrusted networks"
  priority: 1000  // Higher priority = evaluated first
  
  match network.is_trusted == false
    AND capability.requires_trusted_network == true
  
  then {
    action: DENY
    reason: "untrusted_network"
    confidence: 1.0
  }
}
```

#### Example 3: Conditional Escalation

```
policy "escalate_unusual_queries" {
  description: "Escalate complex queries for review"
  priority: 50
  
  match capability == "telemetry.query"
    AND parameters.query_complexity > 5
    AND actor.trust_score < 0.8
  
  then {
    action: ESCALATE
    reason: "unusual_query_pattern"
    confidence: 0.75
  }
}
```

#### Example 4: Infrastructure Deployment with Approval

```
policy "infrastructure_deploy_prod" {
  match capability == "infrastructure.deploy"
    AND parameters.environment == "production"
    AND actor.role in ["devops-lead", "infrastructure-architect"]
  
  then {
    action: REQUIRE_CONFIRMATION
    reason: "production_deployment_confirmation_required"
    constraints: {
      requires_change_request: true,
      change_request_id_required: true
    }
  }
}
```

### Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `capability` | string | yes in condition | Name of capability being evaluated |
| `actor.role` | array | in conditions | Roles actor is member of (from actor registry) |
| `actor.trust_score` | float | in conditions | Trust score [0.0 - 1.0] from AEGIS_AGP1_TRUST_MODEL |
| `environment` | enum | in conditions | `production`, `staging`, `development` |
| `day_of_week` | string | in conditions | Day name: Monday - Sunday |
| `hour_of_day` | integer | in conditions | 0-23 UTC hour |
| `network.is_trusted` | boolean | in conditions | Known trusted network |
| `parameters.*` | varies | in conditions | Action-specific parameters |

---

## Evaluation Algorithm (Deterministic)

```pseudo
function evaluatePolicy(actionPropose, capability, policySet):
  
  // Step 1: Check explicit deny policies FIRST (highest precedence)
  for each policy in policySet.explicit_denies sorted by priority desc:
    if policy.matches(actionPropose):
      log("deny_policy_matched: " + policy.id)
      return DENY(policy.reason)
  
  // Step 2: Evaluate allow policies in priority order
  for each policy in policySet.allow_policies sorted by priority desc:
    if policy.matches(actionPropose):
      constraints = policy.extractConstraints(actionPropose)
      confidence = policy.confidenceScore()
      log("allow_policy_matched: " + policy.id)
      return ALLOW(policy.id, constraints, confidence)
  
  // Step 3: Evaluate escalation policies
  for each policy in policySet.escalation_policies sorted by priority desc:
    if policy.matches(actionPropose):
      log("escalation_policy_matched: " + policy.id)
      return ESCALATE(policy.reason)
  
  // Step 4: No policy matched
  log("no_matching_policy")
  return DENY("no_matching_policy", 
              "no policy permits this action")
```

### Determinism Guarantees

This algorithm guarantees:

1. **Reproducibility**: Same input + same policies = same decision every time
2. **Completeness**: Every valid request reaches a decision (never hangs)
3. **Single Path**: Exactly one policy matches (no ambiguity)
4. **Explainability**: Can trace decision through policy IDs and reasons

---

## Conflict Resolution

When multiple policies could match, resolution order:

### Rule 1: Explicit DENY Always Wins

```
policy "deny_network_x" { action: DENY, priority: 500 }
policy "allow_user_y" { action: ALLOW, priority: 600 }

// Result: DENY (because explicit deny is checked first, regardless of priority)
```

### Rule 2: Higher Priority Evaluated First

```
policy "deny_untrusted" { priority: 1000 }  // Evaluated 1st
policy "allow_standard" { priority: 100 }   // Evaluated 2nd
```

### Rule 3: More Specific Policy Wins (same priority)

```
policy "telemetry_query_allowed" {
  match capability == "telemetry.query"  // Specific
    AND actor.role == "soc-analyst"
}

policy "data_query_allowed" {
  match capability starts_with "telemetry"  // General
}

// More specific policy wins
```

### Rule 4: First Matching Policy Wins (evaluation order)

If policies have same specificity and priority, first one in document order wins.

---

## Constraint Application

When policy returns ALLOW, constraints are extracted and enforced:

```json
{
  "decision": "ALLOW",
  "applied_constraints": {
    "max_results": 500,
    "timeout_seconds": 15,
    "requires_encryption": true,
    "audit_logging": "verbose",
    "notification_required": true
  }
}
```

Client MUST enforce these constraints during execution:

- **max_results**: Limit query results to 500 rows
- **timeout_seconds**: Kill action if > 15 seconds
- **requires_encryption**: Use TLS/encryption
- **audit_logging**: Enable verbose audit logging
- **notification_required**: Alert operator after execution

---

## Capability Inheritance

Capabilities may inherit constraints from base capabilities:

```
capability "telemetry.query.advanced" {
  inherits_from: "telemetry.query"
  
  additional_constraints: {
    requires_mfa: true,
    rate_limit: "100 per minute"
  }
}
```

Evaluation merges constraints:

```python
constraints = {}
for cap in inheritance_chain(capability_id):
    constraints.update(cap.constraints)

# Result includes both base and derived constraints
# Derived constraints override base (if both specified)
```

---

## Testing & Validation

### Policy Unit Tests

Every policy SHOULD have test cases:

```yaml
policy: "soc_analysts_business_hours"
test_cases:
  - name: "allow analyst during business hours"
    actor_id: "analyst:alice"
    actor_role: "soc-analyst"
    day_of_week: "Monday"
    hour_of_day: 10
    environment: "production"
    expected_decision: "ALLOW"
    
  - name: "deny analyst on weekend"
    actor_id: "analyst:alice"
    actor_role: "soc-analyst"
    day_of_week: "Saturday"
    hour_of_day: 14
    expected_decision: "DENY"
    expected_reason: "not_business_hours"
```

### Policy Simulation

Before deploying new policies:

```bash
# Simulate all historical requests against new policy set
$ aegis-simulate \
    --current-policy-set current.yaml \
    --new-policy-set new.yaml \
    --historical-requests requests.jsonl

Results:
  Total decisions: 10,000
  Changed from ALLOW → DENY: 23 (0.23%)  ⚠️ Impact!
  Changed from DENY → ALLOW: 0
  No change: 9,977 (99.77%) ✅
```

---

## Next Steps

- [AEGIS_AGP1_RISK_SCORING.md](./AEGIS_AGP1_RISK_SCORING.md) - Risk calculation and decision thresholds
- [AEGIS_AGP1_FLOWS.md](./AEGIS_AGP1_FLOWS.md) - Complete protocol flows with policy evaluation

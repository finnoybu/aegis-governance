# End-to-End Request Flow

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## Complete Walkthrough: AI Agent Reading Production Database

This document traces a capability request through all AEGIS components
from submission to decision to audit.

---

## Scenario Setup

**Agent**: `agent_prod_analyzer`

- Status: Established, 200+ successful operations
- First violation: 1 month ago (minor)

**Capability**: `data.database_query`

- Risk factor: 15 (execution against production infrastructure)

**Resource**: `production_db.customers`

- Sensitivity: 18 (contains internal business data, not PII)
- Classification: business_critical

**Environment**: Production, 2:15 AM (off-hours)

**Request Timestamp**: 2025-03-05T02:15:00Z

---

## Request Submission

### Initial Request

```json
{
  "agent_id": "agent_prod_analyzer",
  "capability": "data.database_query",
  "resource": "production_db.customers",
  "context": {
    "environment": "production",
    "operation_type": "routine_analysis",
    "query_complexity": "medium"
  }
}
```

Agent submits request to DecisionEngine.authorize()

---

## Stage 1: Capability Registration Check

### DecisionEngine.authorize() entry point

```python
function authorize(request: AGPRequest) -> AGPResponse

# Step 1: Verify agent holds requested capability
agent_id = "agent_prod_analyzer"
capability = "data.database_query"

capability_registry.has_capability(agent_id, capability)
# Looks up: capabilities["agent_prod_analyzer"] = {
#   "filesystem.read": true,
#   "data.database_query": true,
#   "network.http_get": true
#   ...
# }
```

**Result**: ✅ GRANTED — Agent has capability

**Log Entry**:

```
[CAP_CHECK] agent_prod_analyzer HAS data.database_query
```

---

## Stage 2: Policy Matching

### PolicyEngine.find_matching_policies()

**All policies in engine**:

1. `allow_public_read` (priority: 100)
2. `deny_shadow_files` (priority: 10)
3. `constrain_db_queries` (priority: 50)
4. `escalate_production_changes` (priority: 40)

**Candidate filtering**:

- Filter enabled policies only
- Filter non-callable conditions out

**Condition evaluation for each**:

#### Policy 1: allow_public_read

```yaml
conditions:
  - type: resource_prefix
    value: /data/public
  - type: capability
    value: filesystem.read
```

**Evaluation**:

- capability (filesystem.read) ≠ requested (data.database_query) → ❌ NO MATCH

#### Policy 2: deny_shadow_files

```yaml
conditions:
  - type: resource_exact
    value: /etc/shadow
```

**Evaluation**:

- resource_exact (/etc/shadow) ≠ requested (production_db.customers) → ❌ NO MATCH

#### Policy 3: constrain_db_queries

```yaml
effect: constrain
priority: 50
conditions:
  - type: capability
    value: data.database_query
  - type: environment
    value: production
  - type: resource_prefix
    value: production_db
constraints:
  max_rows: 10000
  rate_limit: "5/minute"
  timeout_seconds: 60
  audit_required: true
```

**Evaluation**:

- capability (data.database_query) = requested ✅
- environment (production) = request context ✅
- resource_prefix (production_db) matches production_db.customers ✅
- **MATCH** → Effect: CONSTRAIN with constraints

#### Policy 4: escalate_production_changes

```yaml
conditions:
  - type: capability
    value: data.database_write
```

**Evaluation**:

- capability (data.database_write) ≠ requested (data.database_query) → ❌ NO MATCH

**Result**: Matched Policy = `constrain_db_queries` (priority 50)

**Log Entry**:

```
[POLICY_MATCH] Matched policy: constrain_db_queries (effect: constrain)
```

---

## Stage 3: Risk Calculation

### RiskEngine.calculate_risk()

#### Component 1: Actor Risk

```python
actor_risk = risk_engine.get_actor_risk("agent_prod_analyzer")

# Lookup from actor registry:
# {
#   "operations_count": 200,
#   "failure_rate": 0.01,
#   "last_violation": "2025-02-05T10:30:00Z",
#   "trust_level": "established"
# }

actor_risk = 10  # Established agent (5-10 range)
```

#### Component 2: Capability Risk

```python
cap_risk = risk_engine.get_capability_risk("data.database_query")

# Database queries are medium risk:
# - Can access business data
# - Execution against critical infrastructure
# - Typically requires rate limiting

cap_risk = 15  # Medium-high
```

#### Component 3: Resource Sensitivity

```python
resource_sens = risk_engine.get_resource_sensitivity("production_db.customers")

# Internal business data:
# - Not personally identifiable information (PII)
# - Contains customer account information
# - Regulatory impact if leaked (not critical)

resource_sens = 18  # Medium-high
```

#### Component 4: Environment Modifier

```python
environment = request.context.get("environment", "unknown")
time_of_day = extract_hour_from_timestamp(request.timestamp)

environment_mod = 0
if environment == "production":
    environment_mod += 10

if time_of_day < 6 or time_of_day > 22:  # Off hours
    environment_mod += 5

# Result: production (+10) + off-hours (+5) = +15
environment_mod = 15
```

#### Component 5: History Modifier

```python
history = audit_system.get_agent_history(
    agent_id="agent_prod_analyzer",
    limit=100  # Last 100 operations
)

# Analysis:
success_count = 199
failure_count = 1  # One violation 1 month ago
success_rate = 99.5%

history_mod = 0
if success_count > 50 and success_rate > 99%:
    history_mod -= 5  # Good history discount
else:
    history_mod += 0

# Minor recent violation (1 month ago):
days_since_violation = 29
if days_since_violation > 30:
    # Violation aged out, no penalty
    history_mod = -5
else:
    history_mod += 0

# Result: -5 (good history discount)
history_mod = -5
```

#### Risk Score Calculation

```
risk_score = actor_risk + cap_risk + resource_sens + env_mod + hist_mod
risk_score = 10 + 15 + 18 + 15 + (-5)
risk_score = 53
```

**Result**: Risk Score = **53** (CONSTRAIN threshold)

**Log Entry**:

```
[RISK_CALC] Score=53
  actor_risk=10
  +(cap_risk=15)
  +(resource_sens=18)
  +(env_mod=15)
  +(history_mod=-5)
```

---

## Stage 4: Decision Threshold Evaluation

### DecisionEngine.evaluate_thresholds()

```python
risk_score = 53

if risk_score >= 81:
    return DENY("Critical risk")
elif risk_score >= 61:
    return ESCALATE("High risk requires review")
elif risk_score >= 31:
    return ALLOW_WITH_CONSTRAINTS("Medium risk, apply policy constraints")
else:
    return ALLOW("Low risk")

# 53 is in range [31, 61) → ALLOW_WITH_CONSTRAINTS
```

**Decision**: ALLOW (with constraints from matched policy)

**Log Entry**:

```
[DECISION] threshold_evaluation
  score=53 in range [31, 61)
  decision=ALLOW_CONSTRAIN
  source_policy=constrain_db_queries
```

---

## Stage 5: Constraint Application

### Extract Constraints from Matched Policy

From `constrain_db_queries` policy:

```yaml
constraints:
  max_rows: 10000
  rate_limit: "5/minute"
  timeout_seconds: 60
  audit_required: true
```

**Interpreted as**:

- Query may return max 10,000 rows
- Agent limited to 5 queries per minute
- Query execution timeout: 60 seconds
- All query details logged to audit system
- Results logged
- Execution time logged

---

## Stage 6: Audit Recording

### AuditSystem.record()

Atomic write to immutable log:

```python
audit_record = AuditRecord(
    audit_id="audit_20250305_021500_a1b2c3",
    timestamp="2025-03-05T02:15:00.123Z",
    agent_id="agent_prod_analyzer",
    capability_requested="data.database_query",
    resource="production_db.customers",
    
    # Decision
    decision="ALLOW_CONSTRAIN",
    reason="Medium risk query approved with constraints",
    
    # Risk breakdown
    risk_score=53,
    actor_risk=10,
    capability_risk=15,
    resource_sensitivity=18,
    environment_modifier=15,
    history_modifier=-5,
    
    # Policy match
    matched_policies=["constrain_db_queries"],
    applied_constraints={
        "max_rows": 10000,
        "rate_limit": "5/minute",
        "timeout_seconds": 60,
        "audit_required": true
    },
    
    # Context
    environment="production",
    request_context={"operation_type": "routine_analysis"},
    
    # Metadata
    request_id="req_20250305_021500_xyz789",
    is_deterministic=true
)

audit_id = audit_system.record(audit_record)
# Returns: "audit_20250305_021500_a1b2c3"
```

**Result**: Audit recorded, ID generated

**Log Entry**:

```
[AUDIT] recorded audit_id=audit_20250305_021500_a1b2c3
```

---

## Stage 7: Response to Agent

### DecisionEngine returns AGPResponse

```python
response = AGPResponse(
    decision="ALLOW",
    
    # Why this decision?
    reason="Medium risk query approved with constraints",
    
    # What constraints apply?
    constraints={
        "max_rows": 10000,
        "rate_limit": "5/minute",
        "timeout_seconds": 60,
        "audit_required": true
    },
    
    # Audit trail
    audit_id="audit_20250305_021500_a1b2c3",
    
    # Decision confidence
    risk_score=53,
    risk_level="MEDIUM",
    
    # Timing
    decision_latency_ms=12,  # Time to reach decision
    timestamp="2025-03-05T02:15:00.123Z"
)

return response to agent
```

---

## Complete Timeline

```
02:15:00.000  |  Request received
02:15:00.002  |  Capability check: PASS
02:15:00.004  |  Policy matching: matched constrain_db_queries
02:15:00.008  |  Risk calculation: 53
02:15:00.009  |  Threshold evaluation: ALLOW_CONSTRAIN
02:15:00.010  |  Constraints extracted
02:15:00.012  |  Audit recorded (audit_id generated)
02:15:00.012  |  Response returned to agent
              |
              |  Total latency: ~12ms
```

---

## Agent Execution Under Constraints

### What Happens Next

Agent receives ALLOW response and constraint set:

```python
# Agent receives response
response = decision_engine.authorize(request)

if response.decision == "ALLOW":
    # Extract constraints
    constraints = response.constraints
    
    # Wrap execution
    try:
        # Enforce timeout
        with timeout(constraints["timeout_seconds"]):
            
            # Check rate limit
            if not rate_limiter.check(
                agent_id="agent_prod_analyzer",
                limit=constraints["rate_limit"]
            ):
                raise RateLimitExceeded()
            
            # Execute query
            results = database.query(
                sql=build_query(),
                max_rows=constraints["max_rows"]
            )
            
            # Log results (audit_required=true)
            audit_system.log_execution(
                audit_id=response.audit_id,
                row_count=len(results),
                execution_time_ms=elapsed
            )
            
            return results
    
    except Exception as e:
        # Log execution failure
        audit_system.log_violation(
            audit_id=response.audit_id,
            error=str(e)
        )
        raise
```

---

## Follow-Up: Constraint Violation Detection

### If Agent Violates Constraints

Example: Agent attempts to return 15,000 rows (max is 10,000)

```
Tool Proxy Layer detects:
  row_count (15000) > max_rows (10000)

Action:
  - Truncate results to 10000 rows
  - Log violation to audit system
  - Increment agent violation counter
  - If pattern detected: increase actor_risk for future requests
  - Optional: escalate to human operator
```

---

## Analytics & Feedback

### Metrics Recorded

After request completion, these metrics added to system:

```python
metrics = {
    "total_requests": 12543,
    "total_allowed": 10230,
    "total_constrained": 1890,
    "total_escalated": 145,
    "total_denied": 278,
    
    "average_risk_score": 42.3,
    "average_decision_latency_ms": 8.7,
    
    "agent_metrics": {
        "agent_prod_analyzer": {
            "requests": 415,
            "allowed": 412,
            "constrained": 3,
            "escalated": 0,
            "denied": 0,
            "violation_count": 1,
            "success_rate": 0.9976
        }
    }
}
```

### Feedback Loop

Over time, AEGIS learns:

**Observation**: `agent_prod_analyzer` made 200+ requests, only 1 violation

**Decision**: Decrease actor_risk from 10 → 8 for future requests

**Effect**: Same request next time has risk_score = 51 (instead of 53) → Still CONSTRAIN, but lower risk

---

## Summary

| Stage | Time | Component | Result |
|-------|------|-----------|--------|
| Cap Check | 0.2ms | Registry | ✅ GRANTED |
| Policy Match | 1.0ms | PolicyEngine | ✅ constrain_db_queries |
| Risk Calc | 3.0ms | RiskEngine | 53 (MEDIUM) |
| Threshold | 0.8ms | DecisionEngine | ALLOW_CONSTRAIN |
| Audit | 1.0ms | AuditSystem | Recorded |
| **Total** | **~12ms** | **Full Stack** | **APPROVED** |

**Key Takeaway**: From request to decision response in ~12ms, with complete
deterministic evaluation and immutable audit trail for compliance and debugging.

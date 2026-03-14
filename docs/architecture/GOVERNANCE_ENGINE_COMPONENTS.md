# AEGIS™ Governance Engine Components

### Architectural Enforcement & Governance of Intelligent Systems

**Version**: 0.2\
**Status**: Informational\
**Part of**: AEGIS™ Architecture\
**Author**: Kenneth Tannenbaum\
**Last Updated**: March 6, 2026

---

## Core Components

### 1. CapabilityRegistry

**Purpose**: Maintains all valid capability definitions and agent grants.

**Key Methods**:

```python
register(capability: Capability) -> None
  # Raises: CapabilityError if already registered
  
grant(agent_id: str, capability_id: str) -> None
  # Raises: CapabilityError if capability unknown
  # Side effect: Creates audit record
  
revoke(agent_id: str, capability_id: str) -> None
  # Raises: CapabilityError if grant doesn't exist
  
get_agent_capabilities(agent_id: str) -> Set[str]
  # Returns: Empty set if agent unknown
  
has_capability(agent_id: str, cap_id: str) -> bool
  # Returns: False if either unknown
```

**Thread-Safety**: Protected by RWLock

---

### 2. PolicyEngine

**Purpose**: Policy evaluation and matching against requests.[^2]

**Key Methods**:

```python
add_policy(policy: Policy) -> None
  # Raises: PolicyError if invalid
  # Validates: ID, name, effect, conditions
  
remove_policy(policy_id: str) -> None
  # Raises: PolicyError if not found
  
find_matching_policies(request: AGPRequest) -> List[Policy]
  # Returns: Sorted by priority (descending)
  # Skips: Disabled policies
  
evaluate(request: AGPRequest) -> PolicyEvaluation
  # Returns: First matching policy result
  # Returns: DENIED if no matches (default-deny)
  
validate_policy(policy: Policy) -> bool
  # Raises: PolicyError with error_code
```

**Thread-Safety**: Protected by RWLock

**Error Codes**:

- EMPTY_POLICY_ID
- EMPTY_POLICY_NAME
- INVALID_POLICY_EFFECT
- NONCALLABLE_CONDITION
- EMPTY_CONDITION_DESC

---

### 3. RiskEngine

**Purpose**: Calculate contextual risk scores for decisions.

**Key Methods**:

```python
calculate_risk(request: AGPRequest, context: dict) -> float
  # Returns: Risk score 0-100
  # Factors: Actor trust, capability risk, resource sensitivity
  
get_actor_risk(agent_id: str) -> float
  # Returns: Actor base risk (0-20)
  
get_capability_risk(cap_id: str) -> float
  # Returns: Capability risk weight (0-25)
  
get_resource_sensitivity(resource: str) -> float
  # Returns: Resource sensitivity (0-25)
```

**Thread-Safety**: Read-only after initialization

---

### 4. DecisionEngine

**Purpose**: Orchestrate policy and risk evaluation → authorization decision.

**Key Methods**:

```python
authorize(request: AGPRequest) -> AGPResponse
  # Returns: Decision with reason, audit_id
  # Side effects: Records metrics, audits decision
  # Process:
  #   1. Check agent has capability (DENY if not)
  #   2. Match and evaluate policies
  #   3. Calculate risk score
  #   4. Apply decision thresholds
  #   5. Return decision + audit record
  
get_metrics() -> DecisionMetrics
  # Returns: Aggregated decision statistics
  
reset_metrics() -> None
  # Clears metrics counters
```

**Decision Logic**: See DECISION_ALGORITHM.md

**Thread-Safety**: Atomic operations via locks

---

### 5. AuditSystem

**Purpose**: Immutable record of all requests and decisions.

**Key Methods**:

```python
record(decision: AGPResponse) -> str  # audit_id
  # Returns: Unique audit record ID
  # Guarantees: Record is immutable after creation
  
get_record(audit_id: str) -> AuditRecord
  # Returns: Complete record or None
  
get_agent_history(agent_id: str, limit=100) -> List[AuditRecord]
  # Returns: Recent records for agent, sorted by time desc
  
batch_record(decisions: List[AGPResponse]) -> List[str]
  # Returns: List of audit IDs
  # Guarantees: Atomic batch operation
```

**Storage**: Write-Ahead Log (WAL) with SQLite

**Thread-Safety**: Thread-safe by design (serialized writes)

---

## Data Flow

```
CapabilityRequest
    ↓
[Parse & Validate]
    ↓
CapabilityRegistry.has_capability(agent, cap)
    ↓ (No) → DENY + audit → return
    ↓ (Yes)
PolicyEngine.find_matching_policies(request)
    ↓ (None) → DENY + audit → return
    ↓ (Found)
RiskEngine.calculate_risk(request)
    ↓
DecisionEngine.evaluate_thresholds(risk_score)
    ↓
Apply decision: ALLOW/CONSTRAIN/ESCALATE/DENY
    ↓
AuditSystem.record(decision)
    ↓
Return AGPResponse + audit_id
```

---

## Error Handling

### Component-Specific Errors

| Component | Exception | Trigger |
|-----------|-----------|----------|
| CapabilityRegistry | CapabilityError | Unknown capability, duplicate register |
| PolicyEngine | PolicyError | Invalid policy, condition error |
| RiskEngine | RiskError | Invalid inputs, calculation failure |
| DecisionEngine | DecisionError | Request validation failure |
| AuditSystem | AuditError | Storage failure, corruption |

### Error Propagation

```python
try:
    response = decision_engine.authorize(request)
except DecisionError as e:
    log_error(f"Decision failure: {e.error_code}")
    return AGPResponse(
        decision=Decision.DEFERRED,
        reason=f"System error: {e.error_code}",
        audit_id=None  # No record if evaluation failed
    )
```

### Failure Modes

1. **PolicyEngine crash**: DecisionEngine catches, logs, escalates
2. **AuditSystem failure**: Decision still returned, audit attempted on retry
3. **Risk calculation failure**: Default to ESCALATE (conservative)[^2]
4. **Capability registry corruption**: Fail-closed (assume no capability)[^2]

---

## Integration Points

Components are wired in DecisionEngine constructor:

```python
engine = DecisionEngine(
    capability_registry=registry,
    policy_engine=policies,
    risk_engine=risks,
    audit_system=audit
)
```

All component access is synchronized through DecisionEngine.authorize()[^1]

---

## References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../../REFERENCES.md).

[^2]: F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security (TISSEC)*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382. See [REFERENCES.md](../../REFERENCES.md).

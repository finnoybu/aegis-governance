# Policy Matching and Debugging Guide

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## Policy Matching Algorithm

When a capability request arrives, PolicyEngine finds matching policies using the following sequence:

### Step 1: Candidate Selection

Iterate through all enabled policies:
- Filter out disabled policies
- Filter out policies with non-callable conditions
- Result: A candidate set of policies

### Step 2: Condition Evaluation

For each candidate policy, evaluate ALL conditions:

```python
def policy_matches(policy, request):
    for condition in policy.conditions:
        if not condition.evaluate(request):
            return False
    return True
```

**Key**: ALL conditions must match (AND logic), not any (OR logic)

### Step 3: Priority Sorting

Match multiple policies? Sort by priority (descending):

```python
matching_policies = [p for p in all_policies if policy_matches(p, request)]
matching_policies.sort(key=lambda p: p.priority, reverse=True)
return matching_policies[0]  # First match wins
```

### Step 4: Effect Selection

The first matching policy's effect is used:
- DENY → immediately reject (no other policies evaluated)
- ALLOW → immediately approve (constrain per policy)
- CONSTRAIN → apply constraints from matching policy
- ESCALATE → escalate for human review

**Exception**: If ANY policy has effect=DENY, recheck for DENY matches first:

```python
# Check for explicit denies first
for policy in all_policies:
    if policy.effect == DENY and policy_matches(policy, request):
        return DENY

# Then evaluate others normally
for policy in sorted_policies:
    if policy_matches(policy, request):
        return policy.effect
```

## Pattern Matching Details

### Exact Match
```yaml
- type: resource_exact
  value: /etc/passwd
```
Matches only: `/etc/passwd`

### Prefix Match
```yaml
- type: resource_prefix
  value: /data/public
```
Matches:
- `/data/public`
- `/data/public/file.txt`
- `/data/public/subdir/other.txt`

Does NOT match:
- `/data/publicly_available` (not a directory boundary)
- `/data/publicity` (different path)

Implement as:
```python
resource.startswith(prefix) and (
    len(resource) == len(prefix) or
    resource[len(prefix)] == '/'
)
```

### Regex Match
```yaml
- type: resource_regex
  value: "^/var/log/.*\\.log$"
```

Uses Python `re.match()`:
- `^` = start of string
- `$` = end of string
- `.` = any character (use `\\.` for literal dot)
- `*` = zero or more
- `+` = one or more

Test patterns:
```python
import re
pattern = re.compile("^/var/log/.*\\.log$")
assert pattern.match("/var/log/app.log")
assert pattern.match("/var/log/subdir/app.log")
assert not pattern.match("/var/log/app.txt")
```

### Capability Hierarchy Match
```yaml
- type: capability
  value: filesystem
```

Matches:
- `filesystem` (exact)
- `filesystem.read`
- `filesystem.write`
- `filesystem.read.metadata`

Does NOT match:
- `filesystem_manager` (different name)
- `file` (different path)

Implement as:
```python
cap_requested.startswith(cap_policy) and (
    len(cap_requested) == len(cap_policy) or
    cap_requested[len(cap_policy)] == '.'
)
```

## Debugging a Decision

If a request was denied unexpectedly, follow this checklist:

### 1. Verify Capability Grant
```python
# Check if agent has this capability
registry.has_capability(agent_id, capability)
```

If False → DENIED_CAPABILITY_CHECK

### 2. Check Policy Matches
```python
# List all enabled policies
matching = [
    p for p in policies.all()
    if p.enabled and policy_matches(p, request)
]
```

Inspection points:
- Are policies enabled?
- Do conditions match?
- Is priority correct?

### 3. Examine Risk Score
```python
# Get breakdown
actor_risk = risk_engine.get_actor_risk(agent_id)
cap_risk = risk_engine.get_capability_risk(capability)
resource_sens = risk_engine.get_resource_sensitivity(resource)
env_mod = determine_environment_modifier(request)
hist_mod = determine_history_modifier(agent_id)

total_risk = sum([actor_risk, cap_risk, resource_sens, env_mod, hist_mod])
```

Is total_risk > 80? → DENIED_RISK

### 4. Review Decision Log
```python
# Get audit record
audit = audit_system.get_record(audit_id)

print(f"Decision: {audit.decision}")
print(f"Reason: {audit.reason}")
print(f"Risk Score: {audit.risk_score}")
print(f"Matched Policies: {audit.matched_policies}")
print(f"Timestamp: {audit.timestamp}")
```

## Common Debugging Scenarios

### Scenario A: "Policy Should Match But Doesn't"

**Symptom**: Expected policy not in matched set

**Investigation**:
1. Is policy **enabled**? Check `enabled: true`
2. Do **all conditions** match?
   ```python
   policy = get_policy_by_id("foo")
   for cond in policy.conditions:
       result = cond.evaluate(request)
       print(f"{cond.type} = {result}")
   ```
3. Is **priority** high enough? Compare with other matches

**Example Fix**:
```yaml
# BEFORE (priority 1 = too low)
policy_id: my_policy
priority: 1
conditions:
  - type: resource_prefix
    value: /data

# AFTER (priority 100 = evaluated first)
policy_id: my_policy
priority: 100
conditions:
  - type: resource_prefix
    value: /data
```

### Scenario B: "Risk Score Higher Than Expected"

**Symptom**: Request scored 75 when expecting 30

**Investigation**:
```python
breakdown = risk_engine.explain_score(request)
print(breakdown)
# Output:
# actor_risk: 10 (trusted)
# capability_risk: 15 (write)
# resource_sensitivity: 20 (PII)
# environment_modifier: +15 (production, off-hours)
# history_modifier: +5 (minor violations)
# ────────────────────
# Total: 75 → ESCALATE
```

**Common causes**:
- Environment flag set to production (+10 to +15)
- History modifier from recent violations (+5 to +15)
- Resource sensitivity overestimated
- Capability risk too high

### Scenario C: "Denied Because No Policies Matched"

**Symptom**: Request returns DENY with reason "No policies matched"

**Investigation**:
1. Does ANY policy target this capability?
   ```python
   policies_by_cap = policy_engine.find_policies_by_capability(request.capability)
   ```
2. If empty → No policies defined for this capability → Default-deny
3. If non-empty → Check conditions:
   ```python
   for p in policies_by_cap:
       matches = policy_matches(p, request)
       print(f"Policy {p.id}: {matches}")
       if not matches:
           for c in p.conditions:
               print(f"  {c.type}: {c.evaluate(request)}")
   ```

**Solution**: Add policy that matches, or add condition to existing policy

## Performance Considerations

### Policy Evaluation Latency

Expected timings:
- Simple conditions (exact, prefix, actor_id): < 1ms per policy
- Regex conditions: 1–5ms (depends on pattern complexity)
- Full decision (capability check + policy eval + risk + decision): 5–20ms

**Optimization**:
1. Sort policies by specificity (most specific first)
2. Use prefix matches instead of regex where possible
3. Cache compiled regex patterns
4. Use RWLock for policy queries (concurrent reads)

### Policy Count Impact

- 10 policies: negligible impact
- 100 policies: < 5ms overhead
- 1000+ policies: consider indexing by capability

## Debugging Output Example

```
=== DECISION AUDIT REPORT ===
timestamp: 2025-03-05T14:22:33Z
request_id: req_abc123
agent_id: agent_456
capability: filesystem.read
resource: /data/sensitive/file.txt

=== STAGE 1: Capability Check ===
Has capability? YES

=== STAGE 2: Policy Evaluation ===
Matching policies:
  1. policy_id: allow_public_read
     priority: 100
     conditions_met: NO (resource doesn't match /data/public)
  
  2. policy_id: block_sensitive_files
     priority: 10
     conditions_met: YES (all 3 conditions match)
     effect: DENY

=== STAGE 3: Risk Score ===
(skipped due to DENY policy)

=== DECISION ===
final_decision: DENY
reason: Denied by policy: block_sensitive_files
audit_id: audit_xyz789

=== END REPORT ===
```

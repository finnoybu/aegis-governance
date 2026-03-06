# AEGIS Policy Language

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## Overview

Policies are expressed in a structured YAML‑based DSL that defines
authorization rules for capability requests.

## Policy Structure

```yaml
policy_id: filesystem_read_policy
name: "Public Data Read Access"
effect: allow
priority: 100
enabled: true
conditions:
  - type: capability
    value: filesystem.read
  - type: resource_prefix
    value: /data/public
  - type: actor_role
    value: system_agent
constraints:
  max_size_mb: 100
  rate_limit: "10/minute"
risk_modifier: -10
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| policy_id | string | Yes | Unique policy identifier |
| name | string | Yes | Human-readable policy description |
| effect | enum | Yes | ALLOW, DENY, CONSTRAIN, ESCALATE |
| priority | int | Yes | Evaluation order (higher first) |
| enabled | bool | No | Enable/disable without deleting |
| conditions | list | Yes | List of condition objects |
| constraints | object | No | Applied constraints if approved |
| risk_modifier | int | No | Adjustment to risk score (-10 to +15) |

## Effects

| Effect | Meaning |
|--------|----------|
| allow | Grant capability request |
| deny | Reject capability request |
| constrain | Grant with runtime constraints |
| escalate | Require human/higher authority review |

## Condition Types

### Capability Match

```yaml
- type: capability
  value: filesystem.read
  # Matches exact capability or parent
  # filesystem.read matches: filesystem, filesystem.read (not filesystem.write)
```

### Resource Patterns

```yaml
- type: resource_prefix
  value: /data/public
  # Prefix match: matches /data/public/*, /data/public**

- type: resource_exact
  value: /etc/passwd
  # Exact match only

- type: resource_regex
  value: "^/var/log/.*\.log$"
  # Regex pattern match
```

### Actor Conditions

```yaml
- type: actor_id
  value: agent_123
  # Exact agent ID match

- type: actor_role
  value: system_agent
  # Actor must have role

- type: actor_trust
  comparison: ">"
  value: 80
  # Actor trust score threshold
```

### Environment Conditions

```yaml
- type: environment
  value: production
  # Environment must match

- type: time_window
  start: "09:00"
  end: "17:00"
  # Request within business hours

- type: day_of_week
  values: [Mon, Tue, Wed, Thu, Fri]
  # Weekdays only
```

## Constraint Types

Applied when effect=constrain:

```yaml
constraints:
  max_size_mb: 100              # File size limit
  max_rows: 1000               # Query result limit
  rate_limit: "10/minute"      # Requests per time
  timeout_seconds: 30          # Execution timeout
  audit_required: true         # Force full audit
  log_level: INFO              # Logging verbosity
```

## Example Policies

### Policy 1: Allow Public Data Read

```yaml
policy_id: allow_public_read
name: "Allow reading public data"
effect: allow
priority: 100
conditions:
  - type: capability
    value: filesystem.read
  - type: resource_prefix
    value: /data/public
risk_modifier: -5
```

### Policy 2: Block Sensitive Files

```yaml
policy_id: block_sensitive_files
name: "Block access to sensitive system files"
effect: deny
priority: 10
conditions:
  - type: capability
    value: filesystem.read
  - type: resource_regex
    value: "^(/etc/shadow|/etc/passwd|/etc/sudoers)$"
```

### Policy 3: Constrained Database Access

```yaml
policy_id: db_query_constrained
name: "Constrained database queries"
effect: constrain
priority: 50
conditions:
  - type: capability
    value: data.database_query
  - type: environment
    value: production
constraints:
  max_rows: 5000
  rate_limit: "5/minute"
  timeout_seconds: 30
  audit_required: true
risk_modifier: 5
```

### Policy 4: Escalate Critical Operations

```yaml
policy_id: escalate_critical_ops
name: "Escalate critical system operations"
effect: escalate
priority: 5
conditions:
  - type: capability
    value: compute.process_spawn
  - type: actor_role
    value: ai_agent
```

### Policy 5: Time-Windowed Access

```yaml
policy_id: business_hours_only
name: "Restrict sensitive operations to business hours"
effect: deny
priority: 20
conditions:
  - type: capability
    value: data.api_call
  - type: resource_prefix
    value: https://sensitive-api.internal
  - type: time_window
    start: "17:00"
    end: "09:00"
    # Denies outside 9am-5pm
```

## Condition Evaluation

All conditions within a policy are AND-ed:

```yaml
Policy matches if:
  (capability == filesystem.read)
  AND (resource matches /data/public)
  AND (actor_role == system_agent)
```

Policies with multiple conditions are more specific and prefer EXACT/REGEX
matches over PREFIX matches.

## Conflict Resolution

When multiple policies match:

1. **Explicit DENY always wins** (if any DENY matches)
2. **Priority field determines evaluation order** (higher first)
3. **First matching policy wins** (for ALLOW/CONSTRAIN/ESCALATE)
4. **Default-deny** if no policies match

## Performance Considerations

- Policy evaluation is O(n) where n = number of policies
- Regex conditions are slower than prefix/exact
- Sort policies by specificity + priority for optimal performance
- Cache compiled regex patterns

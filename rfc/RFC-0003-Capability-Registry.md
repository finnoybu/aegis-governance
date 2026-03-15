# RFC-0003: AEGIS™ Capability Registry and Policy 

**RFC:** RFC-0003
**Status:** Draft  
**Version:** 0.2  
**Created:** 2026-03-05  
**Updated:** 2026-03-06  
**Author:** AEGIS™ Initiative, Finnoybu IP LLC  
**Repository:** aegis-governance  
**Target milestone:** v1.0  
**Supersedes:** None  
**Superseded by:** None  

---

## Summary

This RFC specifies the capability schema, inheritance model, policy language syntax, and deterministic evaluation algorithm that together define what an AI agent is permitted to do within an AEGIS-governed environment.

---

## Motivation

The governance runtime ([RFC-0002](./RFC-0002-Governance-Runtime.md)) enforces decisions. This RFC defines the vocabulary and logic those decisions are based on. Without a formal capability model and policy language, governance is arbitrary. With it, governance is deterministic, auditable, and reproducible.

---

## Guide-Level Explanation

A capability is a named, versioned declaration of something an agent is allowed to attempt. Before an agent can take an action, that action must map to a registered capability the agent has been granted.

A policy is a rule that says: when these conditions are true, make this decision. Policies are evaluated in priority order. The first matching deny wins. If nothing matches, the default is deny.[^2]

Together, the capability registry and policy engine answer one question: should this agent be allowed to do this thing right now?

---

## Reference-Level Explanation

### 1. Capability Definition Schema

```yaml
id: telemetry.query
description: Query security telemetry datasets
parent: telemetry.*
allowed_roles: [soc_analyst, incident_responder]
environments: [staging, production]
risk_level: low
constraints:
  max_results: 500
  timeout_ms: 10000
deprecated: false
version: 1
```

### 2. Capability Inheritance Model

Capability IDs form a dotted hierarchy: `telemetry.*` (parent), `telemetry.query` (child), `telemetry.query.raw` (grandchild).

Inheritance rules:
- Child inherits parent constraints unless explicitly overridden
- Child may narrow permissions but may not broaden parent-denied scope
- Deny constraints on parent are immutable to descendants
- Multiple inheritance is not allowed in v1

Conflict resolution: stricter constraint wins; deny beats allow; environment intersection is applied.

### 3. Capability Validation Rules

A capability definition is valid only if:
1. `id` matches regex `^[a-z][a-z0-9_.-]*$`
2. `risk_level` is one of `low|medium|high|critical`
3. All `allowed_roles` are known roles
4. Parent exists (unless root capability)
5. No inheritance cycle exists
6. Constraint keys are from approved vocabulary

Invalid definitions MUST be rejected at registration time.
## 4. Policy Language

Policy outcomes: `ALLOW`, `DENY`, `ESCALATE`, `REQUIRE_CONFIRMATION`

Policy structure:

```yaml
policy_id: telemetry_query_allowed
priority: 100
enabled: true
when:
  capability: telemetry.query
  actor.role: soc_analyst
  environment: production
then:
  decision: ALLOW
  constraints:
    max_results: 500
```

### 5. Formal Policy Syntax (EBNF)

```text
policy      = header, when_clause, then_clause ;
header      = "policy_id" ":" IDENT, "priority" ":" INT, "enabled" ":" BOOL ;
when_clause = "when" ":", condition_list ;
condition_list = condition, { condition } ;
condition   = field, operator, value ;
field       = IDENT, { ".", IDENT } ;
operator    = "==" | "!=" | ">" | ">=" | "<" | "<=" | "in" | "matches" ;
then_clause = "then" ":", "decision" ":" DECISION, [constraints_clause] ;
DECISION    = "ALLOW" | "DENY" | "ESCALATE" | "REQUIRE_CONFIRMATION" ;
```

### 6. Policy Evaluation Algorithm

```text
1. Load enabled policies.
2. Sort ascending by priority number (0 is highest priority).
3. Evaluate policy conditions in order.
4. If a matching DENY is found, return DENY immediately.
5. Track first matching non-deny decision by priority.
6. Apply risk overrides without violating deny precedence.
7. If no match, return DENY (default deny).
8. Emit evaluation trace for audit.
```

Step 7 implements default-deny[^2] — absence of explicit authorization yields denial. Step 8 records the full evaluation trace to support complete auditability.[^1]

Complexity target: O(P * C), where P is policies and C is conditions per policy.

### 7. Complex Policy Examples

Role + environment + risk gate:

```yaml
policy_id: infra_deploy_prod_guard
priority: 10
enabled: true
when:
  capability: infrastructure.deploy
  environment: production
  actor.role in: [devops_engineer, sre]
  risk_score >=: 8
then:
  decision: REQUIRE_CONFIRMATION
```

Hard deny invariant:

```yaml
policy_id: deny_unknown_capability
priority: 0
enabled: true
when:
  capability_defined == false
then:
  decision: DENY
```

### 8. Policy Versioning

Policy sets MUST include: `policy_set_id`, semantic version, immutable hash, activation timestamp. Decision replay MUST reference policy-set version and hash.

---

## Drawbacks

- The capability hierarchy model adds complexity for organizations with flat authorization models. The inheritance rules must be understood before the registry can be correctly populated.
- Regex-based pattern matching in policy conditions is expressive but can produce unexpected matches. Implementers must validate patterns before activation.
- Policy evaluation is O(P * C). Large policy sets with many conditions will increase decision latency.

---

## Alternatives Considered

**Flat capability list without inheritance:** Simpler but requires every capability to be fully specified independently, producing large registries and making bulk policy changes difficult.

**Natural language policy definitions:** More accessible but non-deterministic. Governance that cannot be reproduced exactly given the same inputs is not governance.

**RBAC only:** Role-based access control is familiar but does not capture contextual conditions (environment, risk score, time window) that are essential for AI agent governance.

---

## Compatibility

Downstream of [RFC-0001](./RFC-0001-AEGIS-Architecture.md) and [RFC-0002](./RFC-0002-Governance-Runtime.md). The policy language defined here is the authoritative input to the Policy Engine specified in RFC-0002.

---

## Implementation Notes

The `deny_unknown_capability` hard deny invariant (Section 7) must be the first policy evaluated in any compliant implementation.

---

## Open Questions

- [ ] Should the policy language support time-window conditions (e.g., deny outside business hours)?
- [ ] Should capability deprecation produce ESCALATE or DENY by default?

---

## Success Criteria

- Any valid capability definition passes validation without modification
- Any invalid capability definition is rejected at registration time with a specific error
- Policy evaluation is deterministic: the same request, policy set, and registry always produce the same decision
- Evaluation trace is sufficient to reconstruct the decision from the audit record alone

---

## References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../REFERENCES.md).

[^2]: F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382. See [REFERENCES.md](../REFERENCES.md).

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*  
*AEGIS Initiative — Finnoybu IP LLC*

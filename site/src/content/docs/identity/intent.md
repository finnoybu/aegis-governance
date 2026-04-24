---
title: "AEGIS AIAM-1: Intent"
description: "AIAM-1 intent claims — structured purpose assertions at moment of action"
---

# AEGIS AIAM-1: Intent

**Document**: AIAM-1/Intent (/identity/intent/)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

This chapter defines intent claims — structured assertions of purpose that AI agents produce at the moment of action. Intent claims are the third input to IBAC authorization decisions (alongside identity and action) and the mechanism by which AIAM-1 binds agent actions to declared goals.

Intent is what distinguishes an AI agent from a service account. A service account executes a fixed script; its "intent" is implicit in its code and never changes. An AI agent plans dynamically, selects actions based on reasoning, and shifts goals within a single session. Without structured intent, an authorization system cannot distinguish between an agent querying a database for legitimate triage and the same agent querying the same database because a prompt injection redirected its reasoning.

---

## 2. Intent Claim Model

### 2.1 What an Intent Claim Is

An intent claim is a structured, machine-readable assertion produced by an agent at the moment it proposes an action. It declares:

- **What goal** the action serves (reference to goal context)
- **Why** the agent decided to take this action (reasoning summary)
- **What outcome** the agent expects
- **What prior actions** this action depends on

An intent claim is not free text. It is not a natural language explanation. It is a structured record that can be validated against the agent's declared goal context, evaluated by an IBAC policy engine, and preserved in an attestation record for forensic analysis.

### 2.2 What an Intent Claim Is Not

- **Not a guarantee of truthfulness.** An intent claim is an assertion by the agent. A compromised or manipulated agent may produce a false intent claim. AIAM-1 provides detection mechanisms (§5) but cannot guarantee that intent claims are always honest — this is an inherent limitation of governing probabilistic reasoning systems.
- **Not a replacement for capability checks.** An agent with a valid intent claim but without a matching capability grant is still denied. Intent is a necessary condition for authorization under IBAC, not a sufficient one.
- **Not a human-readable explanation.** Intent claims serve governance, not user experience. They are structured for machine evaluation, not for display to end users.

Intent claims are non-deterministic in origin but deterministic as input. The agent that produces an intent claim is probabilistic — its reasoning is shaped by model weights, context, and potentially adversarial inputs. But once emitted, the intent claim is a fixed data structure. Policy evaluation treats it as evidence, not as oracle. The IBAC engine evaluates the claim's fields against policy patterns with the same determinism it applies to identity and action. This is how IBAC reconciles its determinism requirement (AIAM1-AUTH-011) with intent claims produced by probabilistic agents: the authorization decision is deterministic over its inputs, even when one of those inputs was produced non-deterministically.

### 2.3 Relationship to AGP-1

AGP-1 ACTION_PROPOSE messages carry action parameters (capability, action_type, target, parameters) but do not carry structured intent. Intent is implicit in the parameters — the system infers purpose from what the agent is doing, not from what the agent says it is doing.

AIAM-1 intent claims **extend** AGP-1 ACTION_PROPOSE with an explicit intent dimension. In an AIAM-1-governed deployment, an ACTION_PROPOSE message is accompanied by an intent claim. The governance gateway evaluates both: the action parameters against capability grants, and the intent claim against IBAC authority policies.

AGP-1 deployments that do not adopt AIAM-1 continue to function without intent claims. IBAC authority evaluation is not available in this configuration; authorization falls back to capability-based and role-based evaluation.

---

## 3. Normative Requirements

### 3.1 Intent Claim Structure

**AIAM1-INT-001.** Every action taken by a conformant AI agent MUST carry an intent claim. Actions without a valid intent claim MUST be treated as unauthorized by default.

**AIAM1-INT-002.** An intent claim MUST be a structured assertion containing, at minimum, the following fields:

| Field | Description | Required |
|---|---|---|
| `intent_id` | Unique identifier for this intent claim | MUST |
| `goal_ref` | Reference to the goal context in the agent's identity claim (`goal_id`) | MUST |
| `action_ref` | Reference to the action proposal this intent claim accompanies | MUST |
| `reasoning_summary` | Structured summary of the reasoning chain that produced the decision to act | MUST |
| `expected_outcome` | Structured description of the expected result of the action | MUST |
| `dependency_refs` | References to prior actions this action builds upon (empty if none) | MUST |
| `timestamp` | Time at which the intent claim was produced | MUST |
| `action_proposal_timestamp` | Timestamp of the action proposal this intent accompanies, for runtime tolerance checking (INT-003) | MUST |
| `confidence` | Agent's self-assessed confidence in the action's alignment with the goal [0.0–1.0] | SHOULD |

**AIAM1-INT-003.** Intent claims MUST be produced by the agent at the moment of action, not synthesized after the fact. The `timestamp` field MUST reflect the time of production, and conformant implementations MUST reject intent claims whose timestamps diverge from the action proposal timestamp by more than a configured tolerance window.

**AIAM1-INT-004.** The `reasoning_summary` field MUST be a structured object, not free text. At minimum, it MUST include:

| Subfield | Description | Required |
|---|---|---|
| `trigger` | What event or condition prompted the agent to consider this action | MUST |
| `alternatives_considered` | Other actions the agent evaluated before selecting this one | SHOULD |
| `selection_rationale` | Why this action was selected over alternatives | MUST |

### 3.2 Intent-Goal Alignment

**AIAM1-INT-010.** A conformant implementation MUST validate intent claims against the goal context declared in the agent's identity claim. Validation MUST verify that:

1. The `goal_ref` in the intent claim matches an active goal context in the agent's identity claim.
2. The `expected_outcome` is consistent with the `scope` defined in the goal context.
3. The action proposed does not violate any `constraints` declared in the goal context.

**AIAM1-INT-011.** An intent claim whose `goal_ref` does not match any active goal context MUST result in the action being denied.

**AIAM1-INT-012.** An intent claim whose `expected_outcome` is inconsistent with the goal context scope SHOULD result in escalation for human review. Inconsistency detection is implementation-defined but MUST be documented.

### 3.3 Intent Claim Preservation

**AIAM1-INT-020.** Intent claims MUST be preserved as part of the attestation record for every action (see [ATTESTATION](/identity/attestation/)).

**AIAM1-INT-021.** Intent claims MUST NOT be modifiable after production. Once an intent claim is submitted with an action proposal, it is immutable. Any correction requires a new action proposal with a new intent claim.

**AIAM1-INT-022.** Intent claims MUST be retained for at least the duration of the attestation record retention period defined by the implementation.

### 3.4 Intent Claims in Delegation Chains

**AIAM1-INT-030.** When an agent delegates an action to a sub-agent, the sub-agent MUST produce its own intent claim for the delegated action. The sub-agent's intent claim MUST reference the parent agent's intent claim via the `dependency_refs` field.

**AIAM1-INT-031.** A sub-agent's intent claim MUST be independently valid — it MUST pass goal-context alignment validation against the sub-agent's own identity claim. A sub-agent MUST NOT inherit intent validation from its parent.

---

## 4. Worked Example

### Scenario

The Acme SOC triage agent (identity claim from [IDENTITY §6](/identity/identity/#6-worked-example-single-principal-single-agent)) detects an anomalous spike in DNS queries from a specific host. It decides to query the SIEM for related network telemetry.

### Intent Claim

```json
{
  "intent_id": "int-acme-soc-20260410-001",
  "goal_ref": "gc-soc-triage-2026Q2",
  "action_ref": "a-acme-soc-20260410-telemetry-query",
  "reasoning_summary": {
    "trigger": "Anomalous DNS query volume detected: host 10.0.5.42 exceeded 3-sigma threshold (2,847 queries in 5 minutes vs. baseline 120)",
    "alternatives_considered": [
      "Escalate directly to human analyst without additional context",
      "Query endpoint detection and response (EDR) logs for host 10.0.5.42",
      "Query SIEM for correlated network telemetry across segment 10.0.0.0/8"
    ],
    "selection_rationale": "SIEM query provides broadest context for triage without requiring elevated EDR access. Direct escalation without context would increase analyst workload."
  },
  "expected_outcome": "Retrieve network flow records for host 10.0.5.42 and correlated hosts in segment 10.0.0.0/8 for the preceding 24 hours. No data modification. Results used to inform escalation decision.",
  "dependency_refs": [],
  "timestamp": "2026-04-10T14:32:07Z",
  "confidence": 0.87
}
```

### IBAC Evaluation

The governance gateway evaluates this intent claim against the IBAC authority policy:

1. **Identity**: `agent:soc-01` → resolves to Acme SOC triage agent identity claim.
2. **Action**: `telemetry.query` on target `siem:network-flows` with parameters scoped to `10.0.0.0/8`.
3. **Intent**: Goal ref matches active goal context `gc-soc-triage-2026Q2`. Expected outcome ("retrieve network flow records, no data modification") is consistent with goal scope ("telemetry query, alert correlation"). No constraint violations.

**Decision**: ALLOW. The (identity, action, intent) triple matches an authorizing IBAC policy.

If the same agent submitted an intent claim with `expected_outcome: "Delete DNS cache on host 10.0.5.42 to force re-resolution"`, the intent-goal alignment check would detect a constraint violation (goal context declares "read-only data access; no remediation actions") and the action would be DENIED.

---

## 5. Intent Spoofing Detection

### 5.0 Value Proposition

IBAC does not prevent malicious intent. It raises the cost of crafting viable spoofed claims, makes attempts visible in attestation records, and enables forensic reconstruction after the fact. An attacker who must produce a structured intent claim that passes goal-context alignment, action-intent coherence, and behavioral consistency checks has a materially harder task than one who simply injects a prompt into an ungoverned agent. But the barrier is economic and forensic, not absolute. Implementations should not describe IBAC as preventive — it is detective and cost-raising, with prevention as a byproduct of the cost barrier in most practical scenarios.

### 5.1 The Problem

A compromised or manipulated agent may produce an intent claim that does not correspond to its actual reasoning. For example, an agent subjected to prompt injection may submit a data exfiltration action with an intent claim that reads "routine telemetry query for SOC triage." The intent claim looks valid; the action is malicious.

### 5.2 Detection Mechanisms

AIAM-1 does not claim to solve intent spoofing completely — this is an open research problem (see Open Questions §7.1). However, conformant implementations SHOULD employ the following detection mechanisms:

**AIAM1-INT-040.** A conformant implementation SHOULD detect intent spoofing through at least one of the following mechanisms:

1. **Behavioral consistency analysis.** Compare the current intent claim against the agent's historical pattern of intent claims. An agent that has submitted 500 "telemetry query" intents and suddenly submits "configuration modification" is statistically anomalous.

2. **Action-intent coherence.** Verify that the action parameters are consistent with the declared intent. An intent claim that says "read-only query" accompanying an action that writes data is incoherent.

3. **Outcome verification.** After action execution, compare the actual outcome against the `expected_outcome` declared in the intent claim. Persistent divergence between declared and actual outcomes is evidence of spoofing or miscalibration.

4. **Confidence calibration.** Track the correlation between the agent's `confidence` scores and actual outcomes. An agent whose high-confidence actions frequently fail or produce unexpected outcomes may be miscalibrated or compromised.

**AIAM1-INT-041.** When intent spoofing is detected or suspected, the implementation MUST produce an attestation record flagging the detection and SHOULD escalate subsequent actions from the affected agent for human review.

---

## 6. Security Considerations

### 6.1 Intent Claims Are Assertions, Not Proofs

Intent claims are self-reported by the agent. They provide a governance surface for evaluation, not a proof of honest intent. The security model treats intent claims as untrusted input that is validated against external constraints (goal context, behavioral history, action parameters) rather than trusted at face value.

### 6.2 Replay and Reuse

**AIAM1-INT-050.** Intent claims are bound to specific action proposals via `action_ref` and `timestamp`. An intent claim MUST NOT be reusable across multiple action proposals. Conformant implementations MUST reject intent claims whose `action_ref` has already been used.

### 6.3 Reasoning Summary Sensitivity

The `reasoning_summary` field may contain information about the agent's internal state, decision process, or environmental observations. Implementations SHOULD consider whether reasoning summaries contain sensitive information and apply appropriate access controls to attestation records containing them.

---

## 7. Open Questions

1. **Intent claim verifiability.** The fundamental open question: how can a relying party verify that an intent claim corresponds to the agent's actual reasoning? Current LLMs do not provide provable execution traces. Chain-of-thought outputs can be manipulated. Hardware-level attestation of model execution is not yet feasible. This remains the most significant theoretical limitation of intent-based governance.

2. **Reasoning summary depth.** How detailed should the `reasoning_summary` be? Too shallow and it provides no governance value. Too deep and it leaks sensitive reasoning, increases message size, and creates a surface for information extraction attacks. A formal guidance on depth is deferred to v0.2.

3. **Multi-step intent.** Some agent actions are part of a multi-step plan. Should intent claims cover the immediate action only, or the entire plan? The current specification requires per-action intent claims with `dependency_refs` linking them. Whether a "plan-level intent claim" is also needed is deferred to v0.2.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

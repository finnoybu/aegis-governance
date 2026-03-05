## Protocol Overview

The AEGIS Governance Protocol (AGP) defines how AI systems submit action requests to the governance runtime and receive decisions.

AGP messages are structured JSON objects transmitted over HTTP or equivalent RPC mechanisms.

The protocol ensures that all operational actions are evaluated by the governance runtime prior to execution.

---

## Message Types

AGP defines four core message types.

| Message            | Description                              |
| ------------------ | ---------------------------------------- |
| ACTION_PROPOSE     | AI system proposes an operational action |
| DECISION_RESPONSE  | Governance runtime returns decision      |
| EXECUTION_RESULT   | Outcome of an approved operation         |
| ESCALATION_REQUEST | Human review required                    |

---

## ACTION_PROPOSE Message

This message represents an action request submitted by an AI system.

```json
{
  "action_id": "a-123",
  "actor": "agent:soc-01",
  "capability": "telemetry.query",
  "resource": "auth_logs",
  "parameters": {
    "query": "failed_login > 10"
  },
  "context": {
    "environment": "production"
  }
}
```

---

## DECISION_RESPONSE Message

Returned by the governance runtime after evaluating the request.

```json
{
  "action_id": "a-123",
  "decision": "ALLOW",
  "risk_score": 2.4,
  "policy_version": "2026.03.05"
}
```

Possible decision values:

```
ALLOW
DENY
ESCALATE
REQUIRE_CONFIRMATION
```

---

## Execution Flow

Typical message exchange:

```
AI Agent
   │
   ▼
ACTION_PROPOSE
   │
   ▼
Governance Runtime
   │
   ▼
DECISION_RESPONSE
   │
   ▼
Tool Proxy executes action
   │
   ▼
EXECUTION_RESULT
```

---

## Error Handling

Example error response:

```json
{
  "error": "capability_not_defined",
  "message": "Requested capability is not registered."
}
```

---

## Security Considerations

AGP implementations must ensure:

* authenticated actor identity
* tamper-resistant message transport
* schema validation
* audit logging of all protocol interactions

````

---

# 2. Add Governance Event Examples (RFC-0004)

Add a section like this to `RFC-0004_Governance_Event_Model.md`.

:::writing{variant="standard" id="event_examples"}
## Example Governance Events

### Circumvention Report

```json
{
  "event_id": "evt-20260305-01",
  "event_type": "circumvention_report",
  "publisher_did": "did:aegis:enterprise-01",
  "timestamp": "2026-03-05T20:10:00Z",
  "payload": {
    "technique_id": "PRMPT-CHAIN-042",
    "category": "prompt-injection",
    "severity": "high",
    "affected_models": ["gpt", "claude"],
    "description": "Prompt chain bypassing guardrails"
  }
}
````

---

### Governance Attestation

```json
{
  "event_type": "governance_attestation",
  "payload": {
    "aegis_version": "1.0",
    "risk_model": "RISK-CORE-7",
    "compliance_profile": "NIST-AI-RMF"
  }
}
```

---

### Risk Signal

```json
{
  "event_type": "risk_signal",
  "payload": {
    "risk_category": "model_manipulation",
    "severity": "warning",
    "trend": "rising"
  }
}
```

# AGP-1 Message Schemas & Field Specifications

**Document**: AEGIS_AGP1_MESSAGES.md  
**Version**: 1.0 (Normative)  
**Part of**: AEGIS Governance Protocol  
**Last Updated**: March 5, 2026

---

## Overview

This document provides complete, normative schemas for all 6 AGP-1 message types. All required fields MUST be present and validated; optional fields MAY be omitted.

---

## 1. ACTION_PROPOSE Message

**Direction**: Client → Server  
**Purpose**: Client proposes an operational action for governance evaluation  
**Response**: [DECISION_RESPONSE](#2-decision_response-message)

### Schema

```json
{
  "agp_version": "1.0.0",
  "message_type": "ACTION_PROPOSE",
  "message_id": "msg-20260305-abc123def456",
  "request_id": "req-soc-001-12345",
  "timestamp": "2026-03-05T14:30:00Z",
  "actor_id": "agent:soc-001",
  "actor_type": "ai_system",
  "authentication": {
    "method": "bearer_token",
    "credentials": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "capability": "telemetry.query",
  "action_type": "tool_call",
  "target": "siem.search",
  "parameters": {
    "query": "source_ip=192.168.1.100 AND event_type=failed_login",
    "time_window_minutes": 15,
    "max_results": 1000
  },
  "context": {
    "session_id": "sess-abc-def-ghi",
    "environment": "production",
    "trace_id": "trace-20260305-001",
    "source_system": "security-orchestrator",
    "priority": "high",
    "reason": "incident_response"
  },
  "constraints": {
    "max_cpu_seconds": 30,
    "require_encryption": true,
    "require_confidential_handling": true
  }
}
```

### Field Specification

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `agp_version` | string | yes | Protocol version (SemVer format) | Must match negotiated version; format: `^\d+\.\d+\.\d+$` |
| `message_type` | enum | yes | Message type identifier | Must be: `ACTION_PROPOSE` |
| `message_id` | uuid | yes | Unique message identifier (for idempotency) | Format: UUID v4; prevents replay attacks |
| `request_id` | string | yes | Business/correlation ID for tracing | Length: 1-256 chars; links to audit trail |
| `timestamp` | RFC3339 | yes | ISO 8601 UTC timestamp | Must be within ±5 minutes of server time (clock skew tolerance) |
| `actor_id` | string | yes | Authenticated actor identifier | Must match authentication token subject |
| `actor_type` | enum | yes | Type of actor | Must be: `ai_system`, `human_user`, `automated_system` |
| `authentication.method` | enum | yes | Authentication mechanism | Must be: `bearer_token`, `mtls`, `api_key` |
| `authentication.credentials` | string | yes | Credentials (format varies by method) | For bearer_token: JWT; for mtls: in TLS layer; for api_key: base64 |
| `capability` | string | yes | Capability being requested | Must be registered in Capability Registry; cannot be empty |
| `action_type` | enum | yes | Category of action | Must be: `tool_call`, `file_operation`, `network_access`, `data_access`, `system_action` |
| `target` | string | yes | Fully-qualified resource identifier | Format: depends on action_type; examples: `siem.search`, `s3://bucket/path` |
| `parameters` | object | yes | Action-specific parameter object | Schema depends on target system; validated by Tool Proxy |
| `context` | object | yes | Contextual metadata for decision-making | Must include at least 3 fields from: session_id, environment, trace_id, source_system, priority, reason |
| `constraints` | object | no | Additional operational constraints | Optional; applies upper bounds on execution parameters |

### Parameter Validation

**capability**: MUST be registered in Capability Registry

```json
{
  "capability_id": "telemetry.query",
  "version": "1.0.0",
  "registered": true,
  "requires_mfa": false,
  "category": "data_access"
}
```

**actor_id**: MUST match authentication token subject

```javascript
// JWT claim:
{ "sub": "agent:soc-001", ... }
// Must match:
{ "actor_id": "agent:soc-001" }
```

**timestamp**: MUST be within clock skew tolerance

```javascript
// Server time: 2026-03-05T14:30:05Z
// Request timestamp: 2026-03-05T14:35:00Z (5 min future)  → ACCEPT
// Request timestamp: 2026-02-28T14:30:00Z (1 week old)   → REJECT
```

### Examples

**Example 1: Simple SIEM Query**

```json
{
  "agp_version": "1.0.0",
  "message_type": "ACTION_PROPOSE",
  "message_id": "msg-20260305-001",
  "request_id": "inc-2026-0305-001",
  "timestamp": "2026-03-05T14:30:00Z",
  "actor_id": "agent:soc-001",
  "actor_type": "ai_system",
  "authentication": {
    "method": "bearer_token",
    "credentials": "Bearer eyJ..."
  },
  "capability": "telemetry.query",
  "action_type": "tool_call",
  "target": "siem.search",
  "parameters": {
    "query": "status=error",
    "time_window_minutes": 60,
    "limit": 100
  },
  "context": {
    "session_id": "sess-001",
    "environment": "production",
    "source_system": "soar-platform"
  }
}
```

**Example 2: High-Risk Infrastructure Change**

```json
{
  "agp_version": "1.0.0",
  "message_type": "ACTION_PROPOSE",
  "message_id": "msg-20260305-002",
  "request_id": "deploy-k8s-prod",
  "timestamp": "2026-03-05T15:00:00Z",
  "actor_id": "user:alice@company.com",
  "actor_type": "human_user",
  "authentication": {
    "method": "mtls",
    "credentials": null
  },
  "capability": "infrastructure.deploy",
  "action_type": "system_action",
  "target": "kubernetes-prod-cluster",
  "parameters": {
    "namespace": "default",
    "image_uri": "gcr.io/myproject/app:v1.2.3",
    "replicas": 5,
    "strategy": "rolling"
  },
  "context": {
    "session_id": "sess-alice-001",
    "environment": "production",
    "trace_id": "trace-deploy-123",
    "reason": "security_patch_deployment"
  },
  "constraints": {
    "timeout_seconds": 300,
    "max_concurrent_updates": 2
  }
}
```

---

## 2. DECISION_RESPONSE Message

**Direction**: Server → Client  
**Purpose**: Server returns governance decision for proposed action  
**Request**: [ACTION_PROPOSE](#1-action_propose-message)

### Schema

```json
{
  "agp_version": "1.0.0",
  "message_type": "DECISION_RESPONSE",
  "message_id": "msg-20260305-def456",
  "request_id": "req-soc-001-12345",
  "timestamp": "2026-03-05T14:30:01Z",
  "decision": "ALLOW",
  "decision_reason": "matches policy 'telemetry_query_soc_allowed'",
  "policy_set_version": "2026.03.05",
  "audit_event_id": "audit-evt-789xyz",
  "risk_score": 2.4,
  "risk_category": "data_access",
  "decision_confidence": 0.99,
  "applied_constraints": {
    "max_results": 1000,
    "timeout_seconds": 30,
    "encryption_required": true,
    "audit_logging": "enhanced"
  },
  "policy_trace": {
    "evaluated_policies": ["deny_untrusted_actors", "telemetry_query_soc_allowed"],
    "matching_policy_id": "telemetry_query_soc_allowed",
    "evaluation_duration_ms": 12,
    "risk_score_breakdown": {
      "historical_attempt_rate": 1.0,
      "actor_trust_score": 0.5,
      "capability_sensitivity": 2.0,
      "behavioral_anomaly": 0.0,
      "federation_signals": 0.0
    }
  }
}
```

### Field Specification

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `decision` | enum | yes | ALLOW, DENY, ESCALATE, REQUIRE_CONFIRMATION |
| `decision_reason` | string | yes | Human-readable explanation (for logs, UI, audit) |
| `policy_set_version` | string | yes | Version of policy set used for evaluation (SemVer) |
| `audit_event_id` | string | yes | Immutable audit log entry ID (for tracing) |
| `risk_score` | float [0.0-10.0] | yes | Overall risk score; higher = riskier |
| `risk_category` | enum | yes | Category: `data_access`, `system_control`, `capability_elevation`, `behavioral_anomaly` |
| `decision_confidence` | float [0.0-1.0] | yes | Confidence in decision determinism |
| `applied_constraints` | object | conditional | Required if decision == ALLOW; constraints client must enforce |
| `policy_trace` | object | yes | Audit trail showing decision computation |

### Decision Outcomes

#### ALLOW

Action is permitted. Client MAY proceed to execution.

- Constraints MUST be enforced during execution
- Client MUST send EXECUTION_REPORT after completion
- No human intervention required (unless constraints exceed authorization)

#### DENY

Action is explicitly forbidden. Client MUST NOT proceed to execution.

- No constraints provided (not applicable)
- Client SHOULD NOT escalate or retry
- Client SHOULD log reason and possibly alert operator
- No EXECUTION_REPORT needed

#### ESCALATE

Action requires human review before execution.

- See [ESCALATION_REQUEST](#4-escalation_request-message) for details
- Client MUST pause and display evidence to operator
- Client waits for ESCALATION_RESPONSE (from operator)
- After approval, client sends new ACTION_PROPOSE (confirms human consent)

#### REQUIRE_CONFIRMATION

Action permitted only with explicit user confirmation.

- Client MUST re-submit ACTION_PROPOSE with `confirmation_token` field
- Used for novel or repetitive high-risk actions
- Similar to ESCALATE but confirms user intent without full review

### Examples

**ALLOW Decision (Low Risk)**

```json
{
  "agp_version": "1.0.0",
  "message_type": "DECISION_RESPONSE",
  "decision": "ALLOW",
  "risk_score": 1.5,
  "decision_confidence": 0.99,
  "applied_constraints": {
    "max_results": 1000,
    "timeout_seconds": 30
  }
}
```

**DENY Decision (Unauthorized)**

```json
{
  "agp_version": "1.0.0",
  "message_type": "DECISION_RESPONSE",
  "decision": "DENY",
  "decision_reason": "actor not granted 'infrastructure.deploy' capability",
  "risk_score": 0.0,
  "decision_confidence": 1.0
}
```

**ESCALATE Decision (High Risk)**

```json
{
  "agp_version": "1.0.0",
  "message_type": "DECISION_RESPONSE",
  "decision": "ESCALATE",
  "decision_reason": "production deployment exceeds risk threshold (6.5/10.0)",
  "risk_score": 6.5,
  "decision_confidence": 0.75,
  "risk_score_breakdown": {
    "historical_attempt_rate": 2.0,
    "capability_sensitivity": 8.0
  }
}
```

---

## 3. EXECUTION_REPORT Message

**Direction**: Client → Server  
**Purpose**: Report execution outcome of approved action  
**Request**: [ACTION_PROPOSE](#1-action_propose-message)

### Schema

```json
{
  "agp_version": "1.0.0",
  "message_type": "EXECUTION_REPORT",
  "message_id": "msg-20260305-ghi789",
  "request_id": "req-soc-001-12345",
  "audit_event_id": "audit-evt-789xyz",
  "timestamp": "2026-03-05T14:30:15Z",
  "actor_id": "agent:soc-001",
  "execution_status": "completed",
  "exit_code": 0,
  "output_summary": "returned 234 matching events",
  "duration_ms": 8450,
  "errors": null,
  "resource_utilization": {
    "cpu_seconds": 2.3,
    "memory_mb": 128,
    "network_bytes_sent": 54000,
    "cost_usd": 0.15
  }
}
```

### Field Specification

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `execution_status` | enum | yes | COMPLETED, FAILED, TIMEOUT, PERMISSION_DENIED, ABORTED_BY_USER |
| `exit_code` | integer | no | Return code from tool (0 = success, nonzero = failure) |
| `output_summary` | string | yes | Brief summary of execution outcome (1-500 chars) |
| `duration_ms` | integer | yes | Wall-clock execution time in milliseconds |
| `errors` | string | no | Error message if status is FAILED or PERMISSION_DENIED |
| `resource_utilization` | object | no | Telemetry for cost/performance tracking |

### Status Codes

| Status | HTTP Equivalent | Meaning | Action |
|--------|-----------------|---------|--------|
| `completed` | 200 | Action succeeded normally | Audit success, return results to user |
| `failed` | 500 | Action raised error in tool | Audit failure, return error message |
| `timeout` | 504 | Action exceeded time limit | Audit timeout, escalate if critical |
| `permission_denied` | 403 | Tool rejected request (permissions) | Audit denial, investigate permissions |
| `aborted_by_user` | 400 | User cancelled operation | Audit cancellation, no error |

### Examples

**Successful Completion**

```json
{
  "message_id": "msg-001",
  "request_id": "req-soc-001-12345",
  "execution_status": "completed",
  "exit_code": 0,
  "output_summary": "SIEM query returned 234 events",
  "duration_ms": 2500,
  "resource_utilization": {
    "cpu_seconds": 1.2,
    "memory_mb": 64
  }
}
```

**Timeout**

```json
{
  "message_id": "msg-002",
  "execution_status": "timeout",
  "output_summary": "query exceeded 30 second timeout limit",
  "duration_ms": 30001,
  "errors": "Query processing incomplete"
}
```

---

## 4. ESCALATION_REQUEST Message

**Direction**: Server → Client  
**Purpose**: Server requests human review for high-risk or uncertain action  
**Response**: ESCALATION_RESPONSE (operator approval/denial)

### Schema

```json
{
  "agp_version": "1.0.0",
  "message_type": "ESCALATION_REQUEST",
  "message_id": "msg-20260305-jkl012",
  "request_id": "req-soc-001-99999",
  "timestamp": "2026-03-05T14:35:00Z",
  "escalation_id": "esc-abc-def-ghi",
  "reason": "high_risk_score",
  "severity": "high",
  "action_summary": {
    "capability": "infrastructure.deploy",
    "target": "prod-kubernetes-cluster",
    "context": "deploying security patch to production"
  },
  "evidence": {
    "risk_score": 7.2,
    "risk_factors": {
      "capability_sensitivity": 9.0,
      "environment_production": true,
      "actor_trust_score": 0.85
    },
    "policies_evaluated": ["require_escalation_prod_deploy"],
    "federation_incidents_count": 2
  },
  "required_actions": [
    "verify_actor_identity",
    "confirm_business_justification",
    "approve_execution"
  ],
  "expire_at": "2026-03-05T15:35:00Z",
  "evidence_url": "https://governance.example.com/escalations/esc-abc-def-ghi"
}
```

### Field Specification

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `escalation_id` | uuid | yes | Unique escalation request ID |
| `reason` | enum | yes | WHY escalation requested: `high_risk_score`, `policy_exception`, `capability_not_found`, `insufficient_trust_score`, `federation_signals_conflicting` |
| `severity` | enum | yes | CRITICAL, HIGH, MEDIUM, LOW |
| `action_summary` | object | yes | Brief description of action (capability, target, context) |
| `evidence` | object | yes | Supporting evidence for escalation (risk scores, policies, signals) |
| `required_actions` | array | yes | What operator must do before approval |
| `expire_at` | RFC3339 | yes | When escalation request expires (typically +1 hour) |
| `evidence_url` | string | no | Deep link to full evidence for operator review |

### Examples

**High Risk Score Escalation**

```json
{
  "escalation_id": "esc-prod-deploy-001",
  "reason": "high_risk_score",
  "severity": "high",
  "risk_score": 7.5,
  "action_summary": {
    "capability": "infrastructure.deploy",
    "target": "prod-cluster"
  },
  "required_actions": [
    "confirm_business_justification",
    "approve_execution"
  ]
}
```

**Policy Exception Escalation**

```json
{
  "escalation_id": "esc-policy-exc-001",
  "reason": "policy_exception",
  "severity": "medium",
  "action_summary": {
    "capability": "data.export_unencrypted"
  },
  "evidence": {
    "policy_violation": "encryption_required_policy"
  },
  "required_actions": [
    "provide_exception_justification",
    "get_manager_approval",
    "approve_execution"
  ]
}
```

---

## 5. AUDIT_QUERY Message

**Direction**: Client → Server  
**Purpose**: Query audit trail for compliance forensics  
**Response**: AUDIT_RESPONSE (array of audit events)

### Schema

```json
{
  "agp_version": "1.0.0",
  "message_type": "AUDIT_QUERY",
  "message_id": "msg-20260305-mno345",
  "timestamp": "2026-03-05T16:00:00Z",
  "actor_id": "analyst:compliance-001",
  "authentication": {
    "method": "bearer_token",
    "credentials": "Bearer eyJ..."
  },
  "query_type": "by_request_id",
  "filters": {
    "request_id": "req-soc-001-12345"
  },
  "limit": 100,
  "offset": 0
}
```

### Query Types

| Type | Filters | Use Case |
|------|---------|----------|
| `by_request_id` | request_id | Retrieve all events for single request |
| `by_actor_id` | actor_id, time_window | Auditing specific actor's actions |
| `by_capability` | capability, time_window | Finding all uses of capability |
| `by_decision` | decision (ALLOW/DENY/etc), time_window | Finding policy violations |
| `by_risk_score` | min_score, max_score, time_window | Finding high-risk decisions |
| `by_time_range` | start_time, end_time | Specific time window audit |

### Examples

**Query: Find all decisions for specific request**

```json
{
  "query_type": "by_request_id",
  "filters": {"request_id": "req-soc-001-12345"}
}
```

**Query: Find all DENY decisions in last 7 days**

```json
{
  "query_type": "by_decision",
  "filters": {
    "decision": "DENY",
    "start_time": "2026-02-26T00:00:00Z",
    "end_time": "2026-03-05T23:59:59Z"
  },
  "limit": 1000
}
```

---

## 6. HEALTH_CHECK Message

**Direction**: Either → Either  
**Purpose**: Test protocol health and version support  
**Response**: HEALTH_CHECK_RESPONSE

### Schema

```json
{
  "agp_version": "1.0.0",
  "message_type": "HEALTH_CHECK",
  "message_id": "msg-20260305-pqr678",
  "timestamp": "2026-03-05T16:05:00Z",
  "initiator": "client",
  "versions_supported": ["1.0.0", "1.1.0"],
  "client_info": {
    "name": "aegis-client/1.0.0",
    "capabilities": ["bearer_token", "mtls"]
  }
}
```

### Response

```json
{
  "agp_version": "1.0.0",
  "message_type": "HEALTH_CHECK_RESPONSE",
  "message_id": "msg-20260305-stu901",
  "timestamp": "2026-03-05T16:05:01Z",
  "status": "healthy",
  "negotiated_version": "1.0.0",
  "server_info": {
    "name": "aegis-runtime/1.0.0",
    "uptime_seconds": 864000
  },
  "subsystem_status": {
    "policy_engine": "operational",
    "risk_evaluator": "operational",
    "audit_store": "operational",
    "capability_registry": "operational"
  },
  "policy_set_version": "2026.03.05"
}
```

---

## Validation Rules (All Messages)

### Schema Validation

- ✅ All required fields present
- ✅ Field types match schema
- ✅ Enums are from allowed set  
- ✅ Arrays/objects are well-formed JSON
- ✅ Strings are valid UTF-8

### Semantic Validation

- ✅ `actor_id` matches authentication token subject
- ✅ `message_id` is UUID v4 or UUIDv5
- ✅ `timestamp` is within clock skew (+/- 5 minutes)
- ✅ `request_id` is non-empty and ≤ 256 chars
- ✅ `capability` is registered in Capability Registry

### Security Validation

- ✅ Authentication credentials present and valid
- ✅ Actor has appropriate authorization scope
- ✅ Message signature valid (if present)
- ✅ Timestamp prevents replay attacks

---

## Next Steps

- [AEGIS_AGP1_WIRE_FORMAT.md](./AEGIS_AGP1_WIRE_FORMAT.md) - HTTP/2 endpoints, serialization, encoding
- [AEGIS_AGP1_AUTHENTICATION.md](./AEGIS_AGP1_AUTHENTICATION.md) - How to authenticate with bearer tokens and mTLS

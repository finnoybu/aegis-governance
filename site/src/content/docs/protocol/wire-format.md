---
title: "AEGIS AGP-1 Wire Format & Transport Specification"
description: "AGP-1 wire format — serialization and transport encoding"
---

# AEGIS AGP-1 Wire Format & Transport Specification

**Document**: AGP-1/Wire (AEGIS_AGP1_WIRE_FORMAT.md)\
**Version**: 1.0 (Normative)\
**Part of**: AEGIS Governance Protocol\
**Last Updated**: March 6, 2026

---

## HTTP/1.1 & HTTP/2 Specification

### Endpoints

```
Base URL: https://governance.example.com/aegis/v1
Protocol: HTTP/1.1 minimum, HTTP/2 recommended
TLS Version: 1.3 required (1.2 deprecated)
```

### API Endpoints

| Method | Path | Message Type | Response |
|--------|------|--------------|----------|
| `POST` | `/governance/propose` | ACTION_PROPOSE | DECISION_RESPONSE or ESCALATION_REQUEST |
| `POST` | `/governance/report` | EXECUTION_REPORT | ACK |
| `POST` | `/governance/escalation/respond` | ESCALATION_RESPONSE | ACK |
| `POST` | `/governance/audit/query` | AUDIT_QUERY | AUDIT_RESPONSE |
| `GET` | `/governance/health` | HEALTH_CHECK | HEALTH_CHECK_RESPONSE |

### Required Headers

```
Content-Type: application/json; charset=utf-8
Authorization: Bearer <jwt-token> | X-Client-Cert: <fingerprint>
X-Trace-ID: <trace-uuid>
X-Request-ID: <request-uuid>
User-Agent: <client-identifier>
```

### Header Details

| Header | Required | Description | Example |
|--------|----------|-------------|---------|
| `Content-Type` | yes | Message format; must be JSON | `application/json; charset=utf-8` |
| `Authorization` | yes | Bearer token for authentication | `Bearer eyJhbGciOiJIUzI1NiI...` |
| `X-Trace-ID` | yes | Trace ID for distributed tracing | `trace-20260305-abc123` |
| `X-Request-ID` | yes | Unique request identifier | `req-soc-001-12345` |
| `X-Idempotency-Key` | no | Idempotent request key (for retries) | `ik-12345-abc` |
| `X-Priority` | no | Request priority: `critical`, `high`, `normal`, `low` | `high` |
| `User-Agent` | no | Client identifier | `aegis-client/1.0.0` |

### Request/Response Patterns

**Synchronous (default)**:

```
Client sends ACTION_PROPOSE
  ↓ (waits)
Server responds with DECISION_RESPONSE or ESCALATION_REQUEST
  ↓
Client takes action
```

Timeout: 30 seconds (configurable per deployment)

**Asynchronous (for long-running)**:

```
Client sends ACTION_PROPOSE
Server responds: 202 Accepted with decision_url
Client polls https://governance.../decisions/{message_id}
```

---

## JSON Schema

### Request Envelope

```json
{
  "envelope_version": "1.0",
  "message": {
    "agp_version": "1.0.0",
    "message_type": "ACTION_PROPOSE",
    ...
  },
  "signature": {
    "algorithm": "hmac-sha256",
    "key_id": "key-1",
    "signature": "base64url(...)"
  }
}
```

**Note**: Signature is OPTIONAL when message is transmitted over authenticated TLS channel (mutual TLS).

### Response Envelope

```json
{
  "envelope_version": "1.0",
  "timestamp": "2026-03-05T14:30:01Z",
  "server_version": "aegis-runtime/1.0.0",
  "message": {
    "agp_version": "1.0.0",
    "message_type": "DECISION_RESPONSE",
    ...
  }
}
```

---

## Protocol Buffers (Optional High-Throughput Format)

For deployments requiring higher throughput, Protocol Buffers v3 is supported.

```proto
syntax = "proto3";
package aegis.governance.v1;

message ActionPropose {
  string agp_version = 1;
  string message_type = 2;
  string message_id = 3;
  string request_id = 4;
  string timestamp = 5;
  string actor_id = 6;
  string actor_type = 7;
  string capability = 8;
  string action_type = 9;
  string target = 10;
  google.protobuf.Struct parameters = 11;
  google.protobuf.Struct context = 12;
  Authentication authentication = 13;
  optional google.protobuf.Struct constraints = 14;
}

message Authentication {
  string method = 1;
  string credentials = 2;
}

message DecisionResponse {
  string agp_version = 1;
  string message_type = 2;
  string message_id = 3;
  string request_id = 4;
  string timestamp = 5;
  string decision = 6;
  string decision_reason = 7;
  float risk_score = 8;
  float decision_confidence = 9;
  string policy_set_version = 10;
  string audit_event_id = 11;
  google.protobuf.Struct applied_constraints = 12;
  PolicyTrace policy_trace = 13;
}

message PolicyTrace {
  repeated string evaluated_policies = 1;
  string matching_policy_id = 2;
  int32 evaluation_duration_ms = 3;
  google.protobuf.Struct risk_score_breakdown = 4;
}
```

### Content Negotiation

```
Accept: application/json, application/protobuf;q=0.8
Content-Type: application/protobuf
```

---

## Content Encoding

### JSON (Default)

```
Content-Type: application/json; charset=utf-8
Content-Length: 1234
```

### GZIP Compression

For payloads > 4KB:

```
Content-Encoding: gzip
Content-Type: application/json; charset=utf-8
```

### Protobuf

For high-throughput deployments:

```
Content-Type: application/protobuf
X-Proto-Version: 3
```

---

## Error Responses

All errors follow standard envelope:

```json
{
  "envelope_version": "1.0",
  "error": {
    "error_code": "INVALID_REQUEST",
    "error_message": "field 'capability' must be non-empty",
    "http_status": 400,
    "request_id": "req-soc-001-12345",
    "timestamp": "2026-03-05T14:30:01Z",
    "retryable": false,
    "details": {
      "field": "capability",
      "constraint": "non-empty string",
      "received": ""
    }
  }
}
```

---

## HTTP Status Codes

| Code | Message | Meaning | Retryable |
|------|---------|---------|-----------|
| 200 | OK | Decision made successfully | - |
| 202 | Accepted | Request queued for async processing | - |
| 400 | Bad Request | Validation error in request | No |
| 401 | Unauthorized | Authentication failed or insufficient scope | No |
| 403 | Forbidden | Actor not authorized for capability | No |
| 404 | Not Found | Capability or resource not found | No |
| 429 | Too Many Requests | Rate limit exceeded | Yes (with backoff) |
| 500 | Internal Server Error | Server error; safe to retry | Yes |
| 503 | Service Unavailable | Server overloaded or audit storage down | Yes |
| 504 | Gateway Timeout | Request processing exceeded timeout | Yes |

---

## Connection Management

### Keep-Alive

```
Connection: keep-alive
Keep-Alive: timeout=60, max=1000
```

### Timeout Handling

```
Request timeout: 30 seconds (configurable)
Connection establishment: 5 seconds
TLS handshake: 5 seconds
```

---

## Security Considerations

### TLS/HTTPS (Mandatory)

```
Minimum: TLS 1.2
Required: TLS 1.3
Cipher suites: TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256
Perfect Forward Secrecy: required
```

### Certificate Validation

For mTLS:

```
Server certificate:
  - Must be valid and not expired
  - CN must match hostname
  - Subject Alternative Name (SAN) must include client hostname
  - Signature must verify against trust root

Client certificate:
  - Must be valid and not expired
  - CN should identify client
  - Extended Key Usage: Client Authentication
```

### Message Signing (Optional)

If transmission is not over authenticated TLS:

```python
signature = HMAC-SHA256(
  key=client_secret,
  message=message_body
)

header("X-Signature") = base64url(signature)
```

---

## Next Steps

- [AEGIS_AGP1_AUTHENTICATION.md](./AEGIS_AGP1_AUTHENTICATION.md) - OAuth, JWT, mTLS details
- [AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md) - Full protocol flows and diagrams

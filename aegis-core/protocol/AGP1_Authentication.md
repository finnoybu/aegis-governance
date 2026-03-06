# AGP-1 Authentication & Authorization

**Document**: AGP1_Authentication.md  
**Version**: 1.0 (Normative)  
**Part of**: AEGIS Governance Protocol  
**Last Updated**: March 5, 2026

---

## Overview

Every AGP-1 message requires authentication proving the client's identity. Three mechanisms are supported, with Bearer tokens being the primary method.

---

## Bearer Token Authentication

**Method**: `bearer_token` (Primary, recommended)  
**Transport**: HTTP Authorization header

### JWT Structure

```json
{
  "alg": "HS256",
  "typ": "JWT",
  "kid": "key-v1"
}
.
{
  "iss": "https://auth.example.com",
  "sub": "agent:soc-001",
  "aud": "https://governance.example.com",
  "iat": 1709624400,
  "exp": 1709628000,
  "scope": "governance:propose_action governance:query_audit",
  "actor_type": "ai_system",
  "trust_level": "L2_TRUSTED"
}
```

### JWT Claims (Normative)

| Claim | Type | Required | Description |
|-------|------|----------|-------------|
| `iss` | string | yes | Issuer; must match configured trust root |
| `sub` | string | yes | Subject (actor_id); must match message actor_id |
| `aud` | string | yes | Audience (server URL) |
| `iat` | integer | yes | Issued-at timestamp (Unix seconds) |
| `exp` | integer | yes | Expiration timestamp (Unix seconds); typically 1-2 hours from iat |
| `scope` | string | yes | Space-separated OAuth scopes (see below) |
| `actor_type` | string | yes | Type of actor: `ai_system`, `human_user`, `automated_system` |
| `trust_level` | string | no | Actor's baseline trust level (from AEGIS_TRUST_MODEL): L0_SYSTEM, L1_PRIMARY, L2_TRUSTED, L3_CONTRIBUTOR, QUARANTINE |

### Authorization Scopes

| Scope | Permission | Notes |
|-------|-----------|-------|
| `governance:propose_action` | Submit ACTION_PROPOSE messages | Required for all governance decisions |
| `governance:query_audit` | Issue AUDIT_QUERY messages | Restricted to compliance/security roles |
| `governance:escalate_decision` | Respond to ESCALATION_REQUEST | Typically human operators only |
| `governance:health_check` | Check protocol health | Low-privilege; usually granted to monitoring |

### JWT Validation

Server MUST validate:

1. **Signature**: JWT signature is valid given issuer's public key
2. **Issued-at**: `iat` timestamp is reasonable (within ±5 minutes of server time)
3. **Expiration**: `exp` timestamp is in future (not expired)
4. **Issuer**: `iss` claim matches trusted issuer
5. **Audience**: `aud` claim matches server URL
6. **Subject**: `sub` claim in JWT matches `actor_id` in message
7. **Scope**: Actor has required scope for requested operation

### Example

**HTTP Request**:
```
POST /aegis/v1/governance/propose HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtleS12MSJ9.eyJpc3MiOiJodHRwczovL2F1dGguZXhhbXBsZS5jb20iLCJzdWIiOiJhZ2VudDpzb2MtMDAxIiwic2NvcGUiOiJnb3Zlcm5hbmNlOnByb3Bvc2VfYWN0aW9uIiwiZXhwIjoxNzA5NjI4MDAwfQ.SIGNATURE
X-Request-ID: req-soc-001-12345

{...message...}
```

---

## Mutual TLS (mTLS)

**Method**: `mtls` (For high-security deployments)  
**Transport**: TLS layer (certificate validation)

### Server Configuration

```yaml
mtls:
  enabled: true
  client_ca_cert: /etc/ssl/certs/client-ca.pem
  verify_mode: VERIFY_PEER_REQUIRE
  require_san: true
```

### Client Certificate Requirements

```
Subject:
  CN = agent-soc-001
  OU = AI-Systems
  O = MyOrg
  C = US

Validity:
  Not before: 2026-01-01
  Not after:  2026-12-31

Extended Key Usage:
  - Client Authentication

Key Usage:
  - Digital Signature
  - Key Encipherment
```

### Server Validation

1. **Certificate is valid**: Not expired, signature chain verifies
2. **Subject Alternative Name (SAN)** includes expected identity (optional but recommended)
3. **CN (Common Name)** maps to known actor_id
4. **Trust anchor**: Issued by CA in client_ca_cert

### Mapping Certificate to Actor

```python
# Extract actor_id from certificate
actor_id = certificate.subject.common_name  # "agent-soc-001"

# Verify against trust database
actor_info = trust_db.get_actor(actor_id)
if actor_info is None:
    raise Unauthorized(f"unknown actor: {actor_id}")

# Grant scopes based on certificate OU and O
scopes = actor_info.default_scopes
```

### Example

**TLS Handshake**:
```
Client presents certificate:
  CN=agent-soc-001, OU=AI-Systems, O=MyOrg

Server validates:
  ✓ Certificate not expired
  ✓ Signature chain valid
  ✓ Common Name maps to known actor

Server grants scopes from database:
  governance:propose_action
  governance:query_audit
```

---

## API Key Authentication  (Deprecated; Sunset: 2026-12-31)

**Method**: `api_key` (Legacy; use Bearer tokens instead)  
**Transport**: Custom headers

### Headers

```
X-API-Key: <base64-encoded-key>
X-Client-ID: agent:soc-001
```

### Key Format

```
Base64(
  client_id:secret_key
)
```

Example plain: `agent:soc-001:mysecretkey123`  
Example encoded: `YWdlbnQ6c29jLTAwMTpteXNlY3JldGtleTEyMw==`

### Security Notes

- ⚠️ Credentials transmitted as HTTP header (only safe over TLS 1.3)
- ⚠️ No expiration (static); high compromise risk
- ⚠️ Requires secure key rotation procedures
- ✅ Simpler than JWT for initial deployments
- ✅ Useful for service-to-service authentication

---

## Request Attribution

Every message MUST include explicit actor identification:

```json
{
  "actor_id": "agent:soc-001",
  "actor_type": "ai_system",
  "authentication": {
    "method": "bearer_token"
  }
}
```

### Actor Types

| Type | Examples | Characteristics |
|------|----------|-----------------|
| `ai_system` | AI agents, copilots, LLMs | Autonomous decision-making; no human in loop for individual actions |
| `human_user` | Security analyst, DevOps engineer | Individual human actor; responsible for actions; can provide context |
| `automated_system` | CI/CD pipelines, scheduled tasks | Non-AI automation; deterministic behavior; typically high-privilege |

### Actor ID Validation

Server MUST verify:

```python
# Rule 1: actor_id in message must match authentication claims
if message.actor_id != auth_token.sub:
    raise AuthorizationError("actor_id mismatch", 
                            message_actor=message.actor_id,
                            token_actor=auth_token.sub)

# Rule 2: actor_id must be registered
actor = actor_registry.lookup(message.actor_id)
if actor is None:
    raise AuthorizationError("unknown actor", actor_id=message.actor_id)

# Rule 3: actor must not be revoked/quarantined
if actor.status in ["QUARANTINE", "REVOKED"]:
    raise AuthorizationError("actor revoked", actor_id=message.actor_id)
```

---

## Scope Validation

For each operation, server verifies required scope:

| Operation | Required Scope | Check |
|-----------|---|---|
| ACTION_PROPOSE | `governance:propose_action` | Must present in JWT `scope` claim |
| EXECUTION_REPORT | `governance:propose_action` | (implicit; proves previous ALLOW) |
| AUDIT_QUERY | `governance:query_audit` | Must present in JWT `scope` claim |
| ESCALATION_RESPONSE | `governance:escalate_decision` | Must present in JWT `scope` claim  |
| HEALTH_CHECK | `governance:health_check` | Optional; no scope required |

### Scope Validation Code

```python
def validate_scope(auth_token, required_scope):
    """Verify actor has required OAuth scope."""
    scopes = auth_token.scope.split(" ")  # space-separated
    
    if required_scope not in scopes:
        raise Unauthorized(
            f"missing required scope: {required_scope}",
            required=required_scope,
            granted=scopes
        )
```

---

## Token Lifecycle

### Issuance

1. Client requests token from OAuth provider
2. Provider validates client identity
3. Provider issues JWT with:
   - Expiration: typically 1-2 hours
   - Scopes: based on client's roles
   - Trust level: based on historical behavior
4. Client receives token and stores securely

### Usage

1. Client includes token in Authorization header
2. Server validates signature and claims
3. Server grants access if all validations pass

### Expiration & Refresh

```
Token issued at: 2026-03-05T14:00:00Z (iat)
Token expires at: 2026-03-05T16:00:00Z (exp)  // 2 hours

When client detects expiration (exp < current_time):
  → Request new token from OAuth provider
  → Retry original request with new token
```

### Revocation

If token must be revoked before expiration (compromise):

1. Add token to revocation list (distributed to servers)
2. Servers check revocation list on validation (with cache TTL)
3. Client re-authenticates to get new token

---

## Best Practices

### For Client Implementations

- ✅ Always use TLS 1.3 for transport
- ✅ Validate server certificate (don't skip hostname checking)
- ✅ Store tokens securely (in-memory or encrypted file; not hardcoded)
- ✅ Implement token refresh before expiration  
- ✅ Handle 401 responses by re-authenticating
- ✅ Never log or expose token values

### For Server Implementations

- ✅ Validate all authentication claims (don't skip checks)
- ✅ Check token expiration on every request
- ✅ Rate-limit failed authentication attempts
- ✅ Maintain audit log of authentication events
- ✅ Rotate signing keys regularly (quarterly minimum)
- ✅ Verify issuer is trusted (don't accept unknown issuers)

---

## Next Steps

- [AGP1_PolicyEvaluation.md](./AGP1_PolicyEvaluation.md) - Capability and policy evaluation
- [AGP1_Flows.md](./AGP1_Flows.md) - Complete protocol flows

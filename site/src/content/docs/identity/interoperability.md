---
title: "AEGIS AIAM-1: Interoperability"
description: "AIAM-1 interoperability — cross-system identity federation"
---

# AEGIS AIAM-1: Interoperability

**Document**: AIAM-1/Interoperability (AEGIS_AIAM1_INTEROPERABILITY.md)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

**AIAM-1 adds to existing IAM; it does not subtract from it.**

This chapter defines how AIAM-1 identity claims, intent claims, and attestation records interoperate with existing identity and access management standards. Organizations deploying AIAM-1 will have OAuth 2.1 authorization servers, OIDC identity providers, SCIM provisioning systems, and SAML federation already in place. AIAM-1 integrates with these systems without requiring them to natively understand AIAM-1 primitives. An AIAM-1 agent authenticates using standard OAuth 2.1 flows. It presents standard JWT tokens to resource servers. It is provisioned through standard SCIM workflows. AIAM-1 adds the composite identity, intent, and IBAC layers on top of these standard mechanisms — it does not replace, modify, or constrain the mechanisms already in place.

---

## 2. OAuth 2.1 Integration

### 2.1 Authentication Flow

**AIAM1-IOP-001.** A conformant implementation MUST support agent authentication against existing identity providers using OAuth 2.1 and OpenID Connect without requiring those identity providers to natively understand AIAM-1 identity claims.

**AIAM1-IOP-002.** The recommended authentication flow for AIAM-1 agents is OAuth 2.1 Client Credentials with JWT bearer tokens, extended as follows:

```
┌──────────┐       ┌──────────────┐       ┌──────────────┐
│ AI Agent │──(1)──│ OAuth 2.1 AS │──(2)──│ AIAM-1       │
│          │       │ (IdP)        │       │ Identity     │
│          │◄─(3)──│              │       │ Registry     │
│          │       └──────────────┘       └──────────────┘
│          │
│          │──(4)── ACTION_PROPOSE + Intent Claim
│          │        + JWT Bearer Token
│          │
│          ├──────► Governance Gateway
│          │        validates JWT (standard OAuth)
│          │        resolves actor.id → AIAM-1 claim
│          │        evaluates IBAC triple
└──────────┘
```

1. Agent requests access token from OAuth 2.1 Authorization Server using client credentials.
2. Authorization Server may optionally query AIAM-1 Identity Registry to enrich token claims.
3. Agent receives JWT access token with standard claims plus optional AIAM-1 references.
4. Agent submits ACTION_PROPOSE with JWT bearer token and AIAM-1 intent claim to governance gateway.

### 2.2 Token Mapping

**AIAM1-IOP-003.** A conformant implementation MUST define a mapping from AIAM-1 identity claims to OAuth 2.1 JWT token claims.

| JWT Claim | AIAM-1 Source | Description |
|---|---|---|
| `sub` | `identity_claim.agent_id` | Agent identifier (maps to AGP-1 `actor.id`) |
| `iss` | Token issuer (OAuth AS) | Standard JWT issuer |
| `aud` | Governance gateway identifier | Standard JWT audience |
| `exp`, `iat`, `nbf` | Token lifecycle | Standard JWT temporal claims |
| `scope` | Derived from capability envelope | OAuth scopes corresponding to AIAM-1 capabilities |
| `actor_type` | `"agent"` | Custom claim identifying actor class |
| `aiam_claim_ref` | `identity_claim.claim_id` | **AIAM-1 extension**: reference to the full composite identity claim |
| `aiam_session_ref` | `session.session_id` | **AIAM-1 extension**: reference to the active session |
| `aiam_principal` | `identity_claim.principal.principal_id` | **AIAM-1 extension**: accountable party identifier |

**AIAM1-IOP-004.** Custom AIAM-1 claims MUST use the `aiam_` prefix to avoid collisions with standard JWT claims or other extensions.

**AIAM1-IOP-005.** Resource servers that do not understand AIAM-1 claims MUST still accept the JWT as a valid OAuth 2.1 bearer token. The AIAM-1 extension claims are additional metadata; their absence from resource server validation does not invalidate the token. The governance gateway — not the resource server — is responsible for IBAC evaluation.

### 2.3 Scope Mapping

**AIAM1-IOP-010.** AIAM-1 capabilities SHOULD map to OAuth 2.1 scopes for compatibility with existing authorization infrastructure.

**AIAM1-IOP-011.** When OAuth 2.1 scopes and AIAM-1 capability grants conflict, the AIAM-1 capability registry is authoritative. An agent whose OAuth token includes a scope not reflected in its AIAM-1 capability grants MUST NOT be permitted to exercise that scope. OAuth scopes are a first-pass filter at the resource server level; IBAC evaluation at the governance gateway is the final authority.

| AIAM-1 Capability | OAuth Scope | Notes |
|---|---|---|
| `telemetry.query` | `governance:telemetry:read` | Read-only telemetry access |
| `alert.escalate` | `governance:alert:write` | Escalation creation |
| `forensics.deep_scan` | `governance:forensics:read` | Deep forensic access |
| `infrastructure.modify` | `governance:infra:write` | Infrastructure modification |

The scope mapping is advisory — the governance gateway performs the authoritative IBAC evaluation. OAuth scopes provide a first-pass filter at the resource server level.

---

## 3. OpenID Connect Integration

**AIAM1-IOP-020.** A conformant implementation SHOULD support OpenID Connect for agent identity federation in environments where OIDC is the standard identity protocol.

**AIAM1-IOP-021.** The OIDC ID Token for an AIAM-1 agent SHOULD include:

- Standard OIDC claims (`sub`, `iss`, `aud`, `exp`, `iat`)
- `aiam_claim_ref` referencing the AIAM-1 composite identity claim
- `aiam_principal` identifying the accountable party

**AIAM1-IOP-022.** OIDC UserInfo endpoint responses for AIAM-1 agents MAY include the full composite identity claim as a nested JSON object under the `aiam_identity` key. This enables OIDC-compatible systems to access AIAM-1 identity depth without requiring a separate AIAM-1 registry query.

---

## 4. SCIM Integration

**AIAM1-IOP-030.** A conformant implementation SHOULD support SCIM (System for Cross-domain Identity Management) for agent lifecycle management.

**AIAM1-IOP-031.** AIAM-1 extends the SCIM User schema with agent-specific attributes:

```json
{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:User",
    "urn:aegis:params:scim:schemas:aiam:1.0:Agent"
  ],
  "id": "agent:soc-01",
  "userName": "soc-triage-agent-01",
  "displayName": "SOC Triage Agent",
  "active": true,
  "urn:aegis:params:scim:schemas:aiam:1.0:Agent": {
    "agentType": "autonomous",
    "modelProvenance": {
      "modelFamily": "claude",
      "modelVersion": "opus-4-6",
      "provider": "anthropic"
    },
    "orchestration": {
      "framework": "aegis-core",
      "frameworkVersion": "0.2.0"
    },
    "principal": {
      "principalId": "org:acme-security-ops",
      "principalType": "organization"
    },
    "aiamClaimRef": "idc-acme-soc-triage-20260410"
  }
}
```

**AIAM1-IOP-032.** Agent provisioning (creation), update, and deprovisioning (deletion) via SCIM MUST produce AIAM-1 attestation records. SCIM-based deprovisioning MUST trigger identity claim revocation.

---

## 5. SAML Integration

**AIAM1-IOP-040.** A conformant implementation SHOULD support SAML assertions for federated agent identity in environments that have not adopted OAuth 2.1.

**AIAM1-IOP-041.** SAML assertions for AIAM-1 agents SHOULD include:

- Standard SAML subject (`NameID` = agent identifier)
- `AttributeStatement` containing:
  - `aiam:ClaimRef` — reference to the AIAM-1 composite identity claim
  - `aiam:Principal` — accountable party identifier
  - `aiam:SessionRef` — active session reference (if applicable)

**AIAM1-IOP-042.** SAML-based federation for AIAM-1 agents is a compatibility mechanism for legacy environments. New deployments SHOULD prefer OAuth 2.1 / OIDC.

---

## 6. Interoperability Integrity

**AIAM1-IOP-050.** Interoperability mappings MUST NOT compromise the integrity of AIAM-1 primitives. Specifically:

- If an interoperability target cannot express intent context (e.g., standard OAuth 2.1 scopes have no intent dimension), the mapping MUST document the loss of enforcement guarantee.
- When intent context cannot be transmitted through the interoperability protocol, the governance gateway MUST obtain it through a separate channel (e.g., the AIAM-1 intent claim submitted alongside the action proposal).
- Compensating controls MUST be documented for any AIAM-1 primitive that is not expressible in the target protocol.

**AIAM1-IOP-051.** The governance gateway is the authoritative enforcement point for IBAC evaluation, regardless of what interoperability protocol carries the authentication credentials. OAuth, OIDC, SCIM, and SAML provide authentication and basic authorization. IBAC provides intent-bound authorization. The two layers are complementary, not substitutive.

---

## 7. Security Considerations

### 7.1 Token Scope Divergence

If OAuth scopes and AIAM-1 capability grants diverge (e.g., the OAuth token includes a scope that the AIAM-1 capability registry does not grant), the governance gateway MUST treat the AIAM-1 capability registry as authoritative. OAuth scopes are a first-pass filter; IBAC evaluation is the final authority.

### 7.2 SCIM Provisioning as Attack Surface

SCIM provisioning endpoints that can create AIAM-1 agents become high-value targets. Implementations MUST protect SCIM endpoints with strong authentication, rate limiting, and audit logging. Unauthorized agent provisioning via SCIM MUST be detectable and reversible.

### 7.3 Cross-Protocol Identity Binding

An agent authenticated via OAuth at one resource server and via SAML at another must be recognized as the same agent. Implementations MUST maintain consistent identity binding across protocols, using the AIAM-1 `claim_id` as the canonical cross-protocol identifier.

---

## 8. Open Questions

1. **AIAM-1 claims in token introspection.** Should the OAuth 2.1 token introspection endpoint (RFC 7662) return AIAM-1 claim references? This would enable resource servers to discover AIAM-1 identity depth without a separate registry query. Deferred to v0.2.

2. **Verifiable Credentials.** W3C Verifiable Credentials provide a standards-based mechanism for presenting claims that could carry AIAM-1 identity and intent. Integration with the VC ecosystem is deferred to v0.2.

3. **AIAM-1 as an OAuth grant type.** Could IBAC evaluation be formalized as a custom OAuth grant type, enabling standard OAuth flows to carry intent context natively? This is an architectural question deferred to v0.2.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — Finnoybu IP LLC*

# ATM-1 Security Properties & Assumptions

**Document**: AEGIS_ATM1_SECURITY_PROPERTIES.md
**Version**: 1.0 (Normative)
**Part of**: AEGIS Adaptive Threat Model (ATM-1)
**Related**: AEGIS_ATM1_ATTACK_VECTORS.md
**Last Updated**: March 5, 2026

---

## Core Security Properties

The AEGIS governance architecture maintains the following core security properties:

### SP-1: Decision Integrity

**Property**: Every governance decision is computed deterministically and cannot be modified after issuance.

**Invariants**:

1. `DECISION_RESPONSE.signature` prevents post-hoc modification
2. `decision_hash = H(request_hash || policy_version || risk_factors || actor_trust)`
3. If computed again with identical inputs → identical decision
4. Audit log stores immutable decision_hash; any modification detected

**How Maintained**:

- Finite-state decision engine (no randomness)
- Deterministic policy evaluation
- Cryptographic signing of decisions
- Audit chaining with tamper-evident hashing

**Threats Prevented**:

- AV-4.1 (Audit Tampering) — hash chain breaks if modified
- AV-1.3 (Replay) — nonce prevents same decision replayed multiple times

---

### SP-2: Actor Attribution

**Property**: Every action is attributable to an authenticated actor identity; no anonymous actions.

**Invariants**:

1. Every ACTION_PROPOSE includes `actor_id` and authentication proof
2. `actor_id` MUST match authenticated token subject
3. Audit log contains: timestamp, actor_id, actor_type, request_hash, decision, signature
4. Actor cannot deny having submitted request (signature proof of involvement)

**How Maintained**:

- Required `actor` field in all messages (no default)
- mTLS or Bearer token authentication (proves identity)
- Cryptographic signature on action and decision
- Audit log includes signature verification

**Threats Prevented**:

- AV-3.1 (Identity Spoofing) — mTLS cert verification prevents forged identity
- AV-3.2 (Lateral Movement) — action attribution reveals privilege escalation attempt
- AV-4.2 (Log Injection) — signature on logs prevents unauthorized entries

---

### SP-3: Policy Immutability Window

**Property**: During execution window, active policy cannot be changed; changes are version-gated.

**Invariants**:

1. Active policy has `version` identifier
2. All decisions include `policy_version` in signature
3. Policy change requires atomic deployment of new version
4. No in-flight decisions affected by policy changes (version-separated)
5. Audit log records all policy versions and change timestamps

**How Maintained**:

- Version-based policy model (not edit-in-place)
- Policy change requires signed deployment artifact
- Two-person approval for production changes
- Automatic reconciliation to catch unauthorized changes

**Threats Prevented**:

- AV-2.3 (Policy Tampering) — signature on policy prevents undetected modification
- AV-2.1 (Policy Evasion) — clear version allows verification of intended policy
- T2: Policy Tampering (from original threat model)

---

### SP-4: Capability Authorization Binding

**Property**: Capability execution strictly requires prior authorization via policy grant.

**Invariants**:

1. Capability MUST be explicitly registered in Capability Registry
2. Actor MUST have explicit grant for capability (in policy)
3. Action execution attempted without grant → DENY decision
4. No implicit or inherited capabilities (grant must be explicit)
5. Grant revocation is immediate (no in-flight window)

**How Maintained**:

- Default-deny policy model
- Capability Registry lookup before policy evaluation
- Policy engine checks actor.grants for capability
- Audit log includes capability existence check result

**Threats Prevented**:

- AV-2.1 (Policy Evasion) — unknown capabilities rejected
- T1: Governance Bypass (from original threat model)

---

### SP-5: Audit Completeness & Append-Only

**Property**: Audit log captures every governance decision and cannot be retroactively modified.

**Invariants**:

1. Every decision recorded in append-only log
2. Audit records cryptographically chained (hash of previous record)
3. Deletion of audit records detected via hash chain break
4. Modification of audit record detected via signature verification
5. Audit log cannot be accessed for write by non-audit service

**How Maintained**:

- Message authentication code on each audit record
- Hash chain linking consecutive records
- Separate audit service with restricted write access
- Regular integrity checks via hash chain verification

**Threats Prevented**:

- AV-4.1 (Audit Tampering) — hash chain breaks if record deleted
- AV-4.2 (Log Injection) — MAC prevents unsigned entries
- AV-4.3 (Audit Availability) — append-only storage ensures new records written despite attacks

---

## Security Assumptions

### Assumption-1: Cryptographic Functions Are Secure

**Assumption**: All cryptographic operations (signing, hashing, encryption) use secure implementations.

**Verified By**:

- Use of NIST-approved algorithms (ED25519, SHA-256, AES-256)
- Cryptographic library audits (e.g., libsodium security review)
- Regular CVE monitoring and patching
- No custom cryptography implementations

**If Violated**: All security properties fail; attacker can forge signatures, break encryption.

---

### Assumption-2: Governance Engine Correctly Implements Policy Language

**Assumption**: Policy evaluator correctly evaluates policy language according to specification.

**Verified By**:

- Formal grammar specification (context-free)
- Automated test suite with >95% decision branch coverage
- Property-based fuzz testing of policy evaluation
- Code review by security specialists

**If Violated**: AV-2.1 (Policy Evasion) becomes likely; policy intent not enforced.

---

### Assumption-3: Network Isolation & TLS Deployment

**Assumption**: Governance communication uses TLS 1.3+; network isolated from untrusted networks.

**Verified By**:

- Mandatory TLS enforcement (reject non-HTTPS)
- Certificate pinning for governance endpoints
- Network segmentation (firewall rules)
- Service mesh mTLS between components

**If Violated**: AV-1.1 (Message Tampering) and AV-1.4 (Token Theft) become feasible.

---

### Assumption-4: Host Security & Container Isolation

**Assumption**: Governance runtime runs in isolated container with restricted system access.

**Verified By**:

- Read-only root filesystem for runtime
- Restricted syscall whitelist (seccomp)
- Network policy (egress only to trusted targets)
- Regular vulnerability scanning of container image

**If Violated**: AV-3.3 (Credential Harvesting) and AV-6.2 (Build Tampering) threats increase.

---

### Assumption-5: Identity Provider Security

**Assumption**: Identity provider (TLS certificate authority, token issuer) is secure and trustworthy.

**Verified By**:

- Authority runs in isolated, heavily monitored environment
- Multi-person approval for certificate issuance
- Audit log of all issued credentials
- Regular key rotation and compromise drills

**If Violated**: AV-3.1 (Identity Spoofing) and AV-3.2 (Lateral Movement) become feasible.

---

### Assumption-6: Audit Storage Integrity

**Assumption**: Audit storage is append-only, with no capability to delete or modify records.

**Verified By**:

- Storage backend designed for immutability (e.g., WORM, blockchain)
- Audit service has read-only access to compute layer
- Regular hash chain verification
- Replicated across geographically separated locations

**If Violated**: AV-4.1 (Audit Tampering) becomes feasible.

---

## Trust Boundaries

### Boundary-1: External Network ↔ Governance Network

**Trust**: One-way (inbound only)

- External API may call governance endpoints
- Governance runtime NEVER initiates outbound connections to external networks
- OAuth/Bearer tokens trusted only if issued by internal authority
- All external input treated as potentially malicious

**Enforcement**:

- Firewall rules (egress blocked except to whitelisted internal targets)
- Network policy in service mesh
- Regular network monitoring for policy violations

---

### Boundary-2: Governance Runtime ↔ Infrastructure

**Trust**: One-way (infrastructure trusts governance decisions)

- Infrastructure receives DECISION_RESPONSE with cryptographic proof
- Infrastructure verifies decision signature before execution
- Infrastructure logs execution outcome and reports back
- Governance cannot execute directly; must go through Tool Proxy

**Enforcement**:

- Tool Proxy cryptographic verification of decision
- Infrastructure audit logging of all governance decisions
- Rolling key rotation for decision signing

---

### Boundary-3: Human Operator ↔ Governance System

**Trust**: One-way (governance trusts human for escalation review)

- Humans assume `escalation_reviewer` role
- Change approval requires human signature (cryptographic proof)
- Human-authorized changes tracked in audit log
- No implicit trust; every action requires explicit approval

**Enforcement**:

- Audit logging of all human-made decisions
- Cryptographic signature on human-authored policies
- Two-person rule for sensitive changes

---

### Boundary-4: Policy Storage ↔ Policy Evaluation

**Trust**: Policy must be signed and verified before use

- Policy evaluated only after cryptographic signature verified
- Policy version MUST match running version
- Drift detection alerts if policy file modified
- No hot-patching of policy without deployment

**Enforcement**:

- Policy signature verification before each evaluation
- Version comparison against expected version
- Deployment validation that matches policy hash

---

## Classified Threat Scenarios

### Classified-1: Persistent Backdoor in Governance Runtime

**Attack Chain**:

1. Supply-chain attacker compromises build system
2. Malicious code injected into governance runtime binary
3. Backdoor remains dormant until triggered
4. On receipt of specific action, bypasses policy evaluation
5. All downstream users affected

**Security Properties Affected**:

- SP-1 (Decision Integrity) — compromised, decisions are forged
- SP-4 (Capability Authorization) — bypassed entirely

**Detectability**: Very difficult without code review or binary analysis

**Detection Methods**:

- Software Bill of Materials (SBOM) analysis
- Live patching detection (modified code sections)
- Decision behavior anomaly detection
- Cryptographic verification of runtime binary

---

### Classified-2: Compromise of Long-Lived Credential

**Attack Chain**:

1. Attacker gains access to high-privilege service account key
2. Uses credential to issue thousands of ACTION_PROPOSE requests
3. Requests use low-risk individual actions
4. Aggregate impact is high (e.g., 1TB data exfil)
5. Undetected due to lack of cross-request correlation

**Security Properties Affected**:

- SP-3 (Audit Completeness) — audit trail exists but patterns undetected

**Detection Methods**:

- Long-term behavior profiling
- Aggregate risk scoring across time windows
- Anomaly detection on request volume/types
- Comparisons to baseline historical behavior

---

## Next Steps

- [AEGIS_ATM1_MITIGATIONS.md](./AEGIS_ATM1_MITIGATIONS.md) — Control strategies and mitigations
- [AEGIS_ATM1_RESIDUAL_RISKS.md](./AEGIS_ATM1_RESIDUAL_RISKS.md) — Residual risks and acceptance

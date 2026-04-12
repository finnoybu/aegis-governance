---
title: "AEGIS ATM-1 Mitigations & Defense Strategies"
description: "ATM-1 mitigations — architectural countermeasures"
---

# AEGIS ATM-1 Mitigations & Defense Strategies

**Document**: ATM-1/Mitigations (AEGIS_ATM1_MITIGATIONS.md)\
**Version**: 1.0 (Normative)\
**Part of**: AEGIS Adaptive Threat Model (ATM-1)\
**References**: ATM-1/Vectors\
**Last Updated**: March 6, 2026

---

### Mitigation Framework

Mitigations are organized by:

1. **Control Type**: Preventive, Detective, Responsive
2. **Scope**: Technical, Process, Operational
3. **Coverage**: Attack vector(s) addressed
4. **Implementation**: How to deploy in AEGIS

---

### Preventive Controls

#### PC-1: Transport Security[^18]

**Applies To**: AV-1.1 (Message Tampering), AV-1.4 (Token Theft)

**Technical Implementation**:

- Mandatory TLS 1.3+ for all AGP-1 communication
- Certificate pinning for governance endpoints
- Strong cipher suites (no legacy): TLS_AES_256_GCM_SHA384
- Perfect forward secrecy (ephemeral keys)

**Configuration**:

```yaml
tls:
  min_version: "1.3"
  cipher_suites:
    - "TLS_AES_256_GCM_SHA384"
    - "TLS_CHACHA20_POLY1305_SHA256"
  certificate_pinning: true
  certificates:
    governance_ca_pin: "sha256/CERTIFICATE_HASH"
```

**Verification**:

- `curl --tls-max 1.2 governance-api` → FAIL (old TLS rejected)
- SSL Labs grade A+
- nmap --script ssl-enum-ciphers → strong ciphers only

---

#### PC-2: Cryptographic Message Authentication[^3]

**Applies To**: AV-1.3 (Replay), AV-4.2 (Log Injection), AV-1.2 (Injection)

**Technical Implementation**:

- HMAC-SHA256 on all AGP-1 messages
- Nonce validation to prevent replay
- Timestamp validation (within ±60 seconds)
- Sequence number tracking per actor

**Implementation**:

```json
{
  "message_type": "ACTION_PROPOSE",
  "action_id": "a-123",
  "timestamp": "2026-03-05T19:12:01Z",
  "nonce": "uuid-random-per-request",
  "hmac": "sha256(body || shared_secret || nonce)",
  "body": { ... }
}
```

**Verification**:

- Replay same nonce → DENY (nonce already used)
- Modify any field → DENY (HMAC verification fails)

---

#### PC-3: Role-Based Access Control (RBAC)[^2]

**Applies To**: AV-2.4 (Authorization Bypass), AV-3.2 (Privilege Escalation)

**Technical Implementation**:

- Define actor roles: `analyst`, `admin`, `escalation_reviewer`
- Capabilities grouped by role
- Explicit grants (no inheritance)
- Regular access reviews

**Grant Model**:

```yaml
roles:
  analyst:
    capabilities: ["telemetry.query", "logs.read"]
    cannot_assume: ["admin"]
    cannot_grant: any
  admin:
    capabilities: ["*"]
    can_assume: ["analyst"]
    can_grant: analysts only
```

**Enforcement**:

- Policy engine verifies actor.role in every decision
- Audit logs role used for each decision

---

#### PC-4: Input Validation & Sanitization

**Applies To**: AV-1.2 (Message Injection), AV-2.1 (Evasion)

**Technical Implementation**:

- Strict JSON schema validation for all messages
- Whitelist-based parameter validation
- Rate limiting on message size (max 1MB)
- No dynamic code execution from user input

**Validation Rules**:

```yaml
action_propose.parameters:
  type: object
  max_properties: 100
  additionalProperties: true
  properties:
    query:
      type: string
      max_length: 10000
      pattern: "^[a-zA-Z0-9_:.*, ()-]+$"  # No SQL injection chars
```

**Enforcement**:

- JSONSchema validation before processing
- Error response if validation fails
- Audit logs invalid message attempts

---

#### PC-5: Policy Signing & Verification

**Applies To**: AV-2.3 (Policy Tampering)

**Technical Implementation**:

- All policies signed with ED25519 key
- Signature verified before policy loaded
- Policy version MUST match expected version
- Automated diff alerts on any change

**Deployment Process**:

```bash
## Sign policy
policy_hash=$(sha256sum policy.yaml | cut -f1)
signature=$(openssl dgst -sha256 -sign policy_key policy.yaml | base64)

## On deployment
verify_signature(policy.yaml, signature, pubkey) || FAIL
check_version(policy.version == expected_version) || FAIL
```

**Verification**:

- Modified policy.yaml → signature fails
- Version mismatch → deployment rejected
- Audit log records all policy versions

---

#### PC-6: Identity Provider Hardening

**Applies To**: AV-3.1 (Identity Spoofing)

**Technical Implementation**:

- Certificate authority runs in isolated, air-gapped network
- Multi-signature requirement for certificate issuance
- Short-lived certificates (max 90 days)
- Revocation capability (CRL/OCSP)

**Configuration**:

```yaml
certificate:
  max_validity_days: 90
  revocation_check: ocsp
  issuer:
    requires_approvals: 2  # Multi-person approval
    approval_quorum: true
```

**Verification**:

- `openssl x509 -noout -dates` → expiry < 90 days
- Revoked cert → connection rejected
- OCSP stapling → instantaneous revocation

---

### Detective Controls

#### DC-1: Audit Logging & Integrity[^1]

**Applies To**: AV-4.1 (Tampering), AV-4.3 (Availability), SP-5 (Completeness)

**Technical Implementation**:

- Append-only audit log with Hash Chain
- MAC on each record: `MAC = HMAC(record || prev_hash, secret_key)`
- Replicated across 3+ geographically separated locations
- Audit log ownership restricted (only audit service can write)

**Schema**:

```json
{
  "entry_id": 12345,
  "timestamp": "2026-03-05T19:12:01Z",
  "actor_id": "agent:soc-01",
  "action": "ACTION_PROPOSE",
  "action_id": "a-123",
  "decision": "ALLOW",
  "policy_version": "2026.03.05",
  "risk_score": 2.5,
  "previous_hash": "sha256-hash-of-entry-12344",
  "entry_hash": "sha256-hash-of-this-entry",
  "mac": "hmac-sha256-of-entry"
}
```

**Verification**:

- `verify_hash_chain(audit_log)` → success iff no deletions/modifications
- Delete any entry → `previous_hash` link breaks
- Modify entry → MAC verification fails

---

#### DC-2: Behavioral Anomaly Detection

**Applies To**: AV-7.1 (Coordinated Abuse), AV-7.2 (Slow-Burn Exfil)

**Technical Implementation**:

- Baseline actor behavior profile (30-day window)
- Detect deviations: request volume, type, rate, timing
- Sliding-window aggregate risk (12-hour window)
- Alert on threshold breach

**Detection Rules**:

```yaml
anomaly_detector:
  rules:
    - name: "high_volume_spike"
      condition: "requests_per_hour > 10x baseline"
      action: "escalate"
    - name: "coordinated_exfil"
      condition: "sum(data_returned, 12h_window) > 100GB"
      action: "escalate"
    - name: "unusual_time_of_day"
      condition: "request_issued_at NOT in historical_times"
      action: "increase_escalation_threshold"
```

**Alert Handling**:

- Alert escalated to security team
- Triggered policy evaluation flag: `anomaly_detected=true`
- Risk threshold may increase for actor
- Escalation to human review recommended

---

#### DC-3: Policy Drift Detection

**Applies To**: AV-2.3 (Policy Tampering)

**Technical Implementation**:

- Hash of expected policy stored in config
- Runtime loads policy, compares hash to expected value
- Any drift triggers alert and audit log entry
- No decision made until drift resolved

**Configuration**:

```yaml
policy:
  expected_hash: "sha256-of-approved-policy"
  load_on_startup: "/etc/aegis/policy.yaml"
  drift_detection:
    enabled: true
    alert_on_mismatch: true
    action: "halt_decisions"
```

**Verification**:

- Modify policy.yaml → hash mismatch → FAIL
- Audit log: "POLICY_DRIFT_DETECTED"
- Operator must approve new policy before decisions resume

---

#### DC-4: Decision Behavior Profiling

**Applies To**: AV-2.1 (Evasion), AV-5.1 (Timing Attacks)

**Technical Implementation**:

- Profile expected decision distribution (approval rate, DENY rate, ESCALATE rate)
- Detect anomalies in decision outcomes
- Compare to historical baseline

**Metrics**:

```yaml
decision_profiling:
  per_actor:
    avg_approval_rate: 0.85  # 85% of requests approved
    std_dev: 0.05
  per_capability:
    telemetry.query:
      escalation_rate: 0.02  # 2% escalations
      denial_rate: 0.01      # 1% denials
  alert_threshold:
    z_score: 3.0  # Alert if 3 standard deviations from mean
```

**Detection Example**:

- Actor normally: 90% ALLOW, 2% ESCALATE, 8% DENY
- Suddenly: 98% ALLOW, 0% ESCALATE, 2% DENY
- z_score = 4.0 → Alert: "Decision outcome anomaly detected"

---

#### DC-5: Runtime Integrity Monitoring[^5]

**Applies To**: AV-6.2 (Build Tampering), Malware Detection

**Technical Implementation**:

- File integrity monitoring (FIM) on runtime binary
- Measure against expected hash at startup
- Periodic rehashing during runtime
- Syscall monitoring for unexpected behavior

**Implementation**:

```bash
## On startup
RUNTIME_HASH=$(sha256sum /opt/aegis/governance-runtime)
EXPECTED_HASH=$(cat /etc/aegis/runtime.hash)
if [ "$RUNTIME_HASH" != "$EXPECTED_HASH" ]; then
  systemctl stop aegis
  alert "RUNTIME_INTEGRITY_FAILURE"
fi
```

**Ongoing Monitoring**:

- Syscall monitoring via seccomp (deny unexpected calls)
- Memory anomaly detection (unexpected changes)
- Network connection monitoring (deny unexpected egress)

---

### Responsive Controls

#### RC-1: Incident Response Playbook

**Process**:

1. **Detection**: Anomaly detected via DC-2, DC-3, DC-4
2. **Alerting**: Automated alert to security team + escalation_reviewer
3. **Investigation**: Retrieve audit logs, analyze decision patterns
4. **Containment**: Revoke actor credentials, disable capability grants
5. **Remediation**: Fix policy, deploy update, verification
6. **Recovery**: Resume operations, monitor for recurrence

**Automation**:

```yaml
incident_response:
  on_anomaly_alert:
    - action: "revoke_actor_credentials"
      reason: "anomaly_detected"
      duration: "24_hours"
    - action: "require_escalation"
      for_actor: "anomaly_actor"
      capability: "*"  # Require review for all actions
    - action: "notify_security_team"
      channels: ["slack", "email", "pagerduty"]
```

---

#### RC-2: Credential Revocation

**Applies To**: AV-3.3 (Credential Harvesting), AV-1.4 (Token Theft)

**Technical Implementation**:

- Revocation list (CRL) for certificates
- Token blacklist for compromised tokens
- Immediate distribution of revocation to all components
- No grace period (revoked credential immediately rejected)

**Process**:

1. Compromise suspected → revocation issued immediately
2. All components (governance runtime, tool proxies) load revocation
3. Revoked credential rejected within seconds
4. New credential issued to actor

**Verification**:

- Revoked bearer token → 401 Unauthorized
- Revoked certificate → TLS verification fails

---

#### RC-3: Automatic Rollback

**Applies To**: AV-2.3 (Policy Tampering), AV-6.2 (Build Tampering)

**Technical Implementation**:

- Policy versioning with automatic rollback capability
- Runtime version tracking and rollback
- Automatic rollback on detection of tampering

**Trigger Conditions**:

```yaml
rollback:
  on_policy_drift: true
  on_signature_failure: true
  on_multiple_anomalies: true  # 3+ alerts in 1 hour
  to_version: "last_known_good"
  verification: "requires_approval"
```

**Process**:

1. Tampering detected → rollback triggered
2. System reverts to last known-good version
3. Notification sent to operators
4. Investigation initiated

---

### Mitigation Coverage Matrix

| Attack Vector | Preventive | Detective | Responsive |
|---|---|---|---|
| AV-1.1 (Tampering) | PC-1 (TLS) | DC-5 (Integrity) | RC-2 (Revocation) |
| AV-1.2 (Injection) | PC-4 (Validation) | DC-1 (Audit) | RC-1 (Response) |
| AV-1.3 (Replay) | PC-2 (Auth) | DC-1 (Audit) | RC-2 (Revocation) |
| AV-1.4 (Token Theft) | PC-1 (TLS) | DC-1 (Audit) | RC-2 (Revocation) |
| AV-2.1 (Evasion) | PC-4 (Validation) | DC-4 (Decision Profiling) | RC-1 (Response) |
| AV-2.2 (Composition) | PC-3 (RBAC) | DC-2 (Anomaly) | RC-1 (Response) |
| AV-2.3 (Tampering) | PC-5 (Signing) | DC-3 (Drift) | RC-3 (Rollback) |
| AV-2.4 (Bypass) | PC-3 (RBAC) | DC-1 (Audit) | RC-1 (Response) |
| AV-3.1 (Spoofing) | PC-6 (Identity) | DC-3 (Drift) | RC-2 (Revocation) |
| AV-3.2 (Escalation) | PC-3 (RBAC) | DC-1 (Audit) | RC-2 (Revocation) |
| AV-4.1 (Log Tampering) | PC-2 (Auth) | DC-1 (Audit) | RC-3 (Rollback) |
| AV-5.1 (Timing) | (None) | DC-4 (Profiling) | (None) |
| AV-6.2 (Build Tampering) | (None) | DC-5 (Integrity) | RC-3 (Rollback) |

---

### Next Steps

- [AEGIS_ATM1_RESIDUAL_RISKS.md](./AEGIS_ATM1_RESIDUAL_RISKS.md) — Residual risks and acceptance
- [AEGIS_ATM1_INDEX.md](./AEGIS_ATM1_INDEX.md) — Complete threat model overview

---

### References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../../REFERENCES.md).

[^2]: F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security (TISSEC)*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382. See [REFERENCES.md](../../REFERENCES.md).

[^3]: S. Hallé and R. Villemaire, "Runtime Enforcement of Message-Based Communication Contracts," *IEEE Transactions on Software Engineering*, vol. 38, no. 3, pp. 531–550, May–June 2012, doi: 10.1109/TSE.2011.31. See [REFERENCES.md](../../REFERENCES.md).

[^5]: H. Pearce, S. Pinisetty, P. S. Roop, M. M. Y. Kuo, and A. Ukil, "Smart I/O Modules for Mitigating Cyber-Physical Attacks on Industrial Control Systems," *IEEE Transactions on Industrial Informatics*, vol. 16, no. 7, pp. 4659–4669, July 2020, doi: 10.1109/TII.2019.2945520. See [REFERENCES.md](../../REFERENCES.md).

[^18]: B. Campbell, J. Bradley, N. Sakimura, and T. Lodderstedt, "OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens," RFC 8705, Internet Engineering Task Force, Feb. 2020. [Online]. Available: <https://www.rfc-editor.org/rfc/rfc8705>. See [REFERENCES.md](../../REFERENCES.md).

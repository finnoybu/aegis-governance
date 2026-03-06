# ATM-1 Attack Vectors & Exploitation Techniques

**Document**: AEGIS_ATM1_ATTACK_VECTORS.md
**Version**: 1.0 (Normative)
**Part of**: AEGIS Adaptive Threat Model (ATM-1)
**Related**: AEGIS_ATM1_THREAT_ACTORS.md
**Last Updated**: March 5, 2026

---

## Attack Surface Map

### Primary Attack Surfaces

| Surface | Layer | Access | Risk |
|---------|-------|--------|------|
| AGP Request Ingress API | Protocol | Network | HIGH |
| Policy Management Plane | Configuration | Internal | CRITICAL |
| Capability Registry | Configuration | Internal | CRITICAL |
| Tool Proxy Execution | Execution | Both | HIGH |
| Audit Storage/Query | Data | Internal | HIGH |
| Governance Engine Logic | Runtime | Internal | CRITICAL |
| Identity/Credential Store | Identity | Internal | CRITICAL |
| Federation Communication | Network | Both | MEDIUM |
| CI/CD Pipeline | Deployment | Internal | CRITICAL |

---

## Attack Vector Categories

### AV-1: Protocol-Level Attacks

#### AV-1.1 Message Tampering
- **Vector**: Attacker intercepts and modifies AGP-1 MESSAGE in transit
- **Precondition**: Network not using TLS or TLS improperly configured
- **Technique**: Man-in-the-middle (MITM) proxy, ARP spoofing, DNS hijacking
- **Impact**: ACTION_PROPOSE parameters modified to request unauthorized capabilities
- **Example**: Change `capability: "telemetry.query"` to `capability: "infrastructure.delete"`

#### AV-1.2 Message Injection
- **Vector**: Attacker crafts malformed AGP-1 message to trigger parser vulnerabilities
- **Precondition**: Message parser doesn't validate input strictly
- **Technique**: Fuzzing, buffer overflow, XML Entity Expansion (XXE), JSON injection
- **Impact**: Code execution in governance runtime, bypass of message validation
- **Example**: Oversized `parameters` object causing memory exhaustion

#### AV-1.3 Replay Attack
- **Vector**: Attacker captures valid governance DECISION_RESPONSE and replays it
- **Precondition**: Nonce or timestamp not validated in replay protection
- **Technique**: Capture decision message, resubmit with original action_id
- **Impact**: Action approved multiple times, causing repeated unauthorized execution
- **Example**: Replay approval for "delete_backup" decision 100 times

#### AV-1.4 Token/Credential Theft
- **Vector**: Attacker steals or forges authentication tokens
- **Precondition**: Tokens not properly secured, long expiration, or weak signing
- **Technique**: Memory dump, token sniffing, JWT algorithm downgrade attack
- **Impact**: Attacker can submit ACTION_PROPOSE as legitimate actor
- **Example**: Forge Bearer token with admin scope, valid for 30 days

---

### AV-2: Policy-Layer Attacks

#### AV-2.1 Policy Evasion
- **Vector**: Attacker crafts ACTION_PROPOSE that technically matches policy but violates intent
- **Precondition**: Policy language is ambiguous or has edge cases
- **Technique**: Semantic exploitation, type confusion, boundary conditions
- **Impact**: Unauthorized action approved by policy evaluator
- **Example**: Policy allows `infrast.query_logs` for "operational" purposes; attacker labels data exfiltration as "operational analysis"

#### AV-2.2 Policy Bypass via Composition
- **Vector**: Attacker combines multiple low-risk approved actions to achieve high-risk goal
- **Precondition**: Risk scoring doesn't consider cross-action patterns
- **Technique**: Distributed attack over hours/days, each action individually approved
- **Impact**: Exfiltrate data 1GB/hour over 1000 requests (each approved) = 1TB exfil undetected
- **Example**: 1000 "telemetry.query" requests each returning 1GB, cumulative risk undetected

#### AV-2.3 Policy Tampering
- **Vector**: Attacker modifies policy files to permit forbidden capabilities
- **Precondition**: Policy storage not signed, versioning not audited, or deployment not verified
- **Technique**: Direct file modification, Git history rewrite, unsafe deployment script
- **Impact**: Systematic privilege escalation; attacker gains capability grant
- **Example**: Edit policy.yaml to add `allow_action: "*" for actor: "attacker"` in production

#### AV-2.4 Authorization Bypass
- **Vector**: Attacker circumvents policy evaluation entirely
- **Precondition**: Multiple execution paths, some skip policy enforcement
- **Technique**: Call Governed Capability directly, bypass Tool Proxy, exploit race condition
- **Impact**: Capability executed without governance approval
- **Example**: Direct call to backend API endpoint that should be Tool Proxy-only

---

### AV-3: Identity & Authentication Attacks

#### AV-3.1 Identity Spoofing
- **Vector**: Attacker assumes identity of legitimate actor
- **Precondition**: Identity verification weak or credential issuer compromised
- **Technique**: Forge certificate, compromise identity provider, social engineer token issuance
- **Impact**: Malicious actions attributed to trusted actor; blame misdirected
- **Example**: Forge mTLS certificate for "soc-analyst-trusted" identity

#### AV-3.2 Lateral Movement via Privilege Escalation
- **Vector**: Attacker gains access as low-privilege agent, escalates to higher-privilege agent
- **Precondition**: Permission model allows agents to assume other identities or grant themselves capabilities
- **Technique**: Exploit role assumption mechanism, SSRF to internal identity service, capability grant exploitation
- **Impact**: Attacker gains access to sensitive capabilities
- **Example**: Low-privilege agent issues ACTION_PROPOSE to grant itself "delete_audit_logs" capability

#### AV-3.3 Credential Harvesting
- **Vector**: Attacker extracts credentials from environment or logs
- **Precondition**: Credentials logged in plaintext, stored unencrypted, or discoverable via information disclosure
- **Technique**: Log injection, environment variable dumping, side-channel attacks (timing)
- **Impact**: Bulk credential compromise; attacker assumes identity of multiple agents
- **Example**: Error logs contain Bearer tokens; attacker extracts 500 tokens from logs

---

### AV-4: Audit & Logging Attacks

#### AV-4.1 Audit Log Tampering
- **Vector**: Attacker deletes or modifies audit records to hide unauthorized actions
- **Precondition**: Audit storage not append-only, not cryptographically signed, or accessible to compromise
- **Technique**: Direct database modification, log file deletion, corrupted backup restoration
- **Impact**: Loss of accountability; no evidence of attack
- **Example**: Delete execution report showing unauthorized "infrastructure.delete" call

#### AV-4.2 Audit Log Injection
- **Vector**: Attacker injects false audit entries to hide or misdirect investigation
- **Precondition**: Audit logging API not authenticated, or allows arbitrary entry insertion
- **Technique**: Craft EXECUTION_REPORT claiming legitimate usage
- **Impact**: Misleading investigation; blame attributed to innocent actor
- **Example**: Inject log entry "analyst:bob performed telemetry.query" to hide attacker's activity

#### AV-4.3 Audit Availability Attacks
- **Vector**: Attacker overwhelms audit storage or retrieval, preventing compliance retrieval
- **Precondition**: Audit storage has DoS vulnerability or rate limiting not enforced
- **Technique**: Millions of queries, storage exhaustion, query amplification
- **Impact**: Audit records inaccessible during incident investigation
- **Example**: Query audit logs 10,000 times/sec, causing database overload

---

### AV-5: Timing & Side-Channel Attacks

#### AV-5.1 Timing Attack on Policy Evaluation
- **Vector**: Attacker measures decision latency to infer policy structure
- **Precondition**: Policy evaluation time varies based on matched rules
- **Technique**: Issue ACTION_PROPOSE, measure response time, infer rule existence/order
- **Impact**: Information disclosure of policy structure; enables targeted evasion
- **Example**: Policy with 1000 rules takes 100ms; timing reveals which rule matched

#### AV-5.2 Risk Scoring Side-Channel
- **Vector**: Attacker infers risk factors from decision outcome
- **Precondition**: Risk score or reason communicated in response
- **Technique**: Issue variations of ACTION_PROPOSE, measure risk change
- **Impact**: Understand risk factors; craft requests to minimize detected risk
- **Example**: Try requests with different timestamps, observe risk diff detection of anomaly detection

---

### AV-6: Supply-Chain & Dependency Attacks

#### AV-6.1 Dependency Poisoning
- **Vector**: Attacker compromises upstream library/container used in AEGIS deployment
- **Precondition**: Dependency not pinned, integrity not verified, or maintainer account compromised
- **Technique**: Typosquatting, account compromise, malicious PR merged
- **Impact**: Backdoor in governance runtime; all deployments vulnerable
- **Example**: Attacker compromises `jwt` library, injects key material extraction in token validation

#### AV-6.2 Build Artifact Tampering
- **Vector**: Attacker modifies compiled decision binary or runtime container image
- **Precondition**: Build artifacts not signed, deployment not verifying signatures
- **Technique**: Container registry compromise, artifact repository MITM
- **Impact**: Attacker's code runs as governance runtime; all decisions under attacker control
- **Example**: Malicious version of policy_evaluator binary distributed via Docker Hub

---

### AV-7: Distributed & Coordinated Attacks

#### AV-7.1 Coordinated Low-Risk Abuse
- **Vector**: Multiple compromised agents coordinate to achieve high-impact goal
- **Precondition**: Risk scoring doesn't correlate across agents
- **Technique**: Each agent issues individually low-risk requests; aggregate risk very high
- **Impact**: Data exfiltration or privilege escalation undetected
- **Example**: 100 agents each issue 1 "telemetry.query" (decision: ALLOW); aggregate result is 100GB exfil

#### AV-7.2 Slow-Burn Exfiltration
- **Vector**: Attacker exfiltrates data over extended period at low rate
- **Precondition**: Anomaly detection doesn't track long-term patterns
- **Technique**: Request small amounts daily, staying under daily risk thresholds
- **Impact**: Large-scale data theft without triggering alerts
- **Example**: 100MB/day for 100 days = 10GB undetected

---

## Severity Assessment

### Critical Severity (Requires Immediate Mitigation)
- AV-2.3 (Policy Tampering)
- AV-3.1 (Identity Spoofing with trusted identity)
- AV-4.1 (Audit Tamper affecting compliance)
- AV-6.2 (Build Artifact Tampering)

### High Severity (Requires Mitigation Within 1 Month)
- AV-1.1 (Message Tampering)
- AV-2.2 (Composition/Slow-Burn)
- AV-3.2 (Privilege Escalation)
- AV-6.1 (Dependency Poisoning)

### Medium Severity (Standard Security Controls)
- AV-1.2 (Message Injection)
- AV-2.1 (Policy Evasion)
- AV-3.3 (Credential Harvesting)
- AV-5.1 (Timing Attacks)

### Low Severity (Defense in Depth)
- AV-1.3 (Replay — with good nonce)
- AV-4.2 (Log Injection — with authentication)
- AV-5.2 (Risk Side-Channel)

---

## Next Steps

- [AEGIS_ATM1_SECURITY_PROPERTIES.md](./AEGIS_ATM1_SECURITY_PROPERTIES.md) — Security assumptions and invariants
- [AEGIS_ATM1_MITIGATIONS.md](./AEGIS_ATM1_MITIGATIONS.md) — Mitigation strategies for each vector

# ATM-1 Residual Risks & Risk Acceptance

**Document**: AEGIS_ATM1_RESIDUAL_RISKS.md
**Version**: 1.0 (Normative)
**Part of**: AEGIS Adaptive Threat Model (ATM-1)
**Related**: AEGIS_ATM1_MITIGATIONS.md
**Last Updated**: March 5, 2026

---

## Overview

Despite comprehensive preventive, detective, and responsive controls, some residual risks remain. This document catalogs:
1. Risks that cannot be fully mitigated
2. Risks where mitigation cost exceeds benefit
3. Risk acceptance criteria and governance
4. Compensating controls and continuous monitoring needs

---

## Residual Risks

### RR-1: Zero-Day Exploits in Governance Runtime

**Description**: A previously unknown vulnerability in governance runtime code is exploited before detection.

**Attack Vector**: AV-6.2 (Build Tampering) or AV-1.2 (Injection)

**Risk Level**: HIGH

**Current Mitigations**:
- DC-5 (Runtime Integrity Monitoring) — detects some exploits post-execution
- DC-1 (Audit Logging) — captures evidence of exploitation
- RC-3 (Automatic Rollback) — can revert to safe version if compromise confirmed

**Exploit Window**:
- Discovery to patch: typically 2-4 weeks industry-wide
- Detection time: with DC-5, typically hours to days
- Exploitation window: hours to weeks

**Why Not Fully Mitigated**:
- Zero-day by definition unknown to vendor/defenders
- Cannot prevent code that doesn't yet exist
- All binary code contains potential vulnerabilities

**Risk Acceptance Criteria**:
- ✅ Accept if: AEGIS governance deployed with extreme isolation (air-gap, network segmentation)
- ✅ Accept if: Continuous monitoring and incident response capability exists
- ❌ Do NOT accept if: Critical infrastructure connected without monitoring/isolation

**Residual Risk Statement**: "AEGIS governance runtime may contain unknown vulnerabilities that could be exploited before detection. Mitigation depends on environmental controls (network isolation, monitoring) external to the product."

---

### RR-2: Insider Compromise (High-Privilege User)

**Description**: System administrator with policy/key access deliberately performs unauthorized acts.

**Attack Vector**: Actor-3 (Insider with Elevation)

**Risk Level**: CRITICAL

**Current Mitigations**:
- PC-5 (Policy Signing) — makes tampering detectable (signature fails)
- DC-1 (Audit Logging) — captures all admin actions
- DC-3 (Drift Detection) — alerts on policy changes
- Process: Two-person approval for sensitive changes

**Unmitigable Scenarios**:
- Both admins collude to change policy and cover tracks
- Insider with physical access to audit storage removes evidence
- Root access allows audit log deletion (filesystem-level)

**Why Not Fully Mitigated**:
- Insider has legitimate access by design
- Cannot audit all physical/logical actions
- Determine collusion is NP-hard problem in general case

**Risk Acceptance Criteria**:
- ✅ Accept if: Insider threat program exists (background checks, access logging, compartmentalization)
- ✅ Accept if: Audit storage is immutable (write-once or distributed with consensus)
- ✅ Accept if: Regular surprise audits and controls testing
- ❌ Do NOT accept without compensating controls

**Residual Risk Statement**: "Insider attacks by high-privilege users are partially mitigated by signing, drift detection, and dual approval. Remaining risk mitigated by organizational controls (access restrictions, monitoring, compartmentalization) not in AEGIS product."

**Compensating Controls**:
- Immutable audit storage (WORM, blockchain, geographic replication)
- Surprise controls testing and audits
- Dependency on other attestation systems (e.g., change management, ticketing)
- Regular security training and background checks

---

### RR-3: Supply-Chain Attack on Cryptographic Libraries

**Description**: Dependency libraries (e.g., jwt, cryptography) are compromised with subtle weaknesses.

**Attack Vector**: AV-6.1 (Dependency Poisoning)

**Risk Level**: HIGH

**Current Mitigations**:
- Dependency pinning (exact version, not ranges)
- Software Bill of Materials (SBOM) generation
- Automated vulnerability scanning (Dependabot, Snyk)
- Code review before dependency updates

**Unmitigable Scenarios**:
- Legitimate maintainer account compromised
- Zero-day vulnerability in crypto library (e.g., ED25519 constant-time leak)
- Subtle bias in random number generation that's cryptographically valid but weak

**Why Not Fully Mitigated**:
- Cannot exhaustively review all dependency code
- Supply-chain trust is ultimately based on human judgment
- Cryptographic attacks may be latent (discovered years later)

**Risk Acceptance Criteria**:
- ✅ Accept if: Dependencies reviewed and from trusted sources (NIST, major projects)
- ✅ Accept if: Cryptographic libraries specifically audited (libsodium)
- ✅ Accept if: Automated scanning enabled and updates regular
- ❌ Do NOT accept if: Unknown or unmaintained dependencies used

**Residual Risk Statement**: "AEGIS depends on third-party cryptographic libraries. While we use well-audited libraries (libsodium, OpenSSL) and scan for vulnerabilities, residual risk of supply-chain compromise exists. Mitigation depends on community security and regular updates."

**Continuous Monitoring**:
- Subscribe to security mailing lists (lib-announce, cves)
- Regular dependency update cycle (monthly minimum)
- Cryptanalysis research monitoring for new attacks
- Incident response plan for crypto library compromise

---

### RR-4: Side-Channel Attacks on Policy Evaluation

**Description**: Attacker measures timing/power/electromagnetic emissions to infer policy structure or decision logic.

**Attack Vector**: AV-5.1 (Timing), AV-5.2 (Risk Scoring Side-Channel)

**Risk Level**: MEDIUM

**Current Mitigations**:
- Constant-time policy evaluation (approximately)
- Decision outcome logged openly (attacker can learn from decision)
- Risk score communicated only on approval

**Unmitigable Scenarios**:
- Attacker with network access measures decision latency with microsecond precision
- Attacker with physical proximity measures power consumption of runtime
- Attacker correlates thousands of decision measurements to infer logic

**Why Not Fully Mitigated**:
- Constant-time code is difficult in practice (optimizing compilers interfere)
- Network timing inherently varies (latency, retries)
- Complete elimination requires specialized hardware (constant-time processor)

**Risk Acceptance Criteria**:
- ✅ Accept if: Attacker model doesn't include network/physical access for thousands of measurements
- ✅ Accept if: Policy structure is not extremely sensitive secret (often it's public)
- ❌ Do NOT accept if: Policy contains cryptographic keys or is nation-state sensitive

**Residual Risk Statement**: "Policy evaluation timing and behavior may leak information about policy structure to attackers with extensive measurement capability (network/physical access, statistical analysis). Acceptable if policy is not highly sensitive; not recommended for classified/secret policy."

**Compensating Controls**:
- Network isolation (reduce attacker measurement opportunities)
- Policy is managed openly (not secret by default)
- Frequent policy rotation (reduce window for correlation attacks)
- Anomaly detection on decision patterns (detect attacker probing)

---

### RR-5: Coordinated Failure of All Mitigations

**Description**: Multiple independent mitigations fail simultaneously or are all bypassed by sophisticated attacker.

**Attack Vector**: Any high-risk vector + concurrent failures

**Risk Level**: HIGH (but low probability)

**Scenario**:
1. Zero-day exploit in governance runtime (RR-1)
2. Insider provides attacker with admin credentials (RR-2)
3. Supply-chain compromise introduces crypto weakness (RR-3)
4. Network monitoring disabled for maintenance window
5. Attacker exploits all 4 simultaneously → complete compromise

**Why Not Fully Mitigated**:
- Mitigations are engineered assuming others exist
- Failure of all mitigations simultaneously rare but possible
- Murphy's Law: "If something can go wrong, it will"

**Risk Acceptance Criteria**:
- ✅ Accept if: Mitigations aren't correlated (independent failures unlikely)
- ✅ Accept if: Regular controls testing confirms mitigations function
- ✅ Accept if: Incident response capability exists for total compromise
- ❌ Do NOT accept without defense-in-depth approach

**Residual Risk Statement**: "Multiple independent mitigations designed to prevent compromise. Risk of simultaneous failure of all mitigations considered low due to independence and regular testing. Residual risk managed through continuous monitoring and incident response."

**Continuous Monitoring**:
- Quarterly controls testing (confirm mitigations work)
- Penetration testing (identify control bypasses)
- Tabletop exercises (test incident response)
- Regular security awareness training

---

### RR-6: Determination of Policy Intent vs. Literal Policy

**Description**: Attacker exploits gap between policy author's intent and policy's literal text.

**Attack Vector**: AV-2.1 (Policy Evasion)

**Risk Level**: MEDIUM

**Example**:
- **Intent**: "Analysts may query logs for operational troubleshooting"
- **Literal Policy**: `allow telemetry.query if actor.role == 'analyst'`
- **Exploit**: Analyst queries logs for data exfiltration, claims "operational troubleshooting"

**Why Not Fully Mitigated**:
- Policy language cannot capture human intent perfectly
- Context-dependent interpretation requires human judgment
- Literal vs. intent gap unavoidable in any formal system

**Risk Acceptance Criteria**:
- ✅ Accept if: Decision escalation exists (humans review high-risk decisions)
- ✅ Accept if: Audit logging captures intent/justification
- ✅ Accept if: Regular policy reviews confirm effectiveness
- ❌ Do NOT accept without human-in-the-loop for sensitive capabilities

**Residual Risk Statement**: "Policy language is formal and executable but may not perfectly capture author's intent. Residual risk managed through (1) escalation to human reviewers, (2) audit logging of justifications, (3) behavioral monitoring for abuse."

---

### RR-7: Catastrophic Audit Storage Failure

**Description**: Entire audit trail is lost due to storage failure or disaster.

**Attack Vector**: Not directly attackable, but impacts consequence severity

**Risk Level**: MEDIUM

**Unmitigable Scenarios**:
- Data center destroyed (tornado, earthquake)
- Ransomware encrypts audit storage across all redundant copies
- Bit rot in tape backup; corruption undetected for years

**Current Mitigations**:
- Geographic replication (3+ separate locations)
- Format integrity checking (hash chains)
- Regular disaster recovery drills
- Immutable storage format (WORM)

**Why Not Fully Mitigated**:
- Catastrophic events can affect all replicas
- Perfect protection against all disasters impossible
- Cost-benefit: Extreme replication too expensive for marginal risk reduction

**Risk Acceptance Criteria**:
- ✅ Accept if: Disaster recovery plan tested annually
- ✅ Accept if: Multiple geographically separated replicas
- ✅ Accept if: Alternative audit sources exist (tool logs, infrastructure logs)
- ❌ Do NOT accept without geographic distribution

**Residual Risk Statement**: "Audit storage replicated across 3+ geographies and protected against corruption. Risk of complete audit loss accepted as low and managed through disaster recovery planning and tests."

---

## Risk Acceptance Governance

### Acceptance Criteria

| Risk Level | Acceptance Requirement | Review Frequency | Approval Authority |
|---|---|---|---|
| LOW | Documented in this threat model | Annual | Security Lead |
| MEDIUM | Risk acceptance statement signed by CISO | Annual review, approval | CISO |
| HIGH | Risk acceptance + compensating controls documented | Quarterly review | CISO + Governance Board |
| CRITICAL | Board-level risk acceptance required | Monthly review | Board of Directors |

### Risk Acceptance Process

1. **Identification**: Risk identified during design, testing, or operations
2. **Assessment**: Risk level determined using likelihood×impact matrix
3. **Mitigation Attempt**: Try to mitigate; document why mitigation impossible/infeasible
4. **Documentation**: Residual risk statement written
5. **Compensating Controls**: Identify and document compensating controls
6. **Approval**: Obtain appropriate authority approval
7. **Continuous Monitoring**: Regular review and monitoring of acceptance

### Acceptance Matrix (Likelihood × Impact)

| Impact ↓ Likelihood → | Very Low | Low | Medium | High | Very High |
|---|---|---|---|---|---|
| **Catastrophic** | MEDIUM | HIGH | CRITICAL | CRITICAL | CRITICAL |
| **Major** | LOW | MEDIUM | HIGH | HIGH | CRITICAL |
| **Moderate** | LOW | LOW | MEDIUM | MEDIUM | HIGH |
| **Minor** | LOW | LOW | LOW | LOW | MEDIUM |
| **Negligible** | LOW | LOW | LOW | LOW | LOW |

---

## Continuous Monitoring Plan

### Quarterly Reviews

- Confirm mitigations remain functional
- Review incident logs for new patterns
- Assess threat landscape changes
- Update risk assessments based on new data

### Annual Audits

- Independent security audit
- Penetration testing
- Controls effectiveness review
- Risk acceptance re-approval

### Real-Time Monitoring

- Security event monitoring (SIEM)
- Anomaly detection alerting
- Metrics tracking (incident count, MTTR)
- Trending analysis

---

## Conclusion

AEGIS threat model provides comprehensive defense against identified threats through defense-in-depth layering. Residual risks are documented, accepted, and actively managed through continuous monitoring, compensating controls, and incident response readiness.

**Overall Risk Assessment**: ACCEPTABLE for operational governance of AI systems in enterprise environments with security program and incident response capability.

---

## Next Steps

- [AEGIS_ATM1_INDEX.md](./AEGIS_ATM1_INDEX.md) — Threat model overview and guidance
- [AEGIS_ATM1_MITIGATIONS.md](./AEGIS_ATM1_MITIGATIONS.md) — Mitigation strategies
- Annual threat model review and update cycle

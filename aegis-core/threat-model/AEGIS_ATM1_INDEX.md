# AEGIS™ ATM-1 Threat Model & Security Analysis

**Document**: ATM-1/Index (AEGIS_ATM1_INDEX.md)\
**Version**: 1.0 (Normative)\
**Part of**: AEGIS Adaptive Threat Model (ATM-1)\
**Last Updated**: March 6, 2026

---

## Document Structure

The AEGIS™ Adaptive Threat Model (ATM-1) comprises five normative documents:

1. **AEGIS_ATM1_INDEX.md** (this document) — Overview, threat actor summary, high-level scenarios
2. **AEGIS_ATM1_THREAT_ACTORS.md** — Detailed profiles of 5 threat actor types with capability/motivation analysis
3. **AEGIS_ATM1_ATTACK_VECTORS.md** — 20+ attack vectors organized in 7 attack surface categories
4. **AEGIS_ATM1_SECURITY_PROPERTIES.md** — 5 core security properties, trust boundaries, security assumptions
5. **AEGIS_ATM1_MITIGATIONS.md** — 6 preventive controls, 5 detective controls, 3 responsive controls, and mitigation coverage matrix
6. **AEGIS_ATM1_RESIDUAL_RISKS.md** — Residual risks, risk acceptance criteria, continuous monitoring plan

### Recommended Reading Paths

**For Security Architects**: INDEX → THREAT_ACTORS → ATTACK_VECTORS → SECURITY_PROPERTIES → MITIGATIONS

**For Risk Managers**: INDEX → MITIGATIONS → RESIDUAL_RISKS → SECURITY_PROPERTIES

**For Operators**: THREAT_ACTORS → MITIGATIONS → RESIDUAL_RISKS

**For Compliance/Audit**: SECURITY_PROPERTIES → MITIGATIONS → RESIDUAL_RISKS

---

## Purpose

This document defines threat actors, attack paths, and control strategies for
the AEGIS governance architecture.

Security objective: prevent unauthorized capability execution while preserving
deterministic, auditable governance behavior.

## Protected Assets

Critical assets:

- Policy definitions and policy history.
- Capability registry and grants.
- Governance decision path and decision integrity.
- Audit records and replay evidence.
- Identity credentials and trust metadata.
- Tool Proxy execution channel.

## Threat Actors

| Actor | Motivation | Typical Capability |
|-------|------------|--------------------|
| Malicious external actor | Data theft, disruption | API exploitation, credential abuse |
| Compromised internal agent | Privilege escalation | Policy probing, lateral movement |
| Insider with elevated access | Unauthorized policy changes | Direct config modification |
| Supply-chain attacker | Persistence, covert control | Dependency or artifact tampering |

## Attack Surfaces

- AGP request ingress API.
- Policy management plane.
- Capability grant/revoke plane.
- Tool Proxy call execution path.
- Audit storage and retrieval interfaces.
- CI/CD path for policy and runtime updates.

## Priority Threat Scenarios

### T1: Governance Bypass[^1]

Scenario:

- Agent attempts direct infrastructure call, skipping Governance Engine.

Impact:

- Unauthorized execution without policy/risk evaluation.

Controls:

- Enforce proxy-only network paths.
- Block direct backend routes via firewall/service mesh.
- Runtime detection and denial for bypass signatures.

### T2: Policy Tampering

Scenario:

- Adversary modifies policy files to allow forbidden capabilities.

Impact:

- Systematic privilege escalation.

Controls:

- Signed policies and verified provenance.
- Two-person approval for policy changes.
- Immutable policy change log and automatic diff alerts.

### T3: Identity Spoofing

Scenario:

- Attacker reuses tokens or forges identity claims.

Impact:

- Malicious actions attributed to trusted actors.

Controls:

- Short-lived credentials with audience restriction.
- mTLS between components.
- Nonce/replay protection and strict token validation.

*Empirical precedent:* Documented in Shapira et al. [Agents of Chaos, 2026], Case Study #8 (Owner Identity Spoofing): agents in a live deployment were successfully manipulated into accepting non-owner instructions as owner-level authority, executing unauthorized actions under false identity assumptions. Attribution of malicious actions to trusted identities was confirmed in practice.

### T4: Audit Log Manipulation

Scenario:

- Adversary deletes or edits evidence to hide policy violations.

Impact:

- Loss of accountability and forensics.

Controls:

- Append-only storage and tamper-evident hash chaining.
- Replicated audit sink.
- Periodic reconciliation jobs with integrity proofs.

### T5: Coordinated Low-Risk Abuse

Scenario:

- Multiple agents execute individually low-risk actions that combine into
 high-impact behavior.

Impact:

- Slow-burn exfiltration or distributed policy evasion.

Controls:

- Cross-agent correlation analytics.
- Sliding-window aggregate risk checks.
- Escalation triggers on coordinated patterns.

### T6: Model/Tool Prompt Injection

Scenario:

- Malicious input attempts to coerce agent behavior toward unsafe capability use.
- Attackers use prompt injection and chain-of-thought manipulation attempts to steer action proposals.[^19]

Impact:

- Elevated volume of risky action proposals.

Controls:

- Governance remains out-of-band and deterministic.
- Prompt content is never an authorization source.
- Policy/risk checks remain mandatory before execution.

*Empirical precedent:* Documented in Shapira et al. [Agents of Chaos, 2026], Case Study #12 (Prompt Injection via Broadcast): malicious broadcast messages caused agents in a live deployment to identify and act on injected instructions propagated through shared communication channels. Cross-agent corruption (Case Study #10) was additionally documented as a multi-hop prompt injection variant, in which unsafe practices propagated between agents through knowledge-sharing mechanisms. Both cases confirm that model-layer defenses are insufficient to prevent injection-driven misbehavior at the execution level.

## Empirical and Industrial Precedent

ATM-1's threat scenarios are not hypothetical — they have been documented empirically in live agentic deployments and validated by decades of industrial control systems security practice.

**Contemporary agentic systems:** Shapira et al. [Agents of Chaos, 2026] conducted a two-week red-teaming study of autonomous LLM-powered agents deployed in a live laboratory environment with persistent memory, email accounts, Discord access, file systems, and shell execution. Twenty AI researchers conducted adversarial testing across eleven documented case studies. The study recorded unauthorized compliance with non-owner instructions, sensitive information disclosure, destructive system-level actions, denial-of-service, owner identity spoofing, cross-agent propagation of unsafe practices, and partial system takeover — mapping directly to T1 (Governance Bypass), T3 (Identity Spoofing), T5 (Coordinated Low-Risk Abuse), T6 (Prompt Injection), and the Information Disclosure and Denial of Service categories in the STRIDE mapping above.

Critically, the paper's authors attribute these failures explicitly to the *agentic layer* — the integration of language models with tool use, persistent memory, communication channels, and delegated authority — not to model-level weaknesses. Model alignment was insufficient to prevent the documented harms. The paper calls explicitly for "systematic oversight and realistic red-teaming for agentic systems" and governance protocols addressing accountability when autonomous systems cause harm. This finding directly establishes the architectural enforcement gap that ATM-1 addresses.

**Industrial control systems precedent:** Pearce et al. [Smart I/O, 2020][^5] establish in the industrial control systems domain that enforcement modules positioned between a potentially-compromised controller and the actuators it commands prevent damage regardless of controller state. The core architectural assumption — that the controller cannot be trusted — maps directly to ATM-1's TA-2 threat actor model: the AI agent (controller) may be compromised through prompt injection, adversarial inputs, or supply-chain manipulation; AEGIS's governance gateway (I/O module enforcer) intercepts and evaluates all action proposals before they reach infrastructure (actuators).

Together, these precedents establish that ATM-1's compromised agent assumption (TA-2) and governance-as-architecture approach are grounded in both contemporary agentic systems research and decades of industrial control systems security practice.

---

## STRIDE Mapping

| STRIDE | Example in AEGIS | Primary Controls |
|--------|-------------------|------------------|
| Spoofing | Forged `agent_id` token | Strong identity, mTLS, token validation |
| Tampering | Policy file modification | Signatures, immutable logs, approvals |
| Repudiation | Denied action claim disputes | Audit immutability, trace IDs |
| Information Disclosure | Unauthorized data reads | Capability scoping, deny policies |
| Denial of Service | Flood decision endpoint | Rate limits, queue isolation, backpressure |
| Elevation of Privilege | Bypass governance path | Proxy enforcement, default deny |

## Risk Prioritization

Threats are prioritized using four factors:

- Likelihood of exploitation.
- Operational impact.
- Detectability.
- Mitigation difficulty.

Top risks requiring continuous validation:

1. Governance bypass (critical).
2. Policy tampering (critical).
3. Identity spoofing (high).
4. Coordinated multi-agent abuse (high).

## Required Security Tests

Minimum threat-model test suite:

- Bypass simulation: direct execution path must fail.
- Policy tamper test: unsigned policies must be rejected.
- Identity replay test: expired/reused tokens denied.
- Audit integrity test: tampering attempts detected.
- Coordinated behavior test: aggregate risk escalation triggered.

## Detection and Response

Mandatory detections:

- `governance_bypass_attempt_total`
- `policy_signature_failure_total`
- `identity_validation_failure_total`
- `audit_integrity_mismatch_total`
- `coordinated_risk_escalations_total`

Incident response triggers:

- Any confirmed bypass attempt.
- Repeated policy integrity failures.
- Audit tampering indication.

## Residual Risks

Residual risks remain for:

- Zero-day vulnerabilities in trusted components.
- Insider abuse under legitimate credentials.
- Novel attack chains outside known signatures.

Mitigation for residual risks depends on layered controls and rapid response.

## Legacy Coverage Mapping

The legacy document `AEGIS_Threat_Model.md` is fully incorporated across ATM-1 documents:

| Legacy Section | ATM-1 Coverage |
|---|---|
| Overview / Purpose | `AEGIS_ATM1_INDEX.md` Purpose |
| Security Goals (Action Governance, Capability Isolation, Authority Attribution, Policy Enforcement, Auditability) | `AEGIS_ATM1_SECURITY_PROPERTIES.md` |
| Threat Actors | `AEGIS_ATM1_THREAT_ACTORS.md` |
| Attack Surface | `AEGIS_ATM1_ATTACK_VECTORS.md` Attack Surface Map |
| STRIDE Mapping | `AEGIS_ATM1_INDEX.md` STRIDE Mapping |
| Threat Scenarios (Prompt Injection, Capability Escalation, Policy Manipulation, Governance Bypass) | `AEGIS_ATM1_INDEX.md` Priority Threat Scenarios + `AEGIS_ATM1_ATTACK_VECTORS.md` |
| Federation Signal Poisoning | `AEGIS_ATM1_ATTACK_VECTORS.md` AV-7.3 |
| Risk Prioritization Factors | `AEGIS_ATM1_INDEX.md` Risk Prioritization + `AEGIS_ATM1_RESIDUAL_RISKS.md` Acceptance Matrix |
| Security Guarantees | `AEGIS_ATM1_SECURITY_PROPERTIES.md` |
| Limitations | `AEGIS_ATM1_RESIDUAL_RISKS.md` |

## Future Threat Modeling Work

Planned extensions:

- Formal attack trees.
- Adversarial simulation.
- Runtime anomaly detection tuning based on production baselines.
- Governance reputation systems within the federation network.

[^5]: H. Pearce, S. Pinisetty, P. S. Roop, M. M. Y. Kuo, and A. Ukil, "Smart I/O Modules for Mitigating Cyber-Physical Attacks on Industrial Control Systems," *IEEE Transactions on Industrial Informatics*, vol. 16, no. 7, pp. 4659–4669, July 2020, doi: 10.1109/TII.2019.2945520. See [REFERENCES.md](../../REFERENCES.md).

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*
*AEGIS Initiative — Finnoybu IP LLC*

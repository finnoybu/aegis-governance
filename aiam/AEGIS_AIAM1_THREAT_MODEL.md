# AEGIS AIAM-1: Threat Model

**Document**: AIAM-1/Threat Model (AEGIS_AIAM1_THREAT_MODEL.md)\
**Version**: 0.1 (Draft)\
**Part of**: AEGIS Identity & Access Management for AI Agents\
**Last Updated**: April 10, 2026

---

## 1. Purpose

This chapter defines the threat model for AIAM-1 — the specific threats that an aIAM system must address when governing AI agent identity, intent, authority, delegation, and accountability. These threats are specific to the agent actor class and arise from the properties that distinguish agents from humans and service accounts: dynamic intent, composed action chains, delegated authority, and probabilistic reasoning.

---

## 2. Threat Classes

AIAM-1 identifies eight threat classes. For each threat class, this chapter specifies: the threat description, the AIAM-1 primitives that provide defense, the residual risk not addressed by this specification, and informative cross-references to related threat models.

### 2.1 TC-1: Intent Spoofing

**Description.** An agent produces an intent claim that does not correspond to its actual reasoning or goal. The intent claim declares "routine telemetry query" while the agent's actual purpose (driven by prompt injection or adversarial manipulation) is data exfiltration. The IBAC authorization decision is made against the false intent, not the true purpose.

**AIAM-1 Defenses.**
- Intent-goal alignment validation (AIAM1-INT-010 through AIAM1-INT-012): intent claims are validated against declared goal context. False intent that references an incorrect goal is caught.
- Behavioral consistency analysis (AIAM1-INT-040.1): anomalous intent patterns relative to historical baseline are flagged.
- Action-intent coherence (AIAM1-INT-040.2): action parameters inconsistent with declared intent are detected.
- Outcome verification (AIAM1-INT-040.3): divergence between declared expected outcome and actual result is evidence of spoofing.

**Residual Risk.** A sufficiently sophisticated attacker can craft intent claims that pass all validation checks — the intent claim is consistent with the goal context, consistent with the action parameters, and consistent with historical patterns, but the underlying purpose is still malicious. This is the fundamental limitation of governing systems whose internal reasoning is opaque. Full mitigation requires either verifiable execution traces (not yet feasible for LLMs) or architectural enforcement at the action boundary that does not depend on intent truthfulness (e.g., capability-based denial regardless of intent).

**Informative cross-references.** ATM-1 AV-3.1 (Identity Spoofing), ATM-1 AV-2.1 (Policy Evasion).

---

### 2.2 TC-2: Capability Composition Attacks

**Description.** An agent composes individually authorized capabilities into a sequence that produces an unauthorized effect. Each action in the sequence is independently authorized — the agent holds the required capability grant, the intent claim is valid, the IBAC policy matches — but the aggregate effect exceeds what any single authorization intended to permit. Example: `database.read` + `network.send` = data exfiltration through an authorized channel.

**AIAM-1 Defenses.**
- Capability composition governance (AIAM1-CAP-010 through AIAM1-CAP-012): composed actions are evaluated as first-class governed operations.
- Non-transitivity (AIAM1-CAP-011): authorization for A and authorization for B does not imply authorization for A-then-B.
- Intent dependency chains (AIAM1-INT-030): sub-actions must reference parent intent, enabling holistic evaluation of action sequences.

**Residual Risk.** Composition detection requires knowing that a sequence constitutes a meaningful composed effect. Novel composition patterns not anticipated by policy authors will not be detected until they are discovered through adversarial testing or incident analysis. Composition governance is as strong as the composition policies defined.

**Informative cross-references.** ATM-1 AV-7.1 (Coordinated Low-Risk Abuse), ATM-1 SP-4 (Capability Authorization Binding), ATX-1 TA002 (Exceed Operational Scope).

---

### 2.3 TC-3: Authority Inheritance Exploitation

**Description.** A sub-agent or delegated agent exploits inherited authority to take actions the original principal did not intend. The delegation chain grants authority for purpose X; the sub-agent exercises that authority for purpose Y. Or: the sub-agent discovers that its delegated authority, combined with an independent capability grant, enables an action the delegating agent could not perform.

**AIAM-1 Defenses.**
- Monotonic authority narrowing (AIAM1-DEL-010): delegated authority narrows down the chain.
- Independent vs. delegated authority distinction (AIAM1-DEL-011): independent grants do not widen delegated authority.
- Sub-agent intent validation (AIAM1-INT-031): sub-agent intent claims are validated independently against the sub-agent's own goal context.
- Delegation chain depth limits (AIAM1-DEL-020): bounds the delegation surface.
- Complete principal chain preservation (AIAM1-DEL-004): makes authority inheritance visible and auditable.

**Residual Risk.** The distinction between delegated and independent authority creates a seam: a sub-agent with narrow delegated authority and broad independent authority may produce effects that the delegating principal did not anticipate. The attestation record makes this visible, but detection depends on audit review.

**Informative cross-references.** ATM-1 SP-4 (Capability Authorization Binding — default-deny + explicit grant), ATX-1 TA001 (Violate Authority Boundaries).

---

### 2.4 TC-4: Principal Chain Obscuration

**Description.** An agent or orchestration layer hides or misrepresents the principal on whose behalf an action is taken. The attestation record shows a principal chain that does not reflect the actual delegation relationships. An attacker uses this to take actions without accountability — the record points to a principal who did not authorize the action, or to a principal that doesn't exist.

**AIAM-1 Defenses.**
- Structural impossibility of obscuration (AIAM1-DEL-004): attestation records MUST preserve the complete principal chain.
- Cryptographic signing of attestation records (AIAM1-ATT-020): the governance system signs the attestation, not the agent. The agent cannot forge a principal chain.
- Delegation records (AIAM1-DEL-023): every delegation is an explicit, attested governance event with a documented delegator, delegatee, and authority scope.

**Residual Risk.** If the governance system itself is compromised, attestation records (including principal chains) can be forged. This is addressed by governance system integrity controls outside the scope of AIAM-1 (e.g., infrastructure security, key management, physical security).

**Informative cross-references.** ATM-1 AV-3.2 (Lateral Movement via Privilege Escalation), ATX-1 TA001 (Violate Authority Boundaries).

---

### 2.5 TC-5: Attestation Forgery

**Description.** An attacker produces attestation records that misrepresent actions taken. False attestation records could create the appearance of authorization for actions that were never evaluated, or create false evidence of governance decisions that were never made.

**AIAM-1 Defenses.**
- Cryptographic signing by the enforcement layer (AIAM1-ATT-020): only the governance system can produce valid attestation records.
- Hash-chaining (AIAM1-ATT-011): insertion or modification of records breaks the chain, making tampering detectable.
- Append-only storage (AIAM1-ATT-013): records cannot be deleted or modified.
- Fail-closed audit (AIAM1-ATT-040): actions cannot proceed without attestation.

**Residual Risk.** Signing key compromise allows an attacker to produce valid-looking attestation records. Key management, rotation, and compromise detection are implementation responsibilities outside the scope of AIAM-1 normative requirements.

**Informative cross-references.** ATM-1 AV-1.3 (Replay), ATM-1 AV-1.4 (Token Theft), ATM-1 AV-6.1 (Dependency Poisoning).

---

### 2.6 TC-6: Revocation Evasion

**Description.** An agent continues to act after its credentials, capabilities, or session have been revoked. The agent races against revocation propagation to execute high-impact actions before the revocation takes effect.

**AIAM-1 Defenses.**
- Pre-action revocation (AIAM1-REV-001): revocation prevents the next action, not undoes the last one.
- Propagation latency guarantee (AIAM1-REV-002): bounds the window of vulnerability.
- Kill-switch (AIAM1-REV-020): highest-priority governance operation, non-deferrable.
- Delegation cascade (AIAM1-REV-030 through AIAM1-REV-033): revocation propagates through the delegation chain.

**Residual Risk.** The propagation latency window is a finite vulnerability period. During this window, an agent with cached credentials at a governance node that hasn't received the revocation update may execute actions. The residual risk is bounded by the propagation latency guarantee and can be reduced by minimizing propagation latency.

**Informative cross-references.** ATM-1 RC-2 (Credential Revocation), ATX-1 TA009 (Evade Governance Detection).

---

### 2.7 TC-7: Governance Visibility Exploitation

**Description.** An agent probes the governance enforcement layer to learn what triggers flags or denials, then adapts its behavior to avoid detection. The agent submits probe actions to map the policy boundary, then operates just inside the detected limits. This is the agent-specific analogue of adversarial probing attacks against ML classifiers.

**AIAM-1 Defenses.**
- Attestation of all actions including denials (AIAM1-ATT-001): probe actions are recorded and visible to auditors.
- Behavioral consistency analysis (AIAM1-INT-040.1): a pattern of probe-like actions (varying parameters incrementally to test boundaries) is anomalous and detectable.
- IBAC intent validation: probe actions must still carry intent claims. A rapid sequence of intent claims with incrementally varying parameters but identical goal context is suspicious.

**Residual Risk.** A slow-drip probing attack (one probe per session over weeks) may not trigger behavioral anomaly detection. The residual risk is inversely proportional to the sophistication of the implementation's anomaly detection. Full mitigation requires either real-time adversarial detection (active area of research) or policy designs that are robust to boundary probing (e.g., policies with significant deny-margin around sensitive boundaries).

**Informative cross-references.** ATX-1 TA010 (Act Beyond Interpretation Boundaries), ATM-1 AV-7.3 (Federation Signal Poisoning — analogous probing of trust boundaries).

---

### 2.8 TC-8: Cross-Authority Composition

**Description.** A sub-agent combines delegated authority from principal A with independent authority granted under principal B to produce an effect that neither principal alone authorized. This is the delegated/independent authority seam (see [DELEGATION §5.1](AEGIS_AIAM1_DELEGATION.md#51-authority-source-composition)) elevated to a first-class threat. Unlike TC-2 (capability composition), which concerns sequences of capabilities under a single authority source, TC-8 concerns the mixing of authority sources themselves.

**Example.** Agent X holds:
- Delegated capability `patient.query` from Hospital A's EHR system (principal: Hospital A)
- Independent capability `analytics.export` granted by Research Institute B (principal: Research Institute B)

Composed: query patient records under Hospital A's authority, export results under Research Institute B's authority. Neither principal authorized the cross-boundary data flow. Hospital A authorized the query. Research Institute B authorized the export. The composition creates a HIPAA violation that neither governance domain anticipated.

**AIAM-1 Defenses.**
- Composition governance extended to authority sources (AIAM1-AUTH-024): actions drawing on mixed delegated and independent authority are evaluated as composed actions under AIAM1-CAP-010.
- Principal chain preservation (AIAM1-DEL-004): the attestation record shows both authority sources.
- IBAC policies can match on principal chain composition — deny or escalate actions where the principal chain contains multiple distinct accountable parties.

**Residual Risk.** MEDIUM. Detection depends on policy authors anticipating cross-authority compositions. Novel cross-authority paths not covered by policy will succeed until discovered. The attestation record ensures forensic reconstruction is possible, but prevention requires explicit composition policies for each authority-source pairing.

**Informative cross-references.** ATX-1 TA007 (Manipulate Multi-Agent Systems), ATM-1 AV-7.1 (Coordinated Low-Risk Abuse).

---

## 3. Threat-to-Defense Matrix

| Threat Class | Primary AIAM-1 Defense | Secondary Defense | Residual Risk Level |
|---|---|---|---|
| TC-1: Intent Spoofing | Intent-goal alignment, behavioral analysis | Action-intent coherence, outcome verification | HIGH — fundamental limitation of governing opaque reasoning |
| TC-2: Composition Attacks | Composition governance, non-transitivity | Intent dependency chains | MEDIUM — depends on composition policy completeness |
| TC-3: Authority Inheritance | Monotonic narrowing, delegation depth limits | Independent vs. delegated distinction, intent validation | MEDIUM — seam between delegated and independent authority |
| TC-4: Chain Obscuration | Structural chain preservation, crypto signing | Delegation attestation records | LOW — requires governance system compromise |
| TC-5: Attestation Forgery | Crypto signing, hash-chaining, append-only | Fail-closed audit | LOW — requires signing key compromise |
| TC-6: Revocation Evasion | Pre-action revocation, kill-switch | Propagation latency guarantee, cascade | LOW — bounded by propagation latency |
| TC-7: Visibility Exploitation | Attestation of all actions, behavioral analysis | Intent validation for probes | MEDIUM — slow-drip probing is hard to detect |
| TC-8: Cross-Authority Composition | Composition governance over authority sources (AUTH-024), principal chain preservation | IBAC policies on multi-principal chains | MEDIUM — depends on policy coverage of authority-source pairings |

---

## 4. Normative Requirements

**AIAM1-TM-001.** A conformant implementation MUST explicitly address all eight threat classes defined in this chapter. For each threat class, the implementation MUST identify the mechanisms in this specification that provide defense and MUST document any residual risk not addressed.

**AIAM1-TM-002.** A conformant implementation SHOULD align its threat model documentation with ATX-1 where applicable. ATX-1 cross-references in this chapter are informative; conformance to AIAM-1 does not require adoption of ATX-1.

**AIAM1-TM-003.** Any trust evaluation of agent identity or behavior implemented alongside AIAM-1 MUST comply with the structural separation of security and reputation signals. Trust scores and security decisions MUST NOT be collapsed into a single metric. (Informative: within the AEGIS ecosystem, this is normatively specified in RFC-0004 §5.)

---

## 5. Open Questions

1. **Adversarial intent generation.** As LLMs improve, the quality of spoofed intent claims will improve. Research into intent verification mechanisms (verifiable execution traces, hardware attestation of model execution, cryptographic proofs of reasoning) will be critical for reducing TC-1 residual risk. AIAM-1 v0.2 should track developments in this space.

2. **Composition attack surface enumeration.** Is it possible to enumerate all meaningful capability compositions for a given capability registry? If so, automated composition policy generation could reduce TC-2 residual risk to near zero. This is a formal verification question deferred to v0.2.

3. **Cross-organization threat model.** The current threat model assumes a single-organization deployment. Cross-organization delegation introduces additional threat classes (bilateral trust exploitation, cross-jurisdictional accountability evasion) that require specification in v0.2.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

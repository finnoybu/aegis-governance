# AEGIS™ Governance Architecture
**A Position Statement for the NIST AI Risk Management Framework**

**Document**: 2026-03-aegis-nist-ai-rmf-position-statement.md  
**Version**: 0.1.0 (Draft)  
**Part of**: AEGIS™ Position Papers  
**Date**: March 7, 2026  
**Submitted to**: NIST AI Risk Management Framework  
**Status**: Draft for Public Comment  
**Steward**: Finnoybu IP LLC | AEGIS™ Initiative  

**Repository**: [github.com/finnoybu/aegis-governance](https://github.com/finnoybu/aegis-governance)  
**Constitution**: [aegissystems.app](https://aegissystems.app)

> *Capability without constraint is not intelligence™*

---

## Executive Summary

AEGIS™ (Architectural Enforcement & Governance of Intelligent Systems) is an open governance architecture that addresses a structural gap in current AI risk management practice: the absence of deterministic, execution-time enforcement between AI-generated actions and operational infrastructure.

While the NIST AI Risk Management Framework (AI RMF 1.0) establishes a comprehensive organizational model for AI governance, its GOVERN, MAP, MEASURE, and MANAGE functions are predominantly realized through documentation, policy, and organizational process. AEGIS™ proposes a complementary architectural layer that makes those governance intentions structurally enforceable at runtime.

**Core thesis:** Governance that exists only in documentation cannot refuse an action at the moment it matters. AEGIS™ introduces a constitutional mediation layer that evaluates AI-generated actions against established policy before those actions reach operational systems — converting organizational intent into architectural enforcement.

This position paper maps AEGIS™ architectural components to NIST AI RMF functions, identifies specific gaps the architecture addresses, and proposes AEGIS™ as a reference implementation pattern for execution-time AI governance.

---

## 1. The Governance Gap AEGIS Addresses

The NIST AI RMF correctly identifies governance as a foundational function. The framework's GOVERN function establishes organizational accountability structures, risk tolerances, and policy frameworks. However, the framework acknowledges that implementation mechanisms are organization-specific.

This creates a structural gap in practice: most organizations implement AI governance as a documentation and review discipline rather than an architectural constraint. The result is what practitioners have begun to call "observational governance" — systems that can explain what happened but cannot refuse an action when it matters.

AEGIS™ addresses this gap through four architectural mechanisms:

- A governance runtime that interposes between AI agents and operational infrastructure
- A capability registry that enforces default-deny access to operational resources
- A policy engine that evaluates action proposals deterministically before execution
- An immutable audit trail that records every governance decision with cryptographic integrity

The distinction is precise: AEGIS™ does not replace organizational AI governance. It operationalizes it — converting policy intent into structural enforcement.

---

## 2. Architectural Overview

### 2.1 The Governance Runtime

The AEGIS™ governance runtime sits between AI agent reasoning and external system execution. No AI-generated action may reach operational infrastructure without passing through the governance evaluation pathway.

The runtime enforces what the AEGIS™ Constitution defines as Article III — Deterministic Enforcement: governance decisions must be enforced through system architecture rather than relying solely on AI model behavior.

**Execution flow:**

1. AI Agent submits `ACTION_PROPOSE` to the Governance Gateway
2. Decision Engine evaluates against Capability Registry and Policy Engine
3. Decision returned: `ALLOW`, `DENY`, `ESCALATE`, or `REQUIRE_CONFIRMATION`
4. Only `ALLOW` decisions proceed to the Tool Proxy Layer for execution
5. All decisions recorded to immutable audit log regardless of outcome

### 2.2 Constitutional Governance Principles

The AEGIS™ Constitution establishes eight articles that define architectural requirements, not aspirational guidelines:

- **Article I — Bounded Capability:** default-deny model; actions referencing undefined capabilities are rejected
- **Article II — Authority Verification:** all actions attributable to authenticated actors; anonymous actions rejected
- **Article III — Deterministic Enforcement:** governance enforced architecturally, not by model compliance
- **Article IV — Operational Safety:** destructive or high-impact actions require elevated review or human confirmation
- **Article V — Data Protection:** sensitive data governed by classification policy; least-privilege access enforced
- **Article VI — Governance Transparency:** policies inspectable, version-controlled, and auditable
- **Article VII — Auditability:** append-only, tamper-evident audit records for every governance decision
- **Article VIII — Federation Cooperation:** optional participation in distributed governance intelligence sharing

### 2.3 The AEGIS Governance Protocol (AGP-1)

AGP-1 is a normative protocol specification defining message structures for AI-governance runtime interaction. It standardizes how AI agents propose actions and receive governance decisions, enabling interoperability across AI frameworks and infrastructure platforms.

AGP-1 defines four message types: `ACTION_PROPOSE`, `ACTION_DECIDE`, `ACTION_EXECUTE`, and `ACTION_ESCALATE`, with accompanying JSON schemas for validation.

### 2.4 Threat Model (ATM-1)

The AEGIS™ Adaptive Threat Model (ATM-1) defines five normative documents covering threat actors, 20+ attack vectors across seven attack surface categories, security properties, mitigation controls, and residual risk analysis.

Priority threat scenarios addressed include governance bypass, policy tampering, identity spoofing, audit log manipulation, coordinated low-risk abuse, and prompt injection. The threat model maps to STRIDE and identifies specific detection metrics for each threat category.

---

## 3. Mapping to NIST AI RMF Functions

| NIST AI RMF Function | RMF Category / Sub-Category | AEGIS™ Architectural Component |
|---|---|---|
| GOVERN | GV-1: Policies, Processes, Procedures | AEGIS™ Constitution (8 Articles); Policy Engine; RFC Process |
| GOVERN | GV-2: Accountability | Authority Verification (Article II); Actor Attribution (ATM-1 SP-2); Audit Trail |
| GOVERN | GV-3: Organizational Teams | Governance Federation Network (GFN-1); Escalation pathways |
| GOVERN | GV-4: Organizational Culture | Open RFC process; Community governance principles; Transparency mandate |
| MAP | MP-2: Risk Context | ATM-1 Threat Model; STRIDE mapping; Risk prioritization framework |
| MAP | MP-3: AI Risk Categorization | Capability Registry; Operational impact classification; Destructive action tagging |
| MAP | MP-5: Impact Assessment | Policy Engine risk evaluation; Aggregate risk scoring; Coordinated behavior detection |
| MEASURE | MS-2: AI Risk Measurement | Governance decision metrics; Audit completeness verification; Security property invariants |
| MEASURE | MS-4: Feedback and Learning | Federation signals; Circumvention reports; Governance attestations |
| MANAGE | MG-1: Risk Treatment | Default-deny capability model; Escalation and confirmation pathways; Human-in-the-loop triggers |
| MANAGE | MG-2: Risk Response | DENY / ESCALATE / REQUIRE_CONFIRMATION decisions; Kill-switch equivalent via governance gateway |
| MANAGE | MG-3: Risk Recovery | Immutable audit trail; Decision replay; Hash-chained evidence preservation |
| MANAGE | MG-4: Residual Risk | ATM-1 Residual Risk documentation; Continuous monitoring plan; Zero-day acknowledgment |

### 3.1 Primary Alignment: GOVERN Function

AEGIS™ most directly operationalizes the GOVERN function. The AI RMF's GOVERN function establishes that organizations should "establish policies, processes, and procedures that enable risk management across the organization." AEGIS™ converts those policies into runtime enforcement.

Specific GOVERN sub-categories addressed:

- **GV-1.1:** Policies and procedures are established and communicated — AEGIS™ Constitution provides the constitutional framework; AGP-1 provides the protocol specification
- **GV-1.2:** Roles and responsibilities are established — Authority verification and actor attribution enforce accountability at execution time
- **GV-1.4:** Organizational teams are committed to risk management — Federation network enables cross-organizational governance intelligence sharing
- **GV-2.2:** Accountability is established for AI system outcomes — Every governance decision is attributable to a verified actor with cryptographic proof

### 3.2 Gap Addressed: Execution-Time Enforcement

The AI RMF does not prescribe implementation mechanisms for policy enforcement. AEGIS™ proposes that the GOVERN function is incomplete without a runtime enforcement layer. Documentation of policy is necessary but not sufficient — governance must be architecturally guaranteed.

**AEGIS™ position:** A reference implementation pattern for execution-time governance should be incorporated into AI RMF guidance as a recognized architectural approach, particularly for agentic AI systems with operational infrastructure access.

---

## 4. Addressing Agentic AI Systems

The AI RMF was developed prior to the widespread deployment of agentic AI systems — systems capable of multi-step planning, tool use, and autonomous operational decisions. These systems introduce governance requirements not fully addressed by the current framework.

### 4.1 The Agentic Governance Problem

Agentic AI systems introduce three governance challenges that observational approaches cannot adequately address:

- **Sequential action risk:** individual actions may appear low-risk in isolation but constitute high-impact behavior in aggregate. AEGIS™ addresses this through sliding-window aggregate risk scoring and coordinated behavior detection (ATM-1 Threat Scenario T5).
- **Execution irreversibility:** unlike text generation, operational actions (data deletion, infrastructure modification, financial transactions) may be irreversible. AEGIS™ requires elevated governance review for actions classified as `DESTRUCTIVE` (Article IV).
- **Model reasoning unreliability:** AI models are probabilistic systems subject to hallucination, prompt injection, and reasoning errors. AEGIS™ treats model reasoning as untrusted input, enforcing governance architecturally rather than relying on model compliance (Article III).

### 4.2 AEGIS as Agentic AI Governance Reference Architecture

AEGIS™ proposes that the NIST AI RMF incorporate explicit guidance for agentic AI systems, including:

- Recognition that governance for agentic systems requires execution-time enforcement in addition to organizational process
- A reference architecture pattern for governance runtime interposition between AI agents and operational infrastructure
- Specific guidance on capability-based authorization as a risk management mechanism
- Requirements for audit trail completeness that extends beyond model outputs to include operational action records

---

## 5. Open Framework and Community Contribution

AEGIS™ was publicly released on March 5, 2026 as an open governance architecture under the Apache 2.0 license. The framework is actively seeking public comment and contribution from practitioners, researchers, and standards bodies.

### 5.1 Current Status

| Component | Status |
|---|---|
| Layers 1–3 (Principles, Architecture, Protocol) | Complete at v0.1 |
| AGP-1 Protocol Specification | Normative, v0.1 |
| ATM-1 Threat Model (5 documents) | Normative, v0.1 |
| AEGIS™ Constitution (8 Articles) | Draft v0.1 |
| RFC-0001 Architecture Specification | Complete |
| Layer 4 Reference Runtime (Python) | In active development, targeted Q2 2026 |
| RFC-0002 through RFC-0004 | In progress, targeted Q2 2026 |
| Layer 5 Federation Network | Designed, implementation targeted Q4 2026–Q4 2028 |

### 5.2 Invitation for NIST Engagement

The AEGIS™ Initiative respectfully requests:

- Recognition of execution-time governance runtime architectures as a legitimate and necessary complement to organizational AI governance frameworks
- Incorporation of capability-based authorization and default-deny execution models into AI RMF implementation guidance for agentic systems
- Consideration of AEGIS™ constitutional principles as a reference model for AI governance architecture standards
- Collaboration opportunities to align AEGIS™ specifications with NIST AI RMF subcategory requirements

Public repository and documentation: [github.com/finnoybu/aegis-governance](https://github.com/finnoybu/aegis-governance)
Constitutional reference site: [aegissystems.app](https://aegissystems.app)

---

## 6. Conclusion

AI governance frameworks have made significant progress in establishing organizational accountability structures, risk categorization models, and policy requirements. The NIST AI RMF represents the most comprehensive and broadly adopted of these frameworks.

As AI systems gain operational capability — writing code, interacting with APIs, modifying infrastructure, executing financial transactions — the governance challenge shifts from behavioral alignment to architectural enforcement. Governance that exists only in documentation cannot refuse an action at the moment it matters.

AEGIS™ proposes that the next evolution of AI governance standards must incorporate execution-time enforcement as a first-class requirement. The architecture is open, the specifications are published, and the community is active.

> *Capability without constraint is not intelligence™*

---

## A Note on Development Process

AEGIS™ was developed through active human-AI collaboration, with strategic direction, governance philosophy, and architectural decisions made by human stewards and implemented in partnership with AI tools. We consider this appropriate: a governance framework for AI systems that was itself built through governed, accountable human-AI collaboration is not a contradiction. It is a demonstration of the principle.

---

## References and Resources

- NIST AI Risk Management Framework (AI RMF 1.0) — [nist.gov](https://www.nist.gov/system/files/documents/2023/01/26/NIST_AI_RMF_1.0.pdf)
- AEGIS™ Governance Repository — [github.com/finnoybu/aegis-governance](https://github.com/finnoybu/aegis-governance)
- AEGIS™ Constitution — [aegissystems.app](https://aegissystems.app)
- AEGIS™ Manifesto — [aegis-core/manifesto](https://github.com/finnoybu/aegis-governance/blob/main/aegis-core/manifesto/AEGIS_Manifesto.md)
- AGP-1 Protocol Specification — [aegis-core/protocol](https://github.com/finnoybu/aegis-governance/blob/main/aegis-core/protocol/AEGIS_AGP1_INDEX.md)
- ATM-1 Threat Model — [aegis-core/threat-model](https://github.com/finnoybu/aegis-governance/blob/main/aegis-core/threat-model/AEGIS_ATM1_INDEX.md)
- RFC-0001 Architecture Specification — [rfc/RFC-0001](https://github.com/finnoybu/aegis-governance/blob/main/rfc/RFC-0001-AEGIS-Architecture.md)
- AEGIS™ Announcement (March 2026) — [docs/announcements](https://github.com/finnoybu/aegis-governance/blob/main/docs/announcements/2026-03-05-launch/ANNOUNCEMENT.md)

---

*© 2026 Finnoybu IP LLC. All Rights Reserved.*
*AEGIS™ and "Capability without constraint is not intelligence™" are trademarks of Finnoybu IP LLC.*
*Version 0.1 | Draft for Public Comment | March 2026*

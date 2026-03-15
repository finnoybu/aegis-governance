# AEGIS™ — Related Work and Differentiation

This document positions AEGIS relative to adjacent AI governance frameworks. It is the authoritative source for differentiation claims made throughout the repository and in external publications.

See [REFERENCES.md](../REFERENCES.md) for full citations.

---

## Positioning Statement

AEGIS governs at the **agent action boundary** — post-reasoning, pre-infrastructure execution. This enforcement point is distinct from every major adjacent framework. The governance gap AEGIS addresses is not what AI agents say or how they reason, but what they are structurally permitted to do against operational infrastructure.

---

## SAGA — Security Architecture for Governing AI Agentic Systems[^21]

Syros et al. (2026) present SAGA, a security architecture for governing the **inter-agent communication plane** — establishing trust and identity between agents in multi-agent pipelines. SAGA addresses a real and important problem: how do agents authenticate each other and establish trust across a pipeline?

AEGIS and SAGA are complementary but govern different planes:

- **SAGA** governs agent-to-agent communication
- **AEGIS** governs agent-to-infrastructure actions

A critical architectural distinction: SAGA introduces a single Provider authority as the trust root, creating a centralized trust oracle and a single point of failure for cross-organizational deployments. AEGIS GFN-1 explicitly rejects centralized trust oracles in favor of a decentralized, cryptographically-anchored federation where no single node holds authority over others.

---

## MI9 — An Integrated Runtime Governance Framework for Agentic AI[^23]

Wang et al. (2025) present MI9, a runtime governance framework that applies policy constraints **inside the agent's reasoning loop** — governing the agent's planning and action selection phases during inference.

AEGIS and MI9 are complementary but govern different layers:

- **MI9** operates inside the agent (reasoning layer)
- **AEGIS** operates outside the agent (infrastructure boundary)

An agent governed by MI9 could still invoke infrastructure directly if its execution environment permits it. AEGIS enforces at the architectural boundary regardless of the agent's internal state — making unauthorized action classes structurally unavailable rather than merely discouraged during reasoning. Neither framework subsumes the other; together they form a more complete governance stack.

---

## GaaS — Governance-as-a-Service[^24]

Gaurav, Heikkonen, and Chaudhary (2025) present a Governance-as-a-Service model that applies governance policies as a **post-inference output filtering layer** — governing the language outputs of AI models after reasoning has completed.

AEGIS and GaaS address categorically different failure modes:

- **GaaS** addresses content risk (what the agent says)
- **AEGIS** addresses action risk (what the agent does)

An agent whose output has been filtered by GaaS retains full capacity to invoke tools, call APIs, and modify state through its execution framework. Output filtering does not intercept infrastructure actions. AEGIS enforces at the execution boundary — before any real-world effect occurs — producing an audit record for every governance decision regardless of the agent's output content.

---

## Comparison Table

| Framework | Governance Layer | Enforcement Point | Federation | Immutable Audit | NIST AI RMF |
|-----------|-----------------|-------------------|------------|-----------------|-------------|
| **AEGIS** | Action boundary | Post-reasoning, pre-infrastructure | ✅ Decentralized (GFN-1) | ✅ | ✅ All 4 functions |
| SAGA[^21] | Inter-agent communication | Agent-to-agent messaging | ❌ Centralized Provider | ❌ | ❌ |
| MI9[^23] | Reasoning loop | Inside agent inference | ❌ | ❌ | ❌ |
| GaaS[^24] | Output filtering | Post-inference | ❌ | ❌ | ❌ |

---

## Further Reading

- [AEGIS Constitution](../aegis-core/constitution/AEGIS_Constitution.md) — Article III (Deterministic Enforcement), Article VII (Auditability)
- [AGP-1 Protocol](../aegis-core/protocol/) — Action boundary enforcement specification
- [GFN-1 Federation](../federation/) — Decentralized trust network architecture
- [ATM-1 Threat Model](../aegis-core/threat-model/) — Threat landscape and mitigations

---

## References

[^21]: G. Syros et al., "SAGA: A Security Architecture for Governing AI Agentic Systems," in *Proc. Network and Distributed System Security Symposium (NDSS)*, San Diego, CA, USA, Feb. 2026. [Online]. Available: <https://www.ndss-symposium.org/wp-content/uploads/2026-s869-paper.pdf>. See [REFERENCES.md](../REFERENCES.md).

[^23]: X. Wang et al., "MI9: An Integrated Runtime Governance Framework for Agentic AI," arXiv:2508.03858v4, 2025. [Online]. Available: <https://arxiv.org/pdf/2508.03858>. See [REFERENCES.md](../REFERENCES.md).

[^24]: S. Gaurav, J. Heikkonen, and R. Chaudhary, "Governance-as-a-Service: A Multi-Agent Framework for AI System Compliance and Policy Enforcement," arXiv:2508.18765v2, 2025. [Online]. Available: <https://arxiv.org/pdf/2508.18765>. See [REFERENCES.md](../REFERENCES.md).

---

*Part of: AEGIS™ Documentation*\
*Maintained by: AEGIS™ Initiative*\
*Last Updated: 2026-03-14*

# AEGIS™ References

Canonical bibliography for the AEGIS™ governance framework. All papers cited anywhere in the repository should appear here. Documents cite inline using IEEE footnote style and reference this file for the full entry.

See [CLAUDE.md](CLAUDE.md) for citation format conventions.

---

## Foundational Security Theory

[1] J. P. Anderson, "Computer Security Technology Planning Study," Technical Report ESD-TR-73-51, The MITRE Corporation, Air Force Electronic Systems Division, Hanscom AFB, Bedford, MA, Oct. 1972, Vols. I and II. [Online]. Available: https://csrc.nist.gov/publications/history/ande72.pdf\
**Relevance to AEGIS:** First articulation of the reference monitor — a component that validates all references made by executing programs against those authorized for the subject. The conceptual origin of every enforcement boundary AEGIS inherits. AEGIS's governance gateway is a direct descendant of this concept.

[2] F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security (TISSEC)*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382.\
**Keywords:** Security automata; runtime monitors; enforceable policies; safety policies\
**Relevance to AEGIS:** Establishes the formal theory of security automata and defines which security policies are enforceable through runtime monitoring. AEGIS's deterministic enforcement model and fail-closed posture are grounded in Schneider's proof that only safety policies are inline-enforceable. The AEGIS Constitution's Article III (Deterministic Enforcement) inherits this foundation directly.

---

## Runtime & Architectural Enforcement

[3] S. Hallé and R. Villemaire, "Runtime Enforcement of Web Service Message Contracts with Data," *IEEE Transactions on Services Computing*, vol. 5, no. 2, pp. 192–206, April–June 2012, doi: 10.1109/TSC.2011.10.\
**Keywords:** Web services; runtime monitoring; temporal logic\
**Relevance to AEGIS:** Foundational runtime contract enforcement pattern. The ACTION_PROPOSE → ACTION_DECIDE → ACTION_EXECUTE message flow follows the transparent enforcement pattern established here for web service contracts, adapted for agentic AI governance.

[4] S. Rasthofer, S. Arzt, E. Lovat, and E. Bodden, "DroidForce: Enforcing Complex, Data-centric, System-wide Policies in Android," *2014 Ninth International Conference on Availability, Reliability and Security (ARES)*, Fribourg, Switzerland, 2014, pp. 40–49, doi: 10.1109/ARES.2014.13.\
**Keywords:** Android; policy; system-wide enforcement; data flow; data-centric\
**Relevance to AEGIS:** Establishes the centralized Policy Decision Point (PDP) + decentralized Policy Enforcement Points (PEPs) architectural pattern that AEGIS adopts. The centralized governance engine (AGP-1) mirrors DroidForce's PDP; AEGIS gates function as distributed PEPs.

[5] H. Pearce, S. Pinisetty, P. S. Roop, M. M. Y. Kuo, and A. Ukil, "Smart I/O Modules for Mitigating Cyber-Physical Attacks on Industrial Control Systems," *IEEE Transactions on Industrial Informatics*, vol. 16, no. 7, pp. 4659–4669, July 2020, doi: 10.1109/TII.2019.2945520.\
**Keywords:** Cyber-physical attacks; industrial control systems; runtime enforcement; security\
**Relevance to AEGIS:** Boundary enforcement between controller and infrastructure directly informs AEGIS gate positioning. Establishes the compromised controller threat model — AEGIS applies this to AI agents (compromised agent assumption). The I/O module pattern is the physical analogue of the AEGIS governance gateway.

[6] S. Majumdar et al., "ProSAS: Proactive Security Auditing System for Clouds," *IEEE Transactions on Dependable and Secure Computing*, vol. 19, no. 4, pp. 2517–2534, July–Aug. 2022, doi: 10.1109/TDSC.2021.3062204.\
**Keywords:** Security auditing; runtime enforcement; cloud security; proactive auditing; continuous auditing; OpenStack\
**Relevance to AEGIS:** Proactive, continuous security auditing in cloud environments validates AEGIS's always-on governance posture. ProSAS's probabilistic runtime enforcement complements AEGIS's deterministic enforcement model and informs the audit system design.

[7] A. Baird, A. Panda, H. Pearce, S. Pinisetty, and P. Roop, "Scalable Security Enforcement for Cyber Physical Systems," *IEEE Access*, vol. 12, pp. 14385–14410, 2024, doi: 10.1109/ACCESS.2024.3357714.\
**Keywords:** Cyber-physical systems; security; runtime enforcement; synchronous programming\
**Relevance to AEGIS:** Compositional enforcement across heterogeneous CPS validates AEGIS's federated governance model. Demonstrates scalable enforcement without modifying underlying applications — a core AEGIS design constraint.

[8] K. Arunachalam, A. Kayyidavazhiyil, and P. Santikellur, "POLYNIX: A Hybrid Policy Enforcement Framework for Zero-Trust Security in Virtualized Systems," *2026 IEEE 23rd Consumer Communications & Networking Conference (CCNC)*, Las Vegas, NV, USA, 2026, doi: 10.1109/CCNC65079.2026.11366307.\
**Keywords:** Zero-trust; hybrid policy enforcement; virtualized systems; OPA; Tetragon\
**Relevance to AEGIS:** Validates AEGIS's centralized decision + distributed enforcement model. POLYNIX demonstrates <1% CPU overhead and <2s policy propagation at scale — directly supports AEGIS performance claims. Hybrid centralized OPA + distributed Tetragon maps to AGP-1 + AEGIS gates.

---

## Model-Layer AI Governance

[9] P. Christiano, J. Leike, T. B. Brown, M. Martic, S. Legg, and D. Amodei, "Deep Reinforcement Learning from Human Preferences," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2017. arXiv:1706.03741. [Online]. Available: https://arxiv.org/abs/1706.03741\
**Keywords:** Reinforcement learning from human feedback; RLHF; human preferences; reward learning\
**Relevance to AEGIS:** Origin paper for RLHF. Cited alongside Constitutional AI [10] to establish the model-layer alignment lineage that AEGIS is complementary to. AEGIS positioning documents distinguish RLHF (human feedback) from Constitutional AI (AI feedback) — this paper establishes the RLHF definition.

[10] Y. Bai et al., "Constitutional AI: Harmlessness from AI Feedback," arXiv:2212.08073, Dec. 2022. [Online]. Available: https://arxiv.org/abs/2212.08073\
**Keywords:** Constitutional AI; RLAIF; AI alignment; harmlessness; reinforcement learning from AI feedback\
**Relevance to AEGIS:** Establishes Constitutional AI (RLAIF) as a distinct model-layer alignment technique, differentiated from RLHF. Used in AEGIS positioning: Constitutional AI governs AI reasoning at training time (probabilistic); AEGIS governs AI execution at runtime (deterministic). The terminology distinction in AEGIS documents (RLHF ≠ Constitutional AI) is grounded in this paper.

[11] W. T. Agbemabiese, "Toward Constitutional Autonomy in AI Systems: A Theoretical Framework for Aligned Agentic Intelligence," *IEEE Access*, vol. 14, pp. 11385–11402, 2026, doi: 10.1109/ACCESS.2026.3654907.\
**Keywords:** Agentic systems; AI alignment; AI governance; artificial general intelligence; constitutional AI; long-horizon autonomy; runtime validation; sociotechnical validation; theoretical framework\
**Relevance to AEGIS:** Model-layer governance complement to AEGIS's architectural-layer approach. Constitutional Autonomy governs AI reasoning through attention mechanism modification; AEGIS governs AI execution at the architectural boundary. Together they form a defense-in-depth governance stack. See [docs/outreach/](docs/outreach/) and [Discussion #39](https://github.com/finnoybu/aegis-governance/discussions/39).

[12] N. Shapira et al., "Agents of Chaos," arXiv:2602.20021, Feb. 2026. [Online]. Available: https://arxiv.org/abs/2602.20021\
**Keywords:** Agentic AI; red-teaming; autonomous agents; LLM safety; tool use; multi-agent systems\
**Relevance to AEGIS:** Red-teaming study of autonomous LLM agents with persistent memory, email, file system, and shell access — documents eleven case studies of governance failures in agentic systems. Directly motivates AEGIS's architectural enforcement posture: agents with real-world tool access require deterministic governance boundaries, not just alignment training.

---

## Standards & Frameworks

[13] National Institute of Standards and Technology, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1, Jan. 2023. [Online]. Available: https://www.nist.gov/itl/ai-risk-management-framework\
**Relevance to AEGIS:** Primary standards framework context for AEGIS. AEGIS submitted an unsolicited position paper proposing execution-time governance as a first-class AI RMF implementation pattern (March 7, 2026). See [docs/position-papers/nist/](docs/position-papers/nist/).

[14] Open Policy Agent Project, "Open Policy Agent," The Linux Foundation, 2016–present. [Online]. Available: https://www.openpolicyagent.org\
**Relevance to AEGIS:** Proven policy engine pattern referenced in AGP-1 and AEGIS_Reference_Architecture.md. POLYNIX [8] validates OPA at scale (<1% CPU overhead, <2s policy propagation), directly supporting AEGIS's policy engine design decisions.

---

## How to Cite

Add new references sequentially at the end of the appropriate section. Use IEEE format for formal papers; adapted format for standards, web resources, and software (see [CLAUDE.md — Citation Format](CLAUDE.md)).

When citing in a document:
1. Add an inline footnote at point of use: `[^N]`
2. Define the footnote at the document bottom: `[^N]: Full citation. See [REFERENCES.md](../../REFERENCES.md).`
3. Ensure the paper appears in this file

---

**Part of**: AEGIS™ Documentation\
**Maintained by**: AEGIS™ Initiative\
**Last Updated**: 2026-03-13

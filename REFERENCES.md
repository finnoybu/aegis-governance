# AEGIS™ References

Canonical bibliography for the AEGIS™ governance framework. All papers cited anywhere in the repository should appear here. Documents cite inline using IEEE footnote style and reference this file for the full entry.

See [CLAUDE.md](CLAUDE.md) for citation format conventions.

---

## Foundational Security Theory

[1] J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. [Online]. Available: <https://csrc.nist.gov/files/pubs/conference/1998/10/08/proceedings-of-the-21st-nissc-1998/final/docs/early-cs-papers/ande72.pdf>\
**Relevance to AEGIS:** First articulation of the reference monitor — a component that validates all references made by executing programs against those authorized for the subject. The conceptual origin of every enforcement boundary AEGIS inherits. AEGIS's governance gateway is a direct descendant of this concept.

[22] J. H. Saltzer and M. D. Schroeder, "The protection of information in computer systems," *Proc. IEEE*, vol. 63, no. 9, pp. 1278–1308, Sep. 1975, doi: 10.1109/PROC.1975.9939. [Online]. Available: <https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1451869>\
**Keywords:** Access control; least privilege; fail-safe defaults; complete mediation; open design; separation of privilege; security design principles\
**Relevance to AEGIS:** Foundational enumeration of eight security design principles that AEGIS instantiates architecturally. Four principles map directly to AGP-1: (1) Fail-safe defaults → capability registry is empty by default; all undefined actions denied. (2) Complete mediation → every agent action passes through the governance gateway without exception. (3) Least privilege → capability grants are explicit, minimal, and scoped to specific action types and resource targets. (4) Open design → AEGIS published under Apache 2.0; security properties do not depend on obscurity. Together with Anderson [1], this paper establishes the theoretical security foundation AEGIS inherits. Anderson defines the enforcement boundary; Saltzer & Schroeder define the principles governing what that boundary enforces.

[2] F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security (TISSEC)*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382.\
**Keywords:** Security automata; runtime monitors; enforceable policies; safety policies\
**Relevance to AEGIS:** Establishes the formal theory of security automata and defines which security policies are enforceable through runtime monitoring. AEGIS's deterministic enforcement model and fail-closed posture are grounded in Schneider's proof that only safety policies are inline-enforceable. The AEGIS Constitution's Article III (Deterministic Enforcement) inherits this foundation directly. Schneider also proves that composition of security automata produces the conjunction of their enforced policies — enforcing multiple automata in tandem enforces all of their policies simultaneously. This is the formal justification for AEGIS's multi-gate enforcement architecture: each gate enforces its own policy, and the composed system enforces all of them.

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
**Relevance to AEGIS:** Proactive, continuous security auditing in cloud environments validates AEGIS's always-on governance posture. ProSAS's probabilistic runtime enforcement complements AEGIS's deterministic enforcement model and informs the audit system design.\
**Cited in:** aegis-core/overview/AEGIS_System_Overview.md

[7] A. Baird, A. Panda, H. Pearce, S. Pinisetty, and P. Roop, "Scalable Security Enforcement for Cyber Physical Systems," *IEEE Access*, vol. 12, pp. 14385–14410, 2024, doi: 10.1109/ACCESS.2024.3357714.\
**Keywords:** Cyber-physical systems; security; runtime enforcement; synchronous programming\
**Relevance to AEGIS:** Compositional enforcement across heterogeneous CPS validates AEGIS's federated governance model. Demonstrates scalable enforcement without modifying underlying applications — a core AEGIS design constraint.

[8] K. Arunachalam, A. Kayyidavazhiyil, and P. Santikellur, "POLYNIX: A Hybrid Policy Enforcement Framework for Zero-Trust Security in Virtualized Systems," *2026 IEEE 23rd Consumer Communications & Networking Conference (CCNC)*, Las Vegas, NV, USA, 2026, doi: 10.1109/CCNC65079.2026.11366307.\
**Keywords:** Zero-trust; hybrid policy enforcement; virtualized systems; OPA; Tetragon\
**Relevance to AEGIS:** Validates AEGIS's centralized decision + distributed enforcement model. POLYNIX demonstrates <1% CPU overhead and <2s policy propagation at scale — directly supports AEGIS performance claims. Hybrid centralized OPA + distributed Tetragon maps to AGP-1 + AEGIS gates.

---

## Model-Layer AI Governance

[9] P. Christiano, J. Leike, T. B. Brown, M. Martic, S. Legg, and D. Amodei, "Deep Reinforcement Learning from Human Preferences," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2017. arXiv:1706.03741. [Online]. Available: <https://arxiv.org/abs/1706.03741>\
**Keywords:** Reinforcement learning from human feedback; RLHF; human preferences; reward learning\
**Relevance to AEGIS:** Origin paper for RLHF. Cited alongside Constitutional AI [10] to establish the model-layer alignment lineage that AEGIS is complementary to. AEGIS positioning documents distinguish RLHF (human feedback) from Constitutional AI (AI feedback) — this paper establishes the RLHF definition.\
**Cited in:** aegis-core/overview/AEGIS_System_Overview.md

[10] Y. Bai et al., "Constitutional AI: Harmlessness from AI Feedback," arXiv:2212.08073, Dec. 2022. [Online]. Available: <https://arxiv.org/abs/2212.08073>\
**Keywords:** Constitutional AI; RLAIF; AI alignment; harmlessness; reinforcement learning from AI feedback\
**Relevance to AEGIS:** Establishes Constitutional AI (RLAIF) as a distinct model-layer alignment technique, differentiated from RLHF. Used in AEGIS positioning: Constitutional AI governs AI reasoning at training time (probabilistic); AEGIS governs AI execution at runtime (deterministic). The terminology distinction in AEGIS documents (RLHF ≠ Constitutional AI) is grounded in this paper.\
**Cited in:** aegis-core/overview/AEGIS_System_Overview.md

[11] W. T. Agbemabiese, "Toward Constitutional Autonomy in AI Systems: A Theoretical Framework for Aligned Agentic Intelligence," *IEEE Access*, vol. 14, pp. 11385–11402, 2026, doi: 10.1109/ACCESS.2026.3654907.\
**Keywords:** Agentic systems; AI alignment; AI governance; artificial general intelligence; constitutional AI; long-horizon autonomy; runtime validation; sociotechnical validation; theoretical framework\
**Relevance to AEGIS:** Model-layer governance complement to AEGIS's architectural-layer approach. Constitutional Autonomy governs AI reasoning through attention mechanism modification; AEGIS governs AI execution at the architectural boundary. Together they form a defense-in-depth governance stack. See [docs/outreach/](docs/outreach/) and [Discussion #39](https://github.com/aegis-initiative/aegis-governance/discussions/39).\
**Cited in:** aegis-core/overview/AEGIS_System_Overview.md

[12] N. Shapira et al., "Agents of Chaos," arXiv:2602.20021, Feb. 2026. [Online]. Available: <https://arxiv.org/abs/2602.20021>\
**Keywords:** Agentic AI; red-teaming; autonomous agents; LLM safety; tool use; multi-agent systems\
**Relevance to AEGIS:** Red-teaming study of autonomous LLM agents with persistent memory, email, file system, and shell access — documents eleven case studies of governance failures in agentic systems. Directly motivates AEGIS's architectural enforcement posture: agents with real-world tool access require deterministic governance boundaries, not just alignment training.

---

## Standards & Frameworks

[13] National Institute of Standards and Technology, "Artificial Intelligence Risk Management Framework (AI RMF 1.0)," NIST AI 100-1, U.S. Department of Commerce, Washington, DC, Jan. 2023, doi: 10.6028/NIST.AI.100-1. [Online]. Available: <https://doi.org/10.6028/NIST.AI.100-1>\
**Relevance to AEGIS:** Primary standards framework context for AEGIS. AEGIS submitted an unsolicited position paper proposing execution-time governance as a first-class AI RMF implementation pattern (March 7, 2026). See [docs/position-papers/nist/](docs/position-papers/nist/).\
**Cited in:** aegis-core/overview/AEGIS_System_Overview.md, docs/architecture/SYSTEM_PRINCIPLES.md

[14] Open Policy Agent Project, "Open Policy Agent," The Linux Foundation, 2016–present. [Online]. Available: <https://www.openpolicyagent.org>\
**Relevance to AEGIS:** Proven policy engine pattern referenced in AGP-1 and AEGIS_Reference_Architecture.md. POLYNIX [8] validates OPA at scale (<1% CPU overhead, <2s policy propagation), directly supporting AEGIS's policy engine design decisions.

[15] European Parliament and Council of the European Union, "Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)," *Official Journal of the European Union*, vol. 67, OJ L, 12 Jul. 2024. [Online]. Available: <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689>\
**Relevance to AEGIS:** Primary EU regulatory framework for AI. While NIST AI RMF [13] is the technical governance framework AEGIS is built against, the EU AI Act is the regulatory environment AEGIS-governed systems must satisfy. Architectural enforcement at runtime (AEGIS's posture) directly supports mandatory conformity requirements under the Act. Most relevant to whitepaper, sponsor copy, and regulatory alignment documentation for EU-market enterprises and public institutions.\
**Cited in:** aegis-core/overview/AEGIS_System_Overview.md, docs/architecture/SYSTEM_PRINCIPLES.md

[16] International Organization for Standardization and International Electrotechnical Commission, "Information technology — Artificial intelligence — Management system," ISO/IEC 42001:2023(E), Geneva, Switzerland, Dec. 2023.\
**Relevance to AEGIS:** The world's first AI management system standard — defines what an organization's AI management system must do. AEGIS provides the architectural enforcement layer that makes ISO/IEC 42001 requirements technically auditable and deterministically enforceable at runtime. Clause mapping: §5.2 (AI policy) → AEGIS Doctrine layer; §6.1.2/6.1.3 (risk assessment/treatment) → ATM-1; §6.1.4 (AI system impact assessment) → AGP-1 ESCALATE/REQUIRE_CONFIRMATION; §8.1 (operational control) → AGP-1 runtime enforcement; §9.1/9.2 (monitoring and audit) → AEGIS audit trail and query interface; Annex A (reference controls) → AEGIS capability registry and policy engine. ISO/IEC 42001 itself uses STRIDE for threat modeling across the AI lifecycle — the same framework as ATM-1. Together with NIST AI RMF [13] and the EU AI Act [15], these three form the governance triad AEGIS implements: risk framework (NIST) + regulatory obligation (EU Act) + management system standard (ISO/IEC 42001).\
**Cited in:** docs/architecture/SYSTEM_PRINCIPLES.md

[17] S. Rose, O. Borchert, S. Mitchell, and S. Connelly, "Zero Trust Architecture," National Institute of Standards and Technology, Gaithersburg, MD, NIST Special Publication 800-207, Aug. 2020, doi: 10.6028/NIST.SP.800-207. [Online]. Available: <https://doi.org/10.6028/NIST.SP.800-207>\
**Keywords:** Zero trust architecture; ZTA; identity verification; dynamic policy; microsegmentation; least privilege\
**Relevance to AEGIS:** Canonical definitional reference for zero-trust architecture. AEGIS implements the four core ZTA tenets from §2 directly: (1) all resources must be authenticated before access is granted → AGP-1 actor identity requirement; (2) access is determined by dynamic policy → AGP-1 capability registry and policy engine; (3) all communication is secured regardless of network location → AGP-1 mTLS requirement; (4) all resource access is logged and inspected → AEGIS immutable audit trail. The §3 logical components model (policy engine, policy administrator, policy enforcement point) maps directly to the AGP-1 architecture. POLYNIX [8] validates these ZTA principles empirically; SP 800-207 is the definitional reference reviewers expect to see cited alongside POLYNIX. Public domain — may be quoted directly.

[18] B. Campbell, J. Bradley, N. Sakimura, and T. Lodderstedt, "OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens," RFC 8705, Internet Engineering Task Force, Feb. 2020, doi: 10.17487/RFC8705. [Online]. Available: <https://www.rfc-editor.org/rfc/rfc8705>\
**Keywords:** OAuth 2.0; mTLS; certificate-bound tokens; client authentication; `cnf` claim; token binding\
**Relevance to AEGIS:** Normative specification for AGP-1's combined JWT + mTLS authentication model. RFC 8705 defines how a client certificate at the TLS layer is cryptographically bound to an access token via the `cnf` (confirmation) claim — the token can only be used by the client holding the corresponding private key. This binding directly closes ATM-1's T3 (Identity Spoofing) and AV-1.4 (Token/Credential Theft) vectors: an intercepted token is useless without the certificate. RFC 7519 (JWT format) is the secondary reference if a reader needs the JWT structure definition; RFC 8705 is the primary citation wherever AGP-1 authentication is invoked.

[20] M. Sporny, A. Guy, M. Sabadello, and D. Reed, "Decentralized Identifiers (DIDs) v1.0: Core architecture, data model, and representations," W3C Recommendation, 19 Jul. 2022. [Online]. Available: <https://www.w3.org/TR/2022/REC-did-core-20220719/>\
**Keywords:** Decentralized identifiers; DID; self-sovereign identity; verifiable credentials; cryptographic identity; W3C\
**Relevance to AEGIS:** Normative specification for the decentralized identifier format underpinning GFN-1 node identity (`did:aegis:<network>:<node-id>`). DIDs provide the cryptographic identity foundation that enables federation nodes to publish signed governance signals that consuming nodes can verify without a central authority. Combined with RFC 8705 [18], DIDs close ATM-1's T3 (Identity Spoofing) vector at the federation layer.

[31] Council of Europe, *Framework Convention on Artificial Intelligence and Human Rights, Democracy and the Rule of Law*, Council of Europe Treaty Series (CETS) No. 225, Opened for signature, Vilnius, Lithuania, 5 Sep. 2024. [Online]. Available: <https://rm.coe.int/1680afae3c>\
**Keywords:** AI governance; human rights; democracy; rule of law; international treaty; lifecycle oversight; transparency; auditability; risk management\
**Relevance to AEGIS:** The first legally binding international treaty dedicated specifically to AI governance. Article 3 §1(b) establishes that parties may address private-sector AI risks either by applying the convention's obligations directly or by "taking other appropriate measures to fulfil the obligation" — the foundational framing for AEGIS's positioning as an architectural conformance pathway. The convention requires transparency, auditability, risk management, and effective oversight throughout AI system lifecycles, all of which AEGIS's deterministic enforcement architecture directly satisfies. Signatories include the EU, UK, Ukraine, Canada, Israel, and the United States (negotiations began September 2022 under the Council of Europe's Committee on AI). EU Parliament consent vote confirmed March 11, 2026 (455 in favour, 101 against, 74 abstentions); EP press release archived at `resources/1773236648570.pdf`. **Primary citation for the "other appropriate measures" conformance flexibility; note that "equivalent protection by other means" in the EP press release is a paraphrase of Article 3 §1(b) — use treaty language in formal documents.**

[32] European Parliament, "Parliament backs EU signature of Framework Convention on Artificial Intelligence," Press Release 20260306IPR37524, 11 Mar. 2026. [Online]. Available: <https://www.europarl.europa.eu/news/en/press-room/20260306IPR37524/parliament-backs-eu-signature-of-framework-convention-on-artificial-intelligence>\
**Keywords:** Council of Europe; Framework Convention on AI; EU signature; European Parliament; consent vote; ratification\
**Relevance to AEGIS:** Secondary source for the ratification narrative. Confirms Parliament's consent vote (455 in favour, 101 against, 74 abstentions) on March 11, 2026 for the EU's signature of the Framework Convention [31]. Source of the "equivalent protection by other means" paraphrase of Article 3 §1(b) — useful for positioning copy but not a substitute for the treaty text in formal citations. Confirms signatory states: EU, UK, Ukraine, Canada, Israel, United States. Source document archived at `resources/1773236648570.pdf`.

---

## AI Agent Governance Frameworks

[21] G. Syros et al., "SAGA: A Security Architecture for Governing AI Agentic Systems," in *Proc. Network and Distributed System Security Symposium (NDSS)*, San Diego, CA, USA, Feb. 2026. [Online]. Available: <https://www.ndss-symposium.org/wp-content/uploads/2026-s869-paper.pdf>\
**Keywords:** AI agents; multi-agent systems; security architecture; agent governance; provider trust; communication plane\
**Relevance to AEGIS:** Primary architectural differentiation target. SAGA governs the inter-agent communication plane — trust and identity between agents in a multi-agent pipeline. AEGIS governs the agent-to-infrastructure action plane — what agents can do against operational systems. SAGA introduces a single Provider authority as trust root, creating a cross-organization single point of failure. AEGIS GFN-1 explicitly rejects centralized trust oracles in favor of a decentralized trust-scored federation. Complementary scope; distinct trust model.\
**Cited in:** docs/RELATED_WORK.md

[23] X. Wang et al., "MI9: An Integrated Runtime Governance Framework for Agentic AI," arXiv:2508.03858v4, 2025. [Online]. Available: <https://arxiv.org/pdf/2508.03858>\
**Keywords:** Agentic AI; runtime governance; agent intelligence protocol; multi-agent systems; LLM governance\
**Relevance to AEGIS:** Differentiation target. MI9 governs the internal reasoning loop of AI agents — applying policy constraints during the agent's planning and action selection phases. AEGIS governs the infrastructure boundary — what agents can do against operational systems post-reasoning. MI9 and AEGIS address complementary layers: MI9 operates inside the agent; AEGIS operates at the agent-infrastructure boundary. Neither subsumes the other; together they form a more complete governance stack.\
**Cited in:** docs/RELATED_WORK.md

[24] S. Gaurav, J. Heikkonen, and R. Chaudhary, "Governance-as-a-Service: A Multi-Agent Framework for AI System Compliance and Policy Enforcement," arXiv:2508.18765v2, 2025. [Online]. Available: <https://arxiv.org/pdf/2508.18765>\
**Keywords:** AI governance; multi-agent systems; compliance; policy enforcement; governance-as-a-service; LLM\
**Relevance to AEGIS:** Differentiation target. GaaS applies governance policies as a post-inference filtering layer operating on AI outputs. AEGIS governs at the action boundary — pre-infrastructure execution — before any real-world effect occurs. GaaS addresses content risk; AEGIS addresses action risk. An agent whose output has been filtered by GaaS can still invoke tools, call APIs, and modify state through its execution framework. The two approaches are complementary but address categorically different failure modes.\
**Cited in:** docs/RELATED_WORK.md

[25] S. Rodriguez Garzon et al., "AI Agents with Decentralized Identifiers and Verifiable Credentials," arXiv:2511.02841v2, 2025. [Online]. Available: <https://arxiv.org/abs/2511.02841>\
**Keywords:** AI agents; decentralized identifiers; verifiable credentials; self-sovereign identity; agent identity; trust\
**Relevance to AEGIS:** Differentiation target. LOKA establishes cryptographic identity for AI agents using DIDs and Verifiable Credentials — a necessary component of accountable governance — but does not specify a governance protocol for agent actions. AEGIS incorporates DID-based identity as the foundation of its GFN-1 authentication layer and extends it with constitutional enforcement, capability authorization, and federated governance. LOKA answers "who is this agent?"; AEGIS answers "what is this agent allowed to do?"

[28] Various authors, "A survey of agentic AI and cybersecurity: Challenges, opportunities and use-case prototypes," arXiv:2601.05293v1, 2026. [Online]. Available: <https://arxiv.org/abs/2601.05293>\
**Keywords:** Agentic AI; cybersecurity; autonomous agents; LLM security; threat landscape; use cases\
**Relevance to AEGIS:** Landscape survey documenting the intersection of agentic AI and cybersecurity as of early 2026. Provides context for the governance gap AEGIS addresses — agentic AI deployment has materially outpaced the development of governance infrastructure suited to the action layer. Cited alongside Chan et al. (AI Agent Index) [29] to establish the scale and urgency of the problem AEGIS solves.

[29] R. Chan et al., "The 2025 AI Agent Index," arXiv:2602.17753v1, 2025. [Online]. Available: <https://arxiv.org/abs/2602.17753>\
**Keywords:** AI agents; agentic AI; agent index; deployment survey; autonomous systems; LLM agents\
**Relevance to AEGIS:** Quantitative evidence of agentic AI proliferation at scale. Documents the order-of-magnitude growth in production autonomous agent deployments across financial services, healthcare, software development, and security operations — directly establishing the scale and urgency of the governance gap AEGIS addresses. Cited alongside the Agentic AI & Cybersecurity Survey [28] and Shapira et al. [Agents of Chaos] to ground the paper's opening argument in measurable real-world deployment reality.

[30] Z. Engin and N. Hand, "Toward Adaptive Categories: Dimensional Governance for Agentic AI," arXiv:2505.11579v2, 2025. [Online]. Available: <https://arxiv.org/pdf/2505.11579>\
**Keywords:** AI governance; agentic AI; dimensional governance; adaptive categories; policy frameworks; autonomous systems\
**Relevance to AEGIS:** Proposes a dimensional governance framework for agentic AI — categorizing governance requirements across multiple axes rather than binary compliant/non-compliant classifications. Potentially relevant to AEGIS's four-outcome decision model (ALLOW, DENY, ESCALATE, REQUIRE_CONFIRMATION) as an instance of dimensional rather than binary governance. Retain if cited in repo documentation; drop if not.

---

## Distributed Trust & Reputation

[26] A. Jøsang, R. Ismail, and C. Boyd, "A survey of trust and reputation systems for online service provision," *Decision Support Systems*, vol. 43, no. 2, pp. 618–644, Mar. 2007, doi: 10.1016/j.dss.2005.05.019. [Online]. Available: <https://folk.universitetetioslo.no/josang/papers/JIB2007-DSS.pdf>\
**Keywords:** Trust; reputation systems; online services; trust metrics; subjective logic; computational trust\
**Relevance to AEGIS:** Foundational survey of trust and reputation modeling for distributed systems. Supports GFN-1's trust scoring model — specifically the principle that trust should be weighted by recency of evidence, not only lifetime record. The temporal decay component (λ=0.01, half-life ≈69 days, GFN-1 §3.8) is consistent with trust modeling approaches documented here where staleness of evidence is a legitimate and designed input to trust evaluation.

[27] H. Shuhan et al., "Decentralised identity federations using blockchain," *Int. J. Inf. Secur.*, 2024, doi: 10.1007/s10207-024-00864-6. [Online preprint]. Available: <https://arxiv.org/pdf/2305.00315>\
**Keywords:** Decentralized identity; blockchain; federation; self-sovereign identity; verifiable credentials; distributed trust\
**Relevance to AEGIS:** Federated identity architecture precedent supporting GFN-1's decentralized trust model. Demonstrates blockchain-anchored DID federation as a viable basis for cross-domain identity without a centralized authority — directly relevant to AEGIS's multi-node governance federation and the trust scoring model in RFC-0004 §5.

---

## LLM Security

[19] OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," Version 2025, Nov. 18, 2024. [Online]. Available: <https://owasp.org/www-project-top-10-for-large-language-model-applications/>\
**Relevance to AEGIS:** The OWASP Top 10 for LLM Applications catalogues the primary security risks in LLM-based systems. LLM01 (Prompt Injection) directly motivates ATM-1 T6 and AEGIS's out-of-band governance posture — prompt content is never an authorization source. LLM06 (Excessive Agency) names the core problem AEGIS addresses: LLMs granted overly permissive capabilities, tools, or actions without adequate governance controls. AEGIS's capability registry, default-deny posture, and execution-time enforcement are direct architectural responses to the Excessive Agency risk.

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
**Last Updated**: 2026-03-13\
**Entries**: 32

# AEGIS™ and the Council of Europe Framework Convention on Artificial Intelligence

**Document**: `docs/position-papers/cets225/2026-03-aegis-cets225-positioning.md`\
**Version**: 0.1 (Living — not submitted)\
**Status**: Active — update as ratification progresses\
**Created**: 2026-03-15\
**Updated**: 2026-03-15\
**Author**: AEGIS™ Initiative, Finnoybu IP LLC\
**Part of**: AEGIS™ Position Papers

> **NOTE — LIVING DOCUMENT**: Unlike the NIST AI RMF position paper, this document is not
> a submitted statement. It is a living positioning resource that will require updates as the
> Council of Europe Framework Convention moves through ratification and implementation
> guidance emerges. The date anchor ("March 11, 2026") reflects the EU Parliament consent
> vote and will become historical context as the process advances.
>
> **Citation convention**: Inline article shorthand `[31, Art. N]` is used in this document
> (formal context). For public-facing copy (landing page, sponsor profile), consolidate to a
> single `[^31]` and move article mapping to the footnote definition. This convention applies
> to all AEGIS documents derived from this file.

---

## One-Line Positioning

AEGIS provides a technical conformance pathway for the Council of Europe Framework
Convention on AI[^31] — architectural enforcement that satisfies the convention's
transparency, auditability, and oversight requirements by making policy violations
structurally unavailable, not just detectable.

---

## Short Form

*(For landing page, sponsor profile body — ~100 words. Use consolidated `[^31]`/`[^32]`
footnotes; do not use inline article shorthand in public-facing copy.)*

On March 11, 2026, the European Parliament voted to endorse the EU's signature of the
Council of Europe Framework Convention on Artificial Intelligence and Human Rights,
Democracy and the Rule of Law[^32] — the first legally binding international treaty
dedicated specifically to AI governance. The convention requires transparency, auditability,
risk management, and lifecycle oversight for AI systems. For private sector actors, it permits
compliance through "other appropriate measures"[^31] rather than direct application of its
obligations.

AEGIS is one such measure. Where the convention defines the obligation, AEGIS provides
the architecture: policy enforcement at the execution boundary that makes certain violations
structurally unavailable — not monitored after the fact, but impossible to reach.

---

## Long Form

*(For whitepaper introduction, IEEE paper background section. Inline article shorthand
applies throughout.)*

The regulatory landscape for AI governance reached a significant milestone on March 11,
2026, when the European Parliament voted to endorse the EU's signature of the Council of
Europe Framework Convention on Artificial Intelligence and Human Rights, Democracy and
the Rule of Law[^32] — the first legally binding international treaty dedicated specifically to
AI governance. Negotiated with participation from the United States, Canada, the United
Kingdom, Japan, and others[^32], the convention establishes a global baseline requiring that
AI systems adhere to transparency [31, Art. 8], accountability [31, Art. 9], risk management
[31, Art. 16], and effective oversight [31, Art. 26] obligations throughout their lifecycles.

The convention's implementation model is notable for private sector actors. Article 3 §1(b)
permits compliance either by directly applying the convention's obligations or by "taking other
appropriate measures"[^31] to achieve the same ends. This framing recognizes that the
convention defines governance objectives, not implementation mechanisms — and that
architectural approaches may satisfy those objectives at least as rigorously as procedural or
monitoring-based compliance regimes.

AEGIS is designed precisely for this role. Rather than monitoring AI agent behavior and
reporting violations after they occur, AEGIS enforces governance policy at the architectural
boundary between AI agents and the infrastructure they act upon — making certain classes of
violation structurally unavailable rather than merely detectable. This approach is
model-agnostic, operates independently of training-time alignment, and produces auditable,
deterministic enforcement records suitable for regulatory compliance demonstration. Aligned
with the NIST AI Risk Management Framework[^13] and now situated within the emerging
international treaty regime, AEGIS provides organizations with a technically rigorous path to
satisfying the convention's requirements through other appropriate measures — by
architectural means.

---

## Convention Article Map

Quick reference for AEGIS-relevant convention obligations. For full text see [^31].

| Article | Obligation | AEGIS Component |
|---|---|---|
| Art. 3 §1(b) | Private sector compliance via "other appropriate measures" | AEGIS as conformance pathway |
| Art. 8 | Transparency and oversight | Audit trail; deterministic enforcement records |
| Art. 9 | Accountability and responsibility | Immutable audit log; actor identity binding |
| Art. 12 | Reliability | Deterministic enforcement; fail-closed posture |
| Art. 16 | Risk and impact management | ATM-1 threat model; capability registry |
| Art. 26 | Effective oversight mechanisms | AGP-1 governance protocol; GFN-1 federation |

---

## Regulatory Stack

AEGIS sits within a three-layer regulatory stack. Each layer reinforces the others:

| Layer | Instrument | Role |
|---|---|---|
| International treaty | Council of Europe CETS 225 [^31] | Global baseline; "other appropriate measures" hook |
| Technical framework | NIST AI RMF [^13] | Risk management structure; AEGIS formally aligned |
| Management system | ISO/IEC 42001:2023 | Organizational AI governance; AEGIS maps to all key clauses |

The convention establishes the obligation. NIST AI RMF provides the technical risk
framework. ISO/IEC 42001 defines the management system requirements. AEGIS is the
architectural enforcement layer that makes all three technically auditable and
deterministically enforceable at runtime.

---

## Update Triggers

This document should be reviewed and updated when:

- [ ] Council formally concludes the agreement (post-Parliament consent)
- [ ] Convention enters into force (five signatories ratify, per Art. 30 §3)
- [ ] Council of Europe publishes implementation guidance
- [ ] Additional major jurisdictions sign or ratify
- [ ] EU Commission publishes guidance on CETS 225 / AI Act alignment

---

## Related Documents

- NIST AI RMF position paper: `docs/position-papers/nist/2026-03-aegis-nist-ai-rmf-position-statement.md`
- EU AI Act reference: `REFERENCES.md` [^15]
- AEGIS architecture: `aegis-core/architecture/`
- ATM-1 threat model: `aegis-core/threat-model/`

---

[^13]: National Institute of Standards and Technology, "Artificial Intelligence Risk Management
Framework (AI RMF 1.0)," NIST AI 100-1, Jan. 2023, doi: 10.6028/NIST.AI.100-1.
See [REFERENCES.md](../../../REFERENCES.md).

[^15]: European Parliament and Council of the European Union, "Regulation (EU) 2024/1689
(Artificial Intelligence Act)," *Official Journal of the European Union*, OJ L, 12 Jul. 2024.
See [REFERENCES.md](../../../REFERENCES.md).

[^31]: Council of Europe, *Framework Convention on Artificial Intelligence and Human Rights,
Democracy and the Rule of Law*, CETS No. 225, Vilnius, 5 Sep. 2024. [Online]. Available:
<https://rm.coe.int/1680afae3c>. See [REFERENCES.md](../../../REFERENCES.md).
**Note**: "equivalent protection by other means" in the EP press release [^32] is a paraphrase
of Article 3 §1(b) — use treaty language ("other appropriate measures") in formal documents.

[^32]: European Parliament, "Parliament backs EU signature of Framework Convention on
Artificial Intelligence," Press Release 20260306IPR37524, 11 Mar. 2026. [Online]. Available:
<https://www.europarl.europa.eu/news/en/press-room/20260306IPR37524/parliament-backs-eu-signature-of-framework-convention-on-artificial-intelligence>.
See [REFERENCES.md](../../../REFERENCES.md).

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — Finnoybu IP LLC*

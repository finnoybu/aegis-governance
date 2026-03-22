# Peer Review Exchange: Trust Decay Determinism Objection
**Date:** March 14, 2026\
**From:** <finnoybu@users.noreply.github.com>\
**To:** Mattijs Moens (Founder, Sovereign Shield)\
**Status:** Response received\
**Response:** Received\
**Discussion:** <https://github.com/aegis-initiative/aegis-governance/discussions/72>

---

## Summary

Mattijs Moens conducted external peer review of the AEGIS governance specification and raised a technical objection to the trust decay mechanic in GFN-1 §3.8. Two issues were identified:

1. **Documentation inconsistency** — RFC-0004's trust decay documentation did not properly cross-reference the normative specification in GFN-1 §3.8. Corrected in RFC-0004 v0.3 (issue #35 — resolved).

2. **Determinism objection** — The decay function `T(t) = T₀ × e^(-λt)` is time-dependent; two nodes evaluating the same publisher at different times will compute different scores. Mattijs raised this as a potential violation of AEGIS Constitution Article III (determinism requirement).

## AEGIS Response (Summary)

AEGIS determinism is local and peer-to-peer, not global. Constitution Article III guarantees identical decisions for identical inputs — time is an explicit, logged input to the decay function, not a stochastic element. The function is fully deterministic given its inputs. Comparable systems (TLS, Kerberos, credit scoring, AML) treat time-awareness as a designed property of trustworthiness evaluation.

Full technical exchange documented in [Discussion #72](https://github.com/aegis-initiative/aegis-governance/discussions/72).

## Outcome

- RFC-0004 v0.3 signed off by Mattijs Moens
- Determinism objection considered resolved

---

> **Transparency Note:** This peer review exchange is archived publicly in the AEGIS repository to maintain transparency in the project's development and collaboration processes.

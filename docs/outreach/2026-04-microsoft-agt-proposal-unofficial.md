# AEGIS Initiative — Governance Architecture Layer

### Unofficial follow-on context — not an AGT proposal submission

**Audience:** Imran Siddique (Group EM, AGT); optionally Jack Batzner
**Status:** Shared as add-on context to the 2026-04-24 email reply, conditional on the `examples/aegis-governance-profile/` contribution (see [official proposal](./2026-04-microsoft-agt-proposal-official.md)) landing cleanly
**Intent:** To explain the broader integration thesis from the 2026-04-14 email — corrected where that framing was wrong — and to describe a three-level integration path *if* adopter signal emerges. This document is not asking for a commitment. It exists so that the example contribution is evaluated with full context rather than in a vacuum. **Acceptance of Level 1 (the example) carries no implicit commitment to consider Levels 2 or 3**; this document is context for evaluation, not a wedge for downstream scope.
**Date Drafted:** 2026-04-24

---

## Preamble — a correction to the original framing

The 2026-04-14 outreach email correctly identified
[REPUTATION-GATED-AUTHORITY.md](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/proposals/REPUTATION-GATED-AUTHORITY.md)
and the NEXUS / A2A trust extensions proposals as *"reaching toward principal accountability architecture,"* and framed AEGIS as closing gaps around *"authorization scope definition, principal delegation chains, data boundary agreements, and liability allocation between principals."*

Re-reading REPUTATION-GATED-AUTHORITY and
[folder-level-governance.md](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/proposals/folder-level-governance.md)
with closer attention to the specifics — the formal invariants, the concrete data models, the trust-composition mechanics — I want to correct the framing. The original email generalized from the *direction* of those proposals. On a careful second pass, they go well past direction-setting into concrete specification: AGT already owns agent-level delegation with cryptographic scope narrowing, trust-gated authority composition, lineage-bound initial trust, and revocation cascade semantics. That's more of the delegation/accountability territory than the 2026-04-14 email's framing implied was still open.

The actual white space — the part AEGIS addresses that AGT by its own scoping does not — is one level up from agent delegation: the **governance of the authority itself**. AGT's model assumes a single coherent policy authority whose decisions have been made and whose policies have been written. AEGIS addresses the case where that assumption has to be earned — multi-stakeholder authorship, formal policy change workflows, cross-organization federation, and principal-level (not agent-level) liability allocation.

The rest of this document reframes the integration thesis around that corrected positioning.

---

## The seam: what AGT scopes out by design

AGT's scoping is deliberate and well-documented in
[docs/LIMITATIONS.md](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/LIMITATIONS.md).
Several of the limitations listed there are deliberately out-of-scope because they belong to layers the runtime doesn't own. Three in particular matter for this document:

1. **Policies are configuration, not governed artifacts.** AGT enforces policies loaded from files. It does not govern the *process* by which those policies came to exist, who is authorized to change them, or what happens when stakeholders disagree on what a policy should say. Policy change is git-commit-and-reload; there is no formal PROPOSE → REVIEW → APPROVE → ENFORCE lifecycle.

2. **Policy authority is presumed singular.** AGT's folder-level-governance proposal scopes policies to directories within one deployment; it does not address the case where two independent principals (e.g., a cloud provider and a customer, or two coalition members) have overlapping authority and need a negotiated agreement rather than a scoped hierarchy.

3. **Principals are agents.** AGT's principal model is agents-with-DIDs. Humans and organizations appear as policy *authors* and trust-score *authorities*, but they are not first-class governed entities with delegation chains and liability allocation of their own.

None of these are gaps in AGT's implementation — they are correctly scoped exclusions. An enforcement runtime that tried to absorb them would become a different product. But they are real problems that show up in enterprise, federated, and regulated deployments, and they are specifically what the AEGIS specification family is built to address.

---

## What AEGIS provides

AEGIS is a four-specification family plus a public constitutional charter. Each component is independently useful and independently published; the integration thesis below does not require adopting all of them.

### AGP-1 — AEGIS Governance Protocol

A formal governance decision protocol with a three-phase lifecycle — ACTION_PROPOSE → ACTION_DECIDE → ACTION_EXECUTE — expressed as a wire format with JSON Schema definitions. Designed for the case where authorization decisions themselves need to be governed events, not configuration reads.

**Maturity:** Python reference implementation public at [github.com/aegis-initiative/aegis-core](https://github.com/aegis-initiative/aegis-core) (Apache 2.0 as of 2026-04-24), 400+ tests passing, pre-alpha. DOI [10.5281/zenodo.19355478](https://doi.org/10.5281/zenodo.19355478). Reference runtime, not a production system.

### AIAM-1 — Identity & Access Management for AI Agents

Introduces the aIAM category (third IAM actor class alongside humans and service accounts) and IBAC (Intent-Bound Access Control), a generalization of RBAC/ABAC/PBAC for agent authorization with structured intent claims, principal chains, and session governance. Addresses what AGT's LIMITATIONS.md calls "credential persistence" and the principal-vs-agent distinction.

**Maturity:** v0.1 specification complete: 12 chapters, 5 JSON schemas, RFC-0019. Published in the aegis-governance repository. Zenodo deposit pending. Standalone design — conformance does not require adopting any other AEGIS spec.

### ATX-1 — AEGIS Threat Matrix for Agentic AI

A systemic-failure taxonomy for agentic governance breakdowns. Complements OWASP Agentic Top 10 (which AGT maps to) by covering failure modes that are not adversarial attacks — broken governance loops, authorization drift, delegation compositions that individually pass but collectively violate intent. Positioned as the third column alongside MITRE ATT&CK and MITRE ATLAS.

**Maturity:** 10 tactics, 29 techniques, 29 sub-techniques. v2.2 current in the aegis-governance repository (sub-techniques added in v2.2 from RFC-0006 adversarial testing); DOI [10.5281/zenodo.19251098](https://doi.org/10.5281/zenodo.19251098) cites v2.1. Referenced in submissions to IEEE Computer (under review), NIST AI RMF (submission acknowledged), and NCCoE (public comment filed).

### GFN-1 — Governance Federation Network

Protocol for cross-organization governance signal propagation and inter-domain trust scoring. Addresses the multi-organization case where no single authority owns the policy model — e.g., supply-chain governance, coalition deployments, regulated cross-vendor agent handoffs. Complements, not replaces, AGT's within-domain trust scoring.

**Maturity:** v1 specification published in aegis-governance. RFC-0016 (cross-domain machine discovery protocol) merged.

### Constitutional articles

The public charter layer expressing the organizational agreements the AEGIS enforcement runtime implements. Published at [aegis-constitution.com](https://aegis-constitution.com), v26.03.22, under CC-BY-SA-4.0. No external body has ratified the charter; it is sole-maintainer-authored and pre-ratification, consistent with the current stage of the project. The structural argument below depends on the vendor-neutral *positioning* of the authority, not on any formal ratification claim.

### Evidence of effectiveness

The strongest evidence artifact is the Round 1 edge-evaluation findings document shared with Imran on 2026-04-21 (the PDF attachment). Summary of what it demonstrates:

- A compressed replication of Shapira et al.'s *Agents of Chaos* (same agent roster, model mix, OpenClaw infrastructure) with an added AEGIS governance condition in the enforcement path.
- Agent-authored 7-finding security audit of the governance layer.
- Explicit mapping of ATX-1 Root Causes to the AoC case studies (RC1–RC4 trace to AoC §16.2–16.3; RC5 is novel to AEGIS).
- Decision-engine benchmarks under adversarial load.
- Transparent limitations section up front: n=1 operator, 10-hour session, directed adversarial priming, not a peer-reviewed replication.

A formal, peer-reviewable replication is separately scoped.

---

## Three-level integration path

Levels below are presented as an escalating ladder of collaboration intensity. Each level is independently useful; advancing is conditional on adopter signal from the level before.

### Level 1 — `examples/aegis-governance-profile/`

The subject of the official proposal. A standalone, Apache 2.0, no-aegis-core-runtime-dependency example demonstrating AEGIS governance profile compilation to Cedar + Rego AGT PolicyDocuments. Lives in `examples/`, submitted as a PR following AGT's standard CLA + CONTRIBUTING process.

- **What it proves:** The authoring-layer pattern works against AGT's real external backends without disturbing any part of AGT's runtime, schema, or dependency graph.
- **What AGT commits to:** Reviewing the PR on its merits.
- **Effort:** Borne entirely by the AEGIS side.
- **Status:** Official proposal scoped; implementation pending.

### Level 2 — AEGIS governance profile as a recognized AGT input format

*Conditional on Level 1 landing and on independent adopter signal.*

The profile format, if it proves useful, moves from an in-example convention to a first-class AGT input alongside YAML, Cedar, and Rego. The `PolicyEvaluator` gains a `load_aegis_profile()` method (or an external adapter package is published under the AEGIS Initiative org and documented as an AGT-recognized option, whichever AGT prefers).

- **What it requires from AGT:** A published JSON Schema recognition for the AEGIS profile format, optionally a thin import surface. No runtime aegis-core dependency.
- **What it delivers to AGT adopters:** A stable, above-the-backend authoring layer with automatic fan-out to Cedar and Rego, governed by a vendor-neutral spec (not a Microsoft-only format).
- **Effort:** Estimated 2–4 weeks. Joint work or AEGIS-side contribution, per AGT's preference.
- **Dependency on Level 3:** None. Level 2 is terminal if adopter demand stops there.

### Level 3 — AGP-1 decision service integration

*Conditional on Level 2 adoption and on demonstrated demand from regulated, federated, or multi-stakeholder deployments.*

For deployments that need policy *change* governance — not just policy evaluation — AGT optionally integrates with an AGP-1 decision runtime. Policy load/reload operations flow through ACTION_PROPOSE → ACTION_DECIDE → ACTION_EXECUTE, producing an auditable governance trail for the policies themselves.

- **What this solves:** The "policies are configuration" limitation from AGT's LIMITATIONS.md. For regulated or cross-stakeholder deployments, policy changes become governed events with proposer, decider, executor, and audit identity.
- **What it requires from AGT:** An optional, opt-in policy-lifecycle hook. Deployments that don't need it keep AGT's current single-authority behavior unchanged.
- **What it requires from adopters:** Running an AGP-1 runtime (aegis-core or a compatible implementation) as a separate service. This is the first level with a runtime dependency on AEGIS code.
- **Effort:** Months of joint design work. Only pursued if Levels 1 and 2 produce concrete adopter demand.
- **Alternative:** AGT could implement its own policy-lifecycle protocol that reads AEGIS profile changes as governed events, with AEGIS's AGP-1 as reference prior art rather than runtime dependency.

---

## Why AEGIS specifically — and not "AGT could just build this"

The three-level path above raises a reasonable question: everything at Levels 2 and 3 could in principle be built inside AGT. Three reasons it's better not to.

1. **Constitutional positioning is vendor-neutral by construction.** The cross-organization governance case (coalition deployments, regulated supply chains, multi-vendor agent handoffs) requires a charter no single vendor can credibly author unilaterally. AEGIS Initiative is structured as a vendor-neutral authority for this layer, with the charter published under CC-BY-SA-4.0 and specifications versioned with public DOIs. The charter is not yet externally ratified — that's an honest limitation of the current stage — but the structural separation (Microsoft hosting the enforcement runtime while AEGIS Initiative hosts the charter) is cleaner than Microsoft hosting both, particularly for enterprise customers whose compliance posture depends on the governance authority being separable from any one provider.

2. **The specification work is already done and public.** AGP-1 + AIAM-1 + ATX-1 + GFN-1 + constitutional articles are published under CC-BY-SA-4.0 with two DOIs minted, reference runtime tested and open-sourced, and an active external citation footprint (NIST RMF submission, NCCoE public comment, IEEE submissions under review). The corpus has been under active development since January 2026, building on a short prior period of conceptual design — compact on the calendar, but the artifacts are concrete and shippable today. Parallel invention inside AGT would reproduce that work at non-trivial cost and without the accumulated standards-engagement footprint.

3. **The reference runtime exists and is now open-source.** aegis-core is public as of 2026-04-24, Apache 2.0, 400+ tests passing, DOI-minted, with demonstrated behavior under the Round 1 adversarial evaluation. Integration cost is lower than parallel-build cost, and AGT adopters who want to extend the governance layer can contribute upstream to an independent project rather than creating a Microsoft-specific fork.

None of these reasons preclude AGT building competing capability at Levels 2–3 later. They argue that starting from the existing artifacts is the faster and structurally cleaner path *if* adopter signal emerges.

---

## Non-goals

To prevent scope creep in either direction:

- **This document is not a request for AGT to commit to anything.** Level 1 is the only active ask. Levels 2 and 3 are described so that Level 1 is evaluated with full context.
- **This is not a reopening of the original "AEGIS as policy source of truth" proposal.** That scope was correctly parked during the six-question exchange. The three-level path is fundamentally different — it's a conditional ladder, not an up-front ask.
- **AEGIS is not competing with REPUTATION-GATED-AUTHORITY.** AGT owns agent-level delegation; AEGIS's delegation model operates at the principal level (humans, organizations, service accounts) above it. Both are needed for full principal-chain coverage, and they compose cleanly.
- **AEGIS is not asking AGT to depend on aegis-core at any level below Level 3.** The entire Level 1 + Level 2 path is designed to be dependency-free from AGT's perspective.

---

## Closing

This document is share-at-your-discretion. It isn't a formal AGT proposal and isn't intended to land in AGT's `docs/proposals/` catalogue; it exists so that when the `examples/aegis-governance-profile/` contribution arrives, the larger context is available without having to reconstruct it from the email thread.

If the example lands cleanly and there's appetite for Level 2, the natural next step is a scoping conversation on the profile-format JSON Schema and the import surface AGT would find acceptable. If there isn't appetite, Level 1 is still independently useful on its own terms and nothing about the larger picture is a precondition for it.

Grateful for the directness of the 2026-04-21 pushback — it produced a cleaner framing than the one I started with.

---

## References

- Official example proposal (narrow scope): [2026-04-microsoft-agt-proposal-official.md](./2026-04-microsoft-agt-proposal-official.md)
- Email thread (through 2026-04-21): [2026-04-microsoft-agt-integration.md](./2026-04-microsoft-agt-integration.md)
- AEGIS repository index: [github.com/aegis-initiative](https://github.com/aegis-initiative)
- aegis-core reference runtime: [github.com/aegis-initiative/aegis-core](https://github.com/aegis-initiative/aegis-core)
- Governance site (AGP-1, AIAM-1, GFN-1 specs): [aegis-governance.com](https://aegis-governance.com)
- Threat matrix: [aegis-docs.com/threat-matrix/](https://aegis-docs.com/threat-matrix/)
- Constitutional charter: [aegis-constitution.com](https://aegis-constitution.com)
- ATX-1 v2.1 DOI: [10.5281/zenodo.19251098](https://doi.org/10.5281/zenodo.19251098)
- aegis-core v0.1.2 DOI: [10.5281/zenodo.19355478](https://doi.org/10.5281/zenodo.19355478)
- AGT REPUTATION-GATED-AUTHORITY proposal: [github.com/microsoft/agent-governance-toolkit/blob/main/docs/proposals/REPUTATION-GATED-AUTHORITY.md](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/proposals/REPUTATION-GATED-AUTHORITY.md)
- AGT LIMITATIONS.md: [github.com/microsoft/agent-governance-toolkit/blob/main/docs/LIMITATIONS.md](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/LIMITATIONS.md)

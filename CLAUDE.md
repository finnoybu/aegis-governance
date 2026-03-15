# CLAUDE.md — AEGIS Repository
_Instructions for Claude Code — 2026-03-15_

## What This Repository Is

The `finnoybu/aegis-governance` repository is a **living scholarly work** — not just code + docs, but a complete, peer-reviewable governance framework where every claim is traceable to established research. See [docs/vision/AEGIS_CANON_VISION.md](docs/vision/AEGIS_CANON_VISION.md) for the full vision.

The canonical bibliography lives in [`REFERENCES.md`](REFERENCES.md).

---

## For Claude Code

### Always
- Read a file before editing it
- Check if claims should be cited; reference `REFERENCES.md` when adding technical content
- Maintain consistent terminology with cited sources (see table below)
- Cross-reference related AEGIS documents rather than restating their content
- Suggest citations when reviewing or adding content

### Never
- Make uncited claims about architectural precedents
- Use terminology inconsistent with cited sources
- Restate content from canonical files — link to them instead
- Edit frozen documents (see table below)
- Apply the GFN-1 trust formula to agent runtime trust — it is scoped to federation publisher trust only (see Trust Architecture below)

---

## Terminology: Critical Distinctions

Do not conflate these terms.

| Term | Definition | Do Not Confuse With |
|------|-----------|---------------------|
| **RLHF** | Reinforcement learning from human feedback (human labelers) | Constitutional AI |
| **Constitutional AI** | Reinforcement learning from AI feedback / RLAIF (Anthropic) | RLHF |
| **Constitutional Autonomy** | Agbemabiese (IEEE Access 2026) — runtime attention mechanism modification | Constitutional AI |
| **Architectural-layer governance** | AEGIS — enforcement at execution boundary, model-agnostic | Model-layer approaches |
| **Model-layer governance** | Training-time alignment (RLHF, Constitutional AI, fine-tuning) | Architectural enforcement |
| **Threat Detection Layer** | RFC-0004 §5.2 — binary, evidence-driven, Engine layer (Layer 3) | Reputation Layer |
| **Reputation Layer** | RFC-0004 §5.3 — graduated, longitudinal, Schema layer (Layer 2) | Threat Detection Layer |
| **Federation publisher trust** | GFN-1 §3.7 — trust score for remote governance signal sources | Agent runtime trust |
| **Agent runtime trust** | RFC-0004 §5 — two-layer model for agent admissibility at execution boundary | Federation publisher trust |

**Constitutional Autonomy** (Agbemabiese 2026) is a recent, not-yet-widely-cited paper. Use it only where properly cited (outreach, Discussion #39). Do not add it to comparison tables without explicit instruction.

**Defense-in-depth framing:** Model-layer and architectural-layer approaches are complementary, not competitive. AEGIS positioning should always reflect this.

---

## Trust Architecture (Normative — Read Before Touching Any Trust-Related Code or Docs)

AEGIS trust operates through two structurally independent models. Do not conflate them.

### Federation Publisher Trust (GFN-1)

Governs how much weight to assign governance signals received from remote AEGIS nodes.

**Normative spec:** `federation/AEGIS_GFN1_TRUST_MODEL.md` §3.7\
**Formula:** `T = 0.30B + 0.25H + 0.20Q + 0.15A + 0.10F`\
**Decay:** `T_decayed = T × e^(-λt)`, λ=0.01, half-life ≈ 69 days (§3.8)\
**Scope:** Federation publisher trust ONLY. MUST NOT be applied to agent runtime trust decisions.

When class disposition (§10.1) and score disposition (§3.9) conflict, the more restrictive applies.

### Agent Runtime Trust (RFC-0004 §5)

Governs agent admissibility at the execution boundary. Two layers, structurally separate.

**Threat Detection Layer** (Engine — Layer 3):
- Binary: block or pass. No score produced.
- Fires on evidence of active threat, immediately.
- A block here CANNOT be overridden by Reputation Layer state under any condition.
- No read access to Reputation Layer state.

**Reputation Layer** (Schema — Layer 2):
- Graduated: informs autonomy expansion, approval latency, capability range.
- Longitudinal: accumulates over operational history.
- No write access to Threat Detection Layer decisions.
- Decay function for agent reputation is **deferred to a future RFC**. GFN-1 §3.8 is the candidate reference; treat as implementation-defined until normatively specified.

**Non-Override Constraint (normative):** No Reputation Layer score, at any value, grants a pass on a Threat Detection Layer block. This separation MUST be architectural, not procedural.

### Origin of the Two-Layer Model

The architectural principle — that security and reputation must never share a single score — was contributed by **Mattijs Moens** (Founder, Sovereign Shield) via peer review on 2026-03-15 (Discussion #72). His framing identified the category error in the prior composite trust model. The specification work is the AEGIS Initiative's; the foundational insight is his. Acknowledged in RFC-0004 §Acknowledgments.

---

## RFC Status Snapshot

| RFC | Title | Version | Status | Notes |
|-----|-------|---------|--------|-------|
| RFC-0001 | AEGIS Architecture | 0.2 | Draft | Foundational — read first |
| RFC-0002 | Governance Runtime | 0.2 | Draft | API, state model, SLOs |
| RFC-0003 | Capability Registry & Policy | 0.2 | Draft | Policy language, evaluation algorithm |
| RFC-0004 | Governance Event Model | 0.4 | Draft | Two-layer trust; issue #35 closed |
| RFC-0005 | Reference Deployment Patterns | 0.1 | Draft | RDP-01–04; RDP-03 is recommended start |
| RFC-0006 | Claude Code Plugin | 0.1 | Draft | **Next implementation target — Q2 2026** |
| RFC-0007 | Operational Considerations | 0.0.1 | Placeholder | Monitoring, DR, day-two ops |
| RFC-0008 | Federation Network Protocol | 0.0.1 | Placeholder | GFN-1 transport layer |

**RFC-0006 is the active implementation target.** It implements RDP-03 (Embedded Lightweight) from RFC-0005 in the Claude Code execution environment. Start there.

RFC-0004 v0.4 is the current trust model specification. The prior composite score model was rejected — it collapsed security and reputation into one number, creating a category error. See RFC-0004 §Alternatives Considered and §5.1.

---

## Frozen & Protected Documents

| Document | Status | Rule |
|----------|--------|------|
| `docs/position-papers/nist/2026-03-aegis-nist-ai-rmf-position-statement.md` | SUBMITTED | Do not edit. |
| `aegis-core/manifesto/AEGIS_Manifesto.md` | v0.1, referenced in NIST submission | Substantial edits require version bump to 0.2. Treat changes as amendments. |

---

## Single Source of Truth

Canonical files are authoritative. All other documents must **link**, not restate.

| Topic | Canonical file |
|-------|---------------|
| NIST submission | `docs/position-papers/nist/2026-03-aegis-nist-ai-rmf-position-statement.md` |
| NIST directory index | `docs/position-papers/nist/README.md` |
| Federation trust model | `federation/AEGIS_GFN1_TRUST_MODEL.md` |
| Agent runtime trust | `rfc/RFC-0004-Governance-Event-Model.md` §5 |
| Outreach records | `docs/outreach/` |
| Bibliography | `REFERENCES.md` |

---

## Key Prior Art (Cite; Do Not Restate)

| Paper | What it establishes | Where to cite |
|-------|-------------------|---------------|
| DroidForce (2014) | Centralized PDP + distributed PEP — AGP-1 + AEGIS gates | Architecture sections |
| Smart I/O Modules (2020) | Boundary enforcement; compromised controller assumption | Threat model |
| POLYNIX (2026) | Hybrid enforcement validated; <1% CPU, <2s propagation | Performance, architecture |
| Web Services (2012) | Foundational runtime contract enforcement (93 citations) | Related work, background |
| CPS Parallel (2024) | Compositional multi-policy; linear scalability | Related work |
| Constitutional Autonomy (2026) | Model-layer complement; defense-in-depth framing | Positioning only; see terminology note |
| NIST SP 800-207 | Zero Trust Architecture | Trust model, RFC-0004 |
| Agents of Chaos (2026) | Governance failures in live agentic deployments | RFC-0006 motivation |
| OWASP LLM Top 10 (2025) | Excessive Agency (LLM06) — motivates execution boundary governance | RFC-0006 motivation |

Full entries in [`REFERENCES.md`](REFERENCES.md).

---

## Git Workflow

```
git checkout -b <type>/<short-description>
git add <specific files>
git commit -m "Type: description\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push -u origin <branch>
gh pr create ...
gh pr merge <number> --squash --auto
```

Branch naming: `docs/topic`, `feat/topic`, `fix/topic`\
Merge strategy: squash merge always\
Never force-push, never skip hooks.

---

## Markdown Conventions

- **Line breaks in metadata/headers:** Backslash `\` at end of line — not trailing spaces (linter strips them)
- **Notes and notices:** Blockquotes `>` — not fenced code blocks
- **Frozen notice:** `> **SUBMITTED — DO NOT EDIT**` as first content after document metadata

---

## Outreach Records (`docs/outreach/`)

Header fields (in order): Date, From, To, Status, Response, Discussion\
Status: `Initial outreach sent` | `Follow-up sent` | `Response received` | `Closed`\
Response: `Pending` | `Received` | `No response`\
File naming: `YYYY-MM-<topic>.md`\
Keep `docs/outreach/README.md` log table current.

---

## Citation Format

Use **IEEE style** for all formal papers. For other source types:

| Source type | Format |
|-------------|--------|
| IEEE / academic paper | `[Author(s)], "Title," *Venue*, vol. X, no. Y, pp. ZZZ–ZZZ, Year, doi: XX.XXXX/XXXXXX.` |
| Standards document | `Organization, *Standard Title*, Standard No., Year. [Online]. Available: URL` |
| Web article / blog | `Author(s), "Title," *Site Name*, Date. [Online]. Available: URL` |
| arXiv preprint | `Author(s), "Title," arXiv:XXXXXXX, Month Year. [Online]. Available: URL` |
| Software / framework | `Name, Version, Organization, Year. [Online]. Available: URL` |

### Inline footnotes (GitHub Markdown)

Use `[^N]` at point of use; define at document bottom:

```markdown
AEGIS adopts the centralized PDP + distributed PEP pattern [^2] proven
effective in system-wide policy enforcement.

[^2]: S. Rasthofer et al., "DroidForce," ARES 2014, doi: 10.1109/ARES.2014.13. See [REFERENCES.md](REFERENCES.md).
```

This renders as a clickable superscript with a jump link to the reference.

### Shorthand in-text citations

Where inline footnotes are not appropriate (tables, positioning statements):

```
[DroidForce, 2014]  or  [1]
```

### Canonical bibliography

All papers cited anywhere in the repo must appear in [`REFERENCES.md`](REFERENCES.md). Individual document footnotes are self-contained but always include a pointer to `REFERENCES.md` for the full entry.

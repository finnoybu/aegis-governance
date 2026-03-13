# CLAUDE.md — AEGIS Repository
_Instructions for Claude Code — 2026-03-13_

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

**Constitutional Autonomy** (Agbemabiese 2026) is a recent, not-yet-widely-cited paper. Use it only where properly cited (outreach, Discussion #39). Do not add it to comparison tables without explicit instruction.

**Defense-in-depth framing:** Model-layer and architectural-layer approaches are complementary, not competitive. AEGIS positioning should always reflect this.

---

## Frozen & Protected Documents

| Document | Status | Rule |
|----------|--------|------|
| `docs/position-papers/nist/2026-03-aegis-nist-ai-rmf-position-statement.md` | SUBMITTED | Do not edit. |
| `aegis-core/manifesto/AEGIS_Manifesto.md` | v0.1, referenced in NIST submission | Substantial edits require version bump to 0.2. Treat changes as amendments. |

---

## Single Source of Truth

Canonical files are authoritative. All other documents must **link**, not restate.

- NIST submission → `docs/position-papers/nist/2026-03-aegis-nist-ai-rmf-position-statement.md`
- NIST directory index → `docs/position-papers/nist/README.md`
- Outreach records → `docs/outreach/`

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

[^2]: S. Rasthofer et al., "DroidForce," ARES 2014, doi: 10.1109/ARES.2014.13. See [REFERENCES.md](../../REFERENCES.md).
```

This renders as a clickable superscript with a jump link to the reference.

### Shorthand in-text citations

Where inline footnotes are not appropriate (tables, positioning statements):

```
[DroidForce, 2014]  or  [1]
```

### Canonical bibliography

All papers cited anywhere in the repo must appear in [`REFERENCES.md`](REFERENCES.md). Individual document footnotes are self-contained but always include a pointer to `REFERENCES.md` for the full entry.

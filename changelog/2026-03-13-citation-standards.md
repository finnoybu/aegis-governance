# 2026-03-13 — Citation Standards & Canonical Bibliography

**Date:** 2026-03-13\
**Type:** Milestone\
**Status:** Committed to `main`

---

## Summary

Citation standards established for the AEGIS repository as part of the repository-as-living-paper initiative. `REFERENCES.md` created as the canonical bibliography with 14 entries. `CLAUDE.md` updated with the full citation standard including source-type table and inline footnote conventions.

---

### Added

- **`REFERENCES.md`** — Canonical bibliography at repository root. 14 entries across four sections:
  - **Foundational Security Theory** — Anderson 1972 (reference monitor), Schneider 2000 (security automata)
  - **Runtime & Architectural Enforcement** — Hallé & Villemaire 2012, Rasthofer et al. 2014 (DroidForce), Pearce et al. 2020 (Smart I/O), Majumdar et al. 2022 (ProSAS), Baird et al. 2024 (CPS), Arunachalam et al. 2026 (POLYNIX)
  - **Model-Layer AI Governance** — Christiano et al. 2017 (RLHF), Bai et al. 2022 (Constitutional AI), Agbemabiese 2026 (Constitutional Autonomy), Shapira et al. 2026 (Agents of Chaos)
  - **Standards & Frameworks** — NIST AI RMF 2023, Open Policy Agent

---

### Changed

- **`CLAUDE.md` — Citation Format section** expanded from a single IEEE template to:
  - Source-type table (IEEE paper, standards, web article, arXiv, software)
  - Inline footnote syntax with GitHub Markdown `[^N]` example
  - Shorthand in-text citation guidance
  - Canonical bibliography pointer rule

---

## Citation Standard (recorded here for permanence)

**Primary style:** IEEE for all formal papers.\
**Fallback by source type:**

| Source type | Format |
|-------------|--------|
| IEEE / academic paper | `Author(s), "Title," *Venue*, vol., no., pp., Year, doi:` |
| Standards document | `Organization, *Title*, Standard No., Year. [Online]. Available: URL` |
| Web article / blog | `Author(s), "Title," *Site*, Date. [Online]. Available: URL` |
| arXiv preprint | `Author(s), "Title," arXiv:XXXXXXX, Month Year. [Online]. Available: URL` |
| Software / framework | `Name, Version, Organization, Year. [Online]. Available: URL` |

**Inline:** GitHub Markdown `[^N]` footnote syntax — superscript at point of use, full citation at document bottom with pointer to `REFERENCES.md`.

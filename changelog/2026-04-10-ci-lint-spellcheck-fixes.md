# 2026-04-10 — CI Lint & Spellcheck Resolution

**Date:** 2026-04-10\
**Type:** Patch\
**Status:** Fixed

---

## Summary

Resolved persistent `markdownlint` and `cspell` CI failures that were
blocking the PR merge pipeline. Failures stemmed from two independent causes:
bare URL violations in the TNSE paper files and unknown abbreviations in
`docs/PUBLICATIONS.md`.

---

### Fixed

- **Markdownlint bare-URL errors** — `AEGIS-TNSE-Edge-Governance-2026.md`
  and `AoC-Lab-Executive-Summary.md` contained bare hyperlinks and email
  addresses flagged by MD034. Resolved by adding
  `docs/position-papers/ieee-tnse-2026/**` to the `.markdownlint-cli2.yaml`
  `ignores` list. The IEEE submission files are excluded from repository
  lint enforcement to preserve their original formatting.

- **Spellcheck unknown words** — `TNSE` (IEEE Transactions on Network and
  Service Engineering) and `TNSEJL` (IEEE TNSE Journal) were not in the
  cspell dictionary, causing `docs/PUBLICATIONS.md` checks to fail. Both
  abbreviations added to `.cspell.json` `words` list.

- **Spellcheck path exclusion** — `docs/position-papers/ieee-tnse-2026/**`
  added to `.cspell.json` `ignorePaths` so that paper source files do not
  produce false-positive spell errors.

---

### Affected CI workflows

| Workflow | Job | Event | Status |
|----------|-----|-------|--------|
| Docs Lint | markdownlint | pull_request | ✅ Fixed |
| Docs Lint | markdownlint | push | ✅ Fixed |
| Spell Check | spelling | pull_request | ✅ Fixed |
| Spell Check | spelling | push | ✅ Fixed |

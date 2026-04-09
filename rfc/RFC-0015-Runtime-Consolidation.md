# RFC-0015: Governance Runtime Consolidation

**RFC:** RFC-0015\
**Status:** Draft\
**Version:** 0.1.0\
**Created:** 2026-03-29\
**Updated:** 2026-03-29\
**Author:** Ken Tannenbaum, AEGIS Initiative / Finnoybu IP LLC\
**Repository:** aegis-governance, aegis-core, aegis-platform\
**Target milestone:** Q2 2026\
**Supersedes:** None\
**Superseded by:** None

---

## Summary

The AEGIS governance enforcement runtime — the Python implementation of the AGP-1 pipeline — currently exists in three locations across the organization. This RFC formalizes `aegis-core/core-py/` as the single canonical location for all runtime code, mandates removal of the redundant copies in `aegis-governance/aegis-runtime/` and `aegis-platform/deploy/aegis/`, and establishes `aegis-core` as a proper dependency consumed by downstream repositories.

This migration was partially initiated prior to this RFC — `aegis-governance/aegis-runtime/` contains a `MOVED.md` noting the migration — but was never formally authorized, the source code was never removed, and a third copy was created in `aegis-platform/deploy/` without any governance record. This RFC corrects that by documenting the full consolidation and establishing the migration as a governed decision.

---

## Motivation

### The Problem

The same governance enforcement runtime exists in three places:

| Location | Package name | Build backend | License | Notes |
|---|---|---|---|---|
| `aegis-governance/aegis-runtime/aegis/` | `aegis-runtime` | setuptools | Apache-2.0 | Has `MOVED.md` but code still present |
| `aegis-core/core-py/aegis_core/` | `aegis-core` | hatchling | BSL-1.1 | Has 3 additional modules not in the other copies |
| `aegis-platform/deploy/aegis/` | (none) | (none) | (none) | Raw copy with committed `.pyc` files; no provenance |

All three copies share the same core modules: `gateway.py`, `policy_engine.py`, `decision_engine.py`, `audit.py`, `capability_registry.py`, `protocol.py`, `runtime.py`, `tool_proxy.py`, `exceptions.py`. These are functionally identical across all three locations, with the sole divergence being the package import prefix in docstring examples (`aegis` vs `aegis_core` in `runtime.py`).

However, `aegis-core` has already diverged ahead of the other two copies with three additional modules:
- `capability.py` — Capability data structures
- `policy.py` — Policy data structures
- `risk.py` — Risk scoring engine

This means drift has already begun. Any change to governance logic now requires updating three codebases — a process that is manual, undocumented, and has no CI enforcement.

### What Happens If We Do Nothing

- Governance logic changes must be manually propagated to three locations
- `aegis-core` will continue to diverge from the other two copies as development progresses
- `aegis-platform` will run stale governance logic in production without any mechanism to detect the drift
- Contributors will encounter three different package names (`aegis`, `aegis_core`, and an unpackaged copy) for the same code, with no clear signal about which is authoritative
- The committed `.pyc` files in `aegis-platform/deploy/` will continue to be a code hygiene issue

### Procedural Note

The initial migration from `aegis-governance/aegis-runtime/` to `aegis-core/core-py/` was performed without an RFC, ADR, or changelog entry. The `aegis-platform/deploy/aegis/` copy was created without any governance record. This RFC retroactively authorizes the migration and mandates the cleanup that should have accompanied it.

---

## Guide-Level Explanation

After this RFC is implemented:

- **`aegis-core`** is the only place governance runtime code lives. If you want to read, modify, test, or contribute to the enforcement engine, you go to `aegis-core/core-py/`.

- **`aegis-governance`** no longer contains any runtime implementation. The `aegis-runtime/` directory is reduced to a `MOVED.md` redirect and a `README.md` noting the historical context. All Python source files and tests are removed.

- **`aegis-platform`** consumes `aegis-core` as a proper Python dependency. The `deploy/aegis/` directory is removed entirely. The platform's API server imports from `aegis_core` instead of from a local copy.

- **`aegis-sdk`** (Python) remains a separate package. It wraps the platform's REST API and does not import from `aegis-core` directly. No change required.

The runtime's canonical identity is:
- **Package name:** `aegis-core`
- **Import prefix:** `aegis_core`
- **Build backend:** hatchling
- **Python version:** 3.11+
- **License:** BSL-1.1
- **Repository:** `aegis-initiative/aegis-core`

---

## Reference-Level Explanation

### Phase 1 — Verify Canonical State

Before removing anything, verify that `aegis-core/core-py/` is a strict superset of the other two copies:

1. Confirm all modules in `aegis-governance/aegis-runtime/aegis/` exist in `aegis-core/core-py/aegis_core/` with identical implementation logic (allowing for import prefix differences)
2. Confirm all modules in `aegis-platform/deploy/aegis/` exist in `aegis-core/core-py/aegis_core/` with identical implementation logic
3. Confirm all test files in `aegis-governance/aegis-runtime/tests/` have counterparts in `aegis-core/core-py/tests/`
4. Confirm the three additional modules in `aegis-core` (`capability.py`, `policy.py`, `risk.py`) do not exist in the other copies
5. Run the full `aegis-core` test suite and confirm all tests pass

### Phase 2 — Remove aegis-governance/aegis-runtime/ Source Code

Remove all Python source files and test files from `aegis-governance/aegis-runtime/`:

**Remove:**
- `aegis-runtime/aegis/__init__.py`
- `aegis-runtime/aegis/audit.py`
- `aegis-runtime/aegis/capability_registry.py`
- `aegis-runtime/aegis/decision_engine.py`
- `aegis-runtime/aegis/exceptions.py`
- `aegis-runtime/aegis/gateway.py`
- `aegis-runtime/aegis/policy_engine.py`
- `aegis-runtime/aegis/protocol.py`
- `aegis-runtime/aegis/runtime.py`
- `aegis-runtime/aegis/tool_proxy.py`
- `aegis-runtime/tests/` (entire directory)
- `aegis-runtime/pyproject.toml`
- `aegis-runtime/LICENSE`
- `aegis-runtime/CHANGELOG.md`

**Retain:**
- `aegis-runtime/MOVED.md` — Updated to reference this RFC
- `https://github.com/aegis-initiative/aegis-core` — Replaced with a short redirect notice referencing this RFC and linking to `aegis-core`

### Phase 3 — Remove aegis-platform/deploy/aegis/ Copy

Remove the entire local runtime copy from `aegis-platform`:

**Remove:**
- `deploy/aegis/` (entire directory, including all `.py` and `.pyc` files)

**Update:**
- `deploy/requirements.txt` — Add `aegis-core` as a dependency (pinned to a specific version or installed from the repository)
- `deploy/main.py` — Update imports from `from aegis import ...` to `from aegis_core import ...`
- `api/main.py` — Update imports if applicable
- `deploy/Dockerfile` — Update to install `aegis-core` dependency
- `api/Dockerfile` — Update to install `aegis-core` dependency
- `.gitignore` — Ensure `__pycache__/` and `*.pyc` are excluded (they were committed in `deploy/aegis/`)

### Phase 4 — Remove Demo Scripts from aegis-governance

The example scripts in `aegis-governance/examples/runtime/` (`hello_aegis.py`, `basic_runtime_demo.py`) import from the `aegis-runtime` package and will no longer function after Phase 2. These are demonstration code, not specifications.

**Move to `aegis-labs`:**
- `examples/runtime/hello_aegis.py`
- `examples/runtime/basic_runtime_demo.py`

Update their imports from `from aegis import ...` to `from aegis_core import ...`.

If `aegis-labs` is not yet structured to receive them, they may be moved to `aegis-core/examples/` as package-level examples instead.

### Phase 5 — Standardize Build Configuration

Ensure `aegis-core/core-py/pyproject.toml` is the authoritative package definition:

| Field | Value |
|---|---|
| name | `aegis-core` |
| version | `0.1.0` |
| build-backend | `hatchling` |
| requires-python | `>=3.11` |
| license | `BSL-1.1` |

Remove `aegis-governance/pyproject.toml` root-level package definition if it references `aegis-runtime` as a dependency or sub-package.

### Phase 6 — CI Validation

Add a CI check to `aegis-platform` that verifies `aegis-core` is installed as a dependency and that no local `aegis/` or `aegis_core/` directories exist in `deploy/`. This prevents future re-introduction of local copies.

---

## Drawbacks

### Deployment Coupling

`aegis-platform` will now depend on `aegis-core` as an external package. This introduces a deployment dependency that did not previously exist — platform deployments require a specific version of `aegis-core` to be available. This is standard practice for library dependencies but does mean that a broken `aegis-core` release could block platform deployment.

**Mitigation:** Pin `aegis-core` to a specific version in `deploy/requirements.txt`. Use a lock file. Run `aegis-core` tests as part of `aegis-platform` CI.

### Import Path Change

All code that currently imports from `aegis` (the old package name) must be updated to import from `aegis_core`. This affects:
- `aegis-platform/deploy/main.py`
- `aegis-platform/api/main.py`
- `aegis-governance/examples/runtime/` (moved to aegis-labs)
- Any external code that may have been written against `aegis-runtime`

**Mitigation:** The `aegis-runtime` package was never published to PyPI. External consumers are unlikely. Internal consumers are enumerable and can be updated in the same set of PRs.

### Loss of In-Repo Development Convenience

Contributors to `aegis-governance` could previously run and test the runtime locally within the same repo. After this RFC, runtime development happens in `aegis-core` exclusively.

**Mitigation:** This is the intended outcome. Specification and implementation should be developed in separate repos with clear boundaries.

---

## Alternatives Considered

### 1. Keep All Three Copies, Synchronize with CI

Rejected. Synchronizing three copies of the same code across three repos is strictly more complex than having one canonical copy. It also violates the principle of single source of truth and invites the exact drift that has already begun.

### 2. Keep aegis-governance/aegis-runtime/ as the Canonical Location

Rejected. `aegis-governance` is a specification repository. Runtime implementation code has different change rates, different reviewers, different CI requirements, and different consumers. The `aegis-core` repo was created specifically to be the implementation home.

### 3. Vendor aegis-core into aegis-platform via Git Submodule

Rejected. Submodules add complexity to the clone and build process, create confusing merge conflicts, and are frequently a source of developer frustration. A proper Python package dependency is simpler and more standard.

### 4. Merge aegis-core into aegis-platform as a Monorepo

Rejected. `aegis-core` is also consumed (or will be consumed) by `aegis-sdk` and potentially by `aegis-federation`. It must remain an independent, importable package.

---

## Compatibility

### Breaking Changes

- **`aegis-runtime` package name is retired.** Any code importing `from aegis import ...` must be updated to `from aegis_core import ...`.
- **`aegis-platform/deploy/aegis/` is removed.** The platform must install `aegis-core` as a dependency.

### Deprecations

- `aegis-governance/aegis-runtime/` — Deprecated and reduced to a redirect notice.
- `aegis-governance/examples/runtime/` — Moved to `aegis-labs` or `aegis-core/examples/`.

### Backwards Compatibility

- `aegis-core/core-py/` is already the most complete copy. No functionality is lost.
- `aegis-governance` specification content is unaffected.
- All JSON schemas, RFCs, protocol definitions, and threat model documents remain in `aegis-governance`.
- No DOI-anchored artifact references the runtime code. No citation impact.

---

## Implementation Notes

### Suggested Sequence

1. Verify Phase 1 (canonical state confirmation) — this should be done before any PRs are opened
2. Open a PR on `aegis-governance` for Phases 2 and 4 (remove runtime source, move examples)
3. Open a PR on `aegis-platform` for Phase 3 (remove local copy, add dependency, update imports)
4. Open a PR on `aegis-core` for Phase 5 (verify pyproject.toml) and Phase 6 (CI check)
5. Update the RFC index (`aegis-governance/rfc/README.md`) to include this RFC

PRs 2 and 3 can be opened in parallel. PR 4 depends on PR 3 being merged (CI check validates the dependency).

### Known Issues to Address During Implementation

- `aegis-platform/deploy/aegis/__pycache__/` contains committed `.pyc` files. These should be removed and `.gitignore` updated.
- `aegis-governance/https://github.com/aegis-initiative/aegis-core` contains duplicated git clone blocks and a stray `*** End Patch` artifact (line 227). The replacement redirect notice resolves this.
- `aegis-governance/pyproject.toml` at the repo root defines an `aegis-governance` package. Verify it does not declare `aegis-runtime` as a sub-package or dependency.

### Dependencies

- No dependency on other RFCs.
- RFC-0014 (ATX-1 Dual-Licensing) is independent and can proceed in parallel.

---

## Open Questions

- [ ] Should `aegis-core` be published to PyPI, or should `aegis-platform` install it directly from the GitHub repository? PyPI publication is cleaner for versioning but adds a release pipeline requirement.
- [ ] Should `aegis-core` expose a compatibility shim (`from aegis import ...` → `from aegis_core import ...`) for a transition period, or should all consumers update immediately? Given the small number of known consumers, immediate update is recommended.
- [ ] Should the demo scripts (`hello_aegis.py`, `basic_runtime_demo.py`) move to `aegis-labs` (per the vision in `README_vision.md`) or to `aegis-core/examples/`? Both are defensible; `aegis-core/examples/` keeps them testable alongside the package.

---

## Success Criteria

1. `aegis-core/core-py/` is the sole location of governance runtime Python code across the entire organization
2. `aegis-governance/aegis-runtime/` contains only `MOVED.md` and a redirect `README.md` — no Python source files
3. `aegis-platform/deploy/aegis/` does not exist; `aegis-platform` installs `aegis-core` as a dependency
4. No `.pyc` files are committed anywhere in the organization
5. `aegis-platform` CI includes a check that prevents re-introduction of local runtime copies
6. All imports across the organization use `aegis_core` — no references to the old `aegis` package name
7. The full `aegis-core` test suite passes
8. The `aegis-platform` deployment functions correctly with `aegis-core` as an external dependency

---

## References

- `aegis-governance/aegis-runtime/MOVED.md` — Existing migration notice (pre-RFC)
- `aegis-core/core-py/pyproject.toml` — Canonical package definition
- `aegis-core/CLAUDE.md` — Repository role and conventions
- `aegis-platform/CLAUDE.md` — Repository role and conventions
- RFC-0002 — Governance Runtime specification
- AEGIS Constitution Article III — Deterministic Enforcement
- AEGIS Constitution Article VII — Auditability

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*
*AEGIS Initiative — Finnoybu IP LLC*

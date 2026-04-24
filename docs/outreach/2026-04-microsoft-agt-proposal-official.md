# AEGIS Governance Profile — Example Contribution to AGT

**Submission:** To be opened as PR to [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit)
**Status:** Draft (2026-04-24) — pending review with Imran Siddique (Group EM, AGT)
**Type:** `examples/` contribution (standalone, runnable)
**Target path:** `examples/aegis-governance-profile/`
**License:** Apache 2.0
**Point of Contact:** Kenneth Tannenbaum, Founder, AEGIS Operations LLC — CLA signer and accountable party for this contribution
**Date Drafted:** 2026-04-24

---

## Summary

A self-contained, runnable AGT example demonstrating **declarative governance
profiles** — a higher-level YAML format describing what an agent (or class of
agents) is permitted to do, with what constraints, under what conditions — and
a standalone Python compiler that emits equivalent [Cedar](https://www.cedarpolicy.com/)
and [OPA/Rego](https://www.openpolicyagent.org/) policies consumable by AGT's
existing `PolicyEvaluator.load_cedar()` and `load_rego()` backends.

The example targets operators who think in domain terms (roles, capabilities,
data scopes, delegation rules, rate limits) rather than in authorization AST
logic, and who want a single declarative source-of-truth that fans out to both
of AGT's external policy backends without hand-authoring either.

## Context

AGT ships with a YAML policy DSL for built-in enforcement, plus first-class
support for external Cedar and Rego backends (per
[docs/tutorials/08-opa-rego-cedar-policies.md](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/tutorials/08-opa-rego-cedar-policies.md)).
Operators running mixed backends today — Cedar for identity/authorization,
Rego for data/resource policy — author each language separately and keep
them in sync by hand. For agentic deployments, the higher-level governance
concepts (role, capability, scope, delegation, rate) are the same across
backends; only the syntax differs.

This example shows one approach to closing that gap: a declarative profile
format modelled on endpoint management patterns (capabilities, limitations,
allowlists/denylists, delegation rules, audit levels) that compiles to both
Cedar and Rego outputs from a single authored source.

## Why a New Format

A reasonable question: AGT already ships a YAML policy DSL — why introduce a
second YAML format? The two are shaped for different audiences.

AGT's built-in YAML DSL is tuned to the toolkit's internal evaluation model —
blocked patterns, PII regex, token/rate limits, content-safety rules. It is
authored by operators who are close to the enforcement runtime.

The AEGIS governance profile is tuned to the authorship level above that:
role-based capability declarations, data-scope allow/deny, delegation rules,
operational constraints — the concepts governance and compliance stakeholders
work in when they describe what an agent (or class of agents) is *authorized*
to do at an organizational level. The profile compiles down to AGT's existing
external backends (Cedar, Rego), so the enforcement plane is unchanged; what
changes is where and how the authorization intent is authored and reviewed.

The two formats are complementary, not substitutes: an operator can ship a
Cedar/Rego policy generated from an AEGIS profile *and* layer AGT's YAML DSL
on top for runtime concerns (PII, token limits, content safety) that the
profile deliberately does not address.

As a concrete illustration of the authoring-surface difference: expressing
"deny any action whose delegation chain traverses more than two principal
boundaries" requires the caller to pre-serialize the delegation chain into
the evaluator's input payload and then encode the traversal check as a
pattern-match rule. An AEGIS profile expresses the same intent as a one-line
declarative constraint under `delegation:`. AGT's Cedar backend can express
the equivalent check natively (Cedar supports entity relationships), so the
gap shows up mainly at the authoring surface — which is exactly the layer the
profile is optimizing.

## Proposed Contribution

```
examples/aegis-governance-profile/
├── README.md                     # Setup, run, expected output, cleanup
├── getting_started.py            # ~150 LOC minimal end-to-end demo
├── profile.yaml                  # Sample AEGIS governance profile
├── compile.py                    # Standalone compiler (no external deps beyond PyYAML)
├── policies/
│   ├── generated.cedar           # Emitted Cedar policy
│   └── generated.rego            # Emitted Rego policy
├── tests/
│   └── test_compilation.py       # Round-trip + semantic-equivalence tests
└── LICENSE                       # Apache 2.0
```

### Sample profile shape

```yaml
# AEGIS Governance Profile — v1
metadata:
  profile_id: research-agent-standard
  profile_version: 1.0.0
  applies_to: principal:role:researcher

capabilities:
  allowed_actions: [web_search, document_read, summarize]
  denied_actions: [file_write, shell_exec]

data_access:
  allowed_scopes: ["public/*", "research/published/*"]
  denied_scopes: ["customer/pii/*", "internal/confidential/*"]
  max_records_per_query: 1000

delegation:
  may_delegate_to: ["role:summarizer"]
  max_delegation_depth: 2

constraints:
  max_operations_per_hour: 500
  require_human_approval_when:
    - action: publish_content
```

### Compilation model

`compile.py` reads `profile.yaml` and emits two files:

- `generated.cedar` — `permit(...)` / `forbid(...)` statements keyed on
  `Action::"<name>"` with conditions derived from delegation depth and
  scope rules.
- `generated.rego` — a `package agentos.aegis` module with
  `default allow = false` and explicit `allow { ... }` rules mirroring
  the Cedar semantics, plus explanation strings for audit output.

The `getting_started.py` demo loads both outputs into AGT's
`PolicyEvaluator` (using `load_cedar()` and `load_rego()`), runs the same
input through each backend, and prints the decision from each — showing the
two PolicyDocuments agree on the evaluation that the profile describes.

### Expected output

Running `python getting_started.py` with the sample profile produces roughly:

```text
[compile] profile.yaml → policies/generated.cedar (14 statements)
[compile] profile.yaml → policies/generated.rego  (package agentos.aegis)

[evaluate] input: {action: web_search, principal: role:researcher, scope: public/*}
  cedar backend: ALLOW  (matched: permit rule #2)
  rego  backend: ALLOW  (matched: data.agentos.aegis.allow → true)

[evaluate] input: {action: file_write, principal: role:researcher, scope: internal/confidential/*}
  cedar backend: DENY   (matched: forbid rule #5)
  rego  backend: DENY   (matched: data.agentos.aegis.allow → false)

[verify] backends agree on 12/12 decisions in the input matrix.
```

## Value Proposition

| Concern | Authoring Cedar + Rego by hand | Authoring an AEGIS profile |
|---|---|---|
| Source of truth | Two files, kept in sync manually | One file, compiled to both |
| Authoring surface | Policy AST | Domain concepts (role, capability, scope) |
| Backend coverage | One language per file | Both AGT external backends from a single source |
| Audit surface | Per-file, per-language | Unified per-profile |
| Review audience | Policy engineers | Governance/compliance stakeholders |

## Constraints Honored

Per the 2026-04-22 scoping agreement with the AGT team, this example:

1. **Has no runtime dependency on `aegis-core`.** The compiler is a single
   Python module with only `pyyaml` as an external dependency. No AEGIS
   Initiative library is imported, bundled, or vendored.
2. **Is decoupled from AGT internals.** The example consumes AGT's public
   `PolicyEvaluator.load_cedar()` / `load_rego()` entry points and emits
   policy text conforming to Cedar and Rego grammars — no AGT-private
   classes, modules, or schemas are referenced.
3. **Is Apache 2.0 licensed.** The example ships with its own LICENSE
   file; no BSL-licensed code is in the dependency chain.
4. **Will be submitted as a PR** following AGT's standard process —
   CLA execution and `CONTRIBUTING.md` compliance before merge.

## Maturity Labelling

Per the guidance in
[examples/AGENTS.md](https://github.com/microsoft/agent-governance-toolkit/blob/main/examples/AGENTS.md)
("do not overstate maturity; label experimental or community-driven examples
clearly"), the example's README will explicitly label the governance profile
format as **community-driven and experimental**, with the caveat that the
profile schema is not yet standardized and may evolve based on adopter
feedback.

## Submission Plan

1. **Pre-PR review** — Share this proposal with Imran Siddique and Jack Batzner
   for scope confirmation before implementation begins.
2. **Implementation** — Build the example to the structure above, targeting a
   lean PR (~600-900 LOC including tests and README).
3. **CLA execution** — Complete the Microsoft CLA as AEGIS Operations LLC.
4. **PR submission** — Open the PR against `main`, reference this proposal in
   the description, follow `CONTRIBUTING.md`.
5. **Iteration** — Respond to AGT team review feedback; target merge without
   requiring aegis-core dependency negotiation.
6. **Long-term maintenance** — AEGIS Operations LLC commits to maintaining
   the example in step with AGT's public API changes, with bugfixes and
   compatibility updates contributed via follow-up PRs.

## Non-Goals

Explicitly out of scope for this contribution:

- Deeper AEGIS ↔ AGT integration (policy source-of-truth proposals, native
  adapter packages, schema federation). Any such direction is a separate
  future conversation, gated on this example landing and on adopter signal.
- Modifying AGT core packages, schemas, or public APIs.
- Adding AEGIS Initiative dependencies to AGT's package graph.
- Benchmark claims — the example demonstrates a pattern, not performance.

## Links

- AGT repository: [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit)
- AGT example contribution guide: [examples/AGENTS.md](https://github.com/microsoft/agent-governance-toolkit/blob/main/examples/AGENTS.md)
- AGT Cedar/Rego tutorial: [docs/tutorials/08-opa-rego-cedar-policies.md](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/tutorials/08-opa-rego-cedar-policies.md)
- Thread context: [2026-04-microsoft-agt-integration.md](./2026-04-microsoft-agt-integration.md)
- AEGIS reference implementation (public): [aegis-initiative/aegis-core](https://github.com/aegis-initiative/aegis-core) — Apache 2.0 as of 2026-04-24

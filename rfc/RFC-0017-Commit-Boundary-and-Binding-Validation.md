# RFC-0017: Commit Boundary and Binding Validation for AGP-1

**RFC:** RFC-0017\
**Status:** Draft\
**Version:** 0.1.0\
**Created:** 2026-04-04\
**Updated:** 2026-04-04\
**Author:** Ken Tannenbaum, AEGIS Initiative / AEGIS Operations LLC\
**Repository:** aegis-governance, aegis-core\
**Target milestone:** Q3 2026\
**Supersedes:** None\
**Superseded by:** None

---

## Summary

AGP-1 currently collapses admissibility evaluation and binding into a single `DECISION_RESPONSE` step. This RFC introduces an explicit **commit boundary** as a first-class protocol concept, separating admissibility (is this transition valid in principle?) from binding (does this transition hold under the state that actually exists at execution time?). It also introduces the **admissible set** — the recognition that governance evaluation may produce multiple valid transitions, not a singleton, and that the protocol must support deterministic resolution over that set.

This RFC aligns AGP-1's execution model vocabulary with Willis (2026), "AI Runtime Governance: Vocabulary," and extends the authority re-derivation work begun in RFC-0011.

---

## Motivation

### The collapse problem

AGP-1's current message flow is:

1. `ACTION_PROPOSE` — agent proposes an action
2. `DECISION_RESPONSE` — governance evaluates and returns ALLOW/DENY/ESCALATE/REQUIRE_CONFIRMATION
3. `EXECUTION_REPORT` — agent reports what happened

The gap is between steps 2 and 3. Once `DECISION_RESPONSE` returns ALLOW, the agent is free to execute. But in concurrent systems, canonical state may have changed between evaluation and execution:

- Another agent may have committed a transition that invalidates the preconditions
- A delegation may have expired
- A quota may have been consumed
- A revocation may have been issued
- A policy state transition may have occurred

AGP-1 has no mechanism to catch these. The `EXECUTION_REPORT` is post-hoc — it tells you what happened, not whether what happened was still admissible at the moment it became real.

### The singleton problem

AGP-1 produces a single decision per proposal. In concurrent multi-agent systems, the governance layer may determine that multiple transitions are admissible under the same canonical state. The current protocol has no concept of an admissible set and no mechanism for deterministic resolution when multiple valid transitions compete for the same commit boundary.

### External validation

Willis (2026) formalizes a 10-step execution model that draws these distinctions precisely [^1]:

- **Proposed Transition** is not execution
- **Admissibility** is not binding
- **Authorization** is not authority at commit
- **Evaluation** is not enforcement
- **Admissible Set** is not a single decision
- **Governance Compilation** is not a system invariant

AGP-1 violates three of these six distinctions in its current form. This is not a theoretical concern — it means AGP-1's governance guarantees degrade in concurrent deployments where state drift between evaluation and execution is non-trivial.

RFC-0011 (Authority Binding Sub-Spec Revision) addresses a subset of this problem — specifically, authority drift and the conditions under which proposal-time authorization does not imply commit-time admissibility. This RFC extends that work to the full protocol flow.

---

## Guide-Level Explanation

### Before this RFC

An agent proposes an action. The governance engine evaluates it and says ALLOW or DENY. If ALLOW, the agent executes. Done.

This works when:
- Only one agent is operating at a time
- State doesn't change between evaluation and execution
- Each proposal has exactly one valid resolution

### After this RFC

The execution model becomes:

1. **Propose** — Agent produces a proposed transition (candidate state mutation, not execution)
2. **Evaluate** — Governance evaluates against canonical state, compiled governance, and derived authority to determine admissibility
3. **Admissible set** — Evaluation may produce one or more admissible transitions (this is the normal case in concurrent systems)
4. **Bind** — At the commit boundary, authority is re-derived from current state, ordering and interaction are resolved, and the admissible set is deterministically resolved
5. **Commit** — Successfully bound transitions mutate canonical state and produce a new baseline for all subsequent evaluation
6. **Report** — Execution artifacts are captured for audit and replay

The key change: **nothing is final until binding**. Admissibility is necessary but not sufficient. A transition that was admissible at evaluation time may not be bindable at commit time because the world moved.

### What this means for implementers

- The `DECISION_RESPONSE` message now represents an **admissibility determination**, not a final authorization to execute
- A new `BIND_REQUEST` / `BIND_RESPONSE` exchange occurs at the commit boundary, where authority is re-derived against current canonical state
- Agents must not treat `DECISION_RESPONSE(ALLOW)` as unconditional permission to execute — they must request binding before committing

---

## Reference-Level Explanation

### New message types

#### `BIND_REQUEST`

Sent by the agent after receiving `DECISION_RESPONSE(ALLOW)` and before executing the proposed action. Requests binding validation against current canonical state.

```
{
  "type": "BIND_REQUEST",
  "proposal_id": "<original proposal ID from ACTION_PROPOSE>",
  "decision_id": "<ID from DECISION_RESPONSE>",
  "agent_state_hash": "<hash of agent's current local state>",
  "timestamp": "<ISO 8601>"
}
```

#### `BIND_RESPONSE`

Returned by the governance engine after re-deriving authority and resolving the admissible set against current canonical state.

```
{
  "type": "BIND_RESPONSE",
  "proposal_id": "<original proposal ID>",
  "decision_id": "<ID from DECISION_RESPONSE>",
  "outcome": "BOUND | REJECTED | SUPERSEDED",
  "rejection_reason": "<if REJECTED: authority_drift | state_conflict | ordering_conflict | delegation_expired | quota_consumed | revocation_issued>",
  "superseded_by": "<if SUPERSEDED: proposal_id of the transition that committed first>",
  "canonical_state_hash": "<hash of canonical state at bind time>",
  "constraints": [ ... ],
  "timestamp": "<ISO 8601>"
}
```

**Outcome semantics:**

- **BOUND** — The transition has been bound to canonical state. The agent MUST now execute. This is the point at which the transition becomes real.
- **REJECTED** — The transition is no longer admissible under current canonical state. The agent MUST NOT execute. The `rejection_reason` field specifies the invalidation condition.
- **SUPERSEDED** — Another transition from the admissible set has already committed, changing canonical state in a way that invalidates this transition. The `superseded_by` field identifies the winning transition.

### Revised protocol flow

```
Agent                          Governance Engine
  |                                   |
  |--- ACTION_PROPOSE -------------->|
  |                                   |-- evaluate admissibility
  |<-- DECISION_RESPONSE ------------|   (against canonical state)
  |    (admissibility determination)  |
  |                                   |
  |--- BIND_REQUEST ---------------->|
  |                                   |-- re-derive authority
  |                                   |-- resolve admissible set
  |                                   |-- validate against CURRENT state
  |<-- BIND_RESPONSE ----------------|
  |    (BOUND / REJECTED / SUPERSEDED)|
  |                                   |
  |    [if BOUND: execute]            |
  |--- EXECUTION_REPORT ------------>|
  |                                   |-- new canonical state produced
```

### Admissible set resolution

When multiple `ACTION_PROPOSE` messages are evaluated concurrently and multiple receive `DECISION_RESPONSE(ALLOW)`, the governance engine maintains an **admissible set** — the set of transitions that are valid under the current canonical state.

At the commit boundary, the engine resolves the admissible set using the following deterministic algorithm:

1. **Re-derive authority** for each candidate against current canonical state
2. **Discard** candidates whose authority no longer holds (REJECTED with reason)
3. **Resolve ordering** — candidates are ordered by proposal timestamp; ties broken by proposal_id lexicographic order
4. **Check interaction** — if committing candidate N would invalidate candidate N+1, mark N+1 as SUPERSEDED
5. **Bind** the first candidate that passes all checks
6. **Re-evaluate** remaining candidates against the new canonical state produced by the bound transition (recursive)

This algorithm is deterministic: same inputs, same ordering, same result. Replay can verify any commit.

### Timing and performance

The `BIND_REQUEST` / `BIND_RESPONSE` exchange introduces latency between admissibility evaluation and execution. Performance targets:

- **Bind validation (simple, no contention):** <50ms (p99)
- **Bind validation (with admissible set resolution):** <200ms (p99)
- **Maximum bind window:** 5000ms — if binding has not completed within 5 seconds of `DECISION_RESPONSE`, the admissibility determination expires and the agent must re-propose

### Interaction with RFC-0011

RFC-0011 defines authority invalidation conditions and failure outcomes. This RFC consumes those definitions:

- RFC-0011's four invalidation conditions (revocation, delegation change, authority epoch drift, policy state transition) map directly to `BIND_RESPONSE` rejection reasons
- RFC-0011's failure outcomes (`authority_not_admissible`, `authority_drift`, `authority_not_captured`) are used as rejection reason values
- RFC-0011's behavioral declaration fields travel from registration through to the bind step

This RFC does not duplicate RFC-0011's normative definitions. It specifies the protocol-level mechanism through which those definitions are enforced.

### Vocabulary alignment

This RFC adopts the following vocabulary from Willis (2026) as normative for AGP-1:

| Willis term | AGP-1 mapping | Status |
|---|---|---|
| Proposed Transition | `ACTION_PROPOSE` | Already aligned |
| Governance Compilation | Policy DSL compilation + capability registry resolution | Already aligned (rename not required) |
| Canonical State | Authoritative system state at evaluation/bind time | New — must be formalized |
| Admissibility | `DECISION_RESPONSE` outcome | Semantics narrowed (was: final decision; now: admissibility determination) |
| Admissible Set | Set of concurrent ALLOW'd proposals pending binding | New concept |
| Binding Validation | `BIND_REQUEST` / `BIND_RESPONSE` | New message types |
| Commit Boundary | The point at which `BIND_RESPONSE(BOUND)` is issued | New concept |
| Bound Transition / Execution | Successfully bound + committed transition | Clarified (was: any executed action) |

---

## Drawbacks

1. **Latency** — The additional `BIND_REQUEST` / `BIND_RESPONSE` round trip adds latency to every governed action. For low-contention single-agent deployments, this overhead provides little benefit.

2. **Complexity** — Agents must now handle three-phase interaction (propose → admissibility → bind) rather than two-phase (propose → decide). SDK implementations become more complex.

3. **Backwards compatibility** — Existing AGP-1 implementations that treat `DECISION_RESPONSE(ALLOW)` as final authorization will need to be updated. A migration path is required.

4. **Admissible set resolution in practice** — Many deployments will never have concurrent proposals competing for the same commit boundary. The admissible set machinery may be over-engineering for common cases.

---

## Alternatives Considered

### 1. Status quo with advisory guidance

Leave AGP-1 as-is and document that `DECISION_RESPONSE(ALLOW)` should be treated as advisory in concurrent deployments. Rejected because advisory guidance without protocol enforcement is exactly the failure mode Willis identifies: "If these distinctions collapse, governance collapses into approximation."

### 2. Optimistic binding with post-hoc validation

Allow agents to execute on `DECISION_RESPONSE(ALLOW)` and validate binding post-hoc via `EXECUTION_REPORT`. If binding would have been rejected, issue a rollback. Rejected because rollback is not always possible (external effects, irreversible actions) and because it violates the principle that governance must hold *before* reality changes.

### 3. Fold into RFC-0011

Extend RFC-0011 to cover the full commit boundary protocol. Rejected because RFC-0011 is scoped to authority binding specifically (claim sets, behavioral declaration, drift conditions). This RFC addresses the broader protocol flow including admissible set resolution, new message types, and vocabulary alignment.

### 4. Optional binding phase

Make `BIND_REQUEST` optional — agents can choose to skip it for low-risk actions. Rejected because optional governance mechanisms tend to become unused governance mechanisms. The binding phase should be mandatory with the governance engine optimizing the fast path (single proposal, no contention → immediate BOUND response).

---

## Compatibility

- **Breaking changes:** `DECISION_RESPONSE(ALLOW)` semantics change from "authorized to execute" to "admissible, pending binding." Agents that execute without binding are non-compliant. This is a breaking change.
- **Migration path:** AGP-1 v1.1 introduces a `protocol_version` negotiation. Agents declaring `agp1/1.0` receive legacy behavior (ALLOW = execute). Agents declaring `agp1/1.1` must use the binding phase. Governance engines MUST support both during the transition period.
- **Deprecation:** `agp1/1.0` behavior (ALLOW = execute) is deprecated upon publication of this RFC and will be removed in AGP-1 v2.0.

---

## Implementation Notes

- **Fast path optimization:** When only one proposal is pending and no concurrent state mutations are detected, the governance engine MAY issue `BIND_RESPONSE(BOUND)` immediately upon receiving `BIND_REQUEST`, without full admissible set resolution. This preserves <50ms latency for the common case.
- **SDK impact:** The aegis-sdk (TypeScript and Python) must be updated to implement the three-phase flow. The SDK should abstract the binding phase so that application developers interact with a single `propose_and_bind()` method that handles the full sequence.
- **Canonical state formalization:** The concept of "canonical state" must be defined normatively. This RFC defers the full definition to a sub-spec but requires at minimum: state hash, timestamp, and monotonic version counter.
- **Dependencies:** RFC-0011 (authority invalidation conditions and failure outcomes) must reach Draft status before this RFC can be finalized. The vocabulary alignment with Willis (2026) should be reviewed by the author if possible.

---

## Open Questions

- [ ] Should the `BIND_REQUEST` include the agent's intended action parameters (enabling the governance engine to validate the *specific* execution plan, not just the proposal category)?
- [ ] What is the maximum admissible set size before the governance engine should reject all and require sequential re-proposal?
- [ ] How does the binding phase interact with `REQUIRE_CONFIRMATION` decisions? Does human confirmation satisfy binding, or must binding still occur after confirmation?
- [ ] Should `BIND_RESPONSE(SUPERSEDED)` include enough information for the agent to re-propose against the new canonical state without a full round trip?
- [ ] Is Willis's vocabulary alignment sufficient, or should AEGIS define its own terminology with explicit mappings? (See RFC-0011 Open Questions on "authority drift" terminology adoption.)

---

## Success Criteria

- Every committed transition in a compliant AGP-1 v1.1 deployment has a corresponding `BIND_RESPONSE(BOUND)` record proving authority was valid at commit time, not just at evaluation time
- Concurrent proposals are resolved deterministically — replay of the same proposals in the same order against the same canonical state produces the same binding outcomes
- No transition can commit if its preconditions were invalidated between admissibility evaluation and binding
- Vocabulary used in AGP-1 specification documents aligns with Willis (2026) normative definitions or provides explicit mapping where AEGIS terminology differs

---

## References

- Willis, J. M., "AI Runtime Governance: Vocabulary — Walkthrough Style," v1.0, April 2026. [Online]. Available: LinkedIn publication.
- AGP-1 Protocol — `aegis-core/protocol/AEGIS_AGP1_INDEX.md`
- RFC-0011 — Authority Binding Sub-Spec Revision
- RFC-0004 — Governance Event Model §5 (Two-Layer Trust)
- RFC-0002 — Governance Runtime (API, state model)
- AEGIS Constitution — `aegis-core/constitution/`

[^1]: Willis, J. M., "AI Runtime Governance: Vocabulary — Walkthrough Style," v1.0, April 2026.

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

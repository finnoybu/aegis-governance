# RFC-0006: AEGIS Claude Code Plugin

**RFC:** RFC-0006\
**Status:** Draft\
**Version:** 0.3.0\
**Created:** 2026-03-08\
**Updated:** 2026-03-26\
**Author:** Kenneth Tannenbaum, AEGIS Operations LLC\
**Repository:** aegis-governance\
**Target milestone:** Q2 2026\
**Supersedes:** None\
**Superseded by:** None

---

## Summary

This RFC defines the AEGIS Claude Code Plugin: a governance enforcement layer for the Claude Code development environment. The plugin intercepts proposed tool actions before execution, evaluates them against a declarative capability registry, and records every governance decision in an append-only, hash-chained audit log. It is the first deployable reference implementation of the AEGIS governance architecture in a real-world execution environment, and the canonical demonstration that AEGIS governance is observable, auditable, and operational — not theoretical.

---

## Motivation

The AEGIS architecture currently exists as a specification and a minimal Python runtime. Neither is immediately demonstrable to a skeptical practitioner. A Claude Code plugin changes that. Claude Code executes real actions: shell commands, file writes, network requests, code execution. These are exactly the action classes AEGIS was designed to govern — the same action classes documented as governance failures in live agentic deployments[^12] and the Excessive Agency risk (OWASP LLM06[^19]) that motivates governing them. A plugin that intercepts those actions, evaluates them, and records decisions is a working governance runtime any developer can install and observe.

---

## Guide-Level Explanation

Install the plugin. From that point forward, every action Claude Code proposes is evaluated before it executes. Shell commands are checked against the capability registry. File writes to sensitive paths are blocked. Network requests are escalated for confirmation. Every decision is written to an audit log you can read.

You can see governance working. That is the point.

---

## Reference-Level Explanation

### Version 1.0 Scope

- `PreToolUse` hook — intercepts all tool executions before they occur
- Local capability registry — declarative JSON definition of permitted, escalated, and denied action classes
- Append-only audit log — hash-chained JSONL record of every governance decision[^1]
- Default-deny posture — actions not explicitly registered are denied[^2]
- Companion `settings.json` — Claude Code native permissions set to permissive; AEGIS is the authoritative governance layer
- Missing registry safe default — deny all with configuration warning if `.aegis/registry.json` is absent

### Version 1.1 Scope (follow-on)

- Slash commands: `/aegis:status`, `/aegis:audit`, `/aegis:register`, `/aegis:explain`
- HMAC signing on audit decision records (Nathan Freestone / Elora pattern — Discussion #73)
- AEGIS plugin marketplace at `github.com/aegis-initiative/aegis-governance`
- Supply chain verification hook

---

### Component 1: PreToolUse Hook (Tool Proxy)

Intercepts: `Bash`, `Write`/`Edit`, `WebFetch`, `Computer`

**AGP-1 governance outcomes:** `ALLOW`, `DENY`, `ESCALATE`, `REQUIRE_CONFIRMATION`

**Resolved output to Claude Code:** `allow` or `deny` only

The hook fires after Claude Code's tool routing but before execution. It is the enforcement boundary — the AEGIS Tool Proxy. All governance decisions originate here. The evaluator produces one of the four AGP-1 outcomes; the Tool Proxy resolves `ESCALATE` and `REQUIRE_CONFIRMATION` by prompting the operator directly (see Component 4), then returns only `allow` or `deny` to Claude Code. The AI never participates in its own governance decisions.

**Implementation language: Node.js.** The hook is invoked by the Claude Code CLI as a child process. Node is used rather than Python to avoid Windows shell invocation path issues (`python` vs `python3` vs Windows Store stub) and to eliminate the `jq` dependency. Node is confirmed present in this environment (npm 2.1.76 is installed).

**Hook invocation:** Claude Code passes event data as JSON to the hook's stdin. The hook reads stdin, evaluates against the registry, resolves any escalation, writes a decision to stdout, and exits.

**Exit code semantics:**

| Exit code | Meaning | Claude Code behavior |
|-----------|---------|---------------------|
| 0 | Structured `allow` or `deny` decision on stdout | Enforces decision |
| 2 | Hard block — missing registry, parse error, unhandled exception | Blocks tool call; stderr fed to Claude as error |
| Other non-zero | Non-blocking error | **Tool call proceeds** — this is a fail-open |

The hook MUST exit with code 2 on any unexpected error. A top-level exception handler ensures unhandled errors produce exit code 2, never exit code 1. This is a safety-critical requirement — any exit code other than 0 or 2 allows the tool call to proceed ungoverned.

**Missing registry behavior:** If `.aegis/registry.json` is absent, the hook MUST deny all tool executions and emit a configuration warning to stderr. Silent fail-open is not permitted.[^2]

**Stdin payload (from Claude Code):**

```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf ./dist"
  },
  "session_id": "uuid-v4",
  "cwd": "/d/dev/aegis-governance",
  "permission_mode": "default"
}
```

**Resolved output (stdout) — always `allow` or `deny`, never `ask`:**

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow | deny",
    "permissionDecisionReason": "Reason shown to Claude"
  }
}
```

---

### Component 2: Capability Registry

Location: `.aegis/registry.json` in project root.

Each capability may include a `tools` array scoping it to specific Claude Code tools. If omitted, the capability matches all tools.

```json
{
  "version": "1.1.0",
  "default_posture": "deny",
  "protected_paths": [".aegis/*", ".claude/*"],
  "capabilities": [
    {
      "id": "CAP-001",
      "name": "shell.read",
      "tools": ["Bash"],
      "pattern": "^(ls|cat|grep|find|echo|pwd|which|env|head|tail|wc|diff|stat|file|type|where|dir)(\\s|$)",
      "decision": "allow"
    },
    {
      "id": "CAP-002",
      "name": "shell.build",
      "tools": ["Bash"],
      "pattern": "^(npm|node|npx|yarn|pnpm|git|make|cmake|cargo|go|python|python3|pip|pip3|mvn|gradle|dotnet)(\\s|$)",
      "decision": "escalate"
    },
    {
      "id": "CAP-003",
      "name": "shell.write",
      "tools": ["Bash"],
      "pattern": "^(rm|mv|cp|mkdir|chmod|chown|dd|truncate|tee|install)(\\s|$)",
      "decision": "escalate"
    },
    {
      "id": "CAP-004",
      "name": "shell.network",
      "tools": ["Bash"],
      "pattern": "^(curl|wget|ssh|scp|nc|ncat|nmap|telnet|ftp|sftp)(\\s|$)",
      "decision": "deny"
    },
    {
      "id": "CAP-005",
      "name": "file.write",
      "tools": ["Write", "Edit"],
      "pattern": ".*",
      "decision": "allow",
      "constraints": {
        "paths_denied": [".env", ".env.*", "*.key", "*.pem", "*.p12", "*.pfx",
                         "*.crt", "*.cer", "*.der", "/etc/*", "~/.ssh/*",
                         "*.secret", "*.credentials", ".aegis/*", ".claude/*"]
      }
    },
    {
      "id": "CAP-006",
      "name": "network.fetch",
      "tools": ["WebFetch"],
      "pattern": ".*",
      "decision": "escalate"
    },
    {
      "id": "CAP-007",
      "name": "computer.action",
      "tools": ["Computer"],
      "pattern": ".*",
      "decision": "escalate"
    }
  ]
}
```

The registry is human-editable without plugin reinstallation. The evaluator reloads it on each hook invocation. This is intentional — operators should be able to adjust governance posture without a deployment cycle.

---

### Component 3: Append-Only Audit Log

Location: `.aegis/audit.jsonl`\
Scope: **Per-project** — persistent across sessions, not scoped to a single Claude Code session.

The audit log is append-only. Records are hash-chained: each record includes the SHA-256 hash of the previous record. This implements the append-only pipeline provenance pattern[^73] — nothing edits previous output; the chain is forensically defensible and tamper-evident.

```json
{
  "timestamp": "2026-03-08T01:47:00.000Z",
  "session_id": "uuid-v4",
  "tool": "Bash",
  "input": "rm -rf ./dist",
  "capability_id": "CAP-002",
  "capability_name": "shell.write",
  "decision": "escalate",
  "reason": "Destructive shell operation requires human confirmation",
  "resolved_by": "operator",
  "resolution": "allow",
  "prev_hash": "sha256:a3f1..."
}
```

> HMAC signing on decision records is deferred to v1.1. The hash chain provides tamper-evidence for v1.0; HMAC signing adds cryptographic non-repudiation for commit decisions. See Discussion #73.

---

### Component 4: Escalation Handling

**v1.0 escalation mechanism: Tool Proxy-owned TTY prompt.**

When the evaluator returns `ESCALATE` or `REQUIRE_CONFIRMATION`, the Tool Proxy resolves the decision by prompting the operator directly via the terminal (TTY), bypassing Claude Code's stdin/stdout which are piped to the hook. Claude Code never sees "ask" — it receives only the resolved `allow` or `deny` after the operator has responded.

This is an architectural requirement, not a convenience choice. If the Tool Proxy returned `ask` to Claude Code, the AI would mediate its own governance decision — presenting the escalation to the human and collecting the response. A drifting, misconfigured, or misbehaving agent must never be in the loop of its own governance. The governance guarantee is unconditional: it does not depend on the AI behaving correctly upstream.

**TTY resolution:** The hook opens `/dev/tty` (Unix) or `CON`/`CONIN$` (Windows) directly to interact with the operator while stdin/stdout remain piped to Claude Code. If no TTY is available (non-interactive environment), the escalation defaults to `deny` — fail-closed.

**Audit completeness:** Because the Tool Proxy owns the entire escalation lifecycle, the audit record includes both the evaluator's original decision (`escalate` or `require_confirmation`) and the operator's resolution (`allow` or `deny`). There are no `resolved_by: pending` holes in the audit trail.

**Independence from Claude Code permissions:** Claude Code may independently be configured to "ask" before certain actions — that is the AI's own behavioral configuration. An AEGIS `DENY` overrides a human-approved Claude Code `ask`. These are two independent systems: Claude Code asks "do you want me to try this?"; AEGIS answers "are you allowed to do this?"

Rationale: synchronous, visible, keeps the developer in the loop, and structurally prevents the AI from participating in governance decisions about its own actions. Queue-based escalation is a v1.1 concern for multi-operator environments.

---

### Component 5: Companion `settings.json`

The plugin ships with a companion `.claude/settings.json` that grants broad tool permissions and configures the AEGIS `PreToolUse` hook. The `hooks` key is a sibling of `permissions` — both are required.

**Rationale:** Claude Code's native `settings.json` is a coarse pattern-matching allowlist with inconsistent enforcement behavior. It does not produce audit records, does not evaluate semantic intent, and does not support escalation. Running two overlapping permission systems creates undefined competition and user confusion. AEGIS replaces `settings.json` as the semantic governance layer.

```json
{
  "permissions": {
    "allow": [
      "Bash(*)",
      "Write(*)",
      "Edit(*)",
      "WebFetch(*)",
      "Computer(*)"
    ],
    "deny": []
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit|WebFetch|Computer",
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/pre_tool_use.js"
          }
        ]
      }
    ]
  }
}
```

> **Note:** This companion `settings.json` makes Claude Code maximally permissive at the native layer. All governance is then enforced by the AEGIS hook and registry. Do not deploy this without a valid `.aegis/registry.json` in place — the missing registry safe default (Component 1) is the only backstop.

Installations that have an existing `settings.json` with project-specific rules should review those rules and migrate any semantic governance intent into the AEGIS capability registry before adopting the companion file.

---

### Governance Cycle ([AGP-1](../aegis-core/protocol/AEGIS_AGP1_INDEX.md) Compliance)

1. **PROPOSAL** — Hook intercepts tool call
2. **EVALUATION** — Evaluator checks registry against tool + input
3. **DECISION** — Allow / Deny / Escalate / Require Confirmation
4. **RESOLUTION** — Escalation resolved by Tool Proxy via operator TTY prompt
5. **RECORD** — Written to audit log with hash chain (complete — no pending holes)
6. **EXECUTION** — If allowed or operator-resolved, tool proceeds

This is a complete AGP-1 governance cycle, observable end-to-end.

---

### Repository Structure

```
aegis-governance/
  plugins/
    claude-code/
      hooks/
        pre_tool_use.js      ← Node.js PreToolUse hook (entry point)
      governance/
        evaluator.js         ← Pattern-matching evaluator
        registry.js          ← Registry loader with safe-default
        audit.js             ← Append-only JSONL audit writer
        escalation.js        ← TTY-based operator escalation handler
      registry/
        default.json         ← Default capability registry
      settings/
        settings.json        ← Companion Claude Code settings
      README.md
```

---

### Installation

```bash
# 1. Create hook and governance directories
mkdir -p .claude/hooks .claude/governance

# 2. Copy hook entry point
cp plugins/claude-code/hooks/pre_tool_use.js .claude/hooks/

# 3. Copy governance modules (required by pre_tool_use.js)
cp plugins/claude-code/governance/registry.js    .claude/governance/
cp plugins/claude-code/governance/evaluator.js   .claude/governance/
cp plugins/claude-code/governance/audit.js       .claude/governance/
cp plugins/claude-code/governance/escalation.js  .claude/governance/

# 4. Apply companion settings.json (backs up existing)
cp .claude/settings.json .claude/settings.json.bak 2>/dev/null || true
cp plugins/claude-code/settings/settings.json .claude/settings.json

# 5. Create AEGIS registry directory and default registry
mkdir -p .aegis
cp plugins/claude-code/registry/default.json .aegis/registry.json
```

Verify the hook is registered:

```bash
# Start Claude Code and check hook fires
claude
# Run any tool — hook should intercept and log to .aegis/audit.jsonl
```

---

## Relationship to Claude Code Native Permissions

Claude Code's native permission system (`settings.json`) and AEGIS operate at different layers and must not be left in undefined competition.

**Claude Code `settings.json`:** Binary tool on/off with pattern matching on command strings. Does not produce audit records. Does not evaluate semantic intent. Enforcement behavior is inconsistent across versions. It is a user convenience mechanism, not a governance system.

**AEGIS capability registry:** Semantic evaluation of what the command does, against whom, in what context. Produces a complete audit trail. Supports graduated outcomes (allow / escalate / deny). Deterministic given identical inputs.

**The boundary:** When AEGIS is active, `settings.json` is set to permissive (Component 5). AEGIS is the authoritative governance layer. The `PreToolUse` hook is the enforcement boundary. `settings.json`'s role is reduced to preventing Claude Code from suppressing tool availability before AEGIS can evaluate it.

If Claude Code's native permission prompts appear alongside AEGIS escalation prompts, it is a configuration error — the companion `settings.json` has not been applied.

---

## Drawbacks

- The plugin operates at the Claude Code layer, not the OS or network layer. A sufficiently determined agent could potentially bypass it through mechanisms not intercepted by the `PreToolUse` hook. This is a known limitation of host-process governance — documented in ATM-1 as a residual risk of logical rather than physical separation.
- The companion `settings.json` makes Claude Code maximally permissive at the native layer. The AEGIS registry is the only enforcement backstop. A misconfigured or absent registry with the companion `settings.json` in place produces an ungoverned environment. The missing registry safe default (Component 1) mitigates this but does not eliminate the risk.
- The default-deny posture will block legitimate actions until the registry is tuned. Initial setup friction is expected.
- Per-action audit log writes add latency to every tool execution.
- Per-project audit log scope means audit records do not aggregate across projects without external tooling. Cross-project visibility is a v1.1 concern.
- Audit log hash chain: if two hook invocations fire simultaneously (e.g., parallel tool calls), both may read the same `prev_hash` and produce a forked chain. For v1.0 single-developer use this is unlikely. A file lock or sequence counter is a v1.1 concern.

---

## Security Considerations

### Shell Command Segmentation (v0.3.0)

Shell commands containing operators (`|`, `&&`, `||`, `;`) are split into segments and each segment is evaluated independently. The most restrictive decision across all segments wins. This prevents bypass attacks where a permitted command (e.g., `echo`) is chained with a denied command (e.g., `curl`) via shell operators.

Commands containing shell metacharacters that embed arbitrary execution (`$(...)`, backticks, `<(...)`) are escalated regardless of the leading command. These constructs can execute any code within an otherwise-permitted command.

### Redirection Target Protection (v0.3.0)

Output redirections (`>`, `>>`) are parsed from shell commands and their target paths are checked against `protected_paths` in the registry. This prevents an agent from using allowed commands (e.g., `echo`) to overwrite governance files via redirection (e.g., `echo {} > .aegis/registry.json`).

### Governance Self-Protection (v0.3.0)

The default registry denies writes to `.aegis/*` and `.claude/*` via both file-write path constraints (CAP-005) and the `protected_paths` redirection check. An agent cannot:

- Overwrite the capability registry (`.aegis/registry.json`)
- Modify the governance hook (`.claude/hooks/pre_tool_use.js`)
- Disable hook configuration (`.claude/settings.json`)

These protections operate at the registry level and can be adjusted by the human operator. They cannot be adjusted by the governed agent.

### Build Tool Escalation (v0.3.0)

Build tools (`python`, `npm`, `node`, `git`, etc.) are classified as `escalate` rather than `allow` in the default registry. These tools can execute arbitrary code — `python -c`, `npm exec`, `node -e` — and must require operator confirmation. Operators may override this for specific build commands in their project registry.

### Known Limitations

- Shell command parsing is heuristic, not a full shell parser. Exotic quoting, heredocs, or non-POSIX shell syntax may not be correctly segmented. The default-deny posture is the backstop.
- The plugin governs tool calls intercepted by the `PreToolUse` hook. Actions outside the hook's scope (e.g., direct OS-level access not mediated by Claude Code tools) are not governed.

---

## Alternatives Considered

**PostToolUse hook only:** Provides audit evidence but no enforcement. Governance that operates after execution is documentation, not control.

**External governance service:** More architecturally pure but adds network dependency and latency to every developer action. RDP-03 embedded pattern is more appropriate for this use case.

**No default registry:** Requires teams to build registries from scratch. Increases adoption friction. The default registry covers the most common development action classes and can be overridden per project.

**Retain `settings.json` as co-governance layer:** Creates two overlapping permission systems with undefined interaction semantics, no unified audit trail, and user confusion when decisions conflict. Rejected in favor of AEGIS as the single authoritative layer.

**Per-session audit log:** Audit records would be lost between sessions, eliminating longitudinal forensic value. Per-project scope is the correct default.

---

## Compatibility

No breaking changes to [RFC-0001](./RFC-0001-AEGIS-Architecture.md) through [RFC-0005](./RFC-0005-Reference-Deployment-Patterns.md). The plugin implements RDP-03 (Embedded Lightweight Pattern) from RFC-0005 in the Claude Code execution environment. It is additive.

**Breaking change from v0.1.0:** The companion `settings.json` and missing registry safe default are new behaviors not present in v0.1.0. Existing installations should review their `settings.json` and registry configuration before upgrading.

---

## Implementation Notes

**Recommended build sequence:**

1. `registry.js` — registry loader with missing-file safe default
2. `evaluator.js` — pattern matching against registry entries; returns AGP-1 decisions
3. `audit.js` — JSONL writer with `prev_hash` chain (using Node `crypto` module — no dependencies)
4. `escalation.js` — TTY-based operator escalation handler for ESCALATE/REQUIRE_CONFIRMATION
5. `pre_tool_use.js` — stdin JSON reader, orchestrates evaluator + escalation + audit, writes resolved decision to stdout
6. `default.json` — default capability registry
7. `settings.json` — companion Claude Code settings with `permissions` + `hooks` keys
8. Integration test: install in project, run `claude`, verify governance cycle fires on first tool use

**Node implementation notes:**
- Read stdin with `process.stdin` — the hook receives one JSON payload per invocation
- No npm dependencies required — use Node built-ins only (`fs`, `crypto`, `path`, `readline`)
- `prev_hash` chain uses `crypto.createHash('sha256')`
- `run()` is async to support TTY-based escalation prompts
- Exit code 0 with JSON stdout for resolved allow/deny decisions only
- Exit code 2 with stderr message for hard blocks (missing registry, parse errors, unhandled exceptions)
- **Any non-zero exit code other than 2 is a fail-open** — Claude Code proceeds with the tool call. The top-level exception handler MUST catch all errors and exit with code 2.
- TTY escalation: open `/dev/tty` (Unix) or `CON`/`CONIN$` (Windows) directly; fall back to deny if unavailable
- Windows path handling: use `path.resolve()` throughout; avoid hardcoded separators

The supply chain verification hook (v1.1) depends on Claude Code plugin manifest capabilities not yet fully documented. Defer until v1.1 scope is confirmed.

The HMAC signing on audit records (v1.1) should reference Nathan Freestone's Elora Taurus Governance Control Plane pattern when implemented. See Discussion #73 and `docs/outreach/2026-03-nathan-freestone-elora-convergence.md`.

---

## Open Questions

- [ ] Should v1.1 marketplace support be in this RFC or RFC-0007?
- [ ] Should cross-project audit aggregation be addressed in this RFC or RFC-0007?
- [ ] Should the default registry be versioned separately from the plugin manifest?

> **Resolved:** *Should escalation present a Claude Code confirmation prompt or write to a separate escalation queue?*
> **Resolution:** Confirmation prompt for v1.0 (synchronous, visible, single-developer context). Queue-based escalation is v1.1 for multi-operator environments.
>
> **Resolved:** *Should the audit log be scoped per-session or per-project?*
> **Resolution:** Per-project. Audit records must persist across sessions for longitudinal forensic value.
>
> **Resolved:** *Should AEGIS co-govern with `settings.json` or replace it as the authoritative layer?*
> **Resolution:** AEGIS replaces `settings.json` as the semantic governance layer. Companion `settings.json` ships with plugin set to permissive. See §Relationship to Claude Code Native Permissions.

---

## Success Criteria

- A developer installs the plugin and immediately has governance enforcement on all tool executions
- Every denied or escalated action produces a readable, hash-chained audit record
- The registry is human-editable without plugin reinstallation
- The plugin demonstrates a complete [AGP-1](../aegis-core/protocol/AEGIS_AGP1_INDEX.md) governance cycle to any observer
- Absent `.aegis/registry.json` produces deny-all with configuration warning, never silent fail-open
- The companion `settings.json` eliminates native Claude Code permission prompts from competing with AEGIS escalation handling

---

## Acknowledgments

The append-only pipeline provenance pattern implemented in the audit log hash chain — each stage appending to a shared artifact, nothing editing previous output, the full chain forensically defensible — was independently developed by **Nathan Freestone** (Founder, The Elora Taurus Project) and identified as an architectural convergence with AEGIS on 2026-03-15. Nathan gave explicit permission for this pattern to be incorporated into the AEGIS specification. See Discussion #73 and `docs/outreach/2026-03-nathan-freestone-elora-convergence.md`.

---

## References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../REFERENCES.md).

[^2]: F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382. See [REFERENCES.md](../REFERENCES.md).

[^12]: N. Shapira et al., "Agents of Chaos," arXiv:2602.20021, Feb. 2026. [Online]. Available: <https://arxiv.org/abs/2602.20021>. See [REFERENCES.md](../REFERENCES.md).

[^19]: OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," Version 2025, Nov. 18, 2024. [Online]. Available: <https://owasp.org/www-project-top-10-for-large-language-model-applications/>. See [REFERENCES.md](../REFERENCES.md).

[^73]: N. Freestone, "Append-Only Pipeline Provenance," AEGIS Discussion #73, aegis-initiative/aegis-governance, Mar. 15, 2026. [Online]. Available: <https://github.com/aegis-initiative/aegis-governance/discussions/73>. See [REFERENCES.md](../REFERENCES.md).

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*\
*AEGIS Initiative — AEGIS Operations LLC*

# AEGIS Claude Code Plugin

**RFC:** RFC-0006 | **Version:** 1.0.0 | **Status:** Draft

Governance enforcement layer for the Claude Code development environment. Intercepts every proposed tool action, evaluates it against a declarative capability registry, and records every decision in an append-only, hash-chained audit log.

Implements RDP-03 (Embedded Lightweight Pattern) from [RFC-0005](../../rfc/RFC-0005-Reference-Deployment-Patterns.md).

---

## Structure

```
plugins/claude-code/
  hooks/
    pre_tool_use.js      ← PreToolUse hook (entry point)
  governance/
    registry.js          ← Registry loader with safe-default
    evaluator.js         ← Pattern-matching evaluator (AGP-1 decisions)
    audit.js             ← Append-only JSONL audit writer
    escalation.js        ← TTY-based operator escalation handler
  registry/
    default.json         ← Default capability registry
  settings/
    settings.json        ← Companion Claude Code settings
  README.md
```

---

## Installation

```bash
# 1. Create hook and governance directories under .claude/
mkdir -p .claude/hooks .claude/governance

# 2. Copy hook entry point
cp plugins/claude-code/hooks/pre_tool_use.js .claude/hooks/

# 3. Copy governance modules (required by pre_tool_use.js)
cp plugins/claude-code/governance/registry.js    .claude/governance/
cp plugins/claude-code/governance/evaluator.js   .claude/governance/
cp plugins/claude-code/governance/audit.js       .claude/governance/
cp plugins/claude-code/governance/escalation.js  .claude/governance/

# 4. Apply companion settings.json (back up any existing file first)
cp .claude/settings.json .claude/settings.json.bak 2>/dev/null || true
cp plugins/claude-code/settings/settings.json .claude/settings.json

# 5. Install default capability registry
mkdir -p .aegis
cp plugins/claude-code/registry/default.json .aegis/registry.json
```

Verify the hook fires:

```bash
# Start Claude Code — on the first tool use, check .aegis/audit.jsonl
claude
```

---

## How It Works

Every time Claude Code proposes a `Bash`, `Write`, `Edit`, `WebFetch`, or `Computer` action, the hook fires **before** execution:

1. **PROPOSAL** — Hook receives the tool event on stdin as JSON
2. **EVALUATION** — `evaluator.js` matches the action against `.aegis/registry.json` (AGP-1 outcomes)
3. **DECISION** — `allow`, `deny`, `escalate`, or `require_confirmation`
4. **RESOLUTION** — If escalated, Tool Proxy prompts the operator directly via TTY
5. **RECORD** — Complete decision written to `.aegis/audit.jsonl` with SHA-256 hash chain
6. **EXECUTION** — Claude Code receives resolved `allow` or `deny` only

The Tool Proxy owns the entire escalation lifecycle. Claude Code never sees "ask" — it receives only resolved decisions. The AI never participates in its own governance.

---

## Capability Registry

Edit `.aegis/registry.json` to adjust governance posture. The registry is reloaded on every hook invocation — no reinstallation required.

**Default posture:** `deny` — actions with no matching capability are denied.

| ID | Name | Tools | Decision |
|----|------|-------|----------|
| CAP-001 | shell.read | Bash | allow |
| CAP-002 | shell.build | Bash | escalate |
| CAP-003 | shell.write | Bash | escalate |
| CAP-004 | shell.network | Bash | deny |
| CAP-005 | file.write | Write, Edit | allow (path constraints apply) |
| CAP-006 | network.fetch | WebFetch | escalate |
| CAP-007 | computer.action | Computer | escalate |

File writes to `.env`, `*.key`, `*.pem`, and other sensitive path patterns are denied regardless of the base capability decision.

---

## Audit Log

Location: `.aegis/audit.jsonl` — persistent across Claude Code sessions.

Each record:

```json
{
  "timestamp": "2026-03-26T12:00:00.000Z",
  "session_id": "uuid-v4",
  "tool": "Bash",
  "input": "rm -rf ./dist",
  "capability_id": "CAP-003",
  "capability_name": "shell.write",
  "decision": "escalate",
  "reason": "Escalated for human review: shell.write (CAP-003) — \"rm -rf ./dist\"",
  "resolved_by": "operator",
  "resolution": "allow",
  "prev_hash": "sha256:a3f1..."
}
```

The `prev_hash` field contains the SHA-256 hash of the preceding record's raw JSON line. The chain is forensically defensible and tamper-evident.

The audit record always includes both the evaluator's original decision and the resolved outcome. There are no `resolved_by: pending` holes — the Tool Proxy completes the record before returning to Claude Code.

> HMAC signing on decision records is deferred to v1.1. See RFC-0006 §Component 3.

---

## Safe Defaults

- **Missing registry:** If `.aegis/registry.json` is absent, all tool executions are denied and a configuration warning is written to stderr. Silent fail-open is not permitted.
- **No matching capability:** Default posture (`deny`) applies.
- **Unhandled exception:** Top-level catch exits with code 2 (block). Never exit code 1 (fail-open).
- **No TTY for escalation:** Defaults to `deny` (fail-closed).
- **Audit failure:** Surfaced as a warning to stderr. The governance decision stands regardless.

---

## Exit Codes

| Code | Meaning | Claude Code behavior |
|------|---------|---------------------|
| 0 | Structured `allow` or `deny` decision on stdout | Enforces decision |
| 2 | Hard block — missing registry, parse error, unhandled exception | Blocks tool call |
| Other | Non-blocking error | **Tool call proceeds (fail-open)** — must be prevented |

---

## Companion `settings.json`

The companion settings file sets Claude Code's native permissions to permissive and registers the AEGIS hook. AEGIS becomes the sole authoritative governance layer.

> **Warning:** Do not deploy the companion `settings.json` without a valid `.aegis/registry.json`. The missing registry safe default is the only backstop in that configuration.

---

*AEGIS™ | RFC-0006 | AEGIS Operations LLC*

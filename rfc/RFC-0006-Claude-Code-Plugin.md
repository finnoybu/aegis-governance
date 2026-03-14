# RFC-0006: AEGIS™ Claude Code Plugin

**RFC:** RFC-0006
**Status:** Draft  
**Version:** 0.1.0  
**Created:** 2026-03-08  
**Updated:** 2026-03-08  
**Author:** Kenneth Tannenbaum, Finnoybu IP LLC  
**Repository:** aegis-governance  
**Target milestone:** Q2 2026  
**Supersedes:** None  
**Superseded by:** None  

---

## Summary

This RFC defines the AEGIS™ Claude Code Plugin: a governance enforcement layer for the Claude Code development environment. The plugin intercepts proposed tool actions before execution, evaluates them against a declarative capability registry, and records every governance decision in an append-only audit log. It is the first deployable reference implementation of the AEGIS governance architecture in a real-world execution environment.

---

## Motivation

The AEGIS™ architecture currently exists as a specification and a minimal Python runtime. Neither is immediately demonstrable to a skeptical practitioner. A Claude Code plugin changes that. Claude Code executes real actions: shell commands, file writes, network requests, code execution. These are exactly the action classes AEGIS™ was designed to govern — the same action classes documented as governance failures in live agentic deployments.[^12] A plugin that intercepts those actions, evaluates them, and records decisions is a working governance runtime any developer can install and observe.

---

## Guide-Level Explanation

Install the plugin. From that point forward, every action Claude Code proposes is evaluated before it executes. Shell commands are checked against the capability registry. File writes to sensitive paths are blocked. Network requests are escalated for confirmation. Every decision is written to an audit log you can read.

You can see governance working. That is the point.

---

## Reference-Level Explanation

### Version 1.0 Scope

- `PreToolUse` hook — intercepts all tool executions before they occur
- Local capability registry — declarative JSON definition of permitted, escalated, and denied action classes
- Append-only audit log — tamper-evident JSONL record of every governance decision[^1]
- Default-deny posture — actions not explicitly registered are denied[^2]

### Version 1.1 Scope (follow-on)

- Slash commands: `/aegis:status`, `/aegis:audit`, `/aegis:register`, `/aegis:explain`
- AEGIS™ plugin marketplace at `github.com/finnoybu/aegis-governance`
- Supply chain verification hook

### Component 1: PreToolUse Hook

Intercepts: `Bash`, `Write`/`Edit`, `WebFetch`, `Computer`

Outputs: `allow`, `deny`, `escalate`

### Component 2: Capability Registry

Location: `.aegis/registry.json` in project root.

```json
{
  "version": "1.0.0",
  "default_posture": "deny",
  "capabilities": [
    {
      "id": "CAP-001",
      "name": "shell.read",
      "pattern": "^(ls|cat|grep|find|echo|pwd|which|env)",
      "decision": "allow"
    },
    {
      "id": "CAP-002",
      "name": "shell.write",
      "pattern": "^(rm|mv|cp|mkdir|chmod|chown|dd|truncate)",
      "decision": "escalate"
    },
    {
      "id": "CAP-003",
      "name": "shell.network",
      "pattern": "^(curl|wget|ssh|scp|nc|nmap)",
      "decision": "deny"
    },
    {
      "id": "CAP-004",
      "name": "file.write",
      "pattern": ".*",
      "decision": "allow",
      "constraints": {
        "paths_denied": [".env", "*.key", "*.pem", "/etc/*", "~/.ssh/*"]
      }
    },
    {
      "id": "CAP-005",
      "name": "network.fetch",
      "pattern": ".*",
      "decision": "escalate"
    }
  ]
}
```

### Component 3: Append-Only Audit Log

Location: `.aegis/audit.jsonl`

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
  "resolved_by": "human",
  "resolution": "allow",
  "prev_hash": "sha256:..."
}
```

### Governance Cycle (AGP-1 Compliance)

1. PROPOSAL — Hook intercepts tool call
2. EVALUATION — Evaluator checks registry
3. DECISION — Allow / Deny / Escalate
4. RECORD — Written to audit log with hash chain
5. EXECUTION — If allowed or human-resolved, tool proceeds

### Repository Structure

```
aegis-governance/
  plugins/
    claude-code/
      manifest.json
      hooks/
        pre_tool_use.py
      governance/
        evaluator.py
        registry.py
        audit.py
      registry/
        default.json
      README.md
  marketplace.json
```

### Installation

```bash
/plugin install github.com/finnoybu/aegis-governance
```

---

## Drawbacks

- The plugin operates at the Claude Code layer, not the OS or network layer. A sufficiently determined agent could potentially bypass it through mechanisms not intercepted by the PreToolUse hook. This is a known limitation of host-process governance.
- The default-deny posture will block legitimate actions until the registry is tuned. Initial setup friction is expected.
- Per-action audit log writes add latency to every tool execution.

---

## Alternatives Considered

**PostToolUse hook only:** Provides audit evidence but no enforcement. Governance that operates after execution is documentation, not control.

**External governance service:** More architecturally pure but adds network dependency and latency to every developer action. RDP-03 embedded pattern is more appropriate for this use case.

**No default registry:** Requires teams to build registries from scratch. Increases adoption friction. The default registry covers the most common development action classes and can be overridden per project.

---

## Compatibility

No breaking changes to RFC-0001 through RFC-0005. The plugin implements RDP-03 (Embedded Lightweight Pattern) in the Claude Code execution environment. It is additive.

---

## Implementation Notes

Begin with the PreToolUse hook and a minimal default registry. Audit log and hash chain can be added incrementally. The aegis-runtime repository provides reference implementations of the evaluator and registry loader that can be adapted for the plugin context.

The supply chain verification hook (v1.1) depends on Claude Code plugin manifest capabilities not yet fully documented. Defer until v1.1 scope is confirmed.

---

## Open Questions

- [ ] Should escalation present a Claude Code confirmation prompt or write to a separate escalation queue?
- [ ] Should the audit log be scoped per-session or per-project?
- [ ] Should the default registry be versioned separately from the plugin?
- [ ] Should v1.1 marketplace support be in this RFC or RFC-0007?

---

## Success Criteria

- A developer installs the plugin and immediately has governance enforcement on all tool executions
- Every denied or escalated action produces a readable audit record
- The registry is human-editable without plugin reinstallation
- The plugin demonstrates a complete AGP-1 governance cycle to any observer

---

## References

**Internal AEGIS documents:**

- [AEGIS Constitution](../aegis-core/constitution/)
- [AGP-1 Protocol](../aegis-core/protocol/AEGIS_AGP1_INDEX.md)
- [SP-1 Decision Integrity](../aegis-core/security-protocols/)
- [RFC-0001 — AEGIS Architecture](./RFC-0001-AEGIS-Architecture.md)
- [RFC-0005 — Reference Deployment Patterns](./RFC-0005-Reference-Deployment-Patterns.md)

**External references:**

- Finnoybu IP LLC, "aegis-runtime," GitHub, 2026. [Online]. Available: <https://github.com/finnoybu/aegis-runtime>
- Anthropic, "Claude Code Plugin Documentation," 2026. [Online]. Available: <https://code.claude.com/docs/en/discover-plugins>

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../REFERENCES.md).

[^2]: F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382. See [REFERENCES.md](../REFERENCES.md).

[^12]: N. Shapira et al., "Agents of Chaos," arXiv:2602.20021, Feb. 2026. [Online]. Available: <https://arxiv.org/abs/2602.20021>. See [REFERENCES.md](../REFERENCES.md).

---

*"Capability without constraint is not intelligence™"*  
*Finnoybu IP LLC — AEGIS™ Initiative*

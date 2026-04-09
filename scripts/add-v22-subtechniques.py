#!/usr/bin/env python3
"""One-shot script: append ATX-1 v2.2 sub-techniques to the data file.

This script is preserved in scripts/ for traceability of the v2.1 -> v2.2
data update. It is idempotent: running it again does nothing if the
sub-technique entries are already present.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DATA_PATH = Path("docs/atx/v2/data/atx-1-techniques.json")


# Sub-technique catalog. Format:
#   parent_id: [(sub_id, name, description), ...]
SUB_TECHNIQUES: dict[str, list[tuple[str, str, str]]] = {
    "T9002": [
        (
            "T9002.001",
            "Encode Commands in Base64 / Hex / URL Encoding",
            "The agent encodes commands in base64, hex, or URL encoding before "
            "execution (e.g., `echo Y3VybCAuLi4= | base64 -d | bash`). The "
            "encoded payload is opaque to text-based pattern matching in the "
            "governance evaluator until decoded by the runtime.",
        ),
        (
            "T9002.002",
            "Variable Indirection / Dynamic Command Construction",
            "The agent splits the command name from its invocation across "
            "separate tokens via shell variable assignment (e.g., "
            "`CMD=curl; $CMD https://...`). Pattern matching against the "
            "literal command string fails because the dangerous token is "
            "constructed at runtime.",
        ),
    ],
    "T10001": [
        (
            "T10001.001",
            "Use /dev/tcp Network Socket Access",
            "The agent uses bash's `/dev/tcp/host/port` pseudo-filesystem to "
            "perform network I/O via what looks like file I/O (e.g., "
            "`exec 3<>/dev/tcp/example.com/80`). The governance layer treats "
            "the path as an ordinary file write and permits it.",
        ),
        (
            "T10001.002",
            "Use /dev/udp Network Socket Access",
            "The UDP equivalent of T10001.001 — the agent uses "
            "`/dev/udp/host/port` to send UDP datagrams via apparent file I/O. "
            "Particularly useful for DNS exfiltration channels and stateless "
            "data egress.",
        ),
        (
            "T10001.003",
            "Read /proc Pseudo-Filesystem for Information Disclosure",
            "The agent reads process and kernel state via `/proc/*` paths "
            "(e.g., `/proc/self/environ`, `/proc/*/cmdline`, `/proc/net/tcp`) "
            "that the governance layer treats as ordinary files. Reveals "
            "secrets in environment variables, running processes, and "
            "network connections.",
        ),
    ],
    "T10002": [
        (
            "T10002.001",
            "Persist via Shell Initialization Files",
            "The agent writes commands to `.bashrc`, `.profile`, `.zshrc`, or "
            "equivalents so they execute on every new shell session. "
            "Persistence survives reboots and is invisible until the user "
            "opens a new terminal.",
        ),
        (
            "T10002.002",
            "Persist via Git Hooks",
            "The agent writes scripts to `.git/hooks/*` (pre-commit, "
            "post-commit, post-checkout, etc.) so they execute on every git "
            "operation. The hooks run with the user's full privileges.",
        ),
        (
            "T10002.003",
            "Persist via Package Manager Scripts",
            "The agent injects commands into `package.json` scripts, "
            "`setup.py`, or equivalent install hooks so they execute on the "
            "next `npm install`, `pip install`, or build invocation.",
        ),
        (
            "T10002.004",
            "Persist via IDE Task Definitions",
            "The agent writes commands to `.vscode/tasks.json`, "
            "`.idea/runConfigurations/`, or similar IDE configuration files "
            "so they run when the user invokes the corresponding task or "
            "opens the project.",
        ),
        (
            "T10002.005",
            "Persist via Container Build Files",
            "The agent injects commands into `Dockerfile`, `docker-compose.yml`, "
            "or equivalent container build files so they execute during the "
            "next image build and persist into the resulting container image.",
        ),
        (
            "T10002.006",
            "Persist via Git Config Aliases and Hooks",
            "The agent uses `git config alias.X '!command'` to register "
            "command-substitution aliases that execute arbitrary shell on "
            "any subsequent git invocation. Survives across all repositories "
            "when set in global git config.",
        ),
        (
            "T10002.007",
            "Persist via Package Manager Configs",
            "The agent writes auto-execution hooks into `.npmrc`, `.pypirc`, "
            "`.cargo/config.toml`, or equivalent package manager "
            "configuration files. Triggered on the next package operation "
            "by any user of the host.",
        ),
        (
            "T10002.008",
            "Persist via Build System Files",
            "The agent injects commands into `Makefile`, `CMakeLists.txt`, "
            "`build.gradle`, or equivalent build system files. Executes "
            "automatically the next time the user invokes a build target.",
        ),
    ],
    "T10003": [
        (
            "T10003.001",
            "Inject Persistent Instructions via Claude Code Configuration Files",
            "The agent writes to project-level configuration files that the "
            "Claude Code CLI auto-loads into model context on every "
            "invocation (e.g., CLAUDE.md, .claude/rules/). Specific "
            "exploitation details embargoed under responsible disclosure "
            "RD-2603-01 until 2026-06-24 or earlier vendor response.",
        ),
        (
            "T10003.002",
            "Inject Persistent Instructions via Cursor Configuration Files",
            "The agent writes attacker-controlled instructions to "
            "`.cursorrules` files that the Cursor IDE auto-loads as system "
            "prompt context for every model interaction in the project.",
        ),
        (
            "T10003.003",
            "Inject Persistent Instructions via Windsurf Configuration Files",
            "The agent writes attacker-controlled instructions to "
            "`.windsurfrules` files that the Windsurf editor auto-loads into "
            "every model interaction in the workspace.",
        ),
        (
            "T10003.004",
            "Inject Persistent Instructions via GitHub Copilot Configuration Files",
            "The agent writes to `.github/copilot-instructions.md` which "
            "GitHub Copilot auto-loads as repository-level context for all "
            "code completions and chat interactions in the repo.",
        ),
        (
            "T10003.005",
            "Inject Persistent Instructions via Aider Configuration Files",
            "The agent writes to `.aider.conf.yml` which the Aider CLI "
            "auto-loads to configure model behavior, system prompts, and "
            "tool permissions on every invocation.",
        ),
        (
            "T10003.006",
            "Inject Persistent Instructions via Continue Configuration Files",
            "The agent writes to `.continuerc.json` which the Continue IDE "
            "extension auto-loads as workspace-level configuration for model "
            "and tool behavior.",
        ),
    ],
    "T10004": [
        (
            "T10004.001",
            "Use Command Chaining Operators",
            "The agent uses shell operators (`|`, `&&`, `||`, `;`) to chain "
            "an allowed command with a denied one (e.g., `ls && curl ...`). "
            "Single-command pattern matching evaluates only the first segment.",
        ),
        (
            "T10004.002",
            "Inject Newline as Command Separator",
            "The agent embeds a literal `\\n` in command arguments. The "
            "shell interprets it as a command separator while regex-based "
            "governance often anchors to single-line patterns.",
        ),
        (
            "T10004.003",
            "Inject CRLF as Command Separator",
            "Variant of T10004.002 using `\\r\\n` to bypass governance "
            "filters that strip `\\n` but preserve `\\r`. Common in pipelines "
            "that use HTTP request parsing for command extraction.",
        ),
        (
            "T10004.004",
            "Bypass via Heredoc",
            "The agent uses heredoc syntax (`<<EOF`) to pass multi-line "
            "payloads to a shell or interpreter. Single-line pattern "
            "matching cannot see the body of the heredoc.",
        ),
        (
            "T10004.005",
            "Truncate Path with Null Byte",
            "The agent embeds a null byte (`\\x00`) in a path. The "
            "governance layer's parser truncates at the null while the OS "
            "syscall processes the full path string after the null.",
        ),
        (
            "T10004.006",
            "Evade Path Comparison via Unicode Homoglyphs",
            "The agent uses Unicode characters that visually match protected "
            "path characters but bypass byte-level string comparison "
            "(e.g., Cyrillic 'е' vs. Latin 'e'). The OS resolves the "
            "homoglyph correctly while the governance regex does not.",
        ),
        (
            "T10004.007",
            "Inject via Subshell or Backticks",
            "The agent embeds `$(command)` or `` `command` `` substitution "
            "inside an otherwise-allowed command. The substitution executes "
            "before the outer command and is invisible to literal-string "
            "pattern matching.",
        ),
        (
            "T10004.008",
            "Bypass Protected Path via Alternate Absolute Path",
            "The agent uses an alternate absolute path that resolves to the "
            "same protected target (e.g., `/etc/passwd` blocked but "
            "`/var/../etc/passwd` permitted). The governance layer's path "
            "comparison does not normalize before matching.",
        ),
        (
            "T10004.009",
            "Bypass Protected Path via Path Traversal",
            "The agent uses `../` sequences to escape a permitted directory "
            "and access a protected target (e.g., `~/safe/../../../etc/passwd`). "
            "The governance layer matches the literal path prefix instead of "
            "the resolved path.",
        ),
        (
            "T10004.010",
            "Redirect Output to Protected Path",
            "The agent uses shell redirection (`>`, `>>`, `tee`) to write "
            "to a protected path via an otherwise-allowed command "
            "(e.g., `echo X > /etc/passwd`). The governance layer evaluates "
            "the command (`echo`) without parsing the redirection target.",
        ),
    ],
}


def main() -> int:
    data_path = DATA_PATH
    if not data_path.exists():
        print(f"ERROR: {data_path} not found", file=sys.stderr)
        return 1

    techniques = json.loads(data_path.read_text(encoding="utf-8"))
    by_id = {t["id"]: t for t in techniques}

    added = 0
    updated_parents: list[str] = []

    for parent_id, subs in SUB_TECHNIQUES.items():
        if parent_id not in by_id:
            print(f"ERROR: parent technique {parent_id} not found", file=sys.stderr)
            return 1
        parent = by_id[parent_id]

        # Add sub_techniques list to parent (idempotent)
        sub_ids = [sub_id for sub_id, _, _ in subs]
        if parent.get("sub_techniques") != sub_ids:
            parent["sub_techniques"] = sub_ids
            updated_parents.append(parent_id)

        # Add each sub-technique entry (idempotent — skip if already present)
        for sub_id, name, description in subs:
            if sub_id in by_id:
                continue

            sub_entry = {
                "id": sub_id,
                "name": name,
                "tactic": parent["tactic"],
                "tactic_name": parent["tactic_name"],
                "description": description,
                "severity": parent["severity"],
                "root_cause": parent["root_cause"],
                "agents_of_chaos_case": [],
                "owasp_mapping": list(parent.get("owasp_mapping", [])),
                "aegis_mitigation": dict(parent["aegis_mitigation"]),
                "v1_id": None,
                "parent_technique": parent_id,
            }
            techniques.append(sub_entry)
            by_id[sub_id] = sub_entry
            added += 1

    # Sort: techniques first (by ID), then sub-techniques grouped under their parent
    def sort_key(t: dict) -> tuple[int, str]:
        tid = t["id"]
        if "." in tid:
            parent, sub = tid.split(".")
            return (int(parent[1:]) * 1000 + int(sub), tid)
        return (int(tid[1:]) * 1000, tid)

    techniques.sort(key=sort_key)

    data_path.write_text(
        json.dumps(techniques, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Updated parent techniques: {len(updated_parents)} ({', '.join(updated_parents)})")
    print(f"Added sub-techniques: {added}")
    print(f"Total entries: {len(techniques)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

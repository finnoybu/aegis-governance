'use strict';

/**
 * AEGIS Claude Code Plugin — evaluator.js
 *
 * Evaluates a proposed tool action against the loaded capability registry.
 * Returns an AGP-1 decision of "allow", "deny", "escalate", or
 * "require_confirmation", along with the matched capability and a
 * human-readable reason.
 *
 * Decision mapping (AGP-1 outcomes):
 *   Registry "allow"                → "allow"
 *   Registry "deny"                 → "deny"
 *   Registry "escalate"             → "escalate"
 *   Registry "require_confirmation" → "require_confirmation"
 *
 * The evaluator returns AGP-1 decisions. The Tool Proxy (pre_tool_use.js) is
 * responsible for resolving escalate/require_confirmation to allow or deny
 * before returning to Claude Code. AEGIS never returns "ask" to the host.
 *
 * Default posture (RFC-0006 §Component 2): deny any action with no matching capability.
 */

/**
 * Extract the matchable subject string from a tool invocation.
 * The subject is what capability patterns are tested against.
 */
const SUBJECT_EXTRACTORS = {
  Bash:      (input) => (input && input.command)   || '',
  Write:     (input) => (input && input.file_path) || '',
  Edit:      (input) => (input && input.file_path) || '',
  WebFetch:  (input) => (input && input.url)       || '',
  Computer:  (input) => (input && (input.action || input.command)) ||
                        safeJson(input).slice(0, 200),
};

/**
 * Tools whose subjects are file paths and must be Unicode-normalized
 * before pattern matching. Without this, homoglyph characters (e.g.
 * U+FF0E FULLWIDTH FULL STOP) bypass capability regex patterns that
 * match ASCII literals like "\." — the normalization was only applied
 * in constraint checking (globMatches/normalizePath), not in pattern
 * matching. See ATX-1 T10004 (parser divergence).
 */
const FILE_PATH_TOOLS = { Write: true, Edit: true };

/**
 * Normalize Unicode homoglyphs and null bytes in a subject string
 * so that capability patterns match consistently. This is lighter
 * than normalizePath() — it does NOT strip drive letters or resolve
 * traversals, so the subject retains its structure for pattern matching.
 *
 * @param {string} subject  Raw subject string
 * @returns {string}        Homoglyph-normalized subject
 */
function normalizeSubjectUnicode(subject) {
  let s = subject;
  // Strip null bytes
  s = s.replace(/\0/g, '');
  // U+FF0E (FULLWIDTH FULL STOP) → .
  s = s.replace(/\uFF0E/g, '.');
  // Collapse consecutive dots created by homoglyph replacement.
  // ".．bashrc" → "..bashrc" → ".bashrc". Safe because: real ".." traversals
  // are handled by normalizePath in globMatches; dual-eval ensures this only
  // applies when it produces a stricter result; a genuine "..filename" is
  // anomalous and worth catching regardless.
  s = s.replace(/\.{2,}/g, '.');
  // U+2215 (DIVISION SLASH), U+2044 (FRACTION SLASH), U+FF0F (FULLWIDTH SOLIDUS) → /
  s = s.replace(/[\u2215\u2044\uFF0F]/g, '/');
  // U+FF3C (FULLWIDTH REVERSE SOLIDUS) → \
  s = s.replace(/\uFF3C/g, '\\');
  return s;
}

function safeJson(v) {
  try { return JSON.stringify(v); } catch (_) { return ''; }
}

// ── Shell command segmentation ──────────────────────────────────────────────
// Splits a shell command into independently evaluable segments.
// Detects: pipes (|), logical operators (&&, ||), semicolons (;),
// newlines (\n, \r\n), command substitution ($(...), `...`),
// and redirection targets.

/**
 * Shell operator pattern — matches |, &&, ||, ;, \n, \r\n as command separators.
 * In bash, a newline is functionally equivalent to ; — it terminates a command.
 * Does not split inside quoted strings (simplified: splits on unquoted operators).
 */
const SHELL_OPERATOR_RE = /\s*(?:\|{1,2}|&&|;|\r?\n)\s*/;

/**
 * Patterns that indicate embedded command execution within a single segment.
 * If any of these appear, the command contains shell metacharacters that could
 * execute arbitrary code beyond the leading command.
 */
const SHELL_METACHAR_RE = /\$\(|\`|<\(/;

/**
 * Redirection pattern — captures the target path of both input and output redirections.
 * Matches: < file, << word, <<< word, > file, >> file, 1> file, 2> file, &> file
 */
const REDIRECT_TARGET_RE = /(?:>{1,2}|[12&]>{1,2}|<{1,3})\s*([^\s;|&]+)/g;

/**
 * Bash built-in network access paths. These open network sockets without
 * invoking any external binary — invisible to command-pattern matching.
 */
const BASH_NETWORK_PATHS_RE = /^\/dev\/(?:tcp|udp)\//;

/**
 * Split a shell command string into segments and redirection targets.
 *
 * @param {string} command  The full shell command string
 * @returns {{ segments: string[], redirectTargets: string[],
 *             hasMetachars: boolean }}
 */
function parseShellCommand(command) {
  const segments = command
    .split(SHELL_OPERATOR_RE)
    .map(function(s) { return s.trim(); })
    .filter(function(s) { return s.length > 0; });

  const hasMetachars = SHELL_METACHAR_RE.test(command);

  const redirectTargets = [];
  let hasBashNetworkAccess = false;
  let match;
  while ((match = REDIRECT_TARGET_RE.exec(command)) !== null) {
    const target = match[1];
    redirectTargets.push(target);
    if (BASH_NETWORK_PATHS_RE.test(target)) {
      hasBashNetworkAccess = true;
    }
  }

  return {
    segments: segments,
    redirectTargets: redirectTargets,
    hasMetachars: hasMetachars,
    hasBashNetworkAccess: hasBashNetworkAccess,
  };
}

const path = require('path');

/**
 * Normalize a file path for constraint matching:
 * - Strip null bytes (prevent truncation attacks)
 * - Normalize Unicode look-alike characters to ASCII equivalents
 * - Resolve . and .. traversals
 * - Normalize separators to forward slash
 * - Strip drive letters and absolute prefixes (C:/, /home/user/, ~/)
 *   to produce a project-relative path for pattern matching
 *
 * @param {string} filePath  The path to normalize
 * @returns {string}         Normalized, project-relative path
 */
function normalizePath(filePath) {
  // Strip null bytes — prevent truncation attacks
  let normalized = filePath.replace(/\0/g, '');

  // Normalize Unicode look-alike separators to ASCII equivalents
  // U+2215 (DIVISION SLASH), U+2044 (FRACTION SLASH), U+FF0F (FULLWIDTH SOLIDUS)
  normalized = normalized.replace(/[\u2215\u2044\uFF0F]/g, '/');
  // U+FF3C (FULLWIDTH REVERSE SOLIDUS)
  normalized = normalized.replace(/\uFF3C/g, '/');
  // U+FF0E (FULLWIDTH FULL STOP) — used as dot homoglyph
  normalized = normalized.replace(/\uFF0E/g, '.');

  // Normalize separators to forward slash
  normalized = normalized.replace(/\\/g, '/');

  // Resolve . and .. traversals (using path.normalize, then re-slash)
  normalized = path.normalize(normalized).replace(/\\/g, '/');

  // Strip Windows drive letter prefix (e.g. C:/)
  normalized = normalized.replace(/^[A-Za-z]:\//, '');

  // Strip Unix absolute prefix
  normalized = normalized.replace(/^\//, '');

  // Strip home-dir prefix variants
  normalized = normalized.replace(/^home\/[^/]+\//, '');
  normalized = normalized.replace(/^Users\/[^/]+\//, '');
  normalized = normalized.replace(/^~\//, '');

  return normalized;
}

/**
 * Minimal glob matcher supporting `*` wildcards.
 * Used for paths_denied constraint evaluation.
 *
 * Handles absolute paths, Windows backslashes, path traversal (../),
 * and case-insensitive matching (for Windows filesystem compatibility).
 *
 * @param {string} pattern  Glob pattern (e.g. "*.key", ".aegis/*", "~/.ssh/*")
 * @param {string} str      The file path to test
 * @returns {boolean}
 */
function globMatches(pattern, str) {
  const normPattern = normalizePath(pattern);
  const normStr     = normalizePath(str);

  // Escape regex metacharacters, then restore * as .*
  const reStr = normPattern
    .replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replace(/\*/g, '.*');

  // Match against full normalized path
  const fullRe = new RegExp('^' + reStr + '$', 'i');
  if (fullRe.test(normStr)) return true;

  // Also try matching against just the tail segments that have the same
  // depth as the pattern (e.g. pattern ".aegis/*" has depth 2, so match
  // against the last 2 segments of the path)
  const patternSegments = normPattern.split('/').length;
  const strSegments     = normStr.split('/');
  if (strSegments.length >= patternSegments) {
    const tail = strSegments.slice(-patternSegments).join('/');
    if (fullRe.test(tail)) return true;
  }

  // Basename-only match (e.g. pattern ".env" matches "src/deep/.env")
  const basename = normStr.split('/').pop() || '';
  return fullRe.test(basename);
}

/**
 * Extract path-like arguments from a shell command string.
 * Used to check Bash command arguments against path constraints.
 *
 * @param {string} command  The full command string (e.g. "cat /proc/self/environ")
 * @returns {string[]}      Array of path-like tokens from the command
 */
function extractPathArguments(command) {
  // Split on whitespace, skip the first token (the command itself),
  // and return tokens that look like paths or globs
  var tokens = command.split(/\s+/).slice(1);
  return tokens.filter(function(t) {
    // Skip flags
    if (t.startsWith('-')) return false;
    // Keep anything that looks like a path
    if (t.includes('/') || t.includes('\\') || t.startsWith('.')) return true;
    // Keep glob patterns that could expand to sensitive files (e.g. *.env, *.key)
    if (/[*?]/.test(t)) return true;
    // Keep tokens with file extensions (e.g. server.key, backup.pem, creds.json)
    // These may match extension-based denied patterns like *.key, *.pem
    if (/\.\w+$/.test(t)) return true;
    return false;
  });
}

/**
 * Check capability constraints. Supports `paths_denied` for both file-path
 * subjects (Write/Edit) and shell command subjects (Bash).
 *
 * For Bash commands, path arguments are extracted from the command string
 * and each is checked independently against the denied patterns.
 *
 * @param {object} constraints  The capability's constraints block
 * @param {string} subject      The resolved subject string for the tool call
 * @param {string} [toolName]   Optional tool name for Bash-specific handling
 * @returns {{ decision: string, reason: string }|null}
 *   Returns a forced deny result if a constraint is violated, otherwise null.
 */
function checkConstraints(constraints, subject, toolName) {
  if (!constraints) return null;

  const denied = constraints.paths_denied;
  if (!Array.isArray(denied) || denied.length === 0) return null;

  // For Bash, check path arguments extracted from the command
  if (toolName === 'Bash') {
    var pathArgs = extractPathArguments(subject);
    for (const arg of pathArgs) {
      // If the argument contains glob wildcards (* or ?), it could expand to
      // match protected files at runtime. The evaluator can't predict expansion,
      // so check if the glob pattern COULD overlap with any denied pattern.
      // Use bidirectional matching: check if the denied pattern matches the arg
      // AND if the arg (as a glob) could match the denied pattern's literal form.
      if (/[*?]/.test(arg)) {
        for (const pattern of denied) {
          // Check both directions: does the denied pattern match the glob arg,
          // OR does the glob arg match the denied pattern's basename?
          const argBase = arg.split('/').pop() || arg;
          const patBase = pattern.split('/').pop() || pattern;
          if (globMatches(pattern, arg) || globMatches(argBase, patBase) || globMatches(arg, patBase)) {
            return {
              decision: 'deny',
              reason:   `Glob argument "${arg}" could expand to match denied pattern "${pattern}"`,
            };
          }
        }
        continue;
      }
      for (const pattern of denied) {
        if (globMatches(pattern, arg)) {
          return {
            decision: 'deny',
            reason:   `Argument "${arg}" matches denied pattern "${pattern}"`,
          };
        }
      }
    }
    return null;
  }

  // For Write/Edit and others, check the subject directly
  for (const pattern of denied) {
    if (globMatches(pattern, subject)) {
      return {
        decision: 'deny',
        reason:   `Path "${subject}" matches denied pattern "${pattern}"`,
      };
    }
  }

  return null;
}

// ── Decision severity ranking ───────────────────────────────────────────────
// Used to select the most restrictive decision across multiple segments.
const DECISION_SEVERITY = { allow: 0, require_confirmation: 1, escalate: 2, deny: 3 };

/**
 * Evaluate a single subject string against the capability registry.
 * Returns the first matching capability result.
 */
function evaluateSingle(capabilities, defaultPosture, toolName, subject) {
  for (const cap of capabilities) {
    if (Array.isArray(cap.tools) && cap.tools.length > 0) {
      if (!cap.tools.includes(toolName)) continue;
    }

    let patternMatched = false;
    try {
      patternMatched = new RegExp(cap.pattern).test(subject);
    } catch (_) {
      continue;
    }

    if (!patternMatched) continue;

    const constraintResult = checkConstraints(cap.constraints, subject, toolName);
    if (constraintResult) {
      return {
        decision:         constraintResult.decision,
        capability_id:    cap.id   || null,
        capability_name:  cap.name || null,
        reason:           constraintResult.reason,
      };
    }

    const decision = cap.decision || defaultPosture;
    return {
      decision:        decision,
      capability_id:   cap.id   || null,
      capability_name: cap.name || null,
      reason:          buildReason(cap, toolName, subject, decision),
    };
  }

  return {
    decision:         defaultPosture,
    capability_id:    null,
    capability_name:  null,
    reason: `No registered capability matched ${toolName} action` +
            (subject ? ` ("${subject.slice(0, 60)}")` : '') +
            `. Default posture: ${defaultPosture}.`,
  };
}

/**
 * Evaluate a tool action against the capability registry.
 *
 * For Bash commands, the evaluator splits the command on shell operators
 * (|, &&, ||, ;) and evaluates each segment independently. The most
 * restrictive decision across all segments wins. Commands containing
 * shell metacharacters ($(...), backticks) that could execute arbitrary
 * embedded code are escalated. Redirection targets are checked against
 * path constraints.
 *
 * @param {object} registry   Parsed registry (from registry.js loadRegistry)
 * @param {string} toolName   Claude Code tool name (e.g. "Bash", "Write")
 * @param {object} toolInput  Tool input payload from the hook event
 * @returns {{ decision: string, capability_id: string|null,
 *             capability_name: string|null, reason: string }}
 */
function evaluate(registry, toolName, toolInput) {
  const defaultPosture = registry.default_posture || 'deny';
  const capabilities   = Array.isArray(registry.capabilities) ? registry.capabilities : [];

  const extractor  = SUBJECT_EXTRACTORS[toolName];
  const rawSubject = extractor ? extractor(toolInput) : safeJson(toolInput).slice(0, 200);

  // For file-path tools (Write/Edit), evaluate BOTH the raw subject AND a
  // Unicode-normalized variant against the capability registry. Use the more
  // restrictive result. This catches homoglyph attacks (T10004) where e.g.
  // U+FF0E (fullwidth dot) replaces ASCII dot in ".bashrc", without breaking
  // cases where normalization produces a different filename (e.g. ".．bashrc"
  // normalizing to "..bashrc" — a different file that wouldn't match patterns).
  const subject = rawSubject;
  const normalizedSubject = FILE_PATH_TOOLS[toolName]
    ? normalizeSubjectUnicode(rawSubject)
    : null;

  // ── Bash-specific: shell command segmentation ───────────────────────────
  if (toolName === 'Bash' && subject) {
    const parsed = parseShellCommand(subject);

    // If the command contains shell metacharacters ($(...), backticks, <(...))
    // that embed arbitrary execution, escalate the entire command
    if (parsed.hasMetachars) {
      return {
        decision:         'escalate',
        capability_id:    null,
        capability_name:  null,
        reason:           'Command contains shell metacharacters that could execute ' +
                          'arbitrary embedded code: "' + subject.slice(0, 60) + '"',
      };
    }

    // Embedded newlines in a command string are a parser divergence attack
    // (ATX-1 T10004). In bash, \n is equivalent to ; — it terminates a command.
    // An embedded newline can smuggle a second command past single-line pattern
    // matching. Legitimate multi-command sequences use && or ; explicitly.
    // Hard deny — this is evasion, not a legitimate compound command.
    if (/\r?\n/.test(subject)) {
      return {
        decision:         'deny',
        capability_id:    null,
        capability_name:  null,
        reason:           'Command contains embedded newline (parser divergence ' +
                          'attack — T10004): "' + subject.replace(/\n/g, '\\n').slice(0, 60) + '"',
      };
    }

    // Check for bash built-in network access via /dev/tcp or /dev/udp.
    // These open sockets without invoking any external binary — invisible
    // to command-pattern matching.
    if (parsed.hasBashNetworkAccess) {
      return {
        decision:         'deny',
        capability_id:    null,
        capability_name:  null,
        reason:           'Command uses bash built-in network access (/dev/tcp or /dev/udp): "' +
                          subject.slice(0, 60) + '"',
      };
    }

    // Check redirection targets against path constraints
    for (const target of parsed.redirectTargets) {
      const pathResult = checkConstraints(
        { paths_denied: registry.protected_paths || [] },
        target
      );
      if (pathResult) {
        return {
          decision:         'deny',
          capability_id:    null,
          capability_name:  null,
          reason:           'Redirection target ' + pathResult.reason,
        };
      }
    }

    // If the command has multiple segments, evaluate each independently
    // and return the most restrictive result
    if (parsed.segments.length > 1) {
      let worstResult = null;
      let worstSeverity = -1;

      for (const segment of parsed.segments) {
        const segResult = evaluateSingle(capabilities, defaultPosture, toolName, segment);
        const severity  = DECISION_SEVERITY[segResult.decision] !== undefined
          ? DECISION_SEVERITY[segResult.decision]
          : 3; // unknown decisions treated as deny-level

        if (severity > worstSeverity) {
          worstSeverity = severity;
          worstResult   = segResult;
        }
      }

      // Annotate the reason to indicate this was a compound command
      if (worstResult && worstSeverity > 0) {
        worstResult.reason = 'Compound command — most restrictive segment: ' +
                             worstResult.reason;
      }

      return worstResult;
    }
  }

  // ── Standard single-subject evaluation ──────────────────────────────────
  // For file-path tools, evaluate both the raw and normalized subjects and
  // return the MORE RESTRICTIVE result. This catches Unicode homoglyph
  // attacks without false-positives from normalization artifacts.
  if (normalizedSubject && normalizedSubject !== subject) {
    const rawResult  = evaluateSingle(capabilities, defaultPosture, toolName, subject);
    const normResult = evaluateSingle(capabilities, defaultPosture, toolName, normalizedSubject);

    const rawSeverity  = DECISION_SEVERITY[rawResult.decision]  !== undefined
      ? DECISION_SEVERITY[rawResult.decision]  : 3;
    const normSeverity = DECISION_SEVERITY[normResult.decision] !== undefined
      ? DECISION_SEVERITY[normResult.decision] : 3;

    if (normSeverity > rawSeverity) {
      normResult.reason = 'Unicode-normalized path matched stricter rule: ' +
                          normResult.reason;
      return normResult;
    }
    return rawResult;
  }

  return evaluateSingle(capabilities, defaultPosture, toolName, subject);
}

function buildReason(cap, toolName, subject, decision) {
  const verb = {
    allow: 'Permitted',
    deny: 'Denied',
    escalate: 'Escalated for human review',
    require_confirmation: 'Requires operator confirmation',
  };
  const display = subject.length > 60 ? subject.slice(0, 60) + '…' : subject;
  return `${verb[decision] || decision}: ${cap.name} (${cap.id}) — "${display}"`;
}

module.exports = { evaluate };

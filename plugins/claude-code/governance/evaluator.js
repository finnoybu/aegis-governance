'use strict';

/**
 * AEGIS Claude Code Plugin — evaluator.js
 *
 * Evaluates a proposed tool action against the loaded capability registry.
 * Returns a decision of "allow", "deny", or "ask" (escalate), along with the
 * matched capability and a human-readable reason.
 *
 * Decision mapping:
 *   Registry "allow"    → "allow"
 *   Registry "deny"     → "deny"
 *   Registry "escalate" → "ask"   (Claude Code confirmation prompt)
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

function safeJson(v) {
  try { return JSON.stringify(v); } catch (_) { return ''; }
}

/**
 * Minimal glob matcher supporting `*` wildcards and leading `~/` expansion.
 * Used for paths_denied constraint evaluation.
 *
 * @param {string} pattern  Glob pattern (e.g. "*.key", "/etc/*", "~/.ssh/*")
 * @param {string} str      The file path to test
 * @returns {boolean}
 */
function globMatches(pattern, str) {
  // Normalise home-dir prefix to allow matching regardless of expansion
  const normPattern = pattern.replace(/^~\//, '');
  const normStr     = str.replace(/^~\//, '').replace(/^\/home\/[^/]+\//, '');

  // Escape regex metacharacters, then restore * as .*
  const reStr = normPattern
    .replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replace(/\*/g, '.*');

  // Match against full string, or as a filename-only match
  const fullRe = new RegExp('^' + reStr + '$', 'i');
  if (fullRe.test(normStr)) return true;

  // Also match the basename alone (e.g. pattern ".env" matches "src/.env")
  const basename = normStr.replace(/^.*[/\\]/, '');
  return fullRe.test(basename);
}

/**
 * Check capability constraints. Currently only `paths_denied` is implemented.
 *
 * @param {object} constraints  The capability's constraints block
 * @param {string} subject      The resolved subject string for the tool call
 * @returns {{ decision: string, reason: string }|null}
 *   Returns a forced deny result if a constraint is violated, otherwise null.
 */
function checkConstraints(constraints, subject) {
  if (!constraints) return null;

  const denied = constraints.paths_denied;
  if (Array.isArray(denied)) {
    for (const pattern of denied) {
      if (globMatches(pattern, subject)) {
        return {
          decision: 'deny',
          reason:   `Path "${subject}" matches denied pattern "${pattern}"`,
        };
      }
    }
  }

  return null;
}

/**
 * Evaluate a tool action against the capability registry.
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

  const extractor = SUBJECT_EXTRACTORS[toolName];
  const subject   = extractor ? extractor(toolInput) : safeJson(toolInput).slice(0, 200);

  for (const cap of capabilities) {
    // If the capability declares a tool scope, skip mismatches
    if (Array.isArray(cap.tools) && cap.tools.length > 0) {
      if (!cap.tools.includes(toolName)) continue;
    }

    // Pattern test
    let patternMatched = false;
    try {
      patternMatched = new RegExp(cap.pattern).test(subject);
    } catch (_) {
      // Malformed regex — skip this capability
      continue;
    }

    if (!patternMatched) continue;

    // Constraint check (may override the capability's base decision)
    const constraintResult = checkConstraints(cap.constraints, subject);
    if (constraintResult) {
      return {
        decision:         constraintResult.decision,
        capability_id:    cap.id   || null,
        capability_name:  cap.name || null,
        reason:           constraintResult.reason,
      };
    }

    // Map registry decision to hook output decision
    const rawDecision = cap.decision || defaultPosture;
    const decision    = rawDecision === 'escalate' ? 'ask' : rawDecision;

    return {
      decision,
      capability_id:   cap.id   || null,
      capability_name: cap.name || null,
      reason:          buildReason(cap, toolName, subject, decision),
    };
  }

  // No capability matched — apply default posture
  const defaultDecision = defaultPosture === 'escalate' ? 'ask' : defaultPosture;
  return {
    decision:         defaultDecision,
    capability_id:    null,
    capability_name:  null,
    reason: `No registered capability matched ${toolName} action` +
            (subject ? ` ("${subject.slice(0, 60)}")` : '') +
            `. Default posture: ${defaultPosture}.`,
  };
}

function buildReason(cap, toolName, subject, decision) {
  const verb = { allow: 'Permitted', deny: 'Denied', ask: 'Requires human confirmation' };
  const display = subject.length > 60 ? subject.slice(0, 60) + '…' : subject;
  return `${verb[decision] || decision}: ${cap.name} (${cap.id}) — "${display}"`;
}

module.exports = { evaluate };

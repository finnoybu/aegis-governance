#!/usr/bin/env node
'use strict';

/**
 * AEGIS Claude Code Plugin — pre_tool_use.js
 *
 * PreToolUse hook. Claude Code invokes this script as a child process before
 * executing any tool matched by the hook configuration in .claude/settings.json.
 *
 * Protocol (RFC-0006 §Component 1):
 *   - Stdin:   One JSON payload (Claude Code hook event)
 *   - Stdout:  One JSON governance decision (hookSpecificOutput envelope)
 *   - Exit 0:  Structured allow/deny/ask decision written to stdout
 *   - Exit 2:  Hard failure (missing registry, stdin parse error) — stderr message
 *
 * Governance cycle (AGP-1):
 *   PROPOSAL → EVALUATION → DECISION → RECORD → EXECUTION
 *
 * Dependencies: Node.js built-ins only (fs, crypto, path).
 * No npm packages required.
 *
 * Installation note: this script requires the governance/ directory to be
 * available at ../governance/ relative to __dirname. When deploying to
 * .claude/hooks/, copy the governance/ directory to .claude/governance/.
 * See plugins/claude-code/README.md for full installation instructions.
 */

const path = require('path');

// Resolve governance modules relative to this file's location so the script
// works both from the source tree and from the installed .claude/hooks/ location.
const governanceDir = path.join(__dirname, '..', 'governance');
const { loadRegistry } = require(path.join(governanceDir, 'registry.js'));
const { evaluate }     = require(path.join(governanceDir, 'evaluator.js'));
const { writeRecord }  = require(path.join(governanceDir, 'audit.js'));

/**
 * Extract a short, log-safe input summary for the audit record.
 */
function inputSummary(toolName, toolInput) {
  if (!toolInput) return '';
  switch (toolName) {
    case 'Bash':     return toolInput.command   || '';
    case 'Write':
    case 'Edit':     return toolInput.file_path || '';
    case 'WebFetch': return toolInput.url       || '';
    case 'Computer': return toolInput.action || toolInput.command || '';
    default:
      try { return JSON.stringify(toolInput).slice(0, 200); } catch (_) { return ''; }
  }
}

// ── Main ──────────────────────────────────────────────────────────────────────

let rawInput = '';
process.stdin.setEncoding('utf8');

process.stdin.on('data', function(chunk) {
  rawInput += chunk;
});

process.stdin.on('end', function() {
  // 1. Parse the hook event from stdin
  let event;
  try {
    event = JSON.parse(rawInput);
  } catch (err) {
    process.stderr.write(
      '[AEGIS] ERROR: Failed to parse hook event from stdin: ' + err.message + '\n'
    );
    process.exit(2);
  }

  // 2. Resolve project root from event.cwd, falling back to process.cwd()
  const cwd         = (event.cwd && typeof event.cwd === 'string') ? event.cwd : process.cwd();
  const projectRoot = path.resolve(cwd);

  // 3. Load registry — exits with code 2 if absent or invalid (RFC-0006 §Component 1)
  const registry = loadRegistry(projectRoot);

  // 4. Evaluate the proposed action against the registry
  const toolName  = event.tool_name  || '';
  const toolInput = event.tool_input || {};
  const result    = evaluate(registry, toolName, toolInput);

  // 5. Write append-only audit record with hash chain (RFC-0006 §Component 3)
  try {
    writeRecord(projectRoot, {
      timestamp:        new Date().toISOString(),
      session_id:       event.session_id   || null,
      tool:             toolName,
      input:            inputSummary(toolName, toolInput),
      capability_id:    result.capability_id,
      capability_name:  result.capability_name,
      decision:         result.decision,
      reason:           result.reason,
      // resolved_by / resolution: "ask" decisions are resolved by the human
      // confirmation prompt; final resolution is not known at hook invocation time
      resolved_by:      result.decision === 'ask' ? 'pending' : 'aegis',
      resolution:       result.decision === 'ask' ? null       : result.decision,
    });
  } catch (auditErr) {
    // Audit failure is surfaced as a warning but does not alter the governance
    // decision — the evaluator result still stands.
    process.stderr.write('[AEGIS] WARNING: Audit write failed: ' + auditErr.message + '\n');
  }

  // 6. Write structured decision to stdout (RFC-0006 §Component 1)
  const output = {
    hookSpecificOutput: {
      hookEventName:              'PreToolUse',
      permissionDecision:         result.decision,
      permissionDecisionReason:   result.reason,
    },
  };

  process.stdout.write(JSON.stringify(output) + '\n');
  process.exit(0);
});

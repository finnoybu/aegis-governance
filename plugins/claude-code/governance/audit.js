'use strict';

/**
 * AEGIS Claude Code Plugin — audit.js
 *
 * Append-only, hash-chained JSONL audit log.
 *
 * Location:  <projectRoot>/.aegis/audit.jsonl
 * Scope:     Per-project, persistent across sessions (RFC-0006 §Component 3)
 *
 * Hash chain: each record includes the SHA-256 hash of the raw JSON line of
 * the preceding record (prev_hash: "sha256:<hex>"). The first record in a new
 * log has prev_hash: null. This implements the append-only pipeline provenance
 * pattern — nothing edits previous output; the chain is forensically defensible
 * and tamper-evident. [^73]
 *
 * HMAC signing on decision records is deferred to v1.1 per RFC-0006 §Component 3.
 *
 * [^73]: N. Freestone, "Append-Only Pipeline Provenance," AEGIS Discussion #73, Mar. 2026.
 */

const fs     = require('fs');
const path   = require('path');
const crypto = require('crypto');

/**
 * Read the last non-empty line from the audit log and return its SHA-256 hash.
 * Returns null if the file does not exist or is empty.
 *
 * @param {string} auditPath  Absolute path to audit.jsonl
 * @returns {string|null}     Hex digest, or null
 */
function getLastRecordHash(auditPath) {
  if (!fs.existsSync(auditPath)) return null;

  let content;
  try {
    content = fs.readFileSync(auditPath, 'utf8');
  } catch (_) {
    return null;
  }

  const lines = content.split('\n').filter(function(l) { return l.trim().length > 0; });
  if (lines.length === 0) return null;

  const lastLine = lines[lines.length - 1];
  return crypto.createHash('sha256').update(lastLine, 'utf8').digest('hex');
}

/**
 * Append a governance decision record to the project's audit log.
 *
 * The record is augmented with a prev_hash field before writing. The function
 * creates .aegis/ if it does not exist.
 *
 * @param {string} projectRoot  Absolute path to the project root.
 * @param {object} record       Governance decision fields (see RFC-0006 §Component 3).
 * @returns {object}            The final record as written (including prev_hash).
 * @throws {Error}              If the append fails (caller decides how to handle).
 */
function writeRecord(projectRoot, record) {
  const aegisDir  = path.resolve(projectRoot, '.aegis');
  const auditPath = path.resolve(aegisDir, 'audit.jsonl');

  if (!fs.existsSync(aegisDir)) {
    fs.mkdirSync(aegisDir, { recursive: true });
  }

  const prevHash = getLastRecordHash(auditPath);

  const entry = Object.assign({}, record, {
    prev_hash: prevHash ? 'sha256:' + prevHash : null,
  });

  // append — flag 'a' guarantees we never truncate existing content
  fs.appendFileSync(auditPath, JSON.stringify(entry) + '\n', { encoding: 'utf8', flag: 'a' });

  return entry;
}

module.exports = { writeRecord };

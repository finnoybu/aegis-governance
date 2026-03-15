'use strict';

/**
 * AEGIS Claude Code Plugin — registry.js
 *
 * Loads and validates .aegis/registry.json from the project root.
 * If the file is absent or unparseable, emits a warning to stderr and
 * exits with code 2. Silent fail-open is not permitted (RFC-0006 §Component 1).
 */

const fs = require('fs');
const path = require('path');

/**
 * Load the capability registry from <projectRoot>/.aegis/registry.json.
 *
 * @param {string} projectRoot  Absolute path to the project root directory.
 * @returns {object}            Parsed registry object.
 *
 * On any failure (missing file, read error, parse error, invalid structure)
 * this function writes a diagnostic to stderr and calls process.exit(2).
 */
function loadRegistry(projectRoot) {
  const registryPath = path.resolve(projectRoot, '.aegis', 'registry.json');

  if (!fs.existsSync(registryPath)) {
    process.stderr.write(
      '[AEGIS] CONFIGURATION WARNING: .aegis/registry.json not found at ' +
      registryPath + '.\n' +
      '[AEGIS] All tool executions will be denied until the registry is installed.\n' +
      '[AEGIS] Copy plugins/claude-code/registry/default.json to .aegis/registry.json to begin.\n'
    );
    process.exit(2);
  }

  let raw;
  try {
    raw = fs.readFileSync(registryPath, 'utf8');
  } catch (err) {
    process.stderr.write(
      '[AEGIS] ERROR: Could not read registry at ' + registryPath + ': ' + err.message + '\n'
    );
    process.exit(2);
  }

  let registry;
  try {
    registry = JSON.parse(raw);
  } catch (err) {
    process.stderr.write(
      '[AEGIS] ERROR: Registry parse error in ' + registryPath + ': ' + err.message + '\n'
    );
    process.exit(2);
  }

  if (!registry || typeof registry !== 'object') {
    process.stderr.write('[AEGIS] ERROR: Registry must be a JSON object.\n');
    process.exit(2);
  }

  if (!Array.isArray(registry.capabilities)) {
    process.stderr.write('[AEGIS] ERROR: Registry missing required "capabilities" array.\n');
    process.exit(2);
  }

  return registry;
}

module.exports = { loadRegistry };

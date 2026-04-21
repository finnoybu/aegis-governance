#!/usr/bin/env node
/**
 * sync-references.mjs
 *
 * Regenerate site/src/content/docs/references.md from the canonical
 * repo-root REFERENCES.md. Runs automatically as a prebuild step so the
 * published /references/ page never drifts from the repository source.
 *
 * Input:  <repo-root>/REFERENCES.md
 * Output: <site>/src/content/docs/references.md
 *
 * Transformations:
 *   1. Strip the "See [CLAUDE.md](CLAUDE.md) …" line (repo-internal reference).
 *   2. Drop the "## How to Cite" section and its preceding separator — its
 *      instructions reference repository workflows that don't apply on the site.
 *   3. Drop the trailing "Part of / Maintained by / Last Updated / Entries"
 *      metadata block (repo-level metadata, not page-level).
 *   4. Prepend Astro content-collection frontmatter.
 *   5. Prepend a cspell:ignore directive that covers author surnames
 *      appearing in the bibliography (otherwise cspell CI fails on every build).
 *   6. Append a canonical-source footer pointing back at the repo file.
 */

import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, relative } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SITE_ROOT = resolve(__dirname, '..');
const REPO_ROOT = resolve(SITE_ROOT, '..');
const SOURCE = resolve(REPO_ROOT, 'REFERENCES.md');
const TARGET = resolve(SITE_ROOT, 'src/content/docs/references.md');

const FRONTMATTER = `---
title: References
description: Canonical bibliography for the AEGIS governance framework — all papers cited in specs, RFCs, threat model, and protocol documents.
---
`;

// Author surnames appearing in the bibliography that cspell's default dictionary
// flags as unknown words. Keep this list sorted and extend when new authors are
// cited in the repo REFERENCES.md.
const CSPELL_IGNORE_WORDS = [
  'Agbemabiese', 'Amodei', 'Arunachalam', 'Arzt', 'Baird',
  'Batzner', 'Bodden', 'Borchert', 'Boyd', 'Bradner',
  'Byun', 'Chaudhary', 'Connelly', 'Engin', 'Gaithersburg',
  'Gaurav', 'Hardt', 'Heikkonen', 'Imran', 'Josang',
  'Kayyidavazhiyil', 'Kuo', 'Leike', 'Lodderstedt', 'Lovat',
  'Majumdar', 'Mitchell', 'Niyato', 'Panda', 'Parecki',
  'Pearce', 'Pinisetty', 'Rasthofer', 'Roop', 'Sabadello',
  'Sakimura', 'Saltzer', 'Santikellur', 'Schneider', 'Schroeder',
  'Shapira', 'Shuhan', 'Siddique', 'Sporny', 'Tapiero',
  'Tetragon', 'Ukil', 'Woodruff',
];

const CANONICAL_FOOTER = `## Canonical Source

This bibliography is regenerated on every build from \`REFERENCES.md\` in the [aegis-governance repository](https://github.com/aegis-initiative/aegis-governance/blob/main/REFERENCES.md). The repository file is canonical; this page mirrors it automatically via \`site/scripts/sync-references.mjs\`.
`;

function stripRepoInternals(raw) {
  let out = raw;

  // Remove the "See [CLAUDE.md](CLAUDE.md) for citation format conventions." line
  // (appears once, near the top).
  out = out.replace(/^See \[CLAUDE\.md\]\(CLAUDE\.md\).*$\n+/m, '');

  // Remove the "## How to Cite" section and its preceding horizontal-rule
  // separator through end of file.
  const howToCiteIdx = out.indexOf('## How to Cite');
  if (howToCiteIdx !== -1) {
    // Walk back through any leading whitespace/separator to find a clean cut point.
    const before = out.slice(0, howToCiteIdx);
    const lastSep = before.lastIndexOf('\n---\n');
    out = lastSep !== -1 ? out.slice(0, lastSep) : out.slice(0, howToCiteIdx);
  }

  // Remove the trailing metadata block ("**Part of**: …" onward).
  out = out.replace(/\n\*\*Part of\*\*:[\s\S]*$/m, '');

  // Tidy trailing whitespace.
  return out.trimEnd() + '\n';
}

async function main() {
  let raw;
  try {
    raw = await readFile(SOURCE, 'utf8');
  } catch (err) {
    throw new Error(
      `Could not read canonical REFERENCES.md at ${SOURCE}\n` +
      `  Cause: ${err.message}\n` +
      `  (sync-references.mjs is invoked from site/ and expects REFERENCES.md one directory up.)`,
    );
  }

  const body = stripRepoInternals(raw);
  const cspellLine = `<!-- cspell:ignore ${CSPELL_IGNORE_WORDS.join(' ')} -->`;

  const output = [
    FRONTMATTER,
    cspellLine,
    '',
    body,
    '',
    CANONICAL_FOOTER,
  ].join('\n');

  await writeFile(TARGET, output, 'utf8');

  const rel = relative(REPO_ROOT, TARGET).replaceAll('\\', '/');
  console.log(`sync-references: regenerated ${rel} from REFERENCES.md`);
}

main().catch((err) => {
  console.error('sync-references failed:');
  console.error(err.message || err);
  process.exit(1);
});

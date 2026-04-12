#!/usr/bin/env node
/**
 * fix-headings.mjs
 * Downshift headings in content files that have multiple H1s.
 * First H1 stays as-is (document title). All subsequent headings
 * get shifted down one level (# → ##, ## → ###, etc.)
 */

import { readFileSync, writeFileSync } from 'fs';
import { resolve } from 'path';
import { execSync } from 'child_process';

const DOCS = resolve(import.meta.dirname, '..', 'src', 'content', 'docs');

// Find files with multiple H1s
const output = execSync(
  `find "${DOCS}" -name "*.md" -exec grep -lc "^# " {} +`,
  { encoding: 'utf-8' }
).trim();

// Parse: find -exec gives us file:count pairs
const files = [];
for (const line of output.split('\n')) {
  // grep -c output: /path/to/file:N
  // But with find -exec, output is just filenames from grep -l...
  // Actually grep -lc isn't a thing. Let me just find files manually.
}

// Just scan all md files
import { readdirSync, statSync } from 'fs';
import { join } from 'path';

function walk(dir) {
  const results = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      results.push(...walk(full));
    } else if (entry.endsWith('.md')) {
      results.push(full);
    }
  }
  return results;
}

let fixed = 0;

for (const filePath of walk(DOCS)) {
  const content = readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');

  // Count H1s (lines starting with "# " but not "##")
  const h1Lines = lines.filter(l => /^# /.test(l));
  if (h1Lines.length <= 1) continue; // Fine — single H1 title

  // Find the first H1 (skip frontmatter)
  let firstH1Found = false;
  let inFrontmatter = false;
  let frontmatterCount = 0;

  const newLines = lines.map((line, i) => {
    // Track frontmatter
    if (line.trim() === '---') {
      frontmatterCount++;
      if (frontmatterCount === 1) inFrontmatter = true;
      if (frontmatterCount === 2) inFrontmatter = false;
      return line;
    }
    if (inFrontmatter) return line;

    // Only process heading lines
    const headingMatch = line.match(/^(#{1,6})\s/);
    if (!headingMatch) return line;

    // First H1 stays as-is
    if (!firstH1Found && headingMatch[1] === '#') {
      firstH1Found = true;
      return line;
    }

    // All subsequent headings: add one # level
    if (firstH1Found) {
      return '#' + line;
    }

    return line;
  });

  const newContent = newLines.join('\n');
  if (newContent !== content) {
    writeFileSync(filePath, newContent, 'utf-8');
    fixed++;
    const rel = filePath.replace(DOCS + '/', '').replace(DOCS + '\\', '');
    console.log(`Fixed: ${rel}`);
  }
}

console.log(`\nDownshifted headings in ${fixed} files`);

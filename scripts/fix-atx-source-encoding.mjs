#!/usr/bin/env node
// One-shot fixer for cp1252 mojibake in ATX-1 source files.
// Background: a prior hand-edit re-saved data/atx-1-techniques.json,
// data/atx-1-navigator-layer.json, and stix/atx-1-bundle.json with a non-UTF-8-aware
// editor that converted real em-dashes (U+2014) into the cp1252-double-encoded
// sequence U+00E2 U+20AC U+201D ("â€\""). This script reverses that one specific
// mapping and writes back as UTF-8 (no BOM).
//
// Conservative by design: only touches the one known pattern, only the three
// known files. Run with --check to see what would change without writing.

import { readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "..");
const ATX_ROOT = join(REPO_ROOT, "docs", "atx", "v2");
const TARGET_FILES = [
  join(ATX_ROOT, "data", "atx-1-techniques.json"),
  join(ATX_ROOT, "data", "atx-1-navigator-layer.json"),
  join(ATX_ROOT, "stix", "atx-1-bundle.json"),
];

const MOJIBAKE = String.fromCodePoint(0x00e2, 0x20ac, 0x201d); // â€"
const CORRECT = String.fromCodePoint(0x2014); // —

const CHECK_ONLY = process.argv.includes("--check");

function showContext(text, idx, span = 24) {
  const start = Math.max(0, idx - span);
  const end = Math.min(text.length, idx + MOJIBAKE.length + span);
  return text.slice(start, end).replace(/\n/g, "\\n");
}

let totalChanges = 0;

for (const f of TARGET_FILES) {
  const text = await readFile(f, "utf8");
  const matches = [...text.matchAll(new RegExp(MOJIBAKE.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g"))];
  if (matches.length === 0) {
    console.log(`[fix-encoding] ${f}: clean`);
    continue;
  }
  totalChanges += matches.length;
  const first = matches[0].index;
  const last = matches[matches.length - 1].index;
  console.log(`[fix-encoding] ${f}: ${matches.length} occurrences`);
  console.log(`  first @ byte~${first}: ...${showContext(text, first)}...`);
  if (matches.length > 1) {
    console.log(`  last  @ byte~${last}: ...${showContext(text, last)}...`);
  }
  if (CHECK_ONLY) continue;
  const fixed = text.replaceAll(MOJIBAKE, CORRECT);
  // Validate the fixed text still parses as JSON before writing
  try {
    JSON.parse(fixed);
  } catch (e) {
    console.error(`[fix-encoding] FATAL: post-fix JSON invalid for ${f}: ${e.message}`);
    process.exit(2);
  }
  // Sanity: byte-length should drop by exactly 5 per replacement
  // (8 bytes c3a2 e282ac e2809d → 3 bytes e28094)
  const sizeDelta = Buffer.byteLength(fixed, "utf8") - Buffer.byteLength(text, "utf8");
  const expectedDelta = matches.length * -5;
  if (sizeDelta !== expectedDelta) {
    console.error(`[fix-encoding] FATAL: byte delta ${sizeDelta} != expected ${expectedDelta} for ${f}`);
    process.exit(2);
  }
  await writeFile(f, fixed, { encoding: "utf8" });
  console.log(`  → wrote (delta ${sizeDelta} bytes)`);
}

console.log(`\n[fix-encoding] ${CHECK_ONLY ? "would fix" : "fixed"} ${totalChanges} occurrence(s) across ${TARGET_FILES.length} file(s)`);
if (CHECK_ONLY && totalChanges > 0) process.exit(1);

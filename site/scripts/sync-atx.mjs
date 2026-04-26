#!/usr/bin/env node
// Sync ATX-1 spec artifacts from docs/atx/v2/ → site/public/.
// Source of truth: docs/atx/v2/atx-meta.json (artifact list + version + descriptions).
// Synthesizes site/public/atx-1/index.json and site/public/atx-1/VERSION from atx-meta.json.
// Validates: techniques.json parses, tactic/technique counts match expected, all source files are valid UTF-8 JSON.
// Run modes: default (write), --check (fail if outputs would change — for CI).

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SITE_ROOT = resolve(__dirname, "..");
const REPO_ROOT = resolve(SITE_ROOT, "..");
const SOURCE_ROOT = join(REPO_ROOT, "docs", "atx", "v2");
const PUBLIC_ROOT = join(SITE_ROOT, "public");
const META_PATH = join(SOURCE_ROOT, "atx-meta.json");

const CHECK_ONLY = process.argv.includes("--check");

function log(level, msg) {
  const prefix = { info: "[sync-atx]", warn: "[sync-atx][warn]", err: "[sync-atx][err]" }[level];
  console[level === "err" ? "error" : "log"](`${prefix} ${msg}`);
}

async function readJson(path) {
  const buf = await readFile(path);
  // Reject UTF-8 BOM and known mojibake markers; they indicate the file was saved
  // with a non-UTF-8-aware editor and would propagate broken bytes downstream.
  if (buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf) {
    throw new Error(`${path} starts with UTF-8 BOM — re-save without BOM`);
  }
  const text = buf.toString("utf8");
  if (text.includes("�") || /â€["”“]/.test(text)) {
    throw new Error(`${path} contains UTF-8 mojibake (cp1252-misread em-dashes / replacement chars)`);
  }
  try {
    return { text, value: JSON.parse(text) };
  } catch (e) {
    throw new Error(`${path}: invalid JSON — ${e.message}`);
  }
}

async function writeJsonStable(path, value, { check }) {
  const next = JSON.stringify(value, null, 2) + "\n";
  if (check) {
    if (!existsSync(path)) {
      throw new Error(`would create ${path}`);
    }
    const cur = await readFile(path, "utf8");
    if (cur !== next) {
      throw new Error(`would update ${path}`);
    }
    return false;
  }
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, next, { encoding: "utf8" });
  return true;
}

async function writeTextStable(path, text, { check }) {
  if (check) {
    if (!existsSync(path)) {
      throw new Error(`would create ${path}`);
    }
    const cur = await readFile(path, "utf8");
    if (cur !== text) {
      throw new Error(`would update ${path}`);
    }
    return false;
  }
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, text, { encoding: "utf8" });
  return true;
}

async function copyJsonStable(srcAbs, dstAbs, { check }) {
  const { value } = await readJson(srcAbs);
  return writeJsonStable(dstAbs, value, { check });
}

function buildIndex(meta) {
  return {
    name: meta.name,
    full_name: meta.full_name,
    version: meta.version,
    date: meta.date,
    description: meta.description,
    license: meta.license,
    publisher: meta.publisher,
    artifacts: meta.artifacts.map((a) => ({
      name: a.name,
      description: a.description,
      path: a.public_path ?? `/${a.dst}`,
      format: a.format,
      ...(a.spec ? { spec: a.spec } : {}),
    })),
    source: meta.source_repo,
    citation: meta.citation,
  };
}

function countTactics(techniques) {
  // Top-level techniques only (sub-techniques carry the same tactic and would double-count).
  const tactics = new Set();
  for (const t of techniques) {
    if (t.tactic && !t.id?.includes(".")) tactics.add(t.tactic);
  }
  return tactics.size;
}

function countTopLevelTechniques(techniques) {
  return techniques.filter((t) => !t.id?.includes(".")).length;
}

async function main() {
  log("info", `mode=${CHECK_ONLY ? "check" : "write"} source=${SOURCE_ROOT}`);

  if (!existsSync(META_PATH)) {
    log("err", `missing meta file: ${META_PATH}`);
    process.exit(2);
  }
  const { value: meta } = await readJson(META_PATH);

  // Sanity-check meta shape before doing anything destructive.
  for (const field of ["version", "date", "artifacts", "expected_counts"]) {
    if (!(field in meta)) {
      log("err", `atx-meta.json missing required field: ${field}`);
      process.exit(2);
    }
  }
  if (!/^\d+\.\d+\.\d+$/.test(meta.version)) {
    log("err", `atx-meta.json version "${meta.version}" is not semver-shaped (X.Y.Z)`);
    process.exit(2);
  }

  // Validate technique counts BEFORE copying — the spec is the contract.
  const techniquesArtifact = meta.artifacts.find((a) => a.key === "techniques");
  if (!techniquesArtifact) {
    log("err", `atx-meta.json artifacts list missing "techniques" entry`);
    process.exit(2);
  }
  const techSrc = join(SOURCE_ROOT, techniquesArtifact.src);
  const { value: techniques } = await readJson(techSrc);
  if (!Array.isArray(techniques)) {
    log("err", `${techSrc} is not a JSON array`);
    process.exit(2);
  }
  const tacticCount = countTactics(techniques);
  const topTechCount = countTopLevelTechniques(techniques);
  const totalTechCount = techniques.length;
  if (tacticCount !== meta.expected_counts.tactics) {
    log("err", `tactic count ${tacticCount} != expected ${meta.expected_counts.tactics}`);
    process.exit(2);
  }
  if (totalTechCount !== meta.expected_counts.techniques) {
    log("err", `technique count ${totalTechCount} != expected ${meta.expected_counts.techniques}`);
    process.exit(2);
  }
  log("info", `validated counts: ${tacticCount} tactics, ${totalTechCount} techniques (${topTechCount} top-level)`);

  // Copy each declared artifact.
  const changes = [];
  for (const a of meta.artifacts) {
    const src = join(SOURCE_ROOT, a.src);
    const dst = join(PUBLIC_ROOT, a.dst);
    if (!existsSync(src)) {
      log("err", `missing source for artifact "${a.key}": ${src}`);
      process.exit(2);
    }
    try {
      const wrote = await copyJsonStable(src, dst, { check: CHECK_ONLY });
      if (wrote) changes.push(a.dst);
    } catch (e) {
      if (CHECK_ONLY && /^would (create|update)/.test(e.message)) {
        changes.push(a.dst);
      } else {
        log("err", `failed to sync ${a.key}: ${e.message}`);
        process.exit(2);
      }
    }
  }

  // Synthesize index.json + VERSION.
  const indexPath = join(PUBLIC_ROOT, "atx-1", "index.json");
  const versionPath = join(PUBLIC_ROOT, "atx-1", "VERSION");
  try {
    if (await writeJsonStable(indexPath, buildIndex(meta), { check: CHECK_ONLY })) changes.push("atx-1/index.json");
  } catch (e) {
    if (CHECK_ONLY && /^would (create|update)/.test(e.message)) changes.push("atx-1/index.json");
    else throw e;
  }
  try {
    if (await writeTextStable(versionPath, meta.version + "\n", { check: CHECK_ONLY })) changes.push("atx-1/VERSION");
  } catch (e) {
    if (CHECK_ONLY && /^would (create|update)/.test(e.message)) changes.push("atx-1/VERSION");
    else throw e;
  }

  if (CHECK_ONLY && changes.length > 0) {
    log("err", `out of sync — ${changes.length} file(s) would change:`);
    for (const c of changes) log("err", `  ${c}`);
    process.exit(1);
  }
  if (changes.length === 0) {
    log("info", "all artifacts in sync — no changes");
  } else {
    log("info", `synced ${changes.length} file(s) → site/public/`);
    for (const c of changes) log("info", `  ${c}`);
  }
}

main().catch((e) => {
  log("err", e.stack ?? e.message);
  process.exit(2);
});

#!/usr/bin/env python3
"""
Nightly release rollup — runs at the start of the next day to seal
the previous day's development work as a release.

Steps:
  1. Read the previous day's daily development log
  2. Extract substantive dev log entries (filter out meta rollup
     commits and Dependabot dependency bumps)
  3. Rewrite the entries into publication-form release notes via the
     Claude API — natural language, past tense, hash-stripped
  4. Skip the release entirely if no substantive entries remain
  5. Prepend a release recap to the top of the daily log
  6. Add/update the release entry in the monthly release file
  7. Add/update the entry in the release index
  8. Write the VERSION file at the repo root
  9. Create the 3-part release tag (vYY.M.D) pointing at the commit
     of the last 4-part dev log tag of that day
 10. Push the release tag to origin

Version scheme:
  vYY.M.D.N  (4-part) — development log snapshot, created on every push
  vYY.M.D    (3-part) — release, created here by rolling up the day's work

The rollup is idempotent — existing release entries and tags are
preserved and re-runs on the same date are safe.

Environment:
  ANTHROPIC_API_KEY — optional. If set, release summaries are rewritten
  into public-facing prose via the Claude API. If not set, the script
  falls back to using the raw (but filtered) dev log entries.

CLI:
  --year YY   (required) two-digit year, e.g. 26
  --month M   (required, 1-12, no leading zero)
  --day D     (required, 1-31, no leading zero)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", required=True, help="Two-digit year (e.g. 26)")
    parser.add_argument("--month", required=True, help="Month (1-12, no leading zero)")
    parser.add_argument("--day", required=True, help="Day (1-31, no leading zero)")
    return parser.parse_args()


def get_dev_log_tags(year, month, day):
    """Find all 4-part development log tags for a specific date.

    Returns tags of the form vYY.M.D.N sorted by N.
    The 3-part release tag (vYY.M.D) is excluded — it's created by
    this script, not by individual pushes.
    """
    prefix = f"v{year}.{month}.{day}."
    # Use list form (no shell=True) so the glob doesn't get mangled by
    # Windows cmd.exe when running locally.
    result = subprocess.run(
        ["git", "tag", "--list", "v*"],
        capture_output=True, text=True,
    )
    all_tags = result.stdout.strip().split("\n")
    pattern = re.compile(rf"^{re.escape(prefix)}\d+$")
    tags = [t for t in all_tags if t.strip() and pattern.match(t)]
    # Sort numerically by the trailing counter
    tags.sort(key=lambda t: int(t.rsplit(".", 1)[-1]))
    return tags


def create_release_tag(release_tag, source_tag):
    """Create the 3-part release tag pointing at source_tag's commit.

    Idempotent: if release_tag already exists, log and skip.
    Returns True if the tag was newly created.
    """
    existing = run(f"git rev-parse --verify --quiet refs/tags/{release_tag}")
    if existing:
        print(f"Release tag {release_tag} already exists — skipping creation")
        return False

    commit = run(f"git rev-list -n 1 {source_tag}")
    if not commit:
        print(f"Could not resolve commit for {source_tag}", file=sys.stderr)
        return False

    result = subprocess.run(
        f"git tag {release_tag} {commit}",
        shell=True, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Failed to create tag {release_tag}: {result.stderr}", file=sys.stderr)
        return False

    push_result = subprocess.run(
        f"git push origin {release_tag}",
        shell=True, capture_output=True, text=True,
    )
    if push_result.returncode != 0:
        print(f"Failed to push tag {release_tag}: {push_result.stderr}", file=sys.stderr)
        return False

    print(f"Created and pushed release tag {release_tag} → {commit[:7]}")
    return True


def update_version_file(release_tag, source_tag):
    """Write the VERSION file at the repo root.

    VERSION is the authoritative machine-readable record of the current
    release. The Astro build reads it to populate the header version
    badge. It's committed in the same rollup commit as the release
    notes so they're always in sync.

    Idempotent: writing the same tag twice is a no-op diff.
    """
    commit = run(f"git rev-list -n 1 {source_tag}")
    short = commit[:7] if commit else ""
    released_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "tag": release_tag,
        "commit": short,
        "released_at": released_at,
    }

    with open("VERSION", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")

    print(f"Wrote VERSION file: {release_tag} @ {short}")


def get_builds_range(tags):
    """Get first and last commit hashes for the day's tags."""
    if not tags:
        return "", ""
    first_hash = run(f"git rev-list -1 {tags[0]}")[:7]
    last_hash = run(f"git rev-list -1 {tags[-1]}")[:7]
    return first_hash, last_hash


# Commit-message patterns that indicate a commit is out of scope for
# the public-facing release notes. Used as a safety net when reading
# historical dev logs that were populated before the workflow-level
# filters were in place.
_META_PREFIXES = (
    "docs: release notes for ",
    "docs: dev log entry for ",
    "docs: nightly release rollup",
)
_DEPS_PREFIXES = (
    "chore(deps",
    "build(deps",
)


def _is_substantive(entry):
    """Return True if a dev log entry represents real user-facing work.

    Strips the leading dash and any surrounding whitespace, then rejects
    the entry if it matches a known meta rollup commit or a dependency
    bump. Used to filter both new and historical dev logs.
    """
    body = entry.lstrip("- ").strip()
    if any(body.startswith(p) for p in _META_PREFIXES):
        return False
    if any(body.startswith(p) for p in _DEPS_PREFIXES):
        return False
    return True


def extract_dev_log_entries(dev_log_content):
    """Extract substantive bullet entries from the day's development log.

    Drops meta rollup commits (e.g. "docs: release notes for ...") and
    Dependabot dependency bumps. Returns an empty list if nothing
    substantive remains — the caller should skip release creation
    rather than cut an empty release.
    """
    raw = [l.strip() for l in dev_log_content.split("\n") if l.strip().startswith("- ")]
    return [e for e in raw if _is_substantive(e)]


def generate_release_summary(raw_entries):
    """Rewrite raw dev log entries into publication-form release notes.

    Calls the Claude API to convert conventional-commit messages into
    natural-language bullets suitable for a public release changelog.
    Falls back to the raw (but filtered) entries if ANTHROPIC_API_KEY
    is not set or the API call fails.
    """
    if not raw_entries:
        return []

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return raw_entries[:20]

    import urllib.request

    joined = "\n".join(raw_entries)

    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": (
                    "You are writing release notes for the AEGIS Governance "
                    "site (technical specifications — RFCs, ATX-1 taxonomy, "
                    "plugins, schemas, data portal). Convert these "
                    "development "
                    "log entries into clear, public-facing release note "
                    "bullet points.\n\n"
                    "Rules:\n"
                    "- Write in natural language, past tense, user-facing.\n"
                    "- Drop commit hashes, PR numbers, and conventional commit "
                    "prefixes (feat:, fix:, chore:, docs:, etc.).\n"
                    "- Group related changes together under a single bullet.\n"
                    "- Skip internal plumbing that doesn't affect users "
                    "(Cloudflare redeploy triggers, lockfile regenerations, "
                    "CI config tweaks) unless they're the whole point of the "
                    "release.\n"
                    "- Emphasize what the reader can now do or see that they "
                    "couldn't before.\n"
                    "- Return ONLY a markdown bulleted list, nothing else.\n\n"
                    "Dev log entries:\n" + joined
                ),
            }
        ],
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["content"][0]["text"].strip()
            bullets = [l.strip() for l in text.split("\n") if l.strip().startswith("- ")]
            return bullets or raw_entries[:20]
    except Exception as exc:
        print(f"Warning: Claude API call failed ({exc}), using raw entries", file=sys.stderr)
        return raw_entries[:20]


def generate_index_summary(release_entries):
    """Derive a one-line index summary from the release entries.

    Calls the Claude API for a concise headline phrase. Falls back to
    the first entry (hash-stripped, truncated) if the API is unavailable.
    """
    if not release_entries:
        return "Updates"

    def _fallback():
        first = release_entries[0].lstrip("- ").strip()
        first = re.sub(r"\s*\([a-f0-9]{7,}\)\s*$", "", first)
        return first[:80]

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return _fallback()

    import json
    import urllib.request

    joined = "\n".join(release_entries)

    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Summarize these release notes into a single concise "
                    "phrase (under 80 chars) for a release index. No period "
                    "at the end. Return ONLY the phrase, no quotes.\n\n"
                    + joined
                ),
            }
        ],
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"].strip().strip('"')[:80]
    except Exception:
        return _fallback()


def update_daily_log(file_path, tag, builds_str, release_entries):
    """Prepend release recap to the daily log."""
    if not os.path.exists(file_path):
        print(f"No daily log found at {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if release recap already exists
    if f"## Release / {tag}" in content:
        print(f"Release recap already exists in {file_path}")
        return False

    # Build release recap
    recap_lines = [f"## Release / {tag}", "", f"*Builds: {builds_str}*", ""]
    recap_lines.extend(release_entries)
    recap_lines.append("")
    recap_lines.append("---")
    recap_lines.append("")
    recap = "\n".join(recap_lines)

    # Insert after frontmatter (after second ---)
    parts = content.split("---", 2)
    if len(parts) >= 3:
        content = parts[0] + "---" + parts[1] + "---\n\n" + recap + parts[2].lstrip("\n")
    else:
        content = content + "\n\n" + recap

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Added release recap to {file_path}")
    return True


def update_monthly(year, month, tag, builds_str, release_entries, day):
    """Add release entry to monthly file."""
    file_path = f"src/content/docs/releases/{year}/{month}.md"

    month_name = datetime.now(timezone.utc).strftime("%B")
    year_full = datetime.now(timezone.utc).strftime("%Y")

    entries_text = "\n".join(release_entries)
    new_section = f"""## Release / {tag}

*Builds: {builds_str}* — [Development Log →](/releases/{year}/{month}/{day}/)

{entries_text}

---

"""

    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        content = f"""---
title: "{month_name} {year_full}"
description: "Release notes for {month_name} {year_full}"
template: doc
sidebar:
  hidden: true
---

{new_section}"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created {file_path}")
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if f"## Release / {tag}" in content:
            print(f"Release already exists in {file_path}")
            return

        # Insert after frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[0] + "---" + parts[1] + "---\n\n" + new_section + parts[2].lstrip("\n")
        else:
            content = content + "\n\n" + new_section

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")


def update_index(year, month, tag, summary):
    """Add/update entry in release index."""
    index_path = "src/content/docs/releases/index.md"

    if not os.path.exists(index_path):
        print(f"Error: {index_path} not found", file=sys.stderr)
        return

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    base_tag = tag.split(".")[0] + "." + tag.split(".")[1] + "." + tag.split(".")[2]
    anchor_tag = base_tag.replace(".", "").replace("v", "v")
    entry_line = f"- [{base_tag}](/releases/{year}/{month}/#release--{anchor_tag}) — {summary}"

    # Check if entry exists
    entry_pattern = re.compile(rf"- \[{re.escape(base_tag)}\].*")
    if entry_pattern.search(content):
        content = entry_pattern.sub(entry_line, content)
        print(f"Updated index entry for {base_tag}")
    else:
        year_full = datetime.now(timezone.utc).strftime("%Y")
        month_name = datetime.now(timezone.utc).strftime("%B")
        month_header = f"### [{month_name}](/releases/{year}/{month}/)"
        year_header = f"## {year_full}"

        if month_header in content:
            pos = content.index(month_header) + len(month_header)
            next_nl = content.index("\n", pos)
            insert_pos = next_nl + 1
            if insert_pos < len(content) and content[insert_pos] == "\n":
                insert_pos += 1
            content = content[:insert_pos] + entry_line + "\n" + content[insert_pos:]
        elif year_header in content:
            pos = content.index(year_header) + len(year_header)
            next_nl = content.index("\n", pos)
            insert = f"\n\n{month_header}\n\n{entry_line}\n"
            content = content[:next_nl + 1] + insert + content[next_nl + 1:]
        else:
            fm_end = content.index("---", content.index("---") + 3) + 3
            insert = f"\n\n{year_header}\n\n{month_header}\n\n{entry_line}\n"
            content = content[:fm_end] + insert + content[fm_end:]

        print(f"Added index entry for {base_tag}")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    args = parse_args()
    year = args.year
    month = args.month
    day = args.day

    print(f"Processing releases for 20{year}-{int(month):02d}-{int(day):02d} (v{year}.{month}.{day})")

    dev_tags = get_dev_log_tags(year, month, day)
    if not dev_tags:
        print("No development log tags found for this date. Nothing to do.")
        sys.exit(0)

    print(f"Found {len(dev_tags)} dev log tag(s): {', '.join(dev_tags)}")

    # The release tag for this day
    release_tag = f"v{year}.{month}.{day}"

    # Get build hashes from the first and last dev log tags
    first_hash, last_hash = get_builds_range(dev_tags)
    builds_str = first_hash if first_hash == last_hash else f"{first_hash} – {last_hash}"

    # Read the daily dev log
    daily_path = f"src/content/docs/releases/{year}/{month}/{day}.md"
    if os.path.exists(daily_path):
        with open(daily_path, "r", encoding="utf-8") as f:
            dev_log_content = f.read()
    else:
        print(f"No daily log at {daily_path}")
        dev_log_content = ""

    # Extract substantive dev log entries (meta rollup commits and
    # Dependabot bumps are filtered out).
    raw_entries = extract_dev_log_entries(dev_log_content)
    print(f"Extracted {len(raw_entries)} substantive dev log entries")

    if not raw_entries:
        print("No substantive entries to release. Skipping release creation.")
        sys.exit(0)

    # Rewrite into publication-form release notes via Claude API
    # (falls back to raw entries if no API key / API failure).
    release_entries = generate_release_summary(raw_entries)
    print(f"Generated {len(release_entries)} release bullets")

    # Derive a one-line headline for the release index.
    index_summary = generate_index_summary(release_entries)
    print(f"Index summary: {index_summary}")

    # Update all three release-notes files
    update_daily_log(daily_path, release_tag, builds_str, release_entries)
    update_monthly(year, month, release_tag, builds_str, release_entries, day)
    update_index(year, month, release_tag, index_summary)

    # Update the machine-readable VERSION file
    update_version_file(release_tag, dev_tags[-1])

    # Create the 3-part release tag pointing at the last dev log tag's commit
    create_release_tag(release_tag, dev_tags[-1])

    print("\nDone.")


if __name__ == "__main__":
    main()

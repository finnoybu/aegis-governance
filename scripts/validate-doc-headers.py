#!/usr/bin/env python3
"""Validate header metadata for AEGIS specification documents.

Each doc class (AGP, ATM, GFN, RFC, architecture) has required header
fields and an acceptable date format. This script enforces them in CI.

Doc class detection is by path/filename.

Required fields and date formats are defined per class below.

Exit codes:
  0 — all docs validated successfully
  1 — one or more validation errors

Usage:
  python scripts/validate-doc-headers.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Force UTF-8 stdout so Unicode glyphs work on Windows consoles too.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).parent.parent

# US English month-day-year, e.g. "March 6, 2026"
US_DATE_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|"
    r"September|October|November|December) \d{1,2}, \d{4}$"
)

# ISO 8601 date, e.g. "2026-03-26"
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_valid_date(value: str) -> bool:
    """A date is valid if it matches either US English or ISO format."""
    return bool(US_DATE_RE.match(value) or ISO_DATE_RE.match(value))


# Header field is "**Key**: value" or "**Key:** value" possibly trailing "\"
HEADER_FIELD_RE = re.compile(r"^\*\*([^*:]+)\*?\*?\s*:?\s*\*?\*?\s*(.+?)\\?$")
# Architecture-style "Key: value" (no bold)
PLAIN_FIELD_RE = re.compile(r"^([A-Z][A-Za-z ]+):\s*(.+?)\\?$")


def parse_header(text: str, max_lines: int = 30) -> dict[str, str]:
    """Extract key/value metadata from the first ``max_lines`` of a doc.

    Stops at the first horizontal rule (---) or first H2 heading. Both
    bold (``**Key**: value``) and plain (``Key: value``) styles are
    recognized.
    """
    fields: dict[str, str] = {}
    for raw_line in text.splitlines()[:max_lines]:
        line = raw_line.strip()
        if line == "---" or line.startswith("## "):
            break
        match = HEADER_FIELD_RE.match(line) or PLAIN_FIELD_RE.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip().rstrip("\\").strip()
            fields[key] = value
    return fields


def classify(path: Path) -> str | None:
    """Return the doc class for ``path``, or ``None`` if not a spec doc."""
    rel = path.relative_to(REPO_ROOT).as_posix()
    name = path.name

    # Index/README files in spec dirs are not specs themselves
    if name in ("README.md", "INDEX.md"):
        return None

    if rel.startswith("aegis-core/protocol/AEGIS_AGP1_"):
        return "AGP"
    if rel.startswith("aegis-core/threat-model/AEGIS_ATM1_"):
        return "ATM"
    if rel.startswith("federation/AEGIS_GFN1_"):
        return "GFN"
    if rel.startswith("rfc/RFC-") and name.startswith("RFC-") and "TEMPLATE" not in name and "PLACEHOLDER" not in name:
        return "RFC"
    if rel.startswith("aegis-core/architecture/AEGIS_") and name.endswith(".md"):
        return "ARCHITECTURE"
    return None


REQUIRED_FIELDS = {
    "AGP": ["Document", "Version", "Part of", "Last Updated"],
    "ATM": ["Document", "Version", "Part of", "Last Updated"],
    "GFN": ["Document", "Version", "Part of", "Last Updated"],
    "RFC": ["RFC", "Status", "Created", "Updated", "Author"],
    "ARCHITECTURE": ["Version", "Status", "Effective Date"],
}

DATE_FIELDS = {
    "AGP": ["Last Updated"],
    "ATM": ["Last Updated"],
    "GFN": ["Last Updated"],
    "RFC": ["Created", "Updated"],
    "ARCHITECTURE": ["Effective Date"],
}


def validate(path: Path, doc_class: str) -> list[str]:
    """Return a list of error messages for ``path`` (empty if valid)."""
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    fields = parse_header(text)

    for required in REQUIRED_FIELDS[doc_class]:
        if required not in fields:
            errors.append(f"missing required field: '{required}'")

    for date_field in DATE_FIELDS[doc_class]:
        value = fields.get(date_field)
        if value and not is_valid_date(value):
            errors.append(
                f"invalid date format in '{date_field}': '{value}' "
                f"(expected 'Month D, YYYY' or 'YYYY-MM-DD')"
            )

    return errors


def main() -> int:
    docs: list[tuple[Path, str]] = []
    for md in REPO_ROOT.rglob("*.md"):
        if any(part in ("node_modules", ".git", "archive") for part in md.parts):
            continue
        doc_class = classify(md)
        if doc_class:
            docs.append((md, doc_class))

    total = len(docs)
    failures: list[tuple[Path, str, list[str]]] = []
    for path, doc_class in sorted(docs):
        errors = validate(path, doc_class)
        if errors:
            failures.append((path, doc_class, errors))

    if failures:
        print(f"❌ {len(failures)}/{total} spec documents failed metadata validation:")
        print()
        for path, doc_class, errors in failures:
            rel = path.relative_to(REPO_ROOT).as_posix()
            print(f"  {rel} [{doc_class}]")
            for err in errors:
                print(f"    - {err}")
            print()
        return 1

    print(f"✅ All {total} spec documents have valid header metadata.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

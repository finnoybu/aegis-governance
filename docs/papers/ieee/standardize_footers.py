"""
Standardize AEGIS footer across all user-readable markdown docs.

Standard footer (added/replaced at end of file):

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*
*AEGIS Initiative — Finnoybu IP LLC*

Rules:
- Skip frozen/submitted docs
- Skip TRADEMARKS.md (trademark registry — has its own format)
- Skip .github/copilot-instructions.md (internal tooling)
- Skip docs/papers/ (paper drafts)
- For files with an existing footer block: replace it
- For files without: append it
- Also fix ™ placement in body text: intelligence™" → intelligence"™
"""

import re
import os

ROOT = "d:/dev/aegis-governance"

SKIP = {
    "docs/position-papers/nist/2026-03-aegis-nist-ai-rmf-position-statement.md",
    "TRADEMARKS.md",
    ".github/copilot-instructions.md",
    "docs/papers/ieee/aegis-ieee-paper-draft-v0.1.md",
    "docs/papers/ieee/aegis-ieee-paper-formatted.docx",
}

STANDARD_FOOTER = (
    "---\n\n"
    "*AEGIS™* | *\"Capability without constraint is not intelligence\"™*  \n"
    "*AEGIS Initiative — Finnoybu IP LLC*\n"
)

# Patterns that constitute an existing footer block at end of file.
# Each is a regex that matches the footer region (may span multiple lines).
FOOTER_PATTERNS = [
    # RFC-style: optional ---, slogan line, optional attribution line
    re.compile(
        r"---\s*\n+"
        r"\*\"Capability without constraint is not intelligence[™\u2122]*\"[™\u2122]*\*\s*\\\s*\n"
        r"\*(?:Finnoybu IP LLC|AEGIS[™\u2122]* Initiative)[^\n]*\*\s*\n?",
        re.MULTILINE,
    ),
    re.compile(
        r"---\s*\n+"
        r"\*\"Capability without constraint is not intelligence[™\u2122]*\"[™\u2122]*\*\s*\n"
        r"\*(?:Finnoybu IP LLC|AEGIS[™\u2122]* Initiative)[^\n]*\*\s*\n?",
        re.MULTILINE,
    ),
    # Heading + blockquote style: # Foundational Principle/Maxim + > slogan
    re.compile(
        r"#{1,3}\s+Foundational (?:Principle|Maxim)\s*\n+"
        r">?\s*\*?\*?\"?Capability without constraint is not intelligence[™\u2122]*\"?[™\u2122]*\*?\*?\s*\n?",
        re.MULTILINE,
    ),
    # Blockquote alone at end: > **Capability...**  or  > Capability...
    re.compile(
        r"> \*?\*?\"?Capability without constraint is not intelligence[™\u2122]*\"?[™\u2122]*\*?\*?\s*\n?",
        re.MULTILINE,
    ),
    # Standalone italic line (no heading)
    re.compile(
        r"\*\"Capability without constraint is not intelligence[™\u2122]*\"[™\u2122]*\*\s*\n?",
        re.MULTILINE,
    ),
    # Bold line
    re.compile(
        r"\*\*\"?Capability without constraint is not intelligence[™\u2122]*\"?[™\u2122]*\*\*\s*\n?",
        re.MULTILINE,
    ),
    # Plain line
    re.compile(
        r"Capability without constraint is not intelligence[™\u2122]*\s*\n?",
        re.MULTILINE,
    ),
]

def fix_tm_in_body(text):
    """Fix intelligence™" → intelligence"™ in body (non-trademark-notice) contexts."""
    return re.sub(
        r'intelligence™"',
        'intelligence"™',
        text
    )

def strip_existing_footer(text):
    """
    Remove the last occurrence of any footer pattern plus any trailing
    --- separator and optional attribution line that follow it.
    """
    # Work from the end of the file.
    # Strategy: find the last '---' that precedes a footer pattern,
    # and strip everything from there.

    # Combined: look for the footer block starting with ---
    combined = re.compile(
        r"\n---\s*\n+"
        r"(?:"
        r"\*\"Capability[^\"]*\"[™\u2122]*\*"          # italic quoted
        r"|> \*?\*?\"?Capability[^\n]*"                 # blockquote
        r"|\*\*\"?Capability[^\n]*"                     # bold
        r"|#{1,3}\s+Foundational[^\n]*\nCapability[^\n]*"  # heading + plain
        r"|#{1,3}\s+Foundational[^\n]*\n+>?[^\n]*Capability[^\n]*"  # heading + blockquote
        r")",
        re.MULTILINE,
    )

    matches = list(combined.finditer(text))
    if matches:
        last = matches[-1]
        # Cut everything from the start of this match to end of file
        text = text[:last.start()]
    else:
        # Try to find heading-only footer (# Foundational ...)
        heading_footer = re.compile(
            r"\n#{1,3}\s+Foundational (?:Principle|Maxim)\s*\n",
            re.MULTILINE,
        )
        matches = list(heading_footer.finditer(text))
        if matches:
            last = matches[-1]
            text = text[:last.start()]

    return text.rstrip()

def process_file(rel_path, abs_path):
    with open(abs_path, "r", encoding="utf-8") as f:
        original = f.read()

    text = original

    # Fix ™ placement in body
    text = fix_tm_in_body(text)

    # Strip existing footer
    text = strip_existing_footer(text)

    # Append standard footer
    text = text.rstrip() + "\n\n" + STANDARD_FOOTER

    if text != original:
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    return False

def main():
    changed = []
    skipped = []

    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Skip hidden and ignored dirs
        dirnames[:] = [d for d in dirnames if d not in {'.git', 'archive', 'resources', '.claude', '__pycache__'}]

        for filename in filenames:
            if not filename.endswith(".md"):
                continue
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, ROOT).replace("\\", "/")

            if rel_path in SKIP:
                skipped.append(rel_path)
                continue

            # Only process files that contain the slogan OR are "primary" docs
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "Capability without constraint" not in content:
                continue

            if process_file(rel_path, abs_path):
                changed.append(rel_path)
                print(f"  UPDATED: {rel_path}")
            else:
                print(f"  unchanged: {rel_path}")

    print(f"\nDone. {len(changed)} files updated, {len(skipped)} skipped.")
    for s in skipped:
        print(f"  skipped: {s}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Append a commit entry to today's daily development log.

Creates the daily log file if it doesn't exist.
Appends the commit message to the Development Log section.

Environment variables:
  HASH    — short commit hash
  MESSAGE — commit message (first line)
  TAG     — CalVer tag
  YEAR    — two-digit year
  MONTH   — month number
  DAY     — day number
"""

import os
import re
from datetime import datetime, timezone

hash_val = os.environ["HASH"]
message = os.environ["MESSAGE"]
tag = os.environ["TAG"]
year = os.environ["YEAR"]
month = os.environ["MONTH"]
day = os.environ["DAY"]

month_name = datetime.now(timezone.utc).strftime("%B")
day_int = int(day)

file_dir = f"src/content/docs/releases/{year}/{month}"
file_path = f"{file_dir}/{day}.md"
os.makedirs(file_dir, exist_ok=True)

dev_log_entry = f"- {message} ({hash_val})\n"

if not os.path.exists(file_path):
    # Create new daily log
    content = f"""---
title: "{month_name} {day_int}, 2026"
description: "Development log for {month_name} {day_int}, 2026"
template: doc
sidebar:
  hidden: true
---

## Development Log

{dev_log_entry}"""
    with open(file_path, "w") as f:
        f.write(content)
    print(f"Created {file_path}")
else:
    with open(file_path, "r") as f:
        content = f.read()

    # Append to Development Log section
    if "## Development Log" in content:
        # Find the end of the Development Log heading line
        idx = content.index("## Development Log")
        # Find the next newline after the heading
        nl = content.index("\n", idx)
        # Skip any blank line after heading
        insert_pos = nl + 1
        if insert_pos < len(content) and content[insert_pos] == "\n":
            insert_pos += 1

        # Find end of dev log section (next ## or end of file)
        next_section = re.search(r"\n## (?!Development Log)", content[insert_pos:])
        if next_section:
            append_pos = insert_pos + next_section.start()
        else:
            append_pos = len(content)

        # Append at the end of the dev log section
        content = content[:append_pos].rstrip("\n") + "\n" + dev_log_entry + content[append_pos:]
    else:
        # No dev log section yet — add one
        content = content.rstrip("\n") + f"\n\n## Development Log\n\n{dev_log_entry}"

    with open(file_path, "w") as f:
        f.write(content)
    print(f"Updated {file_path}")

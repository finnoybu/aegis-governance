#!/usr/bin/env python3
"""
Generate release notes from git commit messages using the Claude API.

Reads:
  ANTHROPIC_API_KEY — from environment
  RAW_COMMITS      — from environment (newline-separated commit messages)

Outputs the generated notes to stdout.
"""

import json
import os
import sys
import urllib.request

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
raw_commits = os.environ.get("RAW_COMMITS", "")

if not api_key:
    print("Warning: ANTHROPIC_API_KEY not set, using raw commits", file=sys.stderr)
    print(raw_commits)
    sys.exit(0)

if not raw_commits.strip():
    print("- No commits since last release")
    sys.exit(0)

payload = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": (
                "You are writing release notes for the AEGIS™ Governance "
                "site (technical specifications — RFCs, ATX-1 taxonomy, "
                "plugins, schemas, data portal). Convert these raw git "
                "commit "
                "messages into clear, professional release note entries. Keep "
                "them concise and human-readable. Return ONLY a markdown "
                "bulleted list, nothing else. No preamble, no explanation, "
                "no code fences.\n\nRaw commits:\n" + raw_commits
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
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(data["content"][0]["text"])
except Exception as e:
    print(f"Warning: Claude API call failed ({e}), using raw commits", file=sys.stderr)
    print(raw_commits)

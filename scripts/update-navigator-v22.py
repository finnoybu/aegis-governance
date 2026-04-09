#!/usr/bin/env python3
"""Update the ATT&CK Navigator layer for ATX-1 v2.2.

- Bumps name/description to v2.2
- Sets showSubtechniques=true on parent techniques that have sub-techniques
- Adds Navigator entries for each new sub-technique (using dotted ID format)

Idempotent: safe to run multiple times.
"""

from __future__ import annotations

import json
from pathlib import Path

DATA_PATH = Path("docs/atx/v2/data/atx-1-techniques.json")
NAV_PATH = Path("docs/atx/v2/data/atx-1-navigator-layer.json")


# Map ATX-1 tactic IDs to Navigator-style slugs (matching existing convention).
TACTIC_SLUGS = {
    "TA001": "violate-authority-boundaries",
    "TA002": "exceed-operational-scope",
    "TA003": "perform-irreversible-action",
    "TA004": "expose-or-exfiltrate-information",
    "TA005": "violate-state-integrity",
    "TA006": "abuse-resource-allocation",
    "TA007": "manipulate-agent-interactions",
    "TA008": "establish-or-modify-persistence",
    "TA009": "evade-detection-or-oversight",
    "TA010": "act-beyond-governance-interpretation",
}

SEVERITY_SCORE = {"critical": 100, "high": 75, "medium": 50, "low": 25}
SEVERITY_COLOR = {
    "critical": "#8B0000",
    "high": "#b35900",
    "medium": "#e6b800",
    "low": "#1a8c1a",
}


def main() -> int:
    techniques = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    nav = json.loads(NAV_PATH.read_text(encoding="utf-8"))

    # Bump version metadata
    nav["name"] = "ATX-1 v2.2: AEGIS Threat Matrix"
    nav["description"] = (
        "ATX-1 v2.2 \u2014 10 tactics, 29 techniques, 29 sub-techniques for "
        "autonomous AI agent threat modeling. v2.2 adds sub-techniques under "
        "T9002 and T10001\u2013T10004 cataloging specific bypass methods "
        "discovered during RFC-0006 adversarial testing."
    )

    # Build parent -> sub IDs map
    by_id: dict[str, dict] = {t["id"]: t for t in techniques}
    parents_with_subs = {
        t["id"]: t["sub_techniques"]
        for t in techniques
        if "sub_techniques" in t
    }

    # Mark parents as having sub-techniques in Navigator
    nav_by_id = {entry["techniqueID"]: entry for entry in nav["techniques"]}
    for parent_id in parents_with_subs:
        if parent_id in nav_by_id:
            nav_by_id[parent_id]["showSubtechniques"] = True

    # Add Navigator entries for each sub-technique
    new_entries: list[dict] = []
    for parent_id, sub_ids in parents_with_subs.items():
        for sub_id in sub_ids:
            if sub_id in nav_by_id:
                continue
            sub = by_id[sub_id]
            tactic_slug = TACTIC_SLUGS[sub["tactic"]]
            severity = sub["severity"]
            entry = {
                "techniqueID": sub_id,
                "tactic": tactic_slug,
                "score": SEVERITY_SCORE[severity],
                "color": SEVERITY_COLOR[severity],
                "comment": sub["description"],
                "enabled": True,
                "metadata": [
                    {"name": "Severity", "value": severity},
                    {"name": "Parent Technique", "value": parent_id},
                    {"name": "Tactic", "value": sub["tactic_name"]},
                ],
                "links": [
                    {
                        "label": "ATX-1 Documentation",
                        "url": "https://aegis-docs.com/threat-matrix/techniques",
                    },
                    {
                        "label": "STIX Bundle",
                        "url": "https://aegis-governance.com/atx-1/stix-bundle.json",
                    },
                ],
                "showSubtechniques": False,
            }
            owasp = sub.get("owasp_mapping") or []
            if owasp:
                entry["metadata"].insert(
                    -1, {"name": "OWASP", "value": ", ".join(owasp)}
                )
            new_entries.append(entry)
            nav_by_id[sub_id] = entry

    if new_entries:
        nav["techniques"].extend(new_entries)

    NAV_PATH.write_text(
        json.dumps(nav, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Marked {len(parents_with_subs)} parent technique(s) as having sub-techniques")
    print(f"Added {len(new_entries)} sub-technique entries to Navigator layer")
    print(f"Total Navigator technique entries: {len(nav['techniques'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

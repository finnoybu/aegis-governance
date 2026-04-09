#!/usr/bin/env python3
"""Add STIX 2.1 attack-pattern objects for ATX-1 v2.2 sub-techniques.

Each sub-technique becomes an attack-pattern object with
``x_mitre_is_subtechnique: true`` and a ``subtechnique-of`` relationship
back to its parent technique.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

DATA_PATH = Path("docs/atx/v2/data/atx-1-techniques.json")
STIX_PATH = Path("docs/atx/v2/stix/atx-1-bundle.json")

# Stable namespace for deterministic IDs
NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def deterministic_id(prefix: str, key: str) -> str:
    return f"{prefix}--{uuid.uuid5(NAMESPACE, key)}"


def main() -> int:
    techniques = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    bundle = json.loads(STIX_PATH.read_text(encoding="utf-8"))

    # Build maps from existing bundle
    existing_attack_patterns: dict[str, dict] = {}
    identity_id = None
    for obj in bundle["objects"]:
        if obj.get("type") == "identity":
            identity_id = obj["id"]
        if obj.get("type") == "attack-pattern":
            for ref in obj.get("external_references", []):
                if ref.get("source_name") == "atx-1":
                    existing_attack_patterns[ref["external_id"]] = obj

    if identity_id is None:
        print("ERROR: no identity object in bundle", file=sys.stderr)
        return 1

    by_id = {t["id"]: t for t in techniques}
    parents_with_subs = {
        t["id"]: t["sub_techniques"]
        for t in techniques
        if "sub_techniques" in t
    }

    new_objects: list[dict] = []
    timestamp = "2026-04-01T00:00:00.000Z"

    for parent_id, sub_ids in parents_with_subs.items():
        parent_ap = existing_attack_patterns.get(parent_id)
        if parent_ap is None:
            print(f"WARNING: parent technique {parent_id} not in STIX bundle, skipping its sub-techniques")
            continue

        for sub_id in sub_ids:
            if sub_id in existing_attack_patterns:
                continue
            sub = by_id[sub_id]

            ap_id = deterministic_id("attack-pattern", f"atx1:{sub_id}")
            kill_chain_phase = parent_ap["kill_chain_phases"][0]["phase_name"]

            external_refs = [
                {"source_name": "atx-1", "external_id": sub_id},
            ]
            for owasp in sub.get("owasp_mapping") or []:
                external_refs.append(
                    {
                        "source_name": "owasp-llm-top-10",
                        "external_id": owasp,
                    }
                )

            attack_pattern = {
                "type": "attack-pattern",
                "spec_version": "2.1",
                "id": ap_id,
                "created": timestamp,
                "modified": timestamp,
                "created_by_ref": identity_id,
                "name": sub["name"],
                "description": sub["description"],
                "kill_chain_phases": [
                    {
                        "kill_chain_name": "atx-1",
                        "phase_name": kill_chain_phase,
                    }
                ],
                "external_references": external_refs,
                "x_mitre_is_subtechnique": True,
                "x_aegis_parent_technique": parent_id,
            }
            new_objects.append(attack_pattern)
            existing_attack_patterns[sub_id] = attack_pattern

            # Create subtechnique-of relationship
            rel_id = deterministic_id("relationship", f"atx1:subtech-of:{sub_id}")
            relationship = {
                "type": "relationship",
                "spec_version": "2.1",
                "id": rel_id,
                "created": timestamp,
                "modified": timestamp,
                "created_by_ref": identity_id,
                "relationship_type": "subtechnique-of",
                "source_ref": ap_id,
                "target_ref": parent_ap["id"],
            }
            new_objects.append(relationship)

    if new_objects:
        bundle["objects"].extend(new_objects)

    STIX_PATH.write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    sub_count = sum(1 for o in new_objects if o["type"] == "attack-pattern")
    rel_count = sum(1 for o in new_objects if o["type"] == "relationship")
    print(f"Added {sub_count} sub-technique attack-patterns and {rel_count} subtechnique-of relationships")
    print(f"Total STIX objects: {len(bundle['objects'])}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main())

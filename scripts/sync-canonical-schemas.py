#!/usr/bin/env python3
"""Sync mirrored shared schemas from the canonical `aegis` repository.

This script copies the shared schema domains from:
  ../aegis/schemas/

into:
  ./aegis-core/schemas/

It intentionally syncs only the shared cross-repository contract domains:
  - agp/
  - aiam/
  - capability/
  - common/
  - governance/

It does not modify:
  - examples/

Usage:
  python scripts/sync-canonical-schemas.py
  python scripts/sync-canonical-schemas.py --check
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

MIRRORED_DIRS = ("agp", "aiam", "capability", "common", "governance")


@dataclass
class SyncStats:
    created: int = 0
    updated: int = 0
    deleted: int = 0
    unchanged: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report whether the mirror is out of sync without changing files.",
    )
    return parser.parse_args()


def repo_paths() -> tuple[Path, Path]:
    script_path = Path(__file__).resolve()
    governance_root = script_path.parent.parent
    workspace_root = governance_root.parent
    canonical_root = workspace_root / "aegis" / "schemas"
    mirror_root = governance_root / "aegis-core" / "schemas"
    return canonical_root, mirror_root


def ensure_roots(canonical_root: Path, mirror_root: Path) -> None:
    if not canonical_root.exists():
        raise SystemExit(f"Canonical schema root not found: {canonical_root}")
    if not mirror_root.exists():
        raise SystemExit(f"Mirror schema root not found: {mirror_root}")


def iter_files(root: Path) -> set[Path]:
    return {path.relative_to(root) for path in root.rglob("*") if path.is_file()}


def sync_domain(
    src_domain: Path,
    dst_domain: Path,
    *,
    check_only: bool,
    stats: SyncStats,
) -> list[str]:
    messages: list[str] = []
    src_files = iter_files(src_domain)
    dst_files = iter_files(dst_domain) if dst_domain.exists() else set()

    for rel_path in sorted(src_files):
        src_file = src_domain / rel_path
        dst_file = dst_domain / rel_path

        if not dst_file.exists():
            stats.created += 1
            messages.append(f"CREATE {dst_file}")
            if not check_only:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
            continue

        if filecmp.cmp(src_file, dst_file, shallow=False):
            stats.unchanged += 1
            continue

        stats.updated += 1
        messages.append(f"UPDATE {dst_file}")
        if not check_only:
            shutil.copy2(src_file, dst_file)

    for rel_path in sorted(dst_files - src_files, reverse=True):
        dst_file = dst_domain / rel_path
        stats.deleted += 1
        messages.append(f"DELETE {dst_file}")
        if not check_only and dst_file.exists():
            dst_file.unlink()

    if not check_only:
        prune_empty_dirs(dst_domain)

    return messages


def prune_empty_dirs(root: Path) -> None:
    if not root.exists():
        return
    for directory in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
        try:
            next(directory.iterdir())
        except StopIteration:
            directory.rmdir()


def main() -> int:
    args = parse_args()
    canonical_root, mirror_root = repo_paths()
    ensure_roots(canonical_root, mirror_root)

    stats = SyncStats()
    messages: list[str] = []

    for domain in MIRRORED_DIRS:
        src_domain = canonical_root / domain
        dst_domain = mirror_root / domain
        if not src_domain.exists():
            raise SystemExit(f"Missing canonical domain: {src_domain}")
        messages.extend(
            sync_domain(src_domain, dst_domain, check_only=args.check, stats=stats)
        )

    if messages:
        print("\n".join(messages))

    print(
        f"created={stats.created} updated={stats.updated} "
        f"deleted={stats.deleted} unchanged={stats.unchanged}"
    )

    if args.check and (stats.created or stats.updated or stats.deleted):
        print("Mirror is out of sync with canonical schemas.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify downloaded datasets meet integrity requirements."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.manifest import DATASETS_DIR, verify_dataset

MIN_DATASETS = 30


def main() -> int:
    if not DATASETS_DIR.exists():
        print(f"ERROR: {DATASETS_DIR} does not exist. Run `make download-all` first.")
        return 1

    dataset_dirs = sorted(
        d for d in DATASETS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_") and d.name != ".gitkeep"
    )

    print(f"Found {len(dataset_dirs)} dataset directories\n")

    passed = 0
    failed = []

    for d in dataset_dirs:
        ok, errors = verify_dataset(d)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {d.name}")
        if errors:
            for err in errors:
                print(f"         - {err}")
        if ok:
            passed += 1
        else:
            failed.append((d.name, errors))

    manifest_path = DATASETS_DIR / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"\nManifest: {manifest.get('successful', '?')}/{manifest.get('total', '?')} successful")

    print(f"\nIntegrity check: {passed}/{len(dataset_dirs)} passed")

    if passed < MIN_DATASETS:
        print(f"ERROR: Need at least {MIN_DATASETS} valid datasets, got {passed}")
        return 1

    if failed:
        print(f"ERROR: {len(failed)} datasets failed integrity checks")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

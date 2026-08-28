"""Dataset manifest and integrity verification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "datasets"


def write_manifest(results: list[dict[str, Any]]) -> Path:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    path = DATASETS_DIR / "manifest.json"
    payload = {
        "total": len(results),
        "successful": sum(1 for r in results if r.get("success")),
        "datasets": results,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def verify_dataset(dataset_dir: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    required = ["README.md", "eda.ipynb", "manifest.json"]

    for fname in required:
        if not (dataset_dir / fname).exists():
            errors.append(f"Missing {fname}")

    data_dir = dataset_dir / "data"
    if not data_dir.is_dir():
        errors.append("Missing data/ directory")
    elif not any(data_dir.glob("*.parquet")):
        errors.append("No parquet files in data/")

    manifest_path = dataset_dir / "manifest.json"
    if manifest_path.exists():
        try:
            meta = json.loads(manifest_path.read_text(encoding="utf-8"))
            for rel in meta.get("files", []):
                if not (dataset_dir / rel).exists():
                    errors.append(f"Manifest references missing file: {rel}")
        except json.JSONDecodeError:
            errors.append("Invalid manifest.json")

    return len(errors) == 0, errors

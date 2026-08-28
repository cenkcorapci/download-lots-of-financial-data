#!/usr/bin/env python3
"""Download all financial datasets."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.downloaders.registry import get_all_downloaders
from scripts.lib.manifest import write_manifest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> int:
    load_dotenv(ROOT / ".env")

    downloaders = get_all_downloaders()
    logger.info("Starting download of %d datasets ...", len(downloaders))

    results = []
    failures = []

    for dl in tqdm(downloaders, desc="Datasets", unit="dataset"):
        result = dl.run()
        entry = {
            "name": result.name,
            "success": result.success,
            "rows": result.rows,
            "error": result.error,
        }
        if result.success:
            entry.update(result.metadata or {})
            results.append(entry)
        else:
            failures.append(entry)
            results.append(entry)
            logger.error("FAILED %s: %s", result.name, result.error)

    write_manifest(results)

    ok = sum(1 for r in results if r.get("success"))
    logger.info("Done: %d/%d datasets downloaded successfully", ok, len(downloaders))

    if failures:
        logger.warning("%d failures:", len(failures))
        for f in failures:
            logger.warning("  - %s: %s", f["name"], f["error"])

    if ok < 30:
        logger.error("Definition of done not met: need >= 30 datasets, got %d", ok)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

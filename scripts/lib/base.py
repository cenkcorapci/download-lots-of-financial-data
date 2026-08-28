"""Base classes for dataset downloaders."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .notebook import write_eda_notebook
from .readme import write_readme

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "datasets"


@dataclass
class DownloadResult:
    name: str
    success: bool
    rows: int = 0
    files: list[str] = field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DatasetDownloader(ABC):
    """Download one dataset into datasets/<name>/ with README and EDA notebook."""

    name: str
    category: str
    description: str
    source: str
    license_info: str = "See source terms of use"

    def output_dir(self) -> Path:
        return DATASETS_DIR / self.name

    def data_dir(self) -> Path:
        return self.output_dir() / "data"

    @abstractmethod
    def fetch(self) -> pd.DataFrame | dict[str, pd.DataFrame]:
        """Return a DataFrame or dict of named DataFrames to persist."""

    def transform(self, data: pd.DataFrame | dict[str, pd.DataFrame]) -> pd.DataFrame | dict[str, pd.DataFrame]:
        return data

    def save(self, data: pd.DataFrame | dict[str, pd.DataFrame]) -> list[Path]:
        self.data_dir().mkdir(parents=True, exist_ok=True)
        saved: list[Path] = []

        if isinstance(data, dict):
            for key, df in data.items():
                path = self.data_dir() / f"{key}.parquet"
                df.to_parquet(path, index=False)
                saved.append(path)
        else:
            path = self.data_dir() / "data.parquet"
            data.to_parquet(path, index=False)
            saved.append(path)

        return saved

    def run(self) -> DownloadResult:
        out = self.output_dir()
        try:
            logger.info("Downloading %s ...", self.name)
            raw = self.fetch()
            data = self.transform(raw)
            files = self.save(data)

            if isinstance(data, dict):
                total_rows = sum(len(df) for df in data.values())
                columns = {k: list(df.columns) for k, df in data.items()}
                dtypes = {k: {c: str(df[c].dtype) for c in df.columns} for k, df in data.items()}
            else:
                total_rows = len(data)
                columns = list(data.columns)
                dtypes = {c: str(data[c].dtype) for c in data.columns}

            size_bytes = sum(f.stat().st_size for f in files)
            meta = {
                "name": self.name,
                "category": self.category,
                "description": self.description,
                "source": self.source,
                "license": self.license_info,
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "rows": total_rows,
                "columns": columns,
                "dtypes": dtypes,
                "files": [str(f.relative_to(out)) for f in files],
                "size_bytes": size_bytes,
            }

            write_readme(out, meta)
            write_eda_notebook(out, meta)
            (out / "manifest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

            return DownloadResult(
                name=self.name,
                success=True,
                rows=total_rows,
                files=[str(f) for f in files],
                metadata=meta,
            )
        except Exception as exc:
            logger.exception("Failed to download %s", self.name)
            return DownloadResult(name=self.name, success=False, error=str(exc))

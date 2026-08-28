"""Generate per-dataset README files."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _format_columns(columns: Any) -> str:
    if isinstance(columns, dict):
        lines = []
        for table, cols in columns.items():
            lines.append(f"### `{table}`")
            lines.append("")
            lines.append("| Column | Description |")
            lines.append("|--------|-------------|")
            for col in cols:
                lines.append(f"| `{col}` | — |")
            lines.append("")
        return "\n".join(lines)

    lines = ["| Column | Description |", "|--------|-------------|"]
    for col in columns:
        lines.append(f"| `{col}` | — |")
    return "\n".join(lines)


def write_readme(output_dir: Path, meta: dict[str, Any]) -> None:
    size_mb = meta.get("size_bytes", 0) / (1024 * 1024)
    files_list = "\n".join(f"- `{f}`" for f in meta.get("files", []))

    content = f"""# {meta['name']}

## Overview

{meta['description']}

| Property | Value |
|----------|-------|
| **Category** | {meta['category']} |
| **Source** | {meta['source']} |
| **License** | {meta['license']} |
| **Rows** | {meta.get('rows', 'N/A'):,} |
| **Size** | {size_mb:.2f} MB |
| **Downloaded** | {meta.get('downloaded_at', 'N/A')} |

## Files

{files_list}

## Columns

{_format_columns(meta.get('columns', []))}

## How to read

```python
import pandas as pd
from pathlib import Path

data_dir = Path("datasets/{meta['name']}/data")
# Single-table datasets:
df = pd.read_parquet(data_dir / "data.parquet")
# Multi-table datasets: load each .parquet file by name.
```

## EDA

Open `eda.ipynb` in this folder for exploratory analysis.

## Notes

- Data is stored as Parquet for fast columnar reads.
- Re-download with `make download-all` from the repository root.
"""
    (output_dir / "README.md").write_text(content, encoding="utf-8")

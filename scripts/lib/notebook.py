"""Generate EDA Jupyter notebooks for each dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")],
    }


def _markdown_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")],
    }


def write_eda_notebook(output_dir: Path, meta: dict[str, Any]) -> None:
    files = meta.get("files", [])
    first_file = files[0] if files else "data/data.parquet"
    rel_path = first_file.replace("\\", "/")

    cells = [
        _markdown_cell(
            f"# EDA: {meta['name']}\n\n"
            f"**Category:** {meta['category']}  \n"
            f"**Source:** {meta['source']}  \n"
            f"**Description:** {meta['description']}"
        ),
        _code_cell(
            "from pathlib import Path\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n\n"
            f"DATA_PATH = Path('{rel_path}')\n"
            "df = pd.read_parquet(DATA_PATH)\n"
            "df.head()"
        ),
        _code_cell("df.info()"),
        _code_cell("df.describe(include='all').T"),
        _code_cell(
            "# Missing values\n"
            "missing = df.isnull().sum()\n"
            "missing[missing > 0]"
        ),
        _code_cell(
            "# Numeric column distributions (first 6 numeric cols)\n"
            "numeric = df.select_dtypes('number')\n"
            "if not numeric.empty:\n"
            "    cols = list(numeric.columns[:6])\n"
            "    numeric[cols].hist(figsize=(12, 8), bins=30)\n"
            "    plt.tight_layout()\n"
            "    plt.show()"
        ),
        _code_cell(
            "# Time series preview if a date/datetime column exists\n"
            "date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]\n"
            "if date_cols:\n"
            "    dc = date_cols[0]\n"
            "    tmp = df.copy()\n"
            "    tmp[dc] = pd.to_datetime(tmp[dc], errors='coerce')\n"
            "    tmp = tmp.dropna(subset=[dc]).sort_values(dc)\n"
            "    num = tmp.select_dtypes('number')\n"
            "    if not num.empty:\n"
            "        tmp.set_index(dc)[num.columns[0]].tail(500).plot(figsize=(12, 4), title=num.columns[0])\n"
            "        plt.tight_layout()\n"
            "        plt.show()"
        ),
    ]

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "cells": cells,
    }

    (output_dir / "eda.ipynb").write_text(json.dumps(notebook, indent=1), encoding="utf-8")

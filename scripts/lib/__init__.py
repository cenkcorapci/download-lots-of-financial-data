"""Shared utilities for dataset downloaders."""

from .base import DatasetDownloader, DownloadResult
from .manifest import write_manifest, verify_dataset

__all__ = [
    "DatasetDownloader",
    "DownloadResult",
    "write_manifest",
    "verify_dataset",
]

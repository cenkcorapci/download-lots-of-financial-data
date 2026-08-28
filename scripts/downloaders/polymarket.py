"""Polymarket prediction market data downloaders."""

from __future__ import annotations

import pandas as pd
import requests

from scripts.lib.base import DatasetDownloader

GAMMA_API = "https://gamma-api.polymarket.com"


class PolymarketMarketsDownloader(DatasetDownloader):
    name = "polymarket-active-markets"
    category = "polymarket"
    description = "Active Polymarket prediction markets with prices, volume, and metadata."
    source = "Polymarket Gamma API"
    license_info = "Polymarket terms of use"

    def fetch(self) -> pd.DataFrame:
        rows = []
        offset = 0
        limit = 100
        while offset < 500:
            resp = requests.get(
                f"{GAMMA_API}/markets",
                params={"limit": limit, "offset": offset, "active": "true"},
                timeout=60,
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            for m in batch:
                rows.append(
                    {
                        "id": m.get("id"),
                        "question": m.get("question"),
                        "slug": m.get("slug"),
                        "end_date": m.get("endDate"),
                        "volume": m.get("volume"),
                        "liquidity": m.get("liquidity"),
                        "outcome_prices": str(m.get("outcomePrices")),
                        "outcomes": str(m.get("outcomes")),
                        "active": m.get("active"),
                        "closed": m.get("closed"),
                        "category": m.get("category"),
                    }
                )
            offset += limit
            if len(batch) < limit:
                break
        if not rows:
            raise RuntimeError("No Polymarket markets returned")
        return pd.DataFrame(rows)


class PolymarketEventsDownloader(DatasetDownloader):
    name = "polymarket-events"
    category = "polymarket"
    description = "Polymarket events grouping related prediction markets."
    source = "Polymarket Gamma API"
    license_info = "Polymarket terms of use"

    def fetch(self) -> pd.DataFrame:
        rows = []
        offset = 0
        limit = 100
        while offset < 300:
            resp = requests.get(
                f"{GAMMA_API}/events",
                params={"limit": limit, "offset": offset},
                timeout=60,
            )
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            for e in batch:
                rows.append(
                    {
                        "id": e.get("id"),
                        "title": e.get("title"),
                        "slug": e.get("slug"),
                        "description": (e.get("description") or "")[:500],
                        "start_date": e.get("startDate"),
                        "end_date": e.get("endDate"),
                        "volume": e.get("volume"),
                        "liquidity": e.get("liquidity"),
                        "active": e.get("active"),
                        "closed": e.get("closed"),
                    }
                )
            offset += limit
            if len(batch) < limit:
                break
        if not rows:
            raise RuntimeError("No Polymarket events returned")
        return pd.DataFrame(rows)


POLYMARKET_DOWNLOADERS = [
    PolymarketMarketsDownloader,
    PolymarketEventsDownloader,
]

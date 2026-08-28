"""Forex and currency dataset downloaders."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from scripts.lib.base import DatasetDownloader

PERIOD = "5y"


def _download_pairs(pairs: list[str]) -> pd.DataFrame:
    frames = []
    for pair in pairs:
        hist = yf.Ticker(pair).history(period=PERIOD, auto_adjust=True)
        if hist.empty:
            continue
        hist = hist.reset_index()
        hist["pair"] = pair
        hist.columns = [c.lower().replace(" ", "_") for c in hist.columns]
        if "date" not in hist.columns and "datetime" in hist.columns:
            hist = hist.rename(columns={"datetime": "date"})
        frames.append(hist)
    if not frames:
        raise RuntimeError("No forex data returned")
    return pd.concat(frames, ignore_index=True)


class ForexMajorsDownloader(DatasetDownloader):
    name = "forex-majors-daily"
    category = "forex"
    description = "Daily OHLCV for major G10 currency pairs vs USD."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X"]

    def fetch(self) -> pd.DataFrame:
        return _download_pairs(self.PAIRS)


class ForexCrossesDownloader(DatasetDownloader):
    name = "forex-crosses-daily"
    category = "forex"
    description = "Daily OHLCV for major cross currency pairs (non-USD)."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    PAIRS = ["EURGBP=X", "EURJPY=X", "GBPJPY=X", "EURCHF=X", "AUDJPY=X", "EURAUD=X"]

    def fetch(self) -> pd.DataFrame:
        return _download_pairs(self.PAIRS)


class ForexEmergingDownloader(DatasetDownloader):
    name = "forex-emerging-daily"
    category = "forex"
    description = "Daily OHLCV for emerging market currencies vs USD."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    PAIRS = ["USDMXN=X", "USDBRL=X", "USDZAR=X", "USDTRY=X", "USDKRW=X", "USDINR=X", "USDCNH=X"]

    def fetch(self) -> pd.DataFrame:
        return _download_pairs(self.PAIRS)


class DollarIndexDownloader(DatasetDownloader):
    name = "dollar-index-daily"
    category = "forex"
    description = "Daily US Dollar Index (DXY) OHLCV."
    source = "Yahoo Finance (yfinance) — DX-Y.NYB"
    license_info = "Yahoo Finance terms of use"

    def fetch(self) -> pd.DataFrame:
        return _download_pairs(["DX-Y.NYB"])


FOREX_DOWNLOADERS = [
    ForexMajorsDownloader,
    ForexCrossesDownloader,
    ForexEmergingDownloader,
    DollarIndexDownloader,
]

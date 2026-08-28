"""Stock price dataset downloaders via Yahoo Finance."""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

from scripts.lib.base import DatasetDownloader

PERIOD = "5y"


def _download_tickers(tickers: list[str], label: str) -> pd.DataFrame:
    frames = []
    for ticker in tickers:
        hist = yf.Ticker(ticker).history(period=PERIOD, auto_adjust=True)
        if hist.empty:
            continue
        hist = hist.reset_index()
        hist["ticker"] = ticker
        hist.columns = [c.lower().replace(" ", "_") for c in hist.columns]
        if "date" not in hist.columns and "datetime" in hist.columns:
            hist = hist.rename(columns={"datetime": "date"})
        frames.append(hist)
    if not frames:
        raise RuntimeError(f"No data returned for {label}")
    return pd.concat(frames, ignore_index=True)


class SP500SampleDownloader(DatasetDownloader):
    name = "sp500-sample-ohlcv"
    category = "stocks"
    description = "Daily OHLCV for 50 large-cap S&P 500 constituents (5-year history)."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "LLY", "AVGO", "JPM",
        "UNH", "XOM", "V", "MA", "PG", "JNJ", "HD", "COST", "ABBV", "MRK",
        "CRM", "AMD", "NFLX", "WMT", "BAC", "KO", "PEP", "TMO", "CSCO", "LIN",
        "ADBE", "ACN", "MCD", "ABT", "DHR", "WFC", "TXN", "DIS", "PM", "INTC",
        "VZ", "CMCSA", "NEE", "RTX", "HON", "QCOM", "IBM", "AMGN", "CAT", "GE",
    ]

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(self.TICKERS, self.name)


class Nasdaq100Downloader(DatasetDownloader):
    name = "nasdaq100-ohlcv"
    category = "stocks"
    description = "Daily OHLCV for Nasdaq-100 technology-heavy constituents."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = [
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "AVGO", "COST",
        "NFLX", "AMD", "ADBE", "PEP", "CSCO", "TMUS", "INTC", "CMCSA", "TXN", "QCOM",
        "INTU", "AMGN", "HON", "AMAT", "ISRG", "BKNG", "VRTX", "ADP", "SBUX", "GILD",
    ]

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(self.TICKERS, self.name)


class Dow30Downloader(DatasetDownloader):
    name = "dow30-ohlcv"
    category = "stocks"
    description = "Daily OHLCV for all 30 Dow Jones Industrial Average components."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = [
        "AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "DOW",
        "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM",
        "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WMT", "WBA",
    ]

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(self.TICKERS, self.name)


class SectorETFsDownloader(DatasetDownloader):
    name = "sector-etfs-ohlcv"
    category = "stocks"
    description = "Daily OHLCV for SPDR sector ETFs covering all 11 GICS sectors."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLP", "XLY", "XLU", "XLB", "XLRE", "XLC"]

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(self.TICKERS, self.name)


class VolatilityIndicesDownloader(DatasetDownloader):
    name = "volatility-indices"
    category = "stocks"
    description = "Daily VIX, VXN, and RVX implied volatility index levels."
    source = "Yahoo Finance (yfinance) — CBOE indices"
    license_info = "Yahoo Finance terms of use"

    TICKERS = ["^VIX", "^VXN", "^RVX"]

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(self.TICKERS, self.name)


class InternationalIndicesDownloader(DatasetDownloader):
    name = "international-indices"
    category = "stocks"
    description = "Daily OHLCV for major global equity indices (US, Europe, Asia)."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = ["^GSPC", "^DJI", "^IXIC", "^FTSE", "^GDAXI", "^FCHI", "^N225", "^HSI", "^STOXX50E"]

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(self.TICKERS, self.name)


class FAANGPlusDownloader(DatasetDownloader):
    name = "faang-plus-ohlcv"
    category = "stocks"
    description = "Daily OHLCV for mega-cap tech growth stocks (FAANG+)."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = ["META", "AAPL", "AMZN", "NFLX", "GOOGL", "MSFT", "NVDA", "TSLA"]

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(self.TICKERS, self.name)


class BondETFsDownloader(DatasetDownloader):
    name = "bond-etfs-ohlcv"
    category = "stocks"
    description = "Daily OHLCV for treasury and corporate bond ETFs."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = ["TLT", "IEF", "SHY", "LQD", "HYG", "AGG", "BND"]

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(self.TICKERS, self.name)


class SmallCapETFDownloader(DatasetDownloader):
    name = "small-cap-etf-ohlcv"
    category = "stocks"
    description = "Daily OHLCV for Russell 2000 proxy ETF (IWM)."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(["IWM"], self.name)


class DividendAristocratsDownloader(DatasetDownloader):
    name = "dividend-aristocrats-ohlcv"
    category = "stocks"
    description = "Daily OHLCV for S&P Dividend Aristocrats sample (25+ years of increases)."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = ["JNJ", "PG", "KO", "PEP", "MMM", "ABT", "CL", "EMR", "ITW", "GPC", "SWK", "LOW"]

    def fetch(self) -> pd.DataFrame:
        return _download_tickers(self.TICKERS, self.name)


STOCK_DOWNLOADERS = [
    SP500SampleDownloader,
    Nasdaq100Downloader,
    Dow30Downloader,
    SectorETFsDownloader,
    VolatilityIndicesDownloader,
    InternationalIndicesDownloader,
    FAANGPlusDownloader,
    BondETFsDownloader,
    SmallCapETFDownloader,
    DividendAristocratsDownloader,
]

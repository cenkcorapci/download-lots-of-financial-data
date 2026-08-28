"""Cryptocurrency dataset downloaders."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import requests
import yfinance as yf

from scripts.lib.base import DatasetDownloader

PERIOD = "5y"
BINANCE_API = "https://api.binance.com/api/v3"


def _download_crypto_yf(symbols: list[str]) -> pd.DataFrame:
    frames = []
    for sym in symbols:
        hist = yf.Ticker(sym).history(period=PERIOD, auto_adjust=True)
        if hist.empty:
            continue
        hist = hist.reset_index()
        hist["symbol"] = sym
        hist.columns = [c.lower().replace(" ", "_") for c in hist.columns]
        if "date" not in hist.columns and "datetime" in hist.columns:
            hist = hist.rename(columns={"datetime": "date"})
        frames.append(hist)
    if not frames:
        raise RuntimeError("No crypto data from yfinance")
    return pd.concat(frames, ignore_index=True)


class CryptoMajorDownloader(DatasetDownloader):
    name = "crypto-btc-eth-daily"
    category = "crypto"
    description = "Daily OHLCV for Bitcoin and Ethereum (BTC-USD, ETH-USD)."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    def fetch(self) -> pd.DataFrame:
        return _download_crypto_yf(["BTC-USD", "ETH-USD"])


class CryptoTop10Downloader(DatasetDownloader):
    name = "crypto-top10-daily"
    category = "crypto"
    description = "Daily OHLCV for top 10 cryptocurrencies by market cap."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    SYMBOLS = [
        "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
        "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "LINK-USD",
    ]

    def fetch(self) -> pd.DataFrame:
        return _download_crypto_yf(self.SYMBOLS)


class CryptoDeFiDownloader(DatasetDownloader):
    name = "crypto-defi-tokens"
    category = "crypto"
    description = "Daily OHLCV for major DeFi protocol tokens."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    SYMBOLS = ["UNI-USD", "AAVE-USD", "MKR-USD", "CRV-USD", "SNX-USD", "COMP-USD", "SUSHI-USD"]

    def fetch(self) -> pd.DataFrame:
        return _download_crypto_yf(self.SYMBOLS)


class BinanceBTCKlinesDownloader(DatasetDownloader):
    name = "binance-btc-klines-1h"
    category = "crypto"
    description = "Binance BTCUSDT 1-hour OHLCV candles (last 1000 bars via public API)."
    source = "Binance REST API (public)"
    license_info = "Binance API terms of use"

    def fetch(self) -> pd.DataFrame:
        resp = requests.get(
            f"{BINANCE_API}/klines",
            params={"symbol": "BTCUSDT", "interval": "1h", "limit": 1000},
            timeout=60,
        )
        resp.raise_for_status()
        rows = resp.json()
        df = pd.DataFrame(
            rows,
            columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "trades", "taker_buy_base",
                "taker_buy_quote", "ignore",
            ],
        )
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
        for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["symbol"] = "BTCUSDT"
        return df.drop(columns=["ignore"])


class FearGreedIndexDownloader(DatasetDownloader):
    name = "crypto-fear-greed-index"
    category = "crypto"
    description = "Crypto Fear & Greed Index daily values (alternative.me)."
    source = "alternative.me Fear & Greed API"
    license_info = "alternative.me terms"

    def fetch(self) -> pd.DataFrame:
        resp = requests.get(
            "https://api.alternative.me/fng/?limit=0&format=json",
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="s", utc=True)
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.rename(columns={"value_classification": "classification"})
        return df[["timestamp", "value", "classification", "time_until_update"]]


class BinanceOrderBookSnapshotDownloader(DatasetDownloader):
    name = "binance-btc-orderbook-l2"
    category = "orderbook"
    description = (
        "Binance BTCUSDT Level-2 order book snapshot (top 1000 price levels). "
        "Public L2 proxy for microstructure research; true L3 requires exchange feeds."
    )
    source = "Binance REST API /api/v3/depth"
    license_info = "Binance API terms of use"

    def fetch(self) -> pd.DataFrame:
        resp = requests.get(
            f"{BINANCE_API}/depth",
            params={"symbol": "BTCUSDT", "limit": 1000},
            timeout=60,
        )
        resp.raise_for_status()
        book = resp.json()
        captured_at = datetime.now(timezone.utc).isoformat()

        bids = pd.DataFrame(book["bids"], columns=["price", "quantity"])
        bids["side"] = "bid"
        asks = pd.DataFrame(book["asks"], columns=["price", "quantity"])
        asks["side"] = "ask"

        df = pd.concat([bids, asks], ignore_index=True)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["symbol"] = "BTCUSDT"
        df["captured_at"] = captured_at
        df["last_update_id"] = book.get("lastUpdateId")
        return df.sort_values(["side", "price"], ascending=[True, False])


CRYPTO_DOWNLOADERS = [
    CryptoMajorDownloader,
    CryptoTop10Downloader,
    CryptoDeFiDownloader,
    BinanceBTCKlinesDownloader,
    FearGreedIndexDownloader,
    BinanceOrderBookSnapshotDownloader,
]

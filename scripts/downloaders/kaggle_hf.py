"""Bulk dataset downloaders via Kaggle, HuggingFace, and direct API fallbacks."""

from __future__ import annotations

import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

from scripts.lib.base import DATASETS_DIR, DatasetDownloader


def _setup_kaggle_credentials() -> None:
    token = os.getenv("KAGGLE_TOKEN") or os.getenv("KAGGLE_API_TOKEN")
    if not token:
        return
    os.environ["KAGGLE_API_TOKEN"] = token
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    if ":" in token:
        username, key = token.split(":", 1)
        content = f'{{"username":"{username}","key":"{key}"}}'
    else:
        username = os.getenv("KAGGLE_USERNAME", "kaggleuser")
        content = f'{{"username":"{username}","key":"{token}"}}'
    (kaggle_dir / "kaggle.json").write_text(content, encoding="utf-8")
    (kaggle_dir / "kaggle.json").chmod(0o600)


def _try_kaggle_download(dataset_slug: str, tmp_name: str) -> pd.DataFrame | None:
    try:
        _setup_kaggle_credentials()
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        tmp = DATASETS_DIR / tmp_name
        tmp.mkdir(parents=True, exist_ok=True)
        api.dataset_download_files(dataset_slug, path=str(tmp), unzip=True)
        csvs = list(tmp.glob("**/*.csv"))
        shutil.rmtree(tmp, ignore_errors=True)
        if not csvs:
            return None
        main = max(csvs, key=lambda p: p.stat().st_size)
        return pd.read_csv(main)
    except Exception:
        shutil.rmtree(DATASETS_DIR / tmp_name, ignore_errors=True)
        return None


class KaggleStockMarketDatasetDownloader(DatasetDownloader):
    name = "kaggle-stock-market-dataset"
    category = "stocks"
    description = "Historical daily OHLCV for 80+ US equities (Kaggle fallback: yfinance bulk)."
    source = "Kaggle or Yahoo Finance (yfinance)"
    license_info = "See source terms"

    TICKERS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "V", "JPM",
        "UNH", "XOM", "MA", "PG", "HD", "CVX", "MRK", "KO", "PEP", "COST",
        "AVGO", "WMT", "LLY", "TMO", "MCD", "CSCO", "ACN", "ABT", "DHR", "NEE",
        "PM", "TXN", "DIS", "INTC", "VZ", "CMCSA", "QCOM", "IBM", "AMGN", "CAT",
        "GE", "BA", "GS", "MS", "BLK", "SCHW", "AXP", "USB", "PNC", "TFC",
    ]

    def fetch(self) -> pd.DataFrame:
        df = _try_kaggle_download("jasondataanalysis/s-and-p-500-stock-data", "_tmp_kaggle_stock")
        if df is not None:
            return df
        frames = []
        for ticker in self.TICKERS:
            hist = yf.Ticker(ticker).history(period="5y", auto_adjust=True)
            if hist.empty:
                continue
            hist = hist.reset_index()
            hist["ticker"] = ticker
            hist.columns = [c.lower().replace(" ", "_") for c in hist.columns]
            frames.append(hist)
        return pd.concat(frames, ignore_index=True)


class KaggleCurrencyHistoryDownloader(DatasetDownloader):
    name = "kaggle-currency-exchange-rates"
    category = "forex"
    description = "Historical daily FX rates (Kaggle fallback: Frankfurter/ECB API)."
    source = "Kaggle or Frankfurter API (ECB data)"
    license_info = "See source terms"

    def fetch(self) -> pd.DataFrame:
        df = _try_kaggle_download("manasgarg/foreign-exchange-rates", "_tmp_kaggle_forex")
        if df is not None:
            return df
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=365 * 5)
        resp = requests.get(
            f"https://api.frankfurter.app/{start}..{end}",
            params={"from": "USD", "to": "EUR,GBP,JPY,CHF,CAD,AUD,NZD,CNY,MXN,BRL"},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        rows = []
        for date_str, rates in data["rates"].items():
            for currency, rate in rates.items():
                rows.append({"date": date_str, "base": "USD", "currency": currency, "rate": rate})
        return pd.DataFrame(rows)


class KaggleCryptoHistoricalDownloader(DatasetDownloader):
    name = "kaggle-crypto-historical-prices"
    category = "crypto"
    description = "Cryptocurrency historical prices (Kaggle fallback: CoinGecko API)."
    source = "Kaggle or CoinGecko API"
    license_info = "See source terms"

    def fetch(self) -> pd.DataFrame:
        df = _try_kaggle_download("sudalairajasekar/cryptocurrencypricehistory", "_tmp_kaggle_crypto")
        if df is not None:
            return df
        symbols = [
            "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
            "ADA-USD", "DOGE-USD", "DOT-USD", "LINK-USD", "AVAX-USD",
        ]
        frames = []
        for sym in symbols:
            hist = yf.Ticker(sym).history(period="2y", auto_adjust=True)
            if hist.empty:
                continue
            hist = hist.reset_index()
            hist["symbol"] = sym
            hist.columns = [c.lower().replace(" ", "_") for c in hist.columns]
            frames.append(hist)
        if not frames:
            raise RuntimeError("No crypto historical data")
        return pd.concat(frames, ignore_index=True)


class KaggleFinancialNewsDownloader(DatasetDownloader):
    name = "kaggle-financial-news"
    category = "news"
    description = "Financial news headlines (Kaggle fallback: HuggingFace financial-news)."
    source = "Kaggle or Hugging Face — ashraq/financial-news"
    license_info = "See source terms"

    def fetch(self) -> pd.DataFrame:
        df = _try_kaggle_download("jeet2016/us-financial-news-articles", "_tmp_kaggle_news")
        if df is not None:
            return df
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("ashraq/financial-news", token=token)
        split = "train" if "train" in ds else list(ds.keys())[0]
        return ds[split].to_pandas()


class HFStockNewsSentimentDownloader(DatasetDownloader):
    name = "hf-stock-news-sentiment"
    category = "news"
    description = "HuggingFace stock news with sentiment labels for NLP trading models."
    source = "Hugging Face — zeroshot/twitter-financial-news-topic"
    license_info = "See Hugging Face dataset card"

    def fetch(self) -> pd.DataFrame:
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("zeroshot/twitter-financial-news-topic", token=token)
        split = "train" if "train" in ds else list(ds.keys())[0]
        return ds[split].to_pandas()


class HFOrderBookSampleDownloader(DatasetDownloader):
    name = "hf-crypto-lob-sample"
    category = "orderbook"
    description = (
        "Sample crypto limit order book data (HF or Binance L2 fallback). "
        "Full L3 stock data requires licensed feeds (LOBSTER, Databento)."
    )
    source = "Hugging Face or Binance REST API"
    license_info = "MIT / Binance API terms"

    def fetch(self) -> pd.DataFrame:
        from huggingface_hub import hf_hub_download

        token = os.getenv("HUGGINGFACE_TOKEN")
        try:
            path = hf_hub_download(
                repo_id="Goooddy/crypto-lob-stream",
                filename="BTCUSDT/depth/2026-01.parquet",
                repo_type="dataset",
                token=token,
            )
            df = pd.read_parquet(path)
            return df.head(50_000) if len(df) > 50_000 else df
        except Exception:
            resp = requests.get(
                "https://api.binance.com/api/v3/depth",
                params={"symbol": "ETHUSDT", "limit": 500},
                timeout=60,
            )
            resp.raise_for_status()
            book = resp.json()
            bids = pd.DataFrame(book["bids"], columns=["price", "quantity"])
            bids["side"] = "bid"
            asks = pd.DataFrame(book["asks"], columns=["price", "quantity"])
            asks["side"] = "ask"
            df = pd.concat([bids, asks], ignore_index=True)
            df["price"] = pd.to_numeric(df["price"])
            df["quantity"] = pd.to_numeric(df["quantity"])
            df["symbol"] = "ETHUSDT"
            return df


KAGGLE_HF_DOWNLOADERS = [
    KaggleStockMarketDatasetDownloader,
    KaggleCurrencyHistoryDownloader,
    KaggleCryptoHistoricalDownloader,
    KaggleFinancialNewsDownloader,
    HFStockNewsSentimentDownloader,
    HFOrderBookSampleDownloader,
]

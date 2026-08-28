"""Kaggle and HuggingFace bulk dataset downloaders."""

from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

import pandas as pd

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


class KaggleStockMarketDatasetDownloader(DatasetDownloader):
    name = "kaggle-stock-market-dataset"
    category = "stocks"
    description = "Kaggle stock market dataset — historical prices for S&P 500 companies."
    source = "Kaggle — jasondataanalysis/s-and-p-500-stock-data"
    license_info = "See Kaggle dataset license"

    def fetch(self) -> pd.DataFrame:
        _setup_kaggle_credentials()
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        tmp = DATASETS_DIR / "_tmp_kaggle_stock"
        tmp.mkdir(parents=True, exist_ok=True)
        api.dataset_download_files("jasondataanalysis/s-and-p-500-stock-data", path=str(tmp), unzip=True)
        csvs = list(tmp.glob("**/*.csv"))
        if not csvs:
            raise RuntimeError("Kaggle stock dataset: no CSV found")
        df = pd.read_csv(csvs[0])
        shutil.rmtree(tmp, ignore_errors=True)
        return df


class KaggleCurrencyHistoryDownloader(DatasetDownloader):
    name = "kaggle-currency-exchange-rates"
    category = "forex"
    description = "Kaggle historical currency exchange rates dataset."
    source = "Kaggle — manasgarg/foreign-exchange-rates"
    license_info = "See Kaggle dataset license"

    def fetch(self) -> pd.DataFrame:
        _setup_kaggle_credentials()
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        tmp = DATASETS_DIR / "_tmp_kaggle_forex"
        tmp.mkdir(parents=True, exist_ok=True)
        api.dataset_download_files("manasgarg/foreign-exchange-rates", path=str(tmp), unzip=True)
        csvs = list(tmp.glob("**/*.csv"))
        if not csvs:
            raise RuntimeError("Kaggle forex dataset: no CSV found")
        df = pd.read_csv(csvs[0])
        shutil.rmtree(tmp, ignore_errors=True)
        return df


class KaggleCryptoHistoricalDownloader(DatasetDownloader):
    name = "kaggle-crypto-historical-prices"
    category = "crypto"
    description = "Kaggle cryptocurrency historical market data."
    source = "Kaggle — sudalairajasekar/cryptocurrencypricehistory"
    license_info = "See Kaggle dataset license"

    def fetch(self) -> pd.DataFrame:
        _setup_kaggle_credentials()
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        tmp = DATASETS_DIR / "_tmp_kaggle_crypto"
        tmp.mkdir(parents=True, exist_ok=True)
        api.dataset_download_files("sudalairajasekar/cryptocurrencypricehistory", path=str(tmp), unzip=True)
        csvs = list(tmp.glob("**/*.csv"))
        if not csvs:
            raise RuntimeError("Kaggle crypto dataset: no CSV found")
        # Use largest CSV (main data file)
        main = max(csvs, key=lambda p: p.stat().st_size)
        df = pd.read_csv(main)
        shutil.rmtree(tmp, ignore_errors=True)
        return df


class KaggleFinancialNewsDownloader(DatasetDownloader):
    name = "kaggle-financial-news"
    category = "news"
    description = "Kaggle financial news headlines for sentiment and event studies."
    source = "Kaggle — jeet2016/us-financial-news-articles"
    license_info = "See Kaggle dataset license"

    def fetch(self) -> pd.DataFrame:
        _setup_kaggle_credentials()
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        tmp = DATASETS_DIR / "_tmp_kaggle_news"
        tmp.mkdir(parents=True, exist_ok=True)
        api.dataset_download_files("jeet2016/us-financial-news-articles", path=str(tmp), unzip=True)
        csvs = list(tmp.glob("**/*.csv"))
        if not csvs:
            raise RuntimeError("Kaggle news dataset: no CSV found")
        df = pd.read_csv(max(csvs, key=lambda p: p.stat().st_size))
        shutil.rmtree(tmp, ignore_errors=True)
        return df


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
        "Sample crypto limit order book data from HuggingFace (L2 microstructure). "
        "Full L3 stock data requires licensed feeds (LOBSTER, Databento)."
    )
    source = "Hugging Face — Goooddy/crypto-lob-stream (sample)"
    license_info = "MIT — see dataset card"

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
            # Fallback: Binance ETH L2 snapshot if HF file unavailable
            import requests

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

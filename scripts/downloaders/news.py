"""News and sentiment dataset downloaders."""

from __future__ import annotations

import os

import pandas as pd
import requests

from scripts.lib.base import DatasetDownloader


class FinancialPhraseBankDownloader(DatasetDownloader):
    name = "financial-phrasebank"
    category = "news"
    description = "Financial text with sentiment labels for NLP trading signals (PhraseBank-style)."
    source = "Hugging Face — gbharti/finance-alpaca (financial Q&A corpus)"
    license_info = "See Hugging Face dataset card"

    def fetch(self) -> pd.DataFrame:
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("gbharti/finance-alpaca", split="train", token=token)
        return ds.to_pandas()


class AGNewsFinancialDownloader(DatasetDownloader):
    name = "ag-news-headlines"
    category = "news"
    description = "AG News dataset — general news headlines including Business category for trading signals."
    source = "Hugging Face — fancyzhx/ag_news"
    license_info = "See Hugging Face dataset card"

    def fetch(self) -> pd.DataFrame:
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("fancyzhx/ag_news", token=token)
        df = ds["train"].to_pandas()
        label_map = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}
        df["category"] = df["label"].map(label_map)
        return df


class BBCNewsDownloader(DatasetDownloader):
    name = "bbc-news-headlines"
    category = "news"
    description = "BBC News articles across business, tech, politics — useful for macro/trading context."
    source = "Hugging Face — SetFit/bbc-news"
    license_info = "See Hugging Face dataset card"

    def fetch(self) -> pd.DataFrame:
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("SetFit/bbc-news", token=token)
        df = ds["train"].to_pandas()
        return df


class TweetFinancialSentimentDownloader(DatasetDownloader):
    name = "tweet-financial-news-sentiment"
    category = "news"
    description = "Tweets labeled with financial sentiment for NLP-based trading signals."
    source = "Hugging Face — zeroshot/twitter-financial-news-sentiment"
    license_info = "See Hugging Face dataset card"

    def fetch(self) -> pd.DataFrame:
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("zeroshot/twitter-financial-news-sentiment", token=token)
        split = "train" if "train" in ds else list(ds.keys())[0]
        df = ds[split].to_pandas()
        return df


class NewsCategoryDownloader(DatasetDownloader):
    name = "news-category-dataset"
    category = "news"
    description = "Financial news headlines with labels for NLP-based trading research."
    source = "Hugging Face — ashraq/financial-news"
    license_info = "See Hugging Face dataset card"

    def fetch(self) -> pd.DataFrame:
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("ashraq/financial-news", token=token)
        split = "train" if "train" in ds else list(ds.keys())[0]
        return ds[split].to_pandas()


class CryptoPanicNewsDownloader(DatasetDownloader):
    name = "cryptopanic-news-sample"
    category = "news"
    description = "Recent financial and crypto news headlines from public RSS feeds."
    source = "Reuters Business RSS + CoinDesk RSS"
    license_info = "See respective publisher terms"

    def fetch(self) -> pd.DataFrame:
        import feedparser

        feeds = [
            "https://feeds.reuters.com/reuters/businessNews",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
        ]
        rows = []
        for url in feeds:
            feed = feedparser.parse(url)
            for entry in feed.entries[:100]:
                rows.append(
                    {
                        "title": entry.get("title"),
                        "link": entry.get("link"),
                        "published": entry.get("published"),
                        "source_feed": url,
                        "summary": (entry.get("summary") or "")[:500],
                    }
                )
        if not rows:
            raise RuntimeError("No RSS news entries returned")
        return pd.DataFrame(rows)


NEWS_DOWNLOADERS = [
    FinancialPhraseBankDownloader,
    AGNewsFinancialDownloader,
    BBCNewsDownloader,
    TweetFinancialSentimentDownloader,
    NewsCategoryDownloader,
    CryptoPanicNewsDownloader,
]

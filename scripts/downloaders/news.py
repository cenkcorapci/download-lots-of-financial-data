"""News and sentiment dataset downloaders."""

from __future__ import annotations

import os

import pandas as pd
import requests

from scripts.lib.base import DatasetDownloader


class FinancialPhraseBankDownloader(DatasetDownloader):
    name = "financial-phrasebank"
    category = "news"
    description = "Financial PhraseBank — sentences labeled with sentiment (positive/negative/neutral)."
    source = "Hugging Face — financial_phrasebank"
    license_info = "Creative Commons Attribution-NonCommercial-ShareAlike 3.0"

    def fetch(self) -> pd.DataFrame:
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("financial_phrasebank", "sentences_allagree", token=token, trust_remote_code=True)
        df = ds["train"].to_pandas()
        return df


class AGNewsFinancialDownloader(DatasetDownloader):
    name = "ag-news-headlines"
    category = "news"
    description = "AG News dataset — general news headlines including Business category for trading signals."
    source = "Hugging Face — ag_news"
    license_info = "See Hugging Face dataset card"

    def fetch(self) -> pd.DataFrame:
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("ag_news", token=token)
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
    description = "HuffPost news headlines with categories — filter for business/finance use cases."
    source = "Hugging Face — SetFit/en_news_category"
    license_info = "See Hugging Face dataset card"

    def fetch(self) -> pd.DataFrame:
        from datasets import load_dataset

        token = os.getenv("HUGGINGFACE_TOKEN")
        ds = load_dataset("SetFit/en_news_category", token=token)
        df = ds["train"].to_pandas()
        return df


class CryptoPanicNewsDownloader(DatasetDownloader):
    name = "cryptopanic-news-sample"
    category = "news"
    description = "Recent crypto news headlines from CryptoPanic public feed (no API key required)."
    source = "CryptoPanic public RSS/JSON"
    license_info = "CryptoPanic terms of use"

    def fetch(self) -> pd.DataFrame:
        import feedparser

        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        rows = []
        for entry in feed.entries[:200]:
            rows.append(
                {
                    "title": entry.get("title"),
                    "link": entry.get("link"),
                    "published": entry.get("published"),
                    "summary": entry.get("summary", "")[:500],
                }
            )
        if not rows:
            raise RuntimeError("No CryptoPanic RSS entries returned")
        return pd.DataFrame(rows)


NEWS_DOWNLOADERS = [
    FinancialPhraseBankDownloader,
    AGNewsFinancialDownloader,
    BBCNewsDownloader,
    TweetFinancialSentimentDownloader,
    NewsCategoryDownloader,
    CryptoPanicNewsDownloader,
]

"""Company information and fundamentals downloaders."""

from __future__ import annotations

import io

import pandas as pd
import requests
import yfinance as yf

from scripts.lib.base import DatasetDownloader


class SP500CompanyListDownloader(DatasetDownloader):
    name = "sp500-company-list"
    category = "company-info"
    description = "S&P 500 constituent list with ticker, company name, and GICS sector."
    source = "Wikipedia — List of S&P 500 companies"
    license_info = "Wikipedia CC BY-SA"

    def fetch(self) -> pd.DataFrame:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        df = tables[0]
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
        return df


class SP500FundamentalsDownloader(DatasetDownloader):
    name = "sp500-fundamentals-sample"
    category = "company-info"
    description = "Key fundamentals (market cap, P/E, sector) for 30 large S&P 500 companies."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "JPM", "V", "UNH",
        "XOM", "MA", "PG", "HD", "CVX", "MRK", "ABBV", "KO", "PEP", "COST",
        "AVGO", "WMT", "LLY", "TMO", "MCD", "CSCO", "ACN", "ABT", "DHR", "NEE",
    ]

    def fetch(self) -> pd.DataFrame:
        rows = []
        for ticker in self.TICKERS:
            info = yf.Ticker(ticker).info
            rows.append(
                {
                    "ticker": ticker,
                    "name": info.get("longName") or info.get("shortName"),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "market_cap": info.get("marketCap"),
                    "trailing_pe": info.get("trailingPE"),
                    "forward_pe": info.get("forwardPE"),
                    "dividend_yield": info.get("dividendYield"),
                    "beta": info.get("beta"),
                    "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                    "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                    "employees": info.get("fullTimeEmployees"),
                    "country": info.get("country"),
                    "website": info.get("website"),
                }
            )
        return pd.DataFrame(rows)


class SECEdgarTickersDownloader(DatasetDownloader):
    name = "sec-edgar-company-tickers"
    category = "company-info"
    description = "SEC EDGAR company ticker mapping (CIK, title, ticker symbol)."
    source = "SEC EDGAR — company_tickers.json"
    license_info = "Public domain — US SEC"

    def fetch(self) -> pd.DataFrame:
        url = "https://www.sec.gov/files/company_tickers.json"
        resp = requests.get(
            url,
            timeout=60,
            headers={"User-Agent": "download-lots-of-financial-data research@example.com"},
        )
        resp.raise_for_status()
        data = resp.json()
        rows = [
            {"cik": v["cik_str"], "ticker": v["ticker"], "title": v["title"]}
            for v in data.values()
        ]
        return pd.DataFrame(rows).sort_values("ticker").reset_index(drop=True)


class EarningsCalendarDownloader(DatasetDownloader):
    name = "earnings-calendar-sample"
    category = "company-info"
    description = "Upcoming and recent earnings dates for major US equities."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "WMT"]

    def fetch(self) -> pd.DataFrame:
        rows = []
        for ticker in self.TICKERS:
            cal = yf.Ticker(ticker).calendar
            if cal is None or (isinstance(cal, pd.DataFrame) and cal.empty):
                continue
            if isinstance(cal, dict):
                for key, val in cal.items():
                    rows.append({"ticker": ticker, "field": key, "value": str(val)})
            else:
                cal = cal.reset_index() if hasattr(cal, "reset_index") else cal
                cal["ticker"] = ticker
                rows.extend(cal.to_dict(orient="records"))
        if not rows:
            # Fallback: use earnings dates from info
            for ticker in self.TICKERS:
                info = yf.Ticker(ticker).info
                rows.append(
                    {
                        "ticker": ticker,
                        "earnings_date": info.get("earningsTimestamp"),
                        "earnings_high": info.get("earningsHigh"),
                        "earnings_low": info.get("earningsLow"),
                    }
                )
        return pd.DataFrame(rows)


COMPANY_DOWNLOADERS = [
    SP500CompanyListDownloader,
    SP500FundamentalsDownloader,
    SECEdgarTickersDownloader,
    EarningsCalendarDownloader,
]

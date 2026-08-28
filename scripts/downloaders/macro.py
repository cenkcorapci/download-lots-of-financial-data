"""Macroeconomic and sector indicator downloaders."""

from __future__ import annotations

import io

import pandas as pd
import requests
import yfinance as yf

from scripts.lib.base import DatasetDownloader

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"


def _fred_series(series_id: str, name: str) -> pd.DataFrame:
    url = FRED_CSV.format(series_id=series_id)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))
    df.columns = ["date", name]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df[name] = pd.to_numeric(df[name], errors="coerce")
    return df.dropna()


def _download_fred_bundle(series: dict[str, str]) -> pd.DataFrame:
    frames = [_fred_series(sid, label) for sid, label in series.items()]
    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="date", how="outer")
    return merged.sort_values("date").reset_index(drop=True)


class TreasuryYieldsDownloader(DatasetDownloader):
    name = "treasury-yields-fred"
    category = "macro"
    description = "US Treasury constant maturity yields (1M through 30Y) from FRED."
    source = "FRED (Federal Reserve Economic Data)"
    license_info = "Public domain — FRED"

    SERIES = {
        "DGS1MO": "yield_1m",
        "DGS3MO": "yield_3m",
        "DGS2": "yield_2y",
        "DGS5": "yield_5y",
        "DGS10": "yield_10y",
        "DGS30": "yield_30y",
    }

    def fetch(self) -> pd.DataFrame:
        return _download_fred_bundle(self.SERIES)


class MacroIndicatorsDownloader(DatasetDownloader):
    name = "macro-indicators-fred"
    category = "macro"
    description = "Key US macro indicators: GDP, CPI, unemployment, industrial production."
    source = "FRED (Federal Reserve Economic Data)"
    license_info = "Public domain — FRED"

    SERIES = {
        "GDP": "gdp_billions",
        "CPIAUCSL": "cpi",
        "UNRATE": "unemployment_rate",
        "INDPRO": "industrial_production",
        "PAYEMS": "nonfarm_payrolls",
    }

    def fetch(self) -> pd.DataFrame:
        return _download_fred_bundle(self.SERIES)


class FedFundsRateDownloader(DatasetDownloader):
    name = "fed-funds-rate"
    category = "macro"
    description = "Effective Federal Funds Rate daily series from FRED."
    source = "FRED — DFF series"
    license_info = "Public domain — FRED"

    def fetch(self) -> pd.DataFrame:
        return _fred_series("DFF", "fed_funds_rate")


class CommoditiesDownloader(DatasetDownloader):
    name = "commodities-daily"
    category = "macro"
    description = "Daily OHLCV for gold, silver, oil, copper, and natural gas futures/ETFs."
    source = "Yahoo Finance (yfinance)"
    license_info = "Yahoo Finance terms of use"

    TICKERS = ["GC=F", "SI=F", "CL=F", "HG=F", "NG=F", "GLD", "USO"]

    def fetch(self) -> pd.DataFrame:
        frames = []
        for ticker in self.TICKERS:
            hist = yf.Ticker(ticker).history(period="5y", auto_adjust=True)
            if hist.empty:
                continue
            hist = hist.reset_index()
            hist["ticker"] = ticker
            hist.columns = [c.lower().replace(" ", "_") for c in hist.columns]
            frames.append(hist)
        if not frames:
            raise RuntimeError("No commodity data")
        return pd.concat(frames, ignore_index=True)


class WorldBankIndicatorsDownloader(DatasetDownloader):
    name = "world-bank-gdp-growth"
    category = "sector-reports"
    description = "World Bank annual GDP growth (%) for G7 and major emerging economies."
    source = "World Bank Open Data API"
    license_info = "CC BY 4.0 — World Bank"

    COUNTRIES = "USA;GBR;DEU;JPN;CHN;IND;BRA;MEX;KOR;FRA"

    def fetch(self) -> pd.DataFrame:
        url = (
            "https://api.worldbank.org/v2/country/{countries}/indicator/NY.GDP.MKTP.KD.ZG"
            "?format=json&per_page=500"
        ).format(countries=self.COUNTRIES)
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        payload = resp.json()
        records = payload[1]
        rows = []
        for rec in records:
            if rec["value"] is None:
                continue
            rows.append(
                {
                    "country": rec["country"]["value"],
                    "country_code": rec["countryiso3code"],
                    "year": int(rec["date"]),
                    "gdp_growth_pct": float(rec["value"]),
                    "indicator": rec["indicator"]["value"],
                }
            )
        df = pd.DataFrame(rows)
        if df.empty:
            raise RuntimeError("No World Bank data returned")
        return df.sort_values(["country_code", "year"]).reset_index(drop=True)


class SectorProductionDownloader(DatasetDownloader):
    name = "us-sector-industrial-production"
    category = "sector-reports"
    description = "US industrial production indices by major sector from FRED."
    source = "FRED — Federal Reserve Board"
    license_info = "Public domain — FRED"

    SERIES = {
        "IPMAN": "manufacturing",
        "IPUTIL": "utilities",
        "IPMINE": "mining",
        "IPCONGD": "consumer_goods",
        "IPBUSEQ": "business_equipment",
        "IPMAT": "materials",
    }

    def fetch(self) -> pd.DataFrame:
        return _download_fred_bundle(self.SERIES)


MACRO_DOWNLOADERS = [
    TreasuryYieldsDownloader,
    MacroIndicatorsDownloader,
    FedFundsRateDownloader,
    CommoditiesDownloader,
    WorldBankIndicatorsDownloader,
    SectorProductionDownloader,
]

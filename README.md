# Financial Data Download Pipeline

One-command pipeline to download 40+ open financial datasets for stock trading bot research.

## Quick start

```bash
make install        # create venv + install deps
make download-all   # download all datasets (~30-60 min depending on network)
make verify         # integrity check (requires >= 30 valid datasets)
```

## What you get

Each dataset lives in `datasets/<name>/`:

```
datasets/sp500-sample-ohlcv/
├── README.md      # columns, size, how to read
├── eda.ipynb      # exploratory analysis notebook
├── manifest.json  # machine-readable metadata
└── data/
    └── data.parquet
```

## Dataset categories (44 total)

| Category | Count | Sources |
|----------|-------|---------|
| Stocks | 11 | Yahoo Finance, Kaggle |
| Forex | 5 | Yahoo Finance, Kaggle |
| Crypto | 7 | Yahoo Finance, Binance, Kaggle, HF |
| Macro / Sector | 6 | FRED, World Bank, Yahoo Finance |
| News / Sentiment | 8 | HuggingFace, Kaggle, CryptoPanic |
| Polymarket | 2 | Polymarket Gamma API |
| Company Info | 4 | Wikipedia, SEC EDGAR, Yahoo Finance |
| Order Book (L2/L3) | 2 | Binance API, HuggingFace crypto-lob-stream |

## Environment

Create `.env` in the project root:

```env
KAGGLE_TOKEN=your_kaggle_token
HUGGINGFACE_TOKEN=your_hf_token
```

Kaggle and HuggingFace datasets are optional but recommended — the pipeline continues if individual downloads fail.

## L3 order book note

True L3 (individual order-level) equity data requires licensed feeds (LOBSTER, Databento, Kraken L3). This repo includes:
- **binance-btc-orderbook-l2** — live L2 snapshot from Binance public API
- **hf-crypto-lob-sample** — crypto L2/L3 microstructure sample from HuggingFace

## Process documentation

See [docs/PROCESS.md](docs/PROCESS.md) for development task breakdown and commit history.

## License

Scripts are MIT. Each dataset has its own license — see per-dataset README files.

"""Registry of all dataset downloaders."""

from scripts.datasets.company import COMPANY_DOWNLOADERS
from scripts.datasets.crypto import CRYPTO_DOWNLOADERS
from scripts.datasets.forex import FOREX_DOWNLOADERS
from scripts.datasets.kaggle_hf import KAGGLE_HF_DOWNLOADERS
from scripts.datasets.macro import MACRO_DOWNLOADERS
from scripts.datasets.news import NEWS_DOWNLOADERS
from scripts.datasets.polymarket import POLYMARKET_DOWNLOADERS
from scripts.datasets.stocks import STOCK_DOWNLOADERS

ALL_DOWNLOADERS = [
    *STOCK_DOWNLOADERS,
    *FOREX_DOWNLOADERS,
    *CRYPTO_DOWNLOADERS,
    *MACRO_DOWNLOADERS,
    *NEWS_DOWNLOADERS,
    *POLYMARKET_DOWNLOADERS,
    *COMPANY_DOWNLOADERS,
    *KAGGLE_HF_DOWNLOADERS,
]


def get_all_downloaders():
    return [cls() for cls in ALL_DOWNLOADERS]

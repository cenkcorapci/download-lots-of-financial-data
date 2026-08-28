"""Registry of all dataset downloaders."""

from scripts.downloaders.company import COMPANY_DOWNLOADERS
from scripts.downloaders.crypto import CRYPTO_DOWNLOADERS
from scripts.downloaders.forex import FOREX_DOWNLOADERS
from scripts.downloaders.kaggle_hf import KAGGLE_HF_DOWNLOADERS
from scripts.downloaders.macro import MACRO_DOWNLOADERS
from scripts.downloaders.news import NEWS_DOWNLOADERS
from scripts.downloaders.polymarket import POLYMARKET_DOWNLOADERS
from scripts.downloaders.stocks import STOCK_DOWNLOADERS

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

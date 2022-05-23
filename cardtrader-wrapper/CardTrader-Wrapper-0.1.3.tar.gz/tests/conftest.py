import os

import pytest

from cardtrader.service import CardTrader
from cardtrader.sqlite_cache import SQLiteCache


@pytest.fixture(scope="session")
def access_token():
    return os.getenv("CARDTRADER_ACCESS_TOKEN", default="Invalid")


@pytest.fixture(scope="session")
def session(access_token) -> CardTrader:
    return CardTrader(access_token, cache=SQLiteCache("tests/cache.sqlite", expiry=None))

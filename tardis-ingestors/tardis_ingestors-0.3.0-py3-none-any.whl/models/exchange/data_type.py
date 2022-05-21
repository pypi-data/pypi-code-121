from enum import Enum
from typedframe import TypedDataFrame
import numpy as np

from typing import Optional, Dict


class Quotes(TypedDataFrame):
    schema = {
        "symbol": str,
        "timestamp": np.int64,
        "ask_amount": np.float32,
        "ask_price": np.float32,
        "bid_amount": np.float32,
        "bid_price": np.float32,
    }


class Trades(TypedDataFrame):
    schema = {
        "symbol": str,
        "timestamp": np.int64,
        "side": ("buy", "sell"),
        "price": np.float32,
        "amount": np.float32,
    }


MAPPING: Dict[str, TypedDataFrame] = {"quotes": Quotes, "trades": Trades}


class DataType(Enum):
    book_snapshot_25 = "book_snapshot_25"
    book_snapshot_5 = "book_snapshot_5"
    book_ticker = "book_ticker"
    derivative_ticker = "derivative_ticker"
    incremental_book_L2 = "incremental_book_L2"
    liquidations = "liquidations"
    options_chain = "options_chain"
    quotes = "quotes"
    trades = "trades"

    def get_pandas_schema(self) -> Optional[Dict[str, type]]:
        typed_frame = MAPPING.get(self.value)
        if not typed_frame:
            return None
        schema = typed_frame.schema.copy()
        for key, value in schema.items():
            if isinstance(value, tuple):
                schema[key] = "category"
        return schema

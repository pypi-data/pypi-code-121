from typedframe import TypedDataFrame
import numpy as np


class CandleFrame(TypedDataFrame):
    schema = {
        "timestamp": np.int64,
        "open": np.float64,
        "high": np.float64,
        "low": np.float64,
        "close": np.float64,
        "volume": np.float64,
    }


class InstrumentStatusFrame(TypedDataFrame):
    schema = {
        "timestamp": np.int64,
        "exchange": str,
        "symbol": str,
        "underlying": str,
        "type": str,
        "strike": np.float64,
        "expiration": int,
        "open_interest": np.float64,
        "last_price": np.float64,
        "bid_price": np.float64,
        "bid_amount": np.float64,
        "bid_iv": np.float64,
        "ask_price": np.float64,
        "ask_amount": np.float64,
        "ask_iv": np.float64,
        "mark_price": np.float64,
        "mark_iv": np.float64,
        "underlying_index": str,
        "underlying_price": np.float64,
        "delta": np.float64,
        "gamma": np.float64,
        "vega": np.float64,
        "theta": np.float64,
        "rho": np.float64,
    }

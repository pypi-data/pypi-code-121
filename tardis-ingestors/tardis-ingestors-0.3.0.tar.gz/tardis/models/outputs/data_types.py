from typing import Optional
from pydantic import BaseModel


class Candle(BaseModel):
    timestamp: int
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    symbol: Optional[str] = None


class InstrumentStatus(BaseModel):
    timestamp: int
    exchange: str
    symbol: Optional[str]
    underlying: Optional[str]
    type: Optional[str]
    strike: Optional[float]
    expiration: Optional[int]
    open_interest: Optional[float]
    last_price: Optional[float]
    bid_price: Optional[float]
    bid_amount: Optional[float]
    bid_iv: Optional[float]
    ask_price: Optional[float]
    ask_amount: Optional[float]
    ask_iv: Optional[float]
    mark_price: Optional[float]
    mark_iv: Optional[float]
    underlying_index: Optional[str]
    underlying_price: Optional[float]
    delta: Optional[float]
    gamma: Optional[float]
    vega: Optional[float]
    theta: Optional[float]
    rho: Optional[float]

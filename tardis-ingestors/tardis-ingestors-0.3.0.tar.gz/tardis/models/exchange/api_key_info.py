from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from tardis.models.exchange import Exchange


class ExchangeAccess(BaseModel):
    exchange: Exchange
    accessType: str
    from_: datetime = Field(..., alias="from")
    to: datetime
    symbols: list
    dataPlan: str

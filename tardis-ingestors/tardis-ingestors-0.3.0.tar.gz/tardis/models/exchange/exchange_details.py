from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from tardis.models.exchange import Exchange
from tardis.models.exchange.data_type import DataType
from tardis.models.exchange.symbol_type import SymbolType
from datetime import datetime


class AvailableSymbol(BaseModel):
    id: str
    type: SymbolType
    available_since: datetime = Field(..., alias="availableSince")


class Stats(BaseModel):
    trades: int
    book_changes: int = Field(..., alias="bookChanges")


class Symbol(BaseModel):
    id: str
    type: SymbolType
    data_types: List[DataType] = Field(..., alias="dataTypes")
    available_since: datetime = Field(..., alias="availableSince")
    available_to: datetime = Field(..., alias="availableTo")
    stats: Stats


class Datasets(BaseModel):
    formats: List[str]
    exported_from: datetime = Field(..., alias="exportedFrom")
    exported_until: datetime = Field(..., alias="exportedUntil")
    stats: Stats
    symbols: List[Symbol]


class IncidentReport(BaseModel):
    from_: datetime = Field(..., alias="from")
    to: Optional[datetime]
    status: str
    details: str


class ExchangeDetails(BaseModel):
    id: Exchange
    name: str
    enabled: bool
    available_since: datetime = Field(..., alias="availableSince")
    available_channels: List[str] = Field(..., alias="availableChannels")
    available_symbols: List[AvailableSymbol] = Field(..., alias="availableSymbols")
    datasets: Datasets
    incident_reports: List[IncidentReport] = Field(..., alias="incidentReports")

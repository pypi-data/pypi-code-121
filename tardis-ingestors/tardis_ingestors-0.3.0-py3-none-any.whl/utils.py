import gzip
import logging
import os
import re
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Generator, Optional, Union, List, Tuple

import numpy as np
import pandas as pd
import requests
from py_vollib.black_scholes.greeks.numerical import delta, gamma, rho, theta, vega
from py_vollib.black_scholes.implied_volatility import implied_volatility

from tardis.models.exchange import Exchange, ExchangeAccess, ExchangeDetails
from tardis.models.outputs.data_types import Candle, InstrumentStatus

from typing import Dict

# configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


TARDIS_API_URL = "https://api.tardis.dev/v1"
TIME_INTERVAL_REGEX = r"(\d+[.]?\d*)\s?([A-Za-z]+)"
TIME_INTERVAL_UNITS: Dict[str, str] = {
    "ms": "milliseconds",
    "s": "seconds",
    "second": "seconds",
    "min": "minutes",
    "m": "minutes",
    "h": "hours",
    "hr": "hours",
    "hour": "hours",
    "d": "days",
    "day": "days",
}
DELTA_OPTION_REGEX = r"(?P<type>^\w)-(?P<underlying>\w+)-(?P<strike>\d+.?\d*)-(?P<day>\d\d)(?P<moth>\d\d)(?P<year>\d\d)"


def get_exchange_details(exchange: Exchange) -> ExchangeDetails:
    url = f"{TARDIS_API_URL}/exchanges/{exchange.value}"
    data = requests.get(url).json()
    return ExchangeDetails.parse_obj(data)


def get_api_key_info(api_key: str) -> Tuple[ExchangeAccess]:
    url = f"{TARDIS_API_URL}/api-key-info"
    headers = {"Authorization": f"Bearer {api_key}"}
    api_key_info = requests.get(url, headers=headers).json()
    return tuple(ExchangeAccess.parse_obj(element) for element in api_key_info)


def file_name_nested(
    exchange: str, data_type: str, date: date, symbol: str, format: str
) -> str:
    return f"{exchange}/{data_type}/{symbol}_{date.strftime('%Y-%m-%d')}.{format}.gz"


def parse_date(date_str: Union[str, date]) -> date:
    if isinstance(date_str, str):
        return date.fromisoformat(date_str.replace("/", "-"))
    return date_str


def parse_datetime(datetime_str: Union[str, datetime]) -> datetime:
    if isinstance(datetime_str, str):
        return datetime.fromisoformat(datetime_str.replace("/", "-"))
    return datetime_str


def parse_timedelta(timedelta_str: Union[str, timedelta]) -> timedelta:
    if isinstance(timedelta_str, str):
        value, unit = re.match(TIME_INTERVAL_REGEX, timedelta_str.strip()).groups()
        value = float(value)
        unit = TIME_INTERVAL_UNITS.get(unit, unit)
        return timedelta(**{unit: value})
    return timedelta_str


def iterate_time_range(
    start: datetime, end: datetime, interval: timedelta
) -> Generator[datetime, None, None]:
    """Iterate over a time range with a step."""
    current = start
    while current < end:
        yield current
        current += interval


def gunzip_file(
    source_filepath: Path,
    dest_filepath: Path = None,
    delete_source: bool = False,
    block_size: int = 65536,
) -> Path:
    """Unzip a .gz file.

    Args:
        source_filepath (Path): The path to the .gz file to unzip.
        dest_filepath (Path, optional): The path to the destination file. Defaults to the source without .gz
        delete_source (bool, optional): Whether to delete the source file. Defaults to False.
        block_size (int, optional): The block size to use when reading and writing. Defaults to 65536.

    Returns:
        Path: The path to the unzipped file.
    """
    source_filepath = Path(source_filepath)
    assert source_filepath.exists(), f"{source_filepath} does not exist"
    dest_filepath = dest_filepath or source_filepath.parent / source_filepath.stem
    dest_filepath = Path(dest_filepath)
    with gzip.open(str(source_filepath), "rb") as source_file:
        with open(dest_filepath, "wb") as dest_file:
            shutil.copyfileobj(source_file, dest_file, block_size)

    if delete_source:
        source_filepath.unlink()

    return dest_filepath


def trim_csv_file(source_filepath: Path, lines: int = 100):
    """Trim a CSV file to its first N lines."""
    source_filepath = Path(source_filepath)
    assert source_filepath.exists(), f"{source_filepath} does not exist"
    with open(source_filepath, "r") as source_file:
        lines = [next(source_file, "") for _ in range(lines)]
    with open(source_filepath, "w") as source_file:
        source_file.writelines(lines)


def get_utc_timestamp(time: datetime) -> int:
    return int(time.replace(tzinfo=timezone.utc).timestamp() * 1e6)


def parse_underlying(symbol_series: pd.Series, exchange: Exchange) -> pd.Series:
    if exchange == Exchange.deribit:
        return symbol_series.str.extract(r"(^\w+)-")
    if exchange == Exchange.delta:
        return symbol_series.str.extract(r"^\w-(\w+)-")


def parse_symbol(symbol_series: pd.Series, exchange: Exchange) -> pd.DataFrame:
    if exchange == Exchange.delta:
        elements: pd.DataFrame = symbol_series.str.extract(DELTA_OPTION_REGEX)
        expiration = elements.apply(
            lambda x: datetime(int(x["year"]) + 2000, int(x["moth"]), int(x["day"])),
            axis=1,
        ).apply(get_utc_timestamp)
        return pd.DataFrame(
            {
                "type": elements["type"].map({"C": "call", "P": "put"}),
                "strike_price": elements["strike"].astype(float),
                "expiration": expiration,
                "underlying": elements["underlying"],
            }
        )


def get_implied_volatility_for_row(
    row: pd.Series,
    price_col: str,
    underlying_col: str,
    strike_col: str,
    timestamp_col: str,
    expiration_col: str,
    type_col: str,
) -> float:
    try:
        price = row[price_col]  # * row[underlying_col]
        time_to_expiration = (
            (row[expiration_col] - row[timestamp_col]) / 1e6 / 3600 / 24 / 365
        )
        flag = "c" if row[type_col] == "call" else "p"
        return (
            implied_volatility(
                price=price,
                S=row[underlying_col],
                K=row[strike_col],
                t=time_to_expiration,
                r=0.0,
                flag=flag,
            )
            * 100
        )
    except Exception:
        return np.nan


def get_implied_volatility(
    df: pd.DataFrame,
    price_col: str,
    underlying_col: str,
    strike_col: str,
    timestamp_col: str,
    expiration_col: str,
    type_col: str,
) -> pd.Series:

    return df.apply(
        get_implied_volatility_for_row,
        price_col=price_col,
        underlying_col=underlying_col,
        strike_col=strike_col,
        timestamp_col=timestamp_col,
        expiration_col=expiration_col,
        type_col=type_col,
        axis=1,
    )


def get_greek_for_row(
    row: pd.Series,
    greek_func: Callable,
    iv_col: str,
    underlying_col: str,
    strike_col: str,
    timestamp_col: str,
    expiration_col: str,
    type_col: str,
) -> float:
    try:
        sigma = row[iv_col] / 100
        time_to_expiration = (
            (row[expiration_col] - row[timestamp_col]) / 1e6 / 3600 / 24 / 365
        )
        flag = "c" if row[type_col] == "call" else "p"
        return greek_func(
            flag=flag,
            S=row[underlying_col],
            K=row[strike_col],
            t=time_to_expiration,
            r=0.0,
            sigma=sigma,
        )
    except Exception:
        return np.nan


def get_greek(
    df: pd.DataFrame,
    func: Callable,
    iv_col: str,
    underlying_col: str,
    strike_col: str,
    timestamp_col: str,
    expiration_col: str,
    type_col: str,
) -> pd.Series:
    return df.apply(
        get_greek_for_row,
        greek_func=func,
        iv_col=iv_col,
        underlying_col=underlying_col,
        strike_col=strike_col,
        timestamp_col=timestamp_col,
        expiration_col=expiration_col,
        type_col=type_col,
        axis=1,
    )


def generate_candle_from_trades(
    trades: pd.DataFrame, start: datetime, end: datetime, max_decimals: int = 6
) -> List[Candle]:
    """Generate a candle from a trades dataframe."""
    start_ts = int(start.replace(tzinfo=timezone.utc).timestamp() * 1e6)
    if trades.empty:
        return []
    trades = trades.sort_values(by="timestamp")
    candles: pd.DataFrame = trades.groupby("symbol").agg(
        open=pd.NamedAgg("price", "first"),
        high=pd.NamedAgg("price", "max"),
        low=pd.NamedAgg("price", "min"),
        close=pd.NamedAgg("price", "last"),
        volume=pd.NamedAgg("amount", "sum"),
    )
    return [
        Candle(
            timestamp=start_ts,
            open=candle["open"],
            high=candle["high"],
            low=candle["low"],
            close=candle["close"],
            volume=candle["volume"],
            symbol=symbol,
        )
        for symbol, candle in candles.iterrows()
    ]


def generate_options_chain_snapshot(
    options_chain: pd.DataFrame,
    snapshot_time: datetime,
    previous_snapshot: List[InstrumentStatus],
    underlyings: Optional[List[str]],
    exchange: Exchange,
    max_decimals: int = 6,
) -> List[InstrumentStatus]:

    end_ts = get_utc_timestamp(snapshot_time)

    # Parse the underlying from the option symbols
    options_chain["underlying"] = parse_underlying(options_chain["symbol"], exchange)

    # Filter to requested underlyings
    if underlyings:
        options_chain = options_chain.loc[options_chain["underlying"].isin(underlyings)]

    # If there have been no contracts offered or written, return the previous snapshot
    if options_chain.empty:
        return previous_snapshot

    # For each option instrument, get the last status
    options_chain = options_chain.sort_values(by="timestamp")
    spot = options_chain.groupby("underlying").last()["underlying_price"]
    last_status = options_chain.groupby("symbol").last().reset_index()
    altered_symbols = last_status["symbol"].unique()

    # Compose the InstrumentStatus abstraction
    current_snapshot = [
        InstrumentStatus(
            timestamp=end_ts,  # snapshot is at the end of the time range
            exchange=exchange.value,
            symbol=row["symbol"],
            underlying=row["underlying"],
            type=row["type"],
            strike=round(row["strike_price"], max_decimals),
            expiration=int(row["expiration"]),
            last_price=round(row["last_price"], max_decimals),
            open_interest=round(row["open_interest"], max_decimals),
            bid_price=round(row["bid_price"], max_decimals),
            bid_amount=round(row["bid_amount"], max_decimals),
            bid_iv=round(row["bid_iv"], max_decimals),
            ask_price=round(row["ask_price"], max_decimals),
            ask_amount=round(row["ask_amount"], max_decimals),
            ask_iv=round(row["ask_iv"], max_decimals),
            mark_price=round(row["mark_price"], max_decimals),
            mark_iv=round(row["mark_iv"], max_decimals),
            underlying_index=row["underlying_index"],
            underlying_price=round(spot.loc[row["underlying"]], max_decimals),
            delta=round(row["delta"], max_decimals),
            gamma=round(row["gamma"], max_decimals),
            vega=round(row["vega"], max_decimals),
            theta=round(row["theta"], max_decimals),
            rho=round(row["rho"], max_decimals),
        )
        for _, row in last_status.iterrows()
        if int(row["expiration"]) >= end_ts
    ]

    # Add any instruments from the previous snapshot that were not altered in this time
    # range and have not expired
    for instrument_status in previous_snapshot:
        if instrument_status.symbol not in altered_symbols:
            if instrument_status.expiration >= end_ts:
                current_snapshot.append(instrument_status)

    return current_snapshot


def generate_derived_options_chain_snapshot(
    quotes: pd.DataFrame,
    snapshot_time: datetime,
    previous_snapshot: List[InstrumentStatus],
    underlying_prices: Dict[str, float],
    exchange: Exchange,
    max_decimals: int = 6,
) -> List[InstrumentStatus]:

    end_ts = get_utc_timestamp(snapshot_time)

    # Parse the underlying from the option symbols
    quotes["underlying"] = parse_underlying(quotes["symbol"], exchange)

    # Filter to requested underlyings
    quotes = quotes.loc[quotes["underlying"].isin(list(underlying_prices.keys()))]

    # If there have been no contracts offered or written, return the previous snapshot
    if quotes.empty:
        return previous_snapshot

    # For each option instrument, get the last status
    quotes = quotes.sort_values(by="timestamp")
    last_status = quotes.groupby("symbol").last().reset_index()
    last_status = last_status[last_status["symbol"].str.match(DELTA_OPTION_REGEX)]
    altered_symbols = last_status["symbol"].unique()

    parsed_properties = parse_symbol(last_status["symbol"], exchange).drop(
        columns="underlying"
    )
    last_status = pd.concat([last_status, parsed_properties], axis=1)
    last_status["underlying_price"] = last_status["underlying"].map(underlying_prices)

    last_status["mark_price"] = (
        last_status["bid_price"] + last_status["ask_price"]
    ) / 2

    for var in ["bid", "ask", "mark"]:
        last_status[var + "_iv"] = get_implied_volatility(
            last_status,
            var + "_price",
            "underlying_price",
            "strike_price",
            "timestamp",
            "expiration",
            "type",
        )

    for greek, func in zip(
        ["delta", "gamma", "vega", "theta", "rho"], [delta, gamma, vega, theta, rho]
    ):
        last_status[greek] = get_greek(
            last_status,
            func,
            "mark_iv",
            "underlying_price",
            "strike_price",
            "timestamp",
            "expiration",
            "type",
        )

    current_snapshot = [
        InstrumentStatus(
            timestamp=end_ts,  # snapshot is at the end of the time range
            exchange=exchange.value,
            symbol=row["symbol"],
            underlying=row["underlying"],
            type=row["type"],
            strike=round(row["strike_price"], max_decimals),
            expiration=int(row["expiration"]),
            bid_price=round(row["bid_price"], max_decimals),
            bid_amount=round(row["bid_amount"], max_decimals),
            bid_iv=round(row["bid_iv"], max_decimals),
            ask_price=round(row["ask_price"], max_decimals),
            ask_amount=round(row["ask_amount"], max_decimals),
            ask_iv=round(row["ask_iv"], max_decimals),
            mark_price=round(row["mark_price"], max_decimals),
            mark_iv=round(row["mark_iv"], max_decimals),
            underlying_price=round(row["underlying_price"], max_decimals),
            delta=round(row["delta"], max_decimals),
            gamma=round(row["gamma"], max_decimals),
            vega=round(row["vega"], max_decimals),
            theta=round(row["theta"], max_decimals),
            rho=round(row["rho"], max_decimals),
        )
        for _, row in last_status.iterrows()
        if int(row["expiration"]) >= end_ts
    ]

    # Add any instruments from the previous snapshot that were not altered in this time
    # range and have not expired
    for instrument_status in previous_snapshot:
        if instrument_status.symbol not in altered_symbols:
            if instrument_status.expiration >= end_ts:
                current_snapshot.append(instrument_status)

    return current_snapshot


def try_load_dotenv():
    try:
        from dotenv import load_dotenv

        load_dotenv()
    finally:
        pass


def get_tardis_api_key() -> str:
    try_load_dotenv()
    return os.getenv("TARDIS_API_KEY")

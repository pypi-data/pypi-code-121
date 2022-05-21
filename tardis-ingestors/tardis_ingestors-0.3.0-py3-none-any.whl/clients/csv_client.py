import datetime
from pathlib import Path
from typing import Callable, Iterable, Iterator, Optional, Union, List, Tuple, Dict

import dask.dataframe as dd

import pandas as pd
from tardis.models.exchange import Exchange, GroupedSymbol
from tardis.models.exchange.data_type import DataType
from tardis.models.outputs.data_types import InstrumentStatus
from tardis.utils import (
    file_name_nested,
    generate_candle_from_trades,
    generate_options_chain_snapshot,
    generate_derived_options_chain_snapshot,
    get_api_key_info,
    get_exchange_details,
    get_utc_timestamp,
    gunzip_file,
    iterate_time_range,
    logger,
    parse_date,
    parse_datetime,
    parse_timedelta,
)

ONE_DAY = datetime.timedelta(days=1)
ONE_MILLISECOND = datetime.timedelta(milliseconds=1)


class ExchangeCSVClient:
    BASE_URL = "https://api.tardis.dev/v1/"
    COMPRESSED = ".csv.gz"

    def __init__(
        self,
        exchange: Union[Exchange, str],
        api_key: str,
        download_manager: str = "async",
    ):
        """Client for downloading data for an exchange from Tardis.

        Args:
            exchange (Union[Exchange, str]): The exchange to download data for.
            api_key (str): The Tardis API key to use.
        """
        self.exchange = Exchange(exchange)
        self._api_key = api_key

        self.api_key_info = get_api_key_info(api_key)
        self.exchange_details = get_exchange_details(self.exchange)
        self.symbol_datasets = self.exchange_details.datasets.symbols

        assert self.exchange in {access.exchange for access in self.api_key_info}, (
            f"{self.exchange.value} is not included in your plan! Your plan includes: "
            f"{', '.join([access.exchange.value for access in self.api_key_info])}"
        )

        if download_manager == "async":
            from tardis_dev import datasets

            self.download_manager = datasets
        elif download_manager == "sync":
            from tardis.managers.downloands_manager import DownloadsManager

            self.download_manager = DownloadsManager()

    @property
    def exchange_symbols(self) -> List[str]:
        return [symbol_dataset.id for symbol_dataset in self.symbol_datasets]

    @property
    def exchange_data_types(self) -> List[str]:
        return {
            data_type.value
            for symbol_dataset in self.symbol_datasets
            for data_type in symbol_dataset.data_types
        }

    @property
    def exchange_grouped_symbols(self) -> List[str]:
        return [
            symbol.value
            for symbol in GroupedSymbol
            if symbol.value in self.exchange_symbols
        ]

    def _assert_symbol_data_type(self, symbol: str, data_type: str):
        assert symbol in self.exchange_symbols, (
            f"Symbol {symbol} is not available on {self.exchange.value}, "
            f"available symbols: {', '.join(self.exchange_symbols)}"
        )
        symbol_data_types = self.get_symbol_data_types(symbol)
        assert data_type in symbol_data_types, (
            f"Data type {data_type} is not available for {symbol}, "
            f"available data types: {', '.join(symbol_data_types)}"
        )

    def _assert_symbol_date_range(
        self, symbol: str, from_date: datetime.date, to_date: datetime.date
    ):
        from_date_min, from_date_max = self.get_symbol_date_range(symbol)
        assert from_date >= from_date_min, (
            f"{from_date} is before the earliest date available for {symbol}, "
            f"which is {from_date_min}"
        )
        assert to_date <= from_date_max, (
            f"{to_date} is after the latest date available for {symbol}, "
            f"which is {from_date_max}"
        )
        assert to_date >= from_date, f"Date {to_date} must be at or after {from_date}"
        assert to_date <= datetime.date.today(), f"Date {to_date} must be before today"

    def symbols_info(self) -> pd.DataFrame:
        """
        Returns a DataFrame with the exchange symbols, their availability, and their
        data types.
        """
        return pd.DataFrame(
            data=[
                {
                    "symbol_identifier": symbol_dataset.id,
                    "symbol_type": symbol_dataset.type,
                    "available_since": symbol_dataset.available_since,
                    "available_to": symbol_dataset.available_to,
                    "stats_trades": symbol_dataset.stats.trades,
                    "stats_book_changes": symbol_dataset.stats.book_changes,
                }
                | {
                    data_type.value: (
                        True if data_type in symbol_dataset.data_types else False
                    )
                    for data_type in DataType
                }
                for symbol_dataset in self.symbol_datasets
            ]
        )

    def get_symbol_data_types(self, symbol: str) -> List[str]:
        """Get a list of data types available for a given symbol.

        Args:
            symbol (str): The symbol to get data types for.

        Returns:
            list[str]: A list of data types available for the given symbol.
        """
        assert (
            symbol in self.exchange_symbols
        ), f"{symbol} is not part of {self.exchange.value}"
        return [
            data_type.value
            for symbol_dataset in self.symbol_datasets
            for data_type in symbol_dataset.data_types
            if symbol == symbol_dataset.id
        ]

    def get_symbol_date_range(self, symbol: str) -> Tuple[datetime.date, datetime.date]:
        """Get the earliest and latest date available for a given symbol.

        Args:
            symbol (str): The symbol to get the date range for.

        Returns:
            tuple[datetime.date, datetime.date]: The earliest and latest date available
                for the given symbol.
        """
        assert (
            symbol in self.exchange_symbols
        ), f"{symbol} is not part of {self.exchange.value}"
        symbol_data = next(item for item in self.symbol_datasets if item.id == symbol)
        return symbol_data.available_since.date(), symbol_data.available_to.date()

    def download_date_range(
        self,
        symbol: str,
        data_type: Union[DataType, str],
        from_date: Union[datetime.date, str],
        to_date: Union[datetime.date, str],
        location: Path = Path("./datasets"),
        get_filename: Optional[
            Callable[[str, str, str, datetime.date, str], str]
        ] = None,
        unzip: bool = False,
    ) -> List[Path]:
        """Downloads compressed CSV data from the exchange for a given symbol and data
        type. One file per day.

        Args:
            symbol (str): The symbol to download data for.
            data_type (str): The data type to download (e.g. trades, derivative_ticker).
            from_date (Union[datetime.date, str]): The date to start downloading from.
            to_date (Union[datetime.date, str]): The date to end downloading to.
            location (Path, optional): Folder to save files to. Defaults to
                Path("./datasets").
            get_filename (Optional[Callable[[str, str, str, datetime.date, str], str]]):
                Function to get filename. Defaults to None.
            unzip (bool, optional): Whether to unzip the downloaded files. Defaults to
                False.

        Returns:
            list[Path]: List of filepaths to the downloaded files.
        """
        get_filename = get_filename or file_name_nested
        from_date = parse_date(from_date)
        to_date = parse_date(to_date)
        data_type = DataType(data_type)

        self._assert_symbol_data_type(symbol, data_type.value)
        self._assert_symbol_date_range(symbol, from_date, to_date)

        # tardis_dev date range behaves differently for to=from, this is a workaround
        norm_to_date = to_date if to_date == from_date else to_date + ONE_DAY

        num_files = int((to_date - from_date).days + 1)

        self.download_manager.download(
            exchange=self.exchange.value,
            data_types=[data_type.value],
            symbols=[symbol],
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=norm_to_date.strftime("%Y-%m-%d"),
            format="csv",
            download_dir=str(location),
            get_filename=get_filename or file_name_nested,
            api_key=self._api_key,
        )

        dates = [from_date + datetime.timedelta(days=n) for n in range(num_files)]
        filepaths = [
            location
            / get_filename(self.exchange.value, data_type.value, date, symbol, "csv")
            for date in dates
        ]
        if unzip:
            filepaths = [gunzip_file(f, delete_source=True) for f in filepaths]
        return filepaths

    def download_date(
        self,
        symbol: str,
        data_type: Union[DataType, str],
        date: Union[datetime.date, str],
        location: Path = Path("./datasets"),
        filename: str = None,
        unzip: bool = False,
    ) -> Path:
        """Downloads compressed CSV data from the exchange for a given symbol and data,
        and day.

        Args:
            symbol (str): The symbol to download data for.
            data_type (str): The data type to download (e.g. trades, derivative_ticker).
            date (Union[datetime.date, str]): The date to download.
            location (Path, optional): Folder to save files to. Defaults to
                Path("./datasets").
            get_filename (Optional[Callable[[str, str, str, datetime.date, str], str]]):
                Function to get filename. Defaults to None.
            unzip (bool, optional): Whether to unzip the downloaded files. Defaults to
                False.

        Returns:
            Path: Filepath to the downloaded file.
        """
        data_type = DataType(data_type)

        logger.info(f"Downloading {symbol} {data_type.value} data for {date}")
        filepaths = self.download_date_range(
            symbol=symbol,
            data_type=data_type,
            from_date=date,
            to_date=date,
            location=location,
            get_filename=(lambda *args: filename) if filename else None,
            unzip=unzip,
        )
        return filepaths.pop()

    def _iterate_time_range_data_low_mem(
        self,
        from_datetime: datetime.datetime,
        to_datetime: datetime.datetime,
        interval: datetime.timedelta,
        data_type: DataType,
        symbol: str,
        temp_location: Path = Path("./temp"),
    ) -> Iterator[Tuple[datetime.datetime, datetime.datetime, pd.DataFrame]]:
        """Iterates over time range data.

        Args:
            start (datetime.datetime): The start of the time range.
            end (datetime.datetime): The end of the time range.
            interval (datetime.timedelta): The interval to iterate over.
            data_type (DataType): The data type to iterate over.
            symbol (str): The symbol to iterate over.

        Yields:
            tuple: A tuple of (datetime.datetime, datetime.datetime, data_df).
        """

        schema = data_type.get_pandas_schema()
        columns = list(schema.keys()) if schema else None

        available_since, available_to = self.get_symbol_date_range(symbol)

        current_interval_dates: set[datetime.date] = set()
        day_data_filepaths: Dict[datetime.date, Path] = {}
        day_data_dfs: Dict[datetime.date, dd.DataFrame] = {}
        for start in iterate_time_range(from_datetime, to_datetime, interval):
            end = start + interval - ONE_MILLISECOND
            if start.date() < available_since or end.date() > available_to:
                yield start, end, None
                continue
            start_ts, end_ts = get_utc_timestamp(start), get_utc_timestamp(end)
            last_interval_dates = current_interval_dates.copy()
            current_interval_dates = {
                dt.date() for dt in iterate_time_range(start, end, ONE_DAY)
            }.union(set((end.date(),)))
            obsolete_interval_dates = last_interval_dates - current_interval_dates
            new_interval_dates = current_interval_dates - last_interval_dates

            for date in obsolete_interval_dates:  # delete uneeded data
                day_data_filepaths[date].unlink()
                del day_data_filepaths[date]
                del day_data_dfs[date]

            for date in new_interval_dates:  # download new needed data
                filepath = self.download_date(
                    symbol=symbol,
                    data_type=data_type.value,
                    date=date,
                    location=temp_location,
                    filename=symbol
                    + data_type.value
                    + date.strftime("%Y-%m-%d")
                    + self.COMPRESSED,
                    unzip=True,
                )
                day_data_filepaths[date] = filepath

                logger.info(f"Reading data for {date} at {filepath}")
                day_data_dfs[date] = dd.read_csv(
                    str(filepath), usecols=columns, dtype=schema
                )

            if len(day_data_dfs) >= 2:
                current_lazy_df = dd.concat(day_data_dfs.values(), ignore_index=True)
            else:
                current_lazy_df: dd.DataFrame = list(day_data_dfs.values())[0]
            current_lazy_df = current_lazy_df[current_lazy_df["timestamp"] >= start_ts]
            current_lazy_df = current_lazy_df[current_lazy_df["timestamp"] <= end_ts]
            current_df: pd.DataFrame = current_lazy_df.compute()
            yield start, end, current_df.sort_values(by=["timestamp"])

        for date in day_data_filepaths:
            day_data_filepaths[date].unlink()

    def _iterate_time_range_data(
        self,
        from_datetime: datetime.datetime,
        to_datetime: datetime.datetime,
        interval: datetime.timedelta,
        data_type: DataType,
        symbol: str,
        temp_location: Path = Path("./temp"),
    ) -> Iterator[Tuple[datetime.datetime, datetime.datetime, pd.DataFrame]]:
        """Iterates over time range data.

        Args:
            start (datetime.datetime): The start of the time range.
            end (datetime.datetime): The end of the time range.
            interval (datetime.timedelta): The interval to iterate over.
            data_type (DataType): The data type to iterate over.
            symbol (str): The symbol to iterate over.

        Yields:
            tuple: A tuple of (datetime.datetime, datetime.datetime, data_df).
        """
        schema = data_type.get_pandas_schema()
        columns = list(schema.keys()) if schema else None

        current_interval_dates: set[datetime.date] = set()
        day_data_filepaths: Dict[datetime.date, Path] = {}
        day_data_dfs: Dict[datetime.date, pd.DataFrame] = {}
        for start in iterate_time_range(from_datetime, to_datetime, interval):
            end = start + interval - ONE_MILLISECOND
            start_ts, end_ts = get_utc_timestamp(start), get_utc_timestamp(end)
            last_interval_dates = current_interval_dates.copy()
            current_interval_dates = {
                dt.date() for dt in iterate_time_range(start, end, ONE_DAY)
            }.union(set((end.date(),)))
            obsolete_interval_dates = last_interval_dates - current_interval_dates
            new_interval_dates = current_interval_dates - last_interval_dates

            for date in obsolete_interval_dates:  # delete uneeded data
                day_data_filepaths[date].unlink()
                del day_data_filepaths[date]
                del day_data_dfs[date]

            for date in new_interval_dates:  # download new needed data
                filepath = self.download_date(
                    symbol=symbol,
                    data_type=data_type.value,
                    date=date,
                    location=temp_location,
                    filename=symbol
                    + data_type.value
                    + date.strftime("%Y-%m-%d")
                    + self.COMPRESSED,
                )
                day_data_filepaths[date] = filepath

                logger.info(f"Reading data for {date} at {filepath}")
                day_data_dfs[date] = pd.read_csv(
                    str(filepath), usecols=columns, dtype=schema
                )

            current_df = pd.concat(day_data_dfs.values(), ignore_index=True)
            current_df = current_df[current_df["timestamp"].between(start_ts, end_ts)]
            yield start, end, current_df.sort_values(by=["timestamp"])

        for date in day_data_filepaths:
            day_data_filepaths[date].unlink()

    def _iterate_time_range_data_combos(
        self,
        from_datetime: datetime.datetime,
        to_datetime: datetime.datetime,
        interval: datetime.timedelta,
        combos: List[Tuple[DataType, str]],
        temp_location: Path = Path("./temp"),
    ) -> Iterator[Tuple[datetime.datetime, datetime.datetime, Iterable[pd.DataFrame]]]:
        """Iterates over time range data.

        Args:
            start (datetime.datetime): The start of the time range.
            end (datetime.datetime): The end of the time range.
            interval (datetime.timedelta): The interval to iterate over.
            combos (list[tuple[DataType, str]]): The data types and symbols to iterate over.

        Yields:
            tuple: A tuple of (datetime.datetime, datetime.datetime, data_df).
        """

        iterators = [
            self._iterate_time_range_data_low_mem(
                from_datetime=from_datetime,
                to_datetime=to_datetime,
                interval=interval,
                data_type=data_type,
                symbol=symbol,
                temp_location=temp_location,
            )
            for data_type, symbol in combos
        ]

        for range_data in zip(*iterators):
            start, end, _ = range_data[0]
            dfs = tuple(data_df for _, _, data_df in range_data)
            yield start, end, dfs

    def generate_candles(
        self,
        symbol: str,
        from_datetime: Union[datetime.datetime, str],
        to_datetime: Union[datetime.datetime, str],
        candle_interval: Union[datetime.timedelta, str],
        temp_location: Path = Path("./temp"),
    ) -> pd.DataFrame:
        """Generates OHLCV candles from the exchange for a given symbol and date range.

        This is meant to generate highly aggregated candles (e.g. 1 hour). It will not
        be efficient for smaller time intervals.

        Args:
            symbol (str): The symbol to generate candles for.
            from_datetime (Union[datetime.datetime, str]): The time to start generating
                candles from.
            to_datetime (Union[datetime.datetime, str]): The time to end generating
                candles to.
            candle_interval (Union[datetime.timedelta, str]): The interval to generate
                candles for.
            location (Path, optional): Folder to save files to. Defaults to
                Path("./temp").

        Returns:
            pd.DataFrame: a dataframe of OHLCV candles, with columns timestamp, open,
                high, low, close, volume.
        """

        from_datetime = parse_datetime(from_datetime)
        to_datetime = parse_datetime(to_datetime)
        candle_interval = parse_timedelta(candle_interval)

        self._assert_symbol_data_type(symbol, DataType.trades.value)
        self._assert_symbol_date_range(symbol, from_datetime.date(), to_datetime.date())

        trades_interator = self._iterate_time_range_data(
            from_datetime,
            to_datetime,
            candle_interval,
            DataType.trades,
            symbol,
            temp_location,
        )

        candles = [
            candle
            for start, end, trades_df in trades_interator
            for candle in generate_candle_from_trades(trades_df, start, end)
        ]

        candles_df = pd.DataFrame.from_records([dict(candle) for candle in candles])
        return candles_df

    def generate_option_chain_snapshots(
        self,
        from_datetime: Union[datetime.datetime, str],
        to_datetime: Union[datetime.datetime, str],
        snapshot_interval: Union[datetime.timedelta, str],
        underlyings: Optional[Iterable[str]] = None,
        temp_location: Path = Path("./temp"),
        previous_snapshot: Optional[List[InstrumentStatus]] = None,
    ) -> pd.DataFrame:
        """Generates option chain snapshots from the exchange for a given date range.

        This is meant to generate highly aggregated snapshots (e.g. 1 day). It will not
        be efficient for smaller time intervals.

        Args:
            from_datetime (Union[datetime.date, str]): The date to start generating
                snapshots from.
            to_datetime (Union[datetime.date, str]): The date to end generating
                snapshots to.
            snapshot_interval (Union[datetime.timedelta, str]): The interval to generate
                snapshots for.
            underlyings (Optional[Iterable[str]]): The underlyings to generate snapshots
                for. Defaults to None for all available symbols.
            location (Path, optional): Folder to save files to. Defaults to
                Path("./temp").
        """

        from_datetime = parse_datetime(from_datetime)
        to_datetime = parse_datetime(to_datetime)
        snapshot_interval = parse_timedelta(snapshot_interval)

        previous_snapshot = previous_snapshot or []

        self._assert_symbol_data_type(
            GroupedSymbol.OPTIONS.value, DataType.options_chain.value
        )
        self._assert_symbol_date_range(
            GroupedSymbol.OPTIONS.value, from_datetime.date(), to_datetime.date()
        )

        options_chain_iterator = self._iterate_time_range_data_low_mem(
            from_datetime,
            to_datetime,
            snapshot_interval,
            DataType.options_chain,
            GroupedSymbol.OPTIONS.value,
            temp_location,
        )
        snapshots: List[List[InstrumentStatus]] = []
        for _, end, options_chain_df in options_chain_iterator:
            print(f"Generating snapshots for {end} {len(options_chain_df)}")
            current_snapshot = generate_options_chain_snapshot(
                options_chain_df,
                end + ONE_MILLISECOND,
                previous_snapshot,
                underlyings,
                self.exchange,
            )
            snapshots.append(current_snapshot)
            previous_snapshot = current_snapshot

        snapshots_df = pd.DataFrame.from_records(
            [
                dict(instrument_status)
                for snapshot in snapshots
                for instrument_status in snapshot
            ]
        )

        return snapshots_df

    def generate_derived_option_chain_snapshots(
        self,
        from_datetime: Union[datetime.date, str],
        to_datetime: Union[datetime.date, str],
        snapshot_interval: Union[datetime.timedelta, str],
        underlyings: Optional[Iterable[str]] = None,
        temp_location: Path = Path("./temp"),
        previous_snapshot: Optional[List[InstrumentStatus]] = None,
    ) -> pd.DataFrame:
        """Generates option chain snapshots from the exchange for a given date range.

        This is meant to generate highly aggregated snapshots (e.g. 1 day). It will not
        be efficient for smaller time intervals.

        Args:
            from_datetime (Union[datetime.date, str]): The date to start generating
                snapshots from.
            to_datetime (Union[datetime.date, str]): The date to end generating
                snapshots to.
            snapshot_interval (Union[datetime.timedelta, str]): The interval to generate
                snapshots for.
            underlyings (Optional[Iterable[str]]): The underlyings to generate snapshots
                for. Defaults to None for all available symbols.
            location (Path, optional): Folder to save files to. Defaults to
                Path("./temp").
        """

        from_datetime = parse_datetime(from_datetime)
        to_datetime = parse_datetime(to_datetime)
        snapshot_interval = parse_timedelta(snapshot_interval)

        previous_snapshot = previous_snapshot or []

        self._assert_symbol_data_type(
            GroupedSymbol.OPTIONS.value, DataType.quotes.value
        )
        self._assert_symbol_date_range(
            GroupedSymbol.OPTIONS.value, from_datetime.date(), to_datetime.date()
        )

        available_underlyings = set(
            [s.split("-")[1] for s in self.exchange_symbols if s.startswith("C-")]
        )
        underlyings = underlyings or list(available_underlyings)
        assert available_underlyings.issuperset(underlyings)

        underlying_trades = [
            (DataType.trades, underlying + "USDT") for underlying in underlyings
        ]

        combo_iterator = self._iterate_time_range_data_combos(
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            interval=snapshot_interval,
            combos=[(DataType.quotes, GroupedSymbol.OPTIONS.value)] + underlying_trades,
            temp_location=temp_location,
        )

        underlying_prices = {}
        snapshots: List[List[InstrumentStatus]] = []
        for _, end, dfs in combo_iterator:
            quotes_df, *underlying_trades_dfs = dfs
            underlying_prices = {
                underlying: underlying_df["price"].iloc[-1]
                if (underlying_df is not None) and (len(underlying_df["price"]) > 0)
                else underlying_prices.get(underlying)
                for underlying, underlying_df in zip(underlyings, underlying_trades_dfs)
            }
            print(f"Generating snapshots for {end} {len(quotes_df)}")
            current_snapshot = generate_derived_options_chain_snapshot(
                quotes=quotes_df,
                snapshot_time=end + ONE_MILLISECOND,
                previous_snapshot=previous_snapshot,
                underlying_prices=underlying_prices,
                exchange=self.exchange,
            )
            snapshots.append(current_snapshot)
            previous_snapshot = current_snapshot

        snapshots_df = pd.DataFrame.from_records(
            [
                dict(instrument_status)
                for snapshot in snapshots
                for instrument_status in snapshot
            ]
        )

        return snapshots_df

import gzip
import hashlib
import json
import logging
import os
import re
import shutil
from collections import defaultdict
from functools import partial
from multiprocessing import Pool
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import sleep
from typing import Union, Optional, TypeVar, Any
from urllib.parse import quote
from zipfile import ZipFile, BadZipFile

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from dateutil.tz import tzutc
from powerbot_client import Signal, Trade, InternalTrade, OwnOrder, ContractItem, ContractApi, ApiClient, ApiException
from pydantic import BaseModel, Field, validate_arguments, root_validator, validator
from sqlalchemy import create_engine
from sqlalchemy.exc import NoSuchModuleError, InterfaceError, ProgrammingError, OperationalError, TimeoutError
from sqlalchemy.orm import Session
from tqdm import tqdm

from powerbot_backtesting.exceptions import SQLExporterError, ChecksumError, NotInCacheError
from powerbot_backtesting.models import HistoryApiClient
from powerbot_backtesting.utils import _cache_data, _get_file_cachepath, _check_contracts, _historic_data_transformation, \
    _historic_contract_transformation, _process_orderbook, _get_private_data, _process_multiple, _splitter, _multiprocess_data_transformation
from powerbot_backtesting.utils import init_client
from powerbot_backtesting.utils.constants import DATE_YMD_TIME_HMS, EXCHANGES, EIC_CODES, DATE_YM, DATE_YMD_TIME_HM_ALT, PRODUCTS, DATE_MD, \
    DATE_YMD, SYSTEMS, DATE_YMD_TIME_HM

# Implement custom type for validation
# noinspection PyTypeHints
pandas_DataFrame = TypeVar('pandas.core.frame.DataFrame')
# noinspection PyTypeHints
val_ApiClient = TypeVar('powerbot_client.api_client.ApiClient')
# noinspection PyTypeHints
val_HistoryApiClient = TypeVar('powerbot_backtesting.models.history_api_models.HistoryApiClient')


class BaseExporter(BaseModel):
    """
    Base class to all of PowerBot's exporter classes.
    """

    def get_contract_ids(self,
                         time_from: datetime = None,
                         time_till: datetime = None,
                         contract_ids: list[str] = None,
                         contract_time: str = "all",
                         products: list[str] = None,
                         allow_udc: bool = False,
                         delivery_areas: list[str] = None,
                         return_contract_objects: bool = False) -> Union[dict[tuple[datetime, datetime], list[str]], list[ContractItem]]:
        """
        Loads all contract IDs for specified timeframe. Alternatively, a list of contract IDs can be passed instead of a timeframe, returning a
        dictionary of contract IDs compatible with all other functions of the Backtesting package. If return_contract_objects is True, a list
        of contract items will be returned.

        If a historic API client is used all parameters except time_from, time_till, contract_time, products and
        allow_udc will be ignored.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_ids (list[str]): Optionally, a list of specific contract IDs can be passed to return contract objects
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): Optional list of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all
            delivery_areas (list): List of EIC-codes
            return_contract_objects (bool): If True, returns complete Contract object

        Returns:
            dict{key: (list[str])}: Dictionary of Contract IDs
            OR: list[ContractItem]: Contract Object
        """
        # Check date input
        timeframes = {"all": 15, "hourly": 60, "half-hourly": 30, "quarter-hourly": 15}

        if not contract_ids:
            if not time_from or not time_till:
                raise TypeError("If no specific contract IDs are given, a time period has to be defined.")

            if not isinstance(time_from, datetime):
                raise ValueError("Please use datetime format (yyyy-mm-dd hh:mm:ss)")

            # if minutes are entered wrong, raise exception
            for t in [i for i in [time_from, time_till] if i]:
                if t.minute not in [0, 15, 30, 45]:
                    raise ValueError("Time period has to start and end with one of these values: 0, 15, 30, 45")

        # Loading from historic data collection
        if isinstance(self.client, HistoryApiClient):
            if not time_from:
                raise AttributeError("Missing input parameter: time_from")
            return self.__get_historic_contract_ids(
                time_from=time_from,
                time_till=time_till,
                contract_time=contract_time,
                products=products if products else [],
                allow_udc=allow_udc,
                return_contract_objects=return_contract_objects)

        contract_api = ContractApi(self.client)
        products = [] if not products else products
        delivery_areas = [] if not delivery_areas else delivery_areas

        # Load Contract IDs
        contracts = defaultdict(list)

        # Loading by time_from & time_till
        if not contract_ids:
            while time_from != time_till:
                if contract_time != "all":
                    new_contracts = contract_api.find_contracts(delivery_start=time_from,
                                                                delivery_end=time_from + timedelta(
                                                                    minutes=timeframes[contract_time]))
                else:
                    new_contracts = contract_api.find_contracts(delivery_start=time_from)

                # Check validity and add to contracts
                [contracts[(c.delivery_start, c.delivery_end)].append(c) for c in new_contracts
                 if _check_contracts(c, delivery_areas, products, allow_udc)]

                time_from += timedelta(minutes=timeframes[contract_time])

        # Loading by specific contract IDs
        else:
            new_contracts = contract_api.find_contracts(contract_id=contract_ids)

            for c in new_contracts:
                # Check validity and add to contracts
                if _check_contracts(c, delivery_areas, products, allow_udc):
                    # Add to contracts
                    contracts[(c.delivery_start, c.delivery_end)].append(c)

        # Cleanup
        contracts = {k: v for k, v in contracts.items() if v}
        contract_ids = {k: [c.contract_id for c in v] for k, v in contracts.items() if v}

        if not contracts:
            print("There was no contract data for your request!")

        # Return Contract Objects
        if return_contract_objects:
            return [i for v in contracts.values() for i in v]

        return contract_ids

    def __get_historic_contract_ids(self,
                                    time_from: datetime,
                                    time_till: datetime,
                                    contract_time: str,
                                    products: list[str],
                                    allow_udc: bool,
                                    return_contract_objects: bool = False) -> Union[dict[tuple[datetime, datetime], list[str]], list[dict]]:
        """
        Function mimics get_contract_ids but loads contract IDs from a cached index file instead of the API. This is necessary when trying to load
        data that is older than the data retention policy for production instances.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): List of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all
            return_contract_objects: if True will return contract objects instead

        Returns:
            dict{key: (list[str])}: Dictionary of Contract IDs or List of Dictionaries
            OR: list[ContractItem]: Contract Object
        """
        # Setup
        timeframes = {"all": 15, "hourly": 60, "half-hourly": 30, "quarter-hourly": 15}
        ct = timeframes[contract_time]
        products = PRODUCTS[contract_time] if not products else products
        contracts = defaultdict(list) if not return_contract_objects else []
        time_range = []

        # Split time up if range covers multiple days
        while time_from.date() < time_till.date():
            time_range.append((time_from, time_from.replace(hour=0, minute=0, second=0) + timedelta(days=1)))
            time_from = time_from.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        else:
            if not time_from == time_till:
                time_range.append((time_from, time_till))

        for tr in time_range:
            # Extract date information
            year_month = tr[0].strftime(DATE_YM)
            day_month = tr[0].strftime(DATE_MD)

            # Construct path to index file
            file_path = Path(f"./__pb_cache__/prod/{self.client.exchange}_{self.client.delivery_area}/{year_month}/{day_month}/raw")  # noqa: W605
            if not file_path.exists():
                raise NotInCacheError("The requested data is currently not cached")
            index = next((i for i in file_path.iterdir() if i.is_file() and "contract" in i.name))

            if not index:
                raise NotInCacheError("Cannot find correct index file in local cache")
            index = pd.read_json(gzip.open(index))

            # Transform
            index['delivery_start'] = pd.to_datetime(index['delivery_start'])
            index['delivery_end'] = pd.to_datetime(index['delivery_end'])
            index = index.astype({"contract_id": "str", "delivery_areas": "str"})

            # Construct list of contract times
            contract_times = [tr[0]]
            [contract_times.append(contract_times[-1] + timedelta(minutes=ct)) for _ in
             range(1, ((tr[1] - tr[0]) / (ct * 60)).seconds)]
            contract_times = [i.replace(tzinfo=tzutc()) for i in contract_times]

            # Filter dataframe down
            index = index.loc[(index._product.isin(PRODUCTS[contract_time])) & (index._product.isin(products)) & (
                index.delivery_areas.str.contains(self.client.delivery_area))]
            index = index.loc[index.delivery_start.isin(contract_times)]

            # Block product filter
            if not contract_time == "all" or not allow_udc:
                if self.client.exchange not in SYSTEMS["NordPool"]:
                    index = index.loc[index.undrlng_contracts.isna()]
                else:
                    index = index.loc[index.productType != "CUSTOM_BLOCK"]

            if not return_contract_objects:
                [contracts[(v.delivery_start.to_pydatetime(), v.delivery_end.to_pydatetime())].append(v.contract_id) for
                 k, v in index.iterrows()]
            else:
                contracts += (index.to_dict(orient="records"))

        return dict(contracts) if not return_contract_objects else contracts

    def get_public_trades(self,
                          contract_ids: dict[tuple[datetime, datetime], list[str]],
                          contract_time: str,
                          delivery_area: str = None,
                          iteration_delay: float = 0,
                          serialize_data: bool = True,
                          add_vwap: bool = False,
                          use_cached_data: bool = True,
                          caching: bool = True,
                          gzip_files: bool = True,
                          as_csv: bool = False) -> dict[tuple[datetime, datetime], pd.DataFrame]:
        """
        Load trade data for given contract IDs. If add_vwap is True, VWAP will be calculated for each trade, incorporating all previous trades.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            contract_time (str): all, hourly, half-hourly or quarter-hourly
            delivery_area (str): EIC Area Code for Delivery Area (not needed when loading from historic cache)
            iteration_delay (float): Optional delay between iterations to prevent hitting API rate limits
            serialize_data (bool): If False, request is received without serialization. Recommended for large data collections
            add_vwap (bool): If True, additional VWAP parameters will be added to each dataframe
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        # Setup
        trades = {}
        missing_contracts = {}
        delivery_area = self.client.delivery_area if isinstance(self.client, HistoryApiClient) else delivery_area

        # Load Data
        # Load from Cache
        if use_cached_data:
            # Find __cache__ directory
            for key, value in tqdm(contract_ids.items(), desc="Loading Cached Trades", unit="time periods", leave=False):
                filepath = _get_file_cachepath(self.client, key, delivery_area)
                tmp_df = None

                for i in [".json.gz", ".json"]:
                    if Path(f"./__pb_cache__/{filepath}_trades{i}").exists():
                        tmp_df = pd.read_json(f"__pb_cache__/{filepath}_trades{i}", dtype=False)

                if isinstance(tmp_df, pd.DataFrame):
                    tmp_df['api_timestamp'] = pd.to_datetime(tmp_df['api_timestamp'])
                    tmp_df['exec_time'] = pd.to_datetime(tmp_df['exec_time'])
                    tmp_df = tmp_df.astype({"price": "float64", "trade_id": "str", "contract_id": "str"})
                    for i in ["price", "quantity"]:
                        tmp_df[i] = round(tmp_df[i], 2)

                    # Filter out any contract IDs that are not in value
                    trades[key] = tmp_df.loc[tmp_df.contract_id.isin(value)]

                else:
                    # Save Missing Contract IDs
                    missing_contracts[key] = value

        # Historic data -> cache only
        if isinstance(self.client, ApiClient):
            contract_api = ContractApi(self.client)
            contract_ids = missing_contracts if use_cached_data else contract_ids

            for key, value in contract_ids.items():
                public_trade_history = []
                for nr, item in enumerate(value):
                    from_public_trade = 0
                    more_public_trades = True
                    while more_public_trades:
                        if serialize_data:
                            public_trades = contract_api.get_public_trades(
                                contract_id=item,
                                delivery_area=delivery_area,
                                offset=from_public_trade,
                                limit=500
                            )
                            public_trade_history.extend([trade.to_dict() for trade in public_trades])

                        else:
                            endpoint = f"{self.client.configuration.host}/contract/{item}/{delivery_area}/" \
                                       f"publictrades?offset={from_public_trade}&limit=500"
                            headers = {"accept": "application/json",
                                       "api_key_security": self.client.configuration.api_key['api_key_security']}
                            public_trades = json.loads(requests.get(endpoint, headers=headers).text)
                            public_trade_history += public_trades

                        if len(public_trades) < 500:
                            more_public_trades = False
                        from_public_trade += len(public_trades)

                if len(public_trade_history) == 0:
                    continue

                df_trades = pd.DataFrame(public_trade_history).sort_values(by=['exec_time'], ascending=True)
                df_trades = df_trades.reset_index(drop=True)
                df_trades['api_timestamp'] = pd.to_datetime(df_trades['api_timestamp'], utc=True)
                df_trades['exec_time'] = pd.to_datetime(df_trades['exec_time'], utc=True)

                trades[key] = df_trades
                sleep(iteration_delay)

        if add_vwap:
            for k, v in trades.items():
                trades[k] = self.calc_trade_vwap(trade_data={k: v}, contract_time=contract_time,
                                                 delivery_area=delivery_area, index="all")

        if caching:
            _cache_data("trades", trades, delivery_area, api_client=self.client, gzip_files=gzip_files, as_csv=as_csv)
        return trades

    def get_contract_history(self,
                             contract_ids: dict[tuple[datetime, datetime], list[str]],
                             delivery_area: str = None,
                             iteration_delay: float = 0,
                             serialize_data: bool = True,
                             use_cached_data: bool = True,
                             caching: bool = True,
                             gzip_files: bool = True,
                             as_csv: bool = False) -> dict[tuple[datetime, datetime], pd.DataFrame]:
        """
        Load contract history for given contract IDs.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            delivery_area (str): EIC Area Code for Delivery Area (not needed when loading from historic cache)
            iteration_delay (float): Optional delay between iterations to prevent hitting API rate limits
            serialize_data (bool): If False, request is received without serialization. Recommended for large data collections
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        # Setup
        orders = {}
        missing_contracts = {}
        delivery_area = self.client.delivery_area if isinstance(self.client, HistoryApiClient) else delivery_area

        if use_cached_data:
            # Find __cache__ directory
            for key, value in contract_ids.items():
                filepath = _get_file_cachepath(self.client, key, delivery_area)
                tmp_df = None

                for i in [".json.gz", ".json"]:
                    if Path(f"./__pb_cache__/{filepath}_ordhist{i}").exists():
                        tmp_df = pd.read_json(f"./__pb_cache__/{filepath}_ordhist{i}", dtype=False,
                                              convert_dates=False)

                if isinstance(tmp_df, pd.DataFrame):
                    tmp_df['as_of'] = pd.to_datetime(tmp_df['as_of'])

                    cols = {"internal_trades": "object", "contract_id": "str", "auction_price": "float64"}
                    cols = {k: v for k, v in cols.items() if k in tmp_df.columns}
                    tmp_df = tmp_df.astype(cols, errors='ignore')
                    for i in ["best_bid_price", "best_bid_quantity", "best_ask_price", "best_ask_quantity",
                              "last_price",
                              "last_quantity", "total_quantity", "high", "low", "vwap"]:
                        try:
                            tmp_df[i] = round(tmp_df[i], 2)
                        except (TypeError, KeyError):
                            pass

                    if "orders" in tmp_df.columns:
                        order_list = tmp_df.orders.tolist()
                        for order_type in ["bid", "ask"]:
                            for i in order_list:
                                if order_type in i and i[order_type]:
                                    for x in i[order_type]:
                                        for param in ["quantity", "price"]:
                                            x[param] = round(x[param], 2)
                                        try:
                                            x["order_entry_time"] = datetime.strptime(x["order_entry_time"],
                                                                                      "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                                                tzinfo=tzutc())
                                        except ValueError:
                                            x["order_entry_time"] = datetime.strptime(x["order_entry_time"],
                                                                                      "%Y-%m-%dT%H:%M:%SZ").replace(
                                                microsecond=0, tzinfo=tzutc())
                        tmp_df["orders"] = order_list

                    # Filter out any contract IDs that are not in value
                    orders[key] = tmp_df.loc[tmp_df.contract_id.isin(value)]

                else:
                    # Save Missing Contract IDs
                    missing_contracts[key] = value

        # Historic data -> cache only
        if isinstance(self.client, ApiClient):
            contract_api = ContractApi(self.client)
            contract_ids = missing_contracts if use_cached_data else contract_ids

            for key, value in tqdm(contract_ids.items(), desc="Downloading Order History", unit="time periods",
                                   leave=False):
                public_contract_history = []
                for nr, item in enumerate(value):
                    more_revisions = True
                    from_revision = 0

                    while more_revisions:
                        if serialize_data:
                            contract_history = contract_api.get_contract_history(
                                contract_id=item,
                                delivery_area=delivery_area,
                                with_orders=True,
                                with_owntrades=False,
                                offset=from_revision,
                                limit=150
                            )
                            public_contract_history.extend([trade.to_dict() for trade in contract_history])

                        else:
                            endpoint = f"{self.client.configuration.host}/contract/{item}/{delivery_area}/" \
                                       f"history?offset={from_revision}&limit=150&with_owntrades=false&with_signals=false&with_orders=true"
                            headers = {"accept": "application/json",
                                       "api_key_security": self.client.configuration.api_key['api_key_security']}
                            contract_history = json.loads(requests.get(endpoint, headers=headers).text)
                            public_contract_history += contract_history

                        if len(contract_history) < 150:
                            more_revisions = False
                        from_revision += len(contract_history)

                if len(public_contract_history) == 0:
                    continue

                df_history = pd.DataFrame(public_contract_history).sort_values(by=['as_of'], ascending=True)
                df_history = df_history.reset_index(drop=True)
                df_history['as_of'] = pd.to_datetime(df_history['as_of'], utc=True)
                df_history.drop(columns=["auction_price", "internal_trades"], inplace=True, errors="ignore")

                orders[key] = df_history
                sleep(iteration_delay)

        if caching:
            _cache_data("ordhist", orders, delivery_area, api_client=self.client, gzip_files=gzip_files, as_csv=as_csv)
        return orders

    @validate_arguments
    def get_ohlc_data(self,
                      trade_data: dict[tuple[datetime, datetime], pandas_DataFrame],
                      timesteps: int,
                      time_unit: str,
                      delivery_area: str = None,
                      use_cached_data: bool = False,
                      caching: bool = True,
                      gzip_files: bool = True) -> dict[tuple[datetime, datetime], pd.DataFrame]:
        """
        Converts trade data into Open-High-Low-Close format in the specified timesteps.

        Args:
            trade_data (dict{key: DataFrame}): Dictionary of Dataframes containing Contract Trade Data
            timesteps (int): Timesteps to group Trades by
            time_unit (str): Time units for timesteps (either hours, minutes or seconds)
            delivery_area (str): Area Code for Delivery Area (not needed when loading from historic cache)
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """

        if not hasattr(self, 'delivery_area') and not delivery_area:
            raise ValueError("Delivery area has to be given")
        delivery_area = delivery_area if delivery_area else self.delivery_area
        client = self.client if hasattr(self, "client") else None

        # Setup Parameters
        all_ohlc_data = {}
        host = client.configuration.host if isinstance(client, ApiClient) else None
        environment = host.split("/")[2].split(".")[0] if host else "prod"
        exchange = host.split("/")[4] if host else client.exchange if isinstance(client, HistoryApiClient) else \
            list(trade_data.values())[0].exchange[0]
        delivery_area = client.delivery_area if isinstance(client, HistoryApiClient) else delivery_area

        for key, value in tqdm(trade_data.items(), desc="Processing Trades", unit="time periods", leave=False):
            # Check If Data Already Cached
            year_month = key[0].strftime(DATE_YM)
            day_month = key[1].strftime(DATE_MD)
            file_name = (f"{key[0].strftime(DATE_YMD_TIME_HM).replace(':', '-')} - "
                         f"{key[1].strftime(DATE_YMD_TIME_HM).replace(':', '-')}")
            data_ohlc = None

            if use_cached_data:
                for i in [".json.gz", ".json"]:
                    if Path(f'./__pb_cache__/{environment}/{exchange}_{delivery_area}/{year_month}/{day_month}'
                            f'/processed/{file_name}_ohlc_{timesteps}{time_unit[0]}{i}').exists():
                        data_ohlc = pd.read_json(f'./__pb_cache__/{environment}/{exchange}_{delivery_area}/'
                                                 f'{year_month}/{day_month}/processed/'
                                                 f'{file_name}_ohlc_{timesteps}{time_unit[0]}{i}',
                                                 dtype=False)

            if isinstance(data_ohlc, pd.DataFrame):
                data_ohlc.rename(columns={0: 'exec_time'}, inplace=True)
                all_ohlc_data[key] = data_ohlc

            else:
                data_ohlc = value.set_index('exec_time')
                data_ohlc = data_ohlc['price'].resample(f'{timesteps}{time_unit[0]}').ohlc() if time_unit != "minutes" \
                    else data_ohlc['price'].resample(f'{timesteps}{time_unit[:3]}').ohlc()
                data_ohlc = data_ohlc.dropna(how='all')

                # Append to complete OHLC collection
                all_ohlc_data[key] = data_ohlc

        # Cache Data as JSON
        if caching:
            _cache_data("ohlc", all_ohlc_data, delivery_area, exchange=exchange, api_client=client,
                        gzip_files=gzip_files, timesteps=timesteps, time_unit=time_unit[0], as_csv=False)

        return all_ohlc_data

    @validate_arguments
    def get_orderbooks(self,
                       contract_hist_data: dict[tuple[datetime, datetime], pandas_DataFrame],
                       delivery_area: str = None,
                       timesteps: int = 15,
                       time_unit: str = "minutes",
                       shortest_interval: bool = False,
                       use_cached_data: bool = False,
                       caching: bool = True,
                       as_json: bool = False,
                       concurrent: bool = True) -> pd.DataFrame:

        """

        Converts contract history data into order books in the specified timesteps. If no API client is passed,
        the function will automatically assume that the data is production data.

        Please be aware that optimally only data from one exchange at a time should be used (e.g. only EPEX).

        To generate specific order books for a position closing algorithm, the timestamp can
        be used.

        Args:
            shortest_interval:
            contract_hist_data (dict{key: DataFrame}): Dictionary of Dataframes containing Contract History Data
            delivery_area (str): Area Code for Delivery Area (not needed when loading from historic cache)
            timesteps (int): Timesteps to group order books by
            time_unit (str): Time units for timesteps (either hours, minutes or seconds)
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if single order books should be cached as JSON
            as_json (bool): True if complete order book should be cached as JSON
            concurrent (bool): True if processing should be multithreaded -> possible performance gain on big datasets
                and a multi-core CPU

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """

        if not hasattr(self, 'delivery_area') and not delivery_area:
            raise ValueError("Delivery area has to be given")
        delivery_area = delivery_area if delivery_area else self.delivery_area
        client = self.client if hasattr(self, "client") else None

        # Initial check
        if not contract_hist_data:
            raise ValueError("Warning: Provided order data is empty")
        if concurrent and len(contract_hist_data) < 2:
            print(
                "Warning: using multithreading on a small dataset might increase processing time. Minimum recommended "
                "size: > 1 contract periods\n "
                "Defaulting to normal processing.")

        # Setup
        all_order_books = []
        host = client.configuration.host if isinstance(client, ApiClient) else None
        environment = host.split("/")[2].split(".")[0] if host else "prod"
        exchange = host.split("/")[4] if host else client.exchange if isinstance(client, HistoryApiClient) else \
            list(contract_hist_data.values())[0].exchange[0]
        delivery_area = client.delivery_area if isinstance(client, HistoryApiClient) else delivery_area

        # Parameters
        contract_times = sorted([i for i in [*contract_hist_data]])
        first_contract = contract_times[0][0]
        last_contract = contract_times[-1][1]
        year_month = first_contract.strftime(DATE_YM)
        day_month = first_contract.strftime(DATE_MD)
        first_contract = first_contract.strftime(DATE_YMD_TIME_HM_ALT)
        last_contract = last_contract.strftime(DATE_YMD_TIME_HM_ALT) if len(contract_times) > 1 else None

        new_dir = f"./__pb_cache__/{environment}/{exchange}_{delivery_area}/{year_month}/{day_month}/processed"

        if concurrent and len(contract_hist_data) > 1:
            # Processing Concurrently with Multiprocessing Pool
            partial_func = partial(_process_multiple,
                                   new_dir=new_dir,
                                   timesteps=timesteps,
                                   time_unit=time_unit,
                                   use_cached_data=use_cached_data,
                                   shortest_interval=shortest_interval)

            process_count = min(os.cpu_count() - 2, len(contract_hist_data))
            with Pool(process_count) as p:
                all_order_books = p.map(partial_func,
                                        [chunk for chunk in _splitter(contract_hist_data, len(contract_hist_data))])

        else:
            # Processing Synchronously
            for key in tqdm(contract_hist_data):
                all_order_books.append(
                    _process_orderbook(key, contract_hist_data[key], str(new_dir), timesteps, time_unit,
                                       use_cached_data=use_cached_data, shortest_interval=shortest_interval))

        all_order_books_df = pd.concat(all_order_books)

        # add best-bid / best-ask and respective quantities if we calculate freshly
        if ("best_bid_qty" not in all_order_books_df.columns) or ("best_ask_qty" not in all_order_books_df.columns):
            all_order_books_df = all_order_books_df.rename(columns={"type": "side"})
            all_order_books_df["price"] = all_order_books_df["price"].astype(float)
            all_order_books_df_asks = all_order_books_df[all_order_books_df["side"] == "ask"].reset_index()
            all_order_books_df_bids = all_order_books_df[all_order_books_df["side"] == "bid"].reset_index()
            min_sell_price = all_order_books_df_asks.groupby(["delivery_start", "delivery_end", "timestep"])["price"].min().reset_index()
            max_buy_price = all_order_books_df_bids.groupby(["delivery_start", "delivery_end", "timestep"])["price"].max().reset_index()
            idx_asks = all_order_books_df_asks.groupby(["delivery_start", "delivery_end", "timestep"])["price"].idxmin()
            idx_bids = all_order_books_df_bids.groupby(["delivery_start", "delivery_end", "timestep"])["price"].idxmax()

            min_sell_quant = all_order_books_df_asks.loc[idx_asks, ["delivery_start", "delivery_end", "timestep", "quantity"]]
            min_sell_quant = min_sell_quant.rename(columns={"quantity": "best_ask_qty"})
            sell_agg = min_sell_quant.merge(min_sell_price)
            sell_agg = sell_agg.rename(columns={"price": "best_ask"})

            max_buy_quant = all_order_books_df_bids.loc[idx_bids, ["delivery_start", "delivery_end", "timestep", "quantity"]]
            max_buy_quant = max_buy_quant.rename(columns={"quantity": "best_bid_qty"})
            buy_agg = max_buy_quant.merge(max_buy_price)
            buy_agg = buy_agg.rename(columns={"price": "best_bid"})
            data_agg = sell_agg.merge(buy_agg, on=["delivery_start", "delivery_end", "timestep"], how="outer")

            all_order_books_df = all_order_books_df.merge(data_agg, left_index=True, right_on=["delivery_start", "delivery_end", "timestep"])
            all_order_books_df.set_index(["delivery_start", "delivery_end", "timestep"], inplace=True)

            all_order_books_df.loc[all_order_books_df["side"] == "bid", "side"] = "BUY"
            all_order_books_df.loc[all_order_books_df["side"] == "ask", "side"] = "SELL"

        # Cache Data as pickle
        if caching:
            _cache_data("orderbook", all_order_books_df, delivery_area, exchange=exchange, api_client=client,
                        gzip_files=False, timesteps=timesteps,
                        time_unit=time_unit[0], shortest_interval=shortest_interval, as_json=False,
                        as_pickle=True)

        # Saving Complete Orderbook as JSON
        if as_json:
            new_dir.mkdir(parents=True, exist_ok=True)

            filename = f'orderbook_{first_contract} - {last_contract}_{timesteps}{time_unit[0]}.json.gz' \
                if last_contract else f'orderbook_{first_contract}_{timesteps}{time_unit[0]}.json.gz'
            with gzip.open(new_dir.joinpath(filename), 'wt', encoding="ascii") as f:
                json.dump({str(key): {str(k): v.to_json() for (k, v) in value.items()} for (key, value) in
                           all_order_books.items()},
                          f, default=str)

        return all_order_books_df

    @staticmethod
    @validate_arguments
    def get_orders(contract_hist_data: dict[tuple[datetime, datetime], pandas_DataFrame],
                   append_all: bool = False) -> dict[tuple[datetime, datetime], pandas_DataFrame]:
        """
        Extracts all order data from contract history as is, without performing any quality control.
        If necessary, orders for all contracts can be appended to a single dataframe.

        Args:
            contract_hist_data (dict): Dictionary of Dataframes containing Contract History Data
            append_all (bool): True if one dataframe containing all orders should be returned

        Returns:
            dict{key: pd.DataFrame}: Dictionary of DataFrames
        """
        order_list = {}

        for key, value in tqdm(contract_hist_data.items(), desc="Extracting Orders", unit="time periods", leave=False):
            value.replace(np.nan, 0, inplace=True)
            bids_asks = []
            if "orders" in value:
                orders_all = value["orders"].to_list()
                for nr, orders in enumerate(orders_all):
                    for k, v in orders.items():
                        if v and k in ["bid", "ask"]:
                            for x in v:
                                x["type"] = k
                                x["order_id"] = str(x["order_id"])
                                x["best_bid"] = round(value.loc[nr, "best_bid_price"], 2)
                                x["best_bid_qty"] = round(value.loc[nr, "best_bid_quantity"], 2)
                                x["best_ask"] = round(value.loc[nr, "best_ask_price"], 2)
                                x["best_ask_qty"] = round(value.loc[nr, "best_ask_quantity"], 2)
                                try:
                                    x["vwap"] = round(value.loc[nr, "vwap"], 2)

                                except:  # noqa: E722
                                    pass
                                x["as_of"] = value.loc[nr]["as_of"].tz_convert(timezone.utc) if value.loc[nr][
                                    "as_of"].tzinfo else \
                                    value.loc[nr]["as_of"].tz_localize(timezone.utc)
                                bids_asks.append(x)
            else:
                value = [v.to_dict() for r, v in value.iterrows()]
                for nr, coll in enumerate(value):
                    for k, v in coll.items():
                        if v and k in ["bids", "asks"]:
                            for x in v:
                                x["type"] = k[:-1]
                                x["order_id"] = str(x["order_id"])
                                x["best_bid"] = round(value[nr].get("best_bid", 0), 2)
                                x["best_bid_qty"] = round(value[nr].get("best_bid_qty", 0), 2)
                                x["best_ask"] = round(value[nr].get("best_ask", 0), 2)
                                x["best_ask_qty"] = round(value[nr].get("best_ask_qty", 0), 2)
                                x["vwap"] = round(value[nr].get("vwap", 0), 2)
                                x["as_of"] = value[nr]["as_of"].tz_convert(timezone.utc) if value[nr][
                                    "as_of"].tzinfo else \
                                    value[nr]["as_of"].tz_localize(timezone.utc)
                                bids_asks.append(x)

            order_list[key] = bids_asks

        orders = {k: pd.DataFrame(v) for k, v in order_list.items()}

        if append_all:
            all_orders = []

            for k, v in orders.items():
                v["time_range_start"] = k[0]
                v["time_range_end"] = k[1]
                all_orders.append(v)
            return pd.concat(all_orders)

        return orders

    @staticmethod
    @validate_arguments
    def vwap_by_depth(objects: dict[tuple[datetime, datetime], pandas_DataFrame],
                      desired_depth: float,
                      min_depth: float = None) -> dict[str, float]:
        """
        This method can be used to calculate the weighted average price for a dictionary of dataframes (e.g. orders, trades) at a desired depth.
        The output is a singular value for each dataframe. This function does not load any data, therefore the already existing data object has to
        be passed as an argument.

        Args:
            objects (dict[str, DataFrame): A dictionary of dataframes, each of which needs to have a 'quantity' and a 'price' field.
            desired_depth (float): The depth (in MW) specifying how many of the objects should be taken into consideration.
            min_depth (float): The required minimum depth (in percent of the desired depth). If this requirement is not met, return value is 0.

        Returns:
            dict[str, float]: The weighted average price for the desired depth for each key in the dictionary.
        """
        if min_depth and min_depth > 0.99:
            raise Exception("The minimum depth has to be given as percentage of the desired depth.")

        vwaps = {k: 0 for k in [*objects]}

        for key, obj in tqdm(objects.items(), desc="Calculating Single VWAPs", unit="time periods", leave=False):
            available_depth = 0
            total_value = 0

            for ind, row in obj.iterrows():
                if available_depth + row.quantity < desired_depth:
                    available_depth = available_depth + row.quantity
                    total_value += row.quantity * row.price
                else:
                    total_value += (desired_depth - available_depth) * row.price
                    available_depth += desired_depth - available_depth
                    available_depth = round(available_depth, 2)
                    break

            # If the 'min_depth' parameter is set, then the available depth on the market has to fulfill the minimum requirements.
            if min_depth and available_depth and available_depth > desired_depth * min_depth \
                    or not min_depth and available_depth:
                vwaps[key] = round(total_value / available_depth, 2)

        return vwaps

    @staticmethod
    def vwap_by_timeperiod(objects: object,
                           timestamp: object,
                           time_spec: str = "60T-60T-0T") -> float:
        """
        Function to calculate the value-weighted average price at the given point in time for the last X minutes.

        To specify the time period precisely, the time_spec parameter should be used. The pattern is always as follows:

        {60/30/15/0}T-{60/45/30/15}T-{45/30/15/0}T

        Explanation:
            {60/30/15/0}T -> Floor, will count back to the last full hour/ half-hour/ quarter-hour / last minute and act as starting point
            {60/45/30/15}T -> Execution From, determines the minutes that should be subtracted from Floor to reach starting point for calculation
            {45/30/15/0}T -> Execution To, determines the minutes that should be subtracted from Floor to reach end point for calculation

        Examples:
            Current Time: 16:23:30
            60T-60T-0T  <--> VWAP of the previous trading hour (15:00-16:00).
            60T-15T-0T  <--> VWAP of the last quarter-hour of the previous trading hour (15:45-16:00).
            60T-30T-15T <--> VWAP of third quarter-hour of the previous trading hour (15:30-15:45).
            15T-60T-0T  <--> VWAP of last hour calculated from last quarter hour (15:15-16:15).
            0T-60T-30T  <--> VWAP of first half of the last hour calculated from current timestamp (15:23-15:53).

        Args:
            objects (pd.DataFrame): Collection of trades/ orders
            timestamp (str): Current timestamp
            time_spec (str): String of time specification as explained above

        Returns:
            float
        """
        if objects is None or isinstance(objects, pd.DataFrame) and objects.empty or not bool(
                re.search("((60|30|15|0)T-(60|45|30|15)T-(45|30|15|0)T)", time_spec)):
            return 0

        # Parse time specification
        time_periods = [int(t) for t in time_spec.replace("T", "").split("-")]
        recalculation_point = timestamp.floor(freq=f"{time_periods[0] or ''}T")
        execution_from = recalculation_point - pd.Timedelta(minutes=time_periods[1])
        execution_to = recalculation_point - pd.Timedelta(minutes=time_periods[2])

        # Filter and check dataframe
        field = "exec_time" if "exec_time" in objects.columns else "as_of"

        if (filtered := objects.loc[(objects[field] >= execution_from) & (objects[field] < execution_to)]).empty:
            return 0

        return round(
            sum(values["price"] * values["quantity"] for row, values in filtered.iterrows()) / sum(filtered.quantity),
            2)

    @staticmethod
    @validate_arguments
    def calc_rolling_vwap(trades: dict[tuple[datetime, datetime], pandas_DataFrame],
                          rolling_interval: int = 1,
                          rolling_time_unit: str = "hour") -> dict[str, pandas_DataFrame]:
        """
        This method can be used to calculate the rolling weighted average price for trades.
        Every item in the given dataframe will be assigned the specific value weighted average price of all previous items that were executed in
        the given time window (counting from the execution time of the current item).

        Args:
            trades (dict[str, DataFrame): A dictionary of dataframes containing trades
            rolling_interval (int): The interval time that should be considered when calculating an items specific VWAP
            rolling_time_unit (str): The time unit that VWAP should be calculated for. Possible: hour, minute, second

        Returns:
            dict[str, pd.Dataframe]: Original dictionary of dataframes, extended by weighted average price for the set time interval for each item
        """

        if rolling_time_unit not in ["hour", "minute", "second"]:
            raise ValueError("rolling_time_unit needs to be one of the following: hour, minute, second")

        t_map = {"hour": "h", "minute": "min", "second": "s"}

        for k, v in tqdm(trades.items(), desc="Calculating Rolling VWAPs", unit="time periods", leave=False):
            t = f"{rolling_interval}{t_map[rolling_time_unit]}"

            # Set index on temporary dataframe
            v_temp = v.set_index("exec_time").sort_values(by="exec_time")

            # Calculate vwap
            ptq = v_temp.price * v_temp.quantity
            quant_sum = v_temp.rolling(window=t)["quantity"].sum()
            ptq_sum = ptq.rolling(window=t).sum()

            # Add to original df
            v[f"vwap_{t}"] = round(ptq_sum / quant_sum, 2).to_list()

        return trades

    @staticmethod
    @validate_arguments
    def calc_orderbook_vwap(orderbook: dict[datetime, pandas_DataFrame],
                            depth: Union[int, float] = 0) -> tuple[pandas_DataFrame, pandas_DataFrame]:
        """
        Function to calculate value-weighted average prices for a single order book for bids and asks respectively.

        Args:
            orderbook (dict): Single order book
            depth (int/float): Depth in MW to calculate average price for

        Returns:
            tuple(vwap_asks, vwap_bids)
        """

        # Add new column for cumulative quantity
        asks = {k: df.insert(1, "cum_quant", value=df.quantity.cumsum()) or df for k, v in orderbook.items() if
                not (df := v.loc[v.type == "ask"].sort_values(by=['price'], ascending=True)).empty}
        bids = {k: df.insert(1, "cum_quant", value=df.quantity.cumsum()) or df for k, v in orderbook.items() if
                not (df := v.loc[v.type == "bid"].sort_values(by=['price'], ascending=False)).empty}

        # takes all orders up to desired depth or the first order if it exceeds depth or all orders if depth is 0
        vwap_asks = pd.DataFrame({k: {
            "vwap": round(sum((df := df_t if not (
                df_t := v.loc[v.cum_quant <= (depth if depth else max(v.cum_quant))]).empty else v.head(
                1)).price * df.quantity) / sum(
                df.quantity), 2),
            "depth": sum(v.quantity)} for k, v in asks.items()}).T

        vwap_bids = pd.DataFrame({k: {
            "vwap": round(sum((df := df_t if not (
                df_t := v.loc[v.cum_quant <= (depth if depth else max(v.cum_quant))]).empty else v.head(
                1)).price * df.quantity) / sum(
                df.quantity), 2),
            "depth": sum(v.quantity)} for k, v in bids.items()}).T

        return vwap_asks, vwap_bids

    @staticmethod
    @validate_arguments
    def plot_ohlc(ohlc_data: dict[tuple[datetime, datetime], pandas_DataFrame],
                  visualization: str = "candlestick",
                  ohlc_key: Union[int, str] = 0) -> Union[go.Figure, None]:
        """
        Creates a plotly plot of all ohlc data to be displayed by Dash server. Set ohlc_key to change displayed
        dataframe.

        Args:
            ohlc_data (dict{key: DataFrame}): OHLC Data
            visualization (str): Type of visualization, either candlestick or ohlc
            ohlc_key (int/ str): Dictionary key

        Returns:
            Plotly plot
        """
        # Check
        empty_ohlc = [k for k, v in ohlc_data.items() if v.empty]
        ohlc_data = {k: v for k, v in ohlc_data.items() if not v.empty}
        if not ohlc_data:
            raise ValueError("All ohlc objects are empty!")
        if empty_ohlc:
            print(f"Warning: The following ohlc objects are empty and have been removed: {empty_ohlc}")

        visualization = "candlestick" if visualization not in ["candlestick", "ohlc"] else visualization

        mapping = {"candlestick": go.candlestick,
                   "ohlc": go.Ohlc}

        # Setup
        try:
            ohlc_key = [*ohlc_data][ohlc_key] if isinstance(ohlc_key, int) else ohlc_key
        except (IndexError, TypeError):
            ohlc_key = [*ohlc_data][0]

        ohlc_data = ohlc_data[ohlc_key]

        # Plotting ohlc-Diagram with Plotly
        try:
            fig = go.Figure(data=mapping[visualization](x=ohlc_data.index,  # Alternative: go.ohlc()
                                                        open=ohlc_data['open'],
                                                        high=ohlc_data['high'],
                                                        low=ohlc_data['low'],
                                                        close=ohlc_data['close']))

            fig.update_layout(title='OHLC-Chart', yaxis_title='Price per MWh')
            return fig

        except:  # noqa: E722
            return None

    @staticmethod
    @validate_arguments
    def ohlc_table(ohlc_data: dict[tuple[datetime, datetime], pandas_DataFrame],
                   ohlc_key: int = 0) -> pd.DataFrame:
        """
        Creates a custom DataFrame to be displayed by Dash server.

        Args:
            ohlc_data (dict[key: DataFrame]): OHLC Data
            ohlc_key (int): Dictionary key

        Returns:
            DataFrame
        """

        # Check
        empty_ohlc = [k for k, v in ohlc_data.items() if v.empty]
        ohlc_data = {k: v for k, v in ohlc_data.items() if not v.empty}
        if not ohlc_data:
            raise ValueError("All ohlc objects are empty!")
        if empty_ohlc:
            print(f"Warning: The following ohlc objects are empty and have been removed: {empty_ohlc}")

        # Setup
        try:
            ohlc_key = [*ohlc_data][ohlc_key]
        except (IndexError, TypeError):
            ohlc_key = [*ohlc_data][0]

        ohlc_contract_data = ohlc_data[ohlc_key].reset_index()
        ohlc_contract_data = ohlc_contract_data.rename(columns={"index": "Timestamp"})

        return ohlc_contract_data

    @staticmethod
    @validate_arguments
    def plot_orderbook(orderbooks: dict[tuple[datetime, datetime], dict[str, pandas_DataFrame]],
                       orderbook_key: Union[int, str] = 0,
                       timestamp: Union[int, str] = -1) -> Union[go.Figure, None]:
        """
        Creates a plotly plot of a single order book to be displayed by browser or Dash server. Use order book_key
        to specify an order book and timestamp to specify the timeframe to display.

        Args:
            orderbooks (dict{key: DataFrame}): Order books
            orderbook_key (int): Dictionary key
            timestamp (int): Order book Key

        Returns:
            Plotly plot
        """
        # Check
        empty_ob = [k for k, v in orderbooks.items() if isinstance(v, pd.DataFrame) or not v]
        orderbooks = {k: v for k, v in orderbooks.items() if not isinstance(v, pd.DataFrame) and v}
        if not orderbooks:
            raise ValueError("All order books are empty!")
        if empty_ob:
            print(f"Warning: The following order books are empty and have been removed: {empty_ob}")

        # Setup
        line_shape = 'hv'
        mode = 'lines+markers'
        try:
            orderbook_key = [*orderbooks][orderbook_key] if isinstance(orderbook_key, int) else orderbook_key
        except (IndexError, TypeError):
            orderbook_key = [*orderbooks][0]

        try:
            timestamp = [*orderbooks[orderbook_key]][timestamp] if isinstance(timestamp, int) else timestamp
        except (IndexError, TypeError):
            timestamp = [*orderbooks][0][-1]

        orders = {"bid": {"name": "Bids", "sort_order": [True, False]},
                  "ask": {"name": "Asks", "sort_order": [True, True]}}

        # Plotting With Plotly
        df_plot = orderbooks[orderbook_key][timestamp].sort_values(by=['price'], ascending=True)
        fig = go.Figure()

        try:
            for i in ["bid", "ask"]:
                prices = df_plot.price[df_plot.type == i].to_list()
                if len(prices) == 0:
                    continue
                quantities = df_plot.quantity[df_plot.type == i].to_list()

                # Add Quantities
                if i == "bid":
                    quantities_added = np.cumsum(quantities[::-1])[::-1]
                else:
                    quantities_added = np.cumsum(quantities)

                temp_dict = {}
                for x, y in enumerate(prices):
                    temp_dict[x] = [y, quantities_added[x]]

                df_temp_plot = pd.DataFrame(temp_dict).T.sort_values(by=[0, 1], ascending=orders[i]["sort_order"])
                df_temp_plot.columns = ["price", "quantity"]

                fig.add_trace(
                    go.Scatter(x=df_temp_plot.price, y=df_temp_plot.quantity, name=orders[i]["name"], fill='tozeroy',
                               line_shape=line_shape, mode=mode))  # fill down to xaxis

            fig.update_layout(title=f'Orderbook {orderbook_key} - {timestamp.split(" ")[1]}',
                              xaxis_title="Price per MWh", yaxis_title='Quantity')

        except:  # noqa: E722
            fig = go.Figure()
            fig.add_trace(go.Scatter())
            fig.update_layout(title=f'Orderbook {orderbook_key}', xaxis_title="Price per MWh", yaxis_title='Quantity')

        return fig

    @staticmethod
    @validate_arguments
    def plot_volume_history(trade_data: dict[tuple[datetime, datetime], pandas_DataFrame],
                            trade_key: Union[int, str] = 0) -> Union[go.Figure, None]:
        """
        Creates a plotly plot of the trade volume for a single contract to be displayed by browser or Dash server.

        Args:
            trade_data (dict{key: DataFrame}):  Trade Data
            trade_key (int/str): Dictionary key

        Returns:
            Plotly plot
        """
        # Check
        empty_trades = [k for k, v in trade_data.items() if v.empty]
        trade_data = {k: v for k, v in trade_data.items() if not v.empty}
        if not trade_data:
            raise ValueError("There are no trades!")
        if empty_trades:
            print(f"Warning: The following trade collections are empty and have been removed: {empty_trades}")

        line_shape = 'hv'
        mode = 'lines+markers'
        try:
            trade_key = [*trade_data][trade_key] if isinstance(trade_key, int) else trade_key
        except (IndexError, TypeError):
            trade_key = [*trade_data][0]

        df_trade = trade_data[trade_key].sort_values(by=["exec_time"], ascending=[True])
        quantities = np.cumsum(df_trade["quantity"].tolist())

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=df_trade.exec_time, y=quantities, name="trades", fill='tozeroy', line_shape=line_shape,
                       mode=mode,
                       line_color='rgb(34,139,34)'))  # fill down to xaxis
        fig.update_layout(title="Trade Volume", xaxis_title="Time", yaxis_title='Quantity')

        return fig

    @validate_arguments
    def calc_trade_vwap(self,
                        contract_time: str,
                        delivery_area: str,
                        trade_data: dict[tuple[datetime, datetime], pandas_DataFrame] = None,
                        time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss",
                                                    default_factory=type(None)),
                        previous_days: int = 10,
                        contract_id: str = None,
                        index: str = "ID3") -> pd.DataFrame:
        """
        Function gets trades for a certain contract for X previous days in the same delivery period and calculates their
        VWAP for ID3 or ID1 or all. Generates a new list of trades for these contracts.
        Can take either a time period or a specific contract ID to load data for.

        If previous days is 0, only the trades for the original time period/ contract will be loaded.

        Can also be called directly from get_public_trades with parameter 'add_vwap' to add VWAP to loaded trades.

        Args:
            contract_time (str): hourly, half-hourly or quarter-hourly
            delivery_area (str): Area Code for Delivery Area
            trade_data (dict[str, pd.DataFrame]: Dictionary of Dataframes containing Contract Trade Data
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            previous_days (int): Amount of previous days to load data
            contract_id (str): ID of specific Contract
            index (str): all, ID3, ID1

        Returns:
            DataFrame: Trade Data with added calculated fields
        """
        # Only ApiExporter can load more than 1 day
        if not hasattr(self, "client") or isinstance(self.client, HistoryApiClient):
            previous_days = 1

        if not trade_data and contract_time == "all":
            raise ValueError(
                "Contract time can only be one of hourly, half-hourly or quarter-hourly if no trade data is given")

        # Setup
        indices = {"all": 1980, "ID3": 180, "ID1": 60}
        contract_api = ContractApi(self.client)

        # Create Empty Dataframe
        all_trade_data = []

        # Get Delivery Start If Contract ID was passed
        if contract_id:
            if not isinstance(contract_id, str):
                raise TypeError("contract_id has to be a string")
            time_from = str(contract_api.find_contracts(contract_id=[contract_id])[0].delivery_start).replace("+00:00",
                                                                                                              "")

        # Get Trade Data
        trade_data = trade_data if trade_data else self.get_public_trades_by_days(time_from=time_from,
                                                                                  previous_days=previous_days,
                                                                                  delivery_area=delivery_area,
                                                                                  contract_time=contract_time)

        # Processing
        for key, value in tqdm(trade_data.items(), desc="Calculating Trade VWAPs", unit="time periods", leave=False):
            # Time Difference In Minutes
            time_diff = [round((key[0].replace(tzinfo=tzutc()) - i.replace(tzinfo=tzutc())).total_seconds() / 60, 2) for
                         i in
                         value.exec_time]
            value["time_diff"] = time_diff
            all_trade_data.append(value)

        all_trade_data = pd.concat(all_trade_data)
        all_trade_data = all_trade_data.loc[all_trade_data["time_diff"] <= indices[index]].sort_values(by=['time_diff'],
                                                                                                       ascending=False)
        total_quantity = all_trade_data.quantity.sum()
        all_quantities = all_trade_data.quantity.tolist()
        all_prices = all_trade_data.price.tolist()

        target_volume = []
        cumulated_quantities = []
        calculated_vwaps = []
        cum_weighted_price = 0

        for nr, item in enumerate(all_quantities):
            cum_sum = round(sum(all_quantities[:nr + 1]), 2)
            cum_weighted_price += all_prices[nr] * all_quantities[nr]
            calculated_vwaps.append(round(cum_weighted_price / cum_sum, 2))
            cumulated_quantities.append(cum_sum)
            target_volume.append(round(cum_sum / total_quantity, 4))

        all_trade_data["cumulated_quantity"] = cumulated_quantities
        all_trade_data["target_volume"] = target_volume
        all_trade_data["vwap"] = calculated_vwaps

        return all_trade_data.reset_index(drop=True)


class ApiExporter(BaseExporter):
    """
    Exporter class for interaction with the PowerBot API.

    This class can/ should be used when:
        - the requested data is recent enough to still be stored in the PowerBot instance (see data retention policy)
        - the requested data is fairly small in size (multiple hours, not multiple day -> extensive loading time &
          constant strain on the API rate limit)
        - the requested data is already stored in the local __pb_cache__ and has been loaded via API.

    ATTENTION: if you try to load data from your cache and the original data is already purged from your instance,
    you are no longer able to create an index of contract IDs to load the local data with. Should this occur, please
    load the data in question via the HistoryExporter.
    """
    api_key: str = Field(description="A Standard API Key",
                         example="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXX")
    host: str = Field(description="URL of the PowerBot instance to connect to",
                      example="https://backup.powerbot-trading.com/{COMPANY NAME}/{EXCHANGE}/v2/api")

    client: val_ApiClient = Field(description="Placeholder value, do not overwrite", default_factory=type(None))

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Init client
        self.client = init_client(api_key=self.api_key, host=self.host)

    @root_validator
    def check_credentials(cls, values):
        api_key, host = values.get('api_key'), values.get('host')

        pattern_key = "\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"  # noqa: W605
        pattern_host = "https://\w{3,7}.powerbot[.-]trading(.com)?(:443)?/\w+/\w+/v\d{1}/api"  # noqa: W605

        assert re.match(pattern_key, api_key) and re.match(pattern_host,
                                                           host), "Your credentials do not conform to the necessary formats"

        return values

    @validate_arguments
    def get_contracts(self,
                      time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss",
                                                  default_factory=type(None)),
                      time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss",
                                                  default_factory=type(None)),
                      contract_ids: list[str] = None,
                      contract_time: str = "all",
                      products: list[str] = None,
                      allow_udc: bool = False,
                      delivery_areas: list[str] = None) -> list[ContractItem]:
        """
        Loads all contracts for specified timeframe. Alternatively, a list of contract IDs can be passed instead of a timeframe.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_ids (list[str]): Optionally, a list of specific contract IDs can be passed to return contract objects
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): Optional list of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all
            delivery_areas (list): List of EIC-codes

        Returns:
            list[ContractItem]: List containing Contracts
        """
        return super().get_contract_ids(
            time_from=time_from,
            time_till=time_till,
            contract_ids=contract_ids,
            contract_time=contract_time,
            products=products,
            allow_udc=allow_udc,
            delivery_areas=delivery_areas,
            return_contract_objects=True)

    @validate_arguments
    def get_contract_ids(self,
                         time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss",
                                                     default_factory=type(None)),
                         time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss",
                                                     default_factory=type(None)),
                         contract_ids: list[str] = None,
                         contract_time: str = "all",
                         products: list[str] = None,
                         allow_udc: bool = False,
                         delivery_areas: list[str] = None) -> dict[str, list[str]]:
        """
        Loads all contract IDs for specified timeframe. Alternatively, a list of contract IDs can be passed instead of a timeframe, returning a
        dictionary of contract IDs compatible with all other functions of the Backtesting package.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_ids (list[str]): Optionally, a list of specific contract IDs can be passed to return contract objects
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): Optional list of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all
            delivery_areas (list): List of EIC-codes

        Returns:
            dict{key: (list[str])}: Dictionary of Contract IDs
        """
        return super().get_contract_ids(time_from=time_from,
                                        time_till=time_till,
                                        contract_ids=contract_ids,
                                        contract_time=contract_time,
                                        products=products,
                                        allow_udc=allow_udc,
                                        delivery_areas=delivery_areas)

    @validate_arguments
    def get_public_trades(self,
                          contract_ids: dict[tuple[datetime, datetime], list[str]],
                          delivery_area: str,
                          contract_time: str,
                          iteration_delay: float = 0,
                          serialize_data: bool = True,
                          add_vwap: bool = False,
                          use_cached_data: bool = False,
                          caching: bool = True,
                          gzip_files: bool = True,
                          as_csv: bool = False) -> dict[tuple[datetime, datetime], pd.DataFrame]:
        """
        Load trade data for given contract IDs. If add_vwap is True, VWAP will be calculated for each trade, incorporating
        all previous trades.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            delivery_area (str): EIC Area Code for Delivery Area (not needed when loading from historic cache)
            contract_time (str): all, hourly, half-hourly or quarter-hourly
            iteration_delay (float): Optional delay between iterations to prevent hitting API rate limits
            serialize_data (bool): If False, request is received without serialization. Recommended for large data collections
            add_vwap (bool): If True, additional VWAP parameters will be added to each dataframe
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        return super().get_public_trades(contract_ids=contract_ids,
                                         contract_time=contract_time,
                                         delivery_area=delivery_area,
                                         iteration_delay=iteration_delay,
                                         serialize_data=serialize_data,
                                         add_vwap=add_vwap,
                                         use_cached_data=use_cached_data,
                                         caching=caching,
                                         gzip_files=gzip_files,
                                         as_csv=as_csv)

    @validate_arguments
    def get_public_trades_by_days(self,
                                  previous_days: int,
                                  delivery_area: str,
                                  time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss",
                                                              default_factory=type(None)),
                                  contract_time: str = None,
                                  contract_id: str = None) -> dict[tuple[datetime, datetime], pd.DataFrame]:
        """
        Gets the contract ID specified by a timeframe or directly by ID and load all trade data for this contract and all
        contracts in the same timeframe for X previous days.

        Args:
            time_from (str/ datetime): YYYY-MM-DD hh:mm:ss
            previous_days (int): Amount of previous days to load data for
            delivery_area (str): EIC Area Code for Delivery Area
            contract_time (str): hourly, half-hourly or quarter-hourly
            contract_id (str): specific contract ID

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        if not time_from and not contract_id:
            raise TypeError("Either time_from and contract_time or a specific contract ID have to be passed.")
        if time_from and not contract_time:
            raise TypeError("If time_from is given, contract_time has to be passed as well.")

        products = None
        use_cached_data = True
        timeframes = {"hourly": 60, "half-hourly": 30, "quarter-hourly": 15}

        try:
            if time_from:
                time_till = time_from + timedelta(minutes=timeframes[contract_time])

            else:
                contract = ContractApi(self.client).find_contracts(contract_id=[contract_id])[0]
                if contract.type == "UDC":
                    raise TypeError("This function does not work for user defined contracts (UDC).")
                time_from = contract.delivery_start
                time_till = contract.delivery_end
                timeframes = {60: "hourly", 30: "half-hourly", 15: "quarter-hourly"}
                contract_time = timeframes[int((contract.delivery_end - contract.delivery_start).seconds / 60)]
                products = [contract.product]
                use_cached_data = False

            contract_ids = self.get_contract_ids(time_from=time_from, time_till=time_till, contract_time=contract_time,
                                                 products=products,
                                                 delivery_areas=[delivery_area])

            for _ in range(previous_days):
                time_from -= timedelta(days=1)
                time_till -= timedelta(days=1)

                contract_ids.update(
                    self.get_contract_ids(time_from=time_from, time_till=time_till, contract_time=contract_time,
                                          products=products))

        except (ValueError, TypeError):
            raise ValueError("Please use correct format: yyyy-mm-dd hh:mm:ss")

        # Get Trade Data
        return self.get_public_trades(contract_ids=contract_ids,
                                      delivery_area=delivery_area,
                                      contract_time=contract_time,
                                      use_cached_data=use_cached_data)

    @validate_arguments
    def get_contract_history(self,
                             contract_ids: dict[tuple[datetime, datetime], list[str]],
                             delivery_area: str,
                             iteration_delay: float = 0,
                             serialize_data: bool = True,
                             use_cached_data: bool = False,
                             caching: bool = True,
                             gzip_files: bool = True,
                             as_csv: bool = False) -> dict[tuple[datetime, datetime], pd.DataFrame]:
        """
        Load contract history for given contract IDs.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            delivery_area (str): EIC Area Code for Delivery Area (not needed when loading from historic cache)
            iteration_delay (float): Optional delay between iterations to prevent hitting API rate limits
            serialize_data (bool): If False, request is received without serialization. Recommended for large data collections
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        return super().get_contract_history(
            contract_ids=contract_ids,
            delivery_area=delivery_area,
            iteration_delay=iteration_delay,
            serialize_data=serialize_data,
            use_cached_data=use_cached_data,
            caching=caching,
            gzip_files=gzip_files,
            as_csv=as_csv)

    @validate_arguments
    def get_signals(self,
                    time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                    time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                    delivery_area: str = None,
                    portfolio_id: list[str] = None) -> list[Signal]:
        """
        Function gathers all Signals received by the API in the specified time period and gathers them in a list.

        Args:
            time_from (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            time_till (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            delivery_area (str): EIC Area Code for Delivery Area
            portfolio_id (str): List of all portfolios that signals should be loaded from

        Returns:
            list[Signal]
        """

        if not isinstance(time_from, datetime) or not isinstance(time_till, datetime):
            raise TypeError("time_from and time_till need to be of type datetime")

        return _get_private_data(api_client=self.client,
                                 data_type="signal",
                                 time_from=time_from,
                                 time_till=time_till,
                                 delivery_area=delivery_area,
                                 portfolio_ids=portfolio_id)

    @validate_arguments
    def get_own_trades(self,
                       time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                       time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                       delivery_area: str = None,
                       portfolio_id: list[str] = None) -> list[Trade]:
        """
        Function to collect all Own Trades for the defined time period, either specific to portfolio and/or delivery area
        or all portfolios and delivery areas used API key has access to.

        Args:
            time_from (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            time_till (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            delivery_area (str): EIC Area Code for Delivery Area
            portfolio_id (list[str]): List of specific portfolio IDs to load trades from. If left out, will load from all IDs.

        Returns:
            list[Trade]
        """

        if not isinstance(time_from, datetime) or not isinstance(time_till, datetime):
            raise TypeError("time_from and time_till need to be of type datetime")

        return _get_private_data(api_client=self.client,
                                 data_type="own_trade",
                                 time_from=time_from,
                                 time_till=time_till,
                                 delivery_area=delivery_area,
                                 portfolio_ids=portfolio_id)

    @validate_arguments
    def get_internal_trades(self,
                            time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                            time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                            delivery_area: str = None,
                            portfolio_id: list[str] = None) -> list[InternalTrade]:
        """
        Function to collect all Internal Trades for the defined time period, either specific to portfolio and/or delivery
        area or all portfolios and delivery areas used API key has access to.

        Args:
            time_from (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            time_till (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            delivery_area (str): EIC Area Code for Delivery Area
            portfolio_id (list[str]): List of specific portfolio IDs to load trades from. If left out, will load from all IDs.

        Returns:
            list[InternalTrade]
        """
        if not isinstance(time_from, datetime) or not isinstance(time_till, datetime):
            raise TypeError("time_from and time_till need to be of type datetime")

        return _get_private_data(api_client=self.client,
                                 data_type="internal_trade",
                                 time_from=time_from,
                                 time_till=time_till,
                                 delivery_area=delivery_area,
                                 portfolio_ids=portfolio_id)

    @validate_arguments
    def get_own_orders(self,
                       delivery_area: str = None,
                       portfolio_ids: list[str] = None,
                       contract_ids: Union[list[str], dict[tuple[datetime, datetime], list[str]]] = None,
                       active_only: bool = False) -> list[OwnOrder]:
        """
        Function to collect all available Own Orders, either specific to portfolio and/or delivery area or all portfolios
        and delivery areas used API key has access to.

        Args:
            delivery_area (str): EIC Area Code for Delivery Area
            portfolio_ids (list[str]): List of specific portfolio IDs to load trades from. If left out, will load from all IDs.
            contract_ids (list/dict): Collection of contract IDs to specifically load own orders for
            active_only (bool):  True if only active orders should be loaded. If False, loads also hibernate and inactive.

        Returns:
            list[OwnOrder]
        """
        return _get_private_data(api_client=self.client,
                                 data_type="own_order",
                                 delivery_area=delivery_area,
                                 portfolio_ids=portfolio_ids,
                                 contract_ids=contract_ids,
                                 active_only=active_only)


class HistoryExporter(BaseExporter):
    """
    Exporter class for interaction with the PowerBot History API and the subsequently created local __pb_cache__.

    This class can/ should be used when:
        - the requested data is older than at least 2-3 days and has already been made available via History API
        - the requested data is already stored in the local __pb_cache__ and has been loaded via History API.

    ATTENTION: loading historic data from the History API will create a json file containing all contract information
    for the respective day. If this file should be deleted, the HistoryExporter can no longer create an index of
    contract IDs and therefore not load anything from the local cache.
    """
    exchange: str = Field(description="The exchange data should be loaded for")
    delivery_area: str = Field(description="EIC-code of the delivery area data should be loaded for")

    client: val_HistoryApiClient = Field(description="Placeholder value, do not overwrite", default_factory=type(None))

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Init client
        self.client = HistoryApiClient(self.exchange, self.delivery_area)

    @root_validator
    def check_credentials(cls, values):
        exchange, delivery_area = values.get('exchange'), values.get('delivery_area')

        assert exchange in EXCHANGES, "Exchange is not in allowed exchanges"
        assert delivery_area in EIC_CODES[exchange], "Delivery area is not in allowed delivery areas for this exchange"

        return values

    @validate_arguments
    def get_historic_data(self,
                          api_key: str,
                          day_from: Union[str, datetime],
                          day_to: Union[str, datetime] = None,
                          delivery_areas: list[str] = None,
                          cache_path: Path = None,
                          extract_files: bool = False,
                          process_data: bool = False,
                          skip_on_error: bool = False,
                          keep_zip_files: bool = False,
                          concurrent: bool = False) -> Union[list, dict]:
        """
        Function loads all public data for specified days in the specified delivery area. Output is a zipped directory containing all files in
        JSON format. Optionally, zip file can be extracted automatically and processed to be compatible with other functions in the
        powerbot_backtesting package.

        Attention:
        If concurrent is True, script has to be run via:
            if __name__ == "__main__":
                ...

        Args:
            api_key (str): Specific history instance API key
            day_from (str): Datetime/ String in format YYYY-MM-DD
            day_to (str): Datetime/ String in format YYYY-MM-DD
            delivery_areas (list): List of EIC Area Codes for Delivery Areas
            cache_path (Path): Optional path for caching files
            extract_files (bool): True if zipped files should be extracted automatically (Warning: immense size increase)
            process_data (bool): True if extracted files should be processed to resemble files loaded via API
            skip_on_error (bool): True if all dates that cannot possibly be loaded (e.g. due to lack of access rights) are
            skipped if the difference between day_from and day_to is at least 2 days
            keep_zip_files (bool): True if zip-files should be kept after download
            concurrent (bool): True if file transformation should be distributed to all CPU cores

        Returns:
            list of loaded file paths | dict
        """
        delivery_areas = delivery_areas if delivery_areas else [self.client.delivery_area]

        # Validity check
        if not isinstance(day_from, datetime):
            try:
                day_from = datetime.strptime(day_from, DATE_YMD)
            except ValueError:
                raise ValueError("day_from needs to be a date or a string in YYYY-MM-DD format")
        if day_to and not isinstance(day_to, datetime):
            try:
                day_to = datetime.strptime(day_to, DATE_YMD)
            except ValueError:
                raise ValueError("day_to needs to be a date or a string in YYYY-MM-DD format")

        delivery_areas = delivery_areas if isinstance(delivery_areas, list) else [delivery_areas]
        cache_path = "./__pb_cache__" if not cache_path else cache_path
        cache_path = Path(cache_path) if not isinstance(cache_path, Path) else cache_path
        headers = {"accept": "application/zip", "X-API-KEY": api_key}
        day_to = day_to if day_to else day_from
        skip_on_error = True if skip_on_error and day_to and day_to - day_from >= timedelta(days=2) else False

        zipfiles = []
        extracted_files = {}
        retry = 0
        reload_faulty = 0

        while day_from <= day_to:
            # While False, days will continue with iteration
            prevent_update = False

            for del_area in delivery_areas:
                host = f"https://history.powerbot-trading.com/history/{self.client.exchange}/{del_area}/{day_from.strftime(DATE_YMD)}"

                # Filepath
                filepath = cache_path.joinpath(
                    f"history/{self.client.exchange}_{del_area}/{day_from.strftime(DATE_YM)}")

                # File
                filename = f"{day_from.strftime(DATE_MD)}_public_data.zip"
                zipfiles.append(f"{del_area}_{filename.strip('.zip')}")

                # Skip if file exists
                if not filepath.joinpath(filename).exists() and not filepath.joinpath(
                        day_from.strftime(DATE_MD)).exists():
                    # Load file
                    r = requests.get(host, headers=headers, stream=True)
                    m = hashlib.sha256()

                    if skip_on_error and r.status_code in [204, 403, 404]:
                        continue
                    if r.status_code == 503:
                        raise ApiException(status=503, reason="Service unavailable or API rate limit exceeded")
                    if r.status_code == 404:
                        raise ApiException(status=404,
                                           reason=f"Data for '{day_from}' in {del_area} has not been exported yet")
                    if r.status_code == 403:
                        raise ApiException(status=403,
                                           reason="Currently used API Key does not have access to this data")
                    if r.status_code == 204:
                        raise ApiException(status=204, reason=f"There is no data for '{day_from}' in {del_area}")

                    # Create filepath only if file is valid
                    filepath.mkdir(parents=True, exist_ok=True)

                    with open(filepath.joinpath(filename), 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=128):
                            m.update(chunk)
                            fd.write(chunk)

                    expected_hash = \
                        json.loads(
                            [i for i in requests.get(host + "/sha256", headers=headers, stream=True).iter_lines()][0])[
                            "sha_256"]

                    if not expected_hash == m.hexdigest():
                        if retry < 3:  # Retry 3 times
                            filepath.joinpath(filename).unlink(missing_ok=False)
                            retry += 1
                            prevent_update = True
                            continue
                        if skip_on_error:  # Skip
                            filepath.joinpath(filename).unlink(missing_ok=False)
                        else:
                            filepath.joinpath(filename).unlink(missing_ok=False)
                            raise ChecksumError(
                                "Corrupted file: expected sha256 checksum does not match sha256 of received files. "
                                "Please try again.")

                # Extraction
                if extract_files and not filepath.joinpath(day_from.strftime(DATE_MD)).exists():
                    try:
                        with ZipFile(filepath.joinpath(filename), 'r') as _zip:
                            _zip.extractall(filepath.joinpath(day_from.strftime(DATE_MD)))
                        if not keep_zip_files:
                            # Delete Zip
                            filepath.joinpath(filename).unlink()
                        # Reset counter if file is OK
                        reload_faulty = 0

                    except BadZipFile:
                        if reload_faulty < 3:
                            print(
                                f"The loaded file for day {day_from} in {del_area} is faulty. "
                                f"Attempting to load it again (Retry {reload_faulty + 1})")

                            # Delete faulty file
                            filepath.joinpath(filename).unlink(missing_ok=True)

                            # Set counter and prevent update
                            reload_faulty += 1
                            prevent_update = True

                        elif skip_on_error:
                            print(
                                f"The loaded file for day {day_from} in {del_area} is still faulty (Retry {reload_faulty}). Skipping file")

                        else:
                            raise TypeError(
                                f"The loaded file for day {day_from} in {del_area} is still faulty (Retry {reload_faulty}). "
                                f"Please delete cache and load again")

                if extract_files and not reload_faulty:
                    # Add to dictionary
                    extracted_files[f"{del_area}_{filename.strip('.zip')}"] = [str(e) for e in filepath.joinpath(
                        day_from.strftime(DATE_MD)).iterdir() if e.is_file()]

                # Reset counters
                retry = 0
                reload_faulty = 0 if reload_faulty and not prevent_update else reload_faulty

            day_from = day_from + timedelta(days=1) if not prevent_update else day_from

        if not zipfiles:
            return []
        if extract_files:
            if process_data:
                return self.__process_historic_data(extracted_files, keep_zip_files, concurrent)
            return extracted_files
        return zipfiles

    def __process_historic_data(self,
                                extracted_files: Union[list[str], dict[str, list[str]]],
                                keep_zip_files: bool = False,
                                concurrent: bool = False):
        """
        Function processes list of files extracted from a zip-file downloaded via History API to be compatible with the
        rest of the powerbot_backtesting package. Once files have been processed, they are cached in the same manner as
        data loaded via PowerBot API, allowing functions like get_contract_history and get_public_trades to load them from
        the cache.

        Args:
            extracted_files (list(str), dict[str, list[str]]): List of files extracted with get_historic_data
            (-> return value of get_historic_data)
            keep_zip_files (bool): True if zip-files should be kept after download
        """
        # Setup
        prod_path = Path("./__pb_cache__/prod")
        prod_files = []

        for f_name, unzipped_files in (tqdm(extracted_files.items(),
                                            desc="Transform extracted files",
                                            unit="days",
                                            eave=False) if concurrent else extracted_files.items()):

            # We cannot delete this -> we need the index
            contract_file = [i for i in unzipped_files if "contracts.json" in i][0]
            contract_file = unzipped_files.pop(unzipped_files.index(contract_file))

            delivery_area = f_name.split("_")[0]

            # Contract file transformation & caching -> serves as index file
            index = _historic_contract_transformation(contract_file, self.client.exchange)

            # Group contracts after delivery period
            index['delivery_start'] = pd.to_datetime(index['delivery_start'])
            index['delivery_end'] = pd.to_datetime(index['delivery_end'])

            index.sort_values(by=["delivery_start"], inplace=True)

            contract_times = {}
            start = index.delivery_start.iloc[0]
            end = index.delivery_start.iloc[-1]

            while start <= end:
                for timestep in [15, 30, 60]:
                    ids = index.loc[(index.delivery_start == start)
                                    & (index.delivery_end == (start + timedelta(minutes=timestep)))].contract_id.tolist()
                    if ids:
                        contract_times[(start, start + timedelta(minutes=timestep))] = ids
                start += timedelta(minutes=15)

            # Add any contract with duration upwards of 1 hour
            udcs = index.loc[index.delivery_end - index.delivery_start > timedelta(hours=1)]

            for r, v in udcs.iterrows():
                if v.delivery_start.date() == v.delivery_end.date():
                    contract_times[(v.delivery_start, v.delivery_end)] = [v.contract_id]

            if concurrent:
                partial_func = partial(_multiprocess_data_transformation, unzipped_files=unzipped_files,
                                       exchange=self.client.exchange)

                with Pool() as p:
                    results = p.map(partial_func, [chunk for chunk in _splitter(contract_times, p._processes)])

                transformed_trade_files = {k: v for result in results for type, files in result.items() for k, v in
                                           files.items() if type == "trades"}
                transformed_order_files = {k: v for result in results for type, files in result.items() for k, v in
                                           files.items() if type == "orders"}

            else:
                transformed_trade_files, transformed_order_files = {}, {}
                # For each timestep
                for time, ids in tqdm(contract_times.items(), desc="Historic File Transformation", unit="files",
                                      leave=False):
                    files = {"trades": [i for i in unzipped_files if any(str(x) in i for x in ids) and "Trades" in i],
                             "orders": [i for i in unzipped_files if any(str(x) in i for x in ids) and "Orders" in i]}

                    for k, v in files.items():
                        if v:
                            if k == "trades":
                                transformed_trade_files[time] = _historic_data_transformation(v, self.client.exchange,
                                                                                              k)
                            else:
                                transformed_order_files[time] = _historic_data_transformation(v, self.client.exchange,
                                                                                              k)

            # Cache the result
            _cache_data("contracts", {index.delivery_start.iloc[0].date(): index}, delivery_area, self.client.exchange)
            _cache_data("trades", transformed_trade_files, delivery_area, self.client.exchange)
            _cache_data("ordhist", transformed_order_files, delivery_area, self.client.exchange)

            # Save paths of all transformed files
            # noqa: W605
            prod_files += [Path(e) for e in
                           prod_path.joinpath(
                               f"{self.client.exchange}_{delivery_area}/{end.strftime('%Y-%m')}/{end.strftime('%m-%d')}/raw").iterdir()  # noqa: W605
                           if e.is_file()]

        # Delete history directory if it's empty (no files)
        history_path = Path("./__pb_cache__/history")
        history_files = [file for root, directory, file in os.walk(history_path)]

        if not all(i for i in history_files) and not keep_zip_files:
            shutil.rmtree(history_path)

        return prod_files

    @staticmethod
    def get_history_key_info(api_key: str) -> dict:
        """
        Returns information for the specified History API Key

        Args:
            api_key (str): History API Key

        Returns:
            dict
        """
        headers = {"accept": "application/json", "X-API-KEY": api_key}
        host = "https://history.powerbot-trading.com/api-key"

        r = requests.get(host, headers=headers, stream=True)

        if r.status_code == 503:
            raise ApiException(status=503, reason="Service unavailable or API rate limit exceeded")
        if r.status_code == 400:
            raise ApiException(status=400, reason="Request could not be processed, please check your API Key")
        return r.json()

    @validate_arguments
    def get_contracts(self,
                      time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                      time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                      contract_time: Optional[str] = "all",
                      products: Optional[list[str]] = None,
                      allow_udc: Optional[bool] = False) -> list[ContractItem]:
        """
        Loads all contract IDs for specified timeframe from the local cache. The cached data has to have been loaded via get_historic_data, as
        this function utilizes the contract file as an index.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): Optional list of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all

        Returns:
            list[dict]: List of Contract Dictionaries
        """
        return super().get_contract_ids(time_from=time_from,
                                        time_till=time_till,
                                        contract_time=contract_time,
                                        products=products if products else [],
                                        allow_udc=allow_udc,
                                        return_contract_objects=True)

    @validate_arguments
    def get_contract_ids(self,
                         time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                         time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                         contract_time: Optional[str] = "all",
                         products: Optional[list[str]] = None,
                         allow_udc: Optional[bool] = False,
                         delivery_areas: Optional[list[str]] = None) -> Union[dict[tuple[datetime, datetime], list[str]], list[ContractItem]]:
        """
        Loads all contract IDs for specified timeframe from the local cache. The cached data has to have been loaded via get_historic_data, as this
        function utilizes the contract file as an index.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): Optional list of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all

        Returns:
            dict{key: (list[str])}: Dictionary of Contract IDs
        """
        return super().get_contract_ids(time_from=time_from,
                                        time_till=time_till,
                                        contract_time=contract_time,
                                        products=products if products else [],
                                        allow_udc=allow_udc)

    @validate_arguments
    def get_public_trades(self,
                          contract_ids: dict[tuple[datetime, datetime], list[str]],
                          contract_time: str,
                          add_vwap: bool = False,
                          as_csv: bool = False) -> dict[tuple[datetime, datetime], pd.DataFrame]:
        """
        Load trade data for given contract IDs from local cache. If add_vwap is True, VWAP will be calculated for each
        trade, incorporating all previous trades.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            contract_time (str): all, hourly, half-hourly or quarter-hourly
            add_vwap (bool): If True, additional VWAP parameters will be added to each dataframe
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        return super().get_public_trades(contract_ids=contract_ids,
                                         contract_time=contract_time,
                                         add_vwap=add_vwap,
                                         caching=True if as_csv else False,
                                         as_csv=as_csv)

    @validate_arguments
    def get_contract_history(self,
                             contract_ids: dict[tuple[datetime, datetime], list[str]],
                             as_csv: bool = False,
                             delivery_area: Optional[str] = None) -> dict[tuple[datetime, datetime], pd.DataFrame]:
        """
        Load contract history for given contract IDs from the local cache.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        return super().get_contract_history(contract_ids=contract_ids,
                                            as_csv=as_csv)


# noinspection PyTypeChecker
class SqlExporter(BaseExporter):
    """
    Exporter class for interaction with a SQL database containing PowerBot data.

    This class can/ should be used when:
        - a database containing the structure as defined per PowerBot SQLImporter exists and contains data.

    Instructions for passing arguments to exporter functions:
        - String
            If keyword argument is a string, it will be simply compared with '='. Optionally, a mathematical/ SQL
            operator (LIKE, BETWEEN x AND y, <, <=, >, >=, <>) can be passed within the string. This operator will be used instead of '='.

            Example:
                best_bid='> 0.00' -> best_bid > 0.00
                as_of="> 2020-09-20 00:00:00" -> as_of > '2020-09-20 00:00:00'
                exec_time='BETWEEN 2021-09-10 AND 2021-09-11' -> exec_time BETWEEN '2021-09-10' AND '2021-09-11'

        - Tuple
            If keyword argument is a tuple, it will be checked, if parameter is one of the elements of the tuple.

            Example:
                exchange=("Epex","NordPool") -> exchange IN ('Epex','NordPool')

        - List
            If keyword argument is a list, each element will be checked if it is in the parameter.

            Example:
                portfolio_ids=["TP1","TP2"] -> (portfolio_id LIKE '%TP1%' OR portfolio_id LIKE '%TP2%')

        - Dictionary
            If keyword argument is a dictionary, all values will be extracted and put into a tuple. Afterwards, the
            behaviour is the same as with tuples.

            Example:
                exchange={1:"Epex",2:"NordPool"} -> exchange IN ("Epex","NordPool")

        - Datetime
            If keyword argument is a datetime, parameter will be searched for the exact time of the datetime argument.
            This will in most cases not provide a satisfying result, therefore it is recommended to pass a datetime as
            a string with an operator in front.

            Example:
                as_of=datetime.datetime(2020, 9, 30, 10, 0, 0) -> as_of = '2020-09-30 10:00:00'
    """
    db_type: str = Field(description="Database type")
    user: str = Field(description="Database user")
    password: str = Field(description="Database password")
    host: str = Field(description="Database host address")
    database: str = Field(description="Database name")
    port: int = Field(description="Database port")

    logger: None = Field(description="Placeholder value, do not overwrite", default_factory=type(None))
    engine: None = Field(description="Placeholder value, do not overwrite", default_factory=type(None))

    SQL_ERRORS = (
        InterfaceError,
        OperationalError,
        ProgrammingError,
        TimeoutError,
    )

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Logging Setup
        logging.basicConfig(format="PowerBot_SQL_Exporter %(asctime)s %(levelname)-8s %(message)s",
                            level=logging.INFO)
        self.logger = logging.getLogger()

        # Initialize Connection
        self.engine = self.__create_sql_engine()

    @validator("user", "password")
    def validate_user_and_password(cls, value):
        value = quote(value)

        return value

    @validator("db_type")
    def validate_db_type(cls, value):
        allowed_db_types = ['mysql', 'mariadb', 'postgresql', 'oracle', 'mssql', 'amazon_redshift', 'apache_drill',
                            'apache_druid', 'apache_hive', 'apache_solr', 'cockroachdb', 'cratedb', 'exasolution',
                            'firebird', 'ibm_db2', 'monetdb', 'snowflake', 'teradata_vantage']

        assert value in allowed_db_types, f"Database {value} is not in allowed database"

        return value

    def __install_packages(self):
        """
        Tests if required packages for chosen SQL database type are available and installs them if necessary.
        """
        db_packages = {"mysql": ["mysql-connector-python"],
                       "mariadb": ["PyMySQL"],
                       "postgresql": ["psycopg2"],
                       "oracle": ["cx-Oracle"],
                       "mssql": ["pyodbc"],
                       "amazon_redshift": ["sqlalchemy-redshift", "psycopg2"],
                       "apache_drill": ["sqlalchemy-drill"],
                       "apache_druid": ["pydruid"],
                       "apache_hive": ["PyHive"],
                       "apache_solr": ["sqlalchemy-solr"],
                       "cockroachdb": ["sqlalchemy-cockroachdb", "psycopg2"],
                       "cratedb": ["crate-python"],
                       "exasolution": ["sqlalchemy_exasol", "pyodbc"],
                       "firebird": ["sqlalchemy-firebird"],
                       "ibm_db2": ["ibm_db_sa"],
                       "monetdb": ["sqlalchemy_monetdb"],
                       "snowflake": ["snowflake-sqlalchemy"],
                       "teradata_vantage": ["teradatasqlalchemy"]}

        self.logger.info("Now installing the following necessary package(s):\n"
                         f"{db_packages[self.db_type]}")

        import subprocess
        import sys
        for pkg in db_packages[self.db_type]:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

        return self.__create_sql_engine()

    def __create_sql_engine(self):
        """
        Initializes connection to SQL database
        """
        db_types = {"mysql": "mysql+mysqlconnector",
                    "mariadb": "mariadb+pymysql",
                    "postgresql": "postgresql+psycopg2",
                    "oracle": "oracle+cx_oracle",
                    "mssql": "mssql+pyodbc",
                    "amazon_redshift": "redshift+psycopg2",
                    "apache_drill": "drill+sadrill",
                    "apache_druid": "druid",
                    "apache_hive": "hive",
                    "apache_solr": "solr",
                    "cockroachdb": "cockroachdb",
                    "cratedb": "crate",
                    "exasolution": "exa+pyodbc",
                    "firebird": "firebird",
                    "ibm_db2": "db2+ibm_db",
                    "monetdb": "monetdb",
                    "snowflake": "snowflake",
                    "teradata_vantage": "teradatasql"}

        if self.port:
            try:
                engine = create_engine(
                    f'{db_types[self.db_type]}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}')
            except:  # noqa: E722
                pass
        try:
            engine = create_engine(
                f'{db_types[self.db_type]}://{self.user}:{self.password}@{self.host}/{self.database}')

            # Test connection
            engine.connect()

        except (NoSuchModuleError, ModuleNotFoundError):
            self.logger.info("You currently do not have all the necessary packages installed to access a database of"
                             f" type {self.db_type}.")
            return self.__install_packages()

        except ProgrammingError:
            self.logger.error("Could not establish connection to database. Please recheck your credentials!")

        except InterfaceError:
            self.logger.error("Database is not available at the moment!")

        except Exception as e:
            raise SQLExporterError(f"Could not establish connection to database. Reason: \n{e}")

        self.logger.info(f"Connection to database '{self.database}' with user '{self.user}' established")
        self.logger.info("Connection ready to export data")

        return engine

    @contextmanager
    def __get_session(self):
        """
        Context manager to handle sessions connecting to the database.
        """
        try:
            session = Session(bind=self.engine)
        except self.SQL_ERRORS:
            session = Session(bind=self.__create_sql_engine())
        try:
            yield session
        finally:
            session.close()

    @validate_arguments
    def get_contracts(self,
                      as_dataframe: bool = True,
                      **kwargs) -> pd.DataFrame:
        """
        Exports contracts from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. revisions='<> 0').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments:
        exchange, contract_id, product, type, undrlng_contracts, name, delivery_start, delivery_end, delivery_areas,
        predefined, duration, delivery_units

        Args:
            as_dataframe (bool): If False -> returns list
            **kwargs: any additional fields of SQL table

        Returns:
            list/ DataFrame: SQL query
        """
        allowed_kwargs = ["name", "delivery_areas", "delivery_start", "delivery_end", "delivery_areas", "type",
                          "predefined", "duration", "delivery_units", "contract_id", "exchange", "product",
                          "undrlng_contracts"]

        sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

        with self.__get_session() as session:
            # noinspection SqlResolve,SqlNoDataSourceInspection
            result = session.execute(f"SELECT * FROM contracts{sql_params}").fetchall()

        if as_dataframe:
            output = pd.DataFrame(result)
            output = output.rename(
                columns={0: 'exchange', 1: 'contract_id', 2: 'product', 3: 'type', 4: 'undrlng_contracts',
                         5: 'name', 6: 'delivery_start', 7: 'delivery_end', 8: 'delivery_areas',
                         9: 'predefined', 10: 'duration', 11: 'delivery_units', 12: 'details'})
            return output

        return result

    @validate_arguments
    def get_contract_ids(self,
                         time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                         time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                         delivery_area: str = Field(description="EIC-code of delivery area"),
                         contract_time: str = "all",
                         exchange: str = "epex",
                         as_list: bool = False) -> dict[str, list[str]]:
        """
            Returns dictionary of contract IDs in a format compatible with backtesting pipeline.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            delivery_area (str): EIC-Code
            contract_time (str): all, hourly, half-hourly or quarter-hourly
            exchange (str): Name of exchange in lowercase
            as_list (bool): True if output should be list of contract IDs

        Returns:
            dict{key: (list[str])}: Dictionary of Contract IDs
        """
        del_units = {"hourly": 1, "half-hourly": 0.5, "quarter-hourly": 0.25}

        if (del_units := del_units.get(contract_time)):
            sql_addition = f" AND delivery_units = {del_units}"
        else:
            sql_addition = ""

        if not isinstance(time_from, datetime) or not isinstance(time_till, datetime):
            raise SQLExporterError("Please use datetime format for time_from & time_till!")

        with self.__get_session() as session:
            # noinspection SqlResolve,SqlNoDataSourceInspection
            result = session.execute(f"SELECT delivery_start, delivery_end, contract_id FROM contracts "
                                     f"WHERE delivery_start >= '{time_from}' "
                                     f"AND delivery_end <= '{time_till}' "
                                     f"AND delivery_areas LIKE '%{delivery_area}%' "
                                     f"AND product IN {PRODUCTS[contract_time]} "
                                     f"AND exchange = '{exchange}'" + sql_addition).fetchall()
            if not result:
                # noinspection SqlResolve,SqlNoDataSourceInspection
                result = session.execute(f"SELECT delivery_start, delivery_end, contract_id FROM contracts "
                                         f"WHERE delivery_start >= '{time_from}' "
                                         f"AND delivery_end <= '{time_till}' "
                                         f"AND product IN {PRODUCTS[contract_time]} "
                                         f"AND exchange = '{exchange}'" + sql_addition).fetchall()

        if not as_list:
            contract_ids = {(i[0].replace(tzinfo=tzutc()), i[1].replace(tzinfo=tzutc())): [] for i in result}
            for i in result:
                contract_ids[(i[0].replace(tzinfo=tzutc()), i[1].replace(tzinfo=tzutc()))].append(i[2])

            # Quality Check
            if not all(i for i in contract_ids.values()):
                raise SQLExporterError("There is no contract data for the specified timeframe!")
        else:
            contract_ids = [i for i in result]

        self.logger.info("Successfully exported contract ids")
        return contract_ids

    @validate_arguments
    def get_public_trades(self,
                          as_dataframe: bool = True,
                          delivery_area: list[str] = None,
                          exchange: str = "epex",
                          use_cached_data: bool = False,
                          caching: bool = False,
                          gzip_files: bool = True,
                          as_csv: bool = False,
                          **kwargs) -> Union[pd.DataFrame, dict[str, pd.DataFrame]]:
        """
        Exports trades from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. price='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments (kwargs):
        price, quantity, prc_x_qty, exchange, contract_id, trade_id, exec_time, api_timestamp, self_trade

        Args:
            as_dataframe (bool): If False -> returns list
            delivery_area (list): List of EIC Area Codes for Delivery Areas
            exchange (str): Exchange of requested data
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON
            **kwargs: any additional fields of SQL table

        Returns:
            list/ DataFrame: SQL query
        """
        if as_dataframe and len(delivery_area) > 1:
            raise ValueError("Please only give one delivery area when loading data as dataframes")

        trades = {}

        if use_cached_data and as_dataframe and (contract_ids := kwargs.get("contract_id")):
            missing_contracts = {}

            for key, value in tqdm(contract_ids.items(), desc="Loading Cached Trades", unit="time periods", leave=False):
                filepath = _get_file_cachepath(None, key, delivery_area[0], exchange)
                tmp_df = None

                for i in [".json.gz", ".json"]:
                    if Path(f"__pb_cache__/{filepath}_trades{i}").exists():
                        tmp_df = pd.read_json(f"__pb_cache__/{filepath}_trades{i}", dtype=False)

                if isinstance(tmp_df, pd.DataFrame):
                    tmp_df['api_timestamp'] = pd.to_datetime(tmp_df['api_timestamp'])
                    tmp_df['exec_time'] = pd.to_datetime(tmp_df['exec_time'])
                    tmp_df = tmp_df.astype({"price": "float64", "trade_id": "str", "contract_id": "str"})
                    for i in ["price", "quantity"]:
                        tmp_df[i] = round(tmp_df[i], 2)

                    # Filter out any contract IDs that are not in value
                    trades[key] = tmp_df.loc[tmp_df.contract_id.isin(value)]

                else:
                    # Save Missing Contract IDs
                    missing_contracts[key] = value

            kwargs["contract_id"] = missing_contracts if missing_contracts else contract_ids

        if (contract_ids := kwargs.get("contract_id")) is None or isinstance(contract_ids, dict) and len(
                contract_ids) > 0:
            allowed_kwargs = ["price", "quantity", "prc_x_qty", "exchange", "contract_id", "trade_id", "exec_time",
                              "api_timestamp", "self_trade"]

            sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

            if delivery_area:
                for i in delivery_area:
                    sql_params += f" {'AND' if 'WHERE' in sql_params else 'WHERE'} (buy_delivery_area = '{i}' OR sell_delivery_area = '{i}')"

            with self.__get_session() as session:
                # noinspection SqlResolve,SqlNoDataSourceInspection
                if not (result := session.execute(f"SELECT * FROM public_trades{sql_params}").fetchall()):
                    raise SQLExporterError("There is no trade data for the specified timeframe!")
        else:
            result = None

        if as_dataframe:
            if result:
                output = pd.DataFrame(result)
                if not output.empty:
                    output = output.rename(columns={0: 'exchange', 1: 'contract_id', 2: 'trade_id', 3: 'api_timestamp',
                                                    4: 'exec_time', 5: 'buy_delivery_area', 6: 'sell_delivery_area',
                                                    7: 'price', 8: 'quantity', 9: 'prc_x_qty', 10: "currency",
                                                    11: 'self_trade'})

                    output['api_timestamp'] = pd.to_datetime(output['api_timestamp'], utc=True)
                    output['exec_time'] = pd.to_datetime(output['exec_time'], utc=True)
                    trades |= self.__convert_dataframe("trades", output)

            # Caching
            if caching:
                _cache_data("trades", trades, delivery_area[0], api_client=None, gzip_files=gzip_files, as_csv=as_csv,
                            exchange=exchange)

            self.logger.info("Successfully exported trades")
            return trades

        self.logger.info("Successfully exported trades")

        return result

    @validate_arguments
    def get_contract_history(self,
                             as_dataframe: bool = True,
                             delivery_area: list[str] = None,
                             exchange: str = "epex",
                             use_cached_data: bool = False,
                             caching: bool = False,
                             gzip_files: bool = True,
                             as_csv: bool = False,
                             **kwargs) -> Union[pd.DataFrame, dict[str, pd.DataFrame]]:
        """
        Exports contract revisions from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. best_bid='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments:
        exchange, contract_id, exchange, delivery_area, revision_no, as_of, best_bid, best_bid_qty, best_ask,
        best_ask_qty, vwap, high, low, last_price, last_qty, last_trade_time, volume, delta

        Args:
            as_dataframe (bool): If False -> returns list
            delivery_area (list): List of EIC Area Codes for Delivery Areas
            exchange (str): Exchange of requested data
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON
            **kwargs: any additional fields of SQL table

        Returns:
            list/ DataFrame: SQL query
        """
        orders = {}
        missing_contracts = {}

        if as_dataframe and len(delivery_area) > 1:
            raise ValueError("Please only give one delivery area when loading data as dataframes")

        if use_cached_data and as_dataframe and (contract_ids := kwargs.get("contract_id")):
            for key, value in contract_ids.items():
                filepath = _get_file_cachepath(None, key, delivery_area[0], exchange)
                tmp_df = None

                for i in [".json.gz", ".json"]:
                    if Path(f"./__pb_cache__/{filepath}_ordhist{i}").exists():
                        tmp_df = pd.read_json(f"./__pb_cache__/{filepath}_ordhist{i}", dtype=False,
                                              convert_dates=False)

                if isinstance(tmp_df, pd.DataFrame):
                    tmp_df['as_of'] = pd.to_datetime(tmp_df['as_of'])

                    cols = {"internal_trades": "object", "contract_id": "str", "auction_price": "float64"}
                    cols = {k: v for k, v in cols.items() if k in tmp_df.columns}
                    tmp_df = tmp_df.astype(cols, errors='ignore')
                    for i in ["best_bid_price", "best_bid_quantity", "best_ask_price", "best_ask_quantity",
                              "last_price",
                              "last_quantity", "total_quantity", "high", "low", "vwap"]:
                        try:
                            tmp_df[i] = round(tmp_df[i], 2)
                        except (TypeError, KeyError):
                            pass

                    if "orders" in tmp_df.columns:
                        order_list = tmp_df.orders.tolist()
                        for order_type in ["bid", "ask"]:
                            for i in order_list:
                                if order_type in i and i[order_type]:
                                    for x in i[order_type]:
                                        for param in ["quantity", "price"]:
                                            x[param] = round(x[param], 2)
                                        try:
                                            x["order_entry_time"] = datetime.strptime(x["order_entry_time"],
                                                                                      "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                                                tzinfo=tzutc())
                                        except ValueError:
                                            x["order_entry_time"] = datetime.strptime(x["order_entry_time"],
                                                                                      "%Y-%m-%dT%H:%M:%SZ").replace(
                                                microsecond=0, tzinfo=tzutc())
                        tmp_df["orders"] = order_list

                    # Filter out any contract IDs that are not in value
                    orders[key] = tmp_df.loc[tmp_df.contract_id.isin(value)]
                else:
                    # Save Missing Contract IDs
                    missing_contracts[key] = value

            kwargs["contract_id"] = missing_contracts

        if (contract_ids := kwargs.get("contract_id")) is None or isinstance(contract_ids, dict) and len(
                contract_ids) > 0:
            allowed_kwargs = ["exchange", "contract_id", "delivery_area", "revision_no", "as_of", "best_bid",
                              "best_bid_qty", "best_ask", "best_ask_qty", "vwap", "high", "low", "last_price",
                              "last_qty", "last_trade_time", "volume", "delta"]

            sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

            if delivery_area and not as_dataframe and len(delivery_area) > 1:
                sql_params += f" AND delivery_area IN {tuple(delivery_area)}"
            else:
                sql_params += f" AND delivery_area = '{delivery_area[0]}'"

            with self.__get_session() as session:
                # noinspection SqlResolve,SqlNoDataSourceInspection
                if not (result := session.execute(f"SELECT * FROM contract_revisions{sql_params}").fetchall()):
                    raise SQLExporterError("There is no order data for the specified timeframe!")
        else:
            result = None

        if as_dataframe:
            if result:
                output = pd.DataFrame(result)
                if not output.empty:
                    output = output.rename(
                        columns={0: 'exchange', 1: 'contract_id', 2: 'delivery_area', 3: 'revision_no',
                                 4: 'as_of', 5: 'best_bid', 6: 'best_bid_qty', 7: 'best_ask',
                                 8: 'best_ask_qty', 9: 'vwap', 10: 'high', 11: 'low', 12: 'last_price',
                                 13: 'last_qty', 14: "last_trade_time", 15: 'volume', 16: 'delta',
                                 17: 'bids', 18: 'asks'})
                orders |= self.__convert_dataframe("orders", output)

            # Caching
            if caching:
                _cache_data("ordhist", orders, delivery_area[0], api_client=None, gzip_files=gzip_files, as_csv=as_csv,
                            exchange=exchange)

            self.logger.info("Successfully exported contract history")
            return orders

        self.logger.info("Successfully exported contract history")

        return result

    @validate_arguments
    def get_own_trades(self,
                       delivery_area: list[str] = None,
                       as_dataframe: bool = True,
                       as_objects: bool = False,
                       **kwargs) -> Union[pd.DataFrame, list[Trade]]:
        """
        Exports Own Trades from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. position_short='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments (kwargs):
        exchange, contract_id, contract_name, prod, delivery_start, delivery_end, trade_id, api_timestamp, exec_time,
        buy, sell, price, quantity, state, buy_delivery_area, sell_delivery_area, buy_order_id, buy_clOrderId, buy_txt,
        buy_user_code, buy_member_id, buy_aggressor_indicator, buy_portfolio_id, sell_order_id, sell_clOrderId,
        sell_txt, sell_user_code, sell_member_id, sell_aggressor_indicator, sell_portfolio_id, self_trade, pre_arranged,
        pre_arrange_type

        Args:
            delivery_area (tuple[str]): Multiple delivery areas inside a tuple. Single del. area can be passed as a string
            as_dataframe (bool): True if output should be DataFrame
            as_objects (bool): True if output should be list of OwnTrades
            **kwargs: any additional fields of SQL table

        Returns:
            list: SQL query
        """

        allowed_kwargs = ["exchange", "contract_id", "contract_name", "prod", "delivery_start", "delivery_end",
                          "trade_id", "api_timestamp",
                          "exec_time", "buy", "sell", "price", "quantity", "state", "buy_delivery_area",
                          "sell_delivery_area", "buy_order_id",
                          "buy_clOrderId", "buy_txt", "buy_user_code", "buy_member_id", "buy_aggressor_indicator",
                          "buy_portfolio_id",
                          "sell_order_id", "sell_clOrderId", "sell_txt", "sell_user_code", "sell_member_id",
                          "sell_aggressor_indicator",
                          "sell_portfolio_id", "self_trade", "pre_arranged", "pre_arrange_type", "customer"]

        sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

        if delivery_area:
            for i in delivery_area:
                sql_params += f" AND (buy_delivery_area = '{i}' OR sell_delivery_area = '{i}')"

        with self.__get_session() as session:
            # noinspection SqlResolve,SqlNoDataSourceInspection
            result = session.execute(f"SELECT * FROM own_trades{sql_params}").fetchall()

        self.logger.info("Successfully exported own trades")

        # Convert data back to Trade objects
        if result and as_objects:
            own_trades = [Trade(exchange=i[0],
                                contract_id=i[1],
                                contract_name=i[2],
                                prod=i[3],
                                delivery_start=i[4],
                                delivery_end=i[5],
                                trade_id=i[6],
                                api_timestamp=i[7],
                                exec_time=i[8],
                                buy=i[9],
                                sell=i[10],
                                price=i[11],
                                quantity=i[12],
                                delivery_area=i[13],
                                state=i[14],
                                buy_delivery_area=i[15],
                                sell_delivery_area=i[16],
                                buy_order_id=i[17],
                                buy_cl_order_id=i[18],
                                buy_txt=i[19],
                                buy_user_code=i[20],
                                buy_member_id=i[21],
                                buy_aggressor_indicator=i[22],
                                buy_portfolio_id=i[23],
                                sell_order_id=i[24],
                                sell_cl_order_id=i[25],
                                sell_txt=i[26],
                                sell_user_code=i[27],
                                sell_member_id=i[28],
                                sell_aggressor_indicator=i[29],
                                sell_portfolio_id=i[30],
                                self_trade=i[31],
                                pre_arranged=i[32],
                                pre_arrange_type=i[33])
                          for i in result]
            return own_trades

        if as_dataframe:
            return pd.DataFrame(result)

        return result

    @validate_arguments
    def get_internal_trades(self,
                            delivery_area: tuple[str] = None,
                            as_dataframe: bool = True,
                            as_objects: bool = False,
                            **kwargs) -> Union[pd.DataFrame, list[InternalTrade]]:
        """
        Exports Internal Trades from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. position_short='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments (kwargs):
        exchange, contract_id, contract_name, prod, delivery_start, delivery_end, internal_trade_id, api_timestamp,
        exec_time, price, quantity, state, buy_delivery_area, sell_delivery_area, buy_order_id, buy_clOrderId, buy_txt,
        buy_aggressor_indicator, buy_portfolio_id, sell_order_id, sell_clOrderId, sell_txt, sell_aggressor_indicator,
        sell_portfolio_id

        Args:
            delivery_area (tuple[str]): Multiple delivery areas inside a tuple. Single del. area can be passed as a string
            as_dataframe (bool): True if output should be DataFrame
            as_objects (bool): True if output should be list of InternalTrades
            **kwargs: any additional fields of SQL table

        Returns:
            list: SQL query
        """
        allowed_kwargs = ["exchange", "contract_id", "contract_name", "prod", "delivery_start", "delivery_end",
                          "internal_trade_id", "api_timestamp", "exec_time", "price", "quantity", "state",
                          "buy_delivery_area", "sell_delivery_area", "buy_order_id", "buy_clOrderId", "buy_txt",
                          "buy_aggressor_indicator", "buy_portfolio_id", "sell_order_id", "sell_clOrderId", "sell_txt",
                          "sell_aggressor_indicator", "sell_portfolio_id", "customer"]

        sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

        if delivery_area:
            for i in delivery_area:
                sql_params += f" AND (buy_delivery_area = '{i}' OR sell_delivery_area = '{i}')"

        with self.__get_session() as session:
            # noinspection SqlResolve,SqlNoDataSourceInspection
            result = session.execute(f"SELECT * FROM internal_trades{sql_params}").fetchall()

        self.logger.info("Successfully exported internal trades")

        # Convert data back to InternalTrade objects
        if result and as_objects:
            internal_trades = [InternalTrade(exchange=i[0],
                                             contract_id=i[1],
                                             contract_name=i[2],
                                             prod=i[3],
                                             delivery_start=i[4],
                                             delivery_end=i[5],
                                             internal_trade_id=i[6],
                                             api_timestamp=i[7],
                                             exec_time=i[8],
                                             price=i[9],
                                             quantity=i[10],
                                             buy_delivery_area=i[11],
                                             sell_delivery_area=i[12],
                                             buy_order_id=i[13],
                                             buy_cl_order_id=i[14],
                                             buy_txt=i[15],
                                             buy_aggressor_indicator=i[16],
                                             buy_portfolio_id=i[17],
                                             sell_order_id=i[18],
                                             sell_cl_order_id=i[19],
                                             sell_txt=i[20],
                                             sell_aggressor_indicator=i[21],
                                             sell_portfolio_id=i[22])
                               for i in result]
            return internal_trades

        if as_dataframe:
            return pd.DataFrame(result)

        return result

    @validate_arguments
    def get_signals(self,
                    time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                    time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                    as_dataframe: bool = True,
                    as_objects: bool = False,
                    **kwargs) -> Union[pd.DataFrame, list[Signal]]:
        """
        Exports signals from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. position_short='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments:
        id, source, received_at, revision, delivery_areas, portfolio_ids, tenant_id, position_short,
        position_long, value

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            as_dataframe (bool): True if output should be DataFrame
            as_objects (bool): True if output should be list of Signals
            **kwargs: any additional fields of SQL table

        Returns:
            list: SQL query
        """
        allowed_kwargs = ["id", "source", "received_at", "revision", "delivery_areas", "portfolio_ids", "tenant_id",
                          "position_short", "position_long", "value", "customer"]

        sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)
        sql_op = "AND" if sql_params else "WHERE"

        with self.__get_session() as session:
            # noinspection SqlResolve,SqlNoDataSourceInspection
            result = session.execute(f"SELECT * FROM signals{sql_params} "
                                     f"{sql_op} delivery_start >= '{time_from}' "
                                     f"AND delivery_end <= '{time_till}'").fetchall()

        self.logger.info("Successfully exported signals")

        # Convert data back to InternalTrade objects
        if result and as_objects:
            signals = [Signal(id=i[0],
                              source=i[1],
                              received_at=i[2],
                              revision=i[3],
                              delivery_start=i[4],
                              delivery_end=i[5],
                              portfolio_ids=i[6],
                              tenant_id=i[7],
                              position_short=i[8],
                              position_long=i[9],
                              value=i[10])
                       for i in result]

            return signals

        if as_dataframe:
            return pd.DataFrame(result)

        return result

    @validate_arguments
    def send_raw_sql(self,
                     sql_statement: str):
        """
        Function allows for raw SQL queries to be sent to the database.

        Args:
            sql_statement (str): SQL query

        Returns:

        """
        with self.__get_session() as session:
            try:
                result = session.execute(sql_statement).fetchall()
            except self.SQL_ERRORS as e:
                return self.logger.error(e)
        return result

    @staticmethod
    def __handle_sql_args(kwargs,
                          allowed_kwargs: list[str]) -> str:
        """
        Handles incoming arguments by adjusting them to be compatible with SQL.

        Args:
            kwargs: **kwargs of export functions
            allowed_kwargs (list[str]): list of allowed kwargs

        Returns:
            str: SQL request
        """
        if not all(arg for arg in kwargs.values()):
            raise SQLExporterError("Some of your input values are invalid or empty!")
        sql_params = ""
        operators = ["LIKE", "BETWEEN", "<", "<=", ">", ">=", "<>"]

        for keyword, argument in kwargs.items():
            op = "="
            sql_statement = "WHERE" if sql_params == "" else "AND"

            if keyword not in allowed_kwargs:
                raise SQLExporterError(f"{keyword} not in allowed keywords. Allowed keywords: {allowed_kwargs}")
            else:
                if isinstance(argument, str):
                    # Check For SQL Commands Or Mathematical Operators
                    if any(x in argument for x in operators):
                        if len(argument.split(" ")) > 2:
                            op = argument.split(" ")[0]
                            argument = argument.replace(f"{op} ", "")
                        else:
                            op, argument = argument.split(" ")
                        if op == "LIKE":
                            argument = f"%{argument}%"
                        if op == "BETWEEN":
                            if " AND " not in argument:
                                raise SQLExporterError(
                                    f"Your input for {keyword} does not conform to the guidelines. Please revise")
                            a1, a2 = argument.split(" AND ")
                            argument = f"'{a1}' AND '{a2}'"
                        try:
                            datetime.strptime(argument, DATE_YMD_TIME_HMS)
                        except:  # noqa: E722
                            pass
                elif isinstance(argument, tuple):
                    if len(argument) == 1:
                        argument = argument[0]
                    else:
                        op = "IN"
                elif isinstance(argument, list):
                    for nr, element in enumerate(argument):
                        if not nr:
                            if element == argument[-1]:
                                sql_params += f" {sql_statement} ({keyword} LIKE '%{element}%')"
                            else:
                                sql_params += f" {sql_statement} ({keyword} LIKE '%{element}%'"
                        elif element == argument[-1]:
                            sql_params += f" OR {keyword} LIKE '%{element}%')"
                        else:
                            sql_params += f" OR {keyword} LIKE '%{element}%'"
                    continue
                elif isinstance(argument, dict):
                    op = "IN"
                    temp_list = [i for x in argument.values() for i in x]
                    argument = tuple(temp_list)
                    if len(argument) == 1:
                        argument = str(argument[0])
                        op = "="
                try:
                    if keyword == "contract_id" and isinstance(argument, str):
                        raise Exception

                    if not isinstance(argument, tuple) and keyword != "contract_id":
                        argument = float(argument)
                    sql_params += f" {sql_statement} {keyword} {op} {argument}"

                except:  # noqa: E722
                    if isinstance(argument, str) and len(argument.split(" AND ")) > 1:
                        sql_params += f" {sql_statement} {keyword} {op} {argument}"
                    else:
                        sql_params += f" {sql_statement} {keyword} {op} '{argument}'"

        return sql_params

    def __convert_dataframe(self,
                            df_type: str,
                            dataframe: pandas_DataFrame) -> dict[str, pd.DataFrame]:
        """
        Function to convert dataframe to required format to be processed by backtesting data pipeline.

        Args:
            df_type (str): orders/trades/orderbooks
            dataframe (DataFrame): DataFrame containing exported Data

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        output = {}

        contract_ids = dataframe.contract_id.unique().tolist()
        contracts = self.get_contracts(contract_id=contract_ids)

        if df_type == "trades":
            dataframe = dataframe.astype({'price': 'float', 'quantity': 'float'})

        elif df_type == "orders":
            dataframe["bids"] = [json.loads(i) if i else None for i in dataframe.bids.tolist()]
            dataframe["asks"] = [json.loads(i) if i else None for i in dataframe.asks.tolist()]

        for row_nr, row_id in enumerate(contracts.contract_id):
            key = (contracts.iloc[row_nr].delivery_start.replace(tzinfo=tzutc()).to_pydatetime(),
                   contracts.iloc[row_nr].delivery_end.replace(tzinfo=tzutc()).to_pydatetime())

            if key not in [*output]:
                output[key] = dataframe[dataframe["contract_id"] == row_id]
            else:
                output[key] = pd.concat([output[key].copy(), dataframe[dataframe["contract_id"] == row_id]])

        return output

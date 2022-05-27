from datetime import timezone

import pandas as pd
import numpy as np

from powerbot_backtesting.exceptions import NotInCacheError
from powerbot_backtesting.utils.constants import DATE_YMD_TIME_HM


def _process_orderbook(key: str,
                       value: pd.DataFrame,
                       directory: str,
                       timesteps: int,
                       time_unit: str,
                       use_cached_data: bool,
                       shortest_interval: bool = True,
                       ):
    """
    Function to process single order book. Return value is appended to collection of order books.

    Returns:
        pd.Dataframe: single order book
    """
    # Setup Parameters

    file_name = (f"{key[0].strftime(DATE_YMD_TIME_HM).replace(':', '-')} - "
                 f"{key[1].strftime(DATE_YMD_TIME_HM).replace(':', '-')}")
    directory = directory.split('/')
    directory = '/'.join(directory)

    try:
        if not use_cached_data:
            raise NotInCacheError("Not loading from cache")
        # Check If Data Already Cached
        time_interval = f"{timesteps}{time_unit[0]}" if not shortest_interval else "shortest"
        orders_df = pd.read_pickle(f"{directory}/{file_name}_orderbook_{time_interval}.p")

    except (NotInCacheError, FileNotFoundError):

        if time_unit == "minutes":
            time_unit_pd = "T"
        elif time_unit == "hours":
            time_unit_pd = "H"
        else:
            time_unit_pd = "S"

        orderdata = value
        orderdata.sort_values(by="as_of", inplace=True, ignore_index=True)

        orders_list_temp = []

        if "orders" in orderdata.columns:
            first_valid_entry = orderdata[["best_bid_price", "best_ask_price"]].notna().idxmax().min()
        else:
            first_valid_entry = orderdata[["best_bid", "best_ask"]].notna().idxmax().min()

        if shortest_interval:
            timesteps_range = orderdata.iloc[first_valid_entry:].as_of
            timesteps_range.reset_index(inplace=True, drop=True)
        else:
            if "orders" in orderdata.columns:
                timesteps_range = pd.date_range(
                    start=orderdata.iloc[first_valid_entry].as_of.ceil(
                        freq=f"{timesteps}{time_unit_pd}"),
                    end=orderdata.as_of[orderdata.shape[0] - 1].ceil(
                        freq=f"{timesteps}{time_unit_pd}"),
                    freq=f"{timesteps}{time_unit_pd}")

            else:
                timesteps_range = pd.date_range(
                    start=orderdata.iloc[first_valid_entry].as_of.ceil(
                        freq=f"{timesteps}{time_unit_pd}"),
                    end=orderdata.as_of[orderdata.shape[0] - 1].ceil(
                        freq=f"{timesteps}{time_unit_pd}"),
                    freq=f"{timesteps}{time_unit_pd}")

        timesteps_range_unique = timesteps_range.unique()

        for timestep in range(timesteps_range_unique.shape[0]):
            if shortest_interval:
                orderdata_red = orderdata[orderdata.as_of == timesteps_range_unique[timestep]]
            else:
                if timestep == 0:
                    orderdata_red = orderdata[
                        orderdata.as_of < timesteps_range_unique[timestep]]

                else:
                    orderdata_red = orderdata[
                        (orderdata.as_of >= timesteps_range_unique[timestep - 1]) & (
                            orderdata.as_of < timesteps_range_unique[timestep])]

            try:
                orders = pd.DataFrame(orders_list_temp[timestep - 1].copy())
                orders.dropna(inplace=True)
                orders.order_id = orders.order_id.astype(str)
                orders.set_index("order_id", inplace=True, drop=False)

            except IndexError:
                orders = pd.DataFrame(
                    columns=["order_id", "price", "quantity", "contract_id",
                             "order_entry_time", "type", "time_step"])
                orders.set_index("order_id", inplace=True, drop=False)
            for order_key in range(orderdata_red.shape[0]):
                row = orderdata_red.iloc[order_key]
                if "orders" in row:
                    if row.orders["delta"]:
                        orders = orders
                    else:
                        orders = pd.DataFrame(
                            columns=["order_id", "price", "quantity", "contract_id",
                                     "order_entry_time", "type", "time_step"])
                        orders.order_id = orders.order_id.astype(str)
                        orders.set_index("order_id", inplace=True, drop=False)
                    for side in ["ask", "bid"]:
                        if pd.isnull([row.orders[f"{side}"]]).any():
                            continue
                        else:
                            for item in row.orders[f"{side}"]:
                                if str(item["order_id"]) in orders.index:
                                    if item["quantity"] == 0:

                                        orders.drop(str(item["order_id"]),
                                                    inplace=True)
                                        orders.set_index("order_id", inplace=True, drop=False)

                                    else:
                                        orders.loc[str(item["order_id"]), "quantity"] = item["quantity"]
                                        orders.set_index("order_id", inplace=True, drop=False)

                                else:
                                    if item["quantity"] != 0:
                                        item_df = pd.DataFrame(
                                            [[str(item["order_id"]), item["price"],
                                              item["quantity"], item["contract_id"], item["order_entry_time"], side]])

                                        item_df["time_step"] = timesteps_range_unique[timestep]

                                        item_df.columns = ["order_id", "price", "quantity", "contract_id",
                                                           "order_entry_time", "type", "time_step"]
                                        item_df.order_id = item_df.order_id.astype(str)
                                        item_df.set_index("order_id", inplace=True, drop=False)

                                        orders = pd.concat([orders, item_df], ignore_index=True)
                                        orders.order_id = orders.order_id.astype(str)
                                        orders.set_index("order_id", inplace=True, drop=False)
                else:
                    if row.delta:
                        orders = orders
                    else:
                        orders = pd.DataFrame(
                            columns=["order_id", "price", "quantity", "contract_id",
                                     "order_entry_time", "type", "time_step"])
                        orders.order_id = orders.order_id.astype(str)
                        orders.set_index("order_id", inplace=True, drop=False)
                    for side in ["asks", "bids"]:
                        if pd.isnull([row[f"{side}"]]).any():
                            continue

                        else:
                            for item in row[f"{side}"]:
                                if str(item["order_id"]) in orders.index:
                                    if item["quantity"] == 0:
                                        orders.drop(str(item["order_id"]),
                                                    inplace=True)
                                        orders.set_index("order_id", inplace=True, drop=False)

                                    else:
                                        orders.loc[str(item["order_id"]), "quantity"] = item["quantity"]
                                        orders.set_index("order_id", inplace=True, drop=False)

                                else:
                                    if item["quantity"] != 0:
                                        item_df = pd.DataFrame([
                                            [str(item["order_id"]), item["price"],
                                             item["quantity"], item["contract_id"], item["order_entry_time"],
                                             side[:-1]]])

                                        item_df["time_step"] = timesteps_range_unique[timestep]
                                        item_df.columns = ["order_id", "price", "quantity", "contract_id",
                                                           "order_entry_time", "type", "time_step"]
                                        item_df.order_id = item_df.order_id.astype(str)
                                        item_df.set_index("order_id", inplace=True, drop=False)
                                        orders = pd.concat([orders, item_df], ignore_index=True)
                                        orders.order_id = orders.order_id.astype(str)
                                        orders.set_index("order_id", inplace=True, drop=False)

            if orders.shape[0] == 0:
                orders = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
                                        timesteps_range_unique[timestep]]],
                                      columns=["order_id", "price", "quantity", "contract_id",
                                               "order_entry_time", "type", "time_step"])

            orders.time_step = timesteps_range_unique[timestep]
            orders = orders.sort_values("order_entry_time")
            orders_list_temp.append(orders)

        orders_df = pd.concat(orders_list_temp)
        orders_df["delivery_start"] = key[0]
        orders_df["delivery_end"] = key[1]
        orders_df.set_index(["delivery_start", "delivery_end", "time_step"], inplace=True, drop=False)
        orders_df = orders_df[["order_id", "price", "quantity", "contract_id", "order_entry_time", "type", "time_step"]]
        orders_df.index.names = ["delivery_start", "delivery_end", "timestep"]
        orders_df["price"] = orders_df.price.astype(float)
        orders_df["quantity"] = orders_df.quantity.astype(float)

    return orders_df


def _orderbook_data_transformation(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Function transforms data in passed dataframe to be compatible with process_orderbooks function

    Args:
        orders (pd.DataFrame): DataFrame containing order data

    Returns:
        pd.Dataframe
    """
    if not isinstance(orders, pd.DataFrame):
        return pd.DataFrame()

    bids_asks = []
    # Processing
    if "orders" in orders.columns:
        orders_all = orders["orders"].to_list()
        dates_all = [str(i) for i in orders["as_of"].to_list()]
        deltas = orders.delta.to_list() if "delta" in orders.columns else [1 for _ in range(len(dates_all))]
        for nr, val in enumerate(orders_all):
            for k, v in val.items():
                if v and k in ["ask", "bid"]:
                    for x in v:
                        x["as_of"] = dates_all[nr]
                        x["type"] = "bid" if k == "bid" else "ask"
                        x["delta"] = val.get("delta", deltas[nr])
                        bids_asks.append(x)

    else:
        for nr, row in orders.iterrows():
            for side in ["bids", "asks"]:
                if row[side] and not isinstance(row[side], float):
                    for entry in row[side]:
                        entry["order_id"] = str(entry["order_id"])
                        entry["type"] = side[:-1]
                        entry["as_of"] = row["as_of"].tz_convert(timezone.utc) if row["as_of"].tzinfo else row[
                            "as_of"].tz_localize(timezone.utc)
                        entry["delta"] = row["delta"]
                        bids_asks.append(entry)

    df_bid_asks = pd.DataFrame(bids_asks)
    df_bid_asks = df_bid_asks.drop(columns=["exe_restriction", "delivery_area", "order_entry_time"],
                                   errors="ignore")
    return df_bid_asks


def _delta_filter(orderbook: pd.DataFrame, orders_to_delete: set) -> pd.DataFrame:
    """
    Function filters dataframe by orders that are not delta reports. If delta is False, all orders before this order have to be deleted.

    Since delta: false is assigned to a revision of a contract, it can contain more than just one order. Therefore, all orders in a delta: false
    revision have that flag assigned. This function takes this situation in account, loading the last delta: false and going back until the space
    between two orders that have delta: false is bigger than 1.

    Args:
        orderbook (pd.Dataframe): Preliminary order book
        orders_to_delete (set): Set of order IDs that need to be purged from future order books

    Returns:
        pd.Dataframe
    """
    if not (ind := orderbook[(~orderbook.delta) | (orderbook.delta == 0)].index).empty:
        original = orderbook.copy(deep=True)
        last_delta = ind[-1]

        for i in ind[::-1]:
            if i == (last_delta - 1) or i == last_delta:
                last_delta = i
            else:
                break

        orderbook = orderbook.loc[orderbook.index >= last_delta].drop(columns=["delta"])
        orders_to_delete.update(original.loc[~original.order_id.isin(orderbook.order_id)].order_id.tolist())

        return orderbook

    return orderbook.drop(columns=["delta"])


def _process_multiple(contract_hist_data,
                      new_dir,
                      timesteps,
                      time_unit,
                      use_cached_data,
                      shortest_interval):
    result = {}
    for nr, (key, value) in enumerate(contract_hist_data.items()):
        result = _process_orderbook(key, value, str(new_dir), timesteps, time_unit,
                                    use_cached_data, shortest_interval)

    return result

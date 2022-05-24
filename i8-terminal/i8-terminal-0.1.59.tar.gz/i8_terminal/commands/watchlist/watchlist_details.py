from typing import Dict, List

import click
import investor8_sdk
from pandas import DataFrame
from rich.console import Console
from rich.table import Table

from i8_terminal.commands.watchlist import watchlist
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.config import USER_SETTINGS

from i8_terminal.types.user_watchlists_param_type import UserWatchlistsParamType  # isort:skip


def get_watchlist_df(name: str) -> DataFrame:
    watchlist_stocks: List[Dict[str, str]] = []
    watchlist = investor8_sdk.UserApi().get_watchlist_by_name_user_id(name=name, user_id=USER_SETTINGS.get("user_id"))
    all_stock_info = investor8_sdk.StockInfoApi().get_all_stock_info(market_index="")
    all_latest_prices = investor8_sdk.PriceApi().get_all_latest_prices()
    all_latest_daily_metrics = investor8_sdk.MetricsApi().get_all_latest_daily_metrics()
    for ticker in watchlist.tickers:
        latest_price = all_latest_prices[ticker]
        stock_info = all_stock_info[ticker]
        daily_metrics = all_latest_daily_metrics[ticker]
        watchlist_stocks.append(
            {
                "ticker": ticker,
                "company": stock_info.name,
                "exchange": stock_info.exchange,
                "latest_price": latest_price.latest_price,
                "change": latest_price.change_perc,
                "market_cap": daily_metrics.marketcap,
            }
        )
    return DataFrame(watchlist_stocks)


def render_watchlist_table(df: DataFrame) -> Table:
    target = "console"
    formatters = {
        "latest_price": get_formatter("price", target),
        "change": get_formatter("perc", target),
        "market_cap": get_formatter("price", target),
    }
    col_names = {
        "ticker": "Ticker",
        "company": "Company",
        "exchange": "Exchange",
        "latest_price": "Price",
        "change": "Change",
        "market_cap": "Market Cap",
    }
    df_formatted = format_df(df, col_names, formatters)
    return df2Table(df_formatted)


@watchlist.command()
@click.option(
    "--name",
    "-n",
    type=UserWatchlistsParamType(),
    required=True,
    help="Name of the watchlist you want to see more details.",
)
@pass_command
def details(name: str) -> None:
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_watchlist_df(name)
    table = render_watchlist_table(df)
    console.print(table)

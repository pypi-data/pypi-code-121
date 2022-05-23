import pandas as pd
import logging

log = logging.getLogger(__name__)


def move_market_ohlc_to_model_data(orig_data: pd.DataFrame, start: str, end: str):
    """
    to project ohlc data for specific time frame

    Args:
        orig_data: global market data
        start: start dt
        end: end dt

    Returns:
        stripped down data
    """

    log.info(f"Start date: {start}")
    log.info(f"End date: {end}")

    instances = orig_data[start:end]
    instances = instances[["Open", "High", "Low", "Close"]]

    return dict(
        instances=instances
    )

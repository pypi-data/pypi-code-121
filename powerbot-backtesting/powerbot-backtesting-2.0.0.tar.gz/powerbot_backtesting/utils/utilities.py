import certifi
import pandas as pd
from powerbot_client import ApiClient, Configuration
from pathlib import Path


def init_client(api_key: str, host: str) -> ApiClient:
    """
    Initializes PowerBot Client to enable data requests by the API.

    Args:
        api_key (str): API Key for PowerBot
        host (str): Host URL for PowerBot

    Returns:
        PowerBot ApiClient Object
    """
    config = Configuration(api_key={'api_key_security': api_key}, host=host, ssl_ca_cert=certifi.where())
    return ApiClient(config)


def generate_input_file(orderbooks: dict[str, pd.DataFrame]):
    """
    Generates a csv file to put positions and signals into to use with the BacktestingAlgo

    Args:
        orderbooks (dict{key: DataFrame}): Dictionary of order books

    Returns:
        csv file
    """
    # File creation
    # input_file = pd.DataFrame({"contract_id": [*orderbooks]})
    # input_file["position"] = ""
    # input_file.set_index("contract_id", inplace=True)
    orderbooks = orderbooks.reset_index().drop("timestep", axis=1)

    input_file = pd.DataFrame(columns=orderbooks.columns).set_index(["delivery_start", "delivery_end"])
    input_file = input_file.rename(columns={"quantity": "position"})
    input_file = input_file.rename(columns={"type": "side"})

    # Caching
    cache_path = Path("./__pb_cache__/analysis_input")
    cache_path.mkdir(parents=True, exist_ok=True)

    # File name
    f_count = 1
    while cache_path.joinpath(f"backtesting_input_{f_count}.csv").exists():
        f_count += 1
    input_file.to_csv(cache_path.joinpath(f"backtesting_input_{f_count}.csv"), sep=";")

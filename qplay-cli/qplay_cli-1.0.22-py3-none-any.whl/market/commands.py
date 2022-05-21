import click
from quantplay.service import market as market_service
import glob
import pandas as pd
from qplay_cli.utils.file_utils import FileUtils


@click.group()
def market():
    pass

def validate_interval(interval):
    if interval == None:
        print("--interval [5minute/15minute] argument is missing")
        print("For more info re-run the command using --help argument")
        exit(1)
    if interval not in ["5minute", "15minute"]:
        print("interval must be in [5minute/15minute]")
        exit(1)

def validate_datset(dataset):
    if dataset == None:
        print("--dataset [NSE_EQ/NSE_OPT] argument is missing")
        print("For more info re-run the command using --help argument")
        exit(1)

@market.command()
@click.option('--interval', default=None)
@click.option('--dataset', default=None)
def create_data(interval, dataset):
    validate_interval(interval)
    validate_datset(dataset)

    if dataset == "NSE_EQ":
        dataset_path = market_service.nse_equity_path
    elif dataset == "NSE_OPT":
        dataset_path = market_service.nse_opt_path
    else:
        print("Dataset must be [NSE_EQ/NSE_OPT]")
        exit(1)

    path = "{}minute/".format(dataset_path)

    stocks = [file.replace(path, '').replace('.csv', '') for file in glob.glob("{}*".format(path)) if 'csv' in file]
    interval_map = {
        "5minute" : "5min",
        "15minute" : "15min"
    }

    FileUtils.create_directory_if_not_exists("{}{}".format(dataset_path, interval))
    for stock in stocks:
        print("Processing {}".format(stock))
        df = pd.read_csv("{}{}.csv".format(path, stock))

        df["date"] = pd.to_datetime(df["date"])

        df = df.groupby(pd.Grouper(key='date', freq=interval_map[interval])).agg({
            "symbol": "first",
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last"
        })
        df.to_csv("{}{}/{}.csv".format(dataset_path, interval, stock))

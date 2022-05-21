import click
from qplay_cli.config.qplay_config import QplayConfig
from kiteconnect import KiteConnect
from qplay_cli.dataset.volume import Volume
from qplay_cli.broker.zerodha.z_broker import ZBroker

@click.group()
def broker():
    pass

@broker.command()
def generate_token():
    ZBroker().generate_token()
    
from qplay_cli.backtest.backtesting import Backtesting
import click

@click.group()
def backtest():
    pass

@backtest.command()
@click.option('--strategy', default=None)
def remote_backtest(strategy):
    if not strategy:
        raise Exception("must provide strategy")
    b = Backtesting()
    b.remote_backtest(strategy)
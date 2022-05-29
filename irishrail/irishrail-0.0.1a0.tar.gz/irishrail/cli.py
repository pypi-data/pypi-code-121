import click
import time
from rich.live import Live
from rich import print

from irishrail import commands


@click.group()
def cli():
    ...


@cli.command()
def stations():
    stations = commands.stations()
    print(stations)


@cli.command()
@click.option("-s", "--station")
@click.option("-f", "--follow", is_flag=True, default=False)
def live(station, follow):
    REFRESH_PER_SECOND = 30
    with Live(commands.live(station), refresh_per_second=REFRESH_PER_SECOND) as live:
        while follow:
            time.sleep(REFRESH_PER_SECOND)
            live.update(commands.live(station))


if __name__ == "__main__":
    cli()

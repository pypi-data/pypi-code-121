from datetime import date
import click
import pygdg.events as e
import pygdg.features as f

DEFAULT_DATE=str(date.today())
DEFAULT_PLAYERS=10
DEFAULT_DAYS=7
DEFAULT_SEED=0
DEFAULT_PLOT=False
DEFAULT_DEBUG=False

@click.group()
def main():
    pass

@main.command()
@click.option('--date', type=click.DateTime(formats=["%Y-%m-%d"]), default=DEFAULT_DATE, help='The acquisition starting date')
@click.option('--players', default=DEFAULT_PLAYERS, help='The number of daily acquired players')
@click.option('--days', default=DEFAULT_DAYS, help='The number of acquisition days')
@click.option('--seed', default=DEFAULT_SEED, help='The random seed')
@click.option('--plot/--no-plot', default=DEFAULT_PLOT, help='The plot flag')
@click.option('--debug/--no-debug', default=DEFAULT_DEBUG, help='The debug flag')
@click.argument('filename', default='events')
def events(filename, date, players, days, seed, plot, debug):
    e.generate(filename, date, players, days, seed, plot, debug)

@main.command()
@click.option('--seed', default=DEFAULT_SEED, help='The random seed')
@click.option('--debug/--no-debug', default=DEFAULT_DEBUG, help='The debug flag')
@click.option('--events', default='events', help='The name of the input events file')
@click.argument('filename', default='features')
def features(filename, events, seed, debug):
    f.generate(filename, events, seed, debug)

@main.command()
@click.option('--seed', default=DEFAULT_SEED, help='The random seed')
@click.option('--debug/--no-debug', default=DEFAULT_DEBUG, help='The debug flag')
@click.option('--events', default='events', help='The name of the input events file')
@click.argument('filename', default='metrics')
def metrics(filename, events, seed, debug):
    click.echo('no metrics yet!')

if __name__ == '__main__':
    main()
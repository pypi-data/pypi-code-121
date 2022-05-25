import click

class Logger:
    """Class description."""

    display = True

    @classmethod
    def write(cls, text: str):
        if Logger.display:
            click.echo(text)

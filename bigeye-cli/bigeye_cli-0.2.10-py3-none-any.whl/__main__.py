import typer

import bigeye_cli.__version__ as bigeye_cli_version
import bigeye_sdk.__version__ as bigeye_sdk_version
from bigeye_cli.deltas import deltas_commands
from bigeye_cli.workspace import workspace_commands
from bigeye_sdk.log import get_logger

from bigeye_cli.catalog import catalog_commands
from bigeye_cli.sla import sla_commands
from bigeye_cli.metric import metric_commands
from bigeye_cli.issues import issue_commands

# create logger
log = get_logger(__file__)

app = typer.Typer(help='Bigeye CLI.')
app.add_typer(sla_commands.app, name='sla')
app.add_typer(catalog_commands.app, name='catalog')
app.add_typer(metric_commands.app, name='metric')
app.add_typer(deltas_commands.app, name='deltas')
app.add_typer(workspace_commands.app, name='workspace')
app.add_typer(issue_commands.app, name='issues')


@app.command()
def version():
    """Returns Bigeye CLI and Bigeye SDK Versions."""
    print(f'Bigeye CLI Version: {bigeye_cli_version.version}\nBigeye SDK Version: {bigeye_sdk_version.version}')


if __name__ == '__main__':
    app()
